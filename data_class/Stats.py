from attr import frozen


@frozen
class Stats:
    """
    Represents the base stats of a Pokemon.
    """

    name: str
    """
    The name of the Pokemon.
    """

    health: int
    """
    The base health of the pokemon
    """

    attack: int
    """
    The base attack of the pokemon
    """

    defense: int
    """
    The base defense of the pokemon
    """

    special_attack: int
    """
    The base special attack of the pokemon
    """

    special_defense: int
    """
    The base special defense of the pokemon
    """

    speed: int
    """
    The base speed of the pokemon    
    """