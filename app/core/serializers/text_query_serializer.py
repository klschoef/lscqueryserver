from core.query.default_filters import default_filters
import re


class TextQuerySerializer:

    @staticmethod
    def text_query_to_dict(text_query, client_request, filters=default_filters):
        query_dict = {
            "clip": None,
            "siglip2": None,
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
        command_prefix_char = client_request.content.get("textCommandPrefix", "-")
        modified_query = f"{' ' if text_query.startswith(command_prefix_char) else ''}{text_query}"
        modified_query = modified_query.replace(f" {command_prefix_char}", f" |°^|°^").split(f" |°^")
        split_regex = r"^\|\°\^([^\s]+)\s(.*)"

        commands = {}
        default_query_model = client_request.content.get("queryDefaultModel")
        if default_query_model not in ["clip", "gpt", "siglip2"]:
            default_query_model = "gpt" if client_request.content.get("useGPTasDefault") else "clip"

        for part in modified_query:
            if part.startswith("|°^"):
                find_results = re.findall(split_regex, part.strip())
                if find_results and len(find_results) == 1 and len(find_results[0]) == 2:
                    commands[find_results[0][0]] = find_results[0][1]
            else:
                commands[default_query_model] = part.strip()


        # apply filters to get the query_dict from the text query
        for current_filter in filters:
            current_filter.add_to_dict(text_query, query_dict, commands)

        return query_dict
