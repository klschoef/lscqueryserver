from core import settings
from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.utils.clip_variants_util import ClipVariantsUtil

class QPTClip(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("clip")) and bool(query_dict.get("clip").get("query"))

    def needed_kwargs(self):
        return ["clip_connection", "message", "client"]

    async def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        clip_connection = kwargs.get("clip_connection")
        message = kwargs.get("message")
        client = kwargs.get("client")

        # fetch amount of variants from the variants subquery
        variants_amount = int(query_dict.get("clip").get("subqueries", {}).get("variants", "1"))
        variant_results = []
        queries = [query_dict.get("clip").get("query")]
        api_key = settings.GPT_API_KEY

        if variants_amount > 1 and api_key:
            # Do GPT variants generation
            await client.send_progress_step("Generating clip variants ...")
            queries += ClipVariantsUtil.fetch_variants(api_key, queries[0], variants_amount)
            debug_info["clip_variants"] = queries

        for query in queries:
            await client.send_progress_step(f"Query Clip with '{query}' ...")
            clip_response = await clip_connection.query(query, message, 5000, 5000)
            if clip_response.results:
                variant_results.append(clip_response.results)

        await client.send_progress_step("Combine Clip ...")
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
