# -*- coding:utf-8 -*-
from contrib.config import config

# PLANSAUDE
PLANSAUDE_ORGAN_COD = config("PLANSAUDE_ORGAN_COD", default=103)
PLANSAUDE_ORGAN_NAME = config("PLANSAUDE_ORGAN_NAME", default="MINISTERIO PUBLICO")

# VIABILLIZE
VIABILLIZE_SECRET_KEY = config("VIABILLIZE_SECRET_KEY", default="secret")
VIABILLIZE_DOMAIN_PORTAL = config(
    "VIABILLIZE_DOMAIN_PORTAL", default="athenas.mpto.mp.br"
)
VIABILLIZE_DEV_NAME = config(
    "VIABILLIZE_DEV_NAME", default="Rayson Romulo Costa e Silva"
)
VIABILLIZE_DEV_FONE = config("VIABILLIZE_DEV_FONE", default="(63) 3216-7564")
VIABILLIZE_DEV_EMAIL = config("VIABILLIZE_DEV_EMAIL", default="raysonsilva@mpto.mp.br")

# EVENTOS UTILIZADOS NA GERACAO DA SEFIP
EVENTOS_INSS = config("EVENTOS_INSS", default=["91000"])
EVENTOS_INSS_13 = config("EVENTOS_INSS_13", default=["91100"])
EVENTOS_MATERNIDADE = config("EVENTOS_MATERNIDADE", default=["04000"])
