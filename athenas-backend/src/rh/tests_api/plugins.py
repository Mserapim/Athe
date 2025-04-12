# -*- coding: utf-8 -*-

from django.conf import settings

from contrib.utils import getLogger
from rh.models import ServidorLotacao

log = getLogger(__name__)


def main():
    if hasattr(settings, "TESTING") and settings.TESTING is False:
        message = """TESTING Plugins activate for Athenas. MUST BE DEACTIVATED WHEN IN PRODUCTION"""
        print(message)
        log.info(message)
        ServidorLotacao.validate_publicacao = validate_publicacao
        ServidorLotacao.validate_lotacao_fora_organograma = (
            validate_lotacao_fora_organograma
        )
        ServidorLotacao.validate_posse = validate_posse


def validate_publicacao(self):
    # if self.publicacao is None:
    # # self.publicacao = mock(model=Publicacao, query=(~Q(data_vigencia=None)))
    return True


def validate_lotacao_fora_organograma(self):
    return True


def validate_posse(self):
    # if self.movimentacao_posse is None:
    #     self.movimentacao_posse = self.servidor.posses_ativas.filter(
    #         quadro__cargo__tipo_lei_cargo='EF').latest('data_exercicio') if self.servidor.posses_ativas.filter(
    #         quadro__cargo__tipo_lei_cargo='EF').exists() else None
    return True


main()
