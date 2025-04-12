# -.- coding: utf-8 -.-
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.extractors.base import ConfigReference, Extractor, Factory
from esocial.models import S1070, InfoSuspensao
from rh.models import LegalProcess, ProcessSuspension

from .utils import format_reference

log = getLogger(__name__)


class S1070Extractor(Extractor):

    VALIDITY_FIELDS = [
        "ide_processo_ini_valid",
        "ide_processo_fim_valid",
        "nova_validade_ini_valid",
        "nova_validade_fim_valid",
    ]

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            """quando temos evento, utilizamos start_validity e checamos se ainda está no _queryset_date"""
            _queryset_date = self._queryset_date(
                self._instance_outside.number_process
                if self._instance_outside
                else self._event.oid
            )
            start_validity = self._event.start_validity
            if start_validity not in _queryset_date:
                """volta a ser o start_validity enviado ao extrator quando o start_validity do evento não está está no _queryset_date"""
                start_validity = (
                    None if not self._start_validity_init else self._start_validity
                )
        else:
            start_validity = self._start_validity

        if start_validity:
            references = self._references()
            references_next = self._references_next(start_validity=start_validity)
            if references_next:
                end_validity = min(references_next)
                end_validity -= relativedelta(days=1)
                end_validity = NewDateRange.from_month(
                    end_validity.year, end_validity.month
                ).last
        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong(start_validity=start_validity)

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside] if self._instance_outside else []

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return self._start_validity and self._query_suspension().exists()

    def _references_next(self, start_validity=None):
        """Este método encontra as datas da próxima referência. Utiliza self._start_validity quando start_validity é None.

        Args:
            start_validity (datetime.date): default None

        Returns:
            list_start_date (set): set de datas maiores que start_validity
        """
        start_validity = self._start_validity if not start_validity else start_validity
        list_start_date = self._queryset_date(
            self._instance_outside.number_process
            if self._instance_outside
            else self._event.oid
        )
        list_start_date = set(filter(lambda dt: dt > start_validity, list_start_date))
        return list_start_date

    @classmethod
    def _queryset_date(cls, number_process):
        list_start_date = []
        if number_process:
            list_start_date += cls.cr_suspensions(number_process)._queryset_date(
                go_limits=True
            )
            initial_group_date = cls.initial_group_date()
            list_start_date = set(
                [max(dt, initial_group_date) for dt in list_start_date]
            )
        return list_start_date

    @classmethod
    def cr_suspensions(cls, number_process):

        return ConfigReference(
            queryset=ProcessSuspension.objects.filter(
                process__number_process=number_process
            ),
            start_validity_field="start_validity",
            end_validity_field="end_validity",
        )

    def _query_suspension(self):
        """Este método encontra o objeto de referência vigente a partir de self._start_validity."""
        if self._instance_outside and self._start_validity:
            query = ProcessSuspension.objects.filter(
                process=self._instance_outside
            ).currents_in(
                drange=NewDateRange(
                    self._start_validity,
                    (
                        self._start_validity
                        if not self._end_validity
                        else self._end_validity
                    ),
                )
            )
        else:
            query = ProcessSuspension.objects.none()
        return query

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        if isinstance(instance_outside, dict):
            return instance_outside.get("number_process")
        return instance_outside.number_process if instance_outside else None

    def ide_processo_tp_proc(self):
        return self._instance_outside.type_process

    def ide_processo_nr_proc(self):
        return self._instance_outside.number_process

    def ide_processo_ini_valid(self):
        if self._event:
            return format_reference(self._event.start_validity)
        return super(S1070Extractor, self).ini_valid()

    def ide_processo_fim_valid(self):
        if self._event:
            return format_reference(self._event.end_validity)
        return super(S1070Extractor, self).fim_valid()

    def dados_proc_ind_autoria(self):
        return self._instance_outside.cod_authorship

    def dados_proc_ind_mat_proc(self):
        return self._instance_outside.matter_process

    def dados_proc_observacao(self):
        return self._instance_outside.note or None

    def dados_proc_jud_uf_vara(self):
        return (
            self._instance_outside.judicial_process_locality.estado.sigla
            if self._instance_outside.judicial_process_locality
            else None
        )

    def dados_proc_jud_cod_munic(self):
        return (
            self._instance_outside.judicial_process_locality.ibge
            if self._instance_outside.judicial_process_locality
            else None
        )

    def dados_proc_jud_id_vara(self):
        return self._instance_outside.judicial_process_id_local or None

    def info_susp(self):
        suspensions = []
        query_suspensions = self._query_suspension()
        for suspension in query_suspensions:
            suspensions.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "_class_": InfoSuspensao,
                    "competence_month": self.competence_month(),
                    "competence_year": self.competence_year(),
                    "oid": str(suspension.pk),
                    "info_susp_cod_susp": suspension.pk,
                    "info_susp_ind_susp": "{:02d}".format(
                        suspension.indicative_suspension
                    ),
                    "info_susp_dt_decisao": suspension.start_validity,
                    "info_susp_ind_deposito": (
                        "S" if suspension.integral_deposit else "N"
                    ),
                }
            )
        return suspensions

    def nova_validade_ini_valid(self):
        return super(S1070Extractor, self).ini_valid()

    def nova_validade_fim_valid(self):
        return super(S1070Extractor, self).fim_valid()


class S1070Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1070
    EXTRACTOR = S1070Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return LegalProcess.objects.exclude(suspensions__isnull=True)

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid. Utiliza start_limit para retornar eventos da data informada.
        """
        return self.extracted_class.objects.valids_by_status().filter(
            oid=oid, start_validity=start_limit
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
                    Q(start_validity__gt=extracted_event.start_validity)
                )
                .filter(oid=self.EXTRACTOR._get_oid(instance_outside))
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
        oids = []
        query = S1070.objects.valids_by_status()

        if filter_query_instance:
            filter_query_instance = Q(
                oid=filter_query_instance.deconstruct()[2].get("number_process")
            )
            query = query.filter(filter_query_instance)

        for event in query.exclude(oid__in=oids):
            """Caso evento não exista nos limites informados, verifica se existe em seus próprios limites."""
            params = {
                "event": event,
                "start_validity": None,
                "end_validity": None,
                "task": task,
            }
            extractor_event = self.extractor(event.legal_process, **params)
            if not extractor_event.check_reference_strong():
                """Caso também não exista nos seus limites, será candidato a exclusão."""
                self.extractors_event_exclude.update({event.pk: extractor_event})

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        list_start_date = self.EXTRACTOR._queryset_date(instance_outside.number_process)
        list_start_date = min(filter(lambda x: x > date, list_start_date), default=None)
        return list_start_date

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        end_validity = self._next_day(instance_outside, date=start_limit)
        if end_validity:
            end_validity -= relativedelta(days=1)
            end_validity = NewDateRange.from_month(
                end_validity.year, end_validity.month
            ).last
        return end_validity
