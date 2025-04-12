# -*- coding:utf-8 -*-
from contrib.config import config

"""
 DEFAULT produção
    Valores:
        1 - Produção;
        2 - Produção restrita.
"""
ESOCIAL_ENVIRONMENT = config("ESOCIAL_ENVIRONMENT", default=2)
