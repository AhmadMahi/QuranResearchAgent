import os
import uuid
from typing import List, Optional
import chromadb


def _make_embedding_function():
    """Use OpenAI text-embedding-3-small when key is available, otherwise ChromaDB default."""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("CHROMA_OPENAI_API_KEY")
    if api_key:
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
        return OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-3-small",
        )
    # Fallback: ChromaDB's built-in sentence-transformer (no API key needed)
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    return DefaultEmbeddingFunction()


class VectorStoreManager:
    def __init__(self):
        self._client = chromadb.EphemeralClient()
        ef = _make_embedding_function()
        self._collection = self._client.get_or_create_collection(
            name="research_docs",
            embedding_function=ef,
        )

    def store_documents(self, documents: List[str], topic: str) -> None:
        clean = [d for d in documents if d and len(d.strip()) > 10]
        if not clean:
            return
        ids = [f"{topic[:20]}-{uuid.uuid4().hex[:8]}" for _ in clean]
        self._collection.add(
            documents=clean,
            ids=ids,
            metadatas=[{"topic": topic} for _ in clean],
        )

    def search(self, query: str, n_results: int = 3) -> List[str]:
        count = self._collection.count()
        if count == 0:
            return []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
            )
            return results.get("documents", [[]])[0]
        except Exception:
            return []
