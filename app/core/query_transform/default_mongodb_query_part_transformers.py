from core.query_transform.mongodb.query_parts.qpt_clip import QPTClip
from core.query_transform.mongodb.query_parts.qpt_heart_rate import QPTHeartRate
from core.query_transform.mongodb.query_parts.qpt_objects import QPTObjects
from core.query_transform.mongodb.query_parts.qpt_texts import QPTTexts

default_mongodb_query_part_transformers = [
    QPTClip(),
    QPTObjects(),
    QPTHeartRate(),
    QPTTexts()
]