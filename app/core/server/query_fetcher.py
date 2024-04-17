import inspect

from core.query_transform.default_mongodb_query_part_transformers import default_mongodb_query_part_transformers


class QueryFetcher:

    def transform_to_mongo_query(query_dict, message, get_clip_websocket):
        for transformer in default_mongodb_query_part_transformers:
            if transformer.should_use(query_dict):
                if transformer.__class__.__name__ == "QPTClip" and self.cached_clip_result:
                    if "$and" not in mongo_query:
                        mongo_query["$and"] = []
                    mongo_query["$and"].append(self.cached_clip_result)
                    break

                kwargs = {}
                needed_kwargs = transformer.needed_kwargs()
                if "clip_websocket" in needed_kwargs:
                    kwargs["clip_websocket"] = await get_clip_websocket()
                if "message" in needed_kwargs:
                    kwargs["message"] = message

                if inspect.iscoroutinefunction(transformer.transform):
                    await transformer.transform(mongo_query, query_dict, debug_info, **kwargs)
                else:
                    transformer.transform(mongo_query, query_dict, debug_info,  **kwargs)

                if transformer.__class__.__name__ == "QPTClip" and mongo_query.get("$and"):
                    self.cached_clip_result = mongo_query.get("$and")[-1]

    def fetch(self, query_dict):
        pass