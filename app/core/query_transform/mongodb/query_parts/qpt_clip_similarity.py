from core import settings
from core.query_transform.base.query_parts.query_part_transformer_base import QueryPartTransformerBase
from core.utils.clip_variants_util import ClipVariantsUtil
import copy

class QPTClipSimilarity(QueryPartTransformerBase):

    def should_use(self, query_dict):
        return bool(query_dict.get("sim"))

    def needed_kwargs(self):
        return ["clip_connection", "message", "client"]

    async def transform(self, result_object, query_dict, debug_info, *args, **kwargs):
        clip_connection = kwargs.get("clip_connection")
        message = copy.deepcopy(kwargs.get("message"))
        message.get("content")["selectedpage"] = "1"
        client = kwargs.get("client")

        query = query_dict.get("sim")
        clip_page_size = message.get("content").get("clipPageSize") or 5000

        common_results = []

        await client.send_progress_step("Start similarity search with clip ...")
        clip_response = await clip_connection.query(query, message, clip_page_size, clip_page_size, event_type="file-similarityquery", pathprefix="")
        if clip_response.results:
            common_results = clip_response.results


        await client.send_progress_step("Start DB Query ...")

        mongo_query = {"filepath": {"$in": common_results}}

        if result_object.get("$and") is None:
            result_object["$and"] = [mongo_query]
        else:
            result_object["$and"].append(mongo_query)
