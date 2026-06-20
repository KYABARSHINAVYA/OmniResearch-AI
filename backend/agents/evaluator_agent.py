import json
import re

from config.llm import invoke_llm


def _extract_json(text):
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None
        try:
            return json.loads(match.group())
        except Exception:
            return None


def evaluate_answer(question, answer, evidence=None):
    evidence = evidence or {}
    prompt = f"""
You are an evaluator for a research assistant.

Score the answer using only the provided evidence. Detect unsupported claims,
missing caveats, and likely hallucinations.

Return only JSON:
{{
  "confidence": 0.0,
  "hallucination_risk": "low | medium | high",
  "unsupported_claims": [],
  "notes": ""
}}

Question:
{question}

Answer:
{answer}

Evidence:
{json.dumps(evidence, default=str)[:12000]}
"""
    raw = invoke_llm(prompt, task="evaluator")
    parsed = _extract_json(raw)
    if parsed:
        parsed["confidence"] = max(0, min(1, float(parsed.get("confidence", 0.55))))
        return parsed

    has_answer = bool(str(answer).strip())
    has_evidence = any(bool(value) for value in evidence.values())
    return {
        "confidence": 0.65 if has_answer and has_evidence else 0.35,
        "hallucination_risk": "medium" if has_evidence else "high",
        "unsupported_claims": [],
        "notes": "Heuristic evaluator fallback was used because structured JSON was not returned.",
    }
