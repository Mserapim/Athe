from django.db.models import Q

from standard.models import Choice
from esocial.models import ItemTable
from esocial.const import DEPENDENT_TYPE_MAP

categs = ItemTable.objects.filter(esocial_table=1)
events = ItemTable.objects.filter(esocial_table=9)
dep_types = ItemTable.objects.filter(esocial_table=7)
street_types = ItemTable.objects.filter(esocial_table=20)
fire_types = ItemTable.objects.filter(esocial_table=19)

queries = [categs, events, dep_types, street_types, fire_types]

e301 = ["EFE", "ECM", "MBR", "MEL", "MCM", "MEC", "EFC", "MBR2", "MEL2", "MCM2", "MEC2"]
e302 = ["CMS"]
e410 = ["REQ", "RCM", "RFC"]
e901 = ["EST"]

TYPE_FIRE_MAP = {
    "23": [1, 2, 3],
    "00": [4, 5, 8, 10, 11, 12, 15, 20],
    "25": [6],
    "10": [7],
    "24": [9],
    "28": [13],
    "18": [14],
    "20": [16],
    "19": [17],
    "29": [18],
    "31": [19],
}

TYPE_STREET_MAP = {
    "AV": [
        1,
    ],
    "PC": [
        2,
    ],
    "VLA": [
        3,
    ],
    "VD": [
        5,
    ],
    "R": [
        8,
    ],
    "Q": [
        9,
    ],
}

TYPE_CATEG_MAP = {"301": e301, "302": e302, "410": e410, "901": e901}

TYPE_DEP_MAP = {
    "01": [
        1,
    ],
    "02": [
        2,
    ],
    "03": [3, 8],
    "04": [
        17,
    ],
    "06": [6, 14, 15],
    "09": [5, 12, 13],
    "10": [
        10,
    ],
    "11": [4, 7, 9, 11],
    "12": [
        16,
    ],
    "99": [18, None],
}

EVENT_MAP = {
    "S2200": e301 + e302,
    "S2300": e410 + e901,
}

maps = [TYPE_CATEG_MAP, EVENT_MAP, TYPE_DEP_MAP, TYPE_STREET_MAP, TYPE_FIRE_MAP]


categ_choice = lambda x, y: Q(cvalue__in=y.get(x.code, []))
event_choice = lambda x, y: Q(cvalue__in=y.get(x.code, []))
dep_choice = lambda x, y: Q(name="DEPENDENT_TYPE", value__in=y.get(x.code, []))
street_choice = lambda x, y: Q(name="TYPE_STREET", value__in=y.get(x.code, []))
fire_choice = lambda x, y: Q(name="TYPE_FIRED", value__in=y.get(x.code, []))

choices_filter = [categ_choice, event_choice, dep_choice, street_choice, fire_choice]


def add_item(query_item, map_ci, choice_param):
    for x in query_item:
        choices = Choice.objects.filter(choice_param(x, map_ci))
        print(choices)
        x.choice.add(*choices)
        print("APARENTELY that works!")


def run():
    list(map(add_item, queries, maps, choices_filter))
