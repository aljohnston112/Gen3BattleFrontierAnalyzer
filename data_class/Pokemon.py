from typing import Dict, List, Optional

import attr
from attr import frozen

from data_class.AllStats import AllStats
from data_class.Attack import Attack
from data_class.PokemonInformation import PokemonInformation


@frozen
class Pokemon:
    pokemon_information: PokemonInformation
    all_stats: AllStats
    fr_level_to_attacks: Dict[int, List[Attack]]
    lg_level_to_attacks: Dict[int, List[Attack]]
    rs_level_to_attacks: Dict[int, List[Attack]]
    emerald_level_up_attacks: Dict[int, List[Attack]]

    tm_or_hm_to_attack: Optional[Dict[str, Attack]] = attr.field(default=None)
    move_tutor_attacks: Optional[List[Attack]] = attr.field(default=None)
    emerald_move_tutor_attacks: Optional[List[Attack]] = attr.field(default=None)
    egg_moves: Optional[List[Attack]] = attr.field(default=None)
    special_attacks: Optional[List[Attack]] = attr.field(default=None)
    attack_form_stats: Optional[AllStats] = attr.field(default=None)
    defence_form_stats: Optional[AllStats] = attr.field(default=None)
    speed_form_stats: Optional[AllStats] = attr.field(default=None)

