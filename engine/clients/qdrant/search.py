import multiprocessing
from typing import List, Optional, Tuple

import httpx
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client import grpc

from engine.base_client.search import BaseSearcher
from engine.clients.qdrant.config import QDRANT_COLLECTION_NAME


class QdrantSearcher(BaseSearcher):
    search_params = {}
    client: QdrantClient = None

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        cls.client: QdrantClient = QdrantClient(host, **connection_params)
        cls.search_params = search_params

    @classmethod
    def conditions_to_filter(cls, _meta_conditions) -> Optional[rest.Filter]:
        # ToDo: implement
        return None

    @classmethod
    def search_one(cls, vector, meta_conditions, top) -> List[Tuple[int, float]]:
        res = cls.client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=vector,
            query_filter=cls.conditions_to_filter(meta_conditions),
            limit=top,
            search_params=rest.SearchParams(**cls.search_params.get("search_params", {})),
        )
        return [(hit.id, hit.score) for hit in res]

