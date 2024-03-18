from core.query_transform.mongodb.subqueries.sqpt_position import SQPTPosition
from core.query_transform.mongodb.subqueries.sqpt_score import SQPTScore

default_mongodb_sub_query_part_transformers = [
    SQPTScore(),
    SQPTPosition()
]