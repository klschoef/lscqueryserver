import re

from pymongo import DESCENDING, ASCENDING

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
            if query:
                query_dicts = [TextQuerySerializer.text_query_to_dict(qd.strip(), client_request) for qd in query.split("<")]

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

        query_mode = client_request.content.get("queryMode", "All Images")
        l2dist = client_request.content.get("l2dist", 10 if query_mode == "distinctive" else (15 if query_mode == "moredistinctive" else None)) # query_mode query for backwards compatibility
        first_per_day = client_request.content.get("firstPerDay", query_mode == "first") # query_mode == first for backwards compatibility

        if l2dist:
            mongo_query["$and"].append({"l2dist": {"$gt": l2dist}})

        images = client.db['images'].aggregate(self.generate_mongo_pipeline(mongo_query, skip, results_per_page, group_by_date=first_per_day, client_request=client_request))

        if client_request.version >= 2:
            results = list(images)
        else:
            results = [image.get('filepath') for image in images]
        return {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info, "requestId": client_request.content.get("requestId")}

    async def handle_temporal_query(self, query_dicts, client_request, client, skip, results_per_page, debug_info):
        # check if information from mongo is needed
        no_mongo_query_required = True
        for query_dict in query_dicts:
            for key in query_dict.keys():
                if key == "clip" or key == "gpt" \
                        or query_dict.get(key) is None \
                        or query_dict.get(key) == [] \
                        or query_dict.get(key) == "":
                    continue
                no_mongo_query_required = False
                break
            if not no_mongo_query_required:
                break

        if no_mongo_query_required:
            filenames_per_part = [
                await QueryFetcher.transform_to_mongo_query(query_dict, client, client_request, debug_info)
                for query_dict in query_dicts]
            filenames_per_part = [m.get("$and", [])[0].get("filepath", {}).get("$in", []) for m in filenames_per_part if len(m.get("$and", [])) > 0]

            date_time_regex = r".*\/.*\/([0-9]{8})_([0-9]{6})"
            result_groups = []
            filenames_per_part = [
                [
                    {
                        "filename": p.get("filename"),
                        "date": p.get("date_time")[0],
                        "seconds_on_day": int(p.get("date_time")[1])
                    }
                    for p in [
                        {
                            "filename": part,
                            "date_time": re.findall(date_time_regex, part)[0],
                        } for part in part_objects]
                ]
                for part_objects in filenames_per_part
            ]

            block_counter = 1
            total_amount_results = len(filenames_per_part[-1])
            reversed_filenames = list(reversed(filenames_per_part))
            for part in reversed_filenames[0]:
                if block_counter % 1000 == 0:
                    await client.send_progress_step(f"Combine ({block_counter}/{total_amount_results}) ...")
                block_counter += 1
                date = part.get("date")
                seconds_on_day = part.get("seconds_on_day")
                last_seconds_on_day = seconds_on_day # value from the last part
                result_group = [part]

                found = True

                # fetch other parts and compare
                for other_parts in reversed_filenames[1:]:
                    temp_seconds_on_day = None
                    temp_part = None
                    for other_part in other_parts:
                        # compare
                        if date == other_part.get("date") and other_part.get("seconds_on_day") < last_seconds_on_day:
                            if not temp_seconds_on_day: # use it, if we have no other value
                                temp_seconds_on_day = other_part.get("seconds_on_day")
                                temp_part = other_part
                            elif other_part.get("seconds_on_day") > temp_seconds_on_day: # if we have a nearer value to the last one, use it
                                temp_seconds_on_day = other_part.get("seconds_on_day")
                                temp_part = other_part
                    if temp_seconds_on_day and temp_part:
                        last_seconds_on_day = temp_seconds_on_day
                        result_group.insert(0, temp_part)
                    else:
                        found = False
                        break

                if found:
                    result_groups.append(result_group)

            await client.send_progress_step(f"Start Fetching Process ...")
            # fetch the images
            results = []
            group_size = 0
            if len(result_groups) > 0:
                group_size = len(result_groups[0])
                filenames = [item.get("filename") for sublist in result_groups for item in sublist]
                paginated_filenames = filenames[skip:skip+results_per_page]
                ungrouped_results = list(client.db['images'].aggregate(self.generate_mongo_pipeline({"$and": [{"filepath": {"$in": paginated_filenames}}]}, 0, results_per_page, client_request=client_request)))
                total_results = len(filenames)
                group = 0
                group_count = 0
                current_date = None
                for result in paginated_filenames:
                    r = [r for r in ungrouped_results if r.get("filepath") == result]
                    if len(r) > 0:
                        r = r[0].copy()
                        datetime_string = r.get("filename")[:8]
                        if group_count < group_size and (current_date is None or current_date == datetime_string):
                            print(f"first")
                            current_date = datetime_string
                            r["group"] = group
                            group_count += 1
                        else:
                            print(f"second")
                            group += 1
                            group_count = 1
                            current_date = datetime_string
                            r["group"] = group
                        r["group_first"] = group_count == 1
                        r["group_last"] = group_count == group_size
                        results.append(r)


            return {"num": len(results), "group_size": group_size, "totalresults": total_results, "results": results, "debug_info": debug_info, "requestId": client_request.content.get("requestId")}

        # First fetch the last query_dict query_dicts[-1]
        await client.send_progress_step("Fetching first query ...")
        mongo_query = await QueryFetcher.transform_to_mongo_query(query_dicts[-1], client, client_request, debug_info)
        total_results = client.db['images'].count_documents(mongo_query)
        # images = client.db['images'].find(mongo_query, {"filepath": 1, "datetime": 1, "heart_rate": 1, "date": 1}).skip(skip).limit(results_per_page)
        images = client.db['images'].aggregate(self.generate_mongo_pipeline(mongo_query, skip, results_per_page, group_by_date=True, client_request=client_request))

        if len(query_dicts) == 1:
            if client_request.version >= 2:
                results = list(images)
            else:
                results = [image.get('filepath') for image in images]
        else:
            # Iterate through the results
            result_images = []
            for image in images:
                await client.send_progress_step(f"Search on day {image.get('date')} ...")
                # Fetch the next query_dict on the same day (string field), but before the first one (time field) (the nearest to the last one)
                # Do this until end, then end it to the results
                nearest_image_on_same_day = image
                invalid_image = False
                found_images = [image]

                for query_dict in query_dicts[:-1]:
                    # build the mongo query
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
                    result_images.extend(reversed(found_images))

            if client_request.version >= 2:
                results = list(result_images)
            else:
                results = [image.get('filepath') for image in result_images]

        return {"num": len(results), "totalresults": total_results, "results": results, "debug_info": debug_info, "requestId": client_request.content.get("requestId")}

    def generate_mongo_pipeline(self, mongo_query, skip, results_per_page, group_by_date=False, client_request=None):
        aggregate_pipeline = [
            {"$match": mongo_query},
        ]
        # add sorting to the pipeline, that we have the sort of the clip order, if we have a clip request, otherwise use just the datetime
        # TODO: add support for sorting by object score, text score, etc. (Maybe sorting by the first on in the list?)
        if mongo_query.get("$and") and mongo_query.get("$and")[0].get("filepath"):
            aggregate_pipeline.extend([
                {"$addFields": {
                    "sortOrder": {
                        "$indexOfArray": [
                            mongo_query.get("$and")[0].get("filepath").get("$in"),
                            "$filepath"
                        ]
                    }
                }},
                {"$sort": {"sortOrder": 1}}
            ])
        elif client_request and client_request.content and client_request.content.get("sorting"):
            sorting = client_request.content.get("sorting")
            aggregate_pipeline.append({"$sort": {sorting.get("field"): ASCENDING if sorting.get("order") == "asc" else DESCENDING}})
        else:
            aggregate_pipeline.append({"$sort": {"datetime": DESCENDING}})

        if group_by_date:
            aggregate_pipeline.extend([
                {"$group": {
                    "_id": "$date",
                    "filepath": {"$first": "$filepath"},
                    "datetime": {"$first": "$datetime"},
                    "heart_rate": {"$first": "$heart_rate"}
                }}
            ])

        aggregate_pipeline.extend([
            {"$project": {"_id": 0, "date": "$_id", "filepath": 1, "filename": 1, "datetime": 1, "heart_rate": 1}},
            {"$skip": skip},
            {"$limit": results_per_page}
        ])

        return aggregate_pipeline