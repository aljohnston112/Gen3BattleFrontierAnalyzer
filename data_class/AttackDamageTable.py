from attr import frozen

from data_class.PokemonType import PokemonType


@frozen
class AttackDamageTable:
    category: str
    move_type: str
    defense_to_damage: dict
    move_name: str


@frozen
class AttackDamageTables:
    pokemon: str
    hp: int
    speed: int
    defense: int
    special_defense: int
    attack_damage_tables: list[AttackDamageTable]
    pokemon_types: list[PokemonType]
