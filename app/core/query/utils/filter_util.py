from core.query.subfilter_handler import SubfilterHandler


class FilterUtil:
    """
    Parses the query string and returns a list of subqueries.
    Example: -o car|score:0.5+-0.1|position:left-bottom,car|score:0.4
    Format: -o <query>|<subquery1>,<query>|<subquery2> (without spaces)

    Output: List of query part objects like for "-o car|score:0.5+-0.1"
    [
     {
        "query": "car",
        "score": {
            "min": 0.4,
            "max": 0.6
        },
     }
    ]
    """

    @staticmethod
    def get_query_and_subqueries(query_parts, key):
        object_raw_parts = [p.strip() for p in query_parts.get(key).split(" ") if p != '']
        objects = []
        for raw_object in object_raw_parts:
            query_and_subqueries = raw_object.split("|")
            object = {
                "query": query_and_subqueries[0],
                "subqueries": {}
            }

            for sub in query_and_subqueries[1:]:
                key, value = SubfilterHandler.subfilter_handler(sub)
                object["subqueries"][key] = value

            objects.append(object)
        return objects

    @staticmethod
    def parse_query_parts(query, prefix):
        # example query string: -o car|score:0.5+-0.1|position:left-bottom,car|score:0.4

        query_parts = []
        # remove prefix
        query = query.replace(prefix, "").strip()

        # iterate through each query part (multiple query values separated by comma)
        for query_part in query.split(","):  # Example query_part string: car|score:0.5+-0.1|position:left-bottom
            # get possible subqueries
            subquery_strings = query_part.split("|")
            # the first one is the main query
            main_query = subquery_strings[0]

            # everything behind the first one is a subquery
            subquery_strings = subquery_strings[1:]

            # add the main query to the query part dict
            query_part_dict = {
                "query": main_query,
                "subqueries": {}
            }

            # parse each subquery
            for subquery_string in subquery_strings:
                key, value = SubfilterHandler.subfilter_handler(subquery_string)
                if key:
                    query_part_dict.get("subqueries")[key] = value
            query_parts.append(query_part_dict)

        return query_parts
