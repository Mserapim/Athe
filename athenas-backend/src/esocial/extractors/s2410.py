# -.- coding: utf-8 -.-
from contrib.daterange import NewDateRange
from esocial.const import PROCESS_STATUS_EVENT_SENT
from esocial.extractors.base import Extractor, Factory
from esocial.models import S2410, S2420, Configuration
from rh.const import MASS_SEGREGATION_PLAN
from rh.models import BenefitMovement, SocialSecurityEmployee
from rh.models import MovimentacaoAposentadoria

PENSION_DEATH = ("0601", "0602", "0603", "0604", "0807", "0808", "0812", "1105", "1106")


class S2410Extractor(Extractor):

    VALIDITY_FIELDS = ["info_ben_inicio_dt_ini_beneficio"]

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2410Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self.check_reference_strong():
            _references_strong_start_date = self._references_strong_start_date()
            if _references_strong_start_date:
                start_validity = max(_references_strong_start_date)

                references = self._references()

                """definindo o fim com a data de desligamento"""
                _references_strong_end_date = self._references_strong_end_date(
                    start_validity=start_validity
                )
                if _references_strong_end_date:
                    end_validity = min(_references_strong_end_date)
        return start_validity, end_validity, references

    def _references_strong_end_date(self, start_validity=None):
        rs = []
        exercise_date = self._instance_outside.data_exercicio
        termination_date = self._instance_outside.data_desligamento
        if (
            exercise_date <= self.initial_group_date()
            and termination_date
            and termination_date <= self.initial_group_date()
        ):
            rs = [self.initial_group_date(), termination_date]
        elif not self._event or (
            self._event and self._event.process_status not in PROCESS_STATUS_EVENT_SENT
        ):
            if (
                termination_date
                and termination_date.year == exercise_date.year
                and termination_date.month == exercise_date.month
            ):
                rs = [termination_date]
        return rs

    def registry_employee(self):
        registry = None
        employee_benefit = Configuration.current_config().employee_benefit.filter()
        filter_benefit = employee_benefit.filter(
            pessoa_fisica__cpf=self._instance_outside.servidor.pessoa_fisica.cpf
        )
        if filter_benefit.exists():
            registry = str(filter_benefit.first().matricula)
        else:
            registry = str(self._instance_outside.servidor.matricula)
        return registry

    def oid(self):
        return self._get_oid(self._instance_outside, start_limit=self._start_validity)

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        start_validity = kwargs.get("start_limit", "")
        return f"{instance_outside.benefit_number}-{start_validity}"

    def _references(self, start_validity=None):
        return self._references_strong(start_validity)

    def _references_strong(self, start_validity=None):
        return [self._instance_outside]

    def _references_strong_start_date(self):
        return [self.initial_group_date(), self._instance_outside.data_exercicio]

    @classmethod
    def _queryset_date(cls, instance_outside):
        return [instance_outside.data_exercicio]

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return (
            self._instance_outside and self._instance_outside.data_exercicio is not None
        )

    def registry_person(self):
        return self.beneficiario_cpf_benef()

    def tp_beneficio_code(self):
        return self._instance_outside.benefit_role.code

    def beneficiario_cpf_benef(self):
        return self._instance_outside.servidor.pessoa_fisica.cpf

    def beneficiario_matricula(self):
        tp_beneficio = self.tp_beneficio_code()
        if tp_beneficio in PENSION_DEATH:
            return str(self._instance_outside.founder_employee.matricula)

        if self.info_ben_inicio_cad_ini() == "N" and tp_beneficio[0:2] in (
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "11",
        ):
            return str(self._instance_outside.servidor.matricula)

        return None

    def beneficiario_cnpj_origem(self):
        return self.configuration.ide_employer_nr_insc

    def info_ben_inicio_cad_ini(self):
        return (
            "S"
            if self._instance_outside.data_exercicio < self.initial_group_date()
            else "N"
        )

    def info_ben_inicio_ind_sit_benef(self):
        return (
            self._instance_outside.situation
            if self.info_ben_inicio_cad_ini() == "N"
            else None
        )

    def info_ben_inicio_nr_beneficio(self, instance_outside=None):
        if not instance_outside:
            instance_outside = self._instance_outside
        return instance_outside.benefit_number

    def info_ben_inicio_dt_ini_beneficio(self):
        if self.info_ben_inicio_cad_ini() == "S":
            return self._instance_outside.data_exercicio
        return self.start_validity()

    def info_ben_inicio_dt_public(self):
        dt_publication = self._instance_outside.publicacao_movimentacao.data_publicacao
        if dt_publication:
            if (
                dt_publication
                > self._instance_outside.publicacao_movimentacao.data_vigencia
                and dt_publication > self.info_ben_inicio_dt_ini_beneficio()
            ):
                return dt_publication
        return None

    def dados_beneficio_tp_beneficio(self):
        tp_beneficio = self.tp_beneficio_code()
        if self.info_ben_inicio_cad_ini() == "N":
            if tp_beneficio in (
                "0801",
                "0802",
                "0803",
                "0804",
                "0805",
                "0806",
                "0807",
                "0808",
                "0809",
                "0810",
                "0811",
                "0812",
            ):
                return None

        return tp_beneficio

    def dados_beneficio_tp_plan_rp(self):
        ss = self.social_security_employee()
        return (
            MASS_SEGREGATION_PLAN.get(ss.social_security_config.mass_segregation_plan)
            if ss
            else None
        )

    def dados_beneficio_dsc(self):
        if self.tp_beneficio_code() in ["0909", "1001", "1009"]:
            return (
                self._instance_outside.texto[:255]
                if self._instance_outside.texto
                else ""
            )
        return None

    def dados_beneficio_ind_dec_jud(self):
        return "S" if self._instance_outside.judicial_decision else "N"

    def info_pen_morte_tp_pen_morte(self):
        if self.tp_beneficio_code() in PENSION_DEATH:
            return self._instance_outside.type_pension_death
        return None

    def inst_pen_morte_cpf_inst(self):
        tp_beneficio = self.tp_beneficio_code()
        if tp_beneficio in PENSION_DEATH:
            return self._instance_outside.founder_employee.pessoa_fisica.cpf
        return None

    def inst_pen_morte_dt_inst(self):
        tp_beneficio = self.tp_beneficio_code()
        if tp_beneficio in PENSION_DEATH:
            return self._instance_outside.founder_employee.pessoa_fisica.data_obito
        return None

    def sucessao_benef_cnpj_orgao_ant(self):
        if self.info_ben_inicio_ind_sit_benef() == 2:
            previous_organ = self._instance_outside.previous_organ
            return (
                previous_organ.pessoa_juridica.cnpj
                if hasattr(previous_organ, "pessoa_juridica")
                else None
            )
        return None

    def sucessao_benef_nr_beneficio_ant(self):
        if self.info_ben_inicio_ind_sit_benef() == 2:
            return self._instance_outside.previous_benefit_number
        return None

    def sucessao_benef_dt_transf(self):
        if self.info_ben_inicio_ind_sit_benef() == 2:
            return self._instance_outside.tranfer_date
        return None

    def sucessao_benef_observacao(self):
        return None

    def mudanca_cpf_cpf_ant(self):
        return None

    def mudanca_cpf_nr_beneficio_ant(self):
        return None

    def mudanca_cpf_dt_alt_cpf(self):
        return None

    def mudanca_cpf_observacao(self):
        return None

    def info_ben_termino_dt_term_beneficio(self):
        if self._instance_outside.data_desligamento:
            if self.info_ben_inicio_cad_ini() == "S":
                if self._instance_outside.data_desligamento < self.initial_group_date():
                    return self._instance_outside.data_desligamento
        return None

    def info_ben_termino_mtv_termino(self):
        if (
            self.info_ben_termino_dt_term_beneficio()
            and self._instance_outside.termination_reason
        ):
            if self._instance_outside.termination_reason.code not in ["09", "10"]:
                return self._instance_outside.termination_reason.code
        return None

    def social_security_employee(self):
        validity = self._start_validity
        if self._end_validity and self._end_validity < self.initial_group_date():
            validity = self._end_validity
        if validity:
            return (
                SocialSecurityEmployee.objects.currents_in(
                    range=NewDateRange(validity, validity)
                )
                .filter(employee=self._instance_outside.servidor)
                .last()
            )
        return None


class S2410Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2410
    EXTRACTOR = S2410Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = BenefitMovement.objects.filter(
            reactivated_benefit__isnull=True
        ).exclude(
            data_desligamento__isnull=False,
            data_desligamento__lt=cls.initial_group_date(),
        )

        return query

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

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_exercicio

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_desligamento

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        return None

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid."""
        oid = oid.split("-")[0]
        return self.extracted_class.objects.valids_by_status().filter(
            oid__icontains=oid
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
                    oid=self._get_oid(
                        instance_outside, start_limit=extracted_event.start_validity
                    )
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

    def _query_delete_not_send(self, oid=None, registry=None, registry_person=None):
        """Este método gera a queryset dos eventos que podem ser excluídos. Utiliza a queryset can_exclude como default.
        Aplicando os parâmetros no filter como AND.

        Args:
            oid (int):
            registry (int):
            registry_person (str):

        Returns:
            queryset."""
        oid = oid.split("-")[0]
        return self.extracted_class.objects.can_exclude().filter(oid__icontains=oid)

    def delete_not_send(self, oid=None, registry=None, registry_person=None):
        oid = oid.split("-")[0]
        for event in S2420.objects.can_exclude().filter(oid__icontains=oid):
            event.delete()
        super().delete_not_send(
            oid=oid, registry=registry, registry_person=registry_person
        )
