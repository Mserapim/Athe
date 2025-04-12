# -*- coding: utf-8 -*-

from django.db.models import Q

from contrib.utils import getLogger
from rh.gfp.loaders import gfp_loader
from rh.gfp.models import Folha  # models as
from standard.models import RunCodeManager

log = getLogger("rh.gfp.loaders.mpmt")


@RunCodeManager.register("gfp-loader-mpmt")
class MPMT(gfp_loader.GFPLoader):
    # I;NORMAL;2013;11;115412;ADRIANY PAULA PEREIRA SILVA VIEIRA;5440;60;913.59;0;;;677AIB
    """ """
    CONFIG = {
        "tipo": 0,
        "matricula": 4,
        "evento": 5,
        "parcela": 6,
        "prazo": 7,
        "valor": 8,
        "pct": 9,
        "info": 10,
    }
    CODE_TYPE = "utf-8"
    TRUNK_CR_NL = True
    HEADER_LINES = 1

    def _convert_matricula(self, value):
        try:
            return value.strip().lstrip("0")
        except ValueError:
            self.ValidateError('Campo "matricula" (%s) com formato inválido!' % (value))

    def _convert_valor(self, value):
        try:
            return float(value.strip())
        except ValueError:
            self.ValidateError('Campo "valor" (%s) com formato inválido!' % (value))

    def _convert_prazo(self, value):
        return int(value.strip()) if value else 0

    def _convert_parcela(self, value):
        return int(value.strip()) if value else 0

    def _convert_pct(self, value):
        try:
            return float(value.strip()) if value else None
        except ValueError:
            self.ValidateError('Campo "valor" (%s) com formato inválido!' % (value))

    def pos_validate(self):
        super(MPMT, self).pre_validate()

        if len(self.header[0]) < 3:
            raise self.ValidateError(
                "Cabeçalho do arquivo inválido! Deve ser AAAA;MM;FOLHA;HASH. \
                    Onde AAAA é o ano, MM é o mês e XXXX qualquer descrição."
            )

        year, month, descption = self.header[0][2], self.header[0][3], self.header[0][1]

        try:
            payroll = Folha.objects.get(
                Q(periodo__ano=year)
                & Q(periodo__mes=month)
                & (
                    Q(tipo_folha__abreviatura=descption)
                    | Q(tipo_folha__titulo=descption)
                )
            )
        except Folha.DoesNotExist:
            raise self.ValidateError(
                "Cabeçalho do arquivo inválido! Não existe folha para o período %s/%s do tipo %s"
                % (month, year, descption)
            )
        except Exception as e:
            raise e
        else:
            if payroll != self.payroll:
                raise self.ValidateError(
                    "Cabeçalho do arquivo inválido! Cabeçalho %s/%s - %s diferente da folha escolhida (%s)!"
                    % (month, year, descption, self.payroll)
                )

    def get_identification_obj(self, obj):
        return "%s%s%05d%s%s" % (
            obj.get("matricula", ""),
            obj.get("tipo", "X"),
            self.payroll.pk,
            obj.get("evento").numero,
            obj.get("info"),
        )

    def get_typeof(self):
        return "MPMT"
