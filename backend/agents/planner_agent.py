from dotenv import load_dotenv
from config.llm import invoke_llm
import json
import re

load_dotenv()


# -----------------------------
# Safe LLM Wrapper
# -----------------------------
def call_llm(prompt: str):
    try:
        return invoke_llm(prompt, task="planner")

    except Exception as e:
        print(f"[LLM ERROR]: {e}")

        # Safe fallback JSON
        return json.dumps({
            "steps": [
                "understand question",
                "retrieve information",
                "generate answer"
            ],
            "route": "hybrid"
        })


# -----------------------------
# Planner Agent
# -----------------------------
def planner(question: str):

    prompt = f"""
You are an AI Planner for a Retrieval-Augmented + Knowledge Graph system.

Your job:
1. Understand the user's question.
2. Break it into logical steps.
3. Decide the best route.

ROUTES:
- rag → documents, PDFs, text explanation
- graph → relationships, entities
- hybrid → both required

Return ONLY valid JSON:

{{
  "steps": ["step1", "step2", "step3"],
  "route": "rag | graph | hybrid"
}}

User Question:
{question}
"""

    content = call_llm(prompt)

    # Try parsing JSON directly
    try:
        return json.loads(content)

    except Exception:
        # Extract JSON from response
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

    # Final fallback
    return {
        "steps": [
            "understand question",
            "retrieve knowledge",
            "generate answer"
        ],
        "route": "hybrid"
    }
