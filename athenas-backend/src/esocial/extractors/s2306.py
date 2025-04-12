# -*- coding: utf-8 -*-
import copy

from django.db.models.query_utils import Q

from contrib.utils import getLogger
from esocial.extractors.base import ConfigReference, Factory
from esocial.extractors.s2300 import (
    VALID_LINKS_EST,
    VALID_LINKS_REQUESTED,
    S2300Extractor,
)
from esocial.models import S2300, S2306
from rh.models import MovimentacaoPosse, Servidor

log = getLogger(__name__)


class S2306Extractor(S2300Extractor):

    VALIDITY_FIELDS = ["info_tsv_alteracao_dt_alteracao"]

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2306Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        _queryset_date = self._queryset_date(self._instance_outside)
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            start_validity = self._event.start_validity
            if self._event.start_validity not in _queryset_date:
                start_validity = end_validity = None
        else:
            start_validity = self._start_validity
            """definindo o fim com a data de desligamento"""

        references = self._references(start_validity)

        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        if not hasattr(self, "_references_strong_obj"):
            setattr(
                self,
                "_references_strong_obj",
                self.cr_possession_cm_fc(self._instance_outside)._references(
                    start_validity
                ),
            )
        return self._references_strong_obj

    def _queryset_date(self, instance_outside):
        if not hasattr(self, "_querysetdate"):
            setattr(
                self,
                "_querysetdate",
                copy.deepcopy(self._generate_queryset_date(instance_outside)),
            )
        return self._querysetdate

    @classmethod
    def _generate_queryset_date(cls, instance_outside):
        list_start_date = cls.cr_possession_cm_fc(instance_outside)._queryset_date()
        dr_possessions = cls.range_possessions(instance_outside.matricula)
        dt_exclude = []
        for rs in dr_possessions.ranges():
            dt_exclude.append(rs[0])
            dt_exclude.append(rs[1])
        list_start_date = set(
            filter(
                lambda dt: dt >= cls.initial_group_date()
                and dr_possessions.in_range(dt)
                and dt not in dt_exclude,
                list_start_date,
            )
        )

        return list_start_date

    @classmethod
    def cr_possession_cm_fc(cls, instance_outside):
        return ConfigReference(
            queryset=MovimentacaoPosse.objects.filter(
                Q(servidor__pk=instance_outside.pk)
                & Q(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
            ),
            start_validity_field="data_exercicio",
            end_validity_field="data_desligamento",
        )

    def ide_trab_sem_vinculo_cpf_trab(self):
        return self.trabalhador_cpf_trab()

    def ide_trab_sem_vinculo_matricula(self):
        return self.info_tsv_inicio_matricula()

    def ide_trab_sem_vinculo_cod_categ(self):
        return None

    def info_tsv_alteracao_dt_alteracao(self):
        return self.start_validity()

    def info_tsv_alteracao_nat_atividade(self):
        return self.info_tsv_inicio_nat_atividade()

    def local_trab_geral_tp_insc(self):
        if self.trainee:
            if self.possession_trainee():
                return self.configuration.ide_employer_tp_insc
            else:
                return None
        return self.configuration.ide_employer_tp_insc

    def local_trab_geral_nr_insc(self):
        if self.trainee:
            if self.possession_trainee():
                return self.configuration.ide_employer_nr_insc
            else:
                return None
        return self.configuration.ide_employer_nr_insc

    def local_trab_geral_desc_comp(self):
        return None


class S2306Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2306
    EXTRACTOR = S2306Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        qs2300 = (
            oid
            for oid in S2300.objects.valids_by_status().values_list("oid", flat=True)
        )
        return Servidor.objects.by_type_possession(
            VALID_LINKS_REQUESTED + VALID_LINKS_EST
        ).filter(matricula__in=qs2300)

    def _queryset_date(self, instance_outside):
        if not hasattr(self, "_querysetdate"):
            setattr(
                self,
                "_querysetdate",
                copy.deepcopy(self.EXTRACTOR._generate_queryset_date(instance_outside)),
            )
        return self._querysetdate

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        s2300 = (
            S2300.objects.filter(oid=instance_outside.matricula)
            .validity_in(start_limit)
            .last()
        )
        if not s2300:
            log.info(
                f"Não possui Evento de cadastro(S2300) para {instance_outside}. Tentando criar {self.EXTRACTED_MODEL_CLASS}."
            )
            return None

        return self._next_day(instance_outside, s2300.start_validity)

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return start_limit

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        list_start_date = self._queryset_date(instance_outside)
        return min(filter(lambda x: x > date, list_start_date), default=None)

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid. Utiliza start_limit para retornar eventos da data informada.
        """
        return self.extracted_class.objects.valids_by_status().filter(
            oid=oid, start_validity=start_limit, registry_employee=registry
        )

    def _find_covered_event_to_exclude(
        self,
        extracted_event,
        instance_outside,
        task=None,
        registry=None,
        registry_person=None,
        period=None,
        organizer=None,
    ):
        """Este método encontra os eventos encobertos por extracted_event para indicar a exclusão. Adiciona os eventos encontrados
        a extractors_event_exclude.

        Args:
            extracted_event (Event): evento extraído
            instance_outside (object): objeto de origem
            task (engine.mq.models.Task, optional): task. Defaults to None.
            registry (int, optional): matrícula do servidor. Defaults to None.
            registry_person (str, optional): cpf da pessoa física. Defaults to None.
            period (rh.gfp.models.Periodo, optional): período da folha. Defaults to None.
            organizer (object, optional): objeto organizador utilizado para prover agrupador de evento. Defaults to None.
        """
        if extracted_event:
            for to_exc in (
                self.extracted_class.objects.filter(
                    start_validity__gt=extracted_event.start_validity
                )
                .filter(registry_employee=registry)
                .valids_by_status()
                .exclude(pk=extracted_event)
            ):
                params = {
                    "task": task,
                    "event": to_exc,
                    "exclude": True,
                    "period": period,
                    "organizer": organizer,
                }
                extractor_event = self.extractor(instance_outside, **params)
                self.extractors_event_exclude.update({to_exc.pk: extractor_event})
