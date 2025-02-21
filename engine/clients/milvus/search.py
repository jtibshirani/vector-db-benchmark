import multiprocessing as mp
from typing import List, Tuple

from pymilvus import Collection, connections

from engine.base_client.search import BaseSearcher
from engine.clients.milvus.config import (
    MILVUS_COLLECTION_NAME,
    MILVUS_DEFAULT_ALIAS,
    MILVUS_DEFAULT_PORT, DISTANCE_MAPPING,
)


class MilvusSearcher(BaseSearcher):
    search_params = {}
    client: connections = None
    collection: Collection = None
    distance: str = None

    @classmethod
    def init_client(cls, host, distance, connection_params: dict, search_params: dict):
        cls.client = connections.connect(
            alias=MILVUS_DEFAULT_ALIAS,
            host=host,
            port=str(connection_params.pop("port", MILVUS_DEFAULT_PORT)),
            **connection_params
        )
        cls.collection = Collection(MILVUS_COLLECTION_NAME, using=MILVUS_DEFAULT_ALIAS)
        cls.search_params = search_params
        cls.distance = DISTANCE_MAPPING[distance]

    @classmethod
    def get_mp_start_method(cls):
        return 'forkserver' if 'forkserver' in mp.get_all_start_methods() else 'spawn'

    @classmethod
    def conditions_to_filter(cls, _meta_conditions):
        # ToDo: implement
        return None

    @classmethod
    def search_one(cls, vector, meta_conditions, top) -> List[Tuple[int, float]]:
        param = {
            "metric_type": cls.distance,
            "params": cls.search_params['params']
        }
        try:
            res = cls.collection.search(
                data=[vector],
                anns_field="vector",
                param=param,
                limit=top,
            )
        except Exception as e:
            import ipdb; ipdb.set_trace()
            print("param: ", param)

            raise e

        return list(zip(res[0].ids, res[0].distances))
