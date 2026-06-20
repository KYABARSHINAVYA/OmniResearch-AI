from langchain_community.vectorstores import FAISS
from rag.embeddings import embedding_model

def search_faiss(query, db_path="vectorstore/faiss_db"):
    db = FAISS.load_local(db_path, embedding_model, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=3)

    return [doc.page_content for doc in docs]