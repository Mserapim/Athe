# -*- coding: utf-8 -*-

from django.db.models import Q

# from rh import models as rh_models
from contrib.utils import getLogger
from rh.gfp.loaders import gfp_loader
from rh.gfp.models import Folha  # models as
from standard.models import RunCodeManager


log = getLogger("ConsigFacil")


@RunCodeManager.register("gfp-loader-consigfacil")
class ConsigFacil(gfp_loader.GFPLoader):
    titulo = "Carregador de arquivos ConsigFacil para a folha"
    # I;NORMAL;2013;11;115412;ADRIANY PAULA PEREIRA SILVA VIEIRA;5440;60;913.59;0;;;677AIB
    """
    FILE_PLAN COMPARTICIPACAO
    """
    # CONFIG = {
    #     'tipo': 0,
    #     'matricula': 1,
    #     'evento': 2,
    #     'prazo': 3,
    #     'parcela': 4,
    #     'valor': 5,
    #     'info': 6,
    # }
    CODE_TYPE = "utf-8"
    TRUNK_CR_NL = True
    HEADER_LINES = 1

    # def _convert_valor(self, value):
    #     try:
    #         return float(value.strip())
    #     except ValueError:
    #         self.ValidateError('Campo "valor" (%s) com formato inválido!' % (value))

    # def _convert_prazo(self, value):
    #     return int(value.strip()) if value else 0

    # def _convert_pct(self, value):
    #     try:
    #         return float(value.strip()) if value else None
    #     except ValueError:
    #         self.ValidateError('Campo "valor" (%s) com formato inválido!' % (value))

    # def pos_validate(self):
    #     super(Neoconsig, self).pre_validate()

    #     if len(self.header[0]) != 5:
    #         raise self.ValidateError(  # NORMAL;2020;11;NEOCONSIG;12112020
    #             'Cabeçalho do arquivo inválido! Deve ser FOLHA;AAAA;MM;TIPO;DATA. \
    #                 Onde AAAA é o ano, MM é o mês.')

    #     fh = self.header[0]
    #     fpayroll, year, month, type_of, fdate = fh[0], int(fh[1]), int(fh[2]), fh[3], fh[4]

    #     if type_of != self.get_typeof():
    #         raise self.ValidateError(f'Cabeçalho do arquivo inválido! Verificar tipo do arquivo: {type_of}')
    #     log.info(f'{fpayroll} not in [{self.payroll.tipo_folha.abreviatura}, {self.payroll.tipo_folha.titulo}] or {self.payroll.periodo.ano} != {year} or {self.payroll.periodo.mes} != {month}')
    #     if (fpayroll not in [self.payroll.tipo_folha.abreviatura, self.payroll.tipo_folha.titulo]) or self.payroll.periodo.ano != year or self.payroll.periodo.mes != month:
    #         raise self.ValidateError(
    #             'Cabeçalho do arquivo inválido! Não existe folha para o período %s/%s do tipo %s'
    #             % (month, year, fpayroll))

    # def get_identification_obj(self, obj):
    #     return '%s%s%05d%s%s' % (obj.get('matricula', ''),
    #                              obj.get('tipo', 'X'),
    #                              self.payroll.pk,
    #                              obj.get('evento').numero,
    #                              obj.get('info'))

    # def get_typeof(self):
    #     return 'NEOCONSIG'

    # def _change_values(self, params):
    #     log.info(f'CHANGE_VALUES: {params}')
    #     return params
