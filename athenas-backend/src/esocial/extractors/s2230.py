# -*- coding: utf-8 -*-
import copy

from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import (
    NOTHING_TODO,
    TYPE_DEPARTURE_COMPETITION,
    TYPE_DEPARTURE_COURSE_CONTEST,
    TYPE_DEPARTURE_MANDATE_ELECTIVE,
    TYPE_DEPARTURE_SUSPENSION,
    TYPE_HEALTH3DAYS,
    TYPE_HEALTH30DAYS,
    TYPE_HEALTH_MEDICAL_BOARD,
    TYPE_LICENSE_MANDATE_CLASSIST,
    TYPE_MATERNITY_LICENSE,
    TYPE_VACATION,
)
from esocial.extractors.base import Extractor, Factory
from esocial.extractors.healthcertificate import HealthCertificateExtractor
from esocial.extractors.s1200 import S1200Extractor
from esocial.extractors.s2300 import VALID_LINKS_EST
from esocial.models import S2200, S2230, S2300, Event, ItemTable, get_current_config
from rh.afastamento.models import BaseLicencaAfastamento, HealthCertificate
from rh.const import (
    ACTIVE,
    CANCELED,
    FINISHED,
    HEALTH_LICENSE_CLS_ANTICIPATION,
    HEALTH_LICENSE_CLS_EXTENSION,
)
from rh.ferias.models import PeriodoAquisitivoServidorUsufruto
from rh.models import Servidor
from datetime import datetime, timedelta

from standard.models import Item

log = getLogger(__name__)

QTD_DEFAULT_DAYS = 30


class S2230Extractor(Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2230Extractor, self).__init__(instance_outside, *args, **kwargs)

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
        if self._instance_outside and (
            not self._instance_outside.estado == CANCELED or not start_validity
        ):
            return [self._instance_outside]
        return []

    def _references_strong_end_date(self, start_validity=None):
        return self._instance_outside.data_fim if self._instance_outside else None

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
            [instance_outside.data_inicio]
            if instance_outside and not instance_outside.estado == CANCELED
            else []
        )
        return list_start_date

    def pre_validate(self):
        if self._instance_outside:
            termination_date = self._instance_outside.servidor.termination_date
            if (
                termination_date
                and self._instance_outside.data_inicio > termination_date
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
        descr = f"{self._instance_outside.servidor.type_by_possession} {self._instance_outside.servidor}"
        descr += f" - {self._instance_outside.situation_unicode}: {self._instance_outside.get_estado_display()}"
        return descr

    def ide_vinculo_cpf_trab(self):
        return self._instance_outside.servidor.pessoa_fisica.cpf

    def ide_vinculo_matricula(self):
        return str(self._instance_outside.servidor.matricula)

    def ide_vinculo_cod_categ(self):
        return None

    def ini_afastamento_dt_ini_afast(self):
        if self._instance_outside.data_inicio >= self.initial_group_date():
            return self._instance_outside.data_inicio
        return None

    def ini_afastamento_cod_mot_afast(self):
        if self.ini_afastamento_dt_ini_afast():
            return ini_afastamento_cod_mot_afast(self._instance_outside)
        return None

    def ini_afastamento_info_mesmo_mtv(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            if ini_afastamento_cod_mot_afast(self._instance_outside) in ["01", "03"]:
                value = (
                    "S"
                    if self._instance_outside.instancia_modelo.consequence_of
                    is not None
                    else "N"
                )
        return value

    def ini_afastamento_tp_acid_transito(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            if (
                ini_afastamento_cod_mot_afast(self._instance_outside) in ("01", "03")
                and self._instance_outside.instancia_modelo.acidente_transito
                is not None
            ):
                value = self._instance_outside.instancia_modelo.acidente_transito
        return value

    def ini_afastamento_observacao(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            if ini_afastamento_cod_mot_afast(self._instance_outside) == "21":
                return self._instance_outside.instancia_modelo.__str_restful__()[0:254]
        return value

    def per_aquis_dt_inicio(self):
        """O (se codMotAfast = [15] E (o código de categoria no RET for igual a [1XX, 301, 302, 303, 304, 306, 307, 309, 310, 312, 410] com
        {tpRegTrab} em S-2200/S-2300 = [1]
        OU o código de categoria no RET for igual a [401] com tpRegTrab em S-2300 = [1] ou não informado) E dtIniAfast >= [2021-07-19]);
        N (nos demais casos)"""
        if self.ini_afastamento_dt_ini_afast():
            if check_per_aquis(self._instance_outside):
                pasu = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    data_inicio=self._instance_outside.data_inicio,
                    data_fim_cache=self._instance_outside.data_fim,
                ).last()
                return pasu.data_inicio if pasu else None
        return None

    def per_aquis_dt_fim(self):
        """O (se codMotAfast = [15] E (o código de categoria no RET for igual a [1XX, 301, 302, 303, 304, 306, 307, 309, 310, 312, 410] com
        {tpRegTrab} em S-2200/S-2300 = [1]
        OU o código de categoria no RET for igual a [401] com tpRegTrab em S-2300 = [1] ou não informado) E dtIniAfast >= [2021-07-19]);
        N (nos demais casos)"""
        if self.ini_afastamento_dt_ini_afast():
            if check_per_aquis(self._instance_outside):
                pasu = PeriodoAquisitivoServidorUsufruto.objects.filter(
                    data_inicio=self._instance_outside.data_inicio,
                    data_fim_cache=self._instance_outside.data_fim,
                ).last()
                return pasu.data_fim_cache if pasu else None
        return None

    def info_atestado(self):
        if self.ini_afastamento_dt_ini_afast():
            return info_atestado(self._instance_outside)
        return None

    def info_cessao_cnpj_cess(self):
        return None

    def info_cessao_inf_onus(self):
        return None

    def info_mand_sind_cnpj_sind(self):
        value = None
        instance = self._instance_outside.instancia_modelo
        if self.ini_afastamento_dt_ini_afast():
            if (
                instance.tipo == TYPE_LICENSE_MANDATE_CLASSIST
                and instance.entidade
                and instance.entidade.pessoa_juridica
            ):
                value = instance.entidade.pessoa_juridica.cnpj
        return value

    def info_mand_sind_inf_onus_remun(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            if self._instance_outside.tipo == TYPE_LICENSE_MANDATE_CLASSIST:
                value = self._instance_outside.instancia_modelo.onus_payment
        return value

    def info_mand_elet_cnpj_mand_elet(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            instance = self._instance_outside.instancia_modelo
            if (
                instance.tipo == TYPE_DEPARTURE_MANDATE_ELECTIVE
                and instance.organ_location
                and instance.organ_location.pessoa_juridica
            ):
                value = instance.organ_location.pessoa_juridica.cnpj
        return value

    def info_mand_elet_ind_remun_cargo(self):
        value = None
        if self.ini_afastamento_dt_ini_afast():
            if self._instance_outside.tipo == TYPE_DEPARTURE_MANDATE_ELECTIVE:
                value = (
                    "S" if self._instance_outside.instancia_modelo.remunerado else "N"
                )
        return value

    def info_retif_orig_retif(self):
        return None

    def info_retif_tp_proc(self):
        return None

    def info_retif_nr_proc(self):
        return None

    def fim_afastamento_dt_term_afast(self):
        return self._instance_outside.data_fim


def ini_afastamento_cod_mot_afast(instance_outside):
    cod = None
    if instance_outside:
        instance = instance_outside.instancia_modelo
        cod = ItemTable.objects.all_choice_table(instance.tipo, "18").last().code
        if (
            instance.tipo
            in (
                TYPE_DEPARTURE_COURSE_CONTEST,
                TYPE_DEPARTURE_COMPETITION,
                TYPE_DEPARTURE_SUSPENSION,
            )
            and instance.remunerado
        ):
            cod = "10"
        elif (
            instance.tipo in (TYPE_DEPARTURE_COURSE_CONTEST, TYPE_DEPARTURE_SUSPENSION)
            and not instance.remunerado
        ):
            cod = "05"
        elif instance.tipo == TYPE_MATERNITY_LICENSE:
            cod = "17"
            if instance.natimorto:
                cod = "19"
            elif instance.classification in (
                HEALTH_LICENSE_CLS_ANTICIPATION,
                HEALTH_LICENSE_CLS_EXTENSION,
            ):
                cod = "35"
        elif (
            instance.tipo
            in (TYPE_HEALTH3DAYS, TYPE_HEALTH_MEDICAL_BOARD, TYPE_HEALTH30DAYS)
            and employee_reg_prev(instance_outside.servidor) == 1
        ):
            """5.1. O código 03 - Acidente/Doença não relacionada ao trabalho da Tabela 18 do eSocial deve ser
            utilizado para informar a ocorrência de afastamentos temporários motivados por acidentes de
            qualquer natureza e doenças não relacionadas ao trabalho, cuja informação só é obrigatória em
            relação a trabalhadores das categorias [1XX], [2XX] igual a [3XX] e {tpRegPrev} for igual a [1] e quando:
                a) sua duração for superior a 15 (quinze) dias;"""
            cod = "03"
            if instance.related_work:
                cod = "01"
    return cod


def employee_reg_prev(employee):
    reg_prev = None
    s2200 = S2200.objects.valids_by_status().filter(
        vinculo_matricula=employee.matricula
    )
    if s2200.exists():
        reg_prev = s2200.last().vinculo_tp_reg_prev
    if not reg_prev:
        s2300 = S2300.objects.valids_by_status().filter(
            info_tsv_inicio_matricula=employee.matricula
        )
        if s2300.exists():
            reg_prev = s2300.last().info_trab_cedido_tp_reg_prev
    return reg_prev


def info_atestado(instance_outside):
    certificates = []
    for obj in HealthCertificate.objects.filter(health_license=instance_outside.pk):
        new_obj = HealthCertificateExtractor(obj)
        new_obj.run()
        certificates.append(new_obj._extracted_fields_json)
    return certificates


def check_per_aquis(instance_outside):
    """O (se codMotAfast = [15] E (o código de categoria no RET for igual a [1XX, 301, 302, 303, 304, 306, 307, 309, 310, 312, 410] com
        {tpRegTrab} em S-2200/S-2300 = [1]
        OU
        o código de categoria no RET for igual a [401] com tpRegTrab em S-2300 = [1] ou não informado) E dtIniAfast >= [2021-07-19]);
    N (nos demais casos)"""
    if ini_afastamento_cod_mot_afast(instance_outside) == "15":
        items = [
            int(code)
            for code in ItemTable.objects.filter(esocial_table="1").values_list(
                "code", flat=True
            )
        ]
        ev2200 = (
            S2200.objects.valids_by_status()
            .filter(oid=instance_outside.servidor.pk)
            .last()
        )
        reg_trab = None
        if ev2200:
            reg_trab = ev2200.vinculo_tp_reg_trab
        else:
            ev2300 = (
                S2300.objects.valids_by_status()
                .filter(oid=instance_outside.servidor.pk)
                .last()
            )
            if ev2300:
                reg_trab = (
                    ev2300.info_dirigente_sindical_tp_reg_trab
                    or ev2300.info_trab_cedido_tp_reg_trab
                    or ev2300.info_mand_elet_tp_reg_trab
                )
        cod_categ = None
        s2200_06 = (
            Event.objects.valids_by_status()
            .filter(oid=instance_outside.servidor.pk, acronym__in=["s2200", "s2206"])
            .order_by("start_validity")
            .last()
        )
        if s2200_06:
            cod_categ = s2200_06.event.info_contrato_cod_categ

        if cod_categ in items and reg_trab == 1:
            return True
    return False


class S2230Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2230
    EXTRACTOR = S2230Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        initial_group_date = cls.initial_group_date()
        config_qtd_dias = Item.objects.filter(key="qtd_dias_evento_afastamento").first()
        qtd_dias = int(config_qtd_dias.value) if config_qtd_dias else QTD_DEFAULT_DAYS

        date_reference_absence = (datetime.now() - timedelta(days=qtd_dias)).date()

        # date_cut_est = S1200Extractor.initial_group_date()
        # date_cut_est = NewDateRange.from_month(date_cut_est.year, date_cut_est.month).first

        # employess_fired = Servidor.objects.filter(
        #     Q(termination_date__lt=initial_group_date) |
        #     Q(type_by_possession__in=VALID_LINKS_EST, termination_date__isnull=False, termination_date__lt=date_cut_est))

        employess_fired = Servidor.objects.filter(
            Q(termination_date__lt=initial_group_date)
        )

        query = BaseLicencaAfastamento.objects.esocial(
            range=NewDateRange(date_reference_absence)
        )

        config = get_current_config()
        query = query.exclude(
            servidor__matricula__in=(
                registry
                for registry in config.employee_exclude.values_list(
                    "matricula", flat=True
                )
            )
        )
        if config.employee_filter.exists():
            query = query.filter(
                servidor__matricula__in=(
                    registry
                    for registry in config.employee_filter.values_list(
                        "matricula", flat=True
                    )
                )
            )

        query = (
            query.filter(
                servidor__type_by_possession__in=[
                    "EFE",
                    "ECM",
                    "EFC",
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "CMS",
                    "REQ",
                    "RCM",
                    "RFC",
                    "CTR",
                    "EST",
                ],
            )
            .filter(estado__in=[ACTIVE, FINISHED])
            .not_canceled()
            .exclude(data_fim__lt=initial_group_date)
        )

        query = query.exclude(
            servidor__pk__in=(pk for pk in employess_fired.values_list("pk", flat=True))
        )

        query = query.exclude(
            Q(
                servidor__type_by_possession__in=[
                    "EFE",
                    "ECM",
                    "EFC",
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "CMS",
                    "REQ",
                    "RCM",
                    "RFC",
                    "CTR",
                ]
            )
            & Q(tipo=TYPE_VACATION)
        )

        return query.order_by("data_inicio")

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_inicio

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
                    ide_vinculo_matricula=instance_outside.servidor.matricula,
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
                extractor_event = self.extractor(to_exc.departure, **params)
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
        departures = (
            BaseLicencaAfastamento.objects.esocial()
            .filter(servidor__matricula=registry)
            .exclude(estado=CANCELED)
        )
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
