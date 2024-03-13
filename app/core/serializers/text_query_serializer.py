from core.query.default_filters import default_filters


class TextQuerySerializer:

    @staticmethod
    def text_query_to_dict(text_query, filters=default_filters):
        query_dict = {
            "clip": None,
            "objects": [],
            "texts": [],
            "concepts": [],
            "places": [],
            "filename": None,
            "year": None,
            "month": None,
            "day": None,
            "weekday": None
        }

        # apply filters to get the query_dict from the text query
        for current_filter in filters:
            current_filter.add_to_dict(text_query, query_dict)
            text_query = current_filter.remove_part_from_query(text_query)

        return query_dict
