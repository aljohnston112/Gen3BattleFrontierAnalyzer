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
        defense = pokemon.all_stats.level_50_min_stats.defense
        special_defense = pokemon.all_stats.level_50_min_stats.special_defense

        min_defense = 9
        max_defense = 614
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
            if category != "status" and category != Category.STATUS and move.accuracy == 100 and \
                    move.name != "Razor Wind" and \
                    move.name != "Skull Bash" and \
                    move.name != "Sky Attack" and \
                    move.name != "Solarbeam" and \
                    move.name != "Rock Wrecker" and \
                    move.name != "Roar Of Time" and \
                    move.name != "Hyper Beam" and \
                    move.name != "Hydro Cannon" and \
                    move.name != "Giga Impact" and \
                    move.name != "Wood Hammer" and \
                    move.name != "Volt Tackle" and \
                    move.name != "Take Down" and \
                    move.name != "Submission" and \
                    move.name != "Selfdestruct" and \
                    move.name != "Head Smash" and \
                    move.name != "Flare Blitz" and \
                    move.name != "Double-edge" and \
                    move.name != "Brave Bird" and \
                    move.name != "Blast Burn" and \
                    move.name != "Endeavor" and \
                    move.name != "Dragon Rage" and \
                    move.name != "Super Fang" and \
                    move.name != "Sonicboom" and \
                    move.name != "Mirror Coat" and \
                    move.name != "Counter" and \
                    move.name != "Bide" and \
                    move.name != "Metal Burst" and \
                    move.name != "Gyro Ball" and \
                    move.name != "Magnitude" and \
                    move.name != "Horn Drill" and \
                    move.name != "Fissure" and \
                    move.name != "Sheer Cold" and \
                    move.name != "Guillotine" and \
                    move.name != "Natural Gift" and \
                    move.name != "Low Kick" and \
                    move.name != "Present" and \
                    move.name != "Seismic Toss" and \
                    move.name != "Night Shade" and \
                    move.name != "Punishment" and \
                    move.name != "Reversal" and \
                    move.name != "Flail" and \
                    move.name != "Trump Card" and \
                    move.name != "Fling" and \
                    move.name != "Wring Out" and \
                    move.name != "Frustration" and \
                    move.name != "Return" and \
                    move.name != "Spit Up" and \
                    move.name != "Hidden Power" and \
                    move.name != "Psywave" and \
                    move.name != "Crush Grip" and \
                    move.name != "Grass Knot" and \
                    move.name != "Belly Drum":
                a = attack if category == Category.PHYSICAL else special_attack
                defense_to_health = dict()
                x = (((2.0 * level) / 5.0) + 2) * power * a
                for d in range(min_defense, max_defense + 1):
                    damage = ((x / d) / 50.0) + 2
                    if move_type in pokemon.pokemon_information.pokemon_types:
                        damage *= 1.5
                    defense_to_health[d] = damage
                damage_table = AttackDamageTable(
                    move_name=move.name,
                    move_type=move.pokemon_type.name,
                    category=move.category.name,
                    defense_to_damage=defense_to_health
                )
                damage_tables.append(damage_table)
        pokemon_to_damage_tables[pokemon.pokemon_information.name].append(
            AttackDamageTables(
                pokemon=pokemon.pokemon_information.name,
                pokemon_types=pokemon.pokemon_information.pokemon_types,
                hp=hp,
                defense=defense,
                special_defense=special_defense,
                speed=speed,
                attack_damage_tables=damage_tables
            )
        )
    return pokemon_to_damage_tables


def load_all_pokemon_to_damage_tables(level):
    file_name = POKEMON_TO_DAMAGE_TABLES + str(level)
    if not exists(file_name):
        set_to_damage_tables = get_pokemon_to_damage_tables(level)
        with open(file_name, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(set_to_damage_tables)))
    else:
        with open(file_name, "r") as fo:
            set_to_damage_tables = cattr.structure(json.loads(fo.read()),  Dict[str, list[AttackDamageTables]])
    return set_to_damage_tables


if __name__ == "__main__":
    level = 50
    pokemon_to_damage_tables = load_all_pokemon_to_damage_tables(level)
    pass
