# -*- coding:utf-8 -*-
from contrib.config import config

WEB_CONTEXT = config("WEB_CONTEXT", default="")  # TODO: Mudar para mpto.mp.br'web'
WEB_DOMAIN = config("WEB_DOMAIN", default="127.0.0.1")  # TODO: Mudar para mpto.mp.br
WEB = "https://%s%s" % (WEB_DOMAIN, WEB_CONTEXT)
WEB_SECRET_KEY = config("WEB_SECRET_KEY", default="secr3t")

IMAGE_SIZES = [
    "square|30",
    "square|54",
    "square|64",
    "square|166",
    "width|170",
    "width|180",
    "width|191",
    "width|250",
    "width|400",
    "width|600",
    "width|1280",
]

PROHIBITED_TAGS = ["mpe", "mpe-to"]
