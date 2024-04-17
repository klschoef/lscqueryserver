import hashlib
import inspect
import json

from core.message_handlers.base.message_base import MessageBase
from core.query_transform.default_mongodb_query_part_transformers import default_mongodb_query_part_transformers
from core.serializers.text_query_serializer import TextQuerySerializer


class MessageQuery(MessageBase):
    def should_handle(self, client_request):
        return client_request.type == "textquery"

    async def handle(self, client_request, client):
        query = client_request.content.get('query')
        debug_info = {}
        query_dicts = client_request.content.get("query_dicts")
        hash_json_string = json.dumps({"query_dicts": query_dicts, "query": query}, sort_keys=True)
        query_request_hash = hashlib.sha256(hash_json_string.encode()).hexdigest()
        if query or query_dicts:
            print(f"Received query {query}")
            if not query_dicts:
                # TODO: add support for getting temporal queries (to get an array of query_dicts)
                query_dicts = [TextQuerySerializer.text_query_to_dict(query)]

            mongo_query = {}

            selected_page = int(client_request.content.get('selectedpage', 1))
            results_per_page = int(client_request.content.get('resultsperpage', 20))
            skip = (selected_page - 1) * results_per_page

            # check if the query is the same (then we can use caching, because just the page is different)
            if query_request_hash not in client.cached_results:
                client.cached_results = {query_request_hash: True}

            images = []
            total_results = 0

            for query_dict in query_dicts:
                # generate the query_hash for caching purposes
                query_dict_json_string = json.dumps(query_dict, sort_keys=True)
                query_hash = hashlib.sha256(query_dict_json_string.encode()).hexdigest()
                # build the mongo query
                # TODO: outsource the transformer logic
                # TODO: outsource the logic, to get images out of an query_dict
                # TODO: for filtering the previous queries. Maybe check if it's possible, that the datetime needs in an array of datetimes
                # TODO: or just the date string (better option)
                # TODO: first (timebased last) query is the first one, and defines the dates. The other queries needs to be on the same date.
                # TODO: check if time is lower after each round.
                """
                Option:
                Erste Seite wird gecheckt. Danach nächste Query. Nächste Query nur das näheste Result wird verwendet (prüfen).
                Oder einfach jedes einzelne Result durchgehen? Dann kann genau geprüft werden, aber mehr DB Requests.
                """
                for transformer in default_mongodb_query_part_transformers:
                    if transformer.should_use(query_dict):
                        cache_key = f"{client.connection_id}_{query_hash}_{transformer.__class__.__name__}"
                        if transformer.__class__.__name__ == "QPTClip" and cache_key in client.cached_results:
                            if "$and" not in mongo_query:
                                mongo_query["$and"] = []
                            mongo_query["$and"].append(client.cached_results.get(cache_key))
                            break

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

                        if transformer.__class__.__name__ == "QPTClip" and mongo_query.get("$and"):
                            client.cached_results[cache_key] = mongo_query.get("$and")[-1]

                # execute the mongo query with pagination
                total_results = client.db['images'].count_documents(mongo_query)
                images = client.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1}).skip(skip).limit(results_per_page)

            if client_request.version >= 2:
                results = list(images)
            else:
                results = [image.get('filepath') for image in images]

            # build result object
            return {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info}
        else:
            print("No query found in content")