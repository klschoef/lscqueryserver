from core.query_transform.mongodb.query_parts.qpt_address import QPTAddress
from core.query_transform.mongodb.query_parts.qpt_clip import QPTClip
from core.query_transform.mongodb.query_parts.qpt_concepts import QPTConcepts
from core.query_transform.mongodb.query_parts.qpt_country import QPTCountry
from core.query_transform.mongodb.query_parts.qpt_day import QPTDay
from core.query_transform.mongodb.query_parts.qpt_filename import QPTFilename
from core.query_transform.mongodb.query_parts.qpt_gpt import QPTGPT
from core.query_transform.mongodb.query_parts.qpt_gptr import QPTGPTR
from core.query_transform.mongodb.query_parts.qpt_gptra import QPTGPTRA
from core.query_transform.mongodb.query_parts.qpt_heart_rate import QPTHeartRate
from core.query_transform.mongodb.query_parts.qpt_month import QPTMonth
from core.query_transform.mongodb.query_parts.qpt_objects import QPTObjects
from core.query_transform.mongodb.query_parts.qpt_places import QPTPlaces
from core.query_transform.mongodb.query_parts.qpt_texts import QPTTexts
from core.query_transform.mongodb.query_parts.qpt_weekday import QPTWeekday
from core.query_transform.mongodb.query_parts.qpt_year import QPTYear

default_mongodb_query_part_transformers = [
    QPTClip(),
    QPTObjects(),
    QPTHeartRate(),
    QPTTexts(),
    QPTConcepts(),
    QPTPlaces(),
    QPTFilename(),
    QPTYear(),
    QPTMonth(),
    QPTDay(),
    QPTWeekday(),
    QPTAddress(),
    QPTCountry(),
    QPTGPTR(),
    QPTGPTRA(),
    QPTGPT()
]