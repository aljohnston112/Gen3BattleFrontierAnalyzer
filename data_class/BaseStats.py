from attr import frozen

from data_class.Stats import Stats


@frozen
class BaseStats:
    name: str
    stats: Stats
