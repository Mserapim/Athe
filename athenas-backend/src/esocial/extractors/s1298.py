# -*- coding: utf-8 -*-
from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import NO_RESTRICTION, NOTHING_TODO
from esocial.extractors.s1200 import ExtractorPayroll
from esocial.models import S1298

log = getLogger(__name__)


class S1298Extractor(ExtractorPayroll):

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
            S1298.objects.valids_sent()
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
