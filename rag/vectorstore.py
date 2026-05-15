import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

CHROMA_PATH = Path(__file__).parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "stock_knowledge"
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


def search(query: str, n_results: int = 3) -> list[dict]:
    collection = get_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({
            "content": doc,
            "source": meta.get("source", "unknown"),
            "score": round(1 - dist, 4),  # cosine similarity
        })
    return output
