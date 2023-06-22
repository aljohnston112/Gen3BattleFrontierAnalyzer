from attr import frozen

from data_class.BaseStats import BaseStats
from data_class.Stats import Stats


@frozen
class AllStats:
    name: str
    base_stats: BaseStats
    level_50_min_stats: Stats
    level_50_max_stats: Stats
    level_100_min_stats: Stats
    level_100_max_stats: Stats
