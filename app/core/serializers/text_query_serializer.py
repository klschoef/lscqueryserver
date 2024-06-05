from core.query.default_filters import default_filters
import re


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
            "weekday": None,
            "heart_rate": None,
        }

        split_regex = r"(-([^\s]+)([^-]*))"

        commands = re.findall(split_regex, text_query)
        commands = {entry[1]:entry[2] for entry in commands if len(entry) > 2}
        clip_command = re.findall(r"^([^-]*)", text_query)

        if clip_command and len(clip_command) > 0:
            commands["clip"] = clip_command[0].strip()

        # apply filters to get the query_dict from the text query
        for current_filter in filters:
            current_filter.add_to_dict(text_query, query_dict, commands)

        return query_dict
