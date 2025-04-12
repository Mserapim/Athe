# -.- coding: utf-8 -.-

from datetime import datetime

from django.db.models import Q

from contrib.utils import getLogger
from esocial.extractors.base import Factory
from esocial.extractors.s2410 import S2410Extractor
from esocial.models import S2420
from rh.const import TYPE_BY_POSSESSION_BENEFICIARY
from rh.models import MovimentacaoDesligamento

log = getLogger(__name__)


class S2420Extractor(S2410Extractor):

    def __init__(self, instance_outside, *args, **kwargs):
        super(S2420Extractor, self).__init__(instance_outside, *args, **kwargs)

    def _define_references(self):
        """define as queries dos objetos de referência válidos"""
        references = []
        start_validity = None
        end_validity = None
        if self.check_reference_strong():
            start_validity = self._instance_outside.data_desligamento
            references = self._references()

        return start_validity, end_validity, references

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        start_validity = kwargs.get("start_limit", None)
        benefit_movement = instance_outside.movimentacao_posse.benefitmovement
        return f"{benefit_movement.benefit_number}-{start_validity}"

    def _references(self):
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

    def ide_beneficio_cpf_benef(self):
        return self.beneficiario_cpf_benef()

    def ide_beneficio_nr_beneficio(self):
        return self.info_ben_inicio_nr_beneficio(
            self._instance_outside.movimentacao_posse.benefitmovement
        )

    def info_ben_termino_dt_term_beneficio(self):
        if self._instance_outside.data_desligamento <= datetime.now().date():
            return self._instance_outside.data_desligamento
        return None

    def info_ben_termino_mtv_termino(self):
        if hasattr(self._instance_outside.movimentacao_posse, "benefitmovement"):
            return (
                self._instance_outside.movimentacao_posse.benefitmovement.termination_reason.code
            )
        return None

    def info_ben_termino_cnpj_orgao_suc(self):
        if hasattr(self._instance_outside.movimentacao_posse, "benefitmovement"):
            benefit_movement = self._instance_outside.movimentacao_posse.benefitmovement
            if self.info_ben_termino_mtv_termino() == "09" and hasattr(
                benefit_movement.after_organ, "pessoa_juridica"
            ):
                return benefit_movement.pessoa_juridica.cnpj
        return None

    def info_ben_termino_novo_cpf(self):
        return None


class S2420Factory(Factory):

    EXTRACTED_MODEL_CLASS = S2420
    EXTRACTOR = S2420Extractor

    @classmethod
    def _query_instances_outside(cls, **kwargs):
        """Este método retorna um queryset dos objetos que darão origem a uma extração.

        Returns:
            queryset: default Event.objects.none()
        """
        today = datetime.now().date()
        query = MovimentacaoDesligamento.objects.filter(
            Q(servidor__type_by_possession__in=TYPE_BY_POSSESSION_BENEFICIARY)
            & Q(data_desligamento__lte=today)
        ).exclude(data_desligamento__lt=cls.initial_group_date())

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

    @classmethod
    def _get_start_limit(cls, instance_outside, start_limit=None, organizer=None):
        return instance_outside.data_desligamento

    @classmethod
    def _get_end_limit(cls, instance_outside, start_limit=None, organizer=None):
        return start_limit

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
        oid = oid.split("-")[0]
        return self.extracted_class.objects.can_exclude().filter(oid__icontains=oid)
