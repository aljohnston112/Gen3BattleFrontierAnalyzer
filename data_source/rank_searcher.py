import json
from collections import defaultdict
from pprint import pp

from Config import SET_TO_POKEMON_TO_MOVES_AND_RANKS


def print_ranks():
    pokemon = ["Gyarados", "Crobat", "Golem", "Steelix", "Gengar"]
    with open(SET_TO_POKEMON_TO_MOVES_AND_RANKS + ".json", "r") as fo:
        set_to_pokemon_to_move_to_rank = json.loads(fo.read())
        set_to_pokemon_to_rank_and_moves = defaultdict(lambda: dict())
        for set_number, pokemon_to_moves_and_ranks in \
                sorted(set_to_pokemon_to_move_to_rank.items(), key=lambda x: x[0]):
            for poke in pokemon:
                set_to_pokemon_to_rank_and_moves[set_number][poke] = \
                    list(pokemon_to_moves_and_ranks[poke].items())[0]

        for set_number, pokemon_to_rank_to_moves_and_ranks in set_to_pokemon_to_rank_and_moves.items():
            print("Set: " + set_number)

            for poke, rank_to_moves_and_ranks in sorted(pokemon_to_rank_to_moves_and_ranks.items(), key=lambda x: x[1][0], reverse=True):
                moves_and_ranks = rank_to_moves_and_ranks
                print(poke + ": ")
                pp(moves_and_ranks)
                print()
            print()


def print_move_sets():
    pokemon = ["Infernape"]
    with open(SET_TO_POKEMON_TO_MOVES_AND_RANKS + "0.json", "r") as fo:
        set_to_pokemon_to_move_to_rank = json.loads(fo.read())
        pokemon_to_rank = defaultdict(lambda: 0.0)
        for set_number, pokemon_to_moves_and_ranks in sorted(set_to_pokemon_to_move_to_rank.items(), key=lambda x: x[0]):
            for poke in pokemon:
                moves = list(pokemon_to_moves_and_ranks[poke].items())[0]
                print("Set: " + str(set_number))
                print(poke + ": ")
                pp(moves)


if __name__ == "__main__":
    print_ranks()
    # print_move_sets()
