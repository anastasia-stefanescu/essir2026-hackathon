"""A thin wrapper over qdrant-client.

Enough to store chunks and search them. The interesting improvements live in the
TODO comments — this is a plain single-vector cosine index and nothing more.
"""

from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient, models

from ..config import get_settings


class VectorStore:
    def __init__(self, url: str, collection: str, local_path: str | None = None):
        if local_path:
            self.client = QdrantClient(path=local_path)
        else:
            self.client = QdrantClient(url=url)
        self.collection = collection

    # --- inspection ---------------------------------------------------------
    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.get_collections().collections]

    def exists(self) -> bool:
        return self.client.collection_exists(self.collection)

    def count(self) -> int:
        if not self.exists():
            return 0
        return self.client.count(self.collection).count

    # --- write --------------------------------------------------------------
    def ensure_collection(self, dim: int, reset: bool = False, sparse: bool = False) -> None:
        """Create the collection sized to the embedding dimension.

        The vector size is fixed at creation, so if you change embedding models you
        must re-ingest (or ingest into a differently named collection).

        Pass sparse=True when search_mode is "sparse" or "hybrid" — this creates
        named vectors ("dense" + "sparse") instead of a single unnamed vector.
        """
        if reset and self.exists():
            self.client.delete_collection(self.collection)
        if not self.exists():
            if sparse:
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config={
                        "dense": models.VectorParams(size=dim, distance=models.Distance.COSINE),
                    },
                    sparse_vectors_config={
                        "sparse": models.SparseVectorParams(
                            index=models.SparseIndexParams(on_disk=False)
                        ),
                    },
                )
            else:
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
                )
            # TODO(level-3): a payload index on e.g. `page` lets you filter searches
            # (search only the references section, only tables, ...). See
            # client.create_payload_index(...).

    def upsert(self, points: list[models.PointStruct]) -> None:
        self.client.upsert(collection_name=self.collection, points=points)

    # --- read ---------------------------------------------------------------
    def search(
        self,
        vector: list[float],
        top_k: int,
        sparse_vector: dict[int, float] | None = None,
        mode: str = "dense",
    ) -> list[models.ScoredPoint]:
        # TODO(level-3): pass a query_filter to scope retrieval to part of the doc.
        if mode == "sparse" and sparse_vector is not None:
            indices = list(sparse_vector.keys())
            values = list(sparse_vector.values())
            result = self.client.query_points(
                collection_name=self.collection,
                query=models.SparseVector(indices=indices, values=values),
                using="sparse",
                limit=top_k,
                with_payload=True,
            )
        elif mode == "hybrid" and sparse_vector is not None:
            indices = list(sparse_vector.keys())
            values = list(sparse_vector.values())
            result = self.client.query_points(
                collection_name=self.collection,
                prefetch=[
                    models.Prefetch(query=vector, using="dense", limit=top_k),
                    models.Prefetch(
                        query=models.SparseVector(indices=indices, values=values),
                        using="sparse",
                        limit=top_k,
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
                with_payload=True,
            )
        else:
            result = self.client.query_points(
                collection_name=self.collection,
                query=vector,
                limit=top_k,
                with_payload=True,
            )
        return result.points


@lru_cache
def get_store() -> VectorStore:
    s = get_settings()
    return VectorStore(s.qdrant_url, s.qdrant_collection, s.qdrant_local_path)
