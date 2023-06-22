import json
from collections import defaultdict
from math import floor
from os.path import exists
from typing import Dict

import cattr

from Config import SET_TO_POKEMON_TO_DAMAGE_TABLES
from data_class.AttackDamageTable import AttackDamageTable, AttackDamageTables
from data_class.Category import Category
from data_source.PokemonIndexDataSource import get_pokemon_name_to_index
from data_source.frontier_pokemon_data_source import get_set_to_frontier_pokemon
from data_source.pokemon_data_source import get_pokemon

set_number_to_pokemon = get_set_to_frontier_pokemon()
pokemon_name_to_index = get_pokemon_name_to_index()
pokemon_index_to_pokemon = get_pokemon()


def get_attack_multiplier(nature: str):
    m = 1.0
    if nature in ["Lonely", "Brave", "Adamant", "Naughty"]:
        m = 1.1
    elif nature in ["Bold", "Timid", "Modest", "Calm"]:
        m = 0.9
    return m


def get_special_attack_multiplier(nature: str):
    m = 1.0
    if nature in ["Modest", "Mild", "Quiet", "Rash"]:
        m = 1.1
    elif nature in ["Adamant", "Impish", "Jolly", "Careful"]:
        m = 0.9
    return m


def get_defense_multiplier(nature: str):
    m = 1.0
    if nature in ["Bold", "Relaxed", "Impish", "Lax"]:
        m = 1.1
    elif nature in ["Lonely", "Hasty", "Mild", "Gentle"]:
        m = 0.9
    return m


def get_special_defense_multiplier(nature: str):
    m = 1.0
    if nature in ['Calm', 'Gentle', 'Sassy', "Careful"]:
        m = 1.1
    elif nature in ["Naughty", "Lax", "Naive", "Rash"]:
        m = 0.9
    return m


def get_speed_multiplier(nature):
    m = 1.0
    if nature in ["Timid", "Hasty", "Jolly", "Naive"]:
        m = 1.1
    elif nature in ["Brave", "Relaxed", "Quiet", "Sassy"]:
        m = 0.9
    return m


def get_iv_for_frontier_pokemon(set_number):
    return (set_number + 2) * 3


def get_hp_for_frontier_trainer(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_health = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.health
    iv = get_iv_for_frontier_pokemon(set_number)
    ev = pokemon["hp_ev"]
    hp = floor(((2.0 * base_health + iv + floor(ev / 4.0)) * level) / 100.0) + level + 10
    return hp


def get_stat_for_frontier_pokemon(base, iv, ev, level):
    return floor(((2.0 * base + iv + floor(ev / 4.0)) * level) / 100.0) + 5


def get_attack_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_attack = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.attack
    iv = get_iv_for_frontier_pokemon(set_number)
    ev = pokemon['attack_ev']
    return floor(
        get_stat_for_frontier_pokemon(base_attack, iv, ev, level) *
        get_attack_multiplier(pokemon['nature'])
    )


def get_special_attack_for_frontier_pokemon(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_attack = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.special_attack
    iv = get_iv_for_frontier_pokemon(set_number)
    ev = pokemon["special_attack_ev"]
    return floor(
        get_stat_for_frontier_pokemon(base_attack, iv, ev, level) *
        get_special_attack_multiplier(pokemon['nature'])
    )


def get_speed_for_frontier_trainer(level, set_number, pokemon):
    pokemon_index = pokemon_name_to_index[pokemon['name']]
    base_speed = pokemon_index_to_pokemon[pokemon_index].all_stats.base_stats.stats.speed
    iv = get_iv_for_frontier_pokemon(set_number)
    ev = pokemon['speed_ev']
    return floor(
        get_stat_for_frontier_pokemon(base_speed, iv, ev, level) *
        get_speed_multiplier(pokemon['nature'])
    )


def get_all_moves(pokemon):
    moves = []

    for attacks in pokemon.fr_level_to_attacks.values():
        for attack in attacks:
            moves.append(attack)

    for attacks in pokemon.lg_level_to_attacks.values():
        for attack in attacks:
            moves.append(attack)

    for attacks in pokemon.rs_level_to_attacks.values():
        for attack in attacks:
            moves.append(attack)

    for attacks in pokemon.emerald_level_up_attacks.values():
        for attack in attacks:
            moves.append(attack)

    if pokemon.tm_or_hm_to_attack is not None:
        for attack in pokemon.tm_or_hm_to_attack.values():
            moves.append(attack)

    if pokemon.move_tutor_attacks is not None:
        for attack in pokemon.move_tutor_attacks:
            moves.append(attack)

    if pokemon.emerald_move_tutor_attacks is not None:
        for attack in pokemon.emerald_move_tutor_attacks:
            moves.append(attack)

    if pokemon.egg_moves is not None:
        for attack in pokemon.egg_moves:
            moves.append(attack)

    if pokemon.special_attacks is not None:
        for attack in pokemon.special_attacks:
            moves.append(attack)

    return moves


def find_move(index, move_name):
    moves = get_all_moves(pokemon_index_to_pokemon[str(index)])
    found = None
    for move in moves:
        if move.name.lower() == move_name.lower():
            found = move

    if not found:
        found = find_move(index - 1, move_name)

    assert found is not None

    return found


def get_set_to_damage_tables(level):
    set_number_to_damage_table = defaultdict(lambda: [])
    for set_number, pokemon_list in set_number_to_pokemon[0].items():
        for pokemon in pokemon_list:
            pokemon['name'] = pokemon['name'].replace("’", "'")
            damage_tables = []
            hp = get_hp_for_frontier_trainer(level, int(set_number), pokemon)
            speed = get_speed_for_frontier_trainer(level, int(set_number), pokemon)
            attack = get_attack_for_frontier_pokemon(level, int(set_number), pokemon)
            special_attack = get_special_attack_for_frontier_pokemon(level, int(set_number), pokemon)
            min_defense = 5
            max_defense = 230
            for move in pokemon['move_names']:
                if move != "-":
                    move = find_move(pokemon["index"], move)
                    move_type = move.pokemon_type
                    power = move.power
                    category = move.category
                    if category != Category.STATUS:
                        a = attack if category == Category.PHYSICAL else special_attack
                        defense_to_health = dict()
                        x = (((2.0 * level) / 5.0) + 2) * power * a
                        for d in range(min_defense, max_defense + 1):
                            damage = ((x / d) / 50.0) + 2
                            if move_type in pokemon_index_to_pokemon[str(pokemon["index"])].pokemon_information.pokemon_types:
                                damage *= 1.5
                            defense_to_health[d] = damage
                        damage_table = AttackDamageTable(
                            move_type=move_type.value,
                            category=move.category.value,
                            defense_to_damage=defense_to_health
                        )
                        damage_tables.append(damage_table)
            set_number_to_damage_table[set_number].append(
                AttackDamageTables(
                    pokemon=pokemon['name'],
                    hp=hp,
                    speed=speed,
                    attack_damage_tables=damage_tables
                )
            )
    return set_number_to_damage_table


def load_frontier_set_to_damage_tables(level) -> Dict[int, AttackDamageTables]:
    file_name = SET_TO_POKEMON_TO_DAMAGE_TABLES + str(level)
    if not exists(file_name):
        set_to_damage_tables = get_set_to_damage_tables(level)
        with open(file_name, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(set_to_damage_tables)))
    else:
        with open(file_name, "r") as fo:
            set_to_damage_tables = cattr.structure(json.loads(fo.read()),  Dict[int, AttackDamageTables])
    return set_to_damage_tables


if __name__ == "__main__":
    level = 50
    set_to_damage_tables = load_frontier_set_to_damage_tables(level)
    pass


