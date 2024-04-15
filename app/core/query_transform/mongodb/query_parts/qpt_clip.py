import json

from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.utils.clip_variants_util import ClipVariantsUtil

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('API_KEY')

class QPTClip(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("clip")) and bool(query_dict.get("clip").get("query"))

    def needed_kwargs(self):
        return ["clip_websocket", "message"]

    async def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        clip_websocket = kwargs.get("clip_websocket")
        message = kwargs.get("message")
        # TODO: replace CLIP logic with new one
        old_results_per_page = message.get("content").get("resultsperpage")
        old_max_results = message.get("content").get("maxresults")
        message.get("content")["resultsperpage"] = 5000
        message.get("content")["maxresults"] = 5000

        # TODO: fetch amount of variants from the variants subquery
        variants_amount = int(query_dict.get("clip").get("subqueries", {}).get("variants", "1"))
        variant_results = []
        queries = [query_dict.get("clip").get("query")]

        if variants_amount > 1 and api_key:
            # Do GPT variants generation
            queries += ClipVariantsUtil.fetch_variants(api_key, queries[0], variants_amount)
            debug_info["clip_variants"] = queries

        for query in queries:
            message.get("content")["query"] = query
            await clip_websocket.send(json.dumps(message))
            clip_response = await clip_websocket.recv()
            clip_response = json.loads(clip_response)
            if clip_response and clip_response.get("results") and len(clip_response.get("results")) > 0:
                variant_results.append(clip_response.get("results"))

        message.get("content")["resultsperpage"] = old_results_per_page
        message.get("content")["maxresults"] = old_max_results

        # Transform the results
        common_results = []
        first_results = variant_results[0]
        for filename in first_results:
            skip = False
            for v_result in variant_results[1:]:
               if filename not in v_result:
                   skip = True
                   break
            if not skip:
                common_results.append(filename)

        mongo_query = {"filepath": {"$in": common_results}}

        if result_object.get("$and") is None:
            result_object["$and"] = [mongo_query]
        else:
            result_object["$and"].append(mongo_query)
