# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from esocial.const import (
    EVENT_KIND,
    EXCLUDE_EVENT,
    NO_RESTRICTION,
    NOTHING_TODO,
    PROCESS_STATUS_EVENT_VALIDS_SENT,
)
from esocial.extractors.base import Extractor
from esocial.models import Event

log = getLogger(__name__)

ALLOWED_EVENTS_CF = list(set(EVENT_KIND.get("CF")) - set(["s3000"]))
ALLOWED_EVENTS_FP = list(set(EVENT_KIND.get("FP")) - set(["s1298", "s1299"]))
ALLOWED_EVENTS_1010 = list(["s1010"])
ALLOWED_EVENTS = ALLOWED_EVENTS_CF + ALLOWED_EVENTS_FP + ALLOWED_EVENTS_1010


class S3000Extractor(Extractor):

    def pre_validate(self):
        if (
            self._instance_outside.process_status
            not in PROCESS_STATUS_EVENT_VALIDS_SENT
            and not self._instance_outside.process_receipt
        ):
            self.task_info(
                msg=f"Evento {self._instance_outside} deve ter status de sucesso para ser excluído pelo S3000",
                type_of=3,
            )
            return NOTHING_TODO

        if self._instance_outside.acronym not in ALLOWED_EVENTS:
            self.task_info(
                msg=f"Evento {self._instance_outside} não encontra-se entre os tipos permitidos para ser exluído pelo S3000.",
                type_of=3,
            )
            return NOTHING_TODO

        if self._event and self._exclude:
            return EXCLUDE_EVENT

        return NO_RESTRICTION

    def pos_validate(self):
        return NO_RESTRICTION

    def _define_references(self):
        return self._instance_outside.start_validity, None, [self._instance_outside]

    def validate_validity_fields(self):
        pass

    def competence_month(self):
        if self._event and self._event.competence_month == 13:
            return self._event.competence_month
        return super().competence_month()

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        if "events" in kwargs:
            return Event.objects.filter(pk__in=kwargs.get("events"))
        return Event.objects.none()

    def description(self):
        return (
            f"{self.modify_event().description} - {self.modify_event().event.acronym}"
        )

    def info_exclusao_tp_evento(self):
        return self._instance_outside.event.acronym.replace("s", "S-")

    def info_exclusao_nr_rec_evt(self):
        return self._instance_outside.event.process_receipt

    def ide_trabalhador_cpf_trab(self):
        return self._instance_outside.event.employee_cpf()

    def ide_folha_pagto_ind_apuracao(self):
        if self._instance_outside.event.acronym in [
            "s1200",
            "s1202",
            "s1207",
            "s1280",
            "s1300",
        ]:
            return self._instance_outside.event.ide_evento_ind_apuracao
        return None

    def ide_folha_pagto_per_apur(self):
        if self._instance_outside.event.acronym in (
            "s1200",
            "s1202",
            "s1207",
            "s1210",
            "s1280",
            "s1300",
        ):
            return self._instance_outside.event.ide_evento_per_apur
        return None

    def modify_event(self):
        return self._event

    def registry_employee(self):
        registry = None
        if hasattr(self.modify_event(), "registry_employee"):
            registry = self.modify_event().registry_employee
        return registry

    def registry_person(self):
        registry = None
        if hasattr(self.modify_event(), "registry_person"):
            registry = self.modify_event().registry_person
        return registry
