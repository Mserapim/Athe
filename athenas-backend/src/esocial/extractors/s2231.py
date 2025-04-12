# -*- coding: utf-8 -*-
import copy
from datetime import datetime

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.extractors.base import Extractor
from esocial.extractors.s2200 import S2200Factory
from esocial.extractors.s2230 import S2230Factory
from esocial.models import S2231, get_current_config
from rh.afastamento.models import AfastamentoOutroOrgao
from rh.const import ACTIVE, CANCELED, FINISHED
from rh.models import Servidor

log = getLogger(__name__)


class S2231Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2231Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        references = []
        start_validity = None
        end_validity = None
        if self._event:
            start_validity = self._event.start_validity
            if start_validity not in self._queryset_date(self._instance_outside):
                start_validity = end_validity = None
        else:
            start_validity = self._start_validity

        references = self._references(start_validity)
        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return (
            [self._instance_outside]
            if self._instance_outside and not self._instance_outside.estado == CANCELED
            else []
        )

    def _references_strong_end_date(self, start_validity=None):
        dt = self._instance_outside.data_fim
        if dt and dt > datetime.now().date():
            dt = None
        return dt

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
        list_start_date = []
        if instance_outside and not instance_outside.estado == CANCELED:
            if instance_outside.data_inicio > cls.initial_group_date():
                list_start_date.append(instance_outside.data_inicio)
            if instance_outside.data_fim:
                list_start_date.append(instance_outside.data_fim)
        return list_start_date

    @classmethod
    def _get_control_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        oid = None
        start_validity = kwargs.get("start_validity", None)
        if start_validity and instance_outside:
            if start_validity == instance_outside.data_inicio:
                oid = "I"
            elif start_validity == instance_outside.data_fim:
                oid = "F"
        return oid

    def control_oid(self):
        return self._get_control_oid(
            self._instance_outside, start_validity=self.start_validity()
        )

    def start_validity(self):
        return self._start_validity

    def end_validity(self):
        return self._end_validity

    def validate_validity_fields(self):
        pass

    def oid(self):
        if self._instance_outside:
            return self._get_oid(
                self._instance_outside, start_validity=self.start_validity()
            )
        return self._event.oid

    def description(self):
        descr = f"{self._instance_outside.servidor.type_by_possession} {self._instance_outside.servidor}"
        descr += f" - {self._instance_outside.situation_unicode}: {self._instance_outside.get_estado_display()}"
        return descr

    def ide_vinculo_cpf_trab(self):
        return self._instance_outside.servidor.pessoa_fisica.cpf

    def ide_vinculo_matricula(self):
        return str(self._instance_outside.servidor.matricula)

    def ini_cessao_dt_ini_cessao(self):
        if (
            self.control_oid() == "I"
            and self._instance_outside.data_inicio > self.initial_group_date()
            and self._instance_outside.data_inicio == self.start_validity()
        ):
            return self._instance_outside.data_inicio
        return None

    def ini_cessao_cnpj_cess(self):
        if (
            self.control_oid() == "I"
            and self._instance_outside.data_inicio > self.initial_group_date()
        ):
            return ini_cessao_cnpj_cess(self._instance_outside)
        return None

    def ini_cessao_resp_remun(self):
        if (
            self.control_oid() == "I"
            and self._instance_outside.data_inicio > self.initial_group_date()
        ):
            return ini_cessao_resp_remun(self._instance_outside)
        return None

    def fim_cessao_dt_term_cessao(self):
        if (
            self._instance_outside.data_fim
            and self._instance_outside.data_fim == self.start_validity()
        ):
            return self._instance_outside.data_fim
        return None


def ini_cessao_cnpj_cess(instance_outside):
    if instance_outside.orgao and instance_outside.orgao.pessoa_juridica:
        value = instance_outside.orgao.pessoa_juridica.cnpj
    return value


def ini_cessao_resp_remun(instance_outside):
    _map = {
        1: "S",  # ORIGEM,  # : 'ORIGEM',
        2: "N",  # REQUISITANTE,  # : 'REQUISITANTE',
        3: "S",  # ORIGEM_REQUISITANTE,  # : 'Cedente e Cessionário',
    }
    return _map.get(instance_outside.onus)


class S2231Factory(S2230Factory):

    EXTRACTED_MODEL_CLASS = S2231
    EXTRACTOR = S2231Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        config = get_current_config()
        initial_date = cls.initial_group_date()
        employess_fired = Servidor.objects.filter(Q(termination_date__lt=initial_date))
        query = (
            AfastamentoOutroOrgao.objects.currents_in(range=NewDateRange(initial_date))
            .filter(
                servidor__pk__in=(
                    pk
                    for pk in S2200Factory._query_instances_outside().values_list(
                        "pk", flat=True
                    )
                )
            )
            .filter(estado__in=[ACTIVE, FINISHED])
            .not_canceled()
            .exclude(
                Q(data_inicio__lt=initial_date)
                & (
                    Q(data_fim__isnull=True)
                    | Q(data_fim__isnull=False, data_fim__gt=datetime.today().date())
                )
            )
            .exclude(data_fim__lt=config.cut_off_date_s2231)
        )

        query = query.exclude(
            servidor__pk__in=(pk for pk in employess_fired.values_list("pk", flat=True))
        )

        # query = query.filter(pk=25171)

        return query.order_by("data_inicio")

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid."""
        control_oid = self._get_control_oid(
            instance_outside, start_validity=start_limit
        )
        return self.extracted_class.objects.valids_by_status().filter(
            oid=oid, control_oid=control_oid, registry_employee=registry
        )

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

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        list_start_date = self.EXTRACTOR._generate_queryset_date(instance_outside)
        return min(list_start_date) if list_start_date else None

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return start_limit

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        list_start_date = self.EXTRACTOR._generate_queryset_date(instance_outside)
        next_day = min(filter(lambda x: x > date, list_start_date), default=None)
        return next_day

    def _set_extractors_event_exclude(
        self,
        oid=None,
        registry=None,
        registry_person=None,
        filter_query_instance=None,
        organizer=None,
        task=None,
    ):
        """Este método encontra os eventos candidatos a exclusão. Ele roda na fase inicial do manage_in_bulk.
        Adiciona os eventos encontrados a extractors_event_exclude.

        Args:
            oid (_type_, optional): _description_. Defaults to None.
            registry (_type_, optional): _description_. Defaults to None.
            registry_person (_type_, optional): _description_. Defaults to None.
            filter_query_instance (_type_, optional): _description_. Defaults to None.
            organizer (_type_, optional): _description_. Defaults to None.
            task (_type_, optional): _description_. Defaults to None."""
        departures = AfastamentoOutroOrgao.objects.filter(
            servidor__matricula=registry
        ).exclude(estado=CANCELED)
        oids = (self._get_oid(dep) for dep in departures)

        query = self.extracted_class.objects.valids_by_status().filter(
            registry_employee=registry
        )

        for event in query.exclude(oid__in=oids):
            """Caso evento não exista nos limites informados, verifica se existe em seus próprios limites."""
            params = {
                "event": event,
                "start_validity": event.start_validity,
                "end_validity": event.end_validity,
                "task": task,
            }
            extractor_event = self.extractor(event.departure, **params)
            if not extractor_event.check_reference_strong():
                """Caso também não exista nos seus limites, será candidato a exclusão."""
                self.extractors_event_exclude.update({event.pk: extractor_event})
