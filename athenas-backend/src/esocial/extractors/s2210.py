# -*- coding: utf-8 -*-
import copy

from django.template.defaultfilters import striptags

from contrib.utils import getLogger
from esocial.const import NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.extractors.registrationbaseworker import type_street
from esocial.models import S2210, Configuration, get_current_config
from health.sst.models import WorkAccidentCommunication
from health.const import NOT_SUPPLIED, YES_OP, NO_OP

log = getLogger(__name__)


MAP_YES_NO_NOT_SUPPLIED = {NOT_SUPPLIED: None, YES_OP: "S", NO_OP: "N"}


class S2210Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2210Extractor, self).__init__(instance_outside, *args, **kwargs)

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
            [instance_outside.accident_date.date()] if instance_outside else []
        )
        return list_start_date

    def pre_validate(self):
        if self._instance_outside:
            termination_date = self._instance_outside.employee.termination_date
            if (
                termination_date
                and self._instance_outside.accident_date.date() > termination_date
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

    def cat_dt_acid(self):
        if self._instance_outside.accident_date.date() >= self.initial_group_date():
            return self._instance_outside.accident_date.date()
        return None

    def cat_tp_acid(self):
        return self._instance_outside.type_cat

    def cat_hr_acid(self):
        if self._instance_outside.accident_date.date() >= self.initial_group_date():
            return self._instance_outside.accident_date.strftime("%H%M").replace(
                ":", ""
            )
        return None

    def cat_hrs_trab_antes_acid(self):
        return self._instance_outside.work_hours_before_accident

    def cat_tp_cat(self):
        return self._instance_outside.type_cat

    def cat_ind_cat_obito(self):
        return "S" if self._instance_outside.death else "N"

    def cat_dt_obito(self):
        return (
            self._instance_outside.death_date.date()
            if self._instance_outside.death_date
            else None
        )

    def cat_ind_comun_policia(self):
        return "S" if self._instance_outside.police_communication else "N"

    def cat_cod_sit_geradora(self):
        return int(self._instance_outside.causer_agent_accident.code)

    def cat_iniciat_cat(self):
        return self._instance_outside.initiator_cat

    def cat_obs_cat(self):
        cat_obs_cat = striptags(self._instance_outside.note_cat)
        return cat_obs_cat if cat_obs_cat else None

    def cat_ult_dia_trab(self):
        return self._instance_outside.last_work_date

    def cat_houve_afast(self):
        """Houve afastamento?
        Valores válidos: S - Sim N - Não
        Validação: Preenchimento obrigatório se dtAcid >= [2023-01-16])."""
        return MAP_YES_NO_NOT_SUPPLIED.get(self._instance_outside.leave_work_accident)

    def local_acidente_tp_local(self):
        return self._instance_outside.type_address_accident

    def local_acidente_dsc_local(self):
        if self._instance_outside.address_description != "":
            return self._instance_outside.address_description
        return None

    def local_acidente_tp_lograd(self):
        return type_street(self._instance_outside.address)

    def local_acidente_dsc_lograd(self):
        address = self._instance_outside.address
        if address:
            return (address.logradouro[:80]).lstrip() if address.logradouro else None
        return None

    def local_acidente_nr_lograd(self):
        address = self._instance_outside.address
        if address:
            return (address.numero[:10] if address.numero else None) or "S/N"
        return None

    def local_acidente_complemento(self):
        address = self._instance_outside.address
        value = None
        if address:
            value = address.complemento
            value = striptags(value)[0:30]
            if len(value) == 0 or value.isspace():
                value = None
        return value

    def local_acidente_bairro(self):
        address = self._instance_outside.address
        if address:
            return address.bairro
        return None

    def local_acidente_cep(self):
        if self.local_acidente_tp_local() != 2:
            address = self._instance_outside.address
            value = None
            if address:
                value = address.cep
            return ("".join(filter(str.isdigit, str(value))))[0:8] if value else value
        return None

    def local_acidente_cod_munic(self):
        if self.local_acidente_tp_local() != 2:
            address = self._instance_outside.address
            if address:
                return address.municipio.ibge
        return None

    def local_acidente_uf(self):
        if self.local_acidente_tp_local() != 2:
            address = self._instance_outside.address
            if address:
                return address.municipio.estado.sigla
        return None

    def local_acidente_pais(self):
        if self.local_acidente_tp_local() == 2:
            address = self._instance_outside.address
            if address:
                return str(address.municipio.estado.pais.esocial_code)
        return None

    def local_acidente_cod_postal(self):
        if self.local_acidente_tp_local() == 2:
            return self.local_acidente_cep()
        return None

    def ide_local_acid_tp_insc(self):
        # TODO: NECESSÁRIO INFORMAR NO MODELO DE ORIGEM
        return self.ide_empregador_tp_insc()

    def ide_local_acid_nr_insc(self):
        # TODO: NECESSÁRIO INFORMAR NO MODELO DE ORIGEM
        return self.configuration.ide_employer_nr_insc

    def parte_atingida_cod_parte_ating(self):
        return int(self._instance_outside.body_part.code)

    def parte_atingida_lateralidade(self):
        if self._instance_outside.laterality == 99:
            return 0
        return self._instance_outside.laterality

    def agente_causador_cod_agnt_causador(self):
        return int(self._instance_outside.causer_agent.code)

    def atestado_dt_atendimento(self):
        return self._instance_outside.attest_date.date()

    def atestado_hr_atendimento(self):
        return self._instance_outside.attest_date.strftime("%H%M").replace(":", "")

    def atestado_ind_internacao(self):
        return "S" if self._instance_outside.hospitalization else "N"

    def atestado_dur_trat(self):
        return self._instance_outside.duration_treatment

    def atestado_ind_afast(self):
        atestado_ind_afast = MAP_YES_NO_NOT_SUPPLIED.get(
            self._instance_outside.leave_work_treatment
        )
        return atestado_ind_afast if atestado_ind_afast else "N"

    def atestado_dsc_lesao(self):
        return int(self._instance_outside.nature_injury.code)

    def atestado_dsc_comp_lesao(self):
        if self._instance_outside.nature_injury_description != "":
            return self._instance_outside.nature_injury_description
        return None

    def atestado_diag_provavel(self):
        if self._instance_outside.diagnosis != "":
            return self._instance_outside.diagnosis
        return None

    def atestado_cod_cid(self):
        return self._instance_outside.cid

    def atestado_observacao(self):
        atestado_observacao = striptags(self._instance_outside.note_attest)
        return atestado_observacao if atestado_observacao else None

    def emitente_nm_emit(self):
        return f"{self._instance_outside.doctor_attest.nome}"[0:69]

    def emitente_ide_oc(self):
        map_professional_council = {
            "CRM": 1,  # Conselho Regional de Medicina - CRM
            "CRO": 2,  # Conselho Regional de Odontologia - CRO
            "RMS": 3,  # Registro do Ministério da Saúde - RMS
        }
        professional_council = self._instance_outside.doctor_attest.professional_council
        return map_professional_council.get(
            professional_council.professional_council_issuer.valor
        )

    def emitente_nr_oc(self):
        professional_council = self._instance_outside.doctor_attest.professional_council
        return professional_council.numero

    def emitente_uf_oc(self):
        professional_council = self._instance_outside.doctor_attest.professional_council
        return professional_council.estado_expedicao.sigla

    def cat_origem_nr_rec_cat_orig(self):
        if self._instance_outside.previous:
            previous_s2210 = S2210.objects.filter(
                oid=self._instance_outside.previous.pk
            ).last()
            if previous_s2210:
                return previous_s2210.process_receipt
        return None


class S2210Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2210
    EXTRACTOR = S2210Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = WorkAccidentCommunication.objects.all()

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

        query = query.exclude(accident_date__lt=cls.initial_group_date())

        return query.order_by("accident_date")

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.accident_date.date()

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
            for dep in WorkAccidentCommunication.objects.filter(
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
