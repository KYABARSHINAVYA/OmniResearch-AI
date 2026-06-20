from langchain_community.vectorstores import FAISS

from rag.embeddings import embedding_model

db = FAISS.load_local(
    "vectorstore/faiss_db",
    embedding_model,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever()

def retrieve_context(question):

    docs = retriever.invoke(question)

    context = ""

    for doc in docs:
        context += doc.page_content

    return context