from enum import Enum, unique


@unique
class PokemonType(Enum):
    """
    Represents the Pokemon types.
    """
    NORMAL = "normal"
    FIGHTING = "fighting"
    FLYING = "flying"
    POISON = "poison"
    GROUND = "ground"
    ROCK = "rock"
    BUG = "bug"
    GHOST = "ghost"
    STEEL = "steel"
    FIRE = "fire"
    WATER = "water"
    GRASS = "grass"
    ELECTRIC = "electric"
    PSYCHIC = "psychic"
    ICE = "ice"
    DRAGON = "dragon"
    DARK = "dark"


__TYPE_DICT__ = {
    "normal": PokemonType.NORMAL,
    "fighting": PokemonType.FIGHTING,
    "flying": PokemonType.FLYING,
    "poison": PokemonType.POISON,
    "ground": PokemonType.GROUND,
    "rock": PokemonType.ROCK,
    "bug": PokemonType.BUG,
    "curse": PokemonType.GHOST,
    "ghost": PokemonType.GHOST,
    "steel": PokemonType.STEEL,
    "fire": PokemonType.FIRE,
    "water": PokemonType.WATER,
    "grass": PokemonType.GRASS,
    "electric": PokemonType.ELECTRIC,
    "psychic": PokemonType.PSYCHIC,
    "ice": PokemonType.ICE,
    "dragon": PokemonType.DRAGON,
    "dark": PokemonType.DARK,
}

pokemon_types = [t for t in PokemonType]


def convert_to_pokemon_type(pokemon_type: str) -> PokemonType:
    """
    Gets the enum representing a Pokemon type.
    :param pokemon_type: The string of the type.
    :return: The enum representing pokemon_type.
    """
    return __TYPE_DICT__[pokemon_type.lower()]
