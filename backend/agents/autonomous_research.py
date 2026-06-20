import os
from datetime import datetime

from agents.browser_agent import browse_url
from agents.evaluator_agent import evaluate_answer
from agents.research_agent import researcher
from agents.writer_agent import writer


REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")


def generate_report(topic, urls=None):
    os.makedirs(REPORT_DIR, exist_ok=True)
    urls = urls or []

    research = researcher(topic)
    browser_notes = [browse_url(url) for url in urls[:5]]
    answer = writer(
        research,
        "\n".join(note.get("text", "") for note in browser_notes),
        "",
        "",
        {"wiki": "", "papers": []},
    )
    evaluation = evaluate_answer(
        topic,
        answer,
        {"research": research, "browser": browser_notes},
    )

    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"report-{timestamp}.md"
    path = os.path.join(REPORT_DIR, filename)
    content = f"""# {topic}

Generated: {datetime.utcnow().isoformat()}Z

Confidence: {evaluation.get("confidence")}
Hallucination risk: {evaluation.get("hallucination_risk")}

## Executive Summary

{answer}

## Evaluation

{evaluation.get("notes", "")}

## Sources

{os.linesep.join(f"- {item.get('url')}: {item.get('title') or item.get('error')}" for item in browser_notes) or "- Web search and local knowledge sources"}
"""
    with open(path, "w", encoding="utf-8") as report:
        report.write(content)

    return {
        "topic": topic,
        "report_path": path,
        "answer": answer,
        "evaluation": evaluation,
    }
