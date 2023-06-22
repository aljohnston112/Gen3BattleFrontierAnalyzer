from enum import unique, Enum


@unique
class Category(Enum):
    """
    Represents whether a Pokemon move of physical or special.
    """
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"


physical_types = ["normal", "fighting", "poison", "ground", "flying", "bug", "rock", "ghost", "steel"]
special_types = ["fire", "water", "electric", "grass", "ice", "psychic", "dragon", "dark"]


def convert_to_attack_category(pokemon_type):
    return Category.PHYSICAL if pokemon_type.lower() in physical_types else Category.SPECIAL
