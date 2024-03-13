# LSC Query Server

## Setup

## Documentation

### Query Dictionary
Each Query String can be converted to a dictionary with query_parts and subqueries like the example below.
```
{
    "clip": "red car",
    "objects": [
        {
            "query": "car",
            "subqueries": {
                "score": {
                    "min": 0.7,
                    "max": 0.9
                 }
                "position": "left-bottom"
            }
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
```

### Query Strings
The query string is a string that can be used to search for images or keyframes. 
It can be used to search for objects, texts, concepts, places, filenames, years, months, days, weekdays and querys with clip.
Example: "I want to have images where a object car is visible on the left bottom of the image, with a score between 0.7 and 0.9".
This can be reached with a query string like "-o car score:0.7+0.2 position:left-bottom".

Format: [free_text] [-[filter_char] [query_string]|[subquery]|[subquery]|...,[query_string]|[subquery]|[subquery]|...]

### Subqueries
Subqueries are a method to apply additional filtering steps to the query like 
"I want to have images where a object car is visible on the left bottom of the image, with a score between 0.7 and 0.9".

That subquery can be reached with a query string like "-o car score:0.7+0.2 position:left-bottom".
Or with a query_dict of
```
{
    "objects": [
        {
            "query": "car",
            "subqueries": {
                "score": {
                    "min": 0.7,
                    "max": 0.9
                },
                "position": "left-bottom"
            }
        }
    ]
}
```

### '<' parameter
The `<` parameter is used to specify which images or keyframes was shown before. Especially for video search it is useful, to find the correct keyframes.
Example Video: A car drives on a street, then we have a switch to a restaurant where a human eats something. The example query can be 'car street < restaurant human'.

In the case of lifelogs, we need to search in the same day, instead of the keyframes.

Current state:
- The < only use it with the clip server (it needs to get combined with the mongo db results, and query parts)
- There is a page size of 1234 currently for each part of the query

### Add a new filter
To add a new filter, you need to do a few simple steps:

1. Add the new filter to the `app/core/query/filters` which extends the FilterBase. 
Please use a name with the suffix `Filter` for the new filter.

```
import re

from core.query.filters.filter_base import FilterBase
from core.query.utils.filter_util import FilterUtil


class FilterObjects(FilterBase):
    REGEX = r'(-o [^\s]*)'

    """
    Remove the query part that is already handled by this filter, to avoid duplicate handling and increase performance
    If you want to keep the parts, just return the query
    """

    def remove_part_from_query(self, query):
        return re.sub(FilterObjects.REGEX, '', query).strip()

    """
    Logic to transform the query part to a dictionary and add it to the query_dict
    """

    def add_to_dict(self, query, query_dict):
        objects = re.findall(FilterObjects.REGEX, query)
        for obj in objects:
            query_parts = FilterUtil.parse_query_parts(obj, "-o")
            if query_parts:
                query_dict["objects"] = query_dict.get("objects", []) + query_parts

```

2. Add a instance of the new filter to the `app/core/query/default_filters.py` file.
```
from core.query.filters.filter_objects import FilterObjects

default_filters = [
    ...,  # other filters
    FilterObjects()
]
```

Now the new filter will be used.

### Add a new subquery
To add a new subquery, you need to do a few simple steps:
1. Add the new subquery to the `app/core/query/subfilters` which extends the SubfilterBase.
```
from core.query.subfilters.subfilter_base import SubfilterBase
from core.query.utils.range_value_util import RangeValueUtil


class SubfilterScore(SubfilterBase):
    def get_subfilter_name(self):
        return "score"

    def get_key_and_dict(self, subquery_string):
        subquery_value = self.get_subfilter_value(subquery_string)
        min_val, max_val = RangeValueUtil.parse_range_values(subquery_value)
        return self.get_subfilter_name(), {
            "min": min_val,
            "max": max_val
        }
```

2. Add a instance of the new subquery to the `app/core/query/default_subfilters.py` file.
```
from core.query.subfilters.subfilter_position import SubfilterPosition
from core.query.subfilters.subfilter_score import SubfilterScore

default_subfilters = [
    ...,  # other subfilters,
    SubfilterScore(),
]
```