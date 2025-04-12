# -.- coding: utf-8 -.-
import copy
from datetime import datetime

from contrib.utils import getLogger
from esocial.extractors.base import Factory
from esocial.extractors.s2410 import S2410Extractor
from esocial.models import S2418, S2420
from rh.models import BenefitMovement

log = getLogger(__name__)


class S2418Extractor(S2410Extractor):

    def __init__(self, *args, **kwargs):
        super(S2418Extractor, self).__init__(*args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        references = []
        start_validity = None
        end_validity = None
        financial_effect_date = None
        if self._event:
            start_validity = self._event.start_validity
            financial_effect_date = self._event.info_reativ_dt_efeito
            dates = [start_validity, financial_effect_date]
            if dates in self._queryset_date(self._instance_outside):
                self._financial_effect_date = financial_effect_date
            else:
                start_validity = end_validity = self._financial_effect_date = None
        else:
            start_validity = self._start_validity

        references = self._references(start_validity)

        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside]

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
        financial_effect_date = instance_outside.data_exercicio
        if instance_outside.financial_effect_date:
            financial_effect_date = instance_outside.financial_effect_date
        list_start_date = [[instance_outside.data_exercicio, financial_effect_date]]

        new_list_start_date = []
        for dates in list_start_date:
            dt = dates[0]
            if dt >= cls.initial_group_date():
                new_list_start_date.append(dates)
        return new_list_start_date

    def oid(self):
        return self._get_oid(
            self._instance_outside,
            start_limit=self._start_validity,
            financial_effect_date=self._financial_effect_date,
        )

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        dt_alt = kwargs.get("start_limit", None)
        dt_ef = kwargs.get("financial_effect_date", None)
        return f"{instance_outside.benefit_number}-{dt_alt}-{dt_ef}"

    def ide_beneficio_cpf_benef(self):
        return self.beneficiario_cpf_benef()

    def ide_beneficio_nr_beneficio(self, instance_outside=None):
        return self.info_ben_inicio_nr_beneficio()

    def info_reativ_dt_efet_reativ(self):
        if (
            self._instance_outside.data_exercicio
            > self._instance_outside.reactivated_benefit.data_desligamento
            and self._instance_outside.data_exercicio <= datetime.now().date()
        ):
            return self._instance_outside.data_exercicio

    def info_reativ_dt_efeito(self):
        if self.info_reativ_dt_efet_reativ():
            if (
                self._instance_outside.financial_effect_date
                <= self.info_reativ_dt_efet_reativ()
                and self._instance_outside.financial_effect_date
                > self._instance_outside.reactivated_benefit.data_desligamento
            ):
                return self._instance_outside.financial_effect_date


class S2418Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2418
    EXTRACTOR = S2418Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return BenefitMovement.objects.filter(reactivated_benefit__isnull=False)

    def _filter_by_factory(self, query, registry_employee=None, registry_person=None):
        """Este método deve ser utilizado para filter em query.

        Args:
            registry_employee (int): a matrícula do servidor
            registry_person (str): o cpf da pessoa física

        Returns:
            query (queryset):"""
        if registry_employee:
            query = query.filter(servidor__matricula=registry_employee)
        return query

    def _queryset_date(self, instance_outside):
        if not hasattr(self, "_querysetdate"):
            setattr(
                self,
                "_querysetdate",
                copy.deepcopy(self.EXTRACTOR._generate_queryset_date(instance_outside)),
            )
        return self._querysetdate

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        event_registration = (
            S2420.objects.filter(registry_employee=instance_outside.servidor.matricula)
            .validity_in(start_limit)
            .last()
        )
        if not event_registration:
            log.info(
                f"Não possui Evento de Término(S2420) para {instance_outside}. Tentando criar {self.EXTRACTED_MODEL_CLASS}."
            )
            return None

        rs = []
        for dates in self._queryset_date(instance_outside):
            dt = dates[0]
            if dt > event_registration.start_validity:
                if not rs:
                    rs = dates
                if dt < rs[0]:
                    rs = dates
        if rs:
            self._queryset_date(instance_outside).remove(rs)
        return rs

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return [start_limit, start_limit]

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        rs = []
        for dates in self._queryset_date(instance_outside):
            dt = dates[0]
            if dt == date:
                rs = dates
                break
            if dt > date:
                if not rs:
                    rs = dates
                if dt < rs[0]:
                    rs = dates
        if rs:
            self._queryset_date(instance_outside).remove(rs)
        return rs

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid. Utiliza start_limit para retornar eventos da data informada.
        """
        oid = oid.split("-")[0]
        return self.extracted_class.objects.valids_by_status().filter(
            oid__icontains=oid, start_validity=start_limit, registry_employee=registry
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
            oid = self._get_oid(
                instance_outside, start_limit=extracted_event.start_validity
            )
            oid = oid.split("-")[0]
            for to_exc in (
                self.extracted_class.objects.filter(
                    start_validity__gt=extracted_event.start_validity,
                    oid__icontains=oid,
                    registry_employee=registry,
                )
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

    def _query_delete_not_send(self, oid=None, registry=None, registry_person=None):
        """Este método gera a queryset dos eventos que podem ser excluídos. Utiliza a queryset can_exclude como default.
        Aplicando os parâmetros no filter como AND.

        Args:
            oid (int):
            registry (int):
            registry_person (str):

        Returns:
            queryset."""
        oid = oid.split("-")[0]
        return self.extracted_class.objects.can_exclude().filter(oid__icontains=oid)
