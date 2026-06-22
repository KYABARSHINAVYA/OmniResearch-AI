from dotenv import load_dotenv
from config.llm import invoke_llm

load_dotenv()


def writer(
        research_data,
        rag_context,
        memory_context,
        graph_context,
        mcp_context,
        question=""
):
    mcp_context = mcp_context or {}

    prompt = f"""
Question:

{question}

Research:

{research_data}

RAG Results:

{rag_context}

Memory:

{memory_context}

Knowledge Graph:

{graph_context}

Wikipedia:

{mcp_context.get("wiki", "")}

Arxiv Papers:

{mcp_context.get("papers", [])}

Generate a clear, useful answer to the question. Be concise unless the question asks for depth.
"""

    return invoke_llm(prompt, task="writer")
