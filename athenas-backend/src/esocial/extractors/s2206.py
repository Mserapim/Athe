# -.- coding: utf-8 -.-
import copy

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.extractors.base import ConfigReference, Factory
from esocial.extractors.s2200 import S2200Extractor
from esocial.models import S2200, S2206, Event
from rh.gfp.models import ExtraPaymentPeriod, MovimentacaoProgressao
from rh.models import MovimentacaoPosse, Servidor

log = getLogger(__name__)


class S2206Extractor(S2200Extractor):

    VALIDITY_FIELDS = ["alt_contratual_dt_alteracao"]

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2206Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        references = []
        start_validity = None
        end_validity = None
        financial_effect_date = None
        if self._event:
            start_validity = self._event.start_validity
            financial_effect_date = self._event.alt_contratual_dt_ef
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
        if not hasattr(self, "_references_strong_obj"):
            buff = self.cr_possession_ef(self._instance_outside)._references(
                start_validity
            )
            buff += self.cr_possession_cm_fc(self._instance_outside)._references(
                start_validity
            )
            buff += self.cr_progression(self._instance_outside)._references(
                start_validity
            )
            buff += self.cr_stay_allowance(self._instance_outside)._references(
                start_validity
            )
            setattr(self, "_references_strong_obj", buff)
        return self._references_strong_obj

    def _config(self):
        """Este método retorna o queryset básico da referência.

        Returns:
            queryset
        """
        return self._instance_outside.posses.filter(
            quadro__cargo__tipo_lei_cargo__in=["CM", "FC", "EF"]
        )

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
        return f"{instance_outside.matricula}-{dt_alt}-{dt_ef}"

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
        list_start_date = cls.cr_possession_ef(instance_outside)._queryset_date(
            pair_date=True
        )
        list_start_date += cls.cr_possession_cm_fc(instance_outside)._queryset_date(
            pair_date=True
        )
        list_start_date += cls.cr_progression(instance_outside)._queryset_date(
            pair_date=True
        )
        list_start_date += cls.cr_stay_allowance(instance_outside)._queryset_date(
            pair_date=True
        )

        dr_possessions = cls.range_possessions(instance_outside.matricula)
        dt_exclude = []
        for rs in dr_possessions.ranges():
            dt_exclude.append(rs[0])
            dt_exclude.append(rs[1])

        new_list_start_date = []
        for dates in list_start_date:
            dt = dates[0]
            if (
                dt >= cls.initial_group_date()
                and dr_possessions.in_range(dt)
                and dt not in dt_exclude
            ):
                new_list_start_date.append(dates)
        return new_list_start_date

    @classmethod
    def cr_possession_ef(cls, instance_outside):
        return ConfigReference(
            queryset=MovimentacaoPosse.objects.filter(
                Q(servidor__pk=instance_outside.pk)
                & Q(quadro__cargo__tipo_lei_cargo="EF")
            ).only_original(),
            start_validity_field="data_exercicio",
            financial_effect_field="financial_effect_date",
        )

    @classmethod
    def cr_possession_cm_fc(cls, instance_outside):
        return ConfigReference(
            queryset=MovimentacaoPosse.objects.filter(
                Q(servidor__pk=instance_outside.pk)
                & Q(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
            ),
            start_validity_field="data_exercicio",
            end_validity_field="data_desligamento",
            financial_effect_field="financial_effect_date",
        )

    @classmethod
    def cr_progression(cls, instance_outside):
        if cls._vinculo_tp_reg_trab() != 2:
            return ConfigReference(
                queryset=MovimentacaoProgressao.objects.filter(
                    Q(servidor__pk=instance_outside.pk)
                ),
                start_validity_field="data_inicio_vigencia",
                end_validity_field="data_fim_vigencia",
                financial_effect_field="data_inicio_vigencia",
            )
        return ConfigReference()

    @classmethod
    def cr_stay_allowance(cls, instance_outside):
        query_epp = ExtraPaymentPeriod.objects.filter(
            employee=instance_outside,
            extra_payment__slug__startswith="ABONO-PERMANENCIA",
            value__gt=0,
        ).order_by("decision_date")[0:1]
        return ConfigReference(
            queryset=query_epp,
            start_validity_field="decision_date",
            financial_effect_field="start_validity",
        )

    def description(self):
        return f"{self._instance_outside.type_by_possession} {self._instance_outside}"

    def ide_vinculo_cpf_trab(self):
        return self.trabalhador_cpf_trab()

    def ide_vinculo_matricula(self):
        return self.vinculo_matricula()

    def alt_contratual_dt_alteracao(self):
        return self.start_validity()

    def alt_contratual_dt_ef(self):
        return self._financial_effect_date

    def alt_contratual_dsc_alt(self):
        # FIXME: COMO PREENCHER?
        return None

    def trab_temp_just_prorr(self):
        return None

    def aprend_ind_aprend(self):
        return None

    def aprend_cnpj_ent_qual(self):
        return None

    def aprend_cnpj_prat(self):
        return None

    def info_estatutario_ind_abono_perm(self):
        """Este método está diferente do s2200 pois no s2206 estes campos são obrigatórios"""
        value = None
        if self.vinculo_tp_reg_prev() == 2:
            epp = ExtraPaymentPeriod.objects.currents_in(
                range=NewDateRange(self._start_validity, self._start_validity)
            ).filter(
                employee=self._instance_outside,
                extra_payment__slug__startswith="ABONO-PERMANENCIA",
                value__gt=0,
            )
            value = "S" if epp.exists() else "N"
        return value

    def serv_publ_mtv_alter(self):
        _mtv_alter = 9
        return _mtv_alter


class S2206Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2206
    EXTRACTOR = S2206Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        qs2200 = (
            oid
            for oid in S2200.objects.valids_by_status().values_list("oid", flat=True)
        )
        query = (
            Servidor.objects.by_type_job_position(["EF", "CM"])
            .without_required()
            .filter(matricula__in=qs2200)
        )
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
            Event.objects.filter(
                acronym__in=["s2200", "s2298"],
                registry_employee=instance_outside.matricula,
            )
            .validity_in(start_limit)
            .last()
        )
        if not event_registration:
            log.info(
                f"Não possui Evento de cadastro(S2200, S2298) para {instance_outside}. Tentando criar {self.EXTRACTED_MODEL_CLASS}."
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

    def delete_xsd_schema_invalid(self, oid, registry=None, registry_person=None):
        """Este método apaga os não validados.

        Args:
            oid (int):
            registry (int):
            registry_person (str):
        """
        query = self.extracted_class.objects.not_validated().filter(
            registry_employee=registry
        )
        for event in query:
            event.delete()
