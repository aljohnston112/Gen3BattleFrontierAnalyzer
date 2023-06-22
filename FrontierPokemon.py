from attr import frozen


@frozen
class FrontierPokemon:
    index: int
    name: str
    item: str
    move_names: list[str]
    nature: str
    hp_ev: int
    attack_ev: int
    defense_ev: int
    special_attack_ev: int
    special_defense_ev: int
    speed_ev: int
