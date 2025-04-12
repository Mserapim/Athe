# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from rh.gfp.models import CargosEstrutura, ReferenciaSalario, TabelaSalarial
from rh.models import Cargo, PessoaJuridica, Servidor
from standard.models import Configuration

log = getLogger(__name__)
log.info("LOAD PLUGIN %s" % __name__)


def get_regime_previdenciario_rev_4419(
    servidor, range_=NewDateRange.from_month(datetime.now().year, datetime.now().month)
):
    message = "Using -> rh.gfp.plugins.rh_models.get_regime_previdenciario_rev_4419"
    log.debug(message)
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
                    .exclude(
                        ~models.Q(data_fim=None) & models.Q(data_fim__lt=range_.first)
                    )
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
                return (
                    posses.exclude(requisicao=None)[0]
                    .requisicao.exclude(data_inicio__gt=range_.last)
                    .exclude(
                        ~models.Q(data_fim=None) & models.Q(data_fim__lt=range_.first)
                    )
                    .get()
                    .orgao_origem.previdencia
                )
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
    return self.social_securities.currents_at(range_.first).last().organ


Servidor.get_regime_previdenciario = get_regime_previdenciario

# Modificando a classe Cargo de rh -------------------------------------------------------------------


class TabelaSalarialNotFound(Exception):
    pass


class ReferenciaSalarialNotFound(Exception):
    pass


class MultipleReferencias(Exception):
    pass


def salario(self, data=None, referencia=None):
    data = datetime.now().date() if not data else data
    tabela = self.tabela_vigente(data)
    salarios = tabela.salarios.filter(
        referencia_nivel2d__cargos_estrutura__cargo=self
    ).exclude(
        models.Q(referencia_nivel2d__cargos_estrutura__data_vigencia_inicio__gt=data)
        | (
            ~models.Q(referencia_nivel2d__cargos_estrutura__data_vigencia_fim=None)
            & models.Q(referencia_nivel2d__cargos_estrutura__data_vigencia_fim__lt=data)
        )
    )

    if not salarios:
        log.debug(
            "(%s) %s - %s: %s | (%s) %s"
            % (self.pk, data, referencia, self, tabela.pk, tabela)
        )
        raise ReferenciaSalarialNotFound(
            "Não existe salario para o cargo %s na tabela %s" % (self, tabela)
        )

    if referencia:
        salarios = salarios.filter(referencia_nivel2d=referencia)

    if (
        self.tipo_lei_cargo
        in [
            "CM",
            "FC",
        ]
        and salarios.count() > 1
    ):
        log.debug(
            "Cargo/Função de confiança (%s) possui mais de um salário na tabela %s."
            % (self, tabela)
        )
        log.debug(
            ["%s:%s - " % (s.referencia_nivel2d, s.tabela_salarial) for s in salarios]
        )
        raise MultipleReferencias(
            "Cargo/Função de confiança (%s) possui mais de um salário na tabela %s. %s"
            % (
                self,
                tabela,
                ["%s:%s" % (s.referencia_nivel2d, s.tabela_salarial) for s in salarios],
            )
        )
    return salarios.order_by("referencia_nivel2d__ordem")[0]


def salarios(self, data_inicio=None, data_fim=None, referencia=None):
    salarios_ = []

    if data_inicio is None:
        data_inicio = datetime.today()

    if data_fim is None:
        data_fim = data_inicio

    range_ = NewDateRange(data_inicio, data_fim)

    tabelas = TabelaSalarial.tabelas_vigente(self, data_inicio, data_fim)

    ces = (
        CargosEstrutura.objects.filter(
            estrutura_salarial__in=[t.estrutura_salarial for t in tabelas], cargo=self
        )
        .exclude(
            models.Q(data_vigencia_inicio__gt=data_fim)
            | (
                ~models.Q(data_vigencia_fim=None)
                & models.Q(data_vigencia_fim__lt=data_inicio)
            )
        )
        .order_by("data_vigencia_inicio")
    )

    salarios_query = ReferenciaSalario.objects.filter(tabela_salarial__in=tabelas)
    if referencia:
        salarios_query = salarios_query.filter(referencia_nivel2d=referencia)

    for ce in ces:
        for salario in salarios_query.filter(
            referencia_nivel2d__in=ce.referencias.all()
        ):
            salarios_.append(
                (
                    range_.intersect(
                        NewDateRange(
                            ce.data_vigencia_inicio, ce.data_vigencia_fim
                        ).intersect(
                            NewDateRange(
                                salario.tabela_salarial.start_validity,
                                salario.tabela_salarial.end_validity,
                            )
                        )
                    ),
                    salario,
                )
            )

    if not salarios_:
        raise ReferenciaSalarialNotFound(
            "Não existe salario para o cargo %s na(s) tabela(s) vigente(s) %s"
            % (self, [str(t) for t in tabelas])
        )
    return salarios_


Cargo.get_salario = salario

Cargo.get_salarios = salarios
