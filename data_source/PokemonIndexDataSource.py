import json

from Config import POKEMON_INDEX_FILE


def get_index_to_pokemon():
    with open(POKEMON_INDEX_FILE, "r") as fo:
        return json.loads(fo.read())


def get_pokemon_name_to_index():
    index_to_pokemon = get_index_to_pokemon()
    return {v: k for k, v in index_to_pokemon.items()}


if __name__ == "__main__":
    index_to_pokemon = get_index_to_pokemon()
    pass
