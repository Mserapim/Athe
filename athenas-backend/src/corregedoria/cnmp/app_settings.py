# -*- coding:utf-8 -*-

from contrib.config import config

# Informações para consumo e envio de dados do scmmp
# ambiente de homologacao
WS_SCMMP_HOMOLOGACAO_URL = config("WS_SCMMP_HOMOLOGACAO_URL", default="")
WS_SCMMP_HOMOLOGACAO_USER = config("WS_SCMMP_HOMOLOGACAO_USER", default="user")
WS_SCMMP_HOMOLOGACAO_PASSWORD = config("WS_SCMMP_HOMOLOGACAO_PASSWORD", default="pass")

# ambiente de producao
WS_SCMMP_PRODUCAO_URL = config("WS_SCMMP_PRODUCAO_URL", default="")
WS_SCMMP_PRODUCAO_USER = config("WS_SCMMP_PRODUCAO_USER", default="user")
WS_SCMMP_PRODUCAO_PASSWORD = config("WS_SCMMP_PRODUCAO_PASSWORD", default="pass")
