import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = ROOT + "/data/"

SET_TO_POKEMON = DATA_DIR + "set_to_pokemon.json"
POKEMON_FILE = DATA_DIR + "all_pokemon.json"
POKEMON_INDEX_FILE = DATA_DIR + "pokemon_indices"

SET_TO_POKEMON_TO_DAMAGE_TABLES = DATA_DIR + "set_to_pokemon_to_damage_tables"
POKEMON_TO_DAMAGE_TABLES = DATA_DIR + "pokemon_to_damage_tables"

SET_TO_POKEMON_TO_MOVE_TO_RANK_FILE = DATA_DIR + "set_to_pokemon_to_move_to_rank"
SET_TO_POKEMON_TO_MOVES_AND_RANKS = DATA_DIR + "set_to_pokemon_to_moves_and_ranks"

ATTACKER_TYPE_FILE = DATA_DIR + "defender_types"
