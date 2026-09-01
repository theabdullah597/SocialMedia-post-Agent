from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant, QdrantVectorStore

from config import QDRANT_URL,QDRANT_API_KEY

Collection_name="educational_content"

def load_document():
    documents=[]
    pdf_files=Path("documents").glob("*.pdf")
    for pdf in pdf_files:
        loader=PyPDFLoader(str(pdf))
        documents.extend(loader.load())

    return documents

def create_vector_store():
    documents=load_document()
    if not documents:
        raise Exception("No documents found")
    print(f"Loaded {len(documents)} documents")
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=10
    )
    chunks=splitter.split_documents(documents)
    print(f"Loaded {len(chunks)} chunks")
    embeddings=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print(embeddings)

    vectors_store=QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=Collection_name
    )
    print("Document successfully store in Qdrant")
    return vectors_store


if __name__=="__main__":
    create_vector_store()