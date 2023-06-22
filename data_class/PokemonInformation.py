from attr import frozen

from data_class.PokemonType import PokemonType


@frozen
class PokemonInformation:
    name: str
    pokemon_types: list[PokemonType]
    id: int
    ability: str
    pounds: float
