from pymongo import DESCENDING

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

            if len(query_dicts) == 1:
                return await self.handle_single_query(query_dicts[0], client_request, client, skip, results_per_page, debug_info)

            return await self.handle_temporal_query(query_dicts, client_request, client, skip, results_per_page, debug_info)

            # build result object
            # return {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info}
        else:
            print("No query found in content")

    async def handle_single_query(self, query_dict, client_request, client, skip, results_per_page, debug_info):
        mongo_query = await QueryFetcher.transform_to_mongo_query(query_dict, client, client_request, debug_info)
        total_results = client.db['images'].count_documents(mongo_query)
        images = client.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1}).limit(results_per_page).skip(skip)
        if client_request.version >= 2:
            results = list(images)
        else:
            results = [image.get('filepath') for image in images]
        return {"num": len(results), "totalresults": total_results, "results": results, "requestId": client_request.content.get("requestId")}

    async def handle_temporal_query(self, query_dicts, client_request, client, skip, results_per_page, debug_info):
        # TODO: First fetch the last query_dict query_dicts[-1]
        await client.send_progress_step("Fetching first query ...")
        mongo_query = await QueryFetcher.transform_to_mongo_query(query_dicts[-1], client, client_request, debug_info)
        total_results = client.db['images'].count_documents(mongo_query)
        # images = client.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1, "date": 1}).skip(skip).limit(results_per_page)
        images = client.db['images'].aggregate([
            {"$match": mongo_query},
            {
                "$sort": {"datetime": DESCENDING}  # Sort documents by datetime in descending order
            },
            {"$group": {
                "_id": "$date",
                "filepath": {"$first": "$filepath"},
                "datetime": {"$first": "$datetime"},
                "heart_rate": {"$first": "$heart_rate"}
            }},
            {"$project": {"_id": 0, "date": "$_id", "filepath": 1, "datetime": 1, "heart_rate": 1}},
            {"$skip": skip},
            {"$limit": results_per_page}
        ])
        if len(query_dicts) == 1:
            if client_request.version >= 2:
                results = list(images)
            else:
                results = [image.get('filepath') for image in images]
        else:
            # TODO: Iterate through the results
            result_images = []
            for image in images:
                await client.send_progress_step(f"Search on day {image.get('date')} ...")
                # TODO: Fetch the next query_dict on the same day (string field), but before the first one (time field) (the nearest to the last one)
                # TODO: Do this until end, then end it to the results
                nearest_image_on_same_day = image
                invalid_image = False
                found_images = [image]

                for query_dict in query_dicts[:-1]:
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

                    if "$and" not in mongo_query:
                        mongo_query["$and"] = []
                    # get only results on the same day
                    mongo_query.get("$and").append({"date": nearest_image_on_same_day.get("date")})
                    # add datetime is lower than the previous one
                    mongo_query.get("$and").append({"datetime": {"$lt": nearest_image_on_same_day.get("datetime")}})

                    # execute the mongo query with pagination
                    nearest_image_on_same_day = next(client.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1, "date": 1}).sort("datetime", -1).limit(1), None)
                    if not nearest_image_on_same_day:
                        invalid_image = True
                        break
                    found_images.append(nearest_image_on_same_day)

                if not invalid_image:
                    #result_images.append(image)
                    result_images.extend(found_images)

            if client_request.version >= 2:
                results = list(result_images)
            else:
                results = [image.get('filepath') for image in result_images]

        return {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info, "requestId": client_request.content.get("requestId")}