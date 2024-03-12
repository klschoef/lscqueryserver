import re

class TextQuerySerializer:
    REGEX_OBJECTS = r'(-o [^\s]*)'
    REGEX_TEXTS = r'(-t [^\s]*)'
    REGEX_SUBQUERY_SCORE = r'score:([0-9]+[.[0-9]+]{0,1})(.*)' # group of main number and the rest score:0.5+0.1-0.2 = 0.5, +0.1-0.2

    @staticmethod
    def get_option_parts(option):
        pass

    @staticmethod
    def text_query_to_dict(text_query):
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
        # Example: red car -o car,person -t audi
        # fetch all objects, and the reminding stuff is the clip query
        objects = re.findall(TextQuerySerializer.REGEX_OBJECTS, text_query)

        for obj in objects:
            # -o car|score:0.5+-0.1|position:left-bottom,car|score:0.4
            obj = obj.replace("-o ", "")
            for obj_part in obj.split(","):
                # car|score:0.5+-0.1|position:left-bottom
                subqueries = obj_part.split("|")
                main_query = subqueries[0]
                subqueries = subqueries[1:]
                query_dict["objects"].append({
                    "query": main_query,
                    "score": {
                        "min": None,
                        "max": None
                    },
                    "position": None
                })



        return {
            "clip": "red car",
            "objects": [
                {
                    "query": "car",
                    "score": "0.5+-0.1",
                    "position": "left-bottom"
                }
            ],
            "texts": [
                {
                    "query": "audi"
                }
            ],
            "concepts": [
                {
                    "query": "car"
                }
            ],
            "places": [
                {
                    "query": "Portugal"
                }
            ],
            "filename": "image.jpg",
            "year": "2020",
            "month": "12",
            "day": "01",
            "weekday": "sunday",
        }