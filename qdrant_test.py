from config import QDRANT_API_KEY
from config import QDRANT_URL
from qdrant_client import QdrantClient
client=QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)
collections=client.get_collections()
print("Collection Created")
print(collections)