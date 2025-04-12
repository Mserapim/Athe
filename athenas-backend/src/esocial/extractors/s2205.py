# -*- coding: utf-8 -*-
from django.db.models import Q

from contrib.utils import getLogger
from esocial.extractors.base import Factory
from esocial.extractors.s2200 import S2200Extractor
from esocial.models import S2200, S2205, S2300, Event
from rh.models import Servidor

log = getLogger(__name__)


class S2205Extractor(S2200Extractor):

    MAP_FIELDS_EQUALS = {
        "dados_trabalhador_grau_instr": "trabalhador_grau_instr",
        "dados_trabalhador_est_civ": "trabalhador_est_civ",
        "dados_trabalhador_sexo": "trabalhador_sexo",
        "dados_trabalhador_nm_trab": "trabalhador_nm_trab",
        "dados_trabalhador_raca_cor": "trabalhador_raca_cor",
        "ide_trabalhador_cpf_trab": "trabalhador_cpf_trab",
        "dados_trabalhador_pais_nac": "nascimento_pais_nascto",
    }

    EXCLUDE_FIELDS_EQUALS = [
        "alteracao_dt_alteracao",
    ]

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2205Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""

        self.cr_dependencies = self._cr_dependency(self._instance_outside)
        self.cr_histories = self._cr_history(self._instance_outside)

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
        return self.cr_dependencies._references(
            start_validity
        ) + self.cr_histories._references(start_validity)

    @classmethod
    def _queryset_date(cls, instance_outside):
        list_start_date = cls._cr_dependency(instance_outside)._queryset_date()
        list_start_date += cls._cr_history(instance_outside)._queryset_date()
        if instance_outside.termination_date:
            list_start_date = set(
                filter(lambda x: x < instance_outside.termination_date, list_start_date)
            )
        list_start_date = set(
            filter(lambda x: x >= cls.initial_group_date(), list_start_date)
        )

        return list_start_date

    def description(self):
        return f"{self._instance_outside.type_by_possession} {self._instance_outside}"

    def alteracao_dt_alteracao(self):
        return self.start_validity()

    def ide_trabalhador_cpf_trab(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_cpf_trab(natural_person_history)

    def dados_trabalhador_nm_trab(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_nm_trab(natural_person_history)

    def dados_trabalhador_sexo(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_sexo(natural_person_history)

    def dados_trabalhador_raca_cor(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_raca_cor(natural_person_history)

    def dados_trabalhador_est_civ(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_est_civ(natural_person_history)

    def dados_trabalhador_grau_instr(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_grau_instr(natural_person_history)

    def dados_trabalhador_nm_soc(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.trabalhador_nm_soc(natural_person_history)

    def dados_trabalhador_pais_nac(self):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return self.nascimento_pais_nascto(natural_person_history)

    def trabalhador_nm_trab(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nome:
            natural_person_history = self.natural_person_history
        return super().trabalhador_nm_trab(natural_person_history)

    def trabalhador_sexo(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.sexo:
            natural_person_history = self.natural_person_history
        return super().trabalhador_sexo(natural_person_history)

    def trabalhador_raca_cor(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.raca_cor:
            natural_person_history = self.natural_person_history
        return super().trabalhador_raca_cor(natural_person_history)

    def trabalhador_est_civ(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.estado_civil:
            natural_person_history = self.natural_person_history
        return super().trabalhador_est_civ(natural_person_history)

    def trabalhador_grau_instr(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.grau_instrucao:
            natural_person_history = self.natural_person_history
        return super().trabalhador_grau_instr(natural_person_history)

    def trabalhador_nm_soc(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.social_name:
            natural_person_history = self.natural_person_history
        return super().trabalhador_nm_soc(natural_person_history)

    def nascimento_dt_nascto(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.data_nascimento:
            natural_person_history = self.natural_person_history
        return super().nascimento_dt_nascto(natural_person_history)

    def nascimento_pais_nascto(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.natural_person_history.municipio_naturalidade
        ):
            natural_person_history = self.natural_person_history
        return super().nascimento_pais_nascto(natural_person_history)

    def nascimento_pais_nac(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history and self.natural_person_history.nationality:
            natural_person_history = self.natural_person_history
        return super().nascimento_pais_nac(natural_person_history)

    def brasil_tp_lograd(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.tipo_logradouro
        ):
            natural_person_history = self.natural_person_history
        return super().brasil_tp_lograd(natural_person_history)

    def brasil_nr_lograd(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.numero
        ):
            natural_person_history = self.person_address
        return super().brasil_nr_lograd(natural_person_history)

    def brasil_complemento(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.complemento
        ):
            natural_person_history = self.person_address
        return super().brasil_complemento(natural_person_history)

    def brasil_bairro(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.bairro
        ):
            natural_person_history = self.person_address
        return super().brasil_bairro(natural_person_history)

    def brasil_cep(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.cep
        ):
            natural_person_history = self.person_address
        return super().brasil_cep(natural_person_history)

    def brasil_cod_munic(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.municipio
        ):
            natural_person_history = self.person_address
        return super().brasil_cod_munic(natural_person_history)

    def brasil_uf(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.municipio
        ):
            natural_person_history = self.person_address
        return super().brasil_uf(natural_person_history)

    def exterior_pais_resid(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.country
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_pais_resid(natural_person_history)

    def exterior_dsc_lograd(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.logradouro
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_dsc_lograd(natural_person_history)

    def exterior_nr_lograd(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.numero
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_nr_lograd(natural_person_history)

    def exterior_complemento(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.complemento
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_complemento(natural_person_history)

    def exterior_bairro(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.bairro
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_bairro(natural_person_history)

    def exterior_nm_cid(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.municipio
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_nm_cid(natural_person_history)

    def exterior_cod_postal(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address_outsider
            and self.person_address_outsider.cep
        ):
            natural_person_history = self.person_address_outsider
        return super().exterior_cod_postal(natural_person_history)

    def trab_imig_tmp_resid(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history:
            natural_person_history = self.natural_person_history
        return super().trab_imig_tmp_resid(natural_person_history)

    def trab_imig_cond_ing(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history:
            natural_person_history = self.natural_person_history
        return super().trab_imig_cond_ing(natural_person_history)

    def contato_fone_princ(self, instance_outside=None):
        natural_person_history = None
        return super().contato_fone_princ(natural_person_history)

    def contato_email_princ(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history:
            natural_person_history = self.natural_person_history
        return super().contato_email_princ(natural_person_history)

    def brasil_dsc_lograd(self, instance_outside=None):
        natural_person_history = None
        if (
            self.natural_person_history
            and self.person_address
            and self.person_address.logradouro
        ):
            natural_person_history = self.person_address
        return super().brasil_dsc_lograd(natural_person_history)

    def trabalhador_cpf_trab(self, instance_outside=None):
        natural_person_history = None
        if self.natural_person_history:
            natural_person_history = self.natural_person_history
        return super().trabalhador_cpf_trab(natural_person_history)


class S2205Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2205
    EXTRACTOR = S2205Extractor

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
        qs2300 = (
            oid
            for oid in S2300.objects.valids_by_status().values_list("oid", flat=True)
        )
        query = Servidor.objects.by_type_possession(
            (
                "EFE",
                "ECM",
                "EFC",
                "MBR",
                "MEL",
                "MCM",
                "MEC",
                "CMS",
                "REQ",
                "REX",
                "RCM",
                "EST",
                "RFC",
            )
        ).filter(Q(matricula__in=qs2200) | Q(matricula__in=qs2300))
        return query

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        event_registration = (
            Event.objects.filter(
                acronym__in=("s2200", "s2300", "s2298"),
                oid=S2205Factory._get_oid(instance_outside),
            )
            .validity_in(start_limit)
            .last()
        )
        if not event_registration:
            message = f"Não possui Evento de cadastro(S2200, S2300, S2298) para {instance_outside}."
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
