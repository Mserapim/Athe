# -*- coding: utf-8 -*-

from datetime import datetime

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.models import PessoaJuridica, Servidor
from standard.models import Configuration

log = getLogger(__name__)
log.info("LOAD SIGNAL %s" % __name__)


def get_regime_previdenciario_(
    servidor, range_=NewDateRange.from_month(datetime.now().year, datetime.now().month)
):
    try:
        cfg = Configuration.get_or_create("gfp")
        inss = PessoaJuridica.objects.get(pk=cfg.get("inss"))
        regime = None
    except PessoaJuridica.DoesNotExist:
        inss = None
    except Exception as e:
        log.exception(e)
        inss = None
    finally:
        if (
            servidor.posses_ativas
        ):  # Procurando pelo regime do servidor caso esteja ATIVO
            posses = servidor.posses_ativas
            if posses.exclude(
                requisicao=None
            ):  # Procudando se o servidor é requisitado
                return (
                    posses.exclude(requisicao=None)[0]
                    .requisicao.exclude(data_inicio__gt=range_.last)
                    .exclude(~Q(data_fim=None) & Q(data_fim__lt=range_.first))
                    .get()
                    .orgao_origem.previdencia
                )
            elif posses.filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"]):
                return posses.filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"])[
                    0
                ].quadro.cargo.unidade_administrativa.previdencia
            else:
                return inss
        elif (
            servidor.posses
        ):  # TODO Procurando pelo regime caso o servidor esteja INATIVO
            posses = servidor.posses
            if posses.exclude(
                requisicao=None
            ):  # Procudando se o servidor é requisitado
                posses_req = (
                    posses.exclude(requisicao=None)[0]
                    .requisicao.exclude(data_inicio__gt=range_.last)
                    .order_by("-data_inicio")
                )
                posses_req2 = posses_req.exclude(
                    ~Q(data_fim=None) & Q(data_fim__lt=range_.first)
                )
                if posses_req2:
                    return posses_req2.get().orgao_origem.previdencia
                else:
                    return posses_req.get().orgao_origem.previdencia
            elif posses.filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"]):
                return posses.filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"])[
                    0
                ].quadro.cargo.unidade_administrativa.previdencia
            else:
                return inss
        else:
            return regime


def get_regime_previdenciario(
    self, range_=NewDateRange.from_month(datetime.now().year, datetime.now().month)
):
    """
    :py:function:: get_regime_previdenciario(
        self, range_=NewDateRange.from_month(datetime.now().year, datetime.now().month))

    This method returns Servidor.social_securities.
    It preserves parameters to avoid breaks.

    :param NewDateRange range_ - default year and current month

    :return: PessoaJuridica instance from social_securities field.
    :rtype: PessoaJuridica
    """
    return (
        self.social_securities.currents_between(range_.first, range_.last).last().organ
    )


Servidor.get_regime_previdenciario = get_regime_previdenciario
