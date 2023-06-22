from attr import frozen


@frozen
class AttackDamageTable:
    category: str
    move_type: str
    defense_to_damage: dict


@frozen
class AttackDamageTables:
    pokemon: str
    hp: int
    speed: int
    attack_damage_tables: list[AttackDamageTable]
