import inspect

from core.query_transform.default_mongodb_query_part_transformers import default_mongodb_query_part_transformers
from core.utils.hash_util import HashUtil


class QueryFetcher:

    @staticmethod
    async def transform_to_mongo_query(query_dict, client, client_request, debug_info):
        mongo_query = {"$and": []}
        query_hash = HashUtil.hash_dict(query_dict)
        activate_caching = client_request.content.get('activate_caching', True)
        for transformer in default_mongodb_query_part_transformers:
            if transformer.should_use(query_dict):
                cache_key = f"{client.connection_id}_{query_hash}_{transformer.__class__.__name__}"
                if activate_caching and transformer.__class__.__name__ == "QPTClip" and cache_key in client.cached_results:
                    if "$and" not in mongo_query:
                        mongo_query["$and"] = []
                    mongo_query["$and"].append(client.cached_results.get(cache_key))
                    continue

                kwargs = {}
                needed_kwargs = transformer.needed_kwargs()
                if "clip_websocket" in needed_kwargs:
                    kwargs["clip_websocket"] = await client.clip_connection.get_clip_websocket()
                if "clip_connection" in needed_kwargs:
                    kwargs["clip_connection"] = client.clip_connection
                if "message" in needed_kwargs:
                    kwargs["message"] = client_request.message
                if "client" in needed_kwargs:
                    kwargs["client"] = client

                if inspect.iscoroutinefunction(transformer.transform):
                    await transformer.transform(mongo_query, query_dict, debug_info, **kwargs)
                else:
                    transformer.transform(mongo_query, query_dict, debug_info,  **kwargs)

                if activate_caching and transformer.__class__.__name__ == "QPTClip" and mongo_query.get("$and"):
                    client.cached_results[cache_key] = mongo_query.get("$and")[-1]

        if len(mongo_query["$and"]) == 0:
            del mongo_query["$and"]
        return mongo_query

    def fetch(self, query_dict):
        pass