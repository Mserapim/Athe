# -*- coding: utf-8 -*-

from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.decorator import cache_return
from contrib.utils import getLogger
from rh.afastamento.models import AfastamentoOutroOrgao, BaseLicencaAfastamento
from rh.const import CANCELADO
from standard.models import Configuration, RunCodeManager

log = getLogger("calculo")


class ServidorDesconhecido(Exception):
    pass


class FolhaDesconhecida(Exception):
    pass


@RunCodeManager.register("gfp-calculo-base")
class BaseCalculo(object):
    typeof = "CALCULO"
    titulo = "Calculo Base"
    descricao = "Este calculo pode ser usado de forma genérica para calculos simples"

    class ErroCalculation(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Erro ao calcular evento...")
            )

    class CalculationNotApplicable(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Cálculo não aplicável ao servidor...")
            )

    # Parametros que poderão ser usador como @params do calculo
    PARAMS_ = [
        "info",
    ]

    def __init__(
        self,
        servidor,
        folha,
        evento=None,
        entry=None,
        exclude_events=[],
        only_events=[],
        year=None,
        month=None,
        params={},
        differences=False,
        group_cache=None,
    ):
        """
        Inicializador do calculo, recebe o servidor, folha a ser calculada e o evento que possui o calculo automático.
        """
        self.cfg = Configuration.get_or_create("gfp")
        self.payroll = folha
        self.employee = servidor
        self.year = year if year else self.payroll.periodo.ano
        self.month = month if month else self.payroll.periodo.mes
        self.range_salary = NewDateRange.from_month(
            self.year, (self.month if self.month < 12 else 12)
        )
        self.exclude_events = exclude_events
        self.only_events = only_events
        self.event = evento
        self.differences = differences

        self.exclude_events = self.exclude_events
        self.evento = evento
        self.servidor = servidor
        self.folha = self.payroll
        self.range_folha = self.range_salary

        # Carregando apenas os params que poder ser passados para o calculo. Definidos em @PARAMS_
        self.params = {}
        for p in params:
            if p in self.PARAMS_:
                self.params[p] = params[p]
        log.debug("CALC PARAMS: %s <> %s" % (params, self.params))

    @property
    def tipos_servidor(self):
        return [
            mp.quadro.cargo.tipo_lei_cargo
            for mp in self.servidor.get_posses_ativas(
                self.range_folha.first, self.range_folha.last
            )
        ]

    # @cache_return
    def quantidade_maxima(self):
        if self.event and self.event.quantidade_max is not None:
            return float(self.event.quantidade_max)
        return 0.00

    # @cache_return
    def quantidade(self):
        if "qnt" in self.params and self.params["qnt"] not in ["", 0]:
            return float(self.params["qnt"])
        if (
            self.event
            and self.event
            and self.event
            and self.event.quantidade is not None
        ):
            return float(self.event and self.event.quantidade)
        return self.quantidade_maxima()

    @cache_return
    def fator_quantidade(self):
        fator = 1.0
        try:
            fator = self.quantidade() / float(self.quantidade_maxima())
        except ZeroDivisionError:
            fator = 1.0
        except Exception as e:
            log.exception(e)
        # finally:
        #     log.info("FATOR de BaseCalculo: %s" % fator)

        return fator

    @cache_return
    def porcentagem(self):
        if "pct" in self.params and self.event and self.event.tipo_calculo in [1, 5]:
            return float(self.params["pct"])
        pct = (
            float(self.event.porcentagem)
            if self.event and self.event.porcentagem
            else 100.0
        )
        # log.info("PORCENTAGEM de BaseCalculo: %s" % pct)
        return pct

    # @cache_return
    def base_previdenciaria(self, total=False):
        """
        Este calculo deve ser sobrescrito para todo calculo que
        se deseja saber a base previdenciária utilizada pelo calculo
        """
        # log.info("BP de BaseCalculo")
        return self.valor()

    def descontos_base(self):
        return 0.0

    @cache_return
    def valor_base(self):
        if not self.event:
            return 0.00

        if self.event.valor_base:
            return float(self.event.valor_base)

        incide_sobre = [e.numero for e in self.event.incide_sobre.all()]
        soma = 0.00
        q_entries = Q(
            evento__numero__in=incide_sobre, contracheque__servidor=self.employee
        )
        if self.exclude_events:
            q_entries = Q(q_entries & ~Q(evento__numero__in=self.exclude_events))
        if self.only_events:
            q_entries = Q(q_entries & Q(evento__numero__in=self.only_events))
        # log.debug('QUERY: %s' % q_entries)

        for fe in self.folha.lancamentos.filter(q_entries):
            soma += float(
                fe.correct_value if fe.evento.tipo == "P" else -fe.correct_value
            )
            # log.info(u">>>>>>>> %s : (%s) %s " % (fe.evento, fe.evento.tipo, fe.valor))
        valor_base = soma - self.descontos_base()
        return valor_base if not self.event.calculo_invertido else -valor_base

    @property
    @cache_return
    def teto(self):
        return float(self.event.teto) if self.event and self.event.teto else 9999999.99

    @property
    @cache_return
    def piso(self):
        return float(self.event.piso) if self.event and self.event.piso else 0.00

    @cache_return
    def valor(self):
        # valor_base = self.valor_base() if self.teto() > self.valor_base() else self.teto()
        valor = (
            self.valor_base() * self.fator_quantidade() * (self.porcentagem() / 100.00)
        )
        valor = min(valor, self.teto)
        valor = max(valor, self.piso)
        log.info(
            "VALOR [%s-%s]: %s/%s >> %s"
            % (self.piso, self.teto, valor, self.valor_base(), self.__class__.__name__)
        )
        return valor

    def valor_patronal(self):
        if "patronal" in self.params:
            return float(self.params["patronal"])
        return 0.0

    def base_socialsecurity(self):
        return self.valor_patronal()

    def info_evento(self):
        if "info" in self.params:
            return self.params["info"]
        return ""

    def validate(self):
        return True

    def vars(self):
        return {}

    def callback(self, **kargs):
        log.debug("CALLBACK for %s" % self.__class__.__name__)

    @property
    def data_referencia_cargo(self):
        return date(year=self.folha.periodo.ano, month=self.folha.periodo.mes, day=1)

    @property
    def efetivo(self):
        return "EF" in self.tipos_servidor

    @property
    def comissionado(self):
        return "CM" in self.tipos_servidor

    @property
    def acordo_de_cooperacao(self):
        return "AC" in self.tipos_servidor

    @property
    def estagiario(self):
        return "ES" in self.tipos_servidor

    def value(self):
        return self.valor()

    def calcular(self):
        log.debug("CALCULAR of %s [%s]" % (self.__class__.__name__, self.params))
        """
        Metodo responsável por realizar o calculo.
        """
        obj = {
            "qnt": 0,
            "pct": 0,
            "valor_base": 0,
            "valor": 0,
            "base_previdencia": 0,
            "patronal": 0,
            "info": "",
            "vars": {},
            "callback": self.callback,
            "validate": {"message": ""},
        }

        try:
            self.validate()
            log.debug("CALCULAR pos-validate %s" % self.__class__.__name__)
            obj.update(
                {
                    # round(self.quantidade() if self.event and self.event.quantidade_max > 0 else 0.0, 2),
                    "qnt": self.quantidade(),
                    "qnt_max": round(self.quantidade_maxima(), 2),
                    "pct": round(
                        (
                            self.porcentagem()
                            if self.event and self.event.tipo_calculo in [1, 5]
                            else 0.0
                        ),
                        2,
                    ),
                    "valor_base": round(self.valor_base(), 2),
                    "valor": round(self.valor(), 2),
                    "base_previdencia": round(self.base_previdenciaria(), 2),
                    "patronal": round(self.valor_patronal(), 2),
                    "info": self.info_evento(),
                    "vars": self.vars(),
                }
            )
        except self.CalculationNotApplicable as e:
            # log.exception('CalculationNotApplicable: %s' % e)
            log.info(str(e))
            # log.info('Calculo %s nao aplicavel ao servidor %s' % (self.titulo, self.servidor))
            obj["validate"]["message"] = str(e)
        except Exception as e:
            log.exception(e)
            obj["validate"]["message"] = "Erro no cálculo!"

        return obj


class QuantidadeCalculo(BaseCalculo):
    pass


class DiasCalculo(QuantidadeCalculo):
    """
    Calculo que utiliza a quantidade de dias de efetivo exercicio no mês de
    referencia da folha para calcular o "qnt"
    """

    @cache_return
    def get_posses(self):
        return self.servidor.get_posses_ativas(
            self.range_folha.first, self.range_folha.last
        )

    # @cache_return
    def range_posse_folha(self, posse=None):
        range_posse_folha = NewDateRange()
        if not posse:
            for posse in self.get_posses():
                range_posse_folha += NewDateRange(
                    posse.data_exercicio,
                    (
                        (posse.data_desligamento - relativedelta(days=1))
                        if posse.data_desligamento
                        else None
                    ),
                )
        else:
            range_posse_folha = NewDateRange(
                posse.data_exercicio,
                (
                    (posse.data_desligamento - relativedelta(days=1))
                    if posse.data_desligamento
                    else None
                ),
            )

        range_posse_folha = range_posse_folha.intersect(self.range_folha)

        ausencias_nao_remuneradas = NewDateRange()
        for mc in (
            AfastamentoOutroOrgao.objects.filter(servidor=self.servidor)
            .exclude(
                Q(data_inicio__gt=self.folha.date_range.last)
                | Q(onus=1)
                | Q(transito_pela_folha=True)
            )
            .exclude(estado=CANCELADO)
        ):
            ausencias_nao_remuneradas += NewDateRange(mc.data_inicio, mc.data_fim)
        for afastamento in (
            BaseLicencaAfastamento.objects.filter(
                remunerado=False, servidor=self.servidor
            )
            .exclude(
                Q(data_fim__lt=self.folha.date_range.first)
                | Q(data_inicio__gt=self.folha.date_range.last)
            )
            .exclude(~Q(afastamento__afastamentooutroorgao=None))
            .exclude(estado=CANCELADO)
        ):
            ausencias_nao_remuneradas += NewDateRange(
                afastamento.data_inicio, afastamento.data_fim
            )
        return (
            (range_posse_folha - ausencias_nao_remuneradas)
            if ausencias_nao_remuneradas.days > 0
            else range_posse_folha
        )

    def get_posses_mes_folha(self, tipos=[]):
        """
        Retorna as posses de efetivo que o servidor tinha no mes da referencia da folha,
        pois pode ser que o servidor começou o mês com um cargo e depois tomou posse em
        outro sendo exonerado do primeiro
        """
        if not isinstance(tipos, list):
            tipos = [tipos]
        posses = (
            self.get_posses()
            .filter(quadro__cargo__tipo_lei_cargo__in=tipos)
            .order_by("-data_exercicio")
        )

        return posses

    # @cache_return
    def quantidade_dias_from_range(self, limites_posse):
        limites_folha = self.range_folha
        limites_exercicio = limites_folha.intersect(limites_posse)

        return limites_exercicio.business_days

    # @cache_return
    def quantidade_dias_from_posse(self, posse):
        limites_posse = NewDateRange(
            posse.data_exercicio,
            (
                (posse.data_desligamento - relativedelta(days=1))
                if posse.data_desligamento
                else None
            ),
        )
        return self.quantidade_dias_from_range(limites_posse)

    def quantidade_dias(self):
        return 0

    def quantidade(self):
        return self.quantidade_dias()


class PorcentagemCalculo(BaseCalculo):
    def porcentagem(self):
        return 0.00
