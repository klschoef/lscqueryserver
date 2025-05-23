# LSC Query Server (Backend)

The **LSC Query Server** is the core backend server of the LifeXplore Backend System. It processes queries via WebSocket communication and integrates with the CLIP, MongoDB, and optionally SOLR servers.

---

## **Requirements**
- Python 3.8 or higher.
- MongoDB and CLIP servers must be running (refer to their respective `README` files for setup).
- SOLR server must be running if description-based search is required.

---

## **Setup**

### **1. Install Python**
Ensure Python 3.8 or higher is installed on your system.

### **2. Configure the Environment**
1. Copy the example environment file and adjust the configuration:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with the following key parameters:
    - `MONGO_DB_URL`: MongoDB connection URL.
    - `MONGO_DB_DATABASE`: MongoDB database name.
    - `CLIP_URL`: URL of the running CLIP server.
    - `SOLR_URL`: URL of the SOLR server (if used).
    - Other parameters can be adjusted as needed.

---

## **Usage**

### **1. Start the Server**
Run the server using the following command:
```bash
python server.py
```
The server will use the configuration values from the `.env` file.

### **2. Development Mode**
For development purposes, use the `server_with_watchdog.py` script. This script automatically restarts the server whenever code changes are detected:
```bash
python server_with_watchdog.py
```

---

## **Additional Notes**
- Ensure all required servers (MongoDB, CLIP, and optionally SOLR) are running before starting the query server.
- Refer to the `README` files of the respective modules for detailed setup instructions.

## **Documentation**

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
    "locations": [
        {
            "query": "12.23,23.23"
        }
    ],
    "filename": "image.jpg",
    "year": "2020",
    "month": "12",
    "day": "01",
    "weekday": "sunday",
    "heart_rate": {
        "min": 60,
        "max": 80
    },
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


## Combine CLIP with MongoDB

Search n keyframes with CLIP, and use these n keyframes to search in MongoDB for the correct images.
We can use default pagination with mongoDB here, if we use all results from CLIP.

But results from CLIP can be very large, so we need a custom pagination.

Use maximal amount of clip results like n = 50.
Use these amount for MongoDB. Then we probably get less then 50 (page_size). So we need to fetch again 50 from CLIP, and do it
again with MongoDB. Repeat this step, until we get the correct amount of images.

But how we save the currentPage of the CLIP results (so we have a different page at clip)?

Save the current page of clip AND the regular current page.

### Example
search clip = "red car" and combine it with -o car
page_size = 50
current_page = 1
clip_search_k = 8000
clip_page_size = 2000 (adjust it, to minimize the amount of mongodb requests, but also minimize the size of a mondodb request (so it shouldn't be too large or too low))
current_clip_page = 1 (only used internally, don't make it controllable via the frontend)

1. Search with clip "red car" and get the first 2000 results
2. Use MongoDB query with object contains car, and file name needs to be in the clip results (array of filenames)
3. If we get less then 50 results, we increment the current_clip_page with 1, and use the next clip page with the mongodb query
4. Repeat step 3 until we get the correct amount of images
5. After that, return the new current_clip_page and the results. The logic for increment the current_page doesn't change in that case.

### How to get the next clip "page"
We need to search for the k best images (with clip_search_k). So we don't have pages here.
But we can use the results (amount of k), and paginate this result. We only do this, to decrease the mongodb request size.

Future research: One mongodb request with all filenames, or multiple requests with a smaller amount of filenames, and combine
it later. With one mongodb request, we can use the mongodb pagination. With multiple request we need to do it manually, but
we also can decrease the requests based on the current results.
But we can't order it by the score of objects or other precalculated values. (if we don't want to do each request).

## Temporary search
First we need to fetch the results from the latest part of the temporary search.
After that we fetch the part with index -1. Remove all resu

We get the day out of the file name, so for clip we can do it more easily
We don't need pagination for the sub-parts of the temporary search, because we only have one day.

### Example
query: red car -o car < rice bowl < beer < bed -o tv
Meaning: Search for a bed when the object tv is also in the query. Before in the day,
also a beer was visible. Before the beer a rice bowl is visible, and before the rice bows
a red car with an object car was visible. Each of them on the same day in this exact order.

1. Search for the last part bed -o tv (right amount of results (or more of them, because we loose some of them in the next steps))
2. For each resulting image, search for the clip query


50 results like 03.04.2021 18.45 clip found it for bed and in mongo db we have a tv as an object
For each result (in that case just the example)

## Query Log
A query log with all requests is stored in app/queries.log with the following format:
```
[timestamp]: [json_query]
[timestamp]: [json_query]
...
```

### Filter Query Log
To get a filtered query log to get all entries between timestamp 1718006958 - 1718013037, you can use the following command:
```
cd app
python3 filter-queries-log.py 1718006958 1718013037
```

The script also offers the following options (you get this info with the -h parameter)
```
usage: filter-queries-log.py [-h] [-i INPUT] [-o OUTPUT] start_timestamp end_timestamp

Filter log entries by timestamp range.

positional arguments:
  start_timestamp       Start timestamp (inclusive).
  end_timestamp         End timestamp (inclusive).

options:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file path (default: ./queries.log)
  -o OUTPUT, --output OUTPUT
                        Output file path (default: queries.log.filtered.[current_timestamp])
```

### Generate results from query log
To generate results from the query log, you can use the following command:
```
cd app
python3 generate-results-log.py path-to-your-queries.log
```

You will get the related response file (the script will fetch each query from the log file via the local websocket server (you also can specify the server with the parameters))

Usage (-h parameter):
```
usage: generate-results-log.py [-h] [--server_url SERVER_URL] [--response_log_file RESPONSE_LOG_FILE] log_file

Process and send log file entries to the lsc query server and save responses.

positional arguments:
  log_file              Path to the log file containing queries to send.

options:
  -h, --help            show this help message and exit
  --server_url SERVER_URL
                        WebSocket server URL (default: ws://localhost:8080).
  --response_log_file RESPONSE_LOG_FILE
                        File to save the responses from the server (default: response.[timestamp].log).

```