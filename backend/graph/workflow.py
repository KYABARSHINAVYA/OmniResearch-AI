from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict
import ast
import re
import time

from agents.evaluator_agent import evaluate_answer
from agents.graph_rag_agent import graph_rag_agent
from agents.mcp_agent import mcp_agent
from agents.memory_agent import memory_agent
from agents.planner_agent import planner
from agents.rag_agent import rag_agent
from agents.research_agent import researcher
from agents.reviewer_agent import reviewer
from agents.writer_agent import writer
from analytics.agent_logs import add_log
from analytics.agent_status import update_status
from analytics.latency_monitor import save_latency
from persistence.checkpoints import save_checkpoint


def _heuristic_plan(question: str):
    lowered = question.lower()
    graph_terms = {"relationship", "relationships", "entity", "entities", "connect", "connected", "graph"}
    route = "graph" if any(term in lowered for term in graph_terms) else "rag"
    return {"steps": ["understand question", "retrieve context", "write answer"], "route": route}


class AgentState(TypedDict, total=False):
    question: str
    mode: str
    plan: dict
    research: str
    rag_context: str
    memory: str
    graph_context: str
    mcp_context: dict
    answer: str
    evaluation: dict
    timings: dict


def _run_node(agent_name, fn, *args):
    update_status(agent_name, "running")
    start = time.time()
    try:
        result = fn(*args)
        update_status(agent_name, "completed")
        add_log(f"{agent_name} completed")
        return agent_name, result, None, time.time() - start
    except Exception as exc:
        update_status(agent_name, "failed")
        add_log(f"{agent_name} failed: {exc}")
        return agent_name, None, exc, time.time() - start


def _looks_like_provider_error(value):
    if not isinstance(value, str):
        return False

    text = value.lower()
    return (
        text.startswith("error:")
        or "insufficient_quota" in text
        or "exceeded your current quota" in text
        or "error code: 429" in text
        or "could not reach any configured language model" in text
    )


def _clean_agent_text(agent_name, value):
    if _looks_like_provider_error(value):
        add_log(f"{agent_name} output ignored because it was a provider error")
        return ""

    return value or ""


def _limit_text(value, limit=5000):
    text = str(value or "")
    return text if len(text) <= limit else text[:limit] + "\n...[truncated for latency]"


def _sentences_from_text(value):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    text = re.sub(r"^(Document Context|Web Results|Research|Memory|Knowledge Graph):\s*", "", text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [
        sentence.strip()
        for sentence in sentences
        if 35 <= len(sentence.strip()) <= 450
        and not _looks_like_provider_error(sentence)
    ]


def _web_result_sentences(value):
    if not isinstance(value, str) or "Web Results:" not in value:
        return []

    _, raw_web_results = value.split("Web Results:", 1)
    try:
        parsed = ast.literal_eval(raw_web_results.strip())
    except (SyntaxError, ValueError):
        return []

    sentences = []
    for result in parsed.get("results", [])[:3]:
        title = result.get("title", "").strip()
        content = result.get("content", "").strip()
        url = result.get("url", "").strip()
        summary = " - ".join(part for part in (title, content) if part)
        if url:
            summary = f"{summary} ({url})" if summary else url
        sentences.extend(_sentences_from_text(summary))

    return sentences


def _extractive_answer(question, evidence):
    question_terms = {
        term
        for term in re.findall(r"[a-zA-Z0-9]+", question.lower())
        if len(term) > 2
    }
    candidates = []

    for key in ("research", "rag", "memory", "graph"):
        value = evidence.get(key, "")
        candidates.extend(_web_result_sentences(value))
        candidates.extend(_sentences_from_text(value))

    mcp_context = evidence.get("mcp", {}) or {}
    candidates.extend(_sentences_from_text(mcp_context.get("wiki", "")))
    for paper in mcp_context.get("papers", []) or []:
        candidates.extend(_sentences_from_text(paper))

    ranked = sorted(
        dict.fromkeys(candidates),
        key=lambda sentence: sum(
            1 for term in question_terms if term in sentence.lower()
        ),
        reverse=True,
    )
    selected = [sentence for sentence in ranked[:4] if sentence]

    if not selected:
        return ""

    bullets = "\n".join(f"- {sentence}" for sentence in selected)
    return (
        "I could not reach the writer model, so here is a concise answer "
        "assembled from retrieved context:\n\n"
        f"{bullets}"
    )


def _quick_evaluation(answer, evidence):
    has_answer = bool(str(answer).strip())
    has_evidence = any(bool(value) for value in evidence.values())
    return {
        "confidence": 0.7 if has_answer and has_evidence else 0.45,
        "hallucination_risk": "medium" if has_evidence else "high",
        "unsupported_claims": [],
        "notes": "Fast heuristic evaluator used to keep latency low.",
    }


class OmniResearchWorkflow:
    """
    Planner runs first, independent retrieval/tool agents fan out in parallel,
    then Writer and Reviewer consume the combined context.
    """

    def invoke(self, state: AgentState):
        question = state["question"]
        mode = state.get("mode", "fast")
        timings = {}

        if mode == "fast":
            start = time.time()
            plan = _heuristic_plan(question)
            elapsed = time.time() - start
            timings["planner"] = elapsed
            save_latency("planner", elapsed)
            update_status("planner", "completed")
            add_log("planner completed with fast heuristic route")
        else:
            _, plan, plan_error, elapsed = _run_node("planner", planner, question)
            timings["planner"] = elapsed
            save_latency("planner", elapsed)
            if plan_error or not isinstance(plan, dict):
                plan = {"steps": ["understand question", "retrieve context", "write answer"], "route": "hybrid"}

        route = plan.get("route", "hybrid")
        parallel_tasks = {
            "memory": memory_agent,
            "rag": rag_agent,
        }

        if route in {"graph", "hybrid"} or mode != "fast":
            parallel_tasks["graph"] = graph_rag_agent
        if route in {"hybrid", "web", "research"} and mode != "fast":
            parallel_tasks["research"] = researcher
        if mode == "deep":
            parallel_tasks["mcp"] = mcp_agent
        elif mode == "balanced" and route == "hybrid":
            parallel_tasks["mcp"] = mcp_agent

        results = {
            "research": "",
            "rag": "",
            "memory": "",
            "graph": "",
            "mcp": {"wiki": "", "papers": []},
        }

        add_log(
            "parallel fan-out started: "
            + ", ".join(sorted(parallel_tasks.keys()))
        )

        with ThreadPoolExecutor(max_workers=min(len(parallel_tasks), 5) or 1) as executor:
            futures = {
                executor.submit(_run_node, name, fn, question): name
                for name, fn in parallel_tasks.items()
            }
            for future in as_completed(futures):
                name, value, error, elapsed = future.result()
                timings[name] = elapsed
                save_latency(name, elapsed)
                if error:
                    continue
                if name == "mcp":
                    results["mcp"] = value or results["mcp"]
                else:
                    results[name] = _limit_text(_clean_agent_text(name, value))

        has_context = any(
            bool(results[key])
            for key in ("research", "rag", "memory", "graph")
        ) or any(bool(value) for value in results["mcp"].values())

        evidence = {
            "research": results["research"],
            "rag": results["rag"],
            "memory": results["memory"],
            "graph": results["graph"],
            "mcp": results["mcp"],
        }

        if has_context:
            _, answer, writer_error, elapsed = _run_node(
                "writer",
                writer,
                results["research"],
                results["rag"],
                results["memory"],
                results["graph"],
                results["mcp"],
                question,
            )
        else:
            answer = (
                "I could not gather usable context because the configured language "
                "model providers are unavailable or out of quota. Please configure "
                "Gemini, DeepSeek, or Ollama, or restore OpenAI billing/quota."
            )
            writer_error = None
            elapsed = 0
            update_status("writer", "failed")
            add_log("writer skipped because no usable context was available")

        answer = _clean_agent_text("writer", answer)
        if not answer:
            answer = _extractive_answer(question, evidence) or (
                "I could not generate a usable answer because the configured language "
                "model providers are unavailable or out of quota."
            )

        timings["writer"] = elapsed
        save_latency("writer", elapsed)
        if writer_error:
            answer = f"I could not generate the final answer: {writer_error}"

        if mode == "deep":
            _, reviewed, _, elapsed = _run_node("reviewer", reviewer, answer)
            timings["reviewer"] = elapsed
            save_latency("reviewer", elapsed)
            answer = _clean_agent_text("reviewer", reviewed) or answer

        if mode == "deep":
            _, evaluation, _, elapsed = _run_node(
                "evaluator",
                evaluate_answer,
                question,
                answer,
                evidence,
            )
            timings["evaluator"] = elapsed
            save_latency("evaluator", elapsed)
        else:
            start = time.time()
            evaluation = _quick_evaluation(answer, evidence)
            elapsed = time.time() - start
            timings["evaluator"] = elapsed
            save_latency("evaluator", elapsed)
            update_status("evaluator", "completed")
            add_log("evaluator completed with fast heuristic scoring")

        output = {
            "question": question,
            "mode": mode,
            "plan": plan,
            "research": results["research"],
            "rag_context": results["rag"],
            "memory": results["memory"],
            "graph_context": results["graph"],
            "mcp_context": results["mcp"],
            "answer": answer,
            "evaluation": evaluation,
            "timings": timings,
        }
        save_checkpoint(output)
        return output


graph = OmniResearchWorkflow()
