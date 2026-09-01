from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from config import QDRANT_URL,QDRANT_API_KEY

Collection_name="educational_content"

embeddings=HuggingFaceEmbeddings(
   model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vector_store=QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=Collection_name,
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)

def search_knowledge(query,k=3):
    results=vector_store.similarity_search(
        query,
        k=k
    )
    return results


if __name__=="__main__":
    query=input("Ask something:")
    result=search_knowledge(query)

    print("Relevant Information")
    for i,document in enumerate(result,start=1):
        print(f"Result{i}")
        print(document.page_content)

