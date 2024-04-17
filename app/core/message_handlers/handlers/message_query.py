from core.message_handlers.base.message_base import MessageBase
from core.serializers.text_query_serializer import TextQuerySerializer
from core.server.query_fetcher import QueryFetcher
from core.utils.hash_util import HashUtil


class MessageQuery(MessageBase):
    def should_handle(self, client_request):
        return client_request.type == "textquery"

    async def handle(self, client_request, client):
        query = client_request.content.get('query')
        debug_info = {}
        query_dicts = client_request.content.get("query_dicts")
        query_request_hash = HashUtil.hash_dict({"query_dicts": query_dicts, "query": query})
        if query or query_dicts:
            print(f"Received query {query}")
            if not query_dicts:
                # TODO: add support for getting temporal queries (to get an array of query_dicts)
                query_dicts = [TextQuerySerializer.text_query_to_dict(query)]

            selected_page = int(client_request.content.get('selectedpage', 1))
            results_per_page = int(client_request.content.get('resultsperpage', 20))
            skip = (selected_page - 1) * results_per_page

            # check if the query is the same (then we can use caching, because just the page is different)
            if query_request_hash not in client.cached_results:
                client.cached_results = {query_request_hash: True}

            images = []
            total_results = 0

            # TODO: First fetch the last query_dict query_dicts[-1]

            # TODO: Iterate through the results
            # TODO: Fetch the next query_dict on the same day (string field), but before the first one (time field) (the nearest to the last one)
            # TODO: Do this until end, then end it to the results

            for query_dict in query_dicts:
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
                mongo_query = await QueryFetcher.transform_to_mongo_query(query_dict, client, client_request, debug_info)

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