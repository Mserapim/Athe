# -.- coding: utf-8 -.-
from esocial.const import DIFF_VALIDITY_END, NOTHING_TODO, PROCESS_STATUS_EVENT_SENT
from esocial.extractors.base import Factory
from esocial.extractors.registrationbaseworker import WorkerBaseExtractor
from esocial.models import S2400, Configuration
from rh.const import TYPE_BY_POSSESSION_BENEFICIARY
from rh.models import Servidor


class S2400Extractor(WorkerBaseExtractor):

    VALIDITY_FIELDS = ["beneficiario_dt_inicio"]

    EXCLUDE_FIELDS_EQUALS = [
        "beneficiario_cpf_benef",
        "beneficiario_nm_benefic",
        "beneficiario_dt_nascto",
        "beneficiario_sexo",
        "beneficiario_raca_cor",
        "beneficiario_est_civ",
        "brasil_dsc_lograd",
        "brasil_complemento",
        "brasil_uf",
        "exterior_pais_resid",
        "exterior_dsc_lograd",
        "exterior_nr_lograd",
        "exterior_complemento",
        "brasil_nr_lograd",
        "brasil_bairro",
        "brasil_cep",
        "brasil_tp_lograd",
        "brasil_cod_munic",
        "exterior_bairro",
        "exterior_nm_cid",
        "exterior_cod_postal",
    ]

    def __init__(self, *args, **kwargs):
        super(S2400Extractor, self).__init__(*args, **kwargs)

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

    def _references(self):
        """define as queries dos objetos de referência válidos"""
        return self._references_strong()

    def _references_strong(self, start_validity=None):
        """define as queries dos objetos de referência válidos"""
        return [self._instance_outside]

    def _references_strong_start_date(self):
        return [self.initial_group_date(), self._instance_outside.exercise_date]

    def _references_strong_end_date(self, start_validity=None):
        rs = []
        exercise_date = self._instance_outside.exercise_date
        termination_date = self._instance_outside.termination_date
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
        if not diffs_content and diff_validity == DIFF_VALIDITY_END:
            return NOTHING_TODO
        return None

    def check_reference_strong(self):
        """Este método verifica se existe uma referência forte para self._start_validity. Retorna True quando existir."""
        return self._instance_outside.exercise_date is not None

    def registry_person(self):
        return self.beneficiario_cpf_benef()

    def start_validity(self):
        return self._start_validity

    def end_validity(self):
        return self._end_validity

    def beneficiario_cpf_benef(self):
        return self.trabalhador_cpf_trab()

    def beneficiario_nm_benefic(self, instance_outside=None):
        return self.trabalhador_nm_trab(instance_outside)

    def beneficiario_dt_nascto(self):
        return self.nascimento_dt_nascto()

    def beneficiario_dt_inicio(self):
        exercise_date = self._instance_outside.exercise_date
        if exercise_date < self.initial_group_date():
            return self.initial_group_date()
        return exercise_date

    def beneficiario_sexo(self, instance_outside=None):
        return self.trabalhador_sexo(instance_outside)

    def beneficiario_raca_cor(self, instance_outside=None):
        return self.trabalhador_raca_cor(instance_outside)

    def beneficiario_est_civ(self, instance_outside=None):
        return self.trabalhador_est_civ(instance_outside)

    def beneficiario_inc_fis_men(self):
        start_date = self.start_validity()
        if start_date < self.initial_group_date():
            start_date = self.initial_group_date()

        if self._instance_outside.molestia and (
            start_date >= self._instance_outside.molestia.data_laudo
        ):
            return "S"

        return "N"

    def beneficiario_dt_inc_fis_men(self):
        if self.beneficiario_inc_fis_men() == "S":
            return self._instance_outside.molestia.data_laudo
        return None


class S2400Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2400
    EXTRACTOR = S2400Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        query = Servidor.objects.by_type_possession(TYPE_BY_POSSESSION_BENEFICIARY)
        if not kwargs.get("dependency", False):
            query = query.exclude(
                termination_date__isnull=False,
                termination_date__lt=cls.initial_group_date(),
            ).exclude(
                matricula__in=Configuration.current_config()
                .employee_benefit_exclude.filter()
                .values_list("matricula", flat=True)
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
            query = query.filter(matricula=registry_employee)
        return query

    def _get_start_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.exercise_date

    def _get_end_limit(self, instance_outside, start_limit=None, organizer=None):
        return instance_outside.termination_date

    def _next_day(self, instance_outside, date=None, organizer=None):
        """Retorna o primeiro dia do próximo mês, que é o próximo dia de análise."""
        return None

    def _query_events_extracted(
        self, oid, start_limit, instance_outside, registry=None, registry_person=None
    ):
        """Este método retorna um queryset dos eventos válidos baseados em
        extracted_class através do oid."""
        return self.extracted_class.objects.valids_by_status().filter(oid=oid)

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
            registry_employee=registry
        )
