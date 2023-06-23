import copy
import json
from collections import defaultdict
from os.path import exists

from Config import SET_TO_POKEMON_TO_MOVE_TO_RANK_FILE, SET_TO_POKEMON_TO_MOVES_AND_RANKS
from TypeChartDataSource import get_defender_type_dict
from data_source.frontier_defense_table_data_source import load_frontier_set_to_damage_tables
from data_source.PokemonAttackDamageDataSource import get_pokemon_to_damage_tables

level = 50
pokemon_to_damage_tables = get_pokemon_to_damage_tables(level)
set_to_damage_tables = load_frontier_set_to_damage_tables(level)
defender_type_chart = get_defender_type_dict()

defense_multiplier_cache = dict()


def get_defense_multipliers_for_type(
        pokemon_type: str,
        current_defense_multipliers=None
):
    safe_to_cache = False
    cached = False
    if current_defense_multipliers is None:
        safe_to_cache = True
        current_defense_multipliers = defense_multiplier_cache.get(pokemon_type, None)
        if current_defense_multipliers is None:
            current_defense_multipliers = defaultdict(lambda: 1.0)
        else:
            cached = True

    if not cached:
        current_defense_multipliers = copy.deepcopy(current_defense_multipliers)
        # [no_eff, not_eff, normal_eff, super_eff]
        no_effect_types = defender_type_chart[0].get(pokemon_type, [])
        not_effective_types = defender_type_chart[1].get(pokemon_type, [])
        normal_effective_types = defender_type_chart[2].get(pokemon_type, [])
        super_effective_types = defender_type_chart[3].get(pokemon_type, [])
        for no_effect_type in no_effect_types:
            current_defense_multipliers[no_effect_type] *= 0.0
        for not_effective_type in not_effective_types:
            current_defense_multipliers[not_effective_type] *= 0.5
        for normal_effective_type in normal_effective_types:
            current_defense_multipliers[normal_effective_type] *= 1.0
        for super_effective_type in super_effective_types:
            current_defense_multipliers[super_effective_type] *= 2.0
        if safe_to_cache:
            defense_multiplier_cache[pokemon_type] = current_defense_multipliers

    return current_defense_multipliers


defense_multipliers_cache = dict()


def get_defense_multipliers_for_types(defender_types: frozenset[str]):
    defense_multipliers = defense_multipliers_cache.get(defender_types, None)
    if defense_multipliers is None:
        for defender_type in defender_types:
            defense_multipliers = get_defense_multipliers_for_type(defender_type, defense_multipliers)
        defense_multipliers_cache[defender_types] = defense_multipliers
    return defense_multipliers


def get_pokemon_to_category_to_type_to_damage_table():
    pokemon_to_category_to_type_to_damage_table = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(lambda: ("", defaultdict(lambda: 0)))
        )
    )
    for pokemon_name, damage_tables_singleton in pokemon_to_damage_tables.items():
        pokemon_damage_tables = damage_tables_singleton[0]
        for pokemon_damage_table in pokemon_damage_tables.attack_damage_tables:
            current_best = pokemon_to_category_to_type_to_damage_table[
                pokemon_name
            ][pokemon_damage_table.category][pokemon_damage_table.move_type][1][10]
            if pokemon_damage_table.defense_to_damage[10] > current_best:
                pokemon_to_category_to_type_to_damage_table[
                    pokemon_name
                ][pokemon_damage_table.category][pokemon_damage_table.move_type] = \
                    (pokemon_damage_table.move_name, pokemon_damage_table.defense_to_damage)
    return pokemon_to_category_to_type_to_damage_table


def rank_pokemon(pokemon_to_category_to_type_to_damage_table):
    set_to_pokemon_to_move_to_rank = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0)))
    for pokemon, pokemon_category_to_type_to_damage_table in pokemon_to_category_to_type_to_damage_table.items():
        pokemon_hp = pokemon_to_damage_tables[pokemon][0].hp
        pokemon_defense = pokemon_to_damage_tables[pokemon][0].defense
        pokemon_special_defense = pokemon_to_damage_tables[pokemon][0].special_defense
        pokemon_speed = pokemon_to_damage_tables[pokemon][0].speed
        pokemon_defense_multipliers = get_defense_multipliers_for_types(
            frozenset([t.name.lower() for t in pokemon_to_damage_tables[pokemon][0].pokemon_types])
        )
        for set_number, frontier_damage_tables in set_to_damage_tables.items():
            for opponent_damage_tables in frontier_damage_tables:
                opponent_hp = opponent_damage_tables.hp
                opponent_defense = opponent_damage_tables.defense
                opponent_special_defense = opponent_damage_tables.special_defense
                opponent_speed = opponent_damage_tables.speed
                opponent_defense_multipliers = get_defense_multipliers_for_types(
                    frozenset([t.name.lower() for t in opponent_damage_tables.pokemon_types])
                )
                max_damage_opponent_can_do = 0
                for opponent_attack_damage_table in opponent_damage_tables.attack_damage_tables:
                    category = opponent_attack_damage_table.category
                    move_type = opponent_attack_damage_table.move_type
                    attack_multiplier = pokemon_defense_multipliers[move_type]
                    if category == 'special':
                        max_damage_opponent_can_do = max(
                            max_damage_opponent_can_do,
                            opponent_attack_damage_table.defense_to_damage[pokemon_special_defense] *
                            attack_multiplier
                        )
                    else:
                        max_damage_opponent_can_do = max(
                            max_damage_opponent_can_do,
                            opponent_attack_damage_table.defense_to_damage[pokemon_defense] *
                            attack_multiplier
                        )

                for pokemon_attack_category, pokemon_attack_type_to_name_and_damage_table \
                        in pokemon_category_to_type_to_damage_table.items():
                    for pokemon_attack_type, pokemon_attack_name_and_damage_table \
                            in pokemon_attack_type_to_name_and_damage_table.items():
                        opponent_defense_multiplier = \
                            opponent_defense_multipliers[pokemon_attack_type.lower()]
                        move_name = pokemon_attack_name_and_damage_table[0]

                        if pokemon_attack_category.lower() == "physical":
                            damage_to_opponent = \
                                pokemon_attack_name_and_damage_table[1][opponent_defense] * \
                                opponent_defense_multiplier
                        else:
                            damage_to_opponent = \
                                pokemon_attack_name_and_damage_table[1][opponent_special_defense] * \
                                opponent_defense_multiplier
                        player_health_stat = pokemon_hp
                        opponent_health_stat = opponent_hp
                        if max_damage_opponent_can_do != 0 or damage_to_opponent != 0:
                            while player_health_stat > 0 and opponent_health_stat > 0:
                                player_health_stat = player_health_stat - max_damage_opponent_can_do
                                opponent_health_stat = opponent_health_stat - damage_to_opponent
                        else:
                            player_health_stat = 0
                        if player_health_stat > 0 or \
                                (
                                        player_health_stat == 0 and
                                        opponent_health_stat == 0 and
                                        pokemon_speed > opponent_speed
                                ):
                            set_to_pokemon_to_move_to_rank[set_number][pokemon][
                                str((move_name, pokemon_attack_type))] += 1
    return set_to_pokemon_to_move_to_rank


def rank_pokemon_by_best_four_attacks(set_to_pokemon_to_move_to_rank):
    set_to_pokemon_to_rank_and_moves = defaultdict(lambda: defaultdict())
    for set_number, pokemon_to_move_to_rank in set_to_pokemon_to_move_to_rank.items():
        number_of_opponents = len(set_to_damage_tables[set_number])
        for pokemon, move_to_rank in pokemon_to_move_to_rank.items():
            sorted_move_to_rank = {
                k: v for k, v in sorted(move_to_rank.items(), key=lambda e: e[1], reverse=True)
            }
            best_move_to_rank = dict()
            added_types = []
            for str_move_tuple, rank in sorted_move_to_rank.items():
                move_keys = str_move_tuple.split("'")
                move_name = move_keys[1]
                move_type = move_keys[3]
                if move_type not in added_types:
                    added_types.append(move_type)
                    best_move_to_rank[move_name] = rank
            sum_for_best_four_attack_ranks = 0
            best_four = dict(list(best_move_to_rank.items())[:4])
            for move_rank in best_four.values():
                sum_for_best_four_attack_ranks += move_rank
            final_rank = (sum_for_best_four_attack_ranks / 4.0) / number_of_opponents
            set_to_pokemon_to_rank_and_moves[set_number][pokemon] = (final_rank, sorted_move_to_rank)

    return {
        set_number: {pokemon: {
            rank: sorted(moves.items(), key=lambda x: x[1], reverse=True)
        }
            for pokemon, (rank, moves)
            in sorted(pokemon_to_rank_and_moves.items(), key=lambda x: x[1][0], reverse=True)
        }
        for set_number, pokemon_to_rank_and_moves
        in set_to_pokemon_to_rank_and_moves.items()
    }


if __name__ == "__main__":
    if not exists(SET_TO_POKEMON_TO_MOVE_TO_RANK_FILE):
        pokemon_to_category_to_type_to_damage_table = get_pokemon_to_category_to_type_to_damage_table()
        set_to_pokemon_to_move_to_rank = rank_pokemon(pokemon_to_category_to_type_to_damage_table)
        with open(SET_TO_POKEMON_TO_MOVE_TO_RANK_FILE, "w") as fo:
            fo.write(
                json.dumps(set_to_pokemon_to_move_to_rank)
            )
    else:
        with open(SET_TO_POKEMON_TO_MOVE_TO_RANK_FILE, "r") as fo:
            set_to_pokemon_to_move_to_rank = json.loads(fo.read())
    set_to_pokemon_to_moves_and_ranks = rank_pokemon_by_best_four_attacks(
        set_to_pokemon_to_move_to_rank
    )
    with open(SET_TO_POKEMON_TO_MOVES_AND_RANKS + ".json", "w") as fo:
        fo.write(
            json.dumps(set_to_pokemon_to_moves_and_ranks)
        )
