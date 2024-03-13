from core.query.subfilters.subfilter_position import SubfilterPosition
from core.query.subfilters.subfilter_score import SubfilterScore

default_subfilters = [
    SubfilterScore(),
    SubfilterPosition(),
]