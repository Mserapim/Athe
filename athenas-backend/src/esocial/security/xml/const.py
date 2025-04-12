# -.- coding: utf-8 -.-

ESOCIAL_TAG = 1
SEND_EVENT_BATCH_TAG = 2
IDE_EMPLOYER_TP_INSC = 4
IDE_EMPLOYER_NR_INSC = 5
IDE_TRANSMITTER_TP_INSC = 7
IDE_TRANSMITTER_NR_INSC = 8
EVENT = 11

# xmldsig
XML_TO_SEND_TEMPLATE = {
    1: {
        "id": 1,
        "father": "",
        "tag": "eSocial",
        "group": True,
        "many": [],
        "has_value": False,
        "value": "",
        "attributes": [{"tag": "xmlns", "value": ""}],
    },
    2: {
        "id": 2,
        "father": 1,
        "tag": "envioLoteEventos",
        "group": True,
        "many": [],
        "has_value": False,
        "value": "",
        "attributes": [{"tag": "grupo", "value": ""}],
    },
    3: {
        "id": 3,
        "father": 2,
        "tag": "ideEmpregador",
        "group": True,
        "many": [],
        "has_value": False,
        "value": "",
        "attributes": [],
    },
    4: {
        "id": 4,
        "father": 3,
        "tag": "tpInsc",
        "group": False,
        "many": [],
        "has_value": "text",
        "value": "",
        "attributes": [],
    },
    5: {
        "id": 5,
        "father": 3,
        "tag": "nrInsc",
        "group": False,
        "many": [],
        "has_value": "text",
        "value": "",
        "attributes": [],
    },
    6: {
        "id": 6,
        "father": 2,
        "tag": "ideTransmissor",
        "group": True,
        "many": [],
        "has_value": False,
        "value": "",
        "attributes": [],
    },
    7: {
        "id": 7,
        "father": 6,
        "tag": "tpInsc",
        "group": False,
        "many": [],
        "has_value": "text",
        "value": "",
        "attributes": [],
    },
    8: {
        "id": 8,
        "father": 6,
        "tag": "nrInsc",
        "group": False,
        "many": [],
        "has_value": "text",
        "value": "",
        "attributes": [],
    },
    10: {
        "id": 10,
        "father": 2,
        "tag": "eventos",
        "group": True,
        "many": [],
        "has_value": False,
        "value": "",
        "attributes": [],
    },
    11: {
        "id": 11,
        "father": 10,
        "tag": "evento",
        "group": False,
        "many": [],
        "has_value": "xml",
        "value": "",
        "attributes": [{"tag": "Id", "value": ""}],
    },
}
