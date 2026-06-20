
from dotenv import load_dotenv

from rag.hybrid_search import hybrid_search
from tools.vector_search import search_faiss
from config.llm import invoke_llm

load_dotenv()



def rag_agent(question):

    try:
        data = hybrid_search(question)
    except Exception as exc:
        return f"RAG unavailable: {exc}"

    prompt = f"""
    Question:

    {question}

    Document Context:

    {data['pdf_context']}

    Web Results:

    {data['web_results']}

    Answer using both sources.
    """

    return invoke_llm(prompt, task="rag")
def run_rag(query):
    docs = search_faiss(query)
    return " ".join(docs)
