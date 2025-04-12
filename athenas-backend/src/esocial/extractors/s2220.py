# -*- coding: utf-8 -*-
import copy

from django.template.defaultfilters import striptags

from contrib.utils import getLogger
from esocial.const import NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.models import S2220, Configuration, Exam, get_current_config
from health.sst.models import MonitorOccupationalHealth

log = getLogger(__name__)


class S2220Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2220Extractor, self).__init__(instance_outside, *args, **kwargs)

    @classmethod
    def initial_group_date(cls):
        return Configuration.current_config().initial_date_sst_events

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            start_validity = end_validity = self._event.start_validity
            if start_validity not in self._queryset_date(self._instance_outside):
                start_validity = end_validity = None
        else:
            start_validity = end_validity = self._start_validity

        references = self._references(start_validity)
        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside] if self._instance_outside else []

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
        list_start_date = (
            [instance_outside.monitoring_date.date()] if instance_outside else []
        )
        return list_start_date

    def pre_validate(self):
        if self._instance_outside:
            termination_date = self._instance_outside.employee.termination_date
            if (
                termination_date
                and self._instance_outside.monitoring_date.date() > termination_date
            ):
                return NOTHING_TODO
        return super().pre_validate()

    def start_validity(self):
        return self._start_validity

    def end_validity(self):
        return self._end_validity

    def validate_validity_fields(self):
        pass

    def oid(self):
        if self._instance_outside:
            return self._get_oid(self._instance_outside)
        return self._event.oid if self._event else None

    def description(self):
        return f"{self._instance_outside.employee.type_by_possession} {self._instance_outside.employee} - {self._instance_outside}"

    def registry_person(self):
        return self.ide_vinculo_cpf_trab()

    def registry_employee(self):
        return None

    def ide_vinculo_cpf_trab(self):
        return self._instance_outside.employee.pessoa_fisica.cpf

    def ide_vinculo_matricula(self):
        return str(self._instance_outside.employee.matricula)

    def ide_vinculo_cod_categ(self):
        return None

    def ex_med_ocup_tp_exame_ocup(self):
        return (
            0
            if self._instance_outside.type_aso == 99
            else self._instance_outside.type_aso
        )

    def aso_dt_aso(self):
        if self._instance_outside.monitoring_date.date() >= self.initial_group_date():
            return self._instance_outside.monitoring_date.date()
        return None

    def aso_res_aso(self):
        return 1 if self._instance_outside.result else 2

    def exam(self):
        createds = []
        for exam in self._instance_outside.examsst.all():
            exame_obs_proc = striptags(exam.note)
            createds.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self.start_validity().month,
                    "competence_year": self.start_validity().year,
                    "_class_": Exam,
                    "oid": f"{self._instance_outside.pk}{exam.pk}",
                    "exame_dt_exm": exam.exam_date.date(),
                    "exame_proc_realizado": exam.diagnosis_procedure.code,
                    "exame_obs_proc": exame_obs_proc if exame_obs_proc else None,
                    "exame_ord_exame": exam.order if exam.order != 99 else None,
                    "exame_ind_result": exam.result if exam.result != 99 else None,
                }
            )
        return createds

    def medico_nm_med(self):
        return f"{self._instance_outside.doctor.nome}"[0:69]

    def medico_nr_crm(self):
        professional_council = self._instance_outside.doctor.professional_council
        return professional_council.numero

    def medico_uf_crm(self):
        professional_council = self._instance_outside.doctor.professional_council
        return professional_council.estado_expedicao.sigla

    def resp_monit_cpf_resp(self):
        if self._instance_outside.doctor_manager:
            return self._instance_outside.doctor_manager.pessoa_fisica.cpf
        return None

    def resp_monit_nm_resp(self):
        if self._instance_outside.doctor_manager:
            return self._instance_outside.doctor_manager.pessoa_fisica.nome[0:69]
        return None

    def resp_monit_nr_crm(self):
        if self._instance_outside.doctor_manager:
            professional_council = (
                self._instance_outside.doctor_manager.professional_council
            )
            return professional_council.numero
        return None

    def resp_monit_uf_crm(self):
        if self._instance_outside.doctor_manager:
            professional_council = (
                self._instance_outside.doctor_manager.professional_council
            )
            return professional_council.estado_expedicao.sigla
        return None


class S2220Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2220
    EXTRACTOR = S2220Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = MonitorOccupationalHealth.objects.all()

        config = get_current_config()
        query = query.exclude(
            employee__matricula__in=(
                registry
                for registry in config.employee_exclude.values_list(
                    "matricula", flat=True
                )
            )
        )
        if config.employee_filter.exists():
            query = query.filter(
                employee__matricula__in=(
                    registry
                    for registry in config.employee_filter.values_list(
                        "matricula", flat=True
                    )
                )
            )

        return query.exclude(monitoring_date__lt=cls.initial_group_date()).order_by(
            "monitoring_date"
        )

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.monitoring_date.date()

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return start_limit

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return None

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
                    start_validity__gt=extracted_event.start_validity,
                    # ide_vinculo_matricula=instance_outside.employee.matricula,
                    registry_person=instance_outside.employee.pessoa_fisica.cpf,
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
                extractor_event = self.extractor(to_exc.instance_outside, **params)
                self.extractors_event_exclude.update({to_exc.pk: extractor_event})

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
        # oids = (self._get_oid(dep) for dep in MonitorOccupationalHealth.objects.filter(employee__matricula=registry))
        oids = (
            self._get_oid(dep)
            for dep in MonitorOccupationalHealth.objects.filter(
                employee__pessoa_fisica__cpf=registry_person
            )
        )

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
            extractor_event = self.extractor(event.instance_outside, **params)
            if not extractor_event.check_reference_strong():
                """Caso também não exista nos seus limites, será candidato a exclusão."""
                self.extractors_event_exclude.update({event.pk: extractor_event})
