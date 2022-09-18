import uuid
from typing import List, Tuple
import multiprocessing as mp

from elasticsearch import Elasticsearch

from engine.base_client.search import BaseSearcher
from engine.clients.elasticsearch import (
    ELASTIC_INDEX,
    ELASTIC_PASSWORD,
    ELASTIC_PORT,
    ELASTIC_USER,
)


class ClosableElastic(Elasticsearch):

    def __del__(self):
        self.close()


class ElasticSearcher(BaseSearcher):
    search_params = {}
    client: Elasticsearch = None

    @classmethod
    def get_mp_start_method(cls):
        return 'forkserver' if 'forkserver' in mp.get_all_start_methods() else 'spawn'

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        init_params = {
            **{
                "verify_certs": False,
                "request_timeout": 90,
                "retry_on_timeout": True,
            },
            **connection_params,
        }
        cls.client: Elasticsearch = Elasticsearch(
            f"http://{host}:{ELASTIC_PORT}",
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            **init_params,
        )
        cls.search_params = search_params

    @classmethod
    def search_one(cls, vector, meta_conditions, top) -> List[Tuple[int, float]]:
        res = cls.client.knn_search(
            index=ELASTIC_INDEX,
            knn={
                "field": "vector",
                "query_vector": vector,
                "k": top,
                **{"num_candidates": 100, **cls.search_params},
            },
            docvalue_fields=["vector_id"],
            stored_fields="_none_"
        )

        return [
            (uuid.UUID(hex=hit["fields"]["vector_id"][0]).int, hit["_score"])
            for hit in res["hits"]["hits"]
        ]
