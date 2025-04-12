# -.- coding: utf-8 -.-
from contrib.utils import getLogger
from esocial.const import NOTHING_TODO
from esocial.extractors.base import Extractor, Factory
from esocial.models import S2298, Event
from rh.models import MovimentacaoPosse

log = getLogger(__name__)


class S2298Extractor(Extractor):

    def __init__(self, *args, **kwargs):
        super(S2298Extractor, self).__init__(*args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self.check_reference_strong():
            start_validity = self._instance_outside.data_exercicio
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
            self._instance_outside and self._instance_outside.data_exercicio is not None
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
        if self._instance_outside.servidor.posses.filter(
            quadro__cargo__tipo_lei_cargo="EF",
            data_desligamento__isnull=False,
            data_desligamento__lte=self.initial_group_date(),
        ).exists():
            return NOTHING_TODO
        return super().pre_validate()

    def start_validity(self):
        return self._start_validity

    def end_validity(self):
        return self._end_validity

    def ide_vinculo_cpf_trab(self):
        return self._instance_outside.servidor.pessoa_fisica.cpf[:11]

    def ide_vinculo_matricula(self):
        return str(self._instance_outside.servidor.matricula)

    def info_reintegr_tp_reint(self):

        _tp_reint = None
        if self._instance_outside.judicial_decision:
            _tp_reint = 1
        elif self._instance_outside.legal_amnesty_process:
            _tp_reint = 2
        elif self._instance_outside.tipo_movcarreira == "REVERSAO":
            _tp_reint = 3
        elif self._instance_outside.tipo_movcarreira == "RECONDUCAO":
            _tp_reint = 4
        else:
            _tp_reint = 9

        return _tp_reint

    def info_reintegr_nr_proc_jud(self):
        _number_process = None
        if self._instance_outside.judicial_decision:
            _number_process = self._instance_outside.number_process
        return _number_process

    def info_reintegr_nr_lei_anistia(self):
        return (
            self._instance_outside.legal_amnesty_process
            if self._instance_outside.legal_amnesty_process
            else None
        )

    def info_reintegr_dt_efet_retorno(self):
        return self._instance_outside.data_exercicio

    def info_reintegr_dt_efeito(self):
        return self._instance_outside.financial_effect_date


class S2298Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2298
    EXTRACTOR = S2298Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return MovimentacaoPosse.objects.filter(
            tipo_movcarreira__in=[
                "RECONDUCAO",
                "REVERSAO",
                "REINTEGRACAO",
                "APROVEITAMENTO",
            ]
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

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        return None

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_exercicio

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
        possessions = self._query_instances_outside().filter(
            servidor__matricula=registry
        )
        oids = (pk for pk in possessions.values_list("pk", flat=True))

        query = S2298.objects.valids_by_status().filter(registry_employee=registry)

        for event in query.exclude(oid__in=oids):
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
