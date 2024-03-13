from core.query.filters.filter_heart_rate import FilterHeartRate
from core.query.filters.filter_objects import FilterObjects

default_filters = [
    FilterObjects(),
    FilterHeartRate()
]