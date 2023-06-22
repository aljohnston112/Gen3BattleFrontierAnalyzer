import json
from collections import defaultdict
from os.path import exists
from typing import Dict

import cattr

from Config import POKEMON_TO_DAMAGE_TABLES
from data_class.Attack import Attack
from data_class.AttackDamageTable import AttackDamageTables, AttackDamageTable
from data_class.Category import Category
from data_source.pokemon_data_source import get_pokemon

pokemon_index_to_pokemon = get_pokemon()


def get_pokemon_to_damage_tables(level):
    pokemon_to_damage_tables = defaultdict(lambda: [])
    for index, pokemon in pokemon_index_to_pokemon.items():
        damage_tables = []
        hp = pokemon.all_stats.level_50_min_stats.health
        speed = pokemon.all_stats.level_50_min_stats.speed
        attack = pokemon.all_stats.level_50_min_stats.attack
        special_attack = pokemon.all_stats.level_50_min_stats.special_attack
        min_defense = 5
        max_defense = 230
        attacks: list[Attack] = []

        for attack_level, attack_list in pokemon.emerald_level_up_attacks.items():
            for a in attack_list:
                if attack_level < level:
                    attacks.append(a)

        if pokemon.tm_or_hm_to_attack is not None:
            attacks += pokemon.tm_or_hm_to_attack.values()

        if pokemon.egg_moves is not None:
            attacks += pokemon.egg_moves

        if pokemon.move_tutor_attacks is not None:
            attacks += pokemon.emerald_move_tutor_attacks

        if pokemon.special_attacks is not None:
            attacks += pokemon.special_attacks

        for move in attacks:
            move_type = move.pokemon_type
            power = move.power
            category = move.category
            if category != Category.STATUS:
                a = attack if category == Category.PHYSICAL else special_attack
                defense_to_health = dict()
                x = (((2.0 * level) / 5.0) + 2) * power * a
                for d in range(min_defense, max_defense + 1):
                    damage = ((x / d) / 50.0) + 2
                    if move_type in pokemon.pokemon_information.pokemon_types:
                        damage *= 1.5
                    defense_to_health[d] = damage
                damage_table = AttackDamageTable(
                    move_type=move.pokemon_type.name,
                    category=move.category.name,
                    defense_to_damage=defense_to_health
                )
                damage_tables.append(damage_table)
        pokemon_to_damage_tables[pokemon.pokemon_information.name].append(
            AttackDamageTables(
                pokemon=pokemon.pokemon_information.name,
                hp=hp,
                speed=speed,
                attack_damage_tables=damage_tables
            )
        )
    return pokemon_to_damage_tables


def load_all_pokemon_set_to_damage_tables(level):
    file_name = POKEMON_TO_DAMAGE_TABLES + str(level)
    if not exists(file_name):
        set_to_damage_tables = get_pokemon_to_damage_tables(level)
        with open(file_name, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(set_to_damage_tables)))
    else:
        with open(file_name, "r") as fo:
            set_to_damage_tables = cattr.structure(json.loads(fo.read()),  Dict[str, AttackDamageTables])
    return set_to_damage_tables


if __name__ == "__main__":
    level = 50
    set_to_damage_tables = load_all_pokemon_set_to_damage_tables(level)
    pass
