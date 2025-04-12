# -*- coding: utf-8 -*-
from django.db.models import Q
from dateutil.relativedelta import relativedelta
from contrib.utils import getLogger
from contrib.daterange import NewDateRange
from rh.gfp.models import ExtensionSalaryProgression
from standard.models import RunCodeManager
from rh.const import CANCELADO
from rh.ponto.models import Falta as Lack
from rh.afastamento.models import AfastamentoSuspensao

from datetime import datetime

log = getLogger(__name__)


@RunCodeManager.register("salaryprogression-base")
class SalaryProgressionBase(object):
    typeof = "PROGRESSION"
    title = "Código de validações base"
    description = ""

    def __init__(self, salaryprogression, **kwargs):
        self.salaryprogression = salaryprogression
        self.configure()

    def configure(self):
        pass

    def validate(self, *args, **kwargs):
        log.debug(
            "VALIDATE PROGRESSAO %s - %s"
            % (str(self.salaryprogression), self.salaryprogression.pk)
        )
        if (
            not self.salaryprogression.referencia_nivel2d.cargos_estrutura.filter(
                cargo=self.salaryprogression.movimentacao_posse.quadro.cargo
            )
            .exclude(
                Q(data_vigencia_inicio__gt=self.salaryprogression.data_inicio_vigencia)
                | (
                    ~Q(data_vigencia_fim=None)
                    & Q(
                        data_vigencia_fim__lt=self.salaryprogression.data_inicio_vigencia
                    )
                )
            )
            .exists()
        ):
            message = (
                "O cargo %s não pertence a nenhuma estrutura da tabela salarial da referência %s"
                % (
                    self.salaryprogression.movimentacao_posse.quadro.cargo,
                    self.salaryprogression.referencia_nivel2d,
                )
            )
            log.exception(message)
            raise Exception(message)

    def requirements(self, *args, **kwargs):
        self.salaryprogression._requirements = {"wait": [], "unfit": [], "block": []}
        return self.salaryprogression._requirements

    def _get_days_suspended_absenses(self, *args, **kwargs):
        salaryprogression = self.salaryprogression
        expected_date = self.initial_expected_date()
        if salaryprogression.progressao_anterior:
            departures = (
                AfastamentoSuspensao.objects.filter(
                    Q(servidor=salaryprogression.servidor)
                    & Q(data_inicio__gte=salaryprogression.data_inicio_vigencia)
                    & Q(data_fim__lte=expected_date)
                )
                .exclude(estado=CANCELADO)
                .order_by("data_inicio")
            )
        else:
            departures = (
                AfastamentoSuspensao.objects.filter(
                    Q(servidor=salaryprogression.servidor)
                    & Q(data_inicio__gte=salaryprogression.data_inicio_vigencia)
                )
                .exclude(estado=CANCELADO)
                .order_by("data_inicio")
            )

        range_departures_days = NewDateRange()
        for departure in departures.order_by("data_inicio"):
            print(departure)
            if departure.data_inicio <= expected_date:
                dr = NewDateRange(departure.data_inicio, departure.data_fim)
                range_departures_days += dr
                try:
                    expected_date += relativedelta(days=dr.days)
                except OverflowError:
                    expected_date = datetime.strptime("9999-12-31", "%Y-%m-%d").date()
        return range_departures_days.days

    def _get_days_lack_work(self, *args, **kwargs):
        try:
            salaryprogression = self.salaryprogression
            lack = 0
            if salaryprogression.progressao_anterior:
                query = Lack.objects.filter(
                    servidor=salaryprogression.servidor,
                    injustificada__gt=0,
                    data__lte=salaryprogression.data_inicio_vigencia,
                    data__gte=salaryprogression.progressao_anterior.data_inicio_vigencia,
                )
            else:
                query = Lack.objects.filter(
                    servidor=salaryprogression.servidor,
                    injustificada__gt=0,
                    data__lte=salaryprogression.data_inicio_vigencia,
                )
            if self.expected_date():
                query = query.filter(data__lte=self.expected_date())
            for f in query:
                days = f.days
                if days[1] >= 1:
                    lack += 1
            return lack
        except Exception as e:
            log.error(e)

    def expected_date(self, *args, **kwargs):
        salaryprogression = self.salaryprogression
        if salaryprogression.next_reference:
            expected_date = salaryprogression.data_referencia + relativedelta(
                months=salaryprogression.referencia_nivel2d.months_progression,
                days=self._get_days_suspended_absenses()
                + salaryprogression.dias_suspenso,
            )
            if ExtensionSalaryProgression.objects.filter(
                progression__servidor=salaryprogression.servidor,
                progression__referencia_nivel2d=salaryprogression.referencia_nivel2d,
            ).exists():
                days = 0
                for extension in ExtensionSalaryProgression.objects.filter(
                    progression__servidor=salaryprogression.servidor,
                    progression__referencia_nivel2d=salaryprogression.referencia_nivel2d,
                ):
                    days += extension.days
                expected_date = expected_date + relativedelta(days=days)
        else:
            expected_date = None
        return expected_date

    def initial_expected_date(self):
        return self.salaryprogression.data_referencia + relativedelta(
            months=self.salaryprogression.referencia_nivel2d.months_progression
        )

    def calculate(self):
        self.validate()
        return {
            "initial_expected_date": self.initial_expected_date(),
            "expected_date": self.expected_date(),
            "period_absences": self._get_days_lack_work(),
            "dias_suspenso_afastamento": self._get_days_suspended_absenses(),
            "requirements": self.requirements(),
        }
