# -*- coding: utf-8 -*-
from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import NO_RESTRICTION, NOTHING_TODO
from esocial.extractors.s1200 import ExtractorPayroll
from esocial.models import S1210, S1299, Event

log = getLogger(__name__)


class S1299Extractor(ExtractorPayroll):

    def _define_references(self):
        month = self._period.mes
        if month == 13:
            month = 12
        dr_period = NewDateRange.from_month(self._period.ano, month)
        return dr_period.first, dr_period.last, self._references_strong()

    def _references_strong(self, start_validity=None):
        return [self._instance_outside]

    def pre_validate(self):
        query = (
            S1299.objects.valids_sent()
            .filter(
                oid=self._get_oid(
                    self._instance_outside,
                    month=self._period.mes,
                    year=self._period.ano,
                )
            )
            .exclude(closed_by_event__isnull=False)
        )
        if query.exists():
            return NOTHING_TODO
        return super().pre_validate()

    def pos_validate(self):
        return NO_RESTRICTION

    def competence_month(self):
        return self._period.mes

    def oid(self):
        return self._get_oid(
            self._instance_outside, month=self._period.mes, year=self._period.ano
        )

    def oid(self):
        return self._get_oid(
            self._instance_outside, month=self._period.mes, year=self._period.ano
        )

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        month = kwargs.get("month", 0)
        year = kwargs.get("year", 0)
        return f"{year}{month:02d}"

    def validate_validity_fields(self):
        pass

    @property
    def remun(self):
        """Este método checa se houve eventos s1200 ou s1202 ou s1207."""
        return (
            Event.objects.valids_sent()
            .filter(
                acronym__in=["s1200", "s1202", "s1207"],
                ide_evento_per_apur=self.ide_evento_per_apur(),
            )
            .exists()
        )

    def info_fech_evt_remun(self):
        log.debug(self.remun)
        return "S" if self.remun else "N"

    def info_fech_evt_pgtos(self):
        """Possui informações de pagamento de rendimentos do trabalho no período de apuração?
        Valores válidos: S - Sim N - Não
        Validação: Se for igual a [S], deve existir o evento S-1210 para o período de apuração, considerando o campo indGuia.
        Caso contrário, não deve existir o evento."""
        exists = (
            S1210.objects.valids_sent()
            .filter(ide_evento_per_apur=self.ide_evento_per_apur())
            .exists()
        )
        return "S" if exists else "N"

    def info_fech_evt_com_prod(self):
        return "N"

    def info_fech_evt_contrat_av_np(self):
        return "N"

    def info_fech_evt_info_compl_per(self):
        return "N"

    def info_fech_ind_exc_apur1250(self):
        return None

    def info_fech_trans_dctf_web(self):
        return None

    def info_fech_nao_valid(self):
        return None
