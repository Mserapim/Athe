# -.- coding: utf-8 -.-
from django.db.models import Q

from esocial.extractors.base import ConfigReference, Factory
from esocial.extractors.s2410 import S2410Extractor
from esocial.models import S2410, S2416
from rh.models import BenefitMovement, SuspensionBenefit


class S2416Extractor(S2410Extractor):

    VALIDITY_FIELDS = ["info_ben_alteracao_dt_alt_beneficio"]

    def __init__(self, *args, **kwargs):
        super(S2416Extractor, self).__init__(*args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        _queryset_date = self._queryset_date(self._instance_outside)
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            start_validity = self._event.start_validity
            list_validity = list(set([start_validity in x for x in _queryset_date]))
            if True not in list_validity:
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
        return self._cr_suspension(self._instance_outside)._references(start_validity)

    @classmethod
    def _queryset_date(cls, instance_outside):
        list_start_date = cls._cr_suspension(instance_outside)._queryset_date()
        list_start_date = set(
            filter(lambda dt: dt >= cls.initial_group_date(), list_start_date)
        )
        return list_start_date

    def oid(self):
        return self._get_oid(self._instance_outside, start_limit=self._start_validity)

    @classmethod
    def _cr_suspension(cls, instance_outside):
        return ConfigReference(
            queryset=SuspensionBenefit.objects.filter(
                benefit_movement_id=instance_outside.pk
            ),
            start_validity_field="start_validity",
            end_validity_field="end_validity",
        )

    def ide_beneficio_cpf_benef(self):
        return self._instance_outside.servidor.pessoa_fisica.cpf

    def ide_beneficio_nr_beneficio(self):
        return self.info_ben_inicio_nr_beneficio()

    def info_ben_alteracao_dt_alt_beneficio(self):
        return self.start_validity()

    def suspension_benefit(self):
        return self._instance_outside.benefit_suspensions.filter(
            Q(end_validity__isnull=True) | Q(end_validity__gt=self.start_validity())
        )

    def dados_beneficio_ind_suspensao(self):
        if self.suspension_benefit():
            return "S"

        return "N"

    def suspensao_mtv_suspensao(self):
        if self.dados_beneficio_ind_suspensao() == "S":
            return self.suspension_benefit().first().reason
        return None

    def suspensao_dsc_suspensao(self):
        if self.suspensao_mtv_suspensao() and self.suspensao_mtv_suspensao() == "99":
            return self.suspension_benefit().first().reason_description
        return None


class S2416Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2416
    EXTRACTOR = S2416Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return BenefitMovement.objects.filter()

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        event_registration = (
            S2410.objects.filter(registry_employee=instance_outside.servidor.matricula)
            .validity_in(start_limit)
            .last()
        )
        if not event_registration:
            message = f"Não possui Evento de cadastro(S2410) para {instance_outside}."
            message = f"{message} Tentando criar {self.EXTRACTED_MODEL_CLASS}."
            return None

        return self._next_day(instance_outside, event_registration.start_validity)

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return start_limit

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        list_start_date = self.EXTRACTOR._queryset_date(instance_outside)
        return min(filter(lambda x: x > date, list_start_date), default=None)

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
