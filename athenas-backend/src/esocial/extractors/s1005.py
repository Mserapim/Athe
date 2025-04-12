# -*- coding: utf-8 -*-
from django.db.models import Q

from contrib.utils import getLogger
from esocial.extractors.base import Extractor, Factory, administrative_unit
from esocial.models import S1005
from rh.models import EstablishmentConfig, ProcessSuspension, UnidadeAdministrativa

from .utils import format_reference, limits_from_date

log = getLogger(__name__)


class S1005Extractor(Extractor):

    VALIDITY_FIELDS = [
        "ide_estab_ini_valid",
        "ide_estab_fim_valid",
        "nova_validade_ini_valid",
        "nova_validade_fim_valid",
    ]

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong() + self._references_weak()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        references = []
        q_config_reference = self._query_config_reference()
        if q_config_reference.exists():
            references.append(q_config_reference.last())
        return references

    def _references_strong_start_date(self):
        return [
            limits_from_date(obj.start_validity)[0] for obj in self._references_strong()
        ]

    def _references_end_date(self):
        return [obj.end_validity for obj in self._references() if obj.end_validity]

    @property
    def _class_config(self):
        return EstablishmentConfig

    def _config(self):
        return self._class_config.objects.filter(
            administrative_unit__pk=self._instance_outside.pk
        )

    def ide_estab_tp_insc(self):
        return self.configuration.ide_employer_tp_insc

    def ide_estab_nr_insc(self):
        return self.configuration.ide_employer_nr_insc

    def ide_estab_ini_valid(self):
        if self._event:
            return format_reference(self._event.start_validity)
        return super(S1005Extractor, self).ini_valid()

    def ide_estab_fim_valid(self):
        if self._event:
            return format_reference(self._event.end_validity)
        return super(S1005Extractor, self).fim_valid()

    def dados_estab_cnae_prep(self):
        config = self._query_config_reference().last()
        return config.cnae_preponderant if config else None

    def aliq_gilrat_aliq_rat(self):
        process_suspension = self.get_process(rat=True)
        config = None
        if process_suspension:
            config = self._query_config_reference().last()
        return config.rat_value if config else None

    def aliq_gilrat_fap(self):
        config = self._query_config_reference().last()
        return config.fap_value if config and config.send_fap else None

    def proc_adm_jud_rat_tp_proc(self):
        process_suspension = self.get_process(rat=True)
        if process_suspension is not None:
            self.set_dependency(
                oid=process_suspension.process.number_process,
                filter_query_instance=Q(
                    number_process=process_suspension.process.number_process
                ),
                acronyms=("s1070",),
            )
        return process_suspension.process.type_process if process_suspension else None

    def proc_adm_jud_rat_nr_proc(self):
        process_suspension = self.get_process(rat=True)
        return process_suspension.process.number_process if process_suspension else None

    def proc_adm_jud_rat_cod_susp(self):
        process_suspension = self.get_process(rat=True)
        return process_suspension.pk if process_suspension else None

    def proc_adm_jud_fap_tp_proc(self):
        process_suspension = self.get_process(fap=True)
        if process_suspension is not None:
            self.set_dependency(
                oid=process_suspension.process.number_process,
                filter_query_instance=Q(
                    number_process=process_suspension.process.number_process
                ),
                acronyms=("s1070",),
            )
        return process_suspension.process.type_process if process_suspension else None

    def proc_adm_jud_fap_nr_proc(self):
        process_suspension = self.get_process(fap=True)
        return process_suspension.process.number_process if process_suspension else None

    def proc_adm_jud_fap_cod_susp(self):
        process_suspension = self.get_process(fap=True)
        return process_suspension.pk if process_suspension else None

    def info_caepf_tp_caepf(self):
        return None

    def info_obra_ind_subst_patr_obra(self):
        return None

    def info_apr_nr_proc_jud(self):
        return None

    def info_ent_educ_nr_insc(self):
        return None

    def info_pcd_nr_proc_jud(self):
        return None

    def nova_validade_ini_valid(self):
        return self.start_validity().strftime("%Y-%m")

    def nova_validade_fim_valid(self):
        return self.end_validity().strftime("%Y-%m") if self.end_validity() else None

    def get_process(self, rat=False, fap=False):
        query = ProcessSuspension.objects.none()
        if self._start_validity:
            query = ProcessSuspension.objects.filter(
                process__matter_process=1,  # tributaria
                indicative_suspension=14,
                scope_decision=2,
                start_validity__lte=self._start_validity,
            )
            if rat:
                query = query.filter(rat_modified=True)
            elif fap:
                query = query.filter(fap_modified=True)
        return query.last()


class S1005Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1005
    EXTRACTOR = S1005Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return UnidadeAdministrativa.objects.filter(pk=administrative_unit().pk)
