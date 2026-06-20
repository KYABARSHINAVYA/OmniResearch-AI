from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

from rag.embeddings import embedding_model

loader = PyPDFLoader(
    "documents/sample.pdf"
)

docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(docs)

db = FAISS.from_documents(
    chunks,
    embedding_model
)

db.save_local(
    "vectorstore/faiss_db"
)

print("Vector DB created")