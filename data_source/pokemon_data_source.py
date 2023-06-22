import json
import os
import random
import time
import urllib.request
from collections import defaultdict
from os.path import exists
from typing import Dict

import cattr
from bs4 import BeautifulSoup

from Config import POKEMON_FILE
from data_class.AllStats import AllStats
from data_class.Attack import Attack
from data_class.BaseStats import BaseStats
from data_class.Category import convert_to_attack_category
from data_class.Pokemon import Pokemon
from data_class.PokemonInformation import PokemonInformation
from data_class.PokemonType import convert_to_pokemon_type
from data_class.Stat import get_health_stat, get_non_health_stat, NatureEnum, StatEnum
from data_class.Stats import Stats

base_url = "https://www.serebii.net/pokedex-rs/"
num_pokemon = 386


def get_url(index: int):
    return base_url + str(index).zfill(3) + ".shtml"


def process_general_information(dextable):
    rows = dextable.find_all("tr")
    assert rows[0].text == '\nPokémon Game Picture\nNational No.\nHoenn No.\nEnglish name\nJapanese Name\n'
    first_row_tokens = rows[1].text.split("\n")

    pokemon_index = int(first_row_tokens[9].strip())
    pokemon_name = first_row_tokens[15].strip()

    ability_text = rows[3].text.split("\n")[9]
    assert "Ability" in ability_text
    ability = ability_text.split(":")[1].strip()

    if len(rows) == 13:
        offset = 0
    elif len(rows) == 12:
        offset = -1
    elif len(rows) == 14:
        offset = 3
    else:
        assert False

    assert rows[9 + offset].text == '\nClassification\nType 1\nType 2\nHeight\nWeight\n'
    pounds = float(rows[10 + offset].text.split("\n")[14].split()[0].replace(",", ""))

    pokemon_types = []
    type_images = rows[10 + offset].find_all("img")
    assert len(type_images) < 3
    for img in type_images:
        pokemon_type = img['src'].split("/")[-1].split(".")[0]
        if pokemon_type != "na":
            pokemon_types.append(
                convert_to_pokemon_type(pokemon_type)
            )

    return PokemonInformation(
        id=pokemon_index,
        name=pokemon_name,
        pokemon_types=pokemon_types,
        ability=ability,
        pounds=pounds
    )


def get_level_up_attacks(dextable):
    level_to_attacks = defaultdict(lambda: [])
    rows = dextable.find_all("tr")
    assert rows[0].text in [
        'Ruby/Sapphire/Emerald/Colosseum/XD Level Up',
        'Fire Red/Leaf Green Level Up',
        'Ruby/Sapphire/Colosseum/XD Level Up',
        'Fire Red Level Up',
        'Leaf Green',
        'Emerald'
    ]
    assert rows[1].text == 'LevelAttack NameTypeAtt.Acc.PPEffect %'

    row_index = 2
    while row_index < len(rows):
        columns = rows[row_index].find_all("td")

        level = columns[0].text
        if level == '—':
            level = 0
        else:
            level = int(level)

        name = columns[1].text
        attack_type = columns[2].find("img")['src'].split("/")[-1].split(".")[0]

        power = columns[3].text
        if power == '--' or \
                name == "Sonicboom" or \
                name == "Endeavor" or \
                name == "Super Fang" or \
                name == "Dragon Rage" or \
                name == "Mirror Coat" or \
                name == "Counter" or \
                name == "Bide":
            power = 0
        elif name == "Horn Drill" or \
                name == "Sheer Cold" or \
                name == "Fissure" or \
                name == "Guillotine":
            power = -1
        elif name == "Magnitude":
            power = 150
        elif name == "Low Kick" or name == "Present":
            power = 120
        elif name == "Seismic Toss" or \
                name == "Night Shade":
            power = 100
        elif name == "Reversal" or \
                name == "Flail":
            power = 200
        elif name == "Psywave" or \
                name == "Magnitude":
            power = 150
        elif name == "Hidden Power":
            power = 70
        else:
            power = int(power)

        accuracy = columns[4].text
        if accuracy == '--':
            accuracy = 0
        else:
            accuracy = int(accuracy)

        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)

        level_to_attacks[level].append(
            Attack(
                name=name,
                pokemon_type=convert_to_pokemon_type(attack_type),
                power=power,
                accuracy=accuracy,
                effect_percent=effect_chance,
                category=convert_to_attack_category(attack_type)
            )
        )

        row_index += 2
    return level_to_attacks


def get_tm_and_hm_attacks(dextable):
    tm_or_hm_to_attack = dict()
    rows = dextable.find_all("tr")
    assert rows[0].text in [
        'TM & HM Attacks'
    ]
    assert rows[1].text == 'TM/HM #Attack NameTypeAtt.Acc.PPEffect %'

    row_index = 2
    while row_index < len(rows):
        columns = rows[row_index].find_all("td")

        tm_or_hm = columns[0].text

        name = columns[1].text
        attack_type = columns[2].find("img")['src'].split("/")[-1].split(".")[0]

        power = columns[3].text
        if power == '--':
            power = 0
        elif name == "Hidden Power":
            power = 70
        elif name == "Frustration" or name == "Return":
            power = 102
        else:
            power = int(power)

        accuracy = columns[4].text
        if accuracy == '--':
            accuracy = 0
        else:
            accuracy = int(accuracy)

        effect_chance = columns[6].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)

        tm_or_hm_to_attack[tm_or_hm] = Attack(
            name=name,
            pokemon_type=convert_to_pokemon_type(attack_type),
            power=power,
            accuracy=accuracy,
            effect_percent=effect_chance,
            category=convert_to_attack_category(attack_type)
        )

        row_index += 2
    return tm_or_hm_to_attack


def get_move_tutor_attacks(dextable):
    attacks = []
    rows = dextable.find_all("tr")
    assert rows[0].text in [
        'Fire Red/Leaf Green/Emerald Tutor Attacks',
        'Emerald Tutor Attacks',
        'Egg Moves',
        'Special Attacks'
    ]
    assert rows[1].text == 'Attack NameTypeAtt.Acc.PPEffect %'

    row_index = 2
    while row_index < len(rows):
        columns = rows[row_index].find_all("td")

        name = columns[0].text
        attack_type = columns[1].find("img")['src'].split("/")[-1].split(".")[0]

        power = columns[2].text
        if power == '--' or \
                name == "Counter" or \
                name == "Mirror Coat" or \
                name == "Endeavor" or \
                name == "Dragon Rage" or \
                name == "Bide" or \
                name == "Sonicboom":
            power = 0
        elif name == "Horn Drill" or \
                name == "Fissure" or \
                name == "Sheer Cold":
            power = -1
        elif name == "Seismic Toss" or \
                name == "Night Shade":
            power = 100
        elif name == "Reversal" or \
                name == "Flail":
            power = 200
        elif name == "Present":
            power = 120
        elif name == "Psywave" or \
                name == "Magnitude":
            power = 150

        else:
            power = int(power)

        accuracy = columns[3].text
        if accuracy == '--':
            accuracy = 0
        else:
            accuracy = int(accuracy)

        effect_chance = columns[5].text
        if effect_chance == "--":
            effect_chance = 0
        effect_chance = int(effect_chance)

        attacks.append(
            Attack(
                name=name,
                pokemon_type=convert_to_pokemon_type(attack_type),
                power=power,
                accuracy=accuracy,
                effect_percent=effect_chance,
                category=convert_to_attack_category(attack_type)
            )
        )

        row_index += 2
    return attacks


def convert_to_level_50_min_stats(base_stats):
    hp = get_health_stat(
        base=base_stats.stats.health,
        iv=0,
        ev=0,
        level=50
    )
    attack = get_non_health_stat(
        base=base_stats.stats.attack,
        stat_type=StatEnum.ATTACK,
        iv=0,
        ev=0,
        level=50,
        nature="bold"
    )

    defense = get_non_health_stat(
        base=base_stats.stats.defense,
        stat_type=StatEnum.DEFENSE,
        iv=0,
        ev=0,
        level=50,
        nature="lonely"
    )

    special_attack = get_non_health_stat(
        base=base_stats.stats.special_attack,
        stat_type=StatEnum.SPECIAL_ATTACK,
        iv=0,
        ev=0,
        level=50,
        nature="adamant"
    )

    special_defense = get_non_health_stat(
        base=base_stats.stats.special_defense,
        stat_type=StatEnum.SPECIAL_DEFENSE,
        iv=0,
        ev=0,
        level=50,
        nature="naughty"
    )

    speed = get_non_health_stat(
        base=base_stats.stats.speed,
        stat_type=StatEnum.SPEED,
        iv=0,
        ev=0,
        level=50,
        nature='brave'
    )

    return Stats(
        name=base_stats.name,
        health=hp,
        attack=attack,
        defense=defense,
        special_attack=special_attack,
        special_defense=special_defense,
        speed=speed
    )


def convert_to_level_50_max_stats(base_stats):
    hp = get_health_stat(
        base=base_stats.stats.health,
        iv=31,
        ev=252,
        level=50
    )
    attack = get_non_health_stat(
        base=base_stats.stats.attack,
        stat_type=StatEnum.ATTACK,
        iv=31,
        ev=252,
        level=50,
        nature="lonely"
    )

    defense = get_non_health_stat(
        base=base_stats.stats.defense,
        stat_type=StatEnum.DEFENSE,
        iv=31,
        ev=252,
        level=50,
        nature="bold"
    )

    special_attack = get_non_health_stat(
        base=base_stats.stats.special_attack,
        stat_type=StatEnum.SPECIAL_ATTACK,
        iv=31,
        ev=252,
        level=50,
        nature="modest"
    )

    special_defense = get_non_health_stat(
        base=base_stats.stats.special_defense,
        stat_type=StatEnum.SPECIAL_DEFENSE,
        iv=31,
        ev=252,
        level=50,
        nature="calm"
    )

    speed = get_non_health_stat(
        base=base_stats.stats.speed,
        stat_type=StatEnum.SPEED,
        iv=31,
        ev=252,
        level=50,
        nature='timid'
    )

    return Stats(
        name=base_stats.name,
        health=hp,
        attack=attack,
        defense=defense,
        special_attack=special_attack,
        special_defense=special_defense,
        speed=speed
    )


def convert_to_level_100_min_stats(base_stats):
    hp = get_health_stat(
        base=base_stats.stats.health,
        iv=0,
        ev=0,
        level=100
    )
    attack = get_non_health_stat(
        base=base_stats.stats.attack,
        stat_type=StatEnum.ATTACK,
        iv=0,
        ev=0,
        level=100,
        nature="bold"
    )

    defense = get_non_health_stat(
        base=base_stats.stats.defense,
        stat_type=StatEnum.DEFENSE,
        iv=0,
        ev=0,
        level=100,
        nature="lonely"
    )

    special_attack = get_non_health_stat(
        base=base_stats.stats.special_attack,
        stat_type=StatEnum.SPECIAL_ATTACK,
        iv=0,
        ev=0,
        level=100,
        nature="adamant"
    )

    special_defense = get_non_health_stat(
        base=base_stats.stats.special_defense,
        stat_type=StatEnum.SPECIAL_DEFENSE,
        iv=0,
        ev=0,
        level=100,
        nature="naughty"
    )

    speed = get_non_health_stat(
        base=base_stats.stats.speed,
        stat_type=StatEnum.SPEED,
        iv=0,
        ev=0,
        level=100,
        nature='brave'
    )

    return Stats(
        name=base_stats.name,
        health=hp,
        attack=attack,
        defense=defense,
        special_attack=special_attack,
        special_defense=special_defense,
        speed=speed
    )


def convert_to_level_100_max_stats(base_stats):
    hp = get_health_stat(
        base=base_stats.stats.health,
        iv=31,
        ev=252,
        level=100
    )
    attack = get_non_health_stat(
        base=base_stats.stats.attack,
        stat_type=StatEnum.ATTACK,
        iv=31,
        ev=252,
        level=100,
        nature="lonely"
    )

    defense = get_non_health_stat(
        base=base_stats.stats.defense,
        stat_type=StatEnum.DEFENSE,
        iv=31,
        ev=252,
        level=100,
        nature="bold"
    )

    special_attack = get_non_health_stat(
        base=base_stats.stats.special_attack,
        stat_type=StatEnum.SPECIAL_ATTACK,
        iv=31,
        ev=252,
        level=100,
        nature="modest"
    )

    special_defense = get_non_health_stat(
        base=base_stats.stats.special_defense,
        stat_type=StatEnum.SPECIAL_DEFENSE,
        iv=31,
        ev=252,
        level=100,
        nature="calm"
    )

    speed = get_non_health_stat(
        base=base_stats.stats.speed,
        stat_type=StatEnum.SPEED,
        iv=31,
        ev=252,
        level=100,
        nature='timid'
    )

    return Stats(
        name=base_stats.name,
        health=hp,
        attack=attack,
        defense=defense,
        special_attack=special_attack,
        special_defense=special_defense,
        speed=speed
    )


def get_stats(dextable, name):
    rows = dextable.find_all("tr")
    assert rows[0].text in [
        'Stats',
        'Stats (Attack form)',
        'Stats (Defence Form)',
        'Stats (Speed form)'
    ]
    assert rows[1].text == ' HP AttackDefenseSp. AttackSp. DefenseSpeed'

    columns = rows[2].find_all("td")
    assert len(columns) == 7
    assert columns[0].text == 'Base Stats'
    base_hp = int(columns[1].text)
    base_attack = int(columns[2].text)
    base_defense = int(columns[3].text)
    base_special_attack = int(columns[4].text)
    base_special_defense = int(columns[5].text)
    base_speed = int(columns[6].text)

    base_stats = BaseStats(
        name=name,
        stats=Stats(
            name=name,
            health=base_hp,
            attack=base_attack,
            defense=base_defense,
            special_attack=base_special_attack,
            special_defense=base_special_defense,
            speed=base_speed
        )
    )

    return AllStats(
        name=name,
        base_stats=base_stats,
        level_50_min_stats=convert_to_level_50_min_stats(base_stats),
        level_50_max_stats=convert_to_level_50_max_stats(base_stats),
        level_100_min_stats=convert_to_level_100_min_stats(base_stats),
        level_100_max_stats=convert_to_level_100_max_stats(base_stats)
    )


def __scrape_serebii_for_move_sets__():
    first_row_text_of_skippable_tables = [
        '\nWild Hold Item\nDex Category\nColour Category\nFootprint\n',
        '\n\n\t\tDamage Taken\n\t\t\n',
        '\n\n\t\tFlavor Text\n\t\t\n',
        '\n\nLocation\n\n',
        '\nEgg Steps to Hatch\nEffort Points from Battling it\nCatch Rate\n',
        'Egg Groups'
    ]

    pokemon_index_to_pokemon: dict[int, Pokemon] = dict()
    last_url_index = 0
    for pokemon_index in range(last_url_index + 1, num_pokemon + 1):
        url = get_url(pokemon_index)
        rse_level_to_attacks = None
        frlf_level_to_attacks = None
        fr_level_to_attacks = None
        lg_level_to_attacks = None
        rs_level_to_attacks = None
        emerald_level_up_attacks = None
        tm_or_hm_to_attack = None
        move_tutor_attacks = None
        emerald_move_tutor_attacks = None
        egg_moves = None
        special_attacks = None
        all_stats = None
        attack_form_stats = None
        defence_form_stats = None
        speed_form_stats = None
        with urllib.request.urlopen(url) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            dextables = soup.find_all("table", class_="dextable")
            for dextable in dextables:
                first_row_text = dextable.find("tr").text
                if first_row_text not in first_row_text_of_skippable_tables:
                    if first_row_text == '\nPokémon Game Picture\nNational No.\nHoenn No.\nEnglish name\nJapanese Name\n':
                        pokemon_information = process_general_information(dextable)
                    elif first_row_text == 'Ruby/Sapphire/Emerald/Colosseum/XD Level Up':
                        rse_level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'Fire Red/Leaf Green Level Up':
                        frlf_level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'Fire Red Level Up':
                        fr_level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'Leaf Green':
                        lg_level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'Ruby/Sapphire/Colosseum/XD Level Up':
                        rs_level_to_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'Emerald':
                        emerald_level_up_attacks = get_level_up_attacks(dextable)
                    elif first_row_text == 'TM & HM Attacks':
                        tm_or_hm_to_attack = get_tm_and_hm_attacks(dextable)
                    elif first_row_text == 'Fire Red/Leaf Green/Emerald Tutor Attacks':
                        move_tutor_attacks = get_move_tutor_attacks(dextable)
                    elif first_row_text == 'Emerald Tutor Attacks':
                        emerald_move_tutor_attacks = get_move_tutor_attacks(dextable)
                    elif first_row_text == 'Egg Moves':
                        egg_moves = get_move_tutor_attacks(dextable)
                    elif first_row_text == 'Special Attacks':
                        special_attacks = get_move_tutor_attacks(dextable)
                    elif first_row_text == 'Stats':
                        all_stats = get_stats(dextable, pokemon_information.name)
                    elif first_row_text == 'Stats (Attack form)':
                        attack_form_stats = get_stats(dextable, pokemon_information.name)
                    elif first_row_text == 'Stats (Defence Form)':
                        defence_form_stats = get_stats(dextable, pokemon_information.name)
                    elif first_row_text == 'Stats (Speed form)':
                        speed_form_stats = get_stats(dextable, pokemon_information.name)
                    else:
                        assert False

        if fr_level_to_attacks is None:
            fr_level_to_attacks = frlf_level_to_attacks
        if lg_level_to_attacks is None:
            lg_level_to_attacks = frlf_level_to_attacks
        if rs_level_to_attacks is None:
            rs_level_to_attacks = rse_level_to_attacks
        if emerald_level_up_attacks is None:
            emerald_level_up_attacks = rse_level_to_attacks

        assert all_stats is not None
        assert fr_level_to_attacks is not None
        assert lg_level_to_attacks is not None
        assert rs_level_to_attacks is not None
        assert emerald_level_up_attacks is not None

        pokemon_index_to_pokemon[pokemon_index] = Pokemon(
            pokemon_information=pokemon_information,
            fr_level_to_attacks=fr_level_to_attacks,
            lg_level_to_attacks=lg_level_to_attacks,
            rs_level_to_attacks=rs_level_to_attacks,
            emerald_level_up_attacks=emerald_level_up_attacks,
            tm_or_hm_to_attack=tm_or_hm_to_attack,
            move_tutor_attacks=move_tutor_attacks,
            emerald_move_tutor_attacks=emerald_move_tutor_attacks,
            egg_moves=egg_moves,
            special_attacks=special_attacks,
            all_stats=all_stats,
            attack_form_stats=attack_form_stats,
            defence_form_stats=defence_form_stats,
            speed_form_stats=speed_form_stats
        )
        time.sleep(0.5 + (random.random() / 2.0))
    return pokemon_index_to_pokemon


def get_pokemon() -> Dict[int, Pokemon]:
    if not exists(POKEMON_FILE):
        pokemon_index_to_pokemon = __scrape_serebii_for_move_sets__()
        with open(POKEMON_FILE, "w") as fo:
            fo.write(json.dumps(cattr.unstructure(pokemon_index_to_pokemon)))
    else:
        with open(POKEMON_FILE, "r") as fo:
            pokemon_index_to_pokemon = cattr.structure(json.loads(fo.read()), Dict[str, Pokemon])
    return pokemon_index_to_pokemon


if __name__ == "__main__":
    pokemon_index_to_pokemon = get_pokemon()
    pass
