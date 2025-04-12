# -.- coding: utf-8 -.-
import copy
import datetime
import importlib
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db.models.expressions import F
from django.db.utils import DataError, IntegrityError

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from engine.mq.models import Task
from esocial.const import (
    ANYTIME,
    DIFF_VALIDITY_DIFF_CONTENT,
    DIFF_VALIDITY_END,
    DIFF_VALIDITY_END_SAME_CONTENT,
    DIFF_VALIDITY_SAME_CONTENT,
    DOESNT_EXIST_REFERENCE,
    EMPLOYER_APP,
    EQUAL_VALIDITY,
    EQUAL_VALIDITY_DIFF_CONTENT,
    EXCLUDE_EVENT,
    EXCLUSION,
    EXCLUSION_TYPE_DEFAULT,
    EXCLUSION_TYPE_S3000,
    FILE_ORIGIN_ORIGINAL,
    FILE_ORIGIN_RECTIFIED,
    INCLUSION,
    MANDATORY_IF_EXIST,
    MAP_VALIDATE_RESULT,
    MAP_VALIDITY_RESULT,
    MODIFICATION,
    NO_RESTRICTION,
    NOTHING_TODO,
    PROCESS_STATUS_EVENT_NOT_SENT,
    PROCESS_STATUS_EVENT_VALIDS_SENT,
    RECTIFICATION,
    SAME_EVENT,
)
from esocial.managers.file_support import get_register_model
from esocial.models import S3000, Configuration, Event, Reference
from esocial.utils import convert_diff_content, esocial_environment

from .utils import (
    all_fields_many_to_many_rel,
    extract_dates,
    format_reference,
    limits_from_date,
    validity_between_events,
)

log = getLogger(__name__)


"""
    "O" = obrigatoriedade de prestação de informações naquele grupo;
    "N" = não pode ser informado;
    “F” = facultativo;
    "OC" = obrigatório se existir informação.
"""


def persist_dict_to_event(
    _dict,
    update_event_pk=None,
    fields_with_not_persist=[],
    instance_outside=None,
    task=None,
):
    """Este método cria ou atualiza um evento. Utiliza @update_event_pk para atualizar o evento.
    Adiciona os relacionamentos m2m utilizando .persist_dict_to_event para criar os eventos relacionais.

    Params:
        _dict(dict):
        update_event_pk(int):
        fields_with_not_persist(list): list de campos que não devem ser persistidos
        instance_outside:
        taks(Task):

    Returns:
        _extracted_event.event(Event): instância do Event que foi criado/atualizado.
    """
    cls_extracted_event = _dict.pop("_class_", None)
    mm_fields = {}
    if not cls_extracted_event:
        raise Exception("Class not defined in extraction!")
    """descobre os m2m"""
    mm_field_names = []
    for k in _dict:
        if isinstance(_dict[k], list):
            mm_field_names.append(k)

    """remove os m2m de _dict(quer será persistido), adiciona a mm_fields para preencher novamente"""
    for k in mm_field_names:
        mm_fields[k] = _dict.pop(k)

    """prepara _dict removendo os campos presentes em fields_with_not_persist, geralmente campos que não estão em event"""
    for k in fields_with_not_persist:
        _dict.get(k, None) and _dict.pop(k)

    """get_or_create ou update_or_create"""
    try:
        if not update_event_pk:
            _extracted_event, created = cls_extracted_event.objects.get_or_create(
                **_dict
            )
        else:
            _extracted_event, created = cls_extracted_event.objects.update_or_create(
                pk=update_event_pk, id=update_event_pk, defaults=_dict
            )
            """delete m2m quando for update"""
            _delete_many_to_many_instance(_extracted_event, mm_fields=mm_fields)
    except DataError as err:
        log.exception(err)
        log.info(f"cls_extracted_event {cls_extracted_event}")
        log.info(_dict)
        raise err
    except IntegrityError as err:
        log.exception(err)
        log.info(f"cls_extracted_event {cls_extracted_event}")
        if f"{err}".find("null value in column") == 0:
            err = f"{err}".split('"')
            message = ""
            for fld in err:
                try:
                    message += f'O campo "{cls_extracted_event._meta.get_field(fld).verbose_name}" não foi preenchido.'
                except:
                    pass
            if message:
                raise Exception(message)
        log.info(_dict)
        raise err
    except Exception as err:
        log.exception(err)
        log.info(f"cls_extracted_event {cls_extracted_event}")
        log.info(_dict)
        raise err

    """cria objetos da relação m2m e depois os adiciona ao _extracted_event"""
    for mm_field in mm_fields:
        for _dict_mm in mm_fields[mm_field]:
            try:
                _field = getattr(_extracted_event, mm_field)
                _dict_mm.update({"father_event": _extracted_event})
                _field.add(
                    persist_dict_to_event(
                        _dict_mm,
                        update_event_pk=None,
                        fields_with_not_persist=fields_with_not_persist,
                        task=task,
                    )
                )
            except Exception as err:
                log.exception(err)
                task_info(
                    task,
                    msg=f"Erro gerando {_extracted_event.event.acronym} de {instance_outside}<br />{err}",
                    type_of=3,
                )
    return _extracted_event.event


def _delete_many_to_many_instance(_extracted_event, mm_fields={}):
    for mm_field in mm_fields:
        for _dict_mm in mm_fields[mm_field]:
            _field = getattr(_extracted_event, mm_field)
            for _obj in _field.filter():
                _obj.delete()


class Factory(object):

    EXTRACTED_MODEL_CLASS = None
    EXTRACTOR = None

    @staticmethod
    def get_factory(acronym=None):
        _module = importlib.import_module("esocial.extractors.%s" % (acronym.lower()))
        return getattr(_module, f"{acronym.upper()}Factory")()

    @property
    def extractor(self):
        return self.EXTRACTOR

    @property
    def extracted_class(self):
        return self.EXTRACTED_MODEL_CLASS

    @property
    def acronym(self):
        return self.EXTRACTED_MODEL_CLASS.__name__.lower()

    @classmethod
    def initial_group_date(cls):
        return cls.EXTRACTOR.initial_group_date()

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return Event.objects.none()

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        return cls.EXTRACTOR._get_oid(instance_outside, **kwargs)

    @classmethod
    def _get_control_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        return cls.EXTRACTOR._get_control_oid(instance_outside, **kwargs)

    def _filter_by_factory(self, query, registry_employee=None, registry_person=None):
        """Este método deve ser utilizado para filter em query.

        Args:
            registry_employee (int): a matrícula do servidor
            registry_person (str): o cpf da pessoa física

        Returns:
            query (queryset):"""
        return query

    @classmethod
    def organizer(cls):
        """Este método retorna uma lista/iterador de objetos utilizados para desambiguar eventos numa mesma validade.
        Ex: S1010 pode ter vários eventos para uma mesma rúbrica na mesma validade em tabelas diferentes.
        Este método deve ser sobrescrito em cada evento que possuir esta característica.
        De forma comum será retornado [1] apenas para gerar um único evento.

        Returns:
            list/iterador: lista/iterador de objetos, default [1]."""
        return [1]

    def manage_in_bulk(
        self,
        clear_env=False,
        task=None,
        filter_query_instance=None,
        start_competence=None,
        end_competence=None,
        write_feedback=False,
        registry=None,
        registry_person=None,
        period=None,
        dependency=False,
    ):
        """

        Args:
            clear_env (bool): indicação de limpeza de produção restrita default False.
            task (engine.mq.models.Task): default None.
            filter_query_instance (django.db.models.Q): default {} -- objeto que será propagado ao query_instances_outside
                quando manage_in_bulk for chamado para filtro.
            start_competence (date): início de competência. Quando None será o início da obrigatoriedade do grupo de evento.
            end_competence (date): fim de competência. Quando None será o mês atual.
            write_feedback (bool): default False.
            registry (int): matrícula do Servidor, default None.
            registry_person (str): cpf do Servidor, default None.
            period (int): pk de rh.gfp.models.Periodo, default None.
            dependency (bool): informar se está extraindo dependência, default False.
        """

        """Events será utilizado no S3000(exclusão)"""

        # log.info(f'====> {self.__class__.__name__}: {registry} | {registry_person}')
        query = self._query_instances_outside(period=period, dependency=dependency)

        query = self._filter_by_factory(
            query, registry_employee=registry, registry_person=registry_person
        )

        if filter_query_instance:
            query = query.filter(filter_query_instance)

        if not start_competence:
            cfg = Configuration.current_config()
            dr = NewDateRange.from_month(
                cfg.initial_date_start_tables.year, cfg.initial_date_start_tables.month
            )
            start_competence = dr.first
        if not end_competence:
            today = datetime.datetime.now().date()
            if clear_env:
                today = NewDateRange.from_month(
                    start_competence.year, start_competence.month
                ).last
            dr = NewDateRange.from_month(today.year, today.month)
            end_competence = dr.last

        """Marca eventos existentes que existem para análise de exclusão."""
        self.extractors_event_exclude = {}
        self._set_extractors_event_exclude(
            registry=registry,
            registry_person=registry_person,
            filter_query_instance=filter_query_instance,
            task=task,
        )

        start_limit = start_competence
        _month = period.mes if period else None
        _year = period.ano if period else None

        total = query.count() if write_feedback else 0

        for instance_outside in query:
            try:
                oid = self._get_oid(instance_outside, month=_month, year=_year)
                log.info(
                    f">>>>>>> {self.__class__.__name__}: ({oid}) {instance_outside}"
                )
                self.delete_not_send(
                    oid=oid, registry=registry, registry_person=registry_person
                )
                self.delete_xsd_schema_invalid(
                    oid, registry=registry, registry_person=registry_person
                )

                end_competence_cache = end_competence

                for obj_organizer in self.organizer():
                    """Roda análise de um tipo evento até o fim da competência informada."""

                    start_limit, financial_effect_date = extract_dates(
                        self._get_start_limit(
                            instance_outside,
                            start_limit=start_competence,
                            organizer=obj_organizer,
                        )
                    )

                    end_competence = end_competence_cache

                    while start_limit and start_limit < end_competence:
                        end_limit, _ = extract_dates(
                            self._get_end_limit(
                                instance_outside, start_limit, organizer=obj_organizer
                            )
                        )

                        extractor_event_to_update = self._find_event_for_competence(
                            instance_outside,
                            start_limit,
                            end_limit=end_limit,
                            task=task,
                            registry=registry,
                            registry_person=registry_person,
                            period=period,
                            financial_effect_date=financial_effect_date,
                            organizer=obj_organizer,
                        )

                        if extractor_event_to_update:
                            """Roda atualização do evento."""
                            extracted_event = extractor_event_to_update.run()
                        else:
                            """Roda criação do evento."""
                            params = {
                                "start_validity": start_limit,
                                "end_validity": end_limit,
                                "task": task,
                                "clear": clear_env,
                                "period": period,
                                "financial_effect_date": financial_effect_date,
                                "organizer": obj_organizer,
                            }
                            extractor_event = self.extractor(instance_outside, **params)
                            extracted_event = None
                            if extractor_event.start_validity():
                                extracted_event = extractor_event.run()
                        self._find_covered_event_to_exclude(
                            extracted_event,
                            instance_outside,
                            task=task,
                            registry=registry,
                            period=period,
                            organizer=obj_organizer,
                        )

                        """Define start_limit em função do evento extraído"""
                        start_limit, financial_effect_date = extract_dates(
                            self._next_start_limit(
                                extracted_event,
                                instance_outside,
                                start_limit,
                                organizer=obj_organizer,
                            )
                        )

                if write_feedback:
                    update_task(
                        task=task,
                        total=total,
                        progress_message=f"{self.acronym}({self.extracted_class.NAME})"[
                            0:99
                        ],
                    )

            except Exception as err:
                log.info(instance_outside)
                log.exception(err)
                task_info(
                    task,
                    msg=f"Erro gerando {self.acronym} de {instance_outside}<br />{err}",
                    type_of=3,
                )

        self.manage_exclusion(task)

    def manage_exclusion(self, task):
        """Este método exclui eventos que estão em extractors_event_exclude.

        Args:
            task (engine.mq.models import Task): task"""
        for ext in self.extractors_event_exclude:
            extractor = self.extractors_event_exclude.get(ext)
            events = Event.objects.filter(pk=extractor._event.pk)
            if events.exists():
                event = events.last().event
                modified_by_event = (
                    hasattr(event, "modified_by_event") and event.modified_by_event
                )
                """Só fará exclusão caso não tenha sido modificado por outro evento."""
                if not modified_by_event:
                    try:
                        extractor.run()
                    except Exception as err:
                        log.exception(err)
                        task_info(
                            task,
                            msg=f"Erro gerando {extractor.acronym()}<br />{err}",
                            type_of=3,
                        )

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
            oid=oid, registry_employee=registry, registry_person=registry_person
        )

    def delete_not_send(self, oid=None, registry=None, registry_person=None):
        """Este método apaga os eventos que podem ser excluídos a partir da queryset can_exclude.

        Args:
            oid (int):
            registry (int):
            registry_person (str):
        """
        query = self._query_delete_not_send(
            oid=oid, registry=registry, registry_person=registry_person
        )
        for event in query:
            event.delete()

    def delete_xsd_schema_invalid(self, oid, registry=None, registry_person=None):
        """Este método apaga os não validados.

        Args:
            oid (int):
            registry (int):
            registry_person (str):
        """
        query = self.extracted_class.objects.not_validated().filter(
            oid=oid, registry_employee=registry, registry_person=registry_person
        )
        for event in query:
            event.delete()

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid."""
        return self.extracted_class.objects.valids_by_status().filter(
            oid=oid, registry_employee=registry, registry_person=registry_person
        )

    def _find_event_for_competence(
        self,
        instance_outside,
        start_limit,
        end_limit=None,
        task=None,
        registry=None,
        registry_person=None,
        period=None,
        financial_effect_date=None,
        organizer=None,
    ):
        """Método para encontrar evento em função de start_limit e end_limit.

        Args:
            instance_outside (Object)
            start_limit (date)
            end_limit (date):
            task (engine.mq.models.Task): default None.
            registry (int): matrícula do Servidor, default None.
            registry_person (str): cpf do Servidor, default None.
            period (int): pk de rh.gfp.models.Periodo, default None.
            financial_effect_date (date):
            organizer (object):

        Returns:
            extractor_event (Extractor): se encontrar o evento, retorna o extractor_event, default None.
        """
        dr_limit = NewDateRange(start_limit, end_limit)

        oid = self._get_oid(
            instance_outside,
            month=period.mes if period else None,
            year=period.ano if period else None,
            start_limit=start_limit,
            financial_effect_date=financial_effect_date,
            organizer=organizer,
        )

        events = self._query_events_extracted(
            oid,
            start_limit,
            instance_outside,
            registry=registry,
            registry_person=registry_person,
        )

        for event in events.order_by("start_validity"):
            params = {
                "event": event,
                "start_validity": start_limit,
                "end_validity": end_limit,
                "task": task,
                "period": period,
                "financial_effect_date": financial_effect_date,
                "organizer": organizer,
            }
            extractor_event = self.extractor(instance_outside, **params)
            if extractor_event.start_validity():
                dr_extractor_event = NewDateRange(
                    extractor_event.start_validity(), extractor_event.end_validity()
                )
                """Verifica se o evento exite nos limites informados."""
                if dr_limit.intersect(dr_extractor_event).days:
                    """Remove evento que era candidato a exclusão quando ele torna-se atualizável."""
                    self.extractors_event_exclude.pop(event.pk, None)
                    return extractor_event
            else:
                """Caso evento não exista nos limites informados, verifica se existe em seus próprios limites."""
                params = {
                    "event": event,
                    "start_validity": event.start_validity,
                    "end_validity": event.end_validity,
                    "task": task,
                    "period": period,
                    "financial_effect_date": financial_effect_date,
                    "organizer": organizer,
                }
                extractor_event = self.extractor(instance_outside, **params)
                if not extractor_event.start_validity():
                    """Caso também não exista nos seus limites, será candidato a exclusão."""
                    extractor_to_exclude = self.extractors_event_exclude.get(
                        event.pk, None
                    )
                    if not extractor_to_exclude or (
                        extractor_to_exclude and extractor_to_exclude._exclude is False
                    ):
                        self.extractors_event_exclude.update(
                            {event.pk: extractor_event}
                        )
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
        """Este método encontra os eventos encobertos por extracted_event para indicar a exclusão. Ele roda durante o manage_in_bulk.
        Adiciona os eventos encontrados a extractors_event_exclude.

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
                self.extracted_class.objects.validity_in(
                    extracted_event.start_validity, extracted_event.end_validity
                )
                .filter(
                    oid=self._get_oid(
                        instance_outside,
                        month=period.mes if period else None,
                        year=period.ano if period else None,
                        organizer=organizer,
                    ),
                    registry_employee=registry,
                    registry_person=registry_person,
                )
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
        ...

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        if extracted_event and extracted_event.end_validity:
            start_limit, _ = extract_dates(
                self._next_day(
                    instance_outside, extracted_event.end_validity, organizer=organizer
                )
            )
        elif extracted_event and extracted_event.end_validity is None:
            """Modificamos para colocar start_limit None quando o fim do extracted_event for None"""
            start_limit = None
        else:
            start_limit, _ = extract_dates(
                self._next_day(instance_outside, start_limit, organizer=organizer)
            )
        return start_limit

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise.
        Em outros extratores pode ser o próximo dia apenas."""
        date = date if date else datetime.now()
        date = limits_from_date(date)[1]
        return date + relativedelta(days=1)

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        """Este método retorna o data de limite inicial. Por padrão baseia-se no máximo entre start_limit e cls.initial_group_date()."""
        return max(
            filter(lambda x: x is not None, [start_limit, self.initial_group_date()])
        )

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        """Este método retorna o data de limite final. Por padrão baseia-se em um NewDateRange de start_limit.year e start_limit.month
        utilizando o seu last."""
        return NewDateRange.from_month(start_limit.year, start_limit.month).last


class Extractor(object):
    """
    Extrator básico de eventos do eSocial.

    Constantes classe:
        EXTRACTED_CLASS: classe do evento que será extraído, padrão é None pois quando referir-se a um evento do esocial a classe será
        extraída em cls._get_extract_model
        ACRONYM: acrônimo do evento quer será extraído, padrão é None pois quando referir-se a um evento do esocial a classe será
        extraída em self.acronym
        INTERNAL: define se objeto extraído é apenas interno, ou seja, não é enviado para o eSocial, padrão é False
        FIELDS_NOT_PERSIST: campos que não devem ser persistidos
        MAP_FIELDS_EQUALS: mapeamento de campos com a mesma semântica, porém com definição diferente. Geralmente utilizado em herança de
        outro extrator quando os campos são diferentes. Padrão {}.
        EXCLUDE_FIELDS_EQUALS: campos que serão excluídos na comparação do evento. Geralmente campos não sensíveis. Padrão [].
        VALIDITY_FIELDS: campos de validade do evento, sempre serão excluídos da comparação de conteúdo.
        Padrão ['ide_periodo_ini_valid', 'ide_periodo_fim_valid', 'nova_validade_ini_valid', 'nova_validade_fim_valid']
    """

    EXTRACTED_CLASS = None
    ACRONYM = None
    INTERNAL = False
    FIELDS_NOT_PERSIST = ["_class_"]
    MAP_FIELDS_EQUALS = {}
    EXCLUDE_FIELDS_EQUALS = ["rra"]
    VALIDITY_FIELDS = []
    EXCLUDE_FIELDS_DIFF_DEFAULT = [
        "ide_evento_nr_recibo",
        "ide_evento_ind_retif",
        "ide_evento_tp_amb",
        "rra",
    ]

    def __str__(self):
        return "%s - Extractor" % self.extracted_class

    def __init__(
        self,
        instance_outside,
        extracted_event=None,
        extracted_json={},
        force_extract=False,
        update_dependecies=False,
        event=None,
        period=None,
        task=None,
        clear=False,
        exclude=False,
        start_validity=None,
        end_validity=None,
        extractor_base=None,
        financial_effect_date=None,
        organizer=None,
        oid=None,
    ):
        """Params:
        instance_outside *: instância geradora do evento do esocial
        extracted_event Event: Event extraído, inicialmente uma instância vázia
        extracted_json dict: dict da extração do evento
        force_extract bool: bool indicando se é obrigatória a extração, default False
        update_dependecies bool: bool indicando se é obrigatória a atualização das dependências, default False
        event Event: Event enviado para comparação de validade e conteúdo no momento da extração
        period *: período da folha
        task Task:
        clear bool: bool indicando se é limpeza(utilizado no s1000), default False
        exclude bool: bool indicando se é exclusão, default False
        start_validity date: início de validade, start_validity é o valor passado(que é o início da compentência),
        ou do self._event ou da data do momento
        end_validity date: fim de validade, end_validity é o valor passado(que é o fim da compentência), ou None
        extractor_base Extractor: default None, extrator base para chamadas a extratores internos
        organizer (object):
        oid (str):"""
        self._extracted_class = self.EXTRACTED_CLASS
        self._acronym = self.ACRONYM
        self._internal = self.INTERNAL
        self._action = INCLUSION
        self.clear = clear

        self.validate_validity_fields()

        self._initial_group_date = None
        self._instance_outside = instance_outside
        self._extracted_event = (
            extracted_event if extracted_event else self.extracted_class()
        )
        self._extracted_fields_json = extracted_json or {}
        self._force_extract = force_extract
        self._update_dependencies = update_dependecies
        self._event = event
        self._period = period
        self._task = task
        self._exclude = exclude
        self._extractor_base = extractor_base
        self._organizer = organizer
        self._oid = oid

        self._extracted_class_created_list = []
        self._dependencies_to_add = []
        self._referencies_outside_to_add = []
        self._configuration = None

        """O _start_validity é o passado(que é o da compentência), ou do self._event ou da data do momento"""
        self._start_validity_init = start_validity
        self._end_validity_init = end_validity
        self._start_validity = start_validity
        self._end_validity = end_validity
        self._financial_effect_date = financial_effect_date

        if not self._start_validity:
            self._start_validity = (
                self._event.start_validity
                if self._event
                else datetime.datetime.now().date()
            )
        if not self._end_validity:
            self._end_validity = self._event.end_validity if self._event else None

        if not self._exclude:
            (
                self._start_validity,
                self._end_validity,
                self._referencies_outside_to_add,
            ) = self._define_references()
        else:
            if not self._event:
                raise Exception("Informe um evento(event) para gerar exclusão.")

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        _references_strong_start_date = self._references_strong_start_date()

        references = []
        start_validity = None
        end_validity = None
        if _references_strong_start_date:
            dts = [
                NewDateRange.from_month(start_date.year, start_date.month).first
                for start_date in _references_strong_start_date
            ]
            dts.append(self.initial_group_date())
            start_validity = max(dts)

            references = self._references()

            """definindo o fim com a maior data da própria referência"""
            _references_end_date = self._references_end_date()
            end_validity_dates = (
                [max(_references_end_date)] if _references_end_date else []
            )
            if end_validity_dates:
                end_validity = end_validity_dates[0]

            """caso exista próxima referência, definindo o fim com a menor data das próximas referências"""
            references_next = self._references_next()
            if references_next:
                dates = [
                    NewDateRange.from_month(start_date.year, start_date.month).first
                    for start_date in references_next
                ]
                end_validity = min(end_validity_dates + dates)
                end_validity -= relativedelta(days=1)
                end_validity = NewDateRange.from_month(
                    end_validity.year, end_validity.month
                ).last

        return start_validity, end_validity, references

    def _references(self, start_validity=None):
        return []

    def _references_weak(self):
        return []

    def _references_strong(self, start_validity=None):
        return []

    @property
    def _class_config(self):
        """Esta propriedade retorna a classe da configuração utilizada como referência.

        Returns:
            class
        """
        return None

    def _config(self):
        """Este método retorna o queryset básico da referência.

        Returns:
            queryset
        """
        return self._class_config.objects.none() if self._class_config else []

    def _references_next(self, start_validity=None):
        references_next = []
        if self._class_config:
            references = self._references()
            q_config = (
                self._config()
                .filter(start_validity__gt=self._start_validity)
                .exclude(
                    pk__in=[
                        ref.pk
                        for ref in references
                        if isinstance(ref, self._class_config)
                    ]
                )
            )
            if q_config:
                references_next.append(
                    q_config.earliest("start_validity").start_validity
                )
        return references_next

    def _query_config_reference(self):
        """Este método retorna o queryset da referência. Definido

        Returns:
            queryset
        """
        if self._start_validity:
            query = self._config()
            query = query.filter(
                Q(start_validity__lte=self._start_validity)
                & (Q(end_validity__gte=self._start_validity) | Q(end_validity=None))
            )
        else:
            query = self._class_config.objects.none()
        return query

    def _references_strong_start_date(self):
        return []

    def _references_strong_end_date(self, start_validity=None):
        return []

    def _references_end_date(self):
        return []

    def validate_validity_fields(self):
        if not self.VALIDITY_FIELDS:
            log.info(
                f"VALIDITY_FIELDS não foi preenchido, é obrigatório pois comparação de conteúdo pode falhar.{self.acronym()}"
            )

    @classmethod
    def _get_extract_model(cls, extract_model=None):
        """Este método retorna o modelo que será extraído. Utilizando EXTRACTED_CLASS, ou get_register_model do extrator.

        Args:
            extract_model (Event): Event. Defaults to None.

        Returns:
            Event: Event
        """
        if not extract_model:
            extract_model = cls.EXTRACTED_CLASS
        if not extract_model:
            extract_model = get_register_model(
                ((cls.__name__).upper()).replace("EXTRACTOR", "")
            )

        return extract_model

    @classmethod
    def initial_group_date(cls):
        """Este método retorna a data do início da obrigatoriedade de acordo com o GROUP do modelo(EXTRACTED_CLASS) extraído.
        Caso seja ambiente 2 e for eventos de benefiário será retornado 4.

        Returns:
            date: data do início da obrigatoriedade do grupo."""
        cfg = Configuration.current_config()
        map_group_to_initial_date_config = {
            1: cfg.initial_date_start_tables,
            2: cfg.initial_date_non_periodic_events,
            3: cfg.initial_date_periodic_events,
            4: cfg.initial_date_sst_events,
        }

        extracted_class = cls._get_extract_model()
        check_benefit = (
            cfg.environment == 2 and str(extracted_class.__name__).lower()[0:3] == "s24"
        )

        if check_benefit:
            return date(2021, 11, 22)
        return map_group_to_initial_date_config.get(extracted_class.GROUP)

    def _without_referencies_outside_to_add(self):
        if not self._referencies_outside_to_add:
            return True
        return False

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return len(self._references_strong(self._start_validity)) > 0

    def pre_validate(self):
        """Este método realiza a pré-validação."""
        return_type = NO_RESTRICTION
        if self._event and self._exclude:
            return_type = EXCLUDE_EVENT
        elif self._event and not self.check_reference_strong() and not self.internal:
            return_type = DOESNT_EXIST_REFERENCE
        elif (
            not self._event and not self.check_reference_strong() and not self.internal
        ):
            return_type = NOTHING_TODO
        return return_type

    def check_diff(self, diffs_content, diff_validity):
        """Este método é utilizado para modificar o pos_validate após diff_content e diff_validity estarem prontos.
        Cabe a cada extrator realizar a mudança e retornar um valor de retorno válido:
            NO_RESTRICTION, EXCLUDE_EVENT, DOESNT_EXIST_REFERENCE, NOTHING_TODO, SAME_EVENT, DIFF_VALIDITY_END_SAME_CONTENT,
            DIFF_VALIDITY_SAME_CONTENT, EQUAL_VALIDITY_DIFF_CONTENT, DIFF_VALIDITY_DIFF_CONTENT

        Args:
            diff_content (dict): dict de diff entre Event
            diff_validity (int): um dos valores: EQUAL_VALIDITY, DIFF_VALIDITY_END

        Returns:
            int: valor de retorno, default None(não interfere no pos_validate)
        """
        return None

    def pos_validate(self):
        """Metodo que valida o json gerado na extração e verifica as pendencias
        dele com os eventos já existentes

        Raises:
            Exception -- [description]
            Exception -- [description]

        Returns:
            [int] --    0: Sem restrições
                        1: Igual ao ultimo evento existente
                        2: Igual validade e conteudo diferente
        """
        return_type = NO_RESTRICTION
        if not self._event:
            return return_type

        """Avaliando as diferenças entre o evento (event) o e evento a ser extraido"""
        exclude_fields = self.EXCLUDE_FIELDS_EQUALS + self.EXCLUDE_FIELDS_DIFF_DEFAULT
        diff_content = self._event.compare_fields(
            self._extracted_fields_json,
            exclude_fields=exclude_fields,
            map_fields=self.MAP_FIELDS_EQUALS,
        )

        if diff_content:
            diff_content = convert_diff_content(diff_content)
            self._extracted_fields_json.update({"diff_content": diff_content})

        diff_validity = validity_between_events(
            NewDateRange(self._event.start_validity, self._event.end_validity),
            NewDateRange(self.start_validity(), self.end_validity()),
        )

        check_diff = self.check_diff(diff_content, diff_validity)
        if check_diff is not None:
            return check_diff
        elif self._without_referencies_outside_to_add():
            return_type = DOESNT_EXIST_REFERENCE
        elif not diff_content:
            if diff_validity == EQUAL_VALIDITY:
                """Caso não exista diferença de conteúdo e seja mesma validade"""
                return_type = SAME_EVENT
            elif diff_validity == DIFF_VALIDITY_END:
                """Caso exista diferença de conteúdo e seja validade diferente"""
                return_type = DIFF_VALIDITY_END_SAME_CONTENT
            else:
                """Caso exista diferença de conteúdo e seja validade diferente"""
                return_type = DIFF_VALIDITY_SAME_CONTENT
        elif diff_content:
            if diff_validity == EQUAL_VALIDITY:
                """Caso exista diferença de conteúdo e seja mesma validade"""
                return_type = EQUAL_VALIDITY_DIFF_CONTENT
            else:
                """Caso exista diferença de conteúdo e seja mesma validade"""
                return_type = DIFF_VALIDITY_DIFF_CONTENT
        else:
            msg = f"POS_VALIDATE em _event: {self._event}<br />instance_outside{self._instance_outside}<br />"
            msg += f"diff_content: {diff_content}<br />diff_validity: {diff_validity}"
            self.task_info(msg=msg, type_of=3)

        if diff_validity != EQUAL_VALIDITY:
            diff_content = f"{diff_content} | {MAP_VALIDITY_RESULT.get(diff_validity)} | {MAP_VALIDATE_RESULT.get(return_type)}"
            self._extracted_fields_json.update({"diff_content": diff_content})

        return return_type

    def run(self):
        validate = self.pre_validate()

        # print(f'pre_validate({validate}): {MAP_VALIDATE_RESULT.get(validate)}')

        if validate != NOTHING_TODO:

            exclude = False
            if validate in (DOESNT_EXIST_REFERENCE, EXCLUDE_EVENT):
                exclude = True

            if not self._extracted_fields_json or self._force_extract:
                self.extract_fields(exclude=exclude)

            if validate not in (DOESNT_EXIST_REFERENCE, EXCLUDE_EVENT):
                validate = self.pos_validate()

            # print(f'pos_validate({validate}): {MAP_VALIDATE_RESULT.get(validate)}')

            if validate == NO_RESTRICTION:
                self._run_persist_dict_to_event()
                self.task_info(msg=f"Criou: {self.acronym()} - {self.description()}")
            elif validate in (
                EQUAL_VALIDITY_DIFF_CONTENT,
                DIFF_VALIDITY_DIFF_CONTENT,
                DIFF_VALIDITY_SAME_CONTENT,
                DIFF_VALIDITY_END_SAME_CONTENT,
            ):
                """EVENTOS S10XX:                                           ALTERAÇÃ0
                EVENTOS S-1200, S-1202, S-1207, S-1210, S-22XX, S-22XX:  RETIFICAÇÃO
                """
                if self._event:
                    if self._event.process_status in PROCESS_STATUS_EVENT_NOT_SENT:
                        """Chama atualização do evento que ainda não foi enviado"""
                        if self._event.process_status == 3:
                            self._event.batches.last().delete()
                            self._event.batches.clear()
                        self._run_persist_dict_to_event(update_event_pk=self._event.pk)
                        log.info(
                            f"Atualizou evento não enviado: {self.acronym()} - {self.description()}"
                        )
                        self.task_info(
                            msg=f"Atualizou evento não enviado: {self.acronym()} - {self.description()}",
                            type_of=1,
                        )
                    elif self._event.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT:
                        """GERANDO Event de alteração"""
                        self._run_event_modification(validate=validate)
                    else:
                        message = f"\n\n\nPROCESS_STATUS INVÁLIDO PARA ATUALIZAÇÃO/RETIFICAÇÃO {self._event} - {self._event.process_status}"
                        message = (
                            f"{message} - {self._event.get_process_status_display()}"
                        )
                        log.info(message)
                else:
                    self._run_persist_dict_to_event()
                    self.task_info(
                        msg=f"GERANDO Evento de inclusão (ANALISAR): {self.acronym()} - {self._extracted_event}"
                    )
            elif validate in (DOESNT_EXIST_REFERENCE, EXCLUDE_EVENT):
                """GERANDO Event de exclusão"""
                if (
                    self._event
                    and self._event.process_status in PROCESS_STATUS_EVENT_NOT_SENT
                ):
                    """Chama atualização do evento que ainda não foi enviado"""
                    if self._event.process_status == 3:
                        self._event.batches.last().delete()
                        self._event.batches.clear()
                    msg = f"Excluiu não enviado: {self.acronym()} - {self._event}"
                    self._event.delete()
                    self.task_info(msg=msg, type_of=1)
                elif (
                    self._event
                    and self._event.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT
                ):
                    self._run_event_exclusion(validate=validate)
                elif self._event:
                    message = f"\n\n\nPROCESS_STATUS INVÁLIDO PARA EXCLUSÃO {self._event} - {self._event.process_status}"
                    message = f"{message} - {self._event.get_process_status_display()}"
                    log.info(message)
                else:
                    msg = f"RUN {self.__class__} em instance_outside {self._instance_outside}<br /> {MAP_VALIDATE_RESULT.get(validate)}({validate})"
                    print(msg)
                    self.task_info(msg=msg, type_of=2)
            elif validate in (SAME_EVENT, NOTHING_TODO):
                pass
            else:
                msg = f"RUN em _event: {self._event}<br />instance_outside{self._instance_outside}<br />"
                msg += f"{MAP_VALIDATE_RESULT.get(validate)}({validate})"
                print(msg)
                self.task_info(msg=msg, type_of=3)

        if self.result_event:
            self.result_event.evaluate_dependency(task=self._task)

        event = self.result_event

        if validate == DIFF_VALIDITY_END_SAME_CONTENT:
            event = None

        return event

    @property
    def result_event(self):
        """Esta propriedade retorna o evento extraído ou o event enviado para análise no extrator. Deve ser utilizado após a extração."""
        event = self._extracted_event
        if event and not event.pk:
            event = self._event
        return event

    def _run_persist_dict_to_event(self, update_event_pk=None):
        extracted_fields_json = copy.deepcopy(self._extracted_fields_json)
        self._extracted_event = persist_dict_to_event(
            extracted_fields_json,
            update_event_pk=update_event_pk,
            fields_with_not_persist=self.FIELDS_NOT_PERSIST,
            instance_outside=self._instance_outside,
            task=self._task,
        )

        self._extracted_class_created_list.append(self._extracted_event)

        self._set_referencies()

        if not self._extracted_event.internal:
            self._extracted_event.set_validation_xml_schema()

    def _run_event_modification(self, validate=None):
        """GERANDO Event de alteração.

        Args:
            validate (int): default None, valores definidos em MAP_VALIDATE_RESULT.
        """
        if MODIFICATION in self._extracted_class.ACTION_PERM:
            self._extracted_fields_json.update(
                action=MODIFICATION, modify_event=self._event
            )
            self._run_persist_dict_to_event()
            self.task_info(
                msg=f"Alteração: {self.acronym()} - {self.description()}", type_of=2
            )
        elif RECTIFICATION in self._extracted_class.ACTION_PERM:
            self._extracted_fields_json.update(
                action=RECTIFICATION,
                ide_evento_ind_retif=FILE_ORIGIN_RECTIFIED,
                ide_evento_nr_recibo=self._event.process_receipt,
                modify_event=self._event,
            )
            self._run_persist_dict_to_event()
            self.task_info(
                msg=f"Alteração: {self.acronym()} - {self.description()}", type_of=2
            )
        else:
            self.task_info(
                msg=f"Alteração inválida! Contate a TI. {self._event}", type_of=3
            )
            log.info(f"Alteração inválida! Contate a TI. {self._event}")
            log.info(self._extracted_fields_json)

    def _run_event_exclusion(self, validate=None):
        """Este método gera o evento de exclusão."""
        from esocial.extractors.s3000 import S3000Extractor

        task = self._task.uuid if self._task else None
        if self._extracted_class.EXCLUSION_TYPE == EXCLUSION_TYPE_DEFAULT:
            """Tenta encontrar o evento de exclusão para remover e reiniciar o processo."""
            try:
                event = S3000.objects.get(
                    modify_event=self._event,
                    process_status__in=PROCESS_STATUS_EVENT_NOT_SENT,
                )
            except S3000.DoesNotExist:
                pass
            else:
                if event.process_status == 3:
                    event.batches.last().delete()
                    event.batches.clear()
                event.delete()
            finally:
                self._extracted_fields_json.update(
                    action=EXCLUSION, modify_event=self._event
                )
                self._run_persist_dict_to_event()
                self.task_info(
                    msg=f"Exclusão: {self.acronym()} - {self.description()}", type_of=1
                )

                month = self._period.mes if self._period else None
                year = self._period.ano if self._period else None

                month = self._period.mes if self._period else None
                year = self._period.ano if self._period else None

                def set_dependency_exclusion_before():
                    """Este método aplica dependência de envio de exclusão antes do envio de inclusão/alteração."""
                    for evt in (
                        self.extracted_class.objects.valids_not_sent()
                        .filter(
                            oid=self.oid()
                            # oid=self._get_oid(self._instance_outside, month=month, year=year, organizer=self._organizer)
                        )
                        .exclude(pk=self._extracted_event.pk)
                    ):
                        evt.add_dependency(
                            task=task,
                            events=[self._extracted_event],
                            oid=self._get_oid(
                                self._instance_outside,
                                month=month,
                                year=year,
                                organizer=self._organizer,
                            ),
                            acronyms=(self._acronym,),
                            create_if_not_exist=False,
                            required=False,
                        )

                set_dependency_exclusion_before()
        elif self._extracted_class.EXCLUSION_TYPE == EXCLUSION_TYPE_S3000:
            S3000Extractor(self._event, event=self._event).run()

    def set_dependency(
        self,
        events=[],
        oid=None,
        acronyms=(),
        required=True,
        create_if_not_exist=True,
        validate_function=None,
        filter_query_instance=None,
        query_filter=None,
        filter_validity_in=True,
        registry_employee=None,
        registry_person=None,
    ):
        """
        Args:
            events (list): default []
            oid (object): default None, qualquer objeto
            acronyms (tuple[str]): default [], list de acrônimos
            required (bool): default True
            create_if_not_exist (bool): default True
            validate_function (object(callable)): default None,
            filter_query_instance (Queryset): default None, queryset que será utilizado no factory para especificar quem será extraído
            query_filter (Queryset): default None -- query filter utilizado para filtro alternativo ao inst_outside
            filter_validity_in (bool): default True, indica se o queryset validity_in será aplicado
            registry_employee (int): default None, matrícula do servidor
            registry_person (int): default None, cpf da pessoa física
        """
        self._dependencies_to_add.append(
            {
                "events": events,
                "oid": oid,
                "acronyms": acronyms,
                "required": required,
                "create_if_not_exist": create_if_not_exist,
                "validate_function": validate_function,
                "filter_query_instance": filter_query_instance,
                "query_filter": query_filter,
                "filter_validity_in": filter_validity_in,
                "registry_employee": registry_employee,
                "registry_person": registry_person,
            }
        )

    def _set_referencies(self):
        if self._extracted_event:
            for ref in self._referencies_outside_to_add:
                Reference.get_or_create(ref_object=ref, event=self._extracted_event)

    @property
    def configuration(self):
        if not self._configuration:
            self._configuration = Configuration.current_config()
        return self._configuration

    @property
    def extracted_class(self):
        if not self._extracted_class:
            self._extracted_class = self._get_extract_model()
        return self._extracted_class

    @property
    def extracted_event(self):
        if self._extracted_event:
            return self._extracted_event
        return None

    def _fields_names(self):
        return [fld.name for fld in self.extracted_class._meta.get_fields()]

    def extract_fields(self, exclude=False):
        all_field_names = set(self.FIELDS_NOT_PERSIST + self._fields_names())

        exclude_fields = []
        """Exclue campos da extração quando estiver excluindo. Pois não é necessário aplicar alguns valores que serão
        preenchidos na instância.
        Outros campos de m2m e onetoone não serão preenchidos.
        """
        if exclude:
            # TODO: AVALIAR POSSIBILIDADE DE AUTOMATICAMENTE, PEGAR OS CAMPOS QUE SÃO EXCLUSIVAMENTE DO Event
            exclude_fields = [
                "event",
                "pk",
                "id",
                "created_by",
                "created_at",
                "acronym",
                "oid",
                "identifier",
                "event_ptr",
                "xsd_schema_validated",
                "process_receipt",
                "xmlns",
                "process_status",
                "process_date",
                "modified_at",
                "modified_by",
                "competence_month",
                "competence_year",
                "archived",
            ]
            m2m_fields = [
                "results",
                "eventdependency_dependency",
                "references",
                "eventdependency_event",
                "children",
                "eventconnection_s5001",
                "eventconnection_s5002",
                "eventconnection_s5011",
                "eventconnection_s5012",
                "eventconnection_s5501",
                "payrollperiod_s1298",
                "payrollperiod_s1299",
                "pendencyperiod",
            ]
            m2m_fields += [f.name for f in self._event._meta.many_to_many]
            m2m_fields += [f.name for f in all_fields_many_to_many_rel(self._event)]
            exclude_fields += m2m_fields

        def _extract_from_extractor(name):
            """Extração exclusiva do extrator"""
            method_evaluate = getattr(self, name, None)
            if callable(method_evaluate):
                self._extracted_fields_json[fld_name] = method_evaluate()

        def _extract_with_exclude(name):
            """Extrai name a partir de um método de evaluação do extrator.
            Quando exclude é True, deve possuir self._event, utiliza o valor extraído do self._event
            """
            if (
                name not in exclude_fields
                and hasattr(self._event, name)
                and name not in self.VALIDITY_FIELDS
            ):
                """extraindo com dados do self._event"""
                self._extracted_fields_json[fld_name] = getattr(self._event, name, None)
            else:
                """extraindo com extrator"""
                _extract_from_extractor(name)

        _extract = _extract_from_extractor
        if exclude is True:
            _extract = _extract_with_exclude

        for fld_name in all_field_names:
            try:
                _extract(fld_name)
            except Exception as err:
                log.exception(err)
                log.info(self.description())
                self.task_info(
                    msg=f"Erro extraindo {fld_name} para {self.description()} em {self.acronym()}<br />{err}",
                    type_of=3,
                )

    def _class_(self):
        return self.extracted_class

    def task_info(self, msg="", type_of=1):
        task_info(self._task, msg=msg, type_of=type_of)

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """

        return str(
            instance_outside.get("pk")
            if isinstance(instance_outside, dict)
            else instance_outside.pk
        )

    def oid(self):
        return self._get_oid(self._instance_outside)

    @classmethod
    def _get_control_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """

        return None

    def control_oid(self):
        return self._get_control_oid(self._instance_outside)

    def registry_employee(self):
        registry = None
        if hasattr(self._instance_outside, "matricula"):
            registry = self._instance_outside.matricula
        elif hasattr(self._instance_outside, "servidor"):
            registry = self._instance_outside.servidor.matricula
        elif hasattr(self._instance_outside, "employee"):
            registry = self._instance_outside.employee.matricula
        return registry

    def start_validity(self):
        if not self._start_validity:
            return None
        if not self._initial_group_date:
            self._initial_group_date = self.initial_group_date()
        if self._start_validity:
            self._initial_group_date = max(
                filter(
                    lambda x: x is not None,
                    [self._initial_group_date, self._start_validity],
                )
            )
        return self._initial_group_date

    def end_validity(self):
        end_validity = None
        if self._end_validity:
            end_validity = max(self._end_validity, self.start_validity())
        return end_validity

    def ini_valid(self):
        return format_reference(self.start_validity())

    def fim_valid(self):
        return format_reference(self.end_validity())

    def ide_empregador_tp_insc(self):
        return self.configuration.ide_employer_tp_insc

    def ide_empregador_nr_insc(self):
        return self.configuration.ide_employer_nr_insc[0:8]

    def ide_evento_tp_amb(self):
        """
        Identificação do ambiente:
        1 - Produção;
        2 - Produção restrita.
        Valores Válidos: 1, 2.
        """
        return esocial_environment()

    def ide_evento_proc_emi(self):
        """
        Processo de emissão do evento:
        1- Aplicativo do empregador;
        2 - Aplicativo governamental.
        Valores Válidos: 1, 2.
        """
        return EMPLOYER_APP

    def ide_evento_ver_proc(self):
        """
        Versão do processo de emissão do evento. Informar a versão do aplicativo
        emissor do evento.
        """
        return "0.1"

    def ide_evento_ind_retif(self):
        """
        Informe [1] para arquivo original ou [2] para arquivo de retificação.
        Valores Válidos: 1, 2.
        """
        return FILE_ORIGIN_ORIGINAL

    def ide_evento_ind_apuracao(self):
        """
        Indicativo de período de apuração:
        1 - Mensal;
        2 - Anual (13° salário).
        Valores Válidos: 1, 2
        """
        return None

    def ide_evento_per_apur(self):
        """
        Informar o mês/ano (formato AAAA-MM) de referência das informações, se
        {indApuracao} for igual a [1], ou apenas o ano (formato AAAA), se
        {indApuracao} for igual a [2]
        Validação: Deve ser um mês/ano ou ano válido, igual ou posterior a
        implementação do eSocial.
        """
        return None

    def ide_evento_nr_recibo(self):
        """
        Preencher com o número do recibo do arquivo a ser retificado.
        Validação: O preenchimento é obrigatório se {indRetif} = [2].
        Deve ser um recibo de entrega válido, correspondente ao arquivo que está
        sendo retificado.
        """
        return None

    def search_cache(self):
        return "{}".format(self._instance_outside)

    def modified_by_event_cache(self):
        return ""

    def batch_cache(self):
        return ""

    def name(self):
        return self.extracted_event._name

    @classmethod
    def _define_acronym(cls):
        return cls.__name__.lower().replace("extractor", "")

    def acronym(self):
        if not self._acronym:
            self._acronym = self.__class__._define_acronym()
        return self._acronym

    def description(self):
        return "{}".format(self._instance_outside)

    def validator(self):
        return None

    def periodicity(self):
        return ANYTIME

    def obligation(self):
        return MANDATORY_IF_EXIST

    def action(self):
        return self._action

    def rectified_register(self):
        return None

    def competence_month(self):
        if self.start_validity():
            return self.start_validity().month
        return datetime.datetime.now().date().month

    def competence_year(self):
        if self.start_validity():
            return self.start_validity().year
        return datetime.datetime.now().date().year

    @property
    def internal(self):
        return self._internal


def administrative_unit():
    configuration = Configuration.current_config()
    if configuration:
        return configuration.employer
    else:
        raise Exception("Não foi possível encontrar o Empregador.")


def bool_yes_no(value):
    value_unicode = "S"
    if value is False:
        value_unicode = "N"
    return value_unicode


def format_date(value):
    return value.strftime(value, "%Y-%m-%d")


def format_space(value):
    return " ".join(value.split())


def task_info(task, msg="", type_of=1):
    if task:
        task.info(msg=msg, type_of=type_of)


def update_task(task=None, progress_message="", progress=0, increment=0, total=0):
    if task:
        if total != 0:
            increment = round(100.0 / float(total), 6)
        if increment:
            Task.objects.filter(pk=task.pk).update(progress=F("progress") + increment)
            task.refresh_from_db()

        if progress_message:
            msg_pct = "Processando %.1f%%" % (task.progress if task.progress else 0)
            Task.objects.filter(pk=task.pk).update(
                progress_message=f"{progress_message} {msg_pct}"
            )


class ConfigReference(object):

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.get("queryset", [])
        self.start_validity_field = kwargs.get("start_validity_field", "")
        self.end_validity_field = kwargs.get("end_validity_field", "")
        self.financial_effect_field = kwargs.get("financial_effect_field", "")

    def _references(self, date=None, go_limits=False, pair_date=False):
        """define as queries dos objetos de referência válidos"""
        objs = []
        if date:
            for obj in self.queryset:
                obj = getattr(obj, "my_origin", obj)
                start_date = getattr(obj, self.start_validity_field, None)
                if start_date:
                    if go_limits:
                        start_date = limits_from_date(start_date)[0]
                    if start_date == date:
                        objs.append(obj)
                if getattr(obj, self.end_validity_field, None):
                    end_date = getattr(obj, self.end_validity_field)
                    if self.end_validity_field != "data_desligamento":
                        end_date += relativedelta(days=1)
                    if go_limits:
                        end_date = limits_from_date(end_date)[1]
                    if end_date == date:
                        objs.append(obj)
        return objs

    def _queryset_date(self, go_limits=False, pair_date=False):
        """Este método retorna todas as datas, início e fim dos objetos sensíveis."""
        dates = []
        for obj in self.queryset:
            obj = getattr(obj, "my_origin", obj)
            start_date = None
            financial_effect_date = None
            if getattr(obj, self.start_validity_field, None):
                start_date = getattr(obj, self.start_validity_field)
                if go_limits:
                    start_date = limits_from_date(start_date)[0]
            if getattr(obj, self.financial_effect_field, None):
                financial_effect_date = getattr(obj, self.financial_effect_field)
                if go_limits:
                    financial_effect_date = limits_from_date(financial_effect_date)[0]

            if pair_date:
                dates.append(
                    [
                        start_date,
                        financial_effect_date if financial_effect_date else start_date,
                    ]
                )
            else:
                if start_date:
                    dates.append(start_date)
                if financial_effect_date:
                    dates.append(financial_effect_date)

            if getattr(obj, self.end_validity_field, None):
                new_date = end_date = getattr(obj, self.end_validity_field)
                if self.end_validity_field != "data_desligamento":
                    new_date = end_date + relativedelta(days=1)

                """Implementação adicionada para não 'pular' para o próximo mês."""
                if go_limits and end_date.month == new_date.month:
                    end_date = limits_from_date(new_date)[1]
                else:
                    end_date = new_date

                if pair_date:
                    dates.append([end_date, end_date])
                elif end_date:
                    dates.append(end_date)
        return dates
