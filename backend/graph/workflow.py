from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict
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


class OmniResearchWorkflow:
    def invoke(self, state: AgentState):
        question = state["question"]
        mode = state.get("mode", "balanced")
        timings = {}

        _, plan, plan_error, elapsed = _run_node("planner", planner, question)
        timings["planner"] = elapsed
        save_latency("planner", elapsed)
        if plan_error or not isinstance(plan, dict):
            plan = {"steps": ["understand question", "retrieve context", "write answer"], "route": "hybrid"}

        route = plan.get("route", "hybrid")
        tasks = {
            "memory": memory_agent,
            "rag": rag_agent,
            "graph": graph_rag_agent,
        }

        if route in {"hybrid", "web", "research"} and mode != "fast":
            tasks["research"] = researcher
        if mode == "deep":
            tasks["mcp"] = mcp_agent
        elif mode == "balanced" and route == "hybrid":
            tasks["mcp"] = mcp_agent

        results = {
            "research": "",
            "rag": "",
            "memory": "",
            "graph": "",
            "mcp": {"wiki": "", "papers": []},
        }

        with ThreadPoolExecutor(max_workers=min(len(tasks), 5) or 1) as executor:
            futures = {
                executor.submit(_run_node, name, fn, question): name
                for name, fn in tasks.items()
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
                    results[name] = value or ""

        _, answer, writer_error, elapsed = _run_node(
            "writer",
            writer,
            results["research"],
            results["rag"],
            results["memory"],
            results["graph"],
            results["mcp"],
        )
        timings["writer"] = elapsed
        save_latency("writer", elapsed)
        if writer_error:
            answer = f"I could not generate the final answer: {writer_error}"

        if mode != "fast":
            _, reviewed, _, elapsed = _run_node("reviewer", reviewer, answer)
            timings["reviewer"] = elapsed
            save_latency("reviewer", elapsed)
            answer = reviewed or answer

        _, evaluation, _, elapsed = _run_node(
            "evaluator",
            evaluate_answer,
            question,
            answer,
            {
                "research": results["research"],
                "rag": results["rag"],
                "memory": results["memory"],
                "graph": results["graph"],
                "mcp": results["mcp"],
            },
        )
        timings["evaluator"] = elapsed
        save_latency("evaluator", elapsed)

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
