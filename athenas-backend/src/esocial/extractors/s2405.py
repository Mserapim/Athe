# -.- coding: utf-8 -.-
from django.db.models import Q

from contrib.utils import getLogger
from esocial.extractors.base import ConfigReference, Factory
from esocial.extractors.s2400 import S2400Extractor
from esocial.models import S2400, S2405
from rh.const import TYPE_BY_POSSESSION_BENEFICIARY
from rh.models import Molestia, Servidor

log = getLogger(__name__)


class S2405Extractor(S2400Extractor):

    MAP_FIELDS_EQUALS = {
        "dados_benef_est_civ": "beneficiario_est_civ",
        "dados_benef_sexo": "beneficiario_sexo",
        "dados_benef_nm_benefic": "beneficiario_nm_benefic",
        "dados_benef_raca_cor": "beneficiario_raca_cor",
        "ide_benef_cpf_benef": "beneficiario_cpf_benef",
    }

    EXCLUDE_FIELDS_EQUALS = ["alteracao_dt_alteracao"]

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        self.cr_dependencies = self._cr_dependency(self._instance_outside)
        self.cr_histories = self._cr_history(self._instance_outside)
        self.cr_diseases = self._cr_disease(self._instance_outside)

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

        self.natural_person_history = None
        self.person_address = None
        self.person_address_outsider = None
        if start_validity:
            self.natural_person_history = self.cr_histories.queryset.filter(
                data_alteracao_esocial=start_validity
            ).last()
            if self.natural_person_history:
                self.person_address = self.natural_person_history.address.filter(
                    outsider=False
                ).last()
                self.person_address_outsider = (
                    self.natural_person_history.address.filter(outsider=True).last()
                )

        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        """define as queries dos objetos de referência válidos"""
        references = self.cr_dependencies._references(start_validity)
        references += self.cr_diseases._references(start_validity)
        references += self.cr_histories._references(start_validity)
        return references

    @classmethod
    def _queryset_date(cls, instance_outside):
        list_start_date = cls._cr_dependency(
            instance_outside
        )._queryset_date()  # pair_date=True
        list_start_date += cls._cr_history(instance_outside)._queryset_date()
        list_start_date += cls._cr_disease(
            instance_outside
        )._queryset_date()  # pair_date=True

        if instance_outside.termination_date:
            list_start_date = set(
                filter(lambda x: x < instance_outside.termination_date, list_start_date)
            )
        list_start_date = set(
            filter(lambda x: x >= cls.initial_group_date(), list_start_date)
        )

        return list_start_date

    @classmethod
    def _cr_disease(cls, instance_outside):
        return ConfigReference(
            queryset=Molestia.objects.filter(servidor__pk=instance_outside.pk),
            start_validity_field="data_laudo",
        )

    def oid(self):
        return self._get_oid(self._instance_outside, start_limit=self._start_validity)

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        start_validity = kwargs.get("start_limit", None)
        return f"{instance_outside.matricula}-{start_validity}"

    def description(self):
        return f"{self._instance_outside.type_by_possession} {self._instance_outside}"

    def ide_benef_cpf_benef(self):
        return self.beneficiario_cpf_benef()

    def alteracao_dt_alteracao(self):
        return self.start_validity()

    def dados_benef_nm_benefic(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nome:
            natural_person_history = self.natural_person_history
        return super().trabalhador_nm_trab(natural_person_history)

    def dados_benef_sexo(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.sexo:
            natural_person_history = self.natural_person_history
        return super().trabalhador_sexo(natural_person_history)

    def dados_benef_raca_cor(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.raca_cor:
            natural_person_history = self.natural_person_history
        return super().trabalhador_raca_cor(natural_person_history)

    def dados_benef_est_civ(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.estado_civil:
            natural_person_history = self.natural_person_history
        return super().trabalhador_est_civ(natural_person_history)

    def dados_benef_inc_fis_men(self):
        return self.beneficiario_inc_fis_men()


class S2405Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2405
    EXTRACTOR = S2405Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        qs2400 = (rs[0] for rs in S2400.objects.valids_by_status().values_list("oid"))
        query = Servidor.objects.by_type_possession(
            TYPE_BY_POSSESSION_BENEFICIARY
        ).filter(Q(matricula__in=qs2400))

        return query

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        event_registration = (
            S2400.objects.filter(registry_employee=instance_outside.matricula)
            .validity_in(start_limit)
            .last()
        )
        if not event_registration:
            message = f"Não possui Evento de cadastro(S2400) para {instance_outside}."
            message = f"{message} Tentando criar {self.EXTRACTED_MODEL_CLASS}."
            log.info(message)
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
        rs = min(filter(lambda x: x > date, list_start_date), default=None)
        return rs

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
                .filter(
                    oid=self._get_oid(
                        instance_outside, start_limit=extracted_event.start_validity
                    )
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
        return self.extracted_class.objects.can_exclude().filter(
            registry_employee=registry
        )
