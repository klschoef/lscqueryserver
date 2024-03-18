from core.query_transform.base.subqueries.sub_query_part_transformer_base import SubQueryPartTransformerBase


class SQPTPosition(SubQueryPartTransformerBase):

    def should_use(self, key, sub_query):
        return key == "position"

    def transform(self, result_object, sub_query, *args, **kwargs):
        # need for another precalculated field, because now we probably have bbox [top-left-x, top-left-y, width, height].
        # But to check if the bbox is in one range of the image, we need the 4 corners of the bbox
        # We also can use aggregate and add a field, but it's probably better to use a precalculated field
        # We also should add the width and height of the image to the image object

        # Another (maybe better approach) is to directly precalculate the position of the bbox within the image, and store it in the object like the bbox.
        # value array like [bottom-left, top-left] etc.
        # TODO: Clear these two options with the team
        pass
