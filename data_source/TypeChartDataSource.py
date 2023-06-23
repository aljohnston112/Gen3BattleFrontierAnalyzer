import json

from Config import ATTACKER_TYPE_FILE


def get_defender_type_dict():
    # [no_eff, not_eff, normal_eff, super_eff]
    with open(ATTACKER_TYPE_FILE, "r") as fo:
        return json.loads(fo.read())