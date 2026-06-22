
from dotenv import load_dotenv

from rag.hybrid_search import hybrid_search
from tools.vector_search import search_faiss

load_dotenv()



def rag_agent(question):

    try:
        data = hybrid_search(question)
    except Exception as exc:
        return f"RAG unavailable: {exc}"

    return (
        "Document Context:\n"
        f"{data.get('pdf_context', '')}\n\n"
        "Web Results:\n"
        f"{data.get('web_results', '')}"
    )
def run_rag(query):
    docs = search_faiss(query)
    return " ".join(docs)
