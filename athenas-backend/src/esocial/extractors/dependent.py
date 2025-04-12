# -.- coding: utf-8 -.-
from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.extractors.base import Extractor
from esocial.models import Dependent, ItemTable
from rh.const import (
    DEPENDENCY_INCOME_TAX,
    DEPENDENCY_SALARY_FAMILY,
    TYPE_BY_POSSESSION_BENEFICIARY,
)

log = getLogger(__name__)

TP_DEP_OUTROS = "99"


class DependentExtractor(Extractor):

    EXTRACTED_CLASS = Dependent
    INTERNAL = True

    def __init__(self, instance_outside, **kwargs):
        super(DependentExtractor, self).__init__(instance_outside, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        return (
            self._extractor_base.start_validity(),
            self._extractor_base.end_validity(),
            [self._instance_outside],
        )

    def validate_validity_fields(self):
        pass

    def start_validity(self):
        return self._extractor_base.start_validity()

    def end_validity(self):
        return self._extractor_base.end_validity()

    def dependente_tp_dep(self):
        return tp_dep(self._instance_outside)

    def dependente_nm_dep(self):
        return str(self._instance_outside.pessoa_fisica)

    def dependente_dt_nascto(self):
        return self._instance_outside.pessoa_fisica.data_nascimento

    def dependente_cpf_dep(self):
        return (
            self._instance_outside.pessoa_fisica.cpf
            if self._instance_outside.pessoa_fisica.cpf
            else None
        )

    def dependente_dep_irrf(self):
        start_date = self.start_validity()
        if start_date < self._extractor_base.initial_group_date():
            start_date = self._extractor_base.initial_group_date()
        dep = dependency(
            self._instance_outside, date_range=NewDateRange(start_date, start_date)
        )
        return "S" if dep.filter(tipo=DEPENDENCY_INCOME_TAX).exists() else "N"

    def dependente_dep_sf(self):
        start_date = self.start_validity()
        if start_date < self._extractor_base.initial_group_date():
            start_date = self._extractor_base.initial_group_date()
        dep = dependency(
            self._instance_outside, date_range=NewDateRange(start_date, start_date)
        )
        return "S" if dep.filter(tipo=DEPENDENCY_SALARY_FAMILY).exists() else "N"

    def dependente_inc_trab(self):
        return "S" if self._instance_outside.incapacity else "N"

    def dependente_sexo_dep(self):
        valids = (
            "EFE",
            "ECM",
            "EFC",
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "CMS",
        )
        if (
            self._extractor_base.vinculo_tp_reg_prev() == 2
            and self._extractor_base.vinculo_cad_ini() == "N"
            and self._instance_outside.servidor.type_by_possession in valids
        ):
            return self._instance_outside.pessoa_fisica.sexo

        if (
            self._instance_outside.servidor.type_by_possession
            in TYPE_BY_POSSESSION_BENEFICIARY
        ):
            return self._instance_outside.pessoa_fisica.sexo

        return None

    def dependente_inc_fis_men(self):
        from esocial.extractors.s2400 import S2400Extractor
        from esocial.extractors.s2405 import S2405Extractor

        if isinstance(self._extractor_base, (S2400Extractor, S2405Extractor)):
            return "S" if self._instance_outside.incapacity else "N"
        return None

    def dependente_descr_dep(self):
        if tp_dep(self._instance_outside) == TP_DEP_OUTROS:
            return f"{self._instance_outside}"
        return None


def tp_dep(inst_outside):
    return ItemTable.objects.by_choice_table(inst_outside.tipo, "7").code


def dependency(inst_outside, date_range):
    return inst_outside.dependencias.active_in(range=date_range)
