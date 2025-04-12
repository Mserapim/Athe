# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from django.db.models import Q

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import NOTHING_TODO
from esocial.extractors.base import ConfigReference, Extractor, Factory
from esocial.models import S1010, IdeProcesso
from rh.gfp.models import ConfigEvent, Evento
from rh.models import ProcessSuspension

from .utils import format_reference

log = getLogger(__name__)


class S1010Extractor(Extractor):

    VALIDITY_FIELDS = [
        "ide_rubrica_ini_valid",
        "ide_rubrica_fim_valid",
        "nova_validade_ini_valid",
        "nova_validade_fim_valid",
    ]

    EXCLUDE_FIELDS_EQUALS = [
        "dados_rubrica_observacao",
    ]

    TAB_RUBR_BY_SUSPENSION = {
        "": "00000000",  # SEM SUSPENSÕES
        "2": "10000000",  # SUSPENSÃO INSS
        "1": "01000000",  # SUSPENSÃO IRRF
        "2,1": "11000000",  # SUSPENSÃO INSS E IRRF
    }

    TIPO_RUBRICA = {"P": 1, "D": 2, "I": 3}

    def __init__(self, *args, **kwargs):
        super(S1010Extractor, self).__init__(*args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self._event:
            """quando temos evento, utilizamos start_validity e checamos se ainda está no _queryset_date"""
            _queryset_date = self._queryset_date(
                (
                    self._instance_outside.numero
                    if self._instance_outside
                    else self._event.ide_rubrica_cod_rubr
                ),
                organizer=self._organizer,
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
        return self._start_validity is not None

    def _config(self):
        """queryset de (self._raw_query_config_event) processo cp, com todos dentro da validade.
        Utilizado para encontrar os próximos objetos de referência."""
        return ConfigEvent.objects.filter(event__numero=self._instance_outside.numero)

    def _references_next(self, start_validity=None):
        """Este método encontra as datas da próxima referência. Utiliza self._start_validity quando start_validity é None.

        Args:
            start_validity (datetime.date): default None

        Returns:
            list_start_date (set): set de datas maiores que start_validity
        """
        start_validity = self._start_validity if not start_validity else start_validity
        list_start_date = self._queryset_date(
            (
                self._instance_outside.numero
                if self._instance_outside
                else self._event.ide_rubrica_cod_rubr
            ),
            organizer=self._organizer,
        )
        list_start_date = set(filter(lambda dt: dt > start_validity, list_start_date))
        return list_start_date

    @classmethod
    def _queryset_date(cls, instance_outside, organizer=None):
        list_start_date = []
        if instance_outside:
            list_start_date_config = set(
                cls.cr_config_event(instance_outside)._queryset_date(go_limits=True)
            )
            min_date_config = min(list_start_date_config, default=None)
            list_start_date = cls.cr_process(
                instance_outside, organizer=organizer
            )._queryset_date(go_limits=True)
            list_start_date = set(
                filter(
                    lambda dt: min_date_config and dt > min_date_config, list_start_date
                )
            )
            list_start_date = list_start_date.union(list_start_date_config)
            initial_group_date = cls.initial_group_date()
            list_start_date = set(
                [max(dt, initial_group_date) for dt in list_start_date]
            )
        return list_start_date

    @classmethod
    def cr_config_event(cls, instance_outside):
        return ConfigReference(
            queryset=ConfigEvent.objects.filter(event__numero=instance_outside),
            start_validity_field="start_validity",
            end_validity_field="end_validity",
        )

    @classmethod
    def cr_process(cls, instance_outside, organizer=None):
        return ConfigReference(
            queryset=ProcessSuspension.objects.filter(
                process__gfp_events__numero=instance_outside
            ).filter(
                process__matter_process=1,
                scope_decision__in=type_suspensions_tab_rubr(organizer),
            ),
            start_validity_field="start_validity",
            end_validity_field="end_validity",
        )

    def pre_validate(self):
        if (
            not self._exclude
            and self._organizer != self.TAB_RUBR_BY_SUSPENSION.get("")
            and not self.tab_rubr_exists(
                self._instance_outside.numero,
                self._start_validity,
                self._end_validity,
                self._organizer,
            )
        ):
            return NOTHING_TODO
        return super().pre_validate()

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        oid = kwargs.get("oid", None)
        if not oid:
            tab_rubr = kwargs.get("organizer", "")
            oid = f"{instance_outside.numero}{tab_rubr}"
            if isinstance(instance_outside, dict):
                oid = f'{instance_outside.get("numero")}{tab_rubr}'
        return oid

    def oid(self):
        if self._exclude:
            return self._event.oid
        return self._get_oid(
            self._instance_outside, organizer=self._organizer, oid=self._oid
        )

    @classmethod
    def get_tab_rubr(
        cls, event_number, start_validity=None, end_validity=None, employee=None
    ):
        suspensions = cls._query_process_suspension(
            event_number, start_validity=start_validity, end_validity=end_validity
        )
        if employee:
            suspensions = suspensions.by_employee(employee)

        key = ""
        if suspensions.filter(scope_decision=2).exists():
            key = "2"
        if suspensions.filter(scope_decision=1).exists():
            key = f"{key},1" if key else "1"
        return cls.TAB_RUBR_BY_SUSPENSION.get(key)

    @classmethod
    def tab_rubr_exists(
        cls, event_number, start_validity=None, end_validity=None, organizer=None
    ):
        """Este método verifica se existe uma tabela de rubricas para o evento de acordo com o organizer.

        Args:
            event_number (str):
            start_validity (date):
            end_validity (date):
            organizer (str): identificação da tabela
        Returns:
            bool: QuerySet de ProcessSuspension."""
        type_suspensions = type_suspensions_tab_rubr(organizer)

        suspensions = cls._query_process_suspension(
            event_number, start_validity=start_validity, end_validity=end_validity
        ).filter(scope_decision__in=type_suspensions)
        type_found = set([str(susp.scope_decision) for susp in suspensions])

        return type_suspensions == type_found

    def ide_rubrica_cod_rubr(self):
        return self._instance_outside.numero

    def ide_rubrica_ide_tab_rubr(self):
        return self._organizer

    def ide_rubrica_ini_valid(self):
        if self._event:
            return format_reference(self._event.start_validity)
        return super(S1010Extractor, self).ini_valid()

    def ide_rubrica_fim_valid(self):
        if self._event:
            return format_reference(self._event.end_validity)
        return super(S1010Extractor, self).fim_valid()

    def dados_rubrica_dsc_rubr(self):
        return self._instance_outside.titulo.lstrip()

    def dados_rubrica_nat_rubr(self):
        config_event = self._query_config_reference().last()
        return (
            int(config_event.nature_event.code)
            if config_event and config_event.nature_event
            else 9989
        )

    def dados_rubrica_tp_rubr(self):
        return self.TIPO_RUBRICA.get(self._instance_outside.tipo, None)

    def dados_rubrica_cod_inc_cp(self):
        query_suspensions = ProcessSuspension.objects.by_event(
            self._instance_outside.numero,
            drange=NewDateRange(
                self._start_validity,
                self._start_validity if not self._end_validity else self._end_validity,
            ),
        ).filter(scope_decision=2)

        config = self._instance_outside.configs.validity_in(
            self._start_validity, self._end_validity
        )
        config = config.last()

        if config and config.esocial_cp:
            from_to_character = {}
            if query_suspensions.exists():
                from_to_character = {
                    # Código de incidência tributária da rubrica para a Previdência Social
                    # 2: '00',  # Não é base de cálculo;
                    # Base de cálculo das contribuições sociais - Salário de Contribuição
                    11: "91",  # Mensal;
                    12: "92",  # 13o Salário;
                    21: "93",  # Maternidade Mensal;
                    22: "94",  # Maternidade 13o Salário;
                }
            return from_to_character.get(config.esocial_cp.code, config.esocial_cp.code)
        return None

    def dados_rubrica_cod_inc_irrf(self):
        query_suspensions = self._query_process_suspension_irrf()

        config = self._instance_outside.configs.validity_in(
            self._start_validity, self._end_validity
        )
        config = config.last()
        if config:
            if config.esocial_irrf:
                if query_suspensions.exists():
                    from_to_character = {
                        # Rendimentos tributáveis - base de cálculo do IRRF:
                        1: 9011,  # Remuneração mensal;
                        9: 9012,  # 13o Salário;
                        13: 9013,  # Férias;
                        15: 11,  # Rendimentos Recebidos Acumuladamente - RRA;
                        # FIXME: 9031 IRRF SOBRE REMUNERAÇÃO
                        # FIXME: 9032 IRRF SOBRE 13
                        # FIXME: 9033 IRRF SOBRE FÉRIAS
                    }
                    return from_to_character.get(self._instance_outside.carater, None)
                return int(config.esocial_irrf.code)
            return None
        return 9

    def dados_rubrica_cod_inc_fgts(self):
        # TODO: DEFINIR
        return "00"

    def dados_rubrica_cod_inc_cprp(self):
        query_suspensions = ProcessSuspension.objects.by_event(
            self._instance_outside.numero,
            drange=NewDateRange(
                self._start_validity,
                self._start_validity if not self._end_validity else self._end_validity,
            ),
        ).filter(scope_decision=2)

        config = self._instance_outside.configs.validity_in(
            self._start_validity, self._end_validity
        )
        config = config.last()

        if config and config.esocial_cprp:
            from_to_character = {}
            if query_suspensions.exists():
                from_to_character = {
                    # Código de incidência tributária da rubrica para a Previdência Social
                    # 2: '00',  # Não é base de cálculo;
                    # Base de cálculo das contribuições sociais - Salário de Contribuição
                    11: "91",  # Mensal;
                    # vai para 93 quando for pra 91
                    12: "92",  # 13o Salário;
                    # 10: '25',  # Salário maternidade mensal pago pelo INSS;
                }
            return from_to_character.get(
                config.esocial_cprp.code, config.esocial_cprp.code
            )
        return None

    def dados_rubrica_teto_remun(self):
        return (
            "S"
            if self._instance_outside.aplica_em.filter(event__tags__label="redutorteto")
            .current_in(start_date=self._start_validity, end_date=self._end_validity)
            .exists()
            else "N"
        )

    def dados_rubrica_observacao(self):
        return (
            self._instance_outside.description[0:254]
            if self._instance_outside.description
            else None
        )

    @classmethod
    def _query_process_suspension(cls, event_number, start_validity, end_validity):
        """Este método retorna um queryset básico de ProcessSuspension para um Evento ativo em start_validity.
        Com escopo de decisão em [1, 2].

        Args:
            event_number (str):
            start_validity (date):
            end_validity (date):

        Returns:
            query (QuerySet): QuerySet de ProcessSuspension."""
        if event_number and start_validity:
            query = ProcessSuspension.objects.by_event(
                event_number,
                drange=NewDateRange(
                    start_validity, start_validity if not end_validity else end_validity
                ),
            )
        else:
            query = ProcessSuspension.objects.none()
        return query

    def _query_process_suspension_cp(self):
        """Este método retorna um queryset ProcessSuspension para um Evento ativo em start_validity.
        Com escopo de decisão em 2.

        Args:
            event_number (str):
            start_validity (date):
            end_validity (date):

        Returns:
            query (QuerySet): QuerySet de ProcessSuspension."""
        if self.ide_rubrica_ide_tab_rubr() in ["10000000", "11000000"]:
            return self._query_process_suspension(
                self._instance_outside.numero,
                start_validity=self._start_validity,
                end_validity=self._end_validity,
            ).filter(scope_decision=2)
        return ProcessSuspension.objects.none()

    def _query_process_suspension_irrf(self):
        """Este método retorna um queryset ProcessSuspension para um Evento ativo em start_validity.
        Com escopo de decisão em 1.

        Args:
            event_number (str):
            start_validity (date):
            end_validity (date):

        Returns:
            query (QuerySet): QuerySet de ProcessSuspension."""
        if self.ide_rubrica_ide_tab_rubr() in ("01000000", "11000000"):
            suspensions = self._query_process_suspension(
                self._instance_outside.numero,
                start_validity=self._start_validity,
                end_validity=self._end_validity,
            ).filter(scope_decision=1)
            return suspensions
        return ProcessSuspension.objects.none()

    def ide_processo_cp(self):
        suspensions = []
        query_suspensions = self._query_process_suspension_cp()
        for suspension in query_suspensions:
            suspensions.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "_class_": IdeProcesso,
                    "competence_month": self.competence_month(),
                    "competence_year": self.competence_year(),
                    "oid": suspension.process.number_process,
                    "ide_processo_nr_proc": suspension.process.number_process,
                    "ide_processo_cod_susp": suspension.id,
                    "ide_processo_tp_proc": suspension.process.type_process,
                    "ide_processo_ext_decisao": suspension.extension_decision,
                }
            )
        return suspensions

    def ide_processo_irrf(self):
        suspensions = []
        query_suspensions = self._query_process_suspension_irrf()
        for suspension in query_suspensions:
            suspensions.append(
                {
                    "start_validity": self.start_validity(),
                    "end_validity": self.end_validity(),
                    "_class_": IdeProcesso,
                    "competence_month": self.competence_month(),
                    "competence_year": self.competence_year(),
                    "oid": suspension.process.number_process,
                    "ide_processo_nr_proc": suspension.process.number_process,
                    "ide_processo_cod_susp": suspension.id,
                }
            )
        return suspensions

    def ide_processo_fgts(self):
        return []

    def nova_validade_ini_valid(self):
        return super(S1010Extractor, self).ini_valid()

    def nova_validade_fim_valid(self):
        return super(S1010Extractor, self).fim_valid()


class S1010Factory(Factory):

    EXTRACTED_MODEL_CLASS = S1010
    EXTRACTOR = S1010Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        return Evento.objects.filter(active=True)

    @classmethod
    def organizer(cls):
        """Este método retorna uma lista/iterador de objetos utilizados para desambiguar eventos numa mesma validade.
        Ex: S1010 pode ter vários eventos para uma mesma rúbrica na mesma validade em tabelas diferentes.
        Este método deve ser sobrescrito em cada evento que possuir esta característica.
        De forma comum será retornado [1] apenas para gerar um único evento.

        Returns:
            list/iterador: lista/iterador de objetos, default [1]."""
        return cls.EXTRACTOR.TAB_RUBR_BY_SUSPENSION.values()

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
                    start_validity__gt=extracted_event.start_validity
                )
                .filter(
                    oid=self.EXTRACTOR._get_oid(instance_outside, organizer=organizer)
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
        query = S1010.objects.valids_by_status()

        if filter_query_instance:
            filter_query_instance = Q(
                ide_rubrica_cod_rubr=filter_query_instance.deconstruct()[2].get(
                    "numero"
                )
            )
            query = query.filter(filter_query_instance)

        for event in query.exclude(oid__in=oids):
            """Caso evento não exista nos limites informados, verifica se existe em seus próprios limites."""
            params = {
                "event": event,
                "start_validity": None,
                "end_validity": None,
                "task": task,
                "oid": event.oid,
            }
            extractor_event = self.extractor(event.entry, **params)
            if not extractor_event.check_reference_strong():
                """Caso também não exista nos seus limites, será candidato a exclusão."""
                self.extractors_event_exclude.update({event.pk: extractor_event})

    def _next_start_limit(
        self, extracted_event, instance_outside, start_limit, organizer=None
    ):
        """Define start_limit em função do evento extraído"""
        return self._next_day(instance_outside, start_limit, organizer=organizer)

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        list_start_date = self.EXTRACTOR._queryset_date(
            instance_outside.numero, organizer=organizer
        )
        rs = min(filter(lambda x: date and x > date, list_start_date), default=None)
        return rs

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        """Este método retorna o data de limite inicial. Por padrão baseia-se no máximo entre start_limit e cls.initial_group_date()."""
        list_start_date = self.EXTRACTOR._queryset_date(
            instance_outside.numero, organizer=organizer
        )
        # return max(filter(lambda x: x is not None, [start_limit, self.initial_group_date()]))
        return min(list_start_date)

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        end_validity = self._next_day(
            instance_outside, date=start_limit, organizer=organizer
        )
        if end_validity:
            end_validity -= relativedelta(days=1)
            end_validity = NewDateRange.from_month(
                end_validity.year, end_validity.month
            ).last
        return end_validity

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
            ide_rubrica_cod_rubr=oid
        )

    def delete_xsd_schema_invalid(self, oid, registry=None, registry_person=None):
        """Este método apaga os não validados.

        Args:
            oid (int):
            registry (int):
            registry_person (str):
        """
        query = self.extracted_class.objects.not_validated().filter(
            ide_rubrica_cod_rubr=oid
        )
        for event in query:
            event.delete()


def type_suspensions_tab_rubr(organizer):
    def _find_key():
        for k, v in S1010Extractor.TAB_RUBR_BY_SUSPENSION.items():
            if v == organizer:
                return k
        return ""

    return set(filter(lambda value: value and value != "", _find_key().split(",")))
