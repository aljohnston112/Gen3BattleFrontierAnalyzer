from attr import frozen

from data_class.Category import Category
from data_class.PokemonType import PokemonType


@frozen
class Attack:
    name: str
    pokemon_type: PokemonType
    category: Category
    power: int
    accuracy: int
    effect_percent: int
