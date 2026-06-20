from rag.retrieval import retrieve_context
from tools.tavily_tool import search_web

def hybrid_search(question):

    pdf_context = retrieve_context(question)

    web_results = search_web(question)

    return {
        "pdf_context": pdf_context,
        "web_results": web_results
    }