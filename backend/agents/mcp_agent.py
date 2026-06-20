from mcp.wikipedia_mcp import wikipedia_search
from mcp.arxiv_mcp import arxiv_search
from analytics.tool_calls import register_tool


def mcp_agent(question):
    register_tool("wikipedia")
    register_tool("arxiv")

    wiki = wikipedia_search(
        question
    )

    papers = arxiv_search(
        question
    )

    return {

        "wiki": wiki,

        "papers": papers

    }
