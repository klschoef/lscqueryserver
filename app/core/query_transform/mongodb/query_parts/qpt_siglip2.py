from core import settings
from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.utils.clip_variants_util import ClipVariantsUtil
import copy


class QPTSigLIP2(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("siglip2")) and bool(query_dict.get("siglip2").get("query"))

    def needed_kwargs(self):
        return ["clip_connection", "message", "client"]

    async def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        clip_connection = kwargs.get("clip_connection")
        message = copy.deepcopy(kwargs.get("message"))
        message.get("content")["selectedpage"] = "1"
        message.get("content")["queryDefaultModel"] = "siglip2"
        message.get("content")["returnCLIPConfig"] = True
        client = kwargs.get("client")
        await clip_connection.ensure_query_model_loaded("siglip2", strict=True)

        variants_amount = int(query_dict.get("siglip2").get("subqueries", {}).get("variants", "0"))
        variant_results = []
        queries = [query_dict.get("siglip2").get("query")]
        api_key = settings.GPT_API_KEY

        if variants_amount > 0 and api_key:
            await client.send_progress_step("Generating SigLIP2 variants ...")
            queries += ClipVariantsUtil.fetch_variants(api_key, queries[0], variants_amount)
            debug_info["siglip2_variants"] = queries

        for query in queries:
            await client.send_progress_step(f"Query SigLIP2 with '{query}' ...")
            clip_page_size = message.get("content").get("clipPageSize") or 5000
            clip_response = await clip_connection.query(query, message, clip_page_size, clip_page_size)
            if clip_response.results or clip_response.results == []:
                variant_results.append(clip_response.results)
            returned_clip_config = clip_response.remote_response.get("clip_config")
            if returned_clip_config:
                debug_info["siglip2_config"] = returned_clip_config

        await client.send_progress_step("Combine SigLIP2 ...")
        common_results = []
        scores = []
        first_results = variant_results[0]
        for filename in first_results:
            skip = False
            score = 0
            for v_result in variant_results[1:]:
                try:
                    index = v_result.index(filename)
                    score += index
                except ValueError:
                    skip = True
                    break
            if not skip:
                common_results.append(filename)
                scores.append(score)

        if len(variant_results) > 1:
            common_results = [x for _, x in sorted(zip(scores, common_results))]

        mongo_query = {"filepath": {"$in": common_results}}

        if result_object.get("$and") is None:
            result_object["$and"] = [mongo_query]
        else:
            result_object["$and"].append(mongo_query)
