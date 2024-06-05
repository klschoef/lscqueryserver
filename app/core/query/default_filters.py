from core.query.filters.filter_address import FilterAddress
from core.query.filters.filter_clip import FilterClip
from core.query.filters.filter_country import FilterCountry
from core.query.filters.filter_day import FilterDay
from core.query.filters.filter_filename import FilterFilename
from core.query.filters.filter_gpt import FilterGPT
from core.query.filters.filter_gptr import FilterGPTR
from core.query.filters.filter_gptra import FilterGPTRA
from core.query.filters.filter_heart_rate import FilterHeartRate
from core.query.filters.filter_hour import FilterHour
from core.query.filters.filter_month import FilterMonth
from core.query.filters.filter_objects import FilterObjects
from core.query.filters.filter_places import FilterPlaces
from core.query.filters.filter_texts import FilterTexts
from core.query.filters.filter_weekday import FilterWeekday
from core.query.filters.filter_year import FilterYear

default_filters = [
    FilterObjects(),
    FilterTexts(),
    FilterHeartRate(),
    FilterClip(),
    FilterGPT(),
    FilterAddress(),
    FilterCountry(),
    FilterDay(),
    FilterFilename(),
    FilterGPTR(),
    FilterGPTRA(),
    FilterHour(),
    FilterMonth(),
    FilterPlaces(),
    FilterWeekday(),
    FilterYear()
]