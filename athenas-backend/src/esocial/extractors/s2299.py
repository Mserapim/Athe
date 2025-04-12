# -.- coding: utf-8 -.-
from datetime import datetime
from logging import getLogger

from django.db.models import F, Q

from esocial.const import NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.models import S2299, ItemTable
from rh.models import MovimentacaoDesligamento

log = getLogger(__name__)


class S2299Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2299Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self.check_reference_strong():
            start_validity = self._instance_outside.data_desligamento
            references = self._references()

        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside] if self._instance_outside else None

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return (
            self._instance_outside
            and self._instance_outside.data_desligamento is not None
        )

    def validate_validity_fields(self):
        pass

    @classmethod
    def _previous_event_not_send(cls, event):
        """Este método retorna o último evento anterior ao extraído, de mesmo oid e acronym, não enviado."""
        return (
            cls._get_extract_model()
            .objects.valids_not_sent()
            .filter(
                oid=event.oid,
                acronym=event.acronym,
                start_validity__lt=event.start_validity,
                registry_employee=event.registry_employee,
            )
            .exclude(pk=event.pk)
            .order_by("-start_validity")[0:1]
        )

    def pre_validate(self):
        if (
            self._instance_outside
            and self._instance_outside.servidor.afastamento_ativo(
                data=self._start_validity
            )
        ):
            return NOTHING_TODO
        return super().pre_validate()

    def oid(self):
        if self._instance_outside:
            return self._get_oid(self._instance_outside)
        return self._event.oid

    def description(self):
        return f"{self._instance_outside.servidor.type_by_possession} {self._instance_outside.servidor} - {self._instance_outside}"

    def ide_evento_ind_guia(self):
        return None

    def sucessao_vinc_tp_insc(self):
        return None

    def sucessao_vinc_nr_insc(self):
        return None

    def ide_vinculo_cpf_trab(self):
        return (
            self._instance_outside.servidor.pessoa_fisica.cpf
            if self._instance_outside
            else None
        )

    def ide_vinculo_matricula(self):
        return (
            str(self._instance_outside.servidor.matricula)
            if self._instance_outside
            else None
        )

    def info_deslig_mtv_deslig(self):
        mtv_deslig = None
        if self._instance_outside:
            try:
                mtv_deslig = (
                    ItemTable.objects.validity_in(
                        self._start_validity, self._start_validity
                    )
                    .by_choice_table(self._instance_outside.tipo_desligamento, "19")
                    .code
                )
                if mtv_deslig not in ["11", "12", "13", "25", "28", "29", "30"]:
                    self.set_dependency(
                        oid=self.configuration.employer.pk, acronyms=("s1005",)
                    )
                    self.set_dependency(
                        oid=self.configuration.employer.pk, acronyms=("s1020",)
                    )
            except Exception as err:
                print(err)
                print(self._start_validity)
                print(self._instance_outside)
                print(
                    self._instance_outside.tipo_desligamento,
                    self._instance_outside.get_tipo_desligamento_display(),
                )
                print("=====================================================")
        return mtv_deslig

    def info_deslig_dt_deslig(self):
        return (
            self._instance_outside.data_desligamento if self._instance_outside else None
        )

    def info_deslig_dt_av_prv(self):
        return None

    def info_deslig_ind_pagto_api(self):
        return "N"

    def info_deslig_dt_proj_fim_api(self):
        return None

    def info_deslig_pens_alim(self):
        return None

    def info_deslig_perc_aliment(self):
        return None

    def info_deslig_vr_alim(self):
        return None

    def info_deslig_nr_proc_trab(self):
        return None

    def info_deslig_ind_pdv(self):
        mtv_deslig = (
            ItemTable.objects.validity_in(self._start_validity, self._start_validity)
            .by_choice_table(self._instance_outside.tipo_desligamento, "19")
            .code
        )
        if mtv_deslig not in [
            "10",
            "11",
            "12",
            "13",
            "28",
            "29",
            "30",
            "34",
            "36",
            "37",
            "40",
            "43",
            "44",
        ]:
            return "S"
        return None

    def info_interm_dia(self):
        return None

    def observacoes_observacao(self):
        return (
            self._instance_outside.texto[:255]
            if self._instance_outside and self._instance_outside.texto
            else None
        )

    def transf_tit_cpf_substituto(self):
        return None

    def transf_tit_dt_nascto(self):
        return None

    def mudanca_cpf_novo_cpf(self):
        return None

    def dm_dev(self):
        return None

    def proc_jud_trab(self):
        return []

    def info_mv_ind_mv(self):
        return None

    def remun_outr_empr_tp_insc(self):
        return None

    def remun_outr_empr_nr_insc(self):
        return None

    def remun_outr_empr_cod_categ(self):
        return None

    def remun_outr_empr_vlr_remun_oe(self):
        return None

    def proc_cs_nr_proc_jud(self):
        return None

    def quarentena_dt_fim_quar(self):
        return None

    def consig_fgts_ins_consig(self):
        return None

    def consig_fgts_nr_contr(self):
        return None


class S2299Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2299
    EXTRACTOR = S2299Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        today = datetime.now().date()
        query = MovimentacaoDesligamento.objects.filter(
            (
                Q(servidor__type_by_possession__in=("EFE", "ECM", "EFC"))
                & Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo="EF")
            )
            | (
                Q(
                    servidor__type_by_possession__in=(
                        "MBR",
                        "MEL",
                        "MCM",
                        "MEC",
                        "MBR2",
                        "MEL2",
                        "MCM2",
                        "MEC2",
                    )
                )
                & Q(servidor__termination_date__isnull=False)
                & Q(servidor__termination_date__lte=today)
                & Q(servidor__termination_date=F("data_desligamento"))
                & Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo="EF")
            )
            | (
                Q(servidor__type_by_possession="CMS")
                & Q(servidor__termination_date__isnull=False)
                & Q(servidor__termination_date__lte=today)
                & Q(servidor__termination_date=F("data_desligamento"))
                & Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo="CM")
            )
        ).exclude(data_desligamento__lt=cls.initial_group_date())
        return query

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        return None

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_desligamento

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return start_limit

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
                    ide_vinculo_matricula=instance_outside.servidor.matricula,
                )
                .filter(oid=instance_outside.pk)
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
        query_s2299 = S2299.objects.valids_by_status()
        fires = MovimentacaoDesligamento.objects.filter()
        if registry:
            query_s2299 = query_s2299.filter(registry_employee=registry)
            fires = fires.filter(servidor__matricula=registry)
        oids = (pk for pk in fires.values_list("pk", flat=True))

        for event in query_s2299.exclude(oid__in=oids):
            """Caso evento não exista nos limites informados, verifica se existe em seus próprios limites."""
            params = {
                "event": event,
                "start_validity": event.start_validity,
                "end_validity": event.end_validity,
                "task": task,
            }
            extractor_event = self.extractor(None, **params)
            if not extractor_event.check_reference_strong():
                """Caso também não exista nos seus limites, será candidato a exclusão."""
                self.extractors_event_exclude.update({event.pk: extractor_event})
