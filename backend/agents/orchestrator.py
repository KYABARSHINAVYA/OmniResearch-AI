from agents.planner_agent import planner
from agents.rag_agent import run_rag
from agents.graph_rag_agent import run_graph
from agents.memory_agent import memory_agent
from agents.mcp_agent import mcp_agent
from agents.writer_agent import writer


def run_agent(question: str):

    # Planner
    print("PLANNER DONE")
    plan = planner(question)

    # RAG
    print("RAG START")
    rag_result = run_rag(question)

    # Graph RAG
    print("GRAPH START")
    graph_result = run_graph(question)

    # Memory
    memory = memory_agent(question)

    # MCP
    mcp_result = mcp_agent(question)

    print("WRITER START")

    final_answer = writer(
        rag_result,
        "",
        memory,
        graph_result,
        mcp_result
    )

    print("WRITER DONE")

    return {
    "plan": plan,
    "route": "hybrid",
    "answer": final_answer
}
