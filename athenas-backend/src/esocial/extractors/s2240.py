# -*- coding: utf-8 -*-
import copy

from django.template.defaultfilters import striptags

from contrib.utils import getLogger
from esocial.const import NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.models import (
    S2240,
    Configuration,
    Epi,
    HarmfulAgent,
    ResponsibleS2240,
    get_current_config,
)
from health.sst.models import ExposureEmployeeEnvironment

log = getLogger(__name__)


class S2240Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2240Extractor, self).__init__(instance_outside, *args, **kwargs)

    @classmethod
    def initial_group_date(cls):
        return Configuration.current_config().initial_date_sst_events

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            start_validity = self._event.start_validity
            end_validity = self._references_strong_end_date()
            if start_validity not in self._queryset_date(self._instance_outside):
                start_validity = end_validity = None
        else:
            start_validity = self._start_validity
            end_validity = self._references_strong_end_date()

        references = self._references(start_validity)
        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside] if self._instance_outside else []

    def _references_strong_end_date(self, start_validity=None):
        return self._instance_outside.end_validity if self._instance_outside else None

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
        list_start_date = [instance_outside.start_validity] if instance_outside else []
        return list_start_date

    def pre_validate(self):
        if self._instance_outside:
            termination_date = self._instance_outside.employee.termination_date
            if (
                termination_date
                and self._instance_outside.start_validity > termination_date
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
        if self._instance_outside:
            return f"{self._instance_outside.employee.type_by_possession} {self._instance_outside.employee}"
        return ""

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

    def info_exp_risco_dt_ini_condicao(self):
        if self._instance_outside.start_validity >= self.initial_group_date():
            return self._instance_outside.start_validity
        return None

    def info_exp_risco_dt_fim_condicao(self):
        return self._instance_outside.end_validity

    def info_amb_local_amb(self):
        return self._instance_outside.environment_working_condition.type_environment

    def info_amb_dsc_setor(self):
        return (
            self._instance_outside.environment_working_condition.description_departament
        )

    def info_amb_tp_insc(self):
        return self.ide_empregador_tp_insc()

    def info_amb_nr_insc(self):
        return self.configuration.ide_employer_nr_insc

    def info_ativ_dsc_ativ_des(self):
        return striptags(self._instance_outside.description_activity)

    def ag_noc(self):
        createds = []
        if self._instance_outside:
            for (
                environmentharmfulagent
            ) in (
                self._instance_outside.environment_working_condition.environmentharmfulagent.all()
            ):
                type_evaluation = None
                if environmentharmfulagent.type_evaluation != 99:
                    type_evaluation = environmentharmfulagent.type_evaluation

                epis = self.epi(environmentharmfulagent)

                epc_epi_utiliz_epc = None
                epc_epi_efic_epc = None
                epc_epi_utiliz_epi = None
                epc_epi_efic_epi = None
                epi_compl_med_protecao = None
                epi_compl_cond_functo = None
                epi_compl_uso_inint = None
                epi_compl_prz_valid = None
                epi_compl_periodic_troca = None
                epi_compl_higienizacao = None
                if environmentharmfulagent.harmful_agent.code != "09.01.001":
                    epc_epi_utiliz_epc = environmentharmfulagent.epc
                    if epc_epi_utiliz_epc == 99:
                        epc_epi_utiliz_epc = 0

                    epc_epi_utiliz_epi = environmentharmfulagent.epi
                    if epc_epi_utiliz_epi == 99:
                        epc_epi_utiliz_epi = 0

                    epc_epi_efic_epc = None
                    if epc_epi_utiliz_epc == 2:
                        epc_epi_efic_epc = (
                            "S" if environmentharmfulagent.efficiency_epc else "N"
                        )

                    epc_epi_efic_epi = None
                    if epc_epi_utiliz_epi == 2:
                        epc_epi_efic_epi = (
                            "S" if environmentharmfulagent.efficiency_epi else "N"
                        )

                    epi_compl_med_protecao = None
                    epi_compl_cond_functo = None
                    epi_compl_uso_inint = None
                    epi_compl_prz_valid = None
                    epi_compl_periodic_troca = None
                    epi_compl_higienizacao = None

                    if len(epis) > 0:
                        epi_compl_med_protecao = (
                            "S" if environmentharmfulagent.implement_protection else "N"
                        )
                        epi_compl_cond_functo = (
                            "S" if environmentharmfulagent.working_condition else "N"
                        )
                        epi_compl_uso_inint = (
                            "S" if environmentharmfulagent.uninterrupted_use else "N"
                        )
                        epi_compl_prz_valid = (
                            "S"
                            if environmentharmfulagent.expiry_date_on_purchase
                            else "N"
                        )
                        epi_compl_periodic_troca = (
                            "S" if environmentharmfulagent.change_frequency else "N"
                        )
                        epi_compl_higienizacao = (
                            "S" if environmentharmfulagent.sanitation else "N"
                        )

                ag_noc_un_med = None
                ag_noc_tec_medicao = None
                ag_noc_nr_proc_jud = None
                ag_noc_int_conc = None
                ag_noc_lim_tol = None
                if environmentharmfulagent.type_evaluation == 1:
                    ag_noc_un_med = (
                        environmentharmfulagent.measure_unit
                        if environmentharmfulagent.measure_unit != 99
                        else None
                    )
                    ag_noc_tec_medicao = (
                        environmentharmfulagent.measurement
                        if environmentharmfulagent.measurement != ""
                        else None
                    )
                    ag_noc_int_conc = environmentharmfulagent.intensity

                    if environmentharmfulagent.harmful_agent.code in (
                        "01.18.001",
                        "02.01.014",
                    ):
                        ag_noc_lim_tol = environmentharmfulagent.limit

                createds.append(
                    {
                        "start_validity": self.start_validity(),
                        "end_validity": self.end_validity(),
                        "competence_month": self.start_validity().month,
                        "competence_year": self.start_validity().year,
                        "registry_employee": self.registry_employee(),
                        "registry_person": self.registry_person(),
                        "_class_": HarmfulAgent,
                        "oid": f"{self._instance_outside.pk}{environmentharmfulagent.pk}",
                        "ag_noc_cod_ag_noc": environmentharmfulagent.harmful_agent.code,
                        "ag_noc_dsc_ag_noc": (
                            environmentharmfulagent.description
                            if environmentharmfulagent.description
                            else None
                        ),
                        "ag_noc_tp_aval": type_evaluation,
                        "ag_noc_int_conc": ag_noc_int_conc,
                        "ag_noc_lim_tol": ag_noc_lim_tol,
                        "ag_noc_un_med": ag_noc_un_med,
                        "ag_noc_tec_medicao": ag_noc_tec_medicao,
                        "ag_noc_nr_proc_jud": ag_noc_nr_proc_jud,
                        "epc_epi_utiliz_epc": epc_epi_utiliz_epc,
                        "epc_epi_efic_epc": epc_epi_efic_epc,
                        "epc_epi_utiliz_epi": epc_epi_utiliz_epi,
                        "epc_epi_efic_epi": epc_epi_efic_epi,
                        "epi_compl_med_protecao": epi_compl_med_protecao,
                        "epi_compl_cond_functo": epi_compl_cond_functo,
                        "epi_compl_uso_inint": epi_compl_uso_inint,
                        "epi_compl_prz_valid": epi_compl_prz_valid,
                        "epi_compl_periodic_troca": epi_compl_periodic_troca,
                        "epi_compl_higienizacao": epi_compl_higienizacao,
                        "epi": epis,
                    }
                )
        return createds

    def epi(self, environmentharmfulagent):
        createds = []
        for epi in environmentharmfulagent.epis.all():
            createds.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self.start_validity().month,
                    "competence_year": self.start_validity().year,
                    "_class_": Epi,
                    "oid": f"{environmentharmfulagent.pk}{epi.pk}",
                    "epi_doc_aval": epi.code,
                }
            )
        return createds

    def resp_reg(self):
        createds = []
        if self._instance_outside:
            responsible = (
                self._instance_outside.environment_working_condition.responsible
            )
            IDE_OC_MAP = {
                "CRM": 1,  # Conselho Regional de Medicina - CRM,
                "CREA": 4,  # Conselho Regional de Engenharia e Agronomia - CREA,
                #  9,  # Outros
            }
            ide_oc = IDE_OC_MAP.get(
                responsible.professional_council.professional_council_issuer.valor, 9
            )

            createds.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "competence_month": self.start_validity().month,
                    "competence_year": self.start_validity().year,
                    "_class_": ResponsibleS2240,
                    "oid": f"{responsible.cpf}",
                    "resp_reg_cpf_resp": responsible.cpf,
                    "resp_reg_ide_oc": ide_oc,
                    "resp_reg_dsc_oc": (
                        responsible.professional_council.professional_council_issuer.valor
                        if ide_oc == 9
                        else None
                    ),
                    "resp_reg_nr_oc": responsible.professional_council.numero,
                    "resp_reg_uf_oc": responsible.professional_council.estado_expedicao.sigla,
                }
            )
        return createds

    def obs_obs_compl(self):
        # models.CharField(max_length=999, null=True, blank=True)
        return None


class S2240Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2240
    EXTRACTOR = S2240Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = ExposureEmployeeEnvironment.objects.all()

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

        return query.order_by("start_validity")

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.start_validity

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
                    ide_vinculo_matricula=instance_outside.employee.matricula,
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
        oids = (
            self._get_oid(dep)
            for dep in ExposureEmployeeEnvironment.objects.filter(
                employee__matricula=registry
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
