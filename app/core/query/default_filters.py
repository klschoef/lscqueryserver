from core.query.filters.filter_clip import FilterClip
from core.query.filters.filter_gpt import FilterGPT
from core.query.filters.filter_heart_rate import FilterHeartRate
from core.query.filters.filter_objects import FilterObjects
from core.query.filters.filter_texts import FilterTexts

default_filters = [
    FilterObjects(),
    FilterTexts(),
    FilterHeartRate(),
    FilterClip(),
    FilterGPT()
]