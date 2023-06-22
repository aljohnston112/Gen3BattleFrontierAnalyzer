import json
import random
import time
import urllib.request
from collections import defaultdict
from os.path import exists
from typing import Dict, List

import cattr
from bs4 import BeautifulSoup

from Config import SET_TO_POKEMON
from FrontierPokemon import FrontierPokemon

base_url = "https://bulbapedia.bulbagarden.net"
url = base_url + "/wiki/List_of_Battle_Frontier_Trainers_(Generation_III)"
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent}

trainer_to_set_numbers = defaultdict(lambda: list())
set_number_to_pokemon = defaultdict(lambda: list())


def process_trainer_urls(trainer_urls):
    for trainer_url in trainer_urls:
        request = urllib.request.Request(trainer_url, None, headers)
        with urllib.request.urlopen(request) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

            # Get trainer names
            table_index_to_trainers = defaultdict(lambda: list())
            toc_list = soup.find_all("div", id="toc")
            assert len(toc_list) == 1
            toc_lines = toc_list[0].text.split("\n")
            assert toc_lines[0] == 'Contents'
            for toc_line in toc_lines:
                if toc_line != "" and toc_line[0].isdigit():
                    toc_tokens = toc_line.split()
                    table_number = int(toc_tokens[0])
                    for i in range(1, len(toc_tokens)):
                        if not toc_tokens[i].isdigit() and toc_tokens[i] != 'and,':
                            table_index_to_trainers[table_number].append(toc_tokens[i].strip(','))

            # Get trainer pokemon
            pokemon_tables = soup.find("div", class_="mw-parser-output").find_all("table")
            assert len(table_index_to_trainers) == len(pokemon_tables) - 1
            for table_index in range(0, len(pokemon_tables) - 1):
                trainers = table_index_to_trainers[table_index]
                set_numbers = set()
                for trainer in trainers:
                    set_numbers = set_numbers.union(set(trainer_to_set_numbers[trainer]))

                table_rows = pokemon_tables[table_index].find_all("tr")
                assert table_rows[0].text == '\n#\n\nPokémon\n\nItem\n\nMoves\n\nNature\n\nEVs\n'
                assert table_rows[1].text == '\nHP\n\nAttack\n\nDefense\n\nSp. Atk\n\nSp. Def\n\nSpeed\n'
                for row_index in range(2, len(table_rows)):
                    row_tokens = table_rows[row_index].text.strip().split("\n")
                    pokemon_index = int(row_tokens[0])
                    pokemon_name = row_tokens[4]
                    item = row_tokens[6].strip()
                    move_names = [row_tokens[8], row_tokens[10], row_tokens[12], row_tokens[14]]
                    nature = row_tokens[16]
                    
                    hp_ev = row_tokens[18]
                    hp_ev = 0 if hp_ev == "-" else int(hp_ev)

                    attack_ev = row_tokens[20]
                    attack_ev = 0 if attack_ev == "-" else int(attack_ev)

                    defense_ev = row_tokens[22]
                    defense_ev = 0 if defense_ev == "-" else int(defense_ev)

                    special_attack_ev = row_tokens[24]
                    special_attack_ev = 0 if special_attack_ev == "-" else int(special_attack_ev)
                    
                    special_defense_ev = row_tokens[26]
                    special_defense_ev = 0 if special_defense_ev == "-" else int(special_defense_ev)

                    speed_ev = row_tokens[28]
                    speed_ev = 0 if speed_ev == "-" else int(speed_ev)

                    pokemon = FrontierPokemon(
                        index=pokemon_index,
                        name=pokemon_name,
                        item=item,
                        move_names=tuple(move_names),
                        nature=nature,
                        hp_ev=hp_ev,
                        attack_ev=attack_ev,
                        defense_ev=defense_ev,
                        special_attack_ev=special_attack_ev,
                        special_defense_ev=special_defense_ev,
                        speed_ev=speed_ev
                    )
                    for set_number in set_numbers:
                        set_number_to_pokemon[set_number].append(pokemon)

            time.sleep(0.5 + (random.random() / 2.0))


def process_trainer_table(table):
    links = table.find_all("tr")[1].find_all("a")
    assert len(links) == 36

    # Get trainer urls
    trainer_urls = []
    for link in links:
        href = link['href']
        trainer_urls.append(base_url + href)

    process_trainer_urls(trainer_urls)


def process_set_table(table):

    table_rows = table.find_all("tr")
    assert len(table_rows) == 302
    for i in range(2, len(table_rows)):
        tokens = table_rows[i].text.split("\n")
        trainer_name = tokens[5]
        for j in range(0, 8):
            if tokens[2 * j + 7] == '✔':
                trainer_to_set_numbers[trainer_name].append(j)


def get_set_to_frontier_pokemon():
    if not exists(SET_TO_POKEMON):
        request = urllib.request.Request(url, None, headers)
        with urllib.request.urlopen(request) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            process_set_table(soup.find_all("table")[0])
            time.sleep(0.5 + (random.random() / 2.0))

            process_trainer_table(soup.find_all("table")[1])
        with open(SET_TO_POKEMON, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(set_number_to_pokemon)))
    else:
        with open(SET_TO_POKEMON, "r") as fo:
            set_number_to_pokemon = json.loads(fo.read()), Dict[int, List[FrontierPokemon]]
    return set_number_to_pokemon


if __name__ == "__main__":
    set_number_to_pokemon = get_set_to_frontier_pokemon()
    pass
