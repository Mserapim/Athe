# -*- coding: utf-8 -*-
import codecs
import copy
import importlib
import os
import shutil
import time
from datetime import date, datetime
from io import StringIO

import untangle
from celery import group
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Case, CharField, Count, F, Q, Value, When, Sum
from django.db.utils import IntegrityError
from django.forms.models import model_to_dict
from lxml import etree

from contrib.helpers import clear_to_ascii
from contrib.middleware import get_current_user
from contrib.utils import get_json_engine, getLogger
from engine.mq.models import Task
from esocial.const import (
    ACTION,
    ACTION_RECTIFICATION,
    ANYTIME,
    CAN_DELETE_EVENT_STATUS,
    CAN_SET_DELETED_EVENT_STATUS,
    CATEGORIA_EVENTO_CADASTRO,
    EVENTOS_CADASTRO,
    EXCLUSION,
    EXCLUSION_TYPE_DEFAULT,
    EXCLUSION_TYPE_S3000,
    INCLUSION,
    MANDATORY_IF_EXIST,
    MAP_TPPGTO_TO_DEMONSTRATIVE,
    MODIFICATION,
    PROCESS_STATUS_EVENT_NOT_SENT,
    PROCESS_STATUS_EVENT_SENT_ERROR,
    PROCESS_STATUS_EVENT_VALIDS_SENT,
    RECTIFICATION,
    VALID_EVENT_STATUS,
)
from esocial.managers.file_support import (
    _load_json_model,
    camel_to_snake,
    create_dir_batch,
    create_dir_event,
)
from esocial.managers.xml import (
    _validation_xml_schema,
    generate_xml_with_value,
    json_model_by_action,
)
from esocial.security.xml.manager import (
    XmlToSendTemplate,
    _load_data_file,
    _load_data_xml,
    _signer_process,
    _write_data_xml,
)
from esocial.tasks.utils import task_conflict_with_all
from esocial.utils import esocial_environment, get_acronyms_from_kind
from esocial.webservice import ClientSendEventBatch
from ged.models import Arquivo as GedFile
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import PessoaFisica as NaturalPerson
from rh.models import Servidor as Employee
from rh.models import UnidadeAdministrativa as AdministrativeUnit
from standard.models import AuditTimestampModel, Choice, ClassCode

json = get_json_engine()

log = getLogger(__name__)


XML_SCHEMA_PATH = "%s/esocial/data/schema" % settings.BASE_DIR


def get_current_config():
    return Configuration.current_config()


def task_info(task, msg="", type_of=1):
    """Este método encapsula a chamada de task.info(msg=msg, type_of=type_of) para evitar erros quando task=None.
    Quando não houver task, o método irá logar a mensagem de info.

    Args:
        task (mq.Task): _description_
        msg (str, optional): _description_. Defaults to ''.
        type_of (int, optional): _description_. Defaults to 1.

    Returns:
        bool: True, se task for diferente de None."""
    if task:
        task.info(msg=msg, type_of=type_of)
        return True
    log.info(f"{msg} - type_of {type_of}")
    return False


class ItemQuerySet(models.QuerySet):
    def all_choice_table(self, choice, table):
        return self.filter(esocial_table=table, choice__value=choice)

    def by_choice_table(self, choice, table):
        return self.get(esocial_table=table, choice__value=choice)

    def by_choicecv_table(self, choice, table):
        return self.get(esocial_table=table, choice__cvalue=choice)

    def by_info_choicecv_table(self, choice, table, info=""):
        return self.get(esocial_table=table, info=info, choice__cvalue=choice)

    def by_code_table(self, code, table):
        return self.get(esocial_table=table, code=code)

    def cnpj_type(self):
        return self.get(esocial_table=5, code="1")

    def worker_table(self):
        return self.get(esocial_table=9, code="S2200")

    def out_worker_table(self):
        return self.get(esocial_table=9, code="S2300")

    def validity_in(self, start_date, end_date=None):
        query = self.exclude(
            Q(end_validity__isnull=False) & Q(end_validity__lt=start_date)
        )
        if end_date:
            query = query.exclude(start_validity__gt=end_date)

        return query

    def get_by_natural_key(self, code, esocial_table, *args):
        return self.get(code=code, esocial_table=esocial_table)


class ItemTable(AuditTimestampModel):
    start_validity = models.DateField(
        verbose_name="Início vigência", null=True, blank=True
    )
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    code = models.CharField(max_length=7, verbose_name="Número")
    info = models.CharField(blank=True, default="", max_length=7, verbose_name="Número")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.CharField(
        max_length=800, verbose_name="Descrição", default="", blank=True
    )
    esocial_table = models.CharField(max_length=2, verbose_name="Tabela e-Social")
    choice = models.ManyToManyField(Choice, blank=True, related_name="items")

    objects = ItemQuerySet.as_manager()

    class Meta:
        unique_together = ("code", "esocial_table", "info")

    def __str__(self):
        return "Tabela {0}: {1}-{2}".format(self.esocial_table, self.code, self.title)

    def natural_key(self):
        return (self.code, self.esocial_table)

    @property
    def esocial_table_int(self):
        return int(self.esocial_table)


class RegistrationQualification(AuditTimestampModel):
    """Summary.

    Attributes:
        cod_cnis_cpf (TYPE): Description
        cod_cnis_cpf_nao_inf (TYPE): Description
        cod_cnis_dn (TYPE): Description
        cod_cnis_nis (TYPE): Description
        cod_cnis_obito (TYPE): Description
        cod_cpf_cancelado (TYPE): Description
        cod_cpf_dn (TYPE): Description
        cod_cpf_inv (TYPE): Description
        cod_cpf_nao_consta (TYPE): Description
        cod_cpf_nome (TYPE): Description
        cod_cpf_nulo (TYPE): Description
        cod_cpf_suspenso (TYPE): Description
        cod_dn_inv (TYPE): Description
        cod_nis_inv (TYPE): Description
        cod_nome_inv (TYPE): Description
        cod_orientacao_cpf (TYPE): Description
        cod_orientacao_nis (TYPE): Description
        cpf (TYPE): Description
        dn (TYPE): Description
        info (TYPE): Description
        last_modified_person_at (TYPE): Description
        last_modified_person_by (TYPE): Description
        last_qualification_at (TYPE): Description
        last_qualification_by (TYPE): Description
        natural_person (TYPE): Description
        nis (TYPE): Description
        nome (TYPE): Description
        qualified (TYPE): Description
        reg_desformatado (TYPE): Description
        return_file (TYPE): Description
        separador (TYPE): Description
        status (TYPE): Description
        type_of_last_qualification (TYPE): Description
        type_of_person (TYPE): Description

    Deleted Attributes:
        last_qualification_online (TYPE): Description
    """

    DEFAULT_USER = "athenas"

    AUDITABLE = {
        "fields": [
            "cpf",
            "nis",
            "nome",
            "dn",
            "cod_cpf_inv",
            "cod_nis_inv",
            "cod_nome_inv",
            "cod_dn_inv",
            "cod_cnis_nis",
            "cod_cnis_dn",
            "cod_cnis_obito",
            "cod_cnis_cpf",
            "cod_cnis_cpf_nao_inf",
            "cod_cpf_nao_consta",
            "cod_cpf_nulo",
            "cod_cpf_cancelado",
            "cod_cpf_suspenso",
            "cod_cpf_dn",
            "cod_cpf_nome",
            "separador",
            "reg_desformatado",
            "qualified",
            "status",
            "info",
            "cod_orientacao_cpf",
            "cod_orientacao_nis",
            "type_of_person",
            "natural_person",
            "employee",
        ]
    }

    natural_person = models.OneToOneField(
        NaturalPerson,
        related_name="qualification",
        verbose_name="Pessoa Física",
        on_delete=models.CASCADE,
    )
    employee = models.ForeignKey(
        "rh.Servidor",
        related_name="qualifications",
        verbose_name="Servidor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    cpf = models.CharField(max_length=11, null=True, blank=True, verbose_name="CPF")
    nis = models.CharField(max_length=11, null=True, blank=True, verbose_name="NIS*")
    nome = models.CharField(max_length=100, blank=True, verbose_name="Nome")
    dn = models.DateField(null=True, blank=True, verbose_name="Data nascimento")
    cod_cpf_inv = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_inv", blank=True
    )
    cod_nis_inv = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_nis_inv", blank=True
    )
    cod_nome_inv = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_nome_inv", blank=True
    )
    cod_dn_inv = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_dn_inv", blank=True
    )
    cod_cnis_nis = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cnis_nis", blank=True
    )
    cod_cnis_dn = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cnis_dn", blank=True
    )
    cod_cnis_obito = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cnis_obito", blank=True
    )
    cod_cnis_cpf = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cnis_cpf", blank=True
    )
    cod_cnis_cpf_nao_inf = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cnis_cpf_nao_inf", blank=True
    )
    cod_cpf_nao_consta = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_nao_consta", blank=True
    )
    cod_cpf_nulo = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_nulo", blank=True
    )
    cod_cpf_cancelado = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_cancelado", blank=True
    )
    cod_cpf_suspenso = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_suspenso", blank=True
    )
    cod_cpf_dn = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_cpf_dn", blank=True
    )
    cod_cpf_nome = models.CharField(
        max_length=100, default="", verbose_name="cod_cpf_nome", blank=True
    )
    cod_orientacao_cpf = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_orientacao_cpf", blank=True
    )
    cod_orientacao_nis = models.PositiveSmallIntegerField(
        default=1, verbose_name="cod_orientacao_nis", blank=True
    )
    separador = models.PositiveSmallIntegerField(
        default=1, verbose_name="separador", blank=True
    )
    reg_desformatado = models.PositiveSmallIntegerField(
        default=1, verbose_name="reg_desformatado", blank=True
    )

    last_qualification_at = models.DateField(
        null=True, blank=True, verbose_name="Qualificado em"
    )
    last_qualification_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Qualificado por",
        related_name="+",
    )
    return_file = models.ForeignKey(
        GedFile, verbose_name="Arquivo", null=True, on_delete=models.CASCADE
    )
    last_modified_person_at = models.DateTimeField(
        blank=True, verbose_name="Modificado em"
    )
    last_modified_person_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        verbose_name="Modificado por",
        related_name="+",
        on_delete=models.CASCADE,
    )
    type_of_person = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("esocial", "TYPE_OF_PERSON")
    )
    qualified = models.BooleanField(verbose_name="Qualificado?", default=False)
    status = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("esocial", "STATUS_QUALIFICATION")
    )
    type_of_last_qualification = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("esocial", "TYPE_QUALIFICATION")
    )
    info = models.TextField(blank=True, verbose_name="Info", default="")

    default_nis = "13333333332"

    ERRORS = {
        "COD_NIS_INV": {0: "OK", 1: "NIS inválido"},
        "COD_CPF_INV": {0: "OK", 1: "CPF inválido"},
        "COD_NOME_INV": {0: "OK", 1: "NOME inválido"},
        "COD_DN_INV": {0: "OK", 1: "DN inválida"},
        "COD_CNIS_NIS": {0: "OK", 1: "NIS inconsistente"},
        "COD_CNIS_DN": {
            0: "OK",
            1: "Data de Nascimento informada diverge da existente no CNIS",
        },
        "COD_CNIS_OBITO": {0: "OK", 1: "NIS com óbito no CNIS"},
        "COD_CNIS_CPF": {0: "OK", 1: "CPF informado diverge do existente no CNIS"},
        "COD_CNIS_CPF_NAO_INF": {0: "OK", 1: "CPF não preenchido no CNIS"},
        "COD_CPF_NAO_CONSTA": {0: "OK", 1: "CPF informado não consta o Cadastro CPF"},
        "COD_CPF_NULO": {0: "OK", 1: "CPF informado NULO no Cadastro CPF"},
        "COD_CPF_CANCELADO": {0: "OK", 1: "CPF informado CANCELADO no Cadastro CPF"},
        "COD_CPF_SUSPENSO": {0: "OK", 1: "CPF informado SUSPENSO no Cadastro CPF"},
        "COD_CPF_DN": {
            0: "OK",
            1: "Data de Nascimento informada diverge da existente no Cadastro CPF",
        },
        "COD_CPF_NOME": {
            0: "OK",
            1: "NOME informado diverge do existente no Cadastro CPF ({nome}). \
                            Obs: Informa o nome que consta no CPF.",
        },
        "SEPARADOR": {0: "OK", 1: 'Separador Inválido. Deve ser ";"'},
        "REG_DESFORMATADO": {0: "OK", 1: "Formatação inválida"},
        "COD_ORIENTACAO_CPF": {
            0: "OK",
            1: "Procurar Conveniadas da RFB: Correios, Banco do Brasil ou CAIXA.",
        },
        "COD_ORIENTACAO_NIS": {
            0: "OK",
            1: "Atualizar NIS no INSS – Ligar 135 para agendar atendimento",
            2: "Atualizar o Cadastro NIS/PIS da CAIXA – Utilizar Cadastro NIS Empresa pelo conectividade Social ou uma \
                agência da CAIXA",
            3: "Atualizar o Cadastro NIS/PASEP em uma agência do Banco do Brasil.",
        },
    }

    class Meta:
        """Meta.

        Attributes:
            ordering (tuple): Description
        """

        ordering = ("status", "-last_qualification_at", "natural_person")

    def set_unqualified(self):
        self.cod_cpf_inv = 1
        self.cod_nis_inv = 1
        self.cod_nome_inv = 1
        self.cod_dn_inv = 1
        self.cod_cnis_nis = 1
        self.cod_cnis_dn = 1
        self.cod_cnis_obito = 1
        self.cod_cnis_cpf = 1
        self.cod_cnis_cpf_nao_inf = 1
        self.cod_cpf_nao_consta = 1
        self.cod_cpf_nulo = 1
        self.cod_cpf_cancelado = 1
        self.cod_cpf_suspenso = 1
        self.cod_cpf_dn = 1
        self.cod_cpf_nome = ""
        self.cod_orientacao_cpf = 1
        self.cod_orientacao_nis = 1
        self.separador = 1
        self.reg_desformatado = 1
        self.qualified = False
        self.status = 1
        self.info = ""

    def update_info(self):
        info = ""
        orientation = ""

        keys = []
        if self.status == 4:
            keys = [
                "COD_NIS_INV",
                "COD_CPF_INV",
                "COD_NOME_INV",
                "COD_DN_INV",
                "SEPARADOR",
                "REG_DESFORMATADO",
            ]
        elif self.status == 3:
            keys = list(self.ERRORS)
            keys.remove("SEPARADOR")
            keys.remove("REG_DESFORMATADO")

        for k in keys:
            if k == "COD_CPF_NOME":
                if getattr(self, k.lower()) != "0":
                    nome = self.cod_cpf_nome.replace("1 - ", "")
                    info += "<p>>%s</p>" % self.ERRORS[k][1].format(nome=nome)
            elif getattr(self, k.lower()) != 0:
                if k in ["COD_ORIENTACAO_CPF", "COD_ORIENTACAO_NIS"]:
                    orientation += "<p><b>%s</b></p>" % self.ERRORS[k].get(
                        getattr(self, k.lower())
                    )
                else:
                    info += "<p>>%s</p>" % (
                        self.ERRORS[k].get(getattr(self, k.lower()))
                    )
        if orientation:
            info += "<br /><p>Orientação:</p>" + orientation

        return info

    def save(self, *args, **kwargs):
        """Sobrescrita do save para preencher dados iniciais.

        Args:
            *args: Description
            **kwargs: Description
        """
        if not self.pk:
            self.last_modified_person_at = self.natural_person.modified_at
            self.last_modified_person_by = self.natural_person.modified_by
            query_nis = self.natural_person.documento.filter(tipo_documento__in=(5, 6))
            self.nis = query_nis.first().numero[0:11] if query_nis else ""
            self.cpf = self.natural_person.cpf[0:11] if self.natural_person.cpf else ""
            self.dn = self.natural_person.data_nascimento
            self.nome = clear_to_ascii(self.natural_person.nome)

        if not self.cpf:
            self.status = 2
        log.debug("CPF: %s STATUS: %s" % (self.cpf, self.status))

        if (
            self.cod_orientacao_cpf == self.separador == self.reg_desformatado == 0
            and (self.cod_orientacao_nis == 0 or self.type_of_person in (3, 5, 6))
        ):

            self.status = 10  # QUALIFICADO
            self.info = ""
        else:
            self.info = self.update_info()

        self.qualified = True if self.status == 10 else False

        super(RegistrationQualification, self).save(*args, **kwargs)


class Configuration(AuditTimestampModel):

    environment = models.PositiveSmallIntegerField(
        verbose_name="Ambiente",
        default=2,
        choices=Choice.get_choices_for("esocial", "ENVIRONMENT"),
    )
    layout_version = models.CharField(verbose_name="Versão do layout", max_length=20)
    ws_batch_submission = models.CharField(
        default="", blank=True, max_length=200, verbose_name="Web Service - Envio"
    )
    ws_batch_consult_process = models.CharField(
        default="", blank=True, max_length=200, verbose_name="Web Service - Consulta"
    )
    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    cut_off_date_s2231 = models.DateField(
        "Data de corte s2231",
        default=datetime(2022, 1, 1).date(),
        null=True,
        blank=True,
    )
    employer = models.ForeignKey(
        AdministrativeUnit,
        on_delete=models.CASCADE,
        verbose_name="Órgão empregador",
        related_name="configuration_employer",
    )
    responsible = models.ForeignKey(
        NaturalPerson,
        on_delete=models.CASCADE,
        verbose_name="Responsável para ESOCIAL",
        related_name="configuration_responsible",
    )
    responsible_software_house = models.ForeignKey(
        NaturalPerson,
        on_delete=models.CASCADE,
        verbose_name="Responsável software house",
        related_name="configuration_responsible_software_house",
    )
    xml_send_schema_name = models.CharField(
        "Nome do Schema de Envio", max_length=50, blank=True, null=True
    )
    xmlns_send = models.CharField(
        default="", blank=True, max_length=200, verbose_name="Url de Envio"
    )
    xml_consult_schema_name = models.CharField(
        "Nome do Schema de Consulta", max_length=50, blank=True, null=True
    )
    xmlns_consult = models.CharField(
        default="", blank=True, max_length=200, verbose_name="Url de Consulta"
    )
    initial_date_start_tables = models.DateField(
        verbose_name="Início - Tabelas iniciais"
    )
    initial_date_non_periodic_events = models.DateField(
        verbose_name="Início - Não periódicos"
    )
    initial_date_periodic_events = models.DateField(verbose_name="Início - Periódicos")
    initial_date_sst_events = models.DateField(
        "Início - Segurança e Saúde no Trabalho", default=datetime(2020, 5, 1)
    )
    queue_send = models.BooleanField(verbose_name="Fila de envio?", default=True)
    generate_events = models.ManyToManyField(
        Choice,
        verbose_name="Eventos que serão gerados",
        related_name="esocial_configuration_generate_events",
    )
    interrupt_batch_events = models.ManyToManyField(
        Choice,
        verbose_name="Eventos que não serão enviados",
        related_name="esocial_configuration_interrupt_batch_events",
    )
    employee_filter = models.ManyToManyField(
        "rh.Servidor",
        verbose_name="Servidores que serão filtrados na geração",
        related_name="employeefilter_esocialconfiguration",
    )
    employee_exclude = models.ManyToManyField(
        "rh.Servidor",
        verbose_name="Servidores que serão excluídos da geração",
        related_name="employeeexclude_esocialconfiguration",
    )
    employee_benefit = models.ManyToManyField(
        "rh.Servidor",
        verbose_name="Matriculas escolhidas em casos de beneficiários com mais de um beneficio",
        related_name="employeebenefit_esocialconfiguration",
    )
    employee_benefit_exclude = models.ManyToManyField(
        "rh.Servidor",
        verbose_name="Matriculas excluidas em casos de beneficiários com mais de um beneficio",
        related_name="employebenefitexclude_esocialconfiguration",
    )
    certificado_a1 = models.ForeignKey(
        GedFile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuration_certificado_a1",
    )
    certificado_cas = models.ForeignKey(
        GedFile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="configuration_certificado_cas",
    )

    @property
    def ide_employer_tp_insc(self):
        return int(ItemTable.objects.cnpj_type().code)

    @property
    def ide_employer_nr_insc(self):
        return self.employer.pessoa_juridica.cnpj

    @property
    def ide_transmitter_tp_insc(self):
        return self.ide_employer_tp_insc

    @property
    def ide_transmitter_nr_insc(self):
        return self.employer.pessoa_juridica.cnpj

    def __str__(self):
        return "%s - %s" % (self.get_environment_display(), self.layout_version)

    @classmethod
    def _query_by_keys(cls, **keys):
        q_objects = cls.objects.all()
        if keys:
            q_objects = q_objects.filter(**keys)
        return q_objects

    @classmethod
    def get_currents(cls, start_date=None, end_date=None, **keys):
        start_date = datetime.now().date() if not start_date else start_date
        end_date = start_date if not end_date else end_date

        q_objects = cls._query_by_keys(**keys).exclude(
            models.Q(start_validity__gt=end_date)
            | (
                models.Q(end_validity__isnull=False)
                & models.Q(end_validity__lt=start_date)
            )
        )

        return q_objects

    @classmethod
    def current_config(cls):
        return cls.get_currents(environment=esocial_environment()).first()

    @classmethod
    def current_prod(cls):
        return cls.get_currents(environment=1).first()

    @classmethod
    def current_homolog(cls):
        return cls.get_currents(environment=2).first()

    def save(self, *args, **kwargs):
        super(Configuration, self).save(*args, **kwargs)


class BatchEventManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(environment=esocial_environment())


class BatchEventAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class BatchEventQuerySet(models.QuerySet):
    def delete(self):
        Event.objects.filter(batches__in=self).update(process_status=1)
        return super(BatchEventQuerySet, self).delete()


class BatchEvent(AuditTimestampModel):

    class Meta:
        ordering = ("-delivery_date", "group", "created_at")

    group = models.PositiveIntegerField(verbose_name="Grupo", default=1)
    description = models.CharField(max_length=255, null=True, blank=True)
    application = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "APPLICATION"), default=1
    )
    delivery_receipt = models.CharField(max_length=255, null=True, blank=True)
    delivery_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="event_batch_user",
        verbose_name="Usuário",
        null=True,
        blank=True,
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_version_app = models.CharField(max_length=20)
    delivery_status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "DELIVERY_STATUS_BATCH"), default=1
    )
    process_date = models.DateTimeField(null=True, blank=True)
    process_version_app = models.CharField(max_length=20)
    process_status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "PROCESS_STATUS_BATCH"), default=101
    )
    xsd_schema_validated = models.BooleanField(verbose_name="Validado", default=False)
    xmlns = models.CharField(max_length=256)
    environment = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )
    archived = models.BooleanField(verbose_name="Arquivado", default=False)
    success_events_cache = models.BooleanField(verbose_name="Sucesso", default=False)

    objects = BatchEventManager.from_queryset(BatchEventQuerySet)()
    objects_all = BatchEventAllManager().from_queryset(BatchEventQuerySet)()

    def __init__(self, *args, **kwargs):
        self._file_directory = None
        self._file_path = None
        self._file_path_signed = None
        self._file_path_result = None
        self._file_path_process = None
        self._file_name = None
        self._xml = None
        self._xml_signed = None
        self._xml_schema = None
        self._file_path_xml_schema = None
        super(BatchEvent, self).__init__(*args, **kwargs)

    def __str__(self):
        return "%s.%s.%s" % ("E" if self.application == 1 else "R", self.group, self.pk)

    @property
    def xml_schema(self):
        if not self._xml_schema:
            with codecs.open(self.file_path_xml_schema, "r") as schema:
                self._xml_schema = schema.read()
        return self._xml_schema

    @property
    def file_path_xml_schema(self):
        configuration = get_current_config()
        if not self._file_path_xml_schema:
            self._file_path_xml_schema = "%s/%s" % (
                XML_SCHEMA_PATH,
                configuration.xml_send_schema_name,
            )
        return self._file_path_xml_schema

    @property
    def file_directory(self):
        if not self._file_directory:
            self._file_directory = create_dir_batch(self)
        return self._file_directory

    @property
    def file_name(self):
        if not self._file_name:
            self._file_name = "batch.xml"
        return self._file_name

    @property
    def file_path(self):
        if not self._file_path:
            self._file_path = "%s/%s" % (self.file_directory, self.file_name)
        return self._file_path

    @property
    def file_path_signed(self):
        if not self._file_path_signed:
            self._file_path_signed = "%s/%s" % (
                self.file_directory,
                self.file_name.replace(".xml", "-signed.xml"),
            )
        return self._file_path_signed

    @property
    def file_path_result(self):
        if not self._file_path_result:
            self._file_path_result = "%s/%s" % (
                self.file_directory,
                self.file_name.replace(".xml", "-result.xml"),
            )
        return self._file_path_result

    @property
    def file_path_process(self):
        if not self._file_path_process:
            self._file_path_process = "%s/%s" % (
                self.file_directory,
                self.file_name.replace(".xml", "-process.xml"),
            )
        return self._file_path_process

    @property
    def xml(self):
        if not os.path.exists(self.file_path):
            self._xml = self.generate_xml_with_value()
        elif not self._xml:
            self._xml = _load_data_xml(self.file_path, encoding=None, to_string=False)
        return self._xml

    @property
    def xml_signed(self):
        if not os.path.exists(self.file_path_signed):
            self._xml_signed = self.signer()
        elif not self._xml_signed:
            self._xml_signed = _load_data_xml(
                self.file_path_signed, encoding=None, to_string=False
            )
        return self._xml_signed

    @property
    def success_events(self):
        if self.pk:
            return not self.events.exclude(process_status=201).exists()
        return False

    def _set_success_events_cache(self):
        self.success_events_cache = self.success_events

    def update_success_events_cache(self):
        if self.success_events != self.success_events_cache:
            self.save()

    def _set_xmlns(self):
        configuration = get_current_config()
        self.xmlns = configuration.xmlns_send

    def update_delivery_status(self, new_status=None, save=True):
        if new_status:
            self.delivery_status = new_status
        if self.diff and save:
            self.save()
        return self.delivery_status

    def save(self, *args, **kwargs):
        self._set_xmlns()
        self._set_success_events_cache()
        if not self.pk:
            self.environment = esocial_environment()
        super(BatchEvent, self).save(*args, **kwargs)

    def validate_delete(self):
        can_delete_status = (401, 402, 403, 404, 405)
        if self.process_status not in can_delete_status:
            raise Exception(
                f"Não é possível remover Lote com Status: {self.get_process_status_display()}"
            )
        return True

    def delete(self, *args, **kwargs):
        self.validate_delete()
        events = [pk for pk in self.events.values_list("pk", flat=True)]
        super(BatchEvent, self).delete(*args, **kwargs)
        for event in Event.objects.filter(pk__in=events):
            event = event.event
            event.update_status(new_status=1)

    def generate_xml_with_value(self):
        configuration = get_current_config()
        xml_to_send_templace = XmlToSendTemplate(
            events=self.events.filter(),
            xmlns=self.xmlns,
            grupo=str(self.group),
            ide_employer_tp_insc=str(configuration.ide_employer_tp_insc),
            ide_employer_nr_insc=configuration.ide_employer_nr_insc[0:8],
            ide_transmitter_tp_insc=str(configuration.ide_transmitter_tp_insc),
            ide_transmitter_nr_insc=configuration.ide_transmitter_nr_insc,
        ).dump(format_dump="element")
        _write_data_xml(xml_to_send_templace, self.file_path, pretty_print=True)
        self._write_xml_event_at_batch_directory()

        return xml_to_send_templace

    def _write_xml_event_at_batch_directory(self):
        for ev in self.events.all():
            event = ev.event
            _file_path = self.file_path.replace("batch.xml", event.file_name)
            event.xml
            if event.file_path != _file_path:
                shutil.move(event.file_path, _file_path)
                shutil.move(
                    event.file_path_signed, _file_path.replace(".xml", ".s.xml")
                )

    def signer(self):
        return _signer_process(self.xml, self.file_path_signed)

    def validation_xml_schema(self, assert_test=False):
        return _validation_xml_schema(
            self.xml_schema, self.file_path, assert_test=assert_test
        )

    def _set_delivery_return(self, xml_or_file_path=None):
        if xml_or_file_path is None:
            xml_or_file_path = self.file_path.replace(".xml", "-receipt.xml")
        xml_str = ""
        if isinstance(xml_or_file_path, str) and os.path.exists(xml_or_file_path):
            xml_str = StringIO(_load_data_file(xml_or_file_path))
        elif isinstance(xml_or_file_path, (etree._Element, etree._ElementTree)):
            xml_str = etree.tounicode(xml_or_file_path)

        if xml_str:
            xml_obj = untangle.parse(xml_str).eSocial.retornoEnvioLoteEventos
            self.delivery_status = int(xml_obj.status.cdResposta.cdata)
            success = self.delivery_status in PROCESS_STATUS_EVENT_VALIDS_SENT
            if success:
                receipt_obj = xml_obj.dadosRecepcaoLote
                try:
                    self.delivery_date = datetime.strptime(
                        receipt_obj.dhRecepcao.cdata, "%Y-%m-%dT%H:%M:%S.%f"
                    )
                except Exception as err:
                    log.exception(err)
                    self.delivery_date = datetime.now()
                    log.info(f"delivery_date - utilizando {self.delivery_date}")
                self.delivery_receipt = receipt_obj.protocoloEnvio.cdata
                self.delivery_version_app = receipt_obj.versaoAplicativoRecepcao.cdata
                self.delivery_user = get_current_user()
                self.process_status = 101
                self.save()

            result = self.results.create()
            result.set_delivery(success)

            status_event = 4 if success else 1
            for ev in self.events.all():
                ev = ev.event
                ev.update_status(status_event)

            for obj in getattr(xml_obj.status, "ocorrencias", []):
                log.debug(
                    "OCURRENCE: %s > %s"
                    % (obj.ocorrencia.codigo.cdata, obj.ocorrencia.descricao.cdata)
                )
                result.ocurrences.get_or_create(
                    environment=esocial_environment(),
                    code=int(obj.ocorrencia.codigo.cdata),
                    type_occurrence=int(obj.ocorrencia.tipo.cdata),
                    location=obj.ocorrencia.localizacao.cdata,
                    defaults={"description": obj.ocorrencia.descricao.cdata},
                )

    def send_to_esocial(self):
        if self.delivery_status in PROCESS_STATUS_EVENT_VALIDS_SENT:
            raise Exception("Lote não pode ser enviado novamente!")

        client = ClientSendEventBatch()
        xml_doc = self.xml.getroot()
        res = client.service.EnviarLoteEventos(loteEventos=xml_doc)
        etree_res = etree.ElementTree(res)
        etree_res.write(
            self.file_path.replace(".xml", "-receipt.xml"),
            encoding="utf-8",
            pretty_print=True,
        )
        self._set_delivery_return(res)

        return res

    def split_namespace(self, elem):
        return elem.tag.split("}")[1]

    def _evaluate_return_totalizers_data(
        self, class_totalizer, elem_totalizer, event_connection, task=None
    ):
        """Este método extrai o totalizador com seus relacionamentos de acordo com retorno do xml.

        Args:
            class_totalizer (Event.__class__): classe dos totalizadores (S5001, S5002, S5011, S5012, S5501)
            elem_totalizer (etree._Element):
            event_connection (Event): Event(S1200, S1202, S1210, S1299) que gerou a criação do totalizador
            task (mq.Task): task que está sendo executada

        Returns:
            instance_totalizer (Event): S5001, S5002, S5011, S5012, S5501
        """

        def evaluate_fields(obj_container, element, m2m_element_list=[]):
            """Este método extrai os atributos de obj_container, adicionando os campos simples e retornando uma lista de elementos m2m.

            Args:
                obj_container (Event):
                element (etree._Element):
                m2m_element_list (list):

            Returns:
                m2m_element_list (list):
            """
            for element_child in list(element):
                class_tag = (
                    self.split_namespace(element_child)[0].upper()
                    + self.split_namespace(element_child)[1:]
                )

                """Utiliza o MAP_CLASS_XML para converter o nome da tag do xml para o nome modelo."""
                class_tag = class_totalizer.MAP_CLASS_XML.get(class_tag, class_tag)

                m2m_fields = [
                    f.related_model.__name__
                    for f in obj_container._meta.get_fields()
                    if (f.many_to_many and not f.auto_created) or f.one_to_many
                ]
                if class_tag not in m2m_fields:
                    if len(list(element_child)) > 0:
                        evaluate_fields(obj_container, element_child, m2m_element_list)
                    else:
                        attribute = "{}_{}".format(
                            camel_to_snake(self.split_namespace(element)),
                            camel_to_snake(self.split_namespace(element_child)),
                        )
                        """Utiliza o MAP_FIELDS_XML para converter o attribute para o nome do campo."""
                        attribute = class_totalizer.MAP_FIELDS_XML.get(
                            attribute, attribute
                        )
                        setattr(obj_container, attribute, element_child.text)
                else:
                    if element_child not in m2m_element_list:
                        m2m_element_list.append(element_child)
            return m2m_element_list

        def evaluate_m2m(obj_container, element):
            """Este método extrai os atributos m2m de obj_container adicionando cada atributo encontrado, seja campo simples ou m2m.

            Args:
                obj_container (Event):
                element (etree._Element):
            """
            for child in element:
                class_tag = (
                    self.split_namespace(child)[0].upper()
                    + self.split_namespace(child)[1:]
                )
                """Utiliza o MAP_CLASS_XML para converter o nome da tag do xml para o nome modelo."""
                class_tag = class_totalizer.MAP_CLASS_XML.get(class_tag, class_tag)
                try:
                    _klass_m2m = eval(class_tag)
                except AttributeError as error:
                    log.exception(error)
                else:
                    obj_m2m = _klass_m2m()
                    obj_m2m.competence_month = obj_container.competence_month
                    obj_m2m.competence_year = obj_container.competence_year
                    obj_m2m.start_validity = obj_container.start_validity
                    m2m_element = evaluate_fields(obj_m2m, child, m2m_element_list=[])
                    exclude_list = [
                        f.name
                        for f in obj_m2m._meta.get_fields()
                        if f.many_to_many or f.name == "id"
                    ]

                    try:
                        obj_m2m = _klass_m2m.objects.get(
                            **model_to_dict(obj_m2m, exclude=exclude_list)
                        )
                    except (ObjectDoesNotExist, _klass_m2m.DoesNotExist):
                        obj_m2m.save()

                    if m2m_element:
                        evaluate_m2m(obj_m2m, m2m_element)

                    try:
                        _attr = "{}".format(camel_to_snake(obj_m2m.__class__.__name__))
                        """Utiliza o MAP_FIELDS_XML para converter o _attr para o nome do campo do m2m."""
                        _attr = class_totalizer.MAP_FIELDS_XML.get(_attr, _attr)
                        """Adiciona o m2m."""
                        obj_container.__getattribute__(_attr).add(obj_m2m)
                    except Exception as err:
                        log.exception(err)
                        if not task_info(
                            task,
                            msg=f"Erro ao tentar extrair totalizador {obj_container}.<br>{err}",
                            type_of=3,
                        ):
                            raise err

        def _nr_rec_arq_base(children):
            nr_rec_arq_base = None
            for child in children:
                if "nrRecArqBase" in child.attrib:
                    nr_rec_arq_base = child.attrib["nrRecArqBase"]
                    break
            return nr_rec_arq_base

        def evaluate_totalizer(el_totalizer):
            instance_totalizer = None
            if not isinstance(event_connection, (S2299, S2399)):
                try:
                    instance_totalizer = class_totalizer.objects.get(
                        identifier=el_totalizer.attrib["Id"]
                    )
                except ObjectDoesNotExist:
                    instance_totalizer = class_totalizer()
                    instance_totalizer.identifier = el_totalizer.attrib["Id"]

                    nr_rec_arq_base = _nr_rec_arq_base(list(el_totalizer))
                    if hasattr(instance_totalizer, "ide_evento_nr_rec_arq_base"):
                        instance_totalizer.ide_evento_nr_rec_arq_base = nr_rec_arq_base
                    elif hasattr(instance_totalizer, "info_cs_nr_rec_arq_base"):
                        instance_totalizer.info_cs_nr_rec_arq_base = nr_rec_arq_base

                instance_totalizer.sequential = datetime.now().strftime("%f")[-5:]
                instance_totalizer.event_connection = event_connection
                instance_totalizer.registry_employee = (
                    event_connection.registry_employee
                )
                instance_totalizer.registry_person = event_connection.registry_person
                instance_totalizer.competence_month = event_connection.competence_month
                instance_totalizer.competence_year = event_connection.competence_year
                instance_totalizer.start_validity = event_connection.start_validity
                instance_totalizer.process_status = 201
                instance_totalizer.description = f"ORIGEM: {event_connection.acronym.upper()} - {event_connection.description}"

                m2m_elements = evaluate_fields(instance_totalizer, el_totalizer)
                instance_totalizer.save()
                evaluate_m2m(instance_totalizer, m2m_elements)

                if isinstance(instance_totalizer, S5001):
                    instance_totalizer.update_from_info_cp_calc()
                elif isinstance(instance_totalizer, (S5002, S5012)):
                    instance_totalizer.update_from_tot_apur_men(task=task)
            return instance_totalizer

        return evaluate_totalizer(elem_totalizer)

    def extract_return_result_totalizers(self, xml_obj, totalizers=[], task=None):
        """Este método solicita extração/persistência de cada totalizador(S5001, S5002, S5011, S5012, S5501) encontrado em xml_obj.

        Args:
            xml_obj (etree._Element)
            totalizers (list, optional): Lista de totalizadores a serem extraídos. Defaults to [], realizará para todos extratores.
            task (mq.Task, optional): Task que está solicitando a extração. Defaults to None.
        """

        def write_xml(element, totalizer):
            if totalizer:
                xml_buff = f"Xml do totalizador {totalizer}"
                for el in element:
                    for el_new in list(el):
                        if (
                            el_new.tag
                            == "{http://www.w3.org/2000/09/xmldsig#}Signature"
                        ):
                            el.remove(el_new)
                    xml_buff = etree.tostring(el, pretty_print=True, encoding=str)

                with codecs.open(totalizer.file_path, "w") as event_xml:
                    event_xml.write(xml_buff)

                totalizer.xsd_schema_validated = totalizer.validation_xml_schema()
                totalizer.save()

        try:
            """Percorre todos os totalizadores do XML."""
            for element in xml_obj.findall(".//{*}tot"):
                identifier_event_connection = element.getparent().attrib["Id"]
                totalizer_type = element.attrib["tipo"]

                class_totalizer = None
                try:
                    class_totalizer = eval(totalizer_type)
                except NameError:
                    log.info(
                        f"!!!!!! >>>>> {totalizer_type} não é um totalizador. <<<<< !!!!!!"
                    )
                except Exception as err:
                    log.exception(err)
                    task_info(
                        task,
                        msg=f"Erro ao tentar extrair totalizador {totalizer_type}.<br>{err}",
                        type_of=3,
                    )

                """Verifica se o totalizador está na lista de totalizadores a serem extraídos."""
                if totalizers and totalizer_type.lower() not in totalizers:
                    class_totalizer = None
                    task_info(
                        task,
                        msg=f"Totalizador {totalizer_type} não está na lista de totalizadores a serem extraídos.",
                        type_of=1,
                    )

                if class_totalizer:
                    """Utiliza a definição do XML_SCHEMA_NAME para encontrar o totalizador no XML. É o nome do totalizador sem o .xsd"""
                    search = ".//{*}" + class_totalizer.XML_SCHEMA_NAME.replace(
                        ".xsd", ""
                    )
                    for elem_totalizer in element.findall(search):
                        """Encontra o evento de conexão."""
                        event_connection = self.events.filter(
                            identifier=identifier_event_connection
                        ).last()
                        if event_connection and event_connection.acronym != "s3000":
                            event_connection = event_connection.event
                            totalizer = self._evaluate_return_totalizers_data(
                                class_totalizer,
                                elem_totalizer,
                                event_connection,
                                task=task,
                            )
                            write_xml(element, totalizer)
                        else:
                            log.info(
                                f"Evento {identifier_event_connection} não encontrado."
                            )

        except Exception as err:
            log.exception(err)
            msg = f"Erro extraindo conteúdo do xml.<br> {err}"
            if not task_info(task, msg=msg, type_of=3):
                raise err

    def _set_process_return(
        self,
        xml_or_file_path=None,
        update_batch=True,
        update_event=True,
        release_send=True,
        totalizers=[],
        task=None,
    ):
        """Este método processa o retorno do Batch.

        Args:
            xml_or_file_path (str): utiliza self.file_path quando None
            update_batch (bool): atualiza o Batch com o resultado do processamento. Default True
            update_event (bool): atualiza o Event com o resultado do processamento. Default True
            release_send (bool): libera o envio em caso de falha do Batch. Default True
            totalizers (list, optional): Lista de totalizadores a serem extraídos. Defaults to [], realizará para todos extratores.
            task (mq.Task, optional): task que está executando o processamento do retorno. Default None

        Returns:
            success (bool): True se process_status em PROCESS_STATUS_EVENT_VALIDS_SENT
        """

        def prepare_occurrence(occurrence):
            """Este método retorna um dict de campos do Occurrence.

            Args:
                occurrence (str):
            Returns:
                (dict): dict de campos do Occurrence
            """
            code = occurrence.find(".//{*}codigo")
            dsc = occurrence.find(".//{*}descricao")
            typeo = occurrence.find(".//{*}tipo")
            local = occurrence.find(".//{*}localizacao")
            return {
                "environment": esocial_environment(),
                "code": code.text,
                "type_occurrence": typeo.text,
                "description": dsc.text,
                "location": local.text if local is not None else "",
            }

        try:
            task_info(
                task,
                msg=f"BATCH {self.group} {self} - Começando processemanto do Retorno do Batch.",
                type_of=1,
            )

            success = False

            if not xml_or_file_path:
                xml_or_file_path = self.file_path_process

            xml_str = etree.parse(xml_or_file_path)
            xml_obj = xml_str.getroot()
            LEVEL_TAG = {"ns1": xml_obj.nsmap[None]}
            process = xml_obj.xpath(".//ns1:cdResposta", namespaces=LEVEL_TAG)[0]

            if update_batch:
                """Atualiza Batch com process_status e process_version_app."""
                self.process_status = int(process.text)
                success = self.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT
                if success:
                    receipt_obj = xml_obj.find(
                        ".//{*}versaoAplicativoProcessamentoLote"
                    )
                    self.process_version_app = receipt_obj.text
                self.save()

                """Cria ReturnResult."""
                return_result_batch = self.results.create()
                return_result_batch.set_process_batch(success)

                """Libera eventos para empacotamento quando houver falha no ambiente do esocial."""
                send_event_again = (
                    self.process_status not in PROCESS_STATUS_EVENT_VALIDS_SENT
                )
                if release_send and send_event_again:
                    status_event = 4 if self.process_status == 101 else 1
                    for ev in self.events.all():
                        ev = ev.event
                        ev.update_status(status_event)

                for re in xml_obj.xpath(".//ns1:retornoEvento", namespaces=LEVEL_TAG):
                    first = list(re)[0]
                    LEVEL_TAG.update({"ns2": first.nsmap[None]})
                    event = self.events.filter(
                        identifier=re.getparent().attrib["Id"]
                    ).first()

                    """Atualização do Event com retorno."""
                    if update_event and event:
                        event = event.event
                        xml_process_obj = next(
                            first.iterfind(".//ns2:processamento", namespaces=LEVEL_TAG)
                        )
                        event.process_status = int(
                            next(
                                first.iterfind(
                                    ".//ns2:cdResposta", namespaces=LEVEL_TAG
                                )
                            ).text
                        )
                        dh_process = next(
                            first.iterfind(
                                ".//ns2:dhProcessamento", namespaces=LEVEL_TAG
                            )
                        )
                        try:
                            event.process_date = datetime.strptime(
                                dh_process.text, "%Y-%m-%dT%H:%M:%S.%f"
                            )
                        except ValueError:
                            event.process_date = datetime.strptime(
                                dh_process.text, "%Y-%m-%dT%H:%M:%S"
                            )
                        app_version = next(
                            first.iterfind(
                                ".//ns2:versaoAppProcessamento", namespaces=LEVEL_TAG
                            )
                        )
                        event.process_version_app = app_version.text
                        if event.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT:
                            try:
                                event.process_receipt = first.xpath(
                                    ".//ns2:nrRecibo", namespaces=LEVEL_TAG
                                )[0].text
                            except IndexError:
                                pass

                        return_result_event = self.results.create(event=event)
                        return_result_event.set_process_event(success)

                        event.update_status(event.process_status)

                        for _occurrence in xml_process_obj.xpath(
                            ".//ns2:ocorrencia", namespaces=LEVEL_TAG
                        ):
                            occurrence = prepare_occurrence(_occurrence)
                            return_result_event.ocurrences.get_or_create(**occurrence)

                    """Ocorrências do Batch."""
                    for _occurrence in xml_obj.xpath(
                        ".//ns1:ocorrencia", namespaces=LEVEL_TAG
                    ):
                        occurrence = prepare_occurrence(_occurrence)
                        return_result_batch.ocurrences.create(**occurrence)
            else:
                success = self.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT

            """Extração de totalizadores."""
            self.extract_return_result_totalizers(
                xml_obj, totalizers=totalizers, task=task
            )
        except Exception as err:
            log.exception(err)
            if not task_info(
                task,
                msg=f"Erro ao extrair BATCH {self.group} {self}.<br>{err}",
                type_of=3,
            ):
                raise err

        task_info(
            task,
            msg=f"BATCH {self.group} {self} - Finalizando processemanto do Retorno do Batch.",
            type_of=1,
        )

        return success

    def consult_process(self, success_return=None, task=None):
        from esocial.webservice import ClientConsultEventBatch

        buff = """<eSocial xmlns="%s">
                    <consultaLoteEventos>
                        <protocoloEnvio>%s</protocoloEnvio>
                    </consultaLoteEventos>
                    </eSocial>""" % (
            get_current_config().xmlns_consult,
            self.delivery_receipt,
        )
        client = ClientConsultEventBatch()
        xml_doc = etree.XML(buff)
        res = client.service.ConsultarLoteEventos(consulta=xml_doc)

        etree_res = etree.ElementTree(res)
        etree_res.write(
            self.file_path.replace(".xml", "-process.xml"),
            encoding="utf-8",
            pretty_print=True,
        )
        status_return = self._set_process_return(task=task)

        self.update_success_events_cache()

        if success_return:
            return status_return

        return res

    @classmethod
    def create_events(
        cls,
        events=[],
        clear_environment=False,
        event_kind=["TI"],
        task=None,
        period=None,
    ):
        from esocial.extractors.base import Factory

        log.debug("BatchEvent create_events...")
        print("BatchEvent create_events...")
        task = Task.objects.filter(uuid=task).last()

        if not events:
            events = get_acronyms_from_kind(event_kind)
        if clear_environment:
            events = [
                "s1000",
            ]

        for event_acronym in events:
            log.debug("CREATE >> %s" % event_acronym)
            print("CREATE >> %s" % event_acronym)
            log.debug("CREATING >> %s" % event_acronym)
            print("CREATING >> %s" % event_acronym)
            Factory.get_factory(event_acronym).manage_in_bulk(
                clear_env=clear_environment,
                task=task,
                period=period,
                write_feedback=True,
            )

        Event.call_evaluate_dependency(acronyms=events, task=task)

    @classmethod
    def generate_events_ti_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_events_ti_task

        if not task_conflict_with_all():
            Task.start(generate_events_ti_task, user=get_current_user().pk)
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_ti_registration_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_events_ti_registration_task

        if not task_conflict_with_all():
            Task.start(generate_events_ti_registration_task, user=get_current_user().pk)
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_registration_call_task(
        cls, task=None, period=None, categories=[]
    ):
        from esocial.tasks.generation import generate_events_registration_task

        if not task_conflict_with_all():
            Task.start(
                generate_events_registration_task,
                user=get_current_user().pk,
                categories=categories,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_sst_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_events_registration_task

        if not task_conflict_with_all():
            Task.start(
                generate_events_registration_task,
                user=get_current_user().pk,
                group_event="SST",
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_payroll_call_task_list(cls, task=None, period=[]):
        from esocial.tasks.generation import generate_events_payroll_task_list

        if not task_conflict_with_all():
            Task.start(
                generate_events_payroll_task_list,
                period=period,
                user=get_current_user().pk,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_payroll_process_call_task_list(
        cls, task=None, period=[], events=[]
    ):
        from esocial.tasks.generation import generate_events_payroll_process_task_list

        if not task_conflict_with_all():
            Task.start(
                generate_events_payroll_process_task_list,
                period=period,
                user=get_current_user().pk,
                events=events,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_payroll_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_events_payroll_task

        if not task_conflict_with_all():
            Task.start(
                generate_events_payroll_task, period=period, user=get_current_user().pk
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_payroll_process_call_task(
        cls, task=None, period=None, events=[]
    ):
        from esocial.tasks.generation import generate_events_payroll_process_task

        if not task_conflict_with_all():
            Task.start(
                generate_events_payroll_process_task,
                period=period,
                user=get_current_user().pk,
                events=events,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_delete_events_payroll_call_task(
        cls, task=None, period=None, events=[]
    ):
        """Este método chama a task generate_delete_events_payroll_task.

        Args:
            task (Task, optional): engine.mq.models.Task. Defaults to None.
            period (int, optional): pk do Periodo. Defaults to None.
            events (list, optional): list de events. Defaults to [].
        """
        from esocial.tasks.generation import generate_delete_events_payroll_task

        if not task_conflict_with_all():
            Task.start(
                generate_delete_events_payroll_task,
                period=period,
                user=get_current_user().pk,
                events=events,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_close_events_payroll_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_close_events_payroll_task

        if not task_conflict_with_all():
            Task.start(
                generate_close_events_payroll_task,
                period=period,
                user=get_current_user().pk,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_reopen_events_payroll_call_task(cls, task=None, period=None):
        from esocial.tasks.generation import generate_reopen_events_payroll_task

        if not task_conflict_with_all():
            Task.start(
                generate_reopen_events_payroll_task,
                period=period,
                user=get_current_user().pk,
            )
        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def generate_events_payroll(cls, task=None, period=None):
        """Este método realiza a Geração de eventos de Folha"""
        from esocial.tasks.generation import generate_event_payroll
        from rh.gfp.models import Periodo

        def _event_payroll(period):
            """Chamada para task de geração de eventos de cadastro."""
            period = Periodo.objects.get(pk=period)
            user = get_current_user()

            naturalperson = [cpf for cpf in cls.gen_naturalpersons(period)]
            total = len(naturalperson)
            inc_progress = 100.0 / total if total else 0
            result = None
            job = group(
                [
                    generate_event_payroll.s(
                        task.uuid, user.pk, period.pk, cpf, inc_progress=inc_progress
                    )
                    for cpf in naturalperson
                ]
            )

            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            job.apply_async(queue="esocial-events")

            # while not result.ready():
            #     time.sleep(2)

            task.info(pct_progress=0)
            task.finish_execution(set_process=False)

        _event_payroll(period)

    @classmethod
    def generate_events_payroll_process(cls, task=None, period=None, events=[]):
        """Este método realiza a Geração de eventos de Folha"""
        from esocial.tasks.generation import generate_event_payroll_process
        from rh.gfp.models import Periodo

        user = get_current_user()

        def _event_payroll(period):
            """Chamada para task de geração de eventos de folha."""
            period = Periodo.objects.get(pk=period)

            naturalperson = [cpf for cpf in cls.gen_naturalpersons(period)]
            total = len(naturalperson)
            inc_progress = 100.0 / total if total else 0
            result = None
            job = group(
                [
                    generate_event_payroll_process.s(
                        task.uuid,
                        user.pk,
                        period.pk,
                        cpf,
                        events=events,
                        inc_progress=inc_progress,
                    )
                    for cpf in naturalperson
                ]
            )

            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            job.apply_async(queue="esocial-events")

            # while not result.ready():
            #     time.sleep(2)

            task.info(pct_progress=0)
            task.finish_execution(set_process=False)

        _event_payroll(period)

    @classmethod
    def generate_close_events_payroll(cls, task=None, period=None):
        """Este método realiza a fechamento (S-1299) de eventos de Folha"""
        from esocial.extractors.s1299 import S1299Extractor
        from rh.gfp.models import Periodo

        task = Task.objects.filter(uuid=task.uuid).last()
        period = Periodo.objects.get(pk=period)

        S1299Extractor(period, period=period, task=task).run()

    @classmethod
    def generate_reopen_events_payroll(cls, task=None, period=None):
        """Este método realiza a reabertura (S-1298) de eventos de Folha."""
        from esocial.extractors.s1298 import S1298Extractor
        from rh.gfp.models import Periodo

        task = Task.objects.filter(uuid=task.uuid).last()
        period = Periodo.objects.get(pk=period)

        S1298Extractor(period, period=period, task=task).run()

    @classmethod
    def gen_naturalpersons(cls, period):
        """Este método é um generator de cpf de pessoas físicas do period.

        Args:
            period (rh.gfp.models.Periodo): _description_

        Returns:
            generator: _description_
        """
        config = get_current_config()
        naturalperson = NaturalPerson.objects.filter(
            (
                Q(servidor__paychecks__folha__periodo__mes=period.mes)
                & Q(servidor__paychecks__folha__periodo__ano=period.ano)
            )
            | Q(
                servidor__paychecks__folha__dt_pagamento__range=(
                    period.start_date,
                    period.end_date,
                )
            )
        )

        if config.employee_filter.exists():
            naturalperson = naturalperson.filter(
                cpf__in=(
                    cpf
                    for cpf in config.employee_filter.values_list(
                        "pessoa_fisica__cpf", flat=True
                    )
                )
            )
        return (cpf for cpf in naturalperson.distinct().values_list("cpf", flat=True))

    @classmethod
    def generate_delete_events_payroll(cls, task=None, period=None, events=[]):
        """Este método realiza a Exclusão (S-3000) de eventos de Folha.

        Args:
            task (Task, optional): engine.mq.models.Task. Defaults to None.
            period (int, optional): pk do Periodo. Defaults to None.
            events (list, optional): list de events. Defaults to [].
        """
        from itertools import chain

        from esocial.extractors.base import Factory
        from rh.gfp.models import Periodo

        period = Periodo.objects.get(pk=period)

        def _prepare_events(period):
            acronyms = (
                set(get_acronyms_from_kind(["FP"]))
                .difference(["s1298", "s1299"])
                .intersection(events)
            )
            generator_events = ()
            for acronym in acronyms:
                query = (
                    Factory.get_factory(acronym)
                    .extracted_class.objects.valids_sent()
                    .filter(
                        competence_month=period.mes,
                        competence_year=period.ano,
                        registry_person__in=cls.gen_naturalpersons(period),
                    )
                )
                generator_events = (
                    *generator_events,
                    (pk for pk in query.values_list("pk", flat=True)),
                )

            return generator_events

        task = Task.objects.filter(uuid=task.uuid).last()

        if (
            not S1299.objects.valids_sent()
            .filter(competence_month=period.mes, competence_year=period.ano)
            .exclude(closed_by_event__isnull=False)
            .exists()
        ):
            cls.generate_delete_events(
                task=task, events=[pk for pk in chain(*_prepare_events(period))]
            )

            query = Event.objects.filter(
                acronym__in=("s1200", "s1202", "s1207", "s1210"),
                registry_person__in=cls.gen_naturalpersons(period),
            ).valids_not_sent()
            Event.call_evaluate_dependency(
                event=(event for event in query.values_list("pk", flat=True)), task=task
            )
        else:
            task.info(
                msg="A folha de pagamentos precisa estar aberta para poder excluir os eventos.",
                type_of=3,
            )

        task.info(pct_progress=100)
        task.finish_execution()

    @classmethod
    def generate_events_ti(cls, task=None, period=None, finish=True):
        """Este método realiza a Geração de eventos de TI."""
        from esocial.extractors.base import Factory
        from esocial.extractors.s1010 import S1010Factory
        from esocial.tasks.generation import generate_event_s1010

        acronyms = get_acronyms_from_kind(["EEMP", "TI"])
        for acronym in acronyms:
            if acronym != "s1010":
                Factory.get_factory(acronym).manage_in_bulk(task=task, period=period)

        user = get_current_user()

        def _event_s1010():
            """Chamada para task de geração de eventos de cadastro."""
            query = S1010Factory._query_instances_outside()

            total = query.count()
            inc_progress = 100.0 / total if total else 0
            result = None
            job = group(
                [
                    generate_event_s1010.s(
                        task.uuid,
                        user.pk,
                        period,
                        entry.numero,
                        inc_progress=inc_progress,
                    )
                    for entry in query
                ]
            )

            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            job.apply_async(queue="esocial-events")
            # while not result.ready():
            #     time.sleep(2)

            if finish:
                task.info(pct_progress=0)
                task.finish_execution(set_process=False)

        if "s1010" in get_acronyms_from_kind(["TI"]):
            _event_s1010()

        Event.call_evaluate_dependency(acronyms=acronyms, task=task)

    @classmethod
    def generate_events_ti_registration(cls, task=None, period=None):
        """Este método realiza a Geração de eventos de TI e Cadastro."""
        from esocial.extractors.s2200 import S2200Extractor
        from esocial.tasks.generation import generate_event_registration

        """Geração de eventos de tabela."""
        cls.generate_events_ti(task=task, period=period, finish=False)

        user = get_current_user()

        def _event_registration():
            """Chamada para task de geração de eventos de cadastro."""
            start_date = S2200Extractor.initial_group_date()
            query = Employee.objects.exclude(
                termination_date__isnull=False, termination_date__lte=start_date
            ).exclude(type_by_possession="XXX")

            config = get_current_config()
            query = query.exclude(
                matricula__in=(
                    registry
                    for registry in config.employee_exclude.values_list(
                        "matricula", flat=True
                    )
                )
            )
            if config.employee_filter.exists():
                query = query.filter(
                    matricula__in=(
                        registry
                        for registry in config.employee_filter.values_list(
                            "matricula", flat=True
                        )
                    )
                )

            total = query.count()
            inc_progress = 100.0 / total if total else 0
            Task.objects.filter(uuid=task.uuid).update(progress=0)
            task.refresh_from_db()
            result = None
            job = group(
                [
                    generate_event_registration.s(
                        task.uuid,
                        user.pk,
                        period,
                        employee.matricula,
                        employee.pessoa_fisica.cpf,
                        inc_progress=inc_progress,
                    )
                    for employee in query
                ]
            )

            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            job.apply_async(queue="esocial-events")
            # while not result.ready():
            #     time.sleep(2)

            task.info(pct_progress=0)
            task.finish_execution(set_process=False)

        _event_registration()

    @classmethod
    def generate_events_registration(
        cls, group_event="CF", task=None, period=None, categories=[]
    ):
        """Este método realiza a Geração de eventos de TI e Cadastro."""
        from esocial.extractors.base import Factory
        from esocial.extractors.s2200 import S2200Extractor
        from esocial.tasks.generation import (
            generate_event_registration,
            generate_event_sst,
        )

        user = get_current_user()

        acronyms = list(
            set(get_acronyms_from_kind(["EEMP", "TI"])).difference(["s1010"])
        )
        acronyms.sort()
        for event_acronym in acronyms:
            Factory.get_factory(event_acronym).manage_in_bulk(task=task, period=period)

        Event.call_evaluate_dependency(acronyms=acronyms, task=task)

        def _run_group_tasks():
            """Chamada para task de geração de eventos de cadastro ou SST."""
            start_date = S2200Extractor.initial_group_date()

            if categories:
                query = (
                    Employee.objects.filter(type_by_possession__in=categories)
                    .exclude(
                        termination_date__isnull=False, termination_date__lte=start_date
                    )
                    .exclude(type_by_possession="XXX")
                )
            else:
                query = Employee.objects.exclude(
                    termination_date__isnull=False, termination_date__lte=start_date
                ).exclude(type_by_possession="XXX")

            config = get_current_config()
            query = query.exclude(
                matricula__in=(
                    registry
                    for registry in config.employee_exclude.values_list(
                        "matricula", flat=True
                    )
                )
            )
            if config.employee_filter.exists():
                query = query.filter(
                    matricula__in=(
                        registry
                        for registry in config.employee_filter.values_list(
                            "matricula", flat=True
                        )
                    )
                )

            _generate_task = generate_event_registration
            if group_event == "SST":
                _generate_task = generate_event_sst
                query = query.distinct("pessoa_fisica__cpf").order_by(
                    "pessoa_fisica__cpf"
                )

            total = query.count()
            inc_progress = ((100.0 / total) / len(EVENTOS_CADASTRO)) if total else 0
            result = None
            jobs = []
            for employee in query:
                jobs.append(
                    group(
                        [
                            _generate_task.s(
                                task.uuid,
                                user.pk,
                                period,
                                employee.matricula,
                                employee.pessoa_fisica.cpf,
                                map_event=map_event,
                                inc_progress=inc_progress,
                            )
                            for map_event in EVENTOS_CADASTRO
                        ]
                    )
                )

            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            [job.apply_async(queue="esocial-events") for job in jobs]

            # while not result.ready():
            #     time.sleep(2)

            task.info(pct_progress=0)
            task.finish_execution(set_process=False)

        _run_group_tasks()

    @classmethod
    def generate_delete_events(cls, task=None, events=[]):
        from esocial.tasks.generation import delete_event_payroll

        total = len(events)
        user = get_current_user()
        inc_progress = 100.0 / total if total else 0
        job = group(
            [
                delete_event_payroll.s(
                    task.uuid if task else None,
                    user.pk,
                    event,
                    inc_progress=inc_progress,
                )
                for event in events
            ]
        )

        # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
        # result = job.apply_async()
        job.apply_async(queue="esocial-events")

        # while not result.ready():
        #     time.sleep(2)
        task.info(pct_progress=0)
        task.finish_execution(set_process=False)

    @classmethod
    def create_batches(cls, group=None, generate_xml=False, **kwargs):
        from esocial.extractors.base import update_task

        def _update_batches():
            for batch in BatchEvent.objects.filter(delivery_status=1):
                if batch.events.count() == 0:
                    batch.delete()
                else:
                    batch.update_delivery_status(new_status=2)

        config = get_current_config()
        task = (
            Task.objects.filter(uuid=kwargs["task"].uuid).last()
            if "task" in kwargs
            else None
        )

        group_batches = {1: None, 2: None, 3: None, 4: None, 5: None}
        events = Event.objects.without_dependencies().exclude(
            acronym__in=(
                label
                for label in config.interrupt_batch_events.filter().values_list(
                    "label", flat=True
                )
            )
        )
        total = events.count()
        progress_message = "Criando lotes - "

        Task.objects.filter(uuid=task.uuid).update(progress=0)
        task.refresh_from_db()
        update_task(progress_message=progress_message, task=task, total=total)
        for ev in events:
            ev = ev.event
            if (
                group_batches[ev._group] is None
                or group_batches[ev._group].events.count() == 50
            ):
                if group_batches[ev._group]:
                    b = group_batches[ev._group]
                    b.update_delivery_status(new_status=2)

                group_batches[ev._group] = BatchEvent.objects.create(
                    environment=esocial_environment(),
                    group=str(ev._group),
                    application=1,
                )

            ev.batches.clear()

            group_batches[ev._group].events.add(ev)
            ev.update_status(3)
            update_task(progress_message=progress_message, task=task, total=total)

        _update_batches()

        return group_batches


class ReturnResultManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(environment=esocial_environment())


class ReturnResultAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class ReturnResult(AuditTimestampModel):

    DEFAULT_USER = "athenas"

    batch = models.ForeignKey(
        "BatchEvent",
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Lote",
    )
    event = models.ForeignKey(
        "Event",
        related_name="results",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_version_app = models.CharField(max_length=20)
    delivery_status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "DELIVERY_STATUS_BATCH"),
        null=True,
        blank=True,
    )
    process_date = models.DateTimeField(null=True, blank=True)
    process_status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "PROCESS_STATUS_BATCH"),
        null=True,
        blank=True,
    )
    process_version_app = models.CharField(max_length=20)
    environment = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )

    objects = ReturnResultManager()
    objects_all = ReturnResultAllManager()

    @property
    def is_delivery(self):
        return (self.delivery_status and True) or False

    def __str__(self):
        _unicode = "%s (%s/%s)" % (
            self.batch,
            self.delivery_status,
            self.process_status,
        )
        if self.event:
            _unicode = "%s: %s" % (_unicode, self.event)
        return _unicode

    def save(self, *args, **kwargs):
        if not self.pk:
            self.environment = esocial_environment()
        super(ReturnResult, self).save(*args, **kwargs)

    def set_delivery(self, success=True):
        self.delivery_status = self.batch.delivery_status
        if success:
            self.delivery_version_app = self.batch.delivery_version_app
            self.delivery_date = self.batch.delivery_date
        self.save()

    def set_process_batch(self, success=True):
        self.process_status = self.batch.process_status
        if success:
            self.process_version_app = self.batch.process_version_app
        self.save()

    def set_process_event(self, success=True):
        if self.event:
            self.process_status = self.event.process_status
            if success:
                self.process_version_app = self.event.process_version_app
                self.process_date = self.event.process_date
        self.save()


class OccurrenceManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(environment=esocial_environment())


class OccurrenceAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class Occurrence(models.Model):

    result = models.ForeignKey(
        "ReturnResult", related_name="ocurrences", on_delete=models.CASCADE
    )
    code = models.PositiveIntegerField(verbose_name="Código", default=0, blank=True)
    type_occurrence = models.PositiveIntegerField(
        verbose_name="Tipo", default=1, blank=True
    )
    description = models.TextField(verbose_name="Descrição", default="", blank=True)
    location = models.CharField(
        verbose_name="Localização", null=True, blank=True, max_length=400
    )
    environment = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )

    objects = OccurrenceManager()
    objects_all = OccurrenceAllManager()

    def __str__(self):
        return "%d: %s" % (self.code, self.description)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.environment = esocial_environment()
        super(Occurrence, self).save(*args, **kwargs)


class ReferenceManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(environment=esocial_environment())


class ReferenceAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class Reference(models.Model):
    oid = models.CharField("ID objeto origem", db_index=True, max_length=32)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    # FIXME: Unlike ForeignKey, GenericForeignKey does not accept an on_delete argument to customize this behavior;
    # if desired, you can avoid the cascade-deletion by not using GenericRelation, and alternate behavior can be provided via
    # the pre_delete signal.
    ref_object = GenericForeignKey("content_type", "oid")
    event = models.ForeignKey(
        "Event", related_name="references", on_delete=models.CASCADE
    )
    environment = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )

    objects = ReferenceManager()
    objects_all = ReferenceAllManager()

    class Meta:
        unique_together = ["oid", "content_type", "event"]

    def __str__(self):
        return f"{self.ref_object} - OID({self.oid}): {self.event}"

    @classmethod
    def get_or_create(cls, ref_object, event):
        created = False
        query = Reference.objects.filter(
            oid=ref_object.pk,
            content_type=ContentType.objects.get_for_model(ref_object),
            event=event,
        )
        if not query.exists():
            rs = Reference.objects.create(ref_object=ref_object, event=event)
            created = True
        else:
            rs = query.last()
        return rs, created

    def get_object_for_this_type_oid(self):
        obj = None
        try:
            obj = self.content_type.get_object_for_this_type(**{"pk": self.oid})
        except Exception as err:
            log.exception(err)
        return obj

    def save(self, *args, **kwargs):
        if not self.pk:
            self.environment = esocial_environment()
        super(Reference, self).save(*args, **kwargs)


class DeletedModelManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class DeletedModellAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class DeletedModelQuerySet(models.QuerySet):
    pass


class DeletedModel(AuditTimestampModel):

    deleted = models.BooleanField(default=False)

    objects = DeletedModelManager.from_queryset(DeletedModelQuerySet)()
    objects_all = DeletedModellAllManager().from_queryset(DeletedModelQuerySet)()

    class Meta:
        abstract = True


class EventManager(models.Manager):

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(ide_evento_tp_amb=esocial_environment(), deleted=False)
        )


class EventDeleteManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(ide_evento_tp_amb=esocial_environment())


class EventAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class EventQuerySet(models.QuerySet):

    def without_invalid_xml_schema(self):
        return self.exclude(xsd_schema_validated=False)

    def without_dependencies(self):
        return self.filter(process_status=1).without_invalid_xml_schema()

    def valids_by_status(self):
        return (
            self.filter(process_status__in=VALID_EVENT_STATUS)
            .exclude(modified_by_event__isnull=False)
            .exclude(action=EXCLUSION)
            .without_invalid_xml_schema()
        )

    def valids_only_by_status(self):
        return (
            self.filter(process_status__in=VALID_EVENT_STATUS)
            .exclude(action=EXCLUSION)
            .without_invalid_xml_schema()
        )

    def valids_sent(self):
        return (
            self.filter(process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT)
            .exclude(modified_by_event__isnull=False)
            .exclude(action=EXCLUSION)
            .without_invalid_xml_schema()
        )

    def invalids_sent(self):
        return self.filter(process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR)

    def exclude_invalids_sent(self):
        return self.exclude(process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR)

    def valids_not_sent(self):
        return self.filter(
            process_status__in=PROCESS_STATUS_EVENT_NOT_SENT
        ).without_invalid_xml_schema()

    def can_exclude(self):
        return self.filter(
            Q(process_status__in=CAN_DELETE_EVENT_STATUS, father_event__isnull=True)
            | Q(father_event__process_status__in=CAN_DELETE_EVENT_STATUS)
        ).exclude(action=EXCLUSION)

    def validity_in(self, start_date, end_date=None):
        query = self.valids_by_status().exclude(
            Q(end_validity__isnull=False) & Q(end_validity__lt=start_date)
        )
        if end_date:
            query = query.exclude(start_validity__gt=end_date)

        return query

    def not_validated(self):
        return self.filter(xsd_schema_validated=False)

    def by_per_apur(self, per_apur):
        return self.filter(ide_evento_per_apur=per_apur)

    def with_problems(self, per_apur):
        return self.by_per_apur(per_apur).exclude(
            pk__in=(
                pk
                for pk in self.by_per_apur(per_apur)
                .valids_sent()
                .values_list("pk", flat=True)
            )
        )

    def summarize(self):
        events = (
            self.filter(
                internal=False, process_status__in=PROCESS_STATUS_EVENT_NOT_SENT
            )
            .annotate(
                acronym2=Case(
                    When(acronym="s3000", then=F("modify_event__acronym")),
                    default=F("acronym"),
                    output_field=CharField(),
                )
            )
            .annotate(
                type_of=Case(
                    When(acronym="s3000", then=Value("EXC")),
                    When(xsd_schema_validated=False, then=Value("INV")),
                    When(
                        xsd_schema_validated=True, action=INCLUSION, then=Value("INC")
                    ),
                    When(
                        xsd_schema_validated=True,
                        action=MODIFICATION,
                        then=Value("MOD"),
                    ),
                    When(
                        xsd_schema_validated=True, action=EXCLUSION, then=Value("EXC")
                    ),
                    When(
                        xsd_schema_validated=True,
                        action=RECTIFICATION,
                        then=Value("RET"),
                    ),
                    default=F("acronym"),
                    output_field=CharField(),
                )
            )
            .values("acronym2")
            .order_by("acronym2")
            .annotate(
                INC=Count("pk", filter=Q(type_of="INC")),
                MOD=Count("pk", filter=Q(type_of="MOD")),
                RET=Count("pk", filter=Q(type_of="RET")),
                EXC=Count("pk", filter=Q(type_of="EXC")),
                INV=Count("pk", filter=Q(type_of="INV")),
            )
        )

        return events


class Event(DeletedModel):
    """Classe base de Eventos do eSocial. Possui todos os campos comuns a todos."""

    class Meta:
        ordering = (
            "group",
            "registry_employee",
            "registry_person",
            "start_validity",
            "acronym",
            "created_at",
        )

    oid = models.CharField(
        "ID objeto origem", db_index=True, max_length=32, null=True, blank=True
    )
    control_oid = models.CharField(
        "Controle de OID", db_index=True, max_length=11, null=True, blank=True
    )
    group = models.PositiveIntegerField(verbose_name="Grupo", default=1)
    batches = models.ManyToManyField(
        BatchEvent, related_name="events", verbose_name="Lotes"
    )
    application = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "APPLICATION"), default=1
    )
    identifier = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=255)
    event_version = models.CharField(max_length=20)
    acronym = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True)
    validator = models.ForeignKey(
        ClassCode,
        blank=True,
        null=True,
        related_name="validator",
        on_delete=models.SET_NULL,
    )
    competence_month = models.PositiveIntegerField()
    competence_year = models.PositiveIntegerField()
    periodicity = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "PERIODICITY"), default=ANYTIME
    )
    obligation = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "OBLIGATION"),
        default=MANDATORY_IF_EXIST,
    )
    action = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "ACTION"), default=INCLUSION
    )
    rectified_register = models.ForeignKey(
        "Event", null=True, blank=True, on_delete=models.CASCADE
    )
    xsd_schema_validated = models.BooleanField(verbose_name="Validado", default=False)
    process_date = models.DateTimeField(null=True, blank=True)
    process_receipt = models.CharField(max_length=255, null=True, blank=True)
    process_status = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "STATUS_EVENT"), default=1
    )
    process_version_app = models.CharField(max_length=20)
    modify_event = models.OneToOneField(
        "Event",
        on_delete=models.SET_NULL,
        related_name="modified_by_event",
        null=True,
        blank=True,
    )
    closed_by_event = models.OneToOneField(
        "Event",
        on_delete=models.SET_NULL,
        related_name="close_event",
        null=True,
        blank=True,
    )
    dependencies = models.ManyToManyField(
        "Event", through="EventDependency", related_name="dependents", symmetrical=False
    )
    search_cache = models.CharField(max_length=255, blank=True, default="")
    internal = models.BooleanField(verbose_name="Indireto", default=False)
    archived = models.BooleanField(verbose_name="Arquivado", default=False)
    start_validity = models.DateField(blank=True)
    end_validity = models.DateField(null=True, blank=True)
    diff_content = models.TextField(
        blank=True, verbose_name="Diff de conteúdo", default=""
    )
    father_event = models.ForeignKey(
        "Event",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    has_exclusion_cache = models.BooleanField(
        verbose_name="Possui evento de exclusão?", default=False
    )
    is_invalid_cache = models.BooleanField(verbose_name="É válido?", default=False)
    modified_by_event_cache = models.CharField(max_length=255, blank=True, default="")
    batch_cache = models.CharField(max_length=255, blank=True, default="")

    xmlns = models.CharField(max_length=256, null=True, blank=True)
    ide_evento_tp_amb = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )
    ide_evento_proc_emi = models.PositiveIntegerField(default=1)
    ide_evento_ver_proc = models.CharField(max_length=20, null=True, blank=True)
    ide_evento_ind_apuracao = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "INDICATIVE_ASCERTAINMENT_PERIOD"),
        null=True,
        blank=True,
    )
    ide_evento_per_apur = models.CharField(max_length=7, null=True, blank=True)
    ide_evento_ind_retif = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "INDICATIVE_TYPE_INFORMATION"),
        null=True,
        blank=True,
    )
    ide_evento_nr_recibo = models.CharField(max_length=40, null=True, blank=True)
    ide_empregador_tp_insc = models.PositiveIntegerField(default=1)
    ide_empregador_nr_insc = models.CharField(max_length=15, null=True, blank=True)
    ide_evento_ind_guia = models.PositiveIntegerField(null=True, blank=True)
    registry_employee = models.IntegerField(
        db_index=True, null=True, blank=True, verbose_name="Matrícula de Servidor"
    )
    registry_person = models.CharField(
        db_index=True,
        max_length=11,
        null=True,
        blank=True,
        verbose_name="CPF da Pessoa Física",
    )

    objects = EventManager.from_queryset(EventQuerySet)()
    objects_deleted = EventDeleteManager.from_queryset(EventQuerySet)()
    objects_all = EventAllManager().from_queryset(EventQuerySet)()

    # DEPRECATED
    sequential = models.PositiveIntegerField()

    XML_SCHEMA_NAME = None
    GROUP = 1
    NAME = "Event"
    ACTION_PERM = ACTION
    INTERNAL = False
    CLOSE_PREVIOUS_EVENTS = False
    EXCLUSION_TYPE = EXCLUSION_TYPE_DEFAULT
    OTHERS_DEPENDENCIES = []
    CREATE_IDENTIFIER = True

    def __str__(self):
        if hasattr(self, "identifier"):
            return f"E: {self.acronym} - Id: ({self.pk}) {self.identifier}"
        return f"E: {self.acronym} - Version: {self.event_version}"

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)

        self._xml_schema_name = self.XML_SCHEMA_NAME
        self._group = self.GROUP
        self._name = self.NAME
        self._action_perm = self.ACTION_PERM
        self._internal = self.INTERNAL
        self.xmlns = getattr(self, "XMLNS", None)

        self._json_model = {}
        self._file_directory = None
        self._file_path = None
        self._file_path_signed = None
        self._file_name = None
        self._xml = None
        self._xml_signed = None
        self._xml_schema = None
        self._file_path_xml_schema = None
        self._current_config = None
        self.current_config

    def _search_cache(self):
        return ""

    @property
    def current_config(self):
        if not self._current_config:
            self._current_config = get_current_config()
        return self._current_config

    @property
    def batch(self):
        return self.batches.first()

    @property
    def has_dependencies(self):
        """Esta propriedade informa se o evento possui dependências de eventos não processados."""
        return (
            EventDependency.objects.filter(event=self)
            .exclude(dependency__process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT)
            .exists()
        )

    @property
    def has_dependencies_not_satisfied(self):
        """Esta propriedade informa se o evento possui dependências que não foram satisfeitas."""
        return (
            EventDependency.objects.filter(event=self)
            .filter(
                Q(dependency__isnull=True) | Q(dependency__xsd_schema_validated=False)
            )
            .exists()
        )

    def set_identifier(self):
        """Este método cria um identifier válido. Também checa se já foi utilizado.
            - Campo Fixo ID, 2 (pos)
            - Tipo inscrição,  1 - CNPJ ou 2 - CPF, 1 (pos)
            - Nr Inscrição CPF, CNPJ, ou CNPJ Base. Preencher com zeros a direita até completar as 14 posições. 14 (pos)
            - Data e hora de geração Formato: YYYYMMDDhhmmss  YYYY- ano; MM - mês; DD - dia; hh - hora; mm - minuto; ss - segundo. 14 (pos)
            - Sequencial Número sequencial de livre preenchimento do empregador. 5 (pos)
        Este método também seta o campo sequential.

        Returns:
            self.identifier (str): Identifier gerado.
        """
        if not self.pk and self.CREATE_IDENTIFIER:
            identifier = "ID%s%s" % (
                self.current_config.ide_employer_tp_insc,
                self.current_config.ide_employer_nr_insc[0:8].ljust(14, "0"),
            )

            def _gen():
                now = datetime.now()
                self.sequential = now.strftime("%f")[-5:]
                self.identifier = "%s%s%s" % (
                    identifier,
                    now.strftime("%Y%m%d%H%M%S"),
                    self.sequential,
                )

            _gen()
            while Event.objects.filter(identifier=self.identifier).exists():
                _gen()
        return self.identifier

    @classmethod
    def _load_json_model(cls):
        return _load_json_model(cls._acronym())

    @classmethod
    def _acronym(cls):
        return cls.__name__

    @property
    def xml_schema(self):
        if not self._xml_schema and self.event.file_path_xml_schema:
            with codecs.open(self.event.file_path_xml_schema, "r") as schema:
                self._xml_schema = schema.read()
        return self._xml_schema

    @property
    def file_directory(self):
        if not self._file_directory:
            self._file_directory = create_dir_event(self)
        return self._file_directory

    @property
    def file_name(self):
        if not self._file_name:
            self._file_name = f"{self.identifier}.{self.acronym}.xml"
        return self._file_name

    @property
    def file_path(self):
        if not self._file_path:
            self._file_path = "%s/%s" % (self.file_directory, self.file_name)
            _bt_file_path = (
                ""
                if not self.batch
                else self.batch.file_path.replace("batch.xml", "%s" % self.file_name)
            )
            if os.path.exists(_bt_file_path):
                self._file_path = _bt_file_path
        return self._file_path

    @property
    def file_path_xml_schema(self):
        if not self._file_path_xml_schema and self._xml_schema_name:
            self._file_path_xml_schema = "%s/%s" % (
                XML_SCHEMA_PATH,
                self._xml_schema_name,
            )
        return self._file_path_xml_schema

    @property
    def file_path_signed(self):
        if not self._file_path_signed:
            self._file_path_signed = self.file_path.replace(".xml", ".s.xml")
        return self._file_path_signed

    @property
    def json_model_by_action(self):
        return json_model_by_action(self.json_model, self.action)

    @property
    def json_model(self):
        """Esta propriedade retorna o modelo json do evento."""
        if not self._json_model:
            self._json_model = self._load_json_model()
        return self._json_model

    @property
    def event(self):
        if hasattr(self, self.acronym.lower()):
            return getattr(self, self.acronym.lower())
        return self

    @property
    def xml(self):
        if os.path.exists(self.file_path):
            self._xml = _load_data_xml(self.file_path, encoding=None, to_string=False)
        elif not self._xml:
            self._xml = self.generate_xml_with_value()
        return self._xml

    @property
    def xml_diff(self):
        return self.diff_content

    @property
    def xml_signed(self):
        if self._xml_signed is None and self.xml is not None:
            self._xml_signed = self.signer()
        return self._xml_signed

    @property
    def has_exclusion(self):
        if (
            hasattr(self, "modified_by_event")
            and self.modified_by_event.acronym == "s3000"
            and self.modified_by_event.process_status
            in PROCESS_STATUS_EVENT_VALIDS_SENT
        ):
            return True
        if (
            self.closed_by_event
            and self.closed_by_event.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT
        ):
            return True
        return False

    @property
    def is_invalid(self):
        return (
            self.process_status not in VALID_EVENT_STATUS
            or self.xsd_schema_validated is False
            or self.has_exclusion
            or (
                hasattr(self, "modified_by_event")
                and self.modified_by_event.process_status
                in PROCESS_STATUS_EVENT_VALIDS_SENT
                and (
                    self.modified_by_event.action == RECTIFICATION
                    or self.modified_by_event.group == 1
                )
            )
        )

    @property
    def totalizers(self):
        """Este método retorna os totalizadores do evento caso exista.

        Returns:
            list (Event): list of S5001 ou S5002 ou S5011 ou S5012 ou S5501"""
        totalizers = []

        totalizer = getattr(self, "eventconnection_s5001", None)
        if totalizer and totalizer.exists():
            totalizers.append(totalizer.last())
        totalizer = getattr(self, "eventconnection_s5002", None)
        if totalizer and totalizer.exists():
            totalizers.append(totalizer.last())
        totalizer = getattr(self, "eventconnection_s5011", None)
        if totalizer and totalizer.exists():
            totalizers.append(totalizer.last())
        totalizer = getattr(self, "eventconnection_s5012", None)
        if totalizer and totalizer.exists():
            totalizers.append(totalizer.last())
        totalizer = getattr(self, "eventconnection_s5501", None)
        if totalizer and totalizer.exists():
            totalizers.append(totalizer.last())
        return totalizers

    def save(self, **kwargs):
        self.internal = self._internal
        self.group = self._group

        self.ide_evento_tp_amb = esocial_environment()

        self.validate()
        self.search_cache = self._search_cache()
        self.is_invalid_cache = self.is_invalid
        self.has_exclusion_cache = self.has_exclusion
        self.modified_by_event_cache = self.get_modified_by_event_cache()
        self.batch_cache = self.get_batch_cache()

        if not self.pk:
            self.set_name()
            self.set_acronym()

        """Escrita de save com atualização de identifier quando houver IntegrityError"""
        integrity = True
        # while integrity:
        #     try:

        #         self.set_identifier()

        #         with transaction.atomic():
        #             super(Event, self).save(**kwargs)
        #             integrity = False

        #             if not self.internal:
        #                 if 'process_status' in self.diff:
        #                     self.update_dependents()
        #                 self.event.close_previous_events()
        #     except IntegrityError as err:
        #         if f'{err}'.find('duplicate key value violates unique constraint') == 0:
        #             log.info(f'Campo identifier duplicado! Tentará novamente. {self} | {self.identifier} | {self.registry_employee} | {self.registry_person}')
        #             integrity = True
        #         else:
        #             log.exception(err)
        #             raise err
        #     except Exception as err:
        #         log.exception(err)
        #         raise err

        try:
            self.set_identifier()

            with transaction.atomic():
                super(Event, self).save(**kwargs)

                if not self.internal:
                    if "process_status" in self.diff:
                        self.update_dependents()
                    self.event.close_previous_events()
        except IntegrityError as err:
            if f"{err}".find("duplicate key value violates unique constraint") == 0:
                log.info(
                    f"Campo identifier duplicado! {self} | {self.identifier} | {self.registry_employee} | {self.registry_person}"
                )
            else:
                log.exception(err)
                raise err
        except Exception as err:
            log.exception(err)
            raise err

    def validate_delete(self):
        if self.process_status not in CAN_DELETE_EVENT_STATUS:
            raise Exception(
                f"Não é possível remover eventos com Status: {self.get_process_status_display()}"
            )
        return True

    def delete(self, *args, **kwargs):
        self.validate_delete()
        self.close_previous_events(delete=True)
        """Tenta apagar um evento, se puder apagar deve-se apagar o lote pois ele está inválido."""
        batch = self.batches.last()

        super(Event, self).delete(*args, **kwargs)

        if batch:
            batch.delete()

    def delete_esocial(self, task=None):
        """Este método gera o evento de exclusão no eSocial.

        Args:
            task (Task, optional): _description_. Defaults to None.

        Raises:
            Exception: raise exception quando houver qualquer problema no extrator.
        """
        from esocial.extractors.s3000 import S3000Extractor

        event = self.event
        if event.EXCLUSION_TYPE == EXCLUSION_TYPE_S3000:
            S3000Extractor(event, event=event, task=task, exclude=True).run()
        elif event.EXCLUSION_TYPE == EXCLUSION_TYPE_DEFAULT:
            event.extractor()(None, event=event, task=task, exclude=True).run()

    def set_name(self):
        self.name = self._name

    def set_acronym(self):
        if not self.acronym:
            self.acronym = self.__class__.__name__.lower()

    def update_dependents(self):
        """Este método solicita atualização de status de eventos dependentes."""
        for ev in self.dependents.all():
            ev_ = ev.event
            ev_.update_status()

    def _previous_event(self):
        """O evento anterior será o evento do mesmo acronym e oid."""
        return (
            Event.objects.valids_sent()
            .filter(
                oid=self.oid,
                acronym=self.acronym,
                start_validity__lt=self.start_validity,
            )
            .exclude(pk=self.pk)
            .order_by("start_validity")
            .last()
        )

    def _check_previous_event(self, previous_event):
        """Este método realiza checagem para atualizar o previous_event encontrado."""
        return (
            self.process_status == 1
            and previous_event
            and (
                not previous_event.end_validity
                or previous_event.end_validity == self.start_validity
            )
        )

    def close_previous_events(self, delete=False):
        """Este método fecha(preenche end_validity) do evento anterior."""
        if self.CLOSE_PREVIOUS_EVENTS:
            previous_event = self._previous_event()

            if self._check_previous_event(previous_event):
                """Fecha o evento anterior"""
                Event.objects.filter(pk=previous_event.pk).update(
                    end_validity=self.start_validity, closed_by_event=self.pk
                )
            elif self.process_status in (401, 402, 403) or delete is True:
                """Abre o evento anterior"""
                Event.objects.filter(closed_by_event=self.pk).update(
                    end_validity=None, closed_by_event=None
                )

    def update_status(
        self,
        new_status=None,
        save=True,
        force=False,
        ignore_dependencies_not_satisfied=False,
        ignore_has_dependencies=False,
    ):
        """Este método atualiza o process_status do Event. Também remove modify_event quando process_status em
        PROCESS_STATUS_EVENT_SENT_ERROR.

        Modifica status quando não estiver em PROCESS_STATUS_EVENT_VALIDS_SENT.
        Quando em has_dependencies_not_satisfied, status será 5.
        Quando em has_dependencies, status será 2.
        Quando em status em 2, status será 1.
        De outra forma será new_status quando este existir.

        Args:
            new_status (int, optional): novo process_status. Defaults to None.
            save (bool, optional): indicativo se save deve ser realizado. Defaults to True.
            force (bool, optional): indicativo se process_status deve ser aplicado diratamente. Defaults to False.

        Returns:
            process_status(int): process_status
        """
        if self.process_status not in PROCESS_STATUS_EVENT_VALIDS_SENT or force:
            if (
                self.pk
                and self.has_dependencies_not_satisfied
                and not ignore_dependencies_not_satisfied
            ):
                self.process_status = 5  # Dependência não satisfeita
            elif self.pk and self.has_dependencies and not ignore_has_dependencies:
                self.process_status = 2  # Aguardando finalização de dependência
            elif self.pk and self.process_status == 2:
                self.process_status = 1  # Aguardando empacotamento
            elif new_status:
                self.process_status = new_status

        """REMOVE modify_event quando event enviado não estiver nos status correto"""
        if self.process_status in PROCESS_STATUS_EVENT_SENT_ERROR:
            if self.acronym != "s3000":
                if self.modify_event:
                    Event.objects.filter(pk=self.modify_event.pk).update(
                        modified_by_event_cache=""
                    )
                self.modify_event = None

        if self.diff and save:
            self.save()

        return self.process_status

    @classmethod
    def set_deleted(cls, events=[]):
        """Este método marca os events como deleted True.

        Args:
            events (list):
        """
        for event in Event.objects.filter(pk__in=events):
            event = event.event
            if event.process_status in CAN_SET_DELETED_EVENT_STATUS:
                event.deleted = True
                event.save()
                # FIXME: CORRIGIR SAVE PARA EXECUTAR O QUE O DELETE PROPORCIONA #3056
            else:
                message = f"O evento ({event}) não pode ser modificado."
                message += f"<br>Apenas eventos com os seguintes status podem sofrer esta ação: {CAN_SET_DELETED_EVENT_STATUS}."
                raise Exception(message)

    def update_process_status_ignore_validate(self, process_status):
        """Este método atualiza o process_status ignorando as validações.

        Args:
            process_status (int):

        Raises:
            Exception: raise exception caso o new_status não seja o correto.
        """
        if not process_status:
            raise Exception("Novo status não informado!")
        self.update_status(
            new_status=process_status,
            ignore_dependencies_not_satisfied=True,
            ignore_has_dependencies=True,
        )
        return self.get_process_status_display()

    def validate(self):
        return True

    def generate_xml_with_value(self, file_path=None):
        return generate_xml_with_value(self, file_path=file_path)

    def validation_xml_schema(self, assert_test=False):
        return _validation_xml_schema(
            self.xml_schema, self.xml_signed, assert_test=assert_test
        )

    def set_validation_xml_schema(self, assert_test=False):
        """Este método realiza a validação do XML. Utiliza asser_test para testar ou não a validação e apresentar a exception.

        Args:
            assert_test (bool): Se True, não apresenta a exception.

        Returns:
            bool: True se o XML for válido."""
        # TODO: CRIAR MÉTODO PARA APLICAR xsd_schema_validated True EM TODOS OS "FILHOS" DOS EVENTOS RELACIONADOS
        if self.pk:
            self.xsd_schema_validated = self.validation_xml_schema(
                assert_test=assert_test
            )
            if (
                self.process_status in PROCESS_STATUS_EVENT_NOT_SENT
                and "xsd_schema_validated" in self.diff
            ):
                self.save()
            elif assert_test and "xsd_schema_validated" in self.diff:
                message = "válido" if self.xsd_schema_validated else "inválido"
                raise Exception(
                    f"Evento com status: {self.get_process_status_display()}, não pode mudar para {message}."
                )
        return self.xsd_schema_validated

    def signer(self):
        """Este método é reponsável por chamar a assinatura do evento."""
        return _signer_process(self.xml, self.file_path_signed)

    @classmethod
    def call_evaluate_dependency(
        cls,
        acronyms=[],
        event=[],
        oid=None,
        registry_employee=None,
        registry_person=None,
        task=None,
    ):
        """Avaliação dependências: reorganizar. Só para valids_not_send e dependência não satisfeita.

        Args:
            acronyms (list, optional): _description_. Defaults to [].
            event (list, optional): _description_. Defaults to [].
            oid (str, optional): _description_. Defaults to None.
            registry_employee (int, optional): _description_. Defaults to None.
            registry_person (str, optional): _description_. Defaults to None.
            task (Task, optional): _description_. Defaults to None.
        """
        query = Event.objects.filter(
            process_status__in=(1, 2)
        ).without_invalid_xml_schema()
        if event:
            query = query.filter(pk__in=event)
        else:
            if acronyms:
                query = query.filter(acronym__in=acronyms)

            if oid:
                query = query.filter(oid=oid)

            if registry_employee:
                query = query.filter(registry_employee=registry_employee)

            if registry_person:
                query = query.filter(registry_person=registry_person)

        for event in query:
            event = event.event
            event.evaluate_dependency(task=task)

    def _general_dependencies(self):
        config = get_current_config()
        is_s1000 = self.acronym == "s1000"
        return {
            f"{('s1000',)}": [
                {
                    "oid": config.employer.pk,
                    "acronyms": ("s1000",),
                    "required": not is_s1000,
                    "create_if_not_exist": not is_s1000,
                    "filter_validity_in": False,
                }
            ]
        }

    def _previous_event_not_send_query(self):
        """Este método retorna o último evento anterior ao extraído, de mesmo oid e acronym, não enviado."""
        if self.action == EXCLUSION:
            return self.__class__.objects.none()
        return (
            self.__class__.objects.valids_not_sent()
            .filter(
                Q(oid=self.oid)
                & Q(acronym=self.acronym)
                & Q(registry_employee=self.registry_employee)
                & Q(registry_person=self.registry_person)
                & (
                    Q(start_validity__lt=self.start_validity)
                    | Q(group=self.group, action=EXCLUSION)
                )
            )
            .exclude(pk=self.pk)
            .order_by("-start_validity")[0:1]
        )

    def _previous_dependencies(self):
        """Este método seta as dependências anteriores de mesmo acronym, para manter a ordem de precedência no envio."""
        deps = {}
        for event in self._previous_event_not_send_query():
            deps.update(
                {
                    f"('{event.acronym}',)": [
                        {
                            "events": [event],
                            "oid": event.oid,
                            "acronyms": (event.acronym,),
                            "required": False,
                            "create_if_not_exist": False,
                            "validate_function": None,
                        }
                    ]
                }
            )
        return deps

    def _base_dependencies(self):
        """Este método adiciona as dependências do Extractor. Deve ser sobrescrito em cada um."""
        return {}

    def evaluate_dependency(self, task=None):
        """Este método chama a avaliação das dependências após a criação do evento."""
        dependencies = {}
        dependencies.update(self._general_dependencies())
        dependencies.update(self._base_dependencies())
        dependencies.update(self._previous_dependencies())

        self.clean_dependency_not_required()
        for key in dependencies:
            """Encontra dependências requeridas que não possuem mais o evento dependente/não satisfeitas."""
            event_dependency = EventDependency.objects.filter(
                event=self, dependency_acronym=key
            )
            if (
                not event_dependency.exists()
                or event_dependency.filter(dependency__isnull=True).exists()
            ):
                event_dependency.delete()
                for dep in dependencies.get(key):
                    self.add_dependency(**dep, task=task)

    def _find_event_dependency_query(self, acronyms):
        """Este método deve representar a query utilizada em _find_event_dependency para encontrar a dependência.
        Filtra por acronyms. Utiliza o self.start_validity para encontrar validades <= ou
            do grupo 1 com validade igual ao início da obrigatoriedade.

        Returns:
            Event.queryset:"""
        return (
            Event.objects.filter(
                Q(acronym__in=acronyms)
                & (
                    Q(start_validity__lte=self.start_validity)
                    | (
                        Q(group=1)
                        & Q(
                            start_validity=get_current_config().initial_date_start_tables
                        )
                    )
                )
            )
            .exclude(pk=self.pk)
            .valids_by_status()
            .order_by("start_validity")
        )

    def add_dependency(
        self,
        task=None,
        events=[],
        oid=None,
        acronyms=(),
        create_if_not_exist=True,
        required=True,
        validate_function=None,
        evaluate_schema=False,
        start_validity=None,
        filter_query_instance=None,
        dependency={},
        query_filter=None,
        filter_validity_in=True,
        registry_employee=None,
        registry_person=None,
        period=None,
    ):
        """Este metodo adiciona uma dependencia a um evento para o evento em questao.

        Keyword Arguments:
            events {list} -- Uma lista de eventos no qual se deseja depender (default: {[]]})
            oid {Object} -- Um objeto qualquer que será usado pelo extrator
                                    para gerar o evento a depender (default: {None})
            acronyms {tuple} -- Uma lista de acronimos para ser usado na busca por
                                eventos desses acronimos ou ser extraido caso nao
                                exista e a variavel @create_if_not_exist=True.
                                OBS.: Caso necessite extrair o evento a depender,
                                o extrator que sera chamado sera o do primeiro acronimo
                                definido na lista (default: {[]})
            create_if_not_exist {bool} -- Se deve ser criado o evento caso a dependencia seja
                                        obrigatoria (default: {True})
            required {bool} -- Se é obrigatorio ter a dependencia (default: {True})
            validate_function {function} -- function que recebe como parametro um evento e
                                retorna um booleano informando se foi validado (default: {None})
            filter_query_instance {} -- objeto que será propagado ao query_instances_outside quando manage_in_bulk for chamado para filtro
            dependency {} -- {acronym: dependency(Event)} objeto que será a dependência, este parâmetro evita a chamada de
                 _find_event_dependency
            query_filter {} -- query filter utilizado para filtro alternativo ao inst_outside
            filter_validity_in(bool) -- default True, indica se o queryset validity_in será aplicado

        Raises:
            Exception -- [description]

        Returns:
            [Event] -- O evento encontrado caso exista ou tenha sido criado e None caso contrario
        """
        from esocial.extractors.base import Factory

        def final_status(message=None):
            if task:
                task.info(
                    msg=f"Não consegui resolver a dependência de {self} para {acronyms} <br /> pois {message}",
                    type_of=2,
                )

        def _set_dependency(events_map):
            """Este método cria as dependências (EventDependency)."""
            for acr in events_map:
                event = events_map.get(acr, None)
                if event and event.event != self.event:
                    """Adicionando a dependência caso o event exista e não seja o próprio event(self)
                    Essa validação é necessária para não gerar uma auto-dependência o que geraria
                    uma impossibilidade de mudança de estado de event"""
                    if event.xsd_schema_validated:
                        if callable(validate_function):
                            satisfied_dependency = validate_function(event)
                            if required and not satisfied_dependency:
                                _obj, _created = (
                                    EventDependency.objects.update_or_create(
                                        event=self,
                                        dependency_acronym=f"{acronyms}",
                                        required=required,
                                        dependency_oid=oid,
                                    )
                                )
                                self.update_status()
                                final_status(
                                    message="a dependência é requerida, mas a validação não foi satisfeita"
                                )
                                return None
                        if not self.pk:
                            print(
                                f">>>>>>> SELF:  {self} {self.registry_employee} {self.registry_person}"
                            )
                            print(f">>>>>>> EVENT: {event}")
                            print(f">>>>>>> SETTINGS DEPENDENCY WITHOUT PK {acronyms}")
                        elif (
                            not self.dependencies.filter(pk=event.pk).exists()
                            and not EventDependency.objects.filter(
                                event=event, dependency=self
                            ).exists()
                        ):
                            _obj, _created = EventDependency.objects.update_or_create(
                                event=self,
                                dependency_acronym=f"{acronyms}",
                                dependency=event,
                                required=required,
                            )
                            self.update_status()
                        return event

                    else:
                        self.update_status()
                        final_status(message="o xsd (da dependência) não é válido")
                else:
                    if required:
                        message = "a dependência é requerida, mas o evento não deve depender dele mesmo"
                        if not event:
                            message = f"a dependência é requerida, mas o evento {acr} não existe"
                        _obj, _created = EventDependency.objects.update_or_create(
                            event=self,
                            dependency_acronym=f"{acronyms}",
                            required=required,
                            dependency_oid=oid,
                        )
                        self.update_status()
                        final_status(message=message)

        def _find_event_dependency(acronyms):
            """Tentando encontrar o último evento para o object(inst_outside) que se depende"""
            _event_dep = self._find_event_dependency_query(acronyms)
            if oid:
                _event_dep = _event_dep.filter(oid=oid)

            if registry_employee:
                _event_dep = _event_dep.filter(registry_employee=registry_employee)

            if registry_person:
                _event_dep = _event_dep.filter(registry_person=registry_person)

            """Deixa apenas o último."""
            event_pk = _event_dep.last().pk if _event_dep.last() else None
            _event_dep = _event_dep.filter(pk=event_pk)

            """Checa se o que sobrou está dentro da validade."""
            if filter_validity_in:
                _event_dep = _event_dep.validity_in(
                    self.start_validity, self.end_validity
                )

            if query_filter:
                _event_dep = _event_dep.filter(query_filter)

            return _event_dep.order_by("start_validity").last()

        """
            Tenta encontrar o evento atráves de _find_event_dependency.
            Se não encontrar, tenta criar um novo evento.
        """
        events_map = {}
        if not events:
            event = _find_event_dependency(acronyms)
            if not event and create_if_not_exist:
                for acr in acronyms:
                    _kwargs = {
                        "start_competence": self.start_validity,
                        "end_competence": self.end_validity,
                        "task": task,
                        "filter_query_instance": filter_query_instance,
                        "registry": registry_employee,
                        "registry_person": registry_person,
                        "period": period,
                        "dependency": True,
                    }
                    Factory.get_factory(acr).manage_in_bulk(**_kwargs)
                event = _find_event_dependency(acronyms)
                if event:
                    events_map.update({acr: event})
            elif event:
                events_map.update({event.event.acronym: event})
        else:
            for evt in events:
                events_map.update({evt.event.acronym: evt})

        if not events_map and required:
            _obj, _created = EventDependency.objects.update_or_create(
                event=self,
                dependency_acronym=f"{acronyms}",
                required=required,
                dependency_oid=oid,
            )
            self.update_status()
            final_status(
                message=f"A dependência {acronyms} é requerida, mas a validação não foi satisfeita"
            )
            return None

        try:
            _set_dependency(events_map=events_map)
        except Exception as err:
            log.exception(err)
            print(err)
            print(self)
            print(events_map)
            raise err

    def clean_dependency_not_required(self):
        """Este método apaga as dependências não requeridas."""
        for dep in self.eventdependency_event.filter(required=False):
            dep.delete()

    @classmethod
    def extractor(cls, acronym=None):
        if not acronym:
            acronym = cls._acronym()
        _module = importlib.import_module("esocial.extractors.%s" % (acronym.lower()))
        return getattr(_module, "%sExtractor" % acronym.upper())

    @classmethod
    def factory(cls, acronym=None):
        if not acronym:
            acronym = cls._acronym()
        _module = importlib.import_module("esocial.extractors.%s" % (acronym.lower()))
        return getattr(_module, "%sFactory" % acronym.upper())

    def compare_fields(
        self, other, fields=[], exclude_fields=[], map_fields={}, direction="R"
    ):
        """Compara fields entre dois eventos ou entre um evento e um dicionario

        Arguments:
            other {Event or dict} -- esocial.Event ou dict que se desejar comparar com
            o evento que esta chamando o metodo

        Keyword Arguments:
            exclude_fields {list} -- Fields que se deseja excluir da comparacao (default: {[]})
            fields {list} -- Fields que se deseja comparar (default: {[]})
            direction {str} -- Direcao da comparacao (default: {'L'})
                R: RIGHT - os fields a serem comparados serão os existentes em other
                L: LEFT - os fields a serem comparadas serão os existentes em self
                B: BOTH - os fields a serem comparados serão os existentes em ambos (L e R)

        Returns:
            bool -- retorna se sao iguais ou diferentes
        """
        diff = {}
        # TODO: Adicionar ao _exclude_fields os fields definidos na variavel de classe de fields não sensíveis
        _exclude_fields = copy.deepcopy(exclude_fields)
        _exclude_fields += [
            fldn.name.replace("_id", "") for fldn in Event._meta.get_fields()
        ]
        _exclude_fields += ["event_ptr", "xmlns", "_class_"]
        _fieldsr = _fieldsl = _fieldsr_mm = _fieldsl_mm = []
        cls_l = self.__class__.__name__
        cls_r = (
            other.get("_class_", "").__name__
            if isinstance(other, dict)
            else other.__class__.__name__
        )

        if direction in ["R", "B"]:
            if isinstance(other, dict):
                _fieldsr = [k for k in other if not isinstance(other.get(k), list)]
                _fieldsr_mm = [k for k in other if isinstance(other.get(k), list)]
            else:
                _fieldsr = [
                    f.name for f in other._meta.fields if f.model == other.__class__
                ]
                _fieldsr_mm = [ff.name for ff in other._meta.many_to_many]
        if direction in ["L", "B"]:
            _fieldsl = [f.name for f in self._meta.fields if f.model == self.__class__]
            _fieldsl_mm = [ff.name for ff in self._meta.many_to_many]

        fields_locals = _fieldsr + _fieldsl
        fields_to_compare = set(fields_locals) - set(_exclude_fields)
        if fields:
            fields_to_compare.intersection_update(fields)

        if cls_l == cls_r:
            map_fields = {}

        for f in fields_to_compare:
            f_map = map_fields.get(f, f)
            other_value = (
                other.get(f, None)
                if isinstance(other, dict)
                else getattr(other, f, None)
            )
            if getattr(self, f_map, None) != other_value:
                diff[f] = [getattr(self, f_map, None), other_value]

        fields_mm = _fieldsr_mm + _fieldsl_mm
        fields_to_compare = set(fields_mm) - set(_exclude_fields)
        if fields:
            fields_to_compare.intersection_update(fields)
        oids_l = oids_r = set([])
        for f in fields_to_compare:
            if hasattr(self, f):
                oids_l = set([obj.oid for obj in getattr(self, f).all()])
            if isinstance(other, dict):
                oids_r = set([obj.get("oid", None) for obj in other.get(f, [])])
            else:
                oids_r = set([obj.oid for obj in getattr(other, f).all()])
            if oids_l != oids_r and (oids_l or oids_r):
                if not diff.get(f):
                    diff[f] = []
                diff[f].append({"oids": [oids_l, oids_r]})
            elif oids_l:
                list_objs_r = (
                    other.get(f, [])
                    if isinstance(other, dict)
                    else getattr(self, f, [])
                )
                for obj_r in list_objs_r:
                    oid = (
                        obj_r.get("oid", None) if isinstance(obj_r, dict) else obj_r.oid
                    )
                    try:
                        obj_l = getattr(self, f).get(oid=oid)
                    except Exception as err:
                        log.exception(err)
                        log.info(getattr(self, f))
                        log.info(f"obj_r: {obj_r}")
                        log.info(f"f: {f}")
                        log.info(f"oid: {oid}")
                    diff_mm = obj_l.compare_fields(
                        obj_r,
                        fields=fields,
                        exclude_fields=_exclude_fields,
                        direction=direction,
                    )
                    if diff_mm:
                        if not diff.get(f):
                            diff[f] = []
                        diff[f].append(diff_mm)

        return diff

    def employee_cpf(self):
        """Este método é utilizado para retornar o cpf contido em algum campo do evento."""
        return None

    def get_modified_by_event_cache(self):
        return f"{getattr(self, 'modified_by_event', '')}"

    def get_batch_cache(self):
        if self.pk:
            batch = self.batch
            return f"{batch}" if batch else ""
        return ""

    def update_cache(self):
        """Este método atualiza os campos de cache: is_invalid_cache e has_exclusion_cache em função das propriedades
        is_invalid e has_exclusion."""
        self.is_invalid_cache = self.is_invalid
        self.has_exclusion_cache = self.has_exclusion
        self.modified_by_event_cache = self.get_modified_by_event_cache()
        self.batch_cache = self.get_batch_cache()

        if self.diff:
            try:
                self.save()
            except Exception as err:
                log.exception(err)

    def update_totalizer(self):
        """Este método atualiza os campos de cache do totalizador associado, em função das propriedades is_invalid e has_exclusion."""
        for totalizer in self.totalizers:
            totalizer.is_invalid_cache = self.is_invalid
            totalizer.has_exclusion_cache = self.has_exclusion
            totalizer.deleted = (
                totalizer.is_invalid_cache or totalizer.has_exclusion_cache
            )
            if totalizer.diff:
                try:
                    totalizer.save()
                except Exception as err:
                    log.exception(err)

    def repport_success(self):
        """Este método modifica o process_status para "Sucesso informado localmente"(201),
        por solicitação do usuário quando process_status for 401."""
        event = self.event
        if event.process_status in [401, 210]:
            event.update_status(new_status=201)

    def repport_error(self):
        """Este método modifica o process_status para "Erro informado localmente"(401),
        por solicitação do usuário quando process_status for 201."""
        event = self.event
        if event.process_status in [201, 210]:
            event.process_status = 401
            event.save()


class EventDependencyManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(environment=esocial_environment())


class EventDependencyAllManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class EventDependency(AuditTimestampModel):
    event = models.ForeignKey(
        "Event",
        related_name="eventdependency_event",
        verbose_name="Dependente",
        on_delete=models.CASCADE,
    )
    dependency = models.ForeignKey(
        "Event",
        related_name="eventdependency_dependency",
        verbose_name="Dependência",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    dependency_acronym = models.CharField(max_length=50)
    dependency_oid = models.CharField(
        "ID objeto origem", db_index=True, max_length=32, null=True, blank=True
    )
    required = models.BooleanField(default=False, blank=True)
    environment = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )

    objects = EventDependencyManager()
    objects_all = EventDependencyAllManager()

    def __str__(self):
        message = "{} depends on {}".format(self.event.acronym, self.dependency_acronym)
        if self.dependency_oid:
            message = "{} - {} - {}".format(
                message, self.dependency_oid, self.dependency
            )
        return message

    def save(self, *args, **kwargs):
        if self.dependency and not self.dependency_acronym:
            self.dependency_acronym = f"{(self.dependency.acronym,)}"
        if self.dependency and not self.dependency_oid:
            self.dependency_oid = self.dependency.oid
        if not self.pk:
            self.environment = esocial_environment()
        super(EventDependency, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super(EventDependency, self).delete(*args, **kwargs)


class Register(Event):
    # TODO: AGENDAR REMOÇÃO DESTE MODELO E CONSEQUENTEMENTE DOS CAMPOS
    xmlns_deprecated = models.CharField(max_length=256)
    ide_evento_tp_amb_deprecated = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "TYPE_ENV"), default=2
    )
    ide_evento_proc_emi_deprecated = models.PositiveIntegerField(default=1)
    ide_evento_ver_proc_deprecated = models.CharField(max_length=20)
    ide_evento_ind_apuracao_deprecated = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "INDICATIVE_ASCERTAINMENT_PERIOD"),
        null=True,
        blank=True,
    )
    ide_evento_per_apur_deprecated = models.CharField(
        max_length=7, null=True, blank=True
    )
    ide_evento_ind_retif_deprecated = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "INDICATIVE_TYPE_INFORMATION"),
        null=True,
        blank=True,
    )
    ide_evento_nr_recibo_deprecated = models.CharField(
        max_length=40, null=True, blank=True
    )
    ide_empregador_tp_insc_deprecated = models.PositiveIntegerField(default=1)
    ide_empregador_nr_insc_deprecated = models.CharField(max_length=15)

    class Meta:
        abstract = True


class RemunOutrEmpr(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class ProcJudTrab(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    proc_jud_trab_tp_trib = models.PositiveIntegerField(null=True, blank=True)
    proc_jud_trab_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    proc_jud_trab_cod_susp = models.PositiveIntegerField(null=True, blank=True)


class InfoCpCalc(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5001."""
    info_cp_calc_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    info_cp_calc_vr_cp_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cp_calc_vr_desc_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoCategIncid(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5001."""
    info_categ_incid_matricula = models.CharField(max_length=30, null=True, blank=True)
    info_categ_incid_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_categ_incid_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    info_per_ref = models.ManyToManyField(
        "InfoPerRef", related_name="infoperref_infocategincid"
    )
    info_base_cs = models.ManyToManyField("InfoBaseCS", related_name="infobasecs_s5001")


class InfoBaseCS(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    info_base_cs_ind13 = models.PositiveIntegerField(null=True, blank=True)
    info_base_cs_tp_valor = models.PositiveIntegerField(null=True, blank=True)
    info_base_cs_valor = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class CalcTerc(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    calc_terc_tp_cr = models.PositiveIntegerField()
    calc_terc_vr_cs_seg_terc = models.DecimalField(max_digits=14, decimal_places=2)
    calc_terc_vr_desc_terc = models.DecimalField(max_digits=14, decimal_places=2)
    # info_categ_incid = models.ForeignKey(InfoCategIncid, on_delete=models.CASCADE)


class InfoPerRef(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    info_per_ref_per_ref = models.CharField(max_length=7)
    ide_adc = models.ManyToManyField("IdeAdc", related_name="ideadc_infoperref")
    det_info_per_ref = models.ManyToManyField(
        "DetInfoPerRef", related_name="detinfoperref_infoperref"
    )


class DetInfoPerRef(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    det_info_per_ref_ind13 = models.PositiveIntegerField()
    det_info_per_ref_tp_vr_per_ref = models.PositiveIntegerField()
    det_info_per_ref_vr_per_ref = models.DecimalField(max_digits=14, decimal_places=2)


class DemonstrativeTot(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5002."""
    dm_dev_per_ref = models.CharField(max_length=7, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    dm_dev_tp_pgto = models.PositiveIntegerField()
    dm_dev_dt_pgto = models.DateField()
    dm_dev_cod_categ = models.PositiveIntegerField()
    dm_dev_info_ir = models.ManyToManyField(
        "InfoIrrf", related_name="dmdevinfoir_demonstrativetot"
    )
    tot_apur_men = models.ManyToManyField(
        "MonthlyCalculatedIrrf", related_name="dmdevinfoir_demonstrativetot"
    )

    def delete(self, *args, **kwargs):
        for obj in self.dm_dev_info_ir.all():
            obj.delete()
        for obj in self.tot_apur_men.all():
            obj.delete()
        super(DemonstrativeTot, self).delete(*args, **kwargs)


class InfoIrrf(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5002."""
    tp_info_ir = models.PositiveIntegerField(null=True, blank=True)
    valor = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    info_ir_desc_rendimento = models.CharField(max_length=255, null=True, blank=True)


class MonthlyCalculatedIrrf(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5002 e S5012."""
    cr_men = models.CharField(max_length=6, null=True, blank=True)
    vlr_cr_men = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    apur_dia = models.ManyToManyField(
        "DayCalculatedIrrf", related_name="dmdevinfoir_demonstrativetot"
    )

    def delete(self, *args, **kwargs):
        for obj in self.apur_dia.all():
            obj.delete()
        super(MonthlyCalculatedIrrf, self).delete(*args, **kwargs)


class DayCalculatedIrrf(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    """Usado em S5002 e S5012."""

    per_apur_dia = models.PositiveIntegerField(null=True, blank=True)
    cr_dia = models.CharField(max_length=6, null=True, blank=True)
    vlr_cr_dia = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class BasesRemun(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    bases_remun_ind_incid = models.PositiveIntegerField(null=True, blank=True)
    bases_remun_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    bases_cp_vr_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp00 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp15 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp20 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp25 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp00_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp15_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp20_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_bc_cp25_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp00_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp15_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp20_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_susp_bc_cp25_va = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_desc_sest = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_calc_sest = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_desc_senat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_calc_senat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_sal_fam = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_cp_vr_sal_mat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoCREstab(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    info_cr_estab_tp_cr = models.PositiveIntegerField(null=True, blank=True)
    info_cr_estab_vr_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cr_estab_vr_susp_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoCRContrib(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    tp_cr = models.PositiveIntegerField(null=True, blank=True)
    vr_cr = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    vr_cr_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoTribute(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    per_ref = models.CharField(max_length=7)
    info_cr_contrib = models.ManyToManyField(
        "InfoCRContrib", related_name="info_cr_contrib_s5501"
    )
    info_cr_irrf = models.ManyToManyField(
        "InfoCRContrib", related_name="info_cr_irrf_s5501"
    )


class Dependent(Event):
    NAME = "Dependente"
    INTERNAL = True

    dependente_tp_dep = models.CharField(max_length=2, null=True, blank=True)
    dependente_nm_dep = models.CharField(max_length=70, null=True, blank=True)
    dependente_dt_nascto = models.DateField(null=True, blank=True)
    dependente_cpf_dep = models.CharField(max_length=20, null=True, blank=True)
    dependente_dep_irrf = models.CharField(max_length=1, null=True, blank=True)
    dependente_dep_sf = models.CharField(max_length=1, null=True, blank=True)
    dependente_inc_trab = models.CharField(max_length=1, null=True, blank=True)
    dependente_sexo_dep = models.CharField(max_length=1, null=True, blank=True)
    dependente_inc_fis_men = models.CharField(max_length=1, null=True, blank=True)
    dependente_descr_dep = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Dependent: {self.dependente_nm_dep} - {self.dependente_dt_nascto}"


class WorkHourInterval(Event):
    GROUP = 1
    NAME = "Intervalo de horário"
    INTERNAL = True

    horario_intervalo_tp_interv = models.PositiveIntegerField(null=True, blank=True)
    horario_intervalo_dur_interv = models.PositiveIntegerField(null=True, blank=True)
    horario_intervalo_ini_interv = models.CharField(max_length=4, null=True, blank=True)
    horario_intervalo_term_interv = models.CharField(
        max_length=4, null=True, blank=True
    )


class Process(Event):
    NAME = "Profissional de Saúde"
    INTERNAL = True

    ide_processo_tp_proc = models.PositiveIntegerField(blank=True, default=1)
    ide_processo_nr_proc = models.CharField(max_length=20, blank=True, default="")
    ide_processo_ext_decisao = models.PositiveIntegerField(blank=True, default=1)
    ide_processo_cod_susp = models.PositiveIntegerField(blank=True, default=1)

    def __str__(self):
        return "%s" % self.ide_processo_nr_proc


class Schedule(Event):
    NAME = "Profissional de Saúde"
    INTERNAL = True

    horario_dia = models.PositiveIntegerField(null=True, blank=True)
    horario_cod_hor_contrat = models.CharField(max_length=30, null=True, blank=True)


class InfoSuspensao(Event):
    NAME = "Informação de Suspensão - Proc. Judicial"
    INTERNAL = True

    info_susp_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    info_susp_ind_susp = models.CharField(max_length=2, null=True, blank=True)
    info_susp_dt_decisao = models.DateField(null=True, blank=True)
    info_susp_ind_deposito = models.CharField(max_length=1, null=True, blank=True)


class ProcJudTerceiro(Event):
    NAME = "Proc. Judicial de terceiros"
    INTERNAL = True

    proc_jud_terceiro_cod_terc = models.CharField(max_length=4, null=True, blank=True)
    proc_jud_terceiro_nr_proc_jud = models.CharField(
        max_length=20, null=True, blank=True
    )
    proc_jud_terceiro_cod_susp = models.PositiveIntegerField(null=True, blank=True)


class IdeProcesso(Event):
    NAME = "Processo de Suspensão"
    INTERNAL = True

    ide_processo_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    ide_processo_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    ide_processo_ext_decisao = models.PositiveIntegerField(null=True, blank=True)
    ide_processo_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    ide_processo_tp_trib = models.PositiveIntegerField(null=True, blank=True)


class HealthCertificate(Event):

    NAME = "Profissional de Saúde"
    INTERNAL = True

    info_atestado_cod_cid = models.CharField(max_length=4, null=True, blank=True)
    info_atestado_qtd_dias_afast = models.PositiveIntegerField(null=True, blank=True)
    emitente_nm_emit = models.CharField(max_length=70, null=True, blank=True)
    emitente_ide_oc = models.PositiveIntegerField(null=True, blank=True)
    emitente_nr_oc = models.CharField(max_length=14, null=True, blank=True)
    emitente_uf_oc = models.CharField(max_length=2, null=True, blank=True)

    def __str__(self):
        return "{} - {}".format(self.info_atestado_cod_cid, self.emitente_nm_emit)


class ChildSupport(Event):

    NAME = "Beneficiários de Pensão Alimentícia"
    INTERNAL = True

    pen_alim_cpf_benef = models.CharField(max_length=11, null=True, blank=True)
    pen_alim_dt_nascto_benef = models.DateField(null=True, blank=True)
    pen_alim_nm_benefic = models.CharField(max_length=70, null=True, blank=True)
    pen_alim_vlr_pensao = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class PaymentDetail(Event):

    NAME = "Detalhamento do pagamento efetuado"
    INTERNAL = True

    per_ref = models.CharField(max_length=7, null=True, blank=True)
    ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    ind_pgto_tt = models.CharField(max_length=1, null=True, blank=True)
    vr_liq = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    nr_rec_arq = models.CharField(max_length=40, null=True, blank=True)
    ret_pgto_tot = models.ManyToManyField(
        "DemonstrativeItem", related_name="totalpayments"
    )
    info_pgto_parc = models.ManyToManyField(
        "DemonstrativeItem", related_name="parcpayments"
    )


class InfoPgto(Event):

    NAME = f"{__name__}"
    INTERNAL = True

    info_pgto_dt_pgto = models.DateField()
    info_pgto_tp_pgto = models.PositiveIntegerField()
    info_pgto_per_ref = models.CharField(max_length=7)
    info_pgto_ide_dm_dev = models.CharField(max_length=30)
    info_pgto_vr_liq = models.DecimalField(max_digits=14, decimal_places=2)
    info_pgto_ext_ind_nif = models.PositiveIntegerField(null=True, blank=True)
    info_pgto_ext_nif_benef = models.CharField(max_length=30, null=True, blank=True)
    info_pgto_ext_frm_tribut = models.CharField(max_length=2, null=True, blank=True)
    end_ext_end_dsc_lograd = models.CharField(max_length=80, null=True, blank=True)
    end_ext_end_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    end_ext_end_complem = models.CharField(max_length=30, null=True, blank=True)
    end_ext_end_bairro = models.CharField(max_length=60, null=True, blank=True)
    end_ext_end_cidade = models.CharField(max_length=40, null=True, blank=True)
    end_ext_end_estado = models.CharField(max_length=40, null=True, blank=True)
    end_ext_end_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    end_ext_telef = models.CharField(max_length=15, null=True, blank=True)


class DedDependente(Event):
    """Dedução do rendimento tributável relativa a dependentes."""

    NAME = f"{__name__}"
    INTERNAL = True

    ded_depen_tp_rend = models.PositiveIntegerField()
    ded_depen_cpf_dep = models.CharField(max_length=11)
    ded_depen_vlr_ded_dep = models.DecimalField(max_digits=14, decimal_places=2)


class DedPenAlim(Event):
    """Informação dos beneficiários da pensão alimentícia."""

    NAME = f"{__name__}"
    INTERNAL = True

    pen_alim_tp_rend = models.PositiveIntegerField()
    pen_alim_cpf_dep = models.CharField(max_length=11)
    pen_alim_vlr_ded_pen_alim = models.DecimalField(max_digits=14, decimal_places=2)


class InfoIRDepedente(Event):
    NAME = f"{__name__}"
    INTERNAL = True

    info_dep_cpf_dep = models.CharField(max_length=11)
    info_dep_dt_nascto = models.DateField()
    info_dep_nome = models.CharField(max_length=70)
    info_dep_dep_irrf = models.CharField(max_length=1, null=True, blank=True)
    info_dep_tp_dep = models.CharField(max_length=2, null=True, blank=True)
    info_dep_descr_dep = models.CharField(max_length=100, null=True, blank=True)


class InfoIRPrevidCompl(Event):
    """Informações relativas a planos de previdência complementar."""

    NAME = "InfoIRPrevidCompl"
    INTERNAL = True

    previd_compl_tp_prev = models.PositiveIntegerField()
    previd_compl_cnpj_entid_pc = models.CharField(max_length=14)
    previd_compl_vlr_ded_pc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_ded_pc13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_patroc_funp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    previd_compl_vlr_patroc_funp13 = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoValoresProcRet(Event):
    """Informações de processos relacionados a não retenção de tributos ou a depósitos judiciais."""

    NAME = "InfoValoresProcRet"
    INTERNAL = True

    info_valores_vlr_n_retido = models.DecimalField(max_digits=14, decimal_places=2)
    info_valores_vlr_dep_jud = models.DecimalField(max_digits=14, decimal_places=2)
    info_valores_vlr_cmp_ano_cal = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_cmp_ano_ant = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_valores_vlr_rend_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class DedBenfPen(Event):
    """Informação das deduções suspensas por dependentes e beneficiários da pensão alimentícia."""

    NAME = "DedBenfPen"
    INTERNAL = True

    benef_pen_cpf_dep = models.CharField(max_length=11)
    benef_pen_vlr_depen_susp = models.DecimalField(max_digits=14, decimal_places=2)


class DedSuspProcRet(Event):
    """Detalhamento das deduções com exigibilidade suspensa."""

    NAME = "DedSuspProcRet"
    INTERNAL = True

    ded_susp_ind_tp_deducao = models.PositiveIntegerField()
    ded_susp_vlr_ded_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ded_susp_cnpj_entid_pc = models.CharField(max_length=14, null=True, blank=True)
    ded_susp_vlr_patroc_funp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ded_susp_benf_pen = models.ManyToManyField(
        "DedBenfPen", related_name="dedsuspprocret"
    )


class InfoIRProcRet(Event):
    """Informações de valores relacionados a não retenção de tributos ou a depósitos judiciais."""

    NAME = "InfoIRProcRet"
    INTERNAL = True

    info_proc_ret_tp_proc_ret = models.PositiveIntegerField()
    info_proc_ret_nr_proc_ret = models.CharField(max_length=21)
    info_proc_ret_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    info_valores_proc_ret = models.ManyToManyField(
        "InfoValoresProcRet", related_name="infoirprocret"
    )
    ded_susp_proc_ret = models.ManyToManyField(
        "DedSuspProcRet", related_name="infoirprocret"
    )


class InfoDepSau(Event):
    """Informações de dependente de plano de saúde coletivo empresarial."""

    NAME = "InfoDepSau"
    INTERNAL = True

    info_dep_sau_cpf_dep = models.CharField(max_length=11)
    info_dep_sau_vlr_saude_dep = models.DecimalField(max_digits=14, decimal_places=2)


class InfoPlanSaude(Event):
    """Plano de saúde coletivo. Identificação da(s) operadora(s) de plano privado coletivo empresarial de assistência à saúde."""

    NAME = "InfoPlanSaude"
    INTERNAL = True

    plan_saude_cnpj_oper = models.CharField(max_length=14)
    plan_saude_reg_ans = models.CharField(max_length=6)
    plan_saude_vlr_saude_tit = models.DecimalField(max_digits=14, decimal_places=2)
    info_dep_saude = models.ManyToManyField("InfoDepSau", related_name="infoplansaude")


class InfodetReembTit(Event):
    """Informações relativas a reembolsos efetuados no período de apuração (perApur) pelo empregador
    ao trabalhador referente a despesas médicas ou odontológicas pagas pelo trabalhador a prestadores de serviços de saúde.
    """

    NAME = "InfodetReembTit"
    INTERNAL = True

    det_reemb_tit_tp_insc = models.PositiveIntegerField()
    det_reemb_tit_nr_insc = models.CharField(max_length=14)
    det_reemb_tit_vlr_reemb = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_reemb_tit_vlr_reemb_ant = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class InfoReembMed(Event):
    """Informação de reembolso do titular do plano de saúde coletivo empresarial."""

    NAME = "InfoReembMed"
    INTERNAL = True

    info_reemb_med_ind_org_reemb = models.PositiveIntegerField()
    info_reemb_med_cnpj_oper = models.CharField(max_length=14)
    info_reemb_med_reg_ans = models.CharField(max_length=6)
    info_det_reemb_tit = models.ManyToManyField(
        "InfodetReembTit", related_name="inforeembmed"
    )
    info_reemb_dep_cpf_benef = models.CharField(max_length=11, null=True, blank=True)


class InfoIrCr(Event):
    """Informações de Imposto de Renda, por Código de Receita - CR."""

    NAME = "InfoIrCr"
    INTERNAL = True

    info_ircr_tp_cr = models.CharField(max_length=6, null=True, blank=True)
    ded_dependente = models.ManyToManyField("DedDependente", related_name="infoircr")
    ded_pen_alim = models.ManyToManyField("DedPenAlim", related_name="infoircr")
    info_ir_previd_compl = models.ManyToManyField(
        "InfoIRPrevidCompl", related_name="infoircr"
    )
    info_ir_proc_ret = models.ManyToManyField("InfoIRProcRet", related_name="infoircr")


class InfoIrComplemen(Event):

    NAME = "Informações de imposto de renda"
    INTERNAL = True

    info_ir_dependente = models.ManyToManyField(
        "InfoIRDepedente", related_name="infoircomplem"
    )
    info_ir_complem_dt_laudo = models.DateField(null=True, blank=True)
    per_ant_per_ref_ajuste = models.CharField(max_length=7, null=True, blank=True)
    per_ant_nr_rec1210_orig = models.CharField(max_length=23, null=True, blank=True)
    info_ir_cr = models.ManyToManyField("InfoIrCr", related_name="infoircomplem")
    info_plan_saude = models.ManyToManyField(
        "InfoPlanSaude", related_name="infoircomplem"
    )
    info_ir_remb_med = models.ManyToManyField(
        "InfoReembMed", related_name="infoircomplem"
    )


class DetPgtoFer(Event):
    NAME = "Detalhamento do Pagamento de Férias"
    INTERNAL = True

    det_pgto_fer_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    det_pgto_fer_matricula = models.CharField(max_length=30, null=True, blank=True)
    det_pgto_fer_dt_ini_goz = models.DateField(null=True, blank=True)
    det_pgto_fer_qt_dias = models.PositiveIntegerField(null=True, blank=True)
    det_pgto_fer_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_pgto_fer_det_rubr_fer = models.ManyToManyField(
        "DemonstrativeItem", related_name="det_pgto_fer_det_rubr_fer_S1210"
    )


class DetPgtoAnt(Event):

    NAME = "Pagamento anterior ao eSocial"
    INTERNAL = True

    det_pgto_ant_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_pgto_ant = models.ForeignKey(
        "InfoPgtoAnt", related_name="info_pgto_ant_S1210", on_delete=models.CASCADE
    )


class InfoPgtoAnt(Event):

    NAME = "Detalhamento de pagamento anterior ao eSocial"
    INTERNAL = True

    info_pgto_ant_tp_bc_irrf = models.CharField(max_length=2, null=True, blank=True)
    info_pgto_ant_vr_bc_irrf = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )


class IdeEstabLot(Event):

    NAME = "Estabelecimento Lote"
    INTERNAL = True

    tp_insc = models.PositiveIntegerField(null=True, blank=True)
    nr_insc = models.CharField(max_length=14, null=True, blank=True)
    cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    qtd_dias_av = models.PositiveIntegerField(null=True, blank=True)
    payroll = models.PositiveIntegerField(null=True, blank=True)
    ide_adc = models.CharField("Ide Adc", max_length=12, null=True, blank=True)

    remun_period = models.ManyToManyField("RemunPeriod", related_name="ideestablot")

    def delete(self, *args, **kwargs):
        for obj in self.remun_period.all():
            obj.delete()
        super(IdeEstabLot, self).delete(*args, **kwargs)


class IdeEstabLot1207(Event):

    NAME = "Estabelecimento Lote s1207"
    INTERNAL = True

    tp_insc = models.PositiveIntegerField(null=True, blank=True)
    nr_insc = models.CharField(max_length=14, null=True, blank=True)
    cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    qtd_dias_av = models.PositiveIntegerField(null=True, blank=True)
    ide_adc = models.CharField("Ide Adc", max_length=12, null=True, blank=True)
    itens_remun = models.ManyToManyField(
        "DemonstrativeItem", related_name="ideestablot1207"
    )

    def delete(self, *args, **kwargs):
        for obj in self.itens_remun.all():
            obj.delete()
        super(IdeEstabLot1207, self).delete(*args, **kwargs)


class IdeEstabLot5001(Event):

    NAME = "Estabelecimento Lote Totalizadores S5001"
    INTERNAL = True

    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    """Estabelicimento do S5001"""
    info_categ_incid = models.ManyToManyField(
        "InfoCategIncid", related_name="infocategincid_ideestablot"
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_categ_incid.all():
            obj.delete()
        super(IdeEstabLot5001, self).delete(*args, **kwargs)


class IdeEstabLot5011(Event):

    NAME = "Estabelecimento Lote Totalizadores S5011"
    INTERNAL = True

    ide_estab_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_nr_insc = models.CharField(max_length=14, null=True, blank=True)

    info_estab_cnae_prep = models.PositiveIntegerField(null=True, blank=True)
    info_estab_cnpj_prep = models.CharField(max_length=14, null=True, blank=True)
    info_estab_cnpj_resp = models.CharField(max_length=14, null=True, blank=True)
    info_estab_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    info_estab_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_estab_aliq_rat_ajust = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    info_estab_ref_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    info_estab_ref_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    info_estab_ref_aliq_rat_ajust = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )

    ide_lotacao_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    ide_lotacao_fpas = models.PositiveIntegerField(null=True, blank=True)
    ide_lotacao_cod_tercs = models.CharField(max_length=4, null=True, blank=True)
    ide_lotacao_cod_tercs_susp = models.CharField(max_length=4, null=True, blank=True)

    info_terc_susp_cod_terc = models.CharField(max_length=4, null=True, blank=True)

    bases_remun = models.ManyToManyField(
        "BasesRemun", related_name="basesremun_ideestablot5011"
    )
    info_cr_estab = models.ManyToManyField(
        "InfoCREstab", related_name="crestab_ideestablot5011"
    )

    def delete(self, *args, **kwargs):
        for obj in self.bases_remun.all():
            obj.delete()
        for obj in self.info_cr_estab.all():
            obj.delete()
        super(IdeEstabLot5011, self).delete(*args, **kwargs)


class DemonstrativeBase(Event):
    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    info_pgto_dt_pgto = models.DateField(null=True, blank=True)
    info_pgto_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    class Meta:
        abstract = True


class Demonstrative(Event):
    """
    dmDev do eSocial.

    Cada matrícula terá um demonstrativo. Assim o detalhamento para RemunPeriod será apenas para uma matrícula.
    """

    NAME = "Demonstrativo"
    INTERNAL = True

    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    info_pgto_dt_pgto = models.DateField(null=True, blank=True)
    info_pgto_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    dm_dev_cod_categ = models.PositiveIntegerField()

    rra = models.CharField("RRA", max_length=12, null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_per_apur_ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot", related_name="demonstrative"
    )
    ide_adc = models.ManyToManyField("IdeAdc", related_name="demonstrative")
    info_compl_cont_cod_cbo = models.CharField(max_length=6, null=True, blank=True)
    info_compl_cont_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_compl_cont_qtd_dias_trab = models.PositiveIntegerField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        for obj in self.info_per_apur_ide_estab_lot.all():
            obj.delete()
        for obj in self.ide_adc.all():
            obj.delete()
        super(Demonstrative, self).delete(*args, **kwargs)

    def employee(self):
        return Employee.objects.filter(matricula=self.registry_employee).last()


class Demonstrative1202(Event):

    NAME = "Demonstrativo 1202"
    INTERNAL = True

    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    info_pgto_dt_pgto = models.DateField(null=True, blank=True)
    info_pgto_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    dm_dev_cod_categ = models.PositiveIntegerField()

    rra = models.CharField("RRA", max_length=12, null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_per_apur_ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot", related_name="demonstrative1202"
    )
    ide_period = models.ManyToManyField("IdePeriod", related_name="demonstrative1202")
    remun_org_suc = models.CharField(max_length=1, null=True, blank=True)

    tp_proc_ret = models.PositiveSmallIntegerField(
        "Preencher com o código correspondente ao tipo de processo",
        null=True,
        blank=True,
        db_index=True,
    )
    nr_proc_ret = models.CharField(
        "Preencher com o código correspondente ao tipo de processo",
        max_length=21,
        null=True,
        blank=True,
        db_index=True,
    )
    cod_susp = models.PositiveSmallIntegerField(
        "Código do indicativo da suspensão, atribuído pelo empregador em S-1070",
        null=True,
        blank=True,
        db_index=True,
    )
    vlr_rend_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_per_apur_ide_estab_lot.all():
            obj.delete()
        for obj in self.ide_period.all():
            obj.delete()
        super(Demonstrative1202, self).delete(*args, **kwargs)

    def employee(self):
        return Employee.objects.filter(matricula=self.registry_employee).last()


class Demonstrative1207(Event):

    NAME = "Demonstrativo 1207"
    INTERNAL = True

    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    info_pgto_dt_pgto = models.DateField(null=True, blank=True)
    info_pgto_vr_liq = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    dm_dev_nr_beneficio = models.CharField(max_length=20)

    rra = models.CharField("RRA", max_length=12, null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_per_apur_ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot1207", related_name="demonstrative1207"
    )
    ide_period = models.ManyToManyField(
        "IdePeriod1207", related_name="demonstrative1207"
    )

    tp_proc_ret = models.PositiveSmallIntegerField(
        "Preencher com o código correspondente ao tipo de processo",
        null=True,
        blank=True,
        db_index=True,
    )
    nr_proc_ret = models.CharField(
        "Preencher com o código correspondente ao tipo de processo",
        max_length=21,
        null=True,
        blank=True,
        db_index=True,
    )
    cod_susp = models.PositiveSmallIntegerField(
        "Código do indicativo da suspensão, atribuído pelo empregador em S-1070",
        null=True,
        blank=True,
        db_index=True,
    )
    vlr_rend_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_per_apur_ide_estab_lot.all():
            obj.delete()
        for obj in self.ide_period.all():
            obj.delete()
        super(Demonstrative1207, self).delete(*args, **kwargs)

    def employee(self):
        return Employee.objects.filter(matricula=self.registry_employee).last()


class RemunPeriod(Event):

    NAME = "Remuneração por Período"
    INTERNAL = True

    matricula = models.CharField(max_length=30, null=True, blank=True)
    ind_simples = models.PositiveIntegerField(null=True, blank=True)
    itens_remun = models.ManyToManyField(
        "DemonstrativeItem", related_name="remunperiod"
    )
    grau_exp = models.PositiveIntegerField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        for obj in self.itens_remun.all():
            obj.delete()
        super(RemunPeriod, self).delete(*args, **kwargs)


class IdeAdc(Event):

    NAME = "Ide Adc"
    INTERNAL = True

    ide_adc_dt_ac_conv = models.DateField(null=True, blank=True)
    ide_adc_tp_ac_conv = models.CharField(max_length=1, null=True, blank=True)
    ide_adc_dsc = models.CharField(max_length=255, null=True, blank=True)
    ide_adc_remun_suc = models.CharField(max_length=1, null=True, blank=True)
    ide_period = models.ManyToManyField("IdePeriod", related_name="ideadc")

    def delete(self, *args, **kwargs):
        for obj in self.ide_period.all():
            obj.delete()
        super(IdeAdc, self).delete(*args, **kwargs)


class IdePeriod(Event):

    NAME = "Ide Período"
    INTERNAL = True

    ide_adc = models.CharField("Ide Adc", max_length=12, null=True, blank=True)
    ide_periodo_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_per_ant_ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot", related_name="ideperiod"
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_per_ant_ide_estab_lot.all():
            obj.delete()
        super(IdePeriod, self).delete(*args, **kwargs)


class IdePeriod1207(Event):

    NAME = "Ide Período 1207"
    INTERNAL = True

    ide_adc = models.CharField("Ide Adc", max_length=12, null=True, blank=True)
    ide_periodo_per_ref = models.CharField(max_length=7, null=True, blank=True)
    info_per_ant_ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot1207", related_name="ideperiod1207"
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_per_ant_ide_estab_lot.all():
            obj.delete()
        super(IdePeriod1207, self).delete(*args, **kwargs)


class DemonstrativeItemManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(ide_evento_tp_amb=esocial_environment())


class DemonstrativeItemQuerySet(models.QuerySet):

    def demonstrative_item_s1200(self, per_apur=None, s1200=None):
        """Este filtro retorna todos DemonstrativeItem. Pode filtrar por per_apur e por s1200.

        Args:
            per_apur(str):
            s1200(S1200):

        Returns:
            queryset"""
        q_filter = Q(remunperiod__ideestablot__demonstrative__s1200__isnull=False) | Q(
            remunperiod__ideestablot__ideperiod__ideadc__demonstrative__s1200__isnull=False
        )
        if s1200:
            q_filter = Q(remunperiod__ideestablot__demonstrative__s1200=s1200) | Q(
                remunperiod__ideestablot__ideperiod__ideadc__demonstrative__s1200=s1200
            )
        if per_apur:
            q_filter = q_filter & Q(ide_evento_per_apur=per_apur)
        return DemonstrativeItem.objects.filter(q_filter)

    def demonstrative_item_s1202(self, per_apur=None, s1202=None):
        """Este filtro retorna todos DemonstrativeItem. Pode filtrar por per_apur e por s1202.

        Args:
            per_apur(str):
            s1202(S1202):

        Returns:
            queryset"""
        q_filter = Q(
            remunperiod__ideestablot__demonstrative1202__s1202__isnull=False
        ) | Q(
            remunperiod__ideestablot__ideperiod__demonstrative1202__s1202__isnull=False
        )
        if s1202:
            q_filter = Q(remunperiod__ideestablot__demonstrative1202__s1202=s1202) | Q(
                remunperiod__ideestablot__ideperiod__demonstrative1202__s1202=s1202
            )
        if per_apur:
            q_filter = q_filter & Q(ide_evento_per_apur=per_apur)
        return DemonstrativeItem.objects.filter(q_filter)

    def demonstrative_item_s1207(self, per_apur=None, s1207=None):
        """Este filtro retorna todos DemonstrativeItem. Pode filtrar por per_apur e por s1207.

        Args:
            per_apur(str):
            s1207(S1207):

        Returns:
            queryset"""
        q_filter = Q(ideestablot1207__demonstrative1207__s1207__isnull=False) | Q(
            ideestablot1207__ideperiod1207__demonstrative1207__s1207__isnull=False
        )
        if s1207:
            q_filter = Q(ideestablot1207__demonstrative1207__s1207=s1207) | Q(
                ideestablot1207__ideperiod1207__demonstrative1207__s1207=s1207
            )
        if per_apur:
            q_filter = q_filter & Q(ide_evento_per_apur=per_apur)
        return DemonstrativeItem.objects.filter(q_filter)

    def demonstrative_item_all(self, per_apur=None):
        """Este filtro retorna todos DemonstrativeItem. Pode filtrar por per_apur.

        Args:
            per_apur(str):

        Returns:
            queryset"""
        return self.filter(
            Q(
                pk__in=(
                    pk
                    for pk in self.demonstrative_item_s1200(
                        per_apur=per_apur
                    ).values_list("pk", flat=True)
                )
            )
            | Q(
                pk__in=(
                    pk
                    for pk in self.demonstrative_item_s1202(
                        per_apur=per_apur
                    ).values_list("pk", flat=True)
                )
            )
            | Q(
                pk__in=(
                    pk
                    for pk in self.demonstrative_item_s1207(
                        per_apur=per_apur
                    ).values_list("pk", flat=True)
                )
            )
        )

    def not_sent(self):
        """Este método gera apenas os itens dos demonstrativos que não foram enviados.

        Returns:
            DemonstrativeItem.queryset"""
        status = PROCESS_STATUS_EVENT_NOT_SENT + (5,)
        rs = []
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1200()
                    .filter(
                        Q(
                            remunperiod__ideestablot__demonstrative__s1200__process_status__in=status
                        )
                        | Q(
                            remunperiod__ideestablot__ideperiod__ideadc__demonstrative__s1200__process_status__in=status
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1202()
                    .filter(
                        Q(
                            remunperiod__ideestablot__demonstrative1202__s1202__process_status__in=status
                        )
                        | Q(
                            remunperiod__ideestablot__ideperiod__demonstrative1202__s1202__process_status__in=status
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1207()
                    .filter(
                        Q(
                            ideestablot1207__demonstrative1207__s1207__process_status__in=status
                        )
                        | Q(
                            ideestablot1207__ideperiod1207__demonstrative1207__s1207__process_status__in=status
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )

        q_filter = None
        for qf in rs:
            if not q_filter:
                q_filter = qf
            else:
                q_filter = q_filter | qf

        return self.filter(q_filter)

    def sent_error(self):
        """Este método gera apenas os itens dos demonstrativos que retornaram com erro.

        Returns:
            DemonstrativeItem.queryset"""
        rs = []
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1200()
                    .filter(
                        Q(
                            remunperiod__ideestablot__demonstrative__s1200__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                        | Q(
                            remunperiod__ideestablot__ideperiod__ideadc__demonstrative__s1200__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1202()
                    .filter(
                        Q(
                            remunperiod__ideestablot__demonstrative1202__s1202__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                        | Q(
                            remunperiod__ideestablot__ideperiod__demonstrative1202__s1202__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )
        rs.append(
            Q(
                pk__in=(
                    pk
                    for pk in DemonstrativeItem.objects.demonstrative_item_s1207()
                    .filter(
                        Q(
                            ideestablot1207__demonstrative1207__s1207__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                        | Q(
                            ideestablot1207__ideperiod1207__demonstrative1207__s1207__process_status__in=PROCESS_STATUS_EVENT_SENT_ERROR
                        )
                    )
                    .values_list("pk", flat=True)
                )
            )
        )

        q_filter = None
        for qf in rs:
            if not q_filter:
                q_filter = qf
            else:
                q_filter = q_filter | qf

        return self.filter(q_filter)


class DemonstrativeItem(Event):

    NAME = "Item do Demonstrativo"
    INTERNAL = True

    cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    qtd_rubr = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ind_apur_ir = models.IntegerField(null=True, blank=True)
    oid_rubr = models.CharField("ID objeto origem", db_index=True, max_length=32)

    desc_folha_tp_desc = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    desc_folha_nr_doc = models.CharField(max_length=12, null=True, blank=True)
    desc_folha_observacao = models.CharField(max_length=55, null=True, blank=True)

    tp_proc_ret = models.PositiveSmallIntegerField(
        "Preencher com o código correspondente ao tipo de processo",
        null=True,
        blank=True,
        db_index=True,
    )
    nr_proc_ret = models.CharField(
        "Preencher com o código correspondente ao tipo de processo",
        max_length=21,
        null=True,
        blank=True,
        db_index=True,
    )
    cod_susp = models.PositiveSmallIntegerField(
        "Código do indicativo da suspensão, atribuído pelo empregador em S-1070",
        null=True,
        blank=True,
        db_index=True,
    )
    vlr_rend_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    objects = DemonstrativeItemManager.from_queryset(DemonstrativeItemQuerySet)()

    def update_entry(self):
        """Este método atualiza o FolhaEvento.event_esocial para self quando existir algum demonstrativo com is_invalid_cache False."""
        from rh.gfp.models import FolhaEvento

        demonstrative = S1200.objects.filter(
            dm_dev__info_per_apur_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
            is_invalid_cache=False,
            process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
        )
        exists = demonstrative.exists()
        if not exists:
            demonstrative = S1200.objects.filter(
                dm_dev__ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            exists = demonstrative.exists()
        if not exists:
            demonstrative = S1202.objects.filter(
                dm_dev__info_per_apur_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            exists = demonstrative.exists()
        if not exists:
            demonstrative = S1202.objects.filter(
                dm_dev__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            exists = demonstrative.exists()
        if not exists:
            demonstrative = S1207.objects.filter(
                dm_dev__info_per_apur_ide_estab_lot__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            exists = demonstrative.exists()
        if not exists:
            demonstrative = S1207.objects.filter(
                dm_dev__ide_period__info_per_ant_ide_estab_lot__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            exists = demonstrative.exists()

        event_esocial = self.pk

        if not exists:
            event_esocial = None
        elif demonstrative.count() > 1:
            raise Exception(f"{self} em mais de um demonstrativo!")

        FolhaEvento.objects.filter(pk=int(self.oid)).exclude(
            event_esocial=event_esocial
        ).update(event_esocial=event_esocial)

    @property
    def demonstrative(self):
        """Este método retorna o S1200, S1202 ou S1207 encontrado.

        Returns:
            Event(S1200, S1202, S1207)"""

        demonstrative = S1200.objects.filter(
            dm_dev__info_per_apur_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
            is_invalid_cache=False,
            process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
        )
        demonstrative = demonstrative.last()
        if not demonstrative:
            demonstrative = S1200.objects.filter(
                dm_dev__ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            demonstrative = demonstrative.last()
        if not demonstrative:
            demonstrative = S1202.objects.filter(
                dm_dev__info_per_apur_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            demonstrative = demonstrative.last()
        if not demonstrative:
            demonstrative = S1202.objects.filter(
                dm_dev__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            demonstrative = demonstrative.last()
        if not demonstrative:
            demonstrative = S1207.objects.filter(
                dm_dev__info_per_apur_ide_estab_lot__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            demonstrative = demonstrative.last()
        if not demonstrative:
            demonstrative = S1207.objects.filter(
                dm_dev__ide_period__info_per_ant_ide_estab_lot__itens_remun__oid=self.oid,
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )
            demonstrative = demonstrative.last()
        return demonstrative


class RescissionDemonstrative(Event):

    NAME = "Demonstrativo de Rescisão"
    INTERNAL = True

    dm_dev_ide_dm_dev = models.CharField(max_length=30)
    det_verbas = models.ManyToManyField(
        "DemonstrativeItem", related_name="rescissiondemonstratives"
    )
    # info_per_ant = models.ManyToManyField('')
    # os campos a seguir sao de um grupo cuja incidencia pode ser maior que um. Contudo, em nosso interpretaçao
    # entedemos que, em nosso caso (MPTO), nao seria necessario, pois teriamos apenas uma incidencia.
    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=15, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    info_simples_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    info_ag_nocivo_grau_exp = models.PositiveIntegerField(null=True, blank=True)


class S1000(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtInfoEmpregador.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtInfoEmpregador/v_S_01_03_00"
    GROUP = 1
    NAME = "Informações do Empregador/Contribuinte"
    ACTION_PERM = ACTION
    CLOSE_PREVIOUS_EVENTS = True

    ide_periodo_ini_valid = models.CharField(max_length=7)
    ide_periodo_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    info_cadastro_nm_razao = models.CharField(max_length=100)
    info_cadastro_class_trib = models.CharField(max_length=2)
    info_cadastro_ind_coop = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_constr = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_des_folha = models.PositiveIntegerField()
    info_cadastro_ind_opc_cp = models.PositiveIntegerField(null=True, blank=True)
    info_cadastro_ind_porte = models.CharField(max_length=1, null=True, blank=True)
    info_cadastro_ind_opt_reg_eletron = models.PositiveIntegerField()
    info_cadastro_cnpj_efr = models.CharField(max_length=14, null=True, blank=True)
    dados_isencao_ide_min_lei = models.CharField(max_length=70, null=True, blank=True)
    dados_isencao_nr_certif = models.CharField(max_length=40, null=True, blank=True)
    dados_isencao_dt_emis_certif = models.DateField(null=True, blank=True)
    dados_isencao_dt_venc_certif = models.DateField(null=True, blank=True)
    dados_isencao_nr_prot_renov = models.CharField(max_length=40, null=True, blank=True)
    dados_isencao_dt_prot_renov = models.DateField(null=True, blank=True)
    dados_isencao_dt_dou = models.DateField(null=True, blank=True)
    dados_isencao_pag_dou = models.PositiveIntegerField(null=True, blank=True)
    info_org_internacional_ind_acordo_isen_multa = models.PositiveIntegerField(
        null=True, blank=True
    )
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)


class S1005(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabEstab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabEstab/v_S_01_03_00"
    GROUP = 1
    NAME = "Tabela de Estabelecimentos e Obras de Construção Civil"
    ACTION_PERM = ACTION

    ide_estab_tp_insc = models.PositiveIntegerField()
    ide_estab_nr_insc = models.CharField(max_length=14)
    ide_estab_ini_valid = models.CharField(max_length=7)
    ide_estab_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_estab_cnae_prep = models.PositiveIntegerField()
    aliq_gilrat_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    aliq_gilrat_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    proc_adm_jud_rat_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_rat_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    proc_adm_jud_rat_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_fap_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    proc_adm_jud_fap_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    proc_adm_jud_fap_cod_susp = models.PositiveIntegerField(null=True, blank=True)
    info_caepf_tp_caepf = models.PositiveIntegerField(null=True, blank=True)
    info_obra_ind_subst_patr_obra = models.PositiveIntegerField(null=True, blank=True)
    info_apr_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    info_ent_educ_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    info_pcd_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)


class S1010(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabRubrica.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabRubrica/v_S_01_03_00"
    GROUP = 1
    NAME = "Tabela de Rubricas"
    ACTION_PERM = ACTION

    ide_rubrica_cod_rubr = models.CharField(max_length=30)
    ide_rubrica_ide_tab_rubr = models.CharField(max_length=8)
    ide_rubrica_ini_valid = models.CharField(max_length=7)
    ide_rubrica_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_rubrica_dsc_rubr = models.CharField(max_length=100, null=True, blank=True)
    dados_rubrica_nat_rubr = models.PositiveIntegerField(null=True, blank=True)
    dados_rubrica_tp_rubr = models.PositiveIntegerField(null=True, blank=True)
    dados_rubrica_cod_inc_cp = models.CharField(max_length=2, null=True, blank=True)
    dados_rubrica_cod_inc_irrf = models.PositiveIntegerField(null=True, blank=True)
    dados_rubrica_cod_inc_fgts = models.CharField(max_length=2, null=True, blank=True)
    dados_rubrica_cod_inc_cprp = models.CharField(max_length=2, null=True, blank=True)
    dados_rubrica_cod_inc_pis_pasep = models.CharField(
        max_length=2, null=True, blank=True
    )
    dados_rubrica_teto_remun = models.CharField(max_length=1, null=True, blank=True)
    dados_rubrica_observacao = models.CharField(max_length=255, null=True, blank=True)
    ide_processo_cp = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_cp_S1010"
    )
    ide_processo_irrf = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_irrf_S1010"
    )
    ide_processo_fgts = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_fgts_S1010"
    )
    ide_processo_pis_pasep = models.ManyToManyField(
        "IdeProcesso", related_name="ide_processo_pis_pasep_S1010"
    )
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)

    @property
    def entry(self):
        from rh.gfp.models import Evento

        return Evento.objects.get(numero=self.ide_rubrica_cod_rubr)

    def _base_dependencies(self):
        employer = get_current_config().employer
        deps = {
            f"{('s1005',)}": [
                {
                    "oid": employer.pk,
                    "registry_employee": None,
                    "acronyms": ("s1005",),
                    "query_filter": None,
                    "filter_query_instance": None,
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }
        if self.action != EXCLUSION:
            buff_s1070 = []
            for process in self.ide_processo_cp.filter().values_list("oid", flat=True):
                buff_s1070.append(
                    {
                        "oid": process,
                        "acronyms": ("s1070",),
                        "query_filter": None,
                        "filter_query_instance": Q(number_process=process),
                        "create_if_not_exist": False,
                        "required": True,
                        "filter_validity_in": True,
                    }
                )
            for process in self.ide_processo_irrf.filter().values_list(
                "oid", flat=True
            ):
                buff_s1070.append(
                    {
                        "oid": process,
                        "acronyms": ("s1070",),
                        "query_filter": None,
                        "filter_query_instance": Q(number_process=process),
                        "create_if_not_exist": False,
                        "required": True,
                        "filter_validity_in": True,
                    }
                )
            for process in self.ide_processo_fgts.filter().values_list(
                "oid", flat=True
            ):
                buff_s1070.append(
                    {
                        "oid": process,
                        "acronyms": ("s1070",),
                        "query_filter": None,
                        "filter_query_instance": Q(number_process=process),
                        "create_if_not_exist": False,
                        "required": True,
                        "filter_validity_in": True,
                    }
                )
            deps.update({f"{('s1070',)}": buff_s1070})
        return deps


class S1020(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabLotacao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabLotacao/v_S_01_03_00"
    GROUP = 1
    NAME = "Tabela de Lotações Tributárias"
    ACTION_PERM = ACTION

    ide_lotacao_cod_lotacao = models.CharField(max_length=30)
    ide_lotacao_ini_valid = models.CharField(max_length=7)
    ide_lotacao_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_lotacao_tp_lotacao = models.CharField(max_length=2)
    dados_lotacao_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    dados_lotacao_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    fpas_lotacao_fpas = models.PositiveIntegerField()
    fpas_lotacao_cod_tercs = models.CharField(max_length=4)
    fpas_lotacao_cod_tercs_susp = models.CharField(max_length=4, null=True, blank=True)
    proc_jud_terceiro = models.ManyToManyField(
        "ProcJudTerceiro", related_name="proc_jud_terceiro_s1020"
    )
    info_empr_parcial_tp_insc_contrat = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_empr_parcial_nr_insc_contrat = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_empr_parcial_tp_insc_prop = models.PositiveIntegerField(null=True, blank=True)
    info_empr_parcial_nr_insc_prop = models.CharField(
        max_length=14, null=True, blank=True
    )
    dados_op_port_aliq_rat = models.PositiveIntegerField(null=True, blank=True)
    dados_op_port_fap = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True
    )
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)


class S1070(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTabProcesso.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTabProcesso/v_S_01_03_00"
    GROUP = 1
    NAME = "Tabela de Processos Administrativos/Judiciais"
    ACTION_PERM = ACTION

    ide_processo_tp_proc = models.PositiveIntegerField()
    ide_processo_nr_proc = models.CharField(max_length=21)
    ide_processo_ini_valid = models.CharField(max_length=7)
    ide_processo_fim_valid = models.CharField(max_length=7, null=True, blank=True)
    dados_proc_ind_autoria = models.PositiveIntegerField(null=True, blank=True)
    dados_proc_ind_mat_proc = models.PositiveIntegerField()
    dados_proc_observacao = models.CharField(max_length=255, null=True, blank=True)
    dados_proc_jud_uf_vara = models.CharField(max_length=2, null=True, blank=True)
    dados_proc_jud_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    dados_proc_jud_id_vara = models.PositiveIntegerField(null=True, blank=True)
    info_susp = models.ManyToManyField("InfoSuspensao", related_name="events")
    nova_validade_ini_valid = models.CharField(max_length=7, null=True, blank=True)
    nova_validade_fim_valid = models.CharField(max_length=7, null=True, blank=True)

    @property
    def legal_process(self):
        from rh.models import LegalProcess

        return LegalProcess.objects.get(number_process=self.ide_processo_nr_proc)

    def _base_dependencies(self):
        employer = get_current_config().employer
        deps = {
            f"{('s1005',)}": [
                {
                    "oid": employer.pk,
                    "registry_employee": None,
                    "acronyms": ("s1005",),
                    "query_filter": None,
                    "filter_query_instance": None,
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }
        return deps


class PaymentEvent(Event):
    class Meta:
        abstract = True


class S1200(PaymentEvent):
    class Meta:
        app_label = "esocial"
        verbose_name = "Remuneração do Trabalhador - RGPS"

    XML_SCHEMA_NAME = "evtRemun.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtRemun/v_S_01_03_00"
    GROUP = 3
    NAME = "Remuneração do Trabalhador - RGPS"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr = models.ManyToManyField(
        "RemunOutrEmpr", related_name="remunoutrempr_s1200"
    )
    info_complem_nm_trab = models.CharField(max_length=70, null=True, blank=True)
    info_complem_dt_nascto = models.DateField(null=True, blank=True)
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_adm = models.DateField(null=True, blank=True)
    sucessao_vinc_observacao = models.CharField(max_length=255, null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "ProcJudTrab", related_name="procjudtrab_s1200"
    )
    dm_dev = models.ManyToManyField("Demonstrative", related_name="s1200")

    def employee(self):
        return Employee.objects.filter(
            pessoa_fisica__cpf=self.ide_trabalhador_cpf_trab
        ).last()

    def employees(self):
        return Employee.objects.filter(pessoa_fisica__cpf=self.ide_trabalhador_cpf_trab)

    def employee_cpf(self):
        return self.ide_trabalhador_cpf_trab

    def delete(self, *args, **kwargs):
        for obj in self.remun_outr_empr.all():
            obj.delete()
        for obj in self.proc_jud_trab.all():
            obj.delete()
        for obj in self.dm_dev.all():
            obj.delete()
        super(S1200, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        deps = {}

        employer = get_current_config().employer
        deps.update(
            {
                f"{('s1005',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1005",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )
        deps.update(
            {
                f"{('s1020',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1020",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )

        buff = []
        for item in (
            self.dm_dev.filter()
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__cod_rubr",
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__oid_rubr",
            )
            .order_by(
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__cod_rubr"
            )
            .distinct()
        ):
            buff.append(
                {
                    "oid": item[1],
                    "acronyms": ("s1010",),
                    "query_filter": None,
                    "filter_query_instance": Q(numero=item[0]),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            )
        for item in (
            self.dm_dev.filter()
            .values_list(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__cod_rubr",
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid_rubr",
            )
            .order_by(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__cod_rubr"
            )
            .distinct()
        ):
            if item[1]:
                buff.append(
                    {
                        "oid": item[1],
                        "acronyms": ("s1010",),
                        "query_filter": None,
                        "filter_query_instance": Q(numero=item[0]),
                        "create_if_not_exist": False,
                        "required": True,
                        "filter_validity_in": True,
                    }
                )
        deps.update({f"{('s1010',)}": buff})

        buff = []
        for registry in (
            self.dm_dev.filter()
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__matricula", flat=True
            )
            .order_by("info_per_apur_ide_estab_lot__remun_period__matricula")
            .distinct()
        ):
            if registry:
                buff.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        for registry in (
            self.dm_dev.filter()
            .values_list(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__matricula",
                flat=True,
            )
            .order_by(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__matricula"
            )
            .distinct()
        ):
            if registry:
                buff.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        deps.update({f"{('s2200', 's2298', 's2300')}": buff})

        if self.action == RECTIFICATION:
            buff_exclusion = []
            query = S3000.objects.filter(
                registry_person=self.registry_person
            ).valids_not_sent()
            for event in query:
                buff_exclusion.append(
                    {
                        "events": [event],
                        "registry_person": self.registry_person,
                        "acronyms": ("s3000",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                )
            deps.update({f"{('s3000', )}": buff_exclusion})

        return deps

    def _find_event_dependency_query(self, acronyms):
        """Este método deve representar a query utilizada em _find_event_dependency para encontrar a dependência."""
        return (
            Event.objects.filter(
                Q(acronym__in=acronyms)
                & (
                    Q(start_validity__lte=self.end_validity)
                    | (
                        Q(group=1)
                        & Q(
                            start_validity=get_current_config().initial_date_start_tables
                        )
                    )
                )
            )
            .exclude(pk=self.pk)
            .valids_by_status()
            .order_by("start_validity")
        )

    @property
    def demonstrative_items(self):
        return DemonstrativeItem.objects.filter(
            Q(remunperiod__ideestablot__demonstrative__s1200=self)
            | Q(remunperiod__ideestablot__ideperiod__ideadc__demonstrative__s1200=self)
        )

    @classmethod
    def update_demonstrative_item(cls, month, year, task=None):
        """Este método chama atualização do FolhaEvento a partir do demonstrativo S1200, S1202, S1207.

        Args:
            period (rh.gfp.models.Periodo): período da folha. Deve ser um valor válido.
            task (_type_, optional): _description_. Defaults to None.
        """
        from esocial.extractors.s1200 import ExtractorPayroll
        from rh.gfp.models import FolhaEvento

        per_apur = ExtractorPayroll._ide_evento_per_apur(month, year)

        def waiting_task_done(tasks_todo):
            total = len(tasks_todo)
            inc_progress = 100.0 / total if total else 0
            if task:
                Task.objects.filter(uuid=task.uuid).update(progress=0)
                task.refresh_from_db()

            timeout = 300
            start = datetime.now()
            tasks_todo_copy = copy.deepcopy(tasks_todo)
            while len(tasks_todo):
                time.sleep(3)
                for key in tasks_todo_copy:
                    t_todo = tasks_todo_copy.get(key)
                    if t_todo.ready():
                        tasks_todo.pop(key)
                        if task:
                            task.info(
                                msg_pct="Atualizando Pagamentos",
                                pct_progress=inc_progress,
                            )
                tasks_todo_copy = copy.deepcopy(tasks_todo)

                # end = datetime.now()
                # result = end - start
                # if result.seconds > timeout:
                #     break

        tasks_todo = {}

        def _update(query):
            total = query.count()
            inc_progress = 100.0 / total if total else 0

            if task:
                Task.objects.filter(uuid=task.uuid).update(progress=0)
                task.refresh_from_db()

            msg_pct = f"Atualizando Itens de Pagamento de {query.model.__name__}"
            for event in query:
                async_result = S1200.update_demonstrative_items(event, task=task)
                if async_result:
                    tasks_todo.update({f"{async_result}": async_result})
                if task:
                    task.info(msg_pct=msg_pct, pct_progress=inc_progress)

        FolhaEvento.objects.filter(
            folha__periodo__mes=month, folha__periodo__ano=year
        ).update(event_esocial=None)

        _update(S1200.objects.by_per_apur(per_apur=per_apur).valids_sent())
        _update(S1202.objects.by_per_apur(per_apur=per_apur).valids_sent())
        _update(S1207.objects.by_per_apur(per_apur=per_apur).valids_sent())

        waiting_task_done(tasks_todo)

    @staticmethod
    def update_demonstrative_items(demonstrative, task=None):
        """Este método é responsável por chamar a atualização de todos DemonstrativeItem que existem no evento de remuneração.
        Utiliza uma task para atualizar individualmente.

        Args:
            demonstrative(S1200, S1202, S1207):
            task:

        Returns:
            job.apply_async or []"""
        from esocial.tasks.generation import update_demonstrative_item

        if demonstrative.process_status > 5:
            user = get_current_user()
            job = group(
                [
                    update_demonstrative_item.s(
                        user.pk, item.pk, task.uuid if task else None
                    )
                    for item in demonstrative.demonstrative_items
                ]
            )
            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # return job.apply_async()
            return job.apply_async(queue="esocial-events")
        return None


class S1202(PaymentEvent):
    class Meta:
        app_label = "esocial"
        verbose_name = "Remuneração do Trabalhador - RPPS"

    XML_SCHEMA_NAME = "evtRmnRPPS.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtRmnRPPS/v_S_01_03_00"
    GROUP = 3
    NAME = "Remuneração do Trabalhador - RPPS"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    info_complem_nm_trab = models.CharField(max_length=70, null=True, blank=True)
    info_complem_dt_nascto = models.DateField(null=True, blank=True)
    sucessao_vinc_cnpj_orgao_ant = models.CharField(
        max_length=14, null=True, blank=True
    )
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_exercicio = models.DateField(null=True, blank=True)
    sucessao_vinc_observacao = models.CharField(max_length=255, null=True, blank=True)
    dm_dev = models.ManyToManyField("Demonstrative1202", related_name="s1202")

    def employee(self):
        return Employee.objects.filter(
            pessoa_fisica__cpf=self.ide_trabalhador_cpf_trab
        ).last()

    def employee_cpf(self):
        return self.ide_trabalhador_cpf_trab

    def delete(self, *args, **kwargs):
        for obj in self.dm_dev.all():
            obj.delete()
        super(S1202, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        deps = {}

        employer = get_current_config().employer
        deps.update(
            {
                f"{('s1005',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1005",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )
        deps.update(
            {
                f"{('s1020',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1020",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )

        buff = []
        for item in (
            self.dm_dev.filter()
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__cod_rubr",
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__oid_rubr",
            )
            .order_by(
                "info_per_apur_ide_estab_lot__remun_period__itens_remun__cod_rubr"
            )
            .distinct()
        ):
            buff.append(
                {
                    "oid": item[1],
                    "acronyms": ("s1010",),
                    "query_filter": None,
                    "filter_query_instance": Q(numero=item[0]),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            )
        for item in (
            self.dm_dev.filter()
            .values_list(
                "ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__cod_rubr",
                "ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__oid_rubr",
            )
            .order_by(
                "ide_period__info_per_ant_ide_estab_lot__remun_period__itens_remun__cod_rubr"
            )
            .distinct()
        ):
            buff.append(
                {
                    "oid": item[1],
                    "acronyms": ("s1010",),
                    "query_filter": None,
                    "filter_query_instance": Q(numero=item[0]),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            )
        deps.update({f"{('s1010',)}": buff})

        buff = []
        for registry in (
            self.dm_dev.filter()
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__matricula", flat=True
            )
            .order_by("info_per_apur_ide_estab_lot__remun_period__matricula")
            .distinct()
        ):
            if registry:
                buff.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        for registry in (
            self.dm_dev.filter()
            .values_list(
                "ide_period__info_per_ant_ide_estab_lot__remun_period__matricula",
                flat=True,
            )
            .order_by("ide_period__info_per_ant_ide_estab_lot__remun_period__matricula")
            .distinct()
        ):
            if registry:
                buff.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        deps.update({f"{('s2200', 's2298', 's2300')}": buff})

        if self.action == RECTIFICATION:
            buff_exclusion = []
            query = S3000.objects.filter(
                registry_person=self.registry_person
            ).valids_not_sent()
            for event in query:
                buff_exclusion.append(
                    {
                        "events": [event],
                        "registry_person": self.registry_person,
                        "acronyms": ("s3000",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                )
            deps.update({f"{('s3000', )}": buff_exclusion})

        return deps

    def _find_event_dependency_query(self, acronyms):
        """Este método deve representar a query utilizada em _find_event_dependency para encontrar a dependência."""
        return (
            Event.objects.filter(
                Q(acronym__in=acronyms)
                & (
                    Q(start_validity__lte=self.end_validity)
                    | (
                        Q(group=1)
                        & Q(
                            start_validity=get_current_config().initial_date_start_tables
                        )
                    )
                )
            )
            .exclude(pk=self.pk)
            .valids_by_status()
            .order_by("start_validity")
        )

    @property
    def demonstrative_items(self):
        return DemonstrativeItem.objects.filter(
            Q(remunperiod__ideestablot__demonstrative1202__s1202=self)
            | Q(remunperiod__ideestablot__ideperiod__demonstrative1202__s1202=self)
        )


class S1207(PaymentEvent):
    class Meta:
        app_label = "esocial"
        verbose_name = "Benefícios - Entes Públicos"

    XML_SCHEMA_NAME = "evtBenPrRP.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtBenPrRP/v_S_01_03_00"
    GROUP = 3
    NAME = "Benefícios - Entes Públicos"
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000
    ACTION_PERM = ACTION_RECTIFICATION

    ide_benef_cpf_benef = models.CharField(max_length=11)
    dm_dev = models.ManyToManyField("Demonstrative1207", related_name="s1207")

    def employee(self):
        return Employee.objects.filter(
            pessoa_fisica__cpf=self.ide_benef_cpf_benef
        ).last()

    def employee_cpf(self):
        return self.ide_benef_cpf_benef

    def delete(self, *args, **kwargs):
        for obj in self.dm_dev.all():
            obj.delete()
        super(S1207, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        deps = {}

        buff = []
        for item in (
            self.dm_dev.filter()
            .values_list(
                "info_per_apur_ide_estab_lot__itens_remun__cod_rubr",
                "info_per_apur_ide_estab_lot__itens_remun__oid_rubr",
            )
            .order_by("info_per_apur_ide_estab_lot__itens_remun__cod_rubr")
            .distinct()
        ):
            buff.append(
                {
                    "oid": item[1],
                    "acronyms": ("s1010",),
                    "query_filter": None,
                    "filter_query_instance": Q(numero=item[1]),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            )
        for item in (
            self.dm_dev.filter()
            .values_list(
                "ide_period__info_per_ant_ide_estab_lot__itens_remun__cod_rubr",
                "ide_period__info_per_ant_ide_estab_lot__itens_remun__oid_rubr",
            )
            .order_by("ide_period__info_per_ant_ide_estab_lot__itens_remun__cod_rubr")
            .distinct()
        ):
            buff.append(
                {
                    "oid": item[1],
                    "acronyms": ("s1010",),
                    "query_filter": None,
                    "filter_query_instance": Q(numero=item[1]),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            )
        deps.update({f"{('s1010',)}": buff})

        buff = []
        deps.update(
            {
                f"{('s2400',)}": [
                    {
                        "registry_person": self.ide_benef_cpf_benef,
                        "acronyms": ("s2400",),
                        "query_filter": None,
                        "filter_query_instance": Q(
                            pessoa_fisica__cpf=self.ide_benef_cpf_benef
                        ),
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )

        buff = []
        for number in (
            self.dm_dev.filter()
            .values_list("dm_dev_nr_beneficio", flat=True)
            .order_by("dm_dev_nr_beneficio")
        ):
            buff.append(
                {
                    "registry_person": self.ide_benef_cpf_benef,
                    "acronyms": ("s2410",),
                    "query_filter": Q(oid__icontains=number),
                    "filter_query_instance": Q(benefit_number=number),
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": False,
                    "events": S2410.objects.filter(info_ben_inicio_nr_beneficio=number),
                }
            )
        deps.update({f"{('s2410',)}": buff})

        if self.action == RECTIFICATION:
            buff_exclusion = []
            query = S3000.objects.filter(
                registry_person=self.registry_person
            ).valids_not_sent()
            for event in query:
                buff_exclusion.append(
                    {
                        "events": [event],
                        "registry_person": self.registry_person,
                        "acronyms": ("s3000",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                )
            deps.update({f"{('s3000', )}": buff_exclusion})

        return deps

    @property
    def demonstrative_items(self):
        return DemonstrativeItem.objects.filter(
            Q(ideestablot1207__demonstrative1207__s1207=self)
            | Q(ideestablot1207__ideperiod1207__demonstrative1207__s1207=self)
        )

    def _find_event_dependency_query(self, acronyms):
        """Este método deve representar a query utilizada em _find_event_dependency para encontrar a dependência."""
        return (
            Event.objects.filter(
                Q(acronym__in=acronyms)
                & (
                    Q(start_validity__lte=self.end_validity)
                    | (
                        Q(group=1)
                        & Q(
                            start_validity=get_current_config().initial_date_start_tables
                        )
                    )
                )
            )
            .exclude(pk=self.pk)
            .valids_by_status()
            .order_by("start_validity")
        )


class S1210(PaymentEvent):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtPgtos.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtPgtos/v_S_01_03_00"
    GROUP = 3
    NAME = "Pagamentos de Rendimentos do Trabalho"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_benef_cpf_benef = models.CharField(max_length=11)
    info_pgto_pais_resid_ext = models.CharField(max_length=3, null=True, blank=True)
    info_pgto = models.ManyToManyField("InfoPgto", related_name="info_pgto_S1210")
    info_ir_complemen = models.ManyToManyField(
        "InfoIrComplemen", related_name="info_ir_complemen_s1210"
    )

    def employee(self):
        return Employee.objects.filter(
            pessoa_fisica__cpf=self.ide_benef_cpf_benef
        ).last()

    def employee_cpf(self):
        return self.ide_benef_cpf_benef

    def delete(self, *args, **kwargs):
        for obj in self.info_pgto.all():
            obj.delete()
        super(S1210, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        deps = {}

        employer = get_current_config().employer
        deps.update(
            {
                f"{('s1005',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1005",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )
        deps.update(
            {
                f"{('s1020',)}": [
                    {
                        "oid": employer.pk,
                        "registry_employee": None,
                        "acronyms": ("s1020",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                ]
            }
        )

        """s2200, s2298 e s2300"""
        buff_registration = []
        query_s1200_registry_per_apur = (
            Demonstrative.objects.filter(
                dm_dev_ide_dm_dev__in=(
                    dmdev
                    for dmdev in self.info_pgto.filter().values_list(
                        "info_pgto_ide_dm_dev", flat=True
                    )
                )
            )
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__matricula", flat=True
            )
            .order_by("info_per_apur_ide_estab_lot__remun_period__matricula")
        )
        for registry in query_s1200_registry_per_apur.distinct():
            if registry:
                buff_registration.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        query_s1200_registry_per_ant = (
            Demonstrative.objects.filter(
                dm_dev_ide_dm_dev__in=(
                    dmdev
                    for dmdev in self.info_pgto.filter().values_list(
                        "info_pgto_ide_dm_dev", flat=True
                    )
                )
            )
            .values_list(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__matricula",
                flat=True,
            )
            .order_by(
                "ide_adc__ide_period__info_per_ant_ide_estab_lot__remun_period__matricula"
            )
        )
        for registry in query_s1200_registry_per_ant.distinct():
            if registry:
                buff_registration.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )

        query_s1202_registry_per_apur = (
            Demonstrative1202.objects.filter(
                dm_dev_ide_dm_dev__in=(
                    dmdev
                    for dmdev in self.info_pgto.filter().values_list(
                        "info_pgto_ide_dm_dev", flat=True
                    )
                )
            )
            .values_list(
                "info_per_apur_ide_estab_lot__remun_period__matricula", flat=True
            )
            .order_by("info_per_apur_ide_estab_lot__remun_period__matricula")
        )
        for registry in query_s1202_registry_per_apur.distinct():
            if registry:
                buff_registration.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        query_s1202_registry_per_ant = (
            Demonstrative1202.objects.filter(
                dm_dev_ide_dm_dev__in=(
                    dmdev
                    for dmdev in self.info_pgto.filter().values_list(
                        "info_pgto_ide_dm_dev", flat=True
                    )
                )
            )
            .values_list(
                "ide_period__info_per_ant_ide_estab_lot__remun_period__matricula",
                flat=True,
            )
            .order_by("ide_period__info_per_ant_ide_estab_lot__remun_period__matricula")
        )
        for registry in query_s1202_registry_per_ant.distinct():
            if registry:
                buff_registration.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2200", "s2298", "s2300"),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        deps.update({f"{('s2200', 's2298', 's2300')}": buff_registration})

        buff_registration = []
        query_s1207 = (
            Demonstrative1207.objects.filter(
                dm_dev_ide_dm_dev__in=(
                    dmdev
                    for dmdev in self.info_pgto.filter().values_list(
                        "info_pgto_ide_dm_dev", flat=True
                    )
                )
            )
            .values_list("registry_employee", flat=True)
            .order_by("registry_employee")
        )
        for registry in query_s1207.distinct():
            if registry:
                """s2400"""
                buff_registration.append(
                    {
                        "registry_employee": registry,
                        "acronyms": ("s2400",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": True,
                        "required": True,
                        "filter_validity_in": False,
                    }
                )
        deps.update({f"{('s2400',)}": buff_registration})

        buff_demonstrative = []
        for info_pgto in self.info_pgto.filter():
            info_pgto_per_ref = info_pgto.info_pgto_per_ref.replace("-", "")
            if len(info_pgto_per_ref) == 4:
                info_pgto_per_ref = f"{info_pgto_per_ref}12"
            buff_demonstrative.append(
                {
                    "oid": f"{info_pgto_per_ref}{self.registry_person}",
                    "registry_person": self.registry_person,
                    "acronyms": ("s1200",),
                    "query_filter": Q(
                        acronym=MAP_TPPGTO_TO_DEMONSTRATIVE.get(
                            info_pgto.info_pgto_tp_pgto
                        )
                    ),
                    "filter_query_instance": Q(cpf=self.registry_person),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            )
            buff_demonstrative.append(
                {
                    "oid": f"{info_pgto_per_ref}{self.registry_person}",
                    "registry_person": self.registry_person,
                    "acronyms": ("s1202",),
                    "query_filter": Q(
                        acronym=MAP_TPPGTO_TO_DEMONSTRATIVE.get(
                            info_pgto.info_pgto_tp_pgto
                        )
                    ),
                    "filter_query_instance": Q(cpf=self.registry_person),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            )
            buff_demonstrative.append(
                {
                    "oid": f"{info_pgto_per_ref}{self.registry_person}",
                    "registry_person": self.registry_person,
                    "acronyms": ("s1207",),
                    "query_filter": Q(
                        acronym=MAP_TPPGTO_TO_DEMONSTRATIVE.get(
                            info_pgto.info_pgto_tp_pgto
                        )
                    ),
                    "filter_query_instance": Q(cpf=self.registry_person),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            )
        deps.update({f"{('s1200', 's1202', 's1207')}": buff_demonstrative})

        return deps

    def _find_event_dependency_query(self, acronyms):
        """Este método deve representar a query utilizada em _find_event_dependency para encontrar a dependência."""
        return (
            Event.objects.filter(
                Q(acronym__in=acronyms)
                & (
                    Q(start_validity__lte=self.end_validity)
                    | (
                        Q(group=1)
                        & Q(
                            start_validity=get_current_config().initial_date_start_tables
                        )
                    )
                )
            )
            .exclude(pk=self.pk)
            .valids_by_status()
            .order_by("start_validity")
        )


class S1298(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReabreEvPer.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReabreEvPer/v_S_01_03_00"
    GROUP = 3
    NAME = "Reabertura dos Eventos Periódicos"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000
    CLOSE_PREVIOUS_EVENTS = True

    def _previous_event(self):
        """O evento anterior será um s1299 válido."""
        return (
            S1299.objects.valids_sent()
            .filter(
                closed_by_event__isnull=True,
                ide_evento_per_apur=self.ide_evento_per_apur,
            )
            .order_by("start_validity")
            .last()
        )

    def _check_previous_event(self, previous_event):
        """Este método realiza checagem para atualizar o previous_event encontrado."""
        return self.process_status == 1 and previous_event


class S1299(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtFechaEvPer.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtFechaEvPer/v_S_01_03_00"
    GROUP = 3
    NAME = "Fechamento dos Eventos Periódicos"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000
    CLOSE_PREVIOUS_EVENTS = True

    info_fech_evt_remun = models.CharField(max_length=1)
    info_fech_evt_pgtos = models.CharField(max_length=1)
    info_fech_evt_com_prod = models.CharField(max_length=1)
    info_fech_evt_contrat_av_np = models.CharField(max_length=1)
    info_fech_evt_info_compl_per = models.CharField(max_length=1)
    info_fech_ind_exc_apur1250 = models.CharField(max_length=1, null=True, blank=True)
    info_fech_trans_dctf_web = models.CharField(max_length=1, null=True, blank=True)
    info_fech_nao_valid = models.CharField(max_length=1, null=True, blank=True)

    def _previous_event(self):
        """O evento anterior será um s1298 válido."""
        return (
            S1298.objects.valids_sent()
            .filter(
                closed_by_event__isnull=True,
                ide_evento_per_apur=self.ide_evento_per_apur,
            )
            .order_by("start_validity")
            .last()
        )

    def _check_previous_event(self, previous_event):
        """Este método realiza checagem para atualizar o previous_event encontrado."""
        return self.process_status == 1 and previous_event

    def can_close(self):
        """Este método verifica se é possível gerar o evento de fechamento.
        Avalia se todos S1200, S1202, S1207, S1210, e se todos FolhaEvento do Athenas foram adicionados aos demonstrativos.
        """
        from rh.gfp.models import Periodo

        return self.check_can_close(
            self.ide_evento_per_apur,
            period=Periodo.objects.get(
                mes=self.competence_month, ano=self.competence_year
            ),
        )

    @classmethod
    def check_can_close(cls, per_apur, period=None):
        """Este método verifica se é possível gerar o evento de fechamento.
        Avalia se todos S1200, S1202, S1207, S1210, e se todos FolhaEvento do Athenas foram adicionados aos demonstrativos.
        """
        cls.check_can_close_s1200(per_apur)
        cls.check_can_close_s1202(per_apur)
        cls.check_can_close_s1207(per_apur)
        cls.check_can_close_s1210(per_apur)
        cls.check_can_close_entry(period=period)
        # self.check_can_close_dm_item_s1200()
        # self.check_can_close_dm_item_s1202()
        # self.check_can_close_dm_item_s1207()
        return True

    @classmethod
    def check_can_close_s1200(cls, per_apur):
        count = S1200.objects.with_problems(per_apur).count()
        if count:
            raise Exception(f"Existem eventos S1200 {count} com problemas!")
        return True

    @classmethod
    def check_can_close_s1202(cls, per_apur):
        count = S1202.objects.with_problems(per_apur).count()
        if count:
            raise Exception(f"Existem eventos S1202 {count} com problemas!")
        return True

    @classmethod
    def check_can_close_s1207(cls, per_apur):
        count = S1207.objects.with_problems(per_apur).count()
        if count:
            raise Exception(f"Existem eventos S1207 {count} com problemas!")
        return True

    @classmethod
    def check_can_close_s1210(cls, per_apur):
        count = S1210.objects.with_problems(per_apur).count()
        if count:
            raise Exception(f"Existem eventos S1210 {count} com problemas!")
        return True

    @classmethod
    def check_can_close_entry(cls, per_apur=None, period=None):
        from esocial.extractors.s1200 import ExtractorPayroll

        count = ExtractorPayroll.entries_not_in_demonstrative_item(
            period.mes, period.ano
        ).count()
        if count:
            raise Exception(
                f"Existem FolhaEvento {count} que não foram adicionados ao eSocial(S1200, S1202, S1207)!"
            )
        return True


class S2200(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAdmissao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAdmissao/v_S_01_03_00"
    GROUP = 2
    NAME = "Admissão de Trabalhador"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    trabalhador_cpf_trab = models.CharField(max_length=11)
    trabalhador_nm_trab = models.CharField(max_length=70)
    trabalhador_sexo = models.CharField(max_length=1, null=True, blank=True)
    trabalhador_raca_cor = models.PositiveIntegerField(null=True, blank=True)
    trabalhador_est_civ = models.PositiveIntegerField(null=True, blank=True)
    trabalhador_grau_instr = models.CharField(max_length=2, null=True, blank=True)
    trabalhador_nm_soc = models.CharField(max_length=70, null=True, blank=True)
    nascimento_dt_nascto = models.DateField(null=True, blank=True)
    nascimento_pais_nascto = models.CharField(max_length=3, null=True, blank=True)
    nascimento_pais_nac = models.CharField(max_length=3, null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    trab_imig_tmp_resid = models.PositiveIntegerField(null=True, blank=True)
    trab_imig_cond_ing = models.PositiveIntegerField(null=True, blank=True)
    info_deficiencia_def_fisica = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_visual = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_auditiva = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_def_mental = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_intelectual = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_reab_readap = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_info_cota = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_observacao = models.CharField(
        max_length=255, null=True, blank=True
    )
    dependente = models.ManyToManyField("Dependent", related_name="dependente_s2200")
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)
    vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    vinculo_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
    vinculo_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    vinculo_cad_ini = models.CharField(max_length=1)
    info_celetista_dt_adm = models.DateField(null=True, blank=True)
    info_celetista_tp_admissao = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_ind_admissao = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nr_proc_trab = models.CharField(max_length=20, null=True, blank=True)
    info_celetista_tp_reg_jor = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_dt_base = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_cnpj_sind_categ_prof = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_celetista_mat_anot_jud = models.CharField(max_length=30, null=True, blank=True)
    fgts_dt_opc_fgts = models.DateField(null=True, blank=True)
    trab_temporario_hip_leg = models.PositiveIntegerField(null=True, blank=True)
    trab_temporario_just_contr = models.CharField(max_length=999, null=True, blank=True)
    ide_estab_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_trab_substituido_cpf_trab_subst = models.CharField(
        max_length=11, null=True, blank=True
    )
    aprend_ind_aprend = models.PositiveIntegerField(null=True, blank=True)
    aprend_cnpj_ent_qual = models.CharField(max_length=14, null=True, blank=True)
    aprend_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    aprend_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    aprend_cnpj_prat = models.CharField(max_length=14, null=True, blank=True)
    info_estatutario_tp_prov = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_dt_exercicio = models.DateField(null=True, blank=True)
    info_estatutario_tp_plan_rp = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_ind_teto_rgps = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_ind_abono_perm = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_dt_ini_abono = models.DateField(null=True, blank=True)
    info_contrato_nm_cargo = models.CharField(max_length=100, null=True, blank=True)
    info_contrato_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_dt_ingr_cargo = models.DateField(null=True, blank=True)
    info_contrato_nm_funcao = models.CharField(max_length=100, null=True, blank=True)
    info_contrato_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_acum_cargo = models.CharField(max_length=1, null=True, blank=True)
    info_contrato_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=999, null=True, blank=True)
    duracao_tp_contr = models.PositiveIntegerField(null=True, blank=True)
    duracao_dt_term = models.DateField(null=True, blank=True)
    duracao_clau_assec = models.CharField(max_length=1, null=True, blank=True)
    duracao_obj_det = models.CharField(max_length=255, null=True, blank=True)
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
    hor_contratual_qtd_hrs_sem = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    hor_contratual_tp_jornada = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_tmp_parc = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_hor_noturno = models.CharField(max_length=1, null=True, blank=True)
    hor_contratual_dsc_jorn = models.CharField(max_length=999, null=True, blank=True)
    alvara_judicial_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=255, null=True, blank=True)
    trei_cap_cod_trei_cap = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_transf = models.DateField(null=True, blank=True)
    sucessao_vinc_observacao = models.CharField(max_length=255, null=True, blank=True)
    transf_dom_cpf_substituido = models.CharField(max_length=11, null=True, blank=True)
    transf_dom_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    transf_dom_dt_transf = models.DateField(null=True, blank=True)
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=255, null=True, blank=True)
    afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    afastamento_cod_mot_afast = models.CharField(max_length=2, null=True, blank=True)
    desligamento_dt_deslig = models.DateField(null=True, blank=True)
    cessao_dt_ini_cessao = models.DateField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.trabalhador_cpf_trab

    def _search_cache(self):
        return "{}".format(self.trabalhador_nm_trab)

    def delete(self, *args, **kwargs):
        for dependent in self.dependente.all():
            dependent.delete()
        super(S2200, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        employer = get_current_config().employer
        return {
            f"{('s1005',)}": [
                {
                    "oid": employer.pk,
                    "registry_employee": None,
                    "acronyms": ("s1005",),
                    "query_filter": None,
                    "filter_query_instance": None,
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": False,
                }
            ]
        }

    @staticmethod
    def update_employee(event):
        """Este método é responsável por atualizar o Servidor.event_esocial com o evento válido.

        Args:
            registration(S2200, S2300, S2400, S2298):"""
        from rh.models import Servidor

        if event.process_status > 5:
            event_esocial = Event.objects.filter(
                oid=str(event.registry_employee),
                acronym__in=("s2200", "s2300", "s2400", "s2298"),
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            ).last()
            if event_esocial:
                Servidor.objects.filter(matricula=event.registry_employee).update(
                    event_esocial=event_esocial.pk
                )


class S2205(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAltCadastral.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAltCadastral/v_S_01_03_00"
    GROUP = 2
    NAME = "Alteração de Dados Cadastrais do Trabalhador"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    alteracao_dt_alteracao = models.DateField()
    dados_trabalhador_nm_trab = models.CharField(max_length=70)
    dados_trabalhador_sexo = models.CharField(max_length=1, null=True, blank=True)
    dados_trabalhador_raca_cor = models.PositiveIntegerField(null=True, blank=True)
    dados_trabalhador_est_civ = models.PositiveIntegerField(null=True, blank=True)
    dados_trabalhador_grau_instr = models.CharField(max_length=2, null=True, blank=True)
    dados_trabalhador_nm_soc = models.CharField(max_length=70, null=True, blank=True)
    dados_trabalhador_pais_nac = models.CharField(max_length=3, null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    trab_imig_tmp_resid = models.PositiveIntegerField(null=True, blank=True)
    trab_imig_cond_ing = models.PositiveIntegerField(null=True, blank=True)
    info_deficiencia_def_fisica = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_visual = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_auditiva = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_def_mental = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_intelectual = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_reab_readap = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_info_cota = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_observacao = models.CharField(
        max_length=255, null=True, blank=True
    )
    dependente = models.ManyToManyField("Dependent", related_name="dependente_s2205")
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)

    @property
    def json_model_by_action(self):
        return json_model_by_action(
            self.json_model, self.action, not_exclude=["alteracao"]
        )

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _search_cache(self):
        return self.dados_trabalhador_nm_trab

    def employee_cpf(self):
        return self.ide_trabalhador_cpf_trab

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2300', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2300", "s2298"),
                    "query_filter": (
                        Q(
                            start_validity=self.extractor()
                            .current_range_possession(
                                self.registry_employee, self.start_validity
                            )
                            .first
                        )
                        | Q(start_validity=self.employee().exercise_date)
                        | Q(acronym="s2300")
                    ),
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2205', 's2206')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2206"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2206(Register):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAltContratual.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAltContratual/v_S_01_03_00"
    GROUP = 2
    NAME = "Alteração de Contrato de Trabalho"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    alt_contratual_dt_alteracao = models.DateField()
    alt_contratual_dt_ef = models.DateField(null=True, blank=True)
    alt_contratual_dsc_alt = models.CharField(max_length=150, null=True, blank=True)
    vinculo_tp_reg_prev = models.PositiveIntegerField()
    info_celetista_tp_reg_jor = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_dt_base = models.PositiveIntegerField(null=True, blank=True)
    info_celetista_cnpj_sind_categ_prof = models.CharField(
        max_length=14, null=True, blank=True
    )
    trab_temporario_just_prorr = models.CharField(max_length=999, null=True, blank=True)
    aprend_ind_aprend = models.PositiveIntegerField(null=True, blank=True)
    aprend_cnpj_ent_qual = models.CharField(max_length=14, null=True, blank=True)
    aprend_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    aprend_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    aprend_cnpj_prat = models.CharField(max_length=14, null=True, blank=True)
    info_estatutario_tp_plan_rp = models.PositiveIntegerField(null=True, blank=True)
    info_estatutario_ind_teto_rgps = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_estatutario_ind_abono_perm = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_contrato_nm_cargo = models.CharField(max_length=100, null=True, blank=True)
    info_contrato_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_nm_funcao = models.CharField(max_length=100, null=True, blank=True)
    info_contrato_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    info_contrato_acum_cargo = models.CharField(max_length=1, null=True, blank=True)
    info_contrato_cod_categ = models.PositiveIntegerField()
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=999, null=True, blank=True)
    duracao_tp_contr = models.PositiveIntegerField(null=True, blank=True)
    duracao_dt_term = models.DateField(null=True, blank=True)
    duracao_obj_det = models.CharField(max_length=255, null=True, blank=True)
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
    local_temp_dom_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    local_temp_dom_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    local_temp_dom_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    local_temp_dom_complemento = models.CharField(max_length=30, null=True, blank=True)
    local_temp_dom_bairro = models.CharField(max_length=90, null=True, blank=True)
    local_temp_dom_cep = models.CharField(max_length=8, null=True, blank=True)
    local_temp_dom_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    local_temp_dom_uf = models.CharField(max_length=2, null=True, blank=True)
    hor_contratual_qtd_hrs_sem = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    hor_contratual_tp_jornada = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_tmp_parc = models.PositiveIntegerField(null=True, blank=True)
    hor_contratual_hor_noturno = models.CharField(max_length=1, null=True, blank=True)
    hor_contratual_dsc_jorn = models.CharField(max_length=999, null=True, blank=True)
    alvara_judicial_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=255, null=True, blank=True)
    trei_cap_cod_trei_cap = models.PositiveIntegerField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2298"),
                    "query_filter": Q(
                        start_validity=self.extractor()
                        .current_range_possession(
                            self.registry_employee, self.start_validity
                        )
                        .first
                    ),
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2205', 's2206')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2206"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2230(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtAfastTemp.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtAfastTemp/v_S_01_03_00"
    GROUP = 2
    NAME = "Afastamento Temporário"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    ini_afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    ini_afastamento_cod_mot_afast = models.CharField(
        max_length=2, null=True, blank=True
    )
    ini_afastamento_info_mesmo_mtv = models.CharField(
        max_length=1, null=True, blank=True
    )
    ini_afastamento_tp_acid_transito = models.PositiveIntegerField(
        null=True, blank=True
    )
    ini_afastamento_observacao = models.CharField(max_length=255, null=True, blank=True)
    per_aquis_dt_inicio = models.DateField(null=True, blank=True)
    per_aquis_dt_fim = models.DateField(null=True, blank=True)
    info_cessao_cnpj_cess = models.CharField(max_length=14, null=True, blank=True)
    info_cessao_inf_onus = models.PositiveIntegerField(null=True, blank=True)
    info_mand_sind_cnpj_sind = models.CharField(max_length=14, null=True, blank=True)
    info_mand_sind_inf_onus_remun = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_cnpj_mand_elet = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_retif_orig_retif = models.PositiveIntegerField(null=True, blank=True)
    info_retif_tp_proc = models.PositiveIntegerField(null=True, blank=True)
    info_retif_nr_proc = models.CharField(max_length=21, null=True, blank=True)
    fim_afastamento_dt_term_afast = models.DateField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _search_cache(self):
        message = ""
        instance = BaseLicencaAfastamento.objects.filter(pk=self.oid)
        if instance.exists():
            instance = instance.last()
            message = "%s - %s" % (instance.servidor, instance.__str_restful__())
        return message

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    @property
    def departure(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        return BaseLicencaAfastamento.objects.get(pk=self.oid).my_origin

    def _previous_dependencies(self):
        """Este método seta as dependências anteriores de mesmo acronym, para manter a ordem de precedência no envio."""
        deps = super()._previous_dependencies()

        query = S3000.objects.valids_not_sent().filter(
            modify_event__acronym=self.acronym, registry_employee=self.registry_employee
        )
        deps.update(
            {
                f"{('s3000',)}": [
                    {
                        "events": query,
                        "acronyms": ("s3000",),
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                ]
            }
        )
        return deps

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2300', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2300", "s2298"),
                    "query_filter": None,
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2205', 's2206', 's2230', 's2231')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2230", "s2231"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }

    @staticmethod
    def update_departure(event):
        """Este método é responsável por atualizar o BaseLicencaAfastamento.event_esocial com o evento válido.

        Args:
            event(S2230, S2231):"""
        from rh.afastamento.models import BaseLicencaAfastamento

        if event.process_status > 5:
            BaseLicencaAfastamento.objects.filter(pk=event.oid).update(
                event_esocial=event.pk
            )


class S2231(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCessao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCessao/v_S_01_03_00"
    GROUP = 2
    NAME = "Cessão/Exercício em Outro Órgão"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    ini_cessao_dt_ini_cessao = models.DateField(null=True, blank=True)
    ini_cessao_cnpj_cess = models.CharField(max_length=14, null=True, blank=True)
    ini_cessao_resp_remun = models.CharField(max_length=1, null=True, blank=True)
    fim_cessao_dt_term_cessao = models.DateField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    @property
    def departure(self):
        from rh.afastamento.models import AfastamentoOutroOrgao

        return AfastamentoOutroOrgao.objects.get(pk=self.oid).my_origin

    def _previous_dependencies(self):
        """Este método seta as dependências anteriores de mesmo acronym, para manter a ordem de precedência no envio."""
        deps = super()._previous_dependencies()

        query = S3000.objects.valids_not_sent().filter(
            modify_event__acronym=self.acronym, registry_employee=self.registry_employee
        )
        deps.update(
            {
                f"{('s3000',)}": [
                    {
                        "events": query,
                        "acronyms": ("s3000",),
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                ]
            }
        )
        return deps

    def _base_dependencies(self):
        return {
            f"{('s2200',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200",),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2205', 's2206', 's2230', 's2231')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2206", "s2230", "s2231"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2298(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReintegr.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReintegr/v_S_01_03_00"
    GROUP = 2
    NAME = "Reintegração"
    ACTION_PERM = ACTION_RECTIFICATION
    CLOSE_PREVIOUS_EVENTS = True
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    info_reintegr_tp_reint = models.PositiveIntegerField()
    info_reintegr_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    info_reintegr_nr_lei_anistia = models.CharField(
        max_length=13, null=True, blank=True
    )
    info_reintegr_dt_efet_retorno = models.DateField()
    info_reintegr_dt_efeito = models.DateField()

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _previous_event(self):
        """O evento anterior será o s2299."""
        return (
            S2299.objects.valids_sent()
            .filter(
                registry_employee=self.registry_employee,
                start_validity__lt=self.start_validity,
            )
            .order_by("start_validity")
            .last()
        )

    def _base_dependencies(self):
        return {
            f"{('s2299', 's2200', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2299", "s2200", "s2298"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": False,
                }
            ],
            f"{('s2205', 's2206', 's2230', 's2231')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2206", "s2230", "s2231"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2299(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtDeslig.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtDeslig/v_S_01_03_00"
    GROUP = 2
    NAME = "Desligamento"
    ACTION_PERM = ACTION_RECTIFICATION
    CLOSE_PREVIOUS_EVENTS = True
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30)
    info_deslig_mtv_deslig = models.CharField(max_length=2, null=True, blank=True)
    info_deslig_dt_deslig = models.DateField()
    info_deslig_dt_av_prv = models.DateField(null=True, blank=True)
    info_deslig_ind_pagto_api = models.CharField(max_length=1)
    info_deslig_dt_proj_fim_api = models.DateField(null=True, blank=True)
    info_deslig_pens_alim = models.PositiveIntegerField(null=True, blank=True)
    info_deslig_perc_aliment = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_deslig_vr_alim = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_deslig_nr_proc_trab = models.CharField(max_length=20, null=True, blank=True)
    info_deslig_ind_pdv = models.CharField(max_length=1, null=True, blank=True)
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    observacoes_observacao = models.CharField(max_length=255, null=True, blank=True)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    transf_tit_cpf_substituto = models.CharField(max_length=11, null=True, blank=True)
    transf_tit_dt_nascto = models.DateField(null=True, blank=True)
    mudanca_cpf_novo_cpf = models.CharField(max_length=11, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    det_verbas_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    det_verbas_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    det_verbas_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_verbas_ind_apur_ir = models.PositiveIntegerField(null=True, blank=True)

    desc_folha_tp_desc = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    desc_folha_nr_doc = models.CharField(max_length=12, null=True, blank=True)
    desc_folha_observacao = models.CharField(max_length=55, null=True, blank=True)

    info_ag_nocivo_grau_exp = models.PositiveIntegerField(null=True, blank=True)
    info_simples_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    ide_adc_dt_ac_conv = models.DateField(null=True, blank=True)
    ide_adc_tp_ac_conv = models.CharField(max_length=1, null=True, blank=True)
    ide_adc_dsc = models.CharField(max_length=255, null=True, blank=True)
    ide_periodo_per_ref = models.CharField(max_length=7, null=True, blank=True)

    ide_periodo_ide_estab_lot_tp_insc = models.PositiveIntegerField(
        null=True, blank=True
    )
    ide_periodo_ide_estab_lot_nr_insc = models.CharField(
        max_length=14, null=True, blank=True
    )
    ide_periodo_ide_estab_lot_cod_lotacao = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_estab_lot_det_verbas_cod_rubr = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_estab_lot_det_verbas_ide_tab_rubr = models.CharField(
        max_length=8, null=True, blank=True
    )
    ide_estab_lot_det_verbas_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_estab_lot_det_verbas_ind_apur_ir = models.PositiveIntegerField(
        null=True, blank=True
    )

    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_s2299"
    )
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    proc_cs_nr_proc_jud = models.CharField(max_length=20, null=True, blank=True)
    consig_fgts_ins_consig = models.CharField(max_length=5, null=True, blank=True)
    consig_fgts_nr_contr = models.CharField(max_length=40, null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remun_apos_deslig_ind_remun = models.PositiveIntegerField(null=True, blank=True)
    remun_apos_deslig_dt_fim_remun = models.DateField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2298"),
                    "query_filter": (
                        Q(end_validity__isnull=True)
                        | Q(end_validity=self.start_validity)
                        | Q(closed_by_event__oid=self.oid)
                    ),
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": False,
                }
            ],
            f"{('s2205', 's2206', 's2230', 's2231')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2206", "s2230", "s2231"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }

    def _previous_event(self):
        """O evento anterior será o s2200."""
        return (
            S2200.objects.valids_sent()
            .filter(
                registry_employee=self.registry_employee,
                start_validity__lt=self.start_validity,
            )
            .order_by("start_validity")
            .last()
        )


class S2300(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVInicio.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVInicio/v_S_01_03_00"
    NAME = "Trabalhador Sem Vínculo – Início"
    GROUP = 2
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    trabalhador_cpf_trab = models.CharField(max_length=11)
    trabalhador_nm_trab = models.CharField(max_length=70)
    trabalhador_sexo = models.CharField(max_length=1, null=True, blank=True)
    trabalhador_raca_cor = models.PositiveIntegerField(null=True, blank=True)
    trabalhador_est_civ = models.PositiveIntegerField(null=True, blank=True)
    trabalhador_grau_instr = models.CharField(max_length=2, null=True, blank=True)
    trabalhador_nm_soc = models.CharField(max_length=70, null=True, blank=True)
    nascimento_dt_nascto = models.DateField(null=True, blank=True)
    nascimento_pais_nascto = models.CharField(max_length=3, null=True, blank=True)
    nascimento_pais_nac = models.CharField(max_length=3, null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    trab_imig_tmp_resid = models.PositiveIntegerField(null=True, blank=True)
    trab_imig_cond_ing = models.PositiveIntegerField(null=True, blank=True)
    info_deficiencia_def_fisica = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_visual = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_auditiva = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_def_mental = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_def_intelectual = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_deficiencia_reab_readap = models.CharField(max_length=1, null=True, blank=True)
    info_deficiencia_observacao = models.CharField(
        max_length=255, null=True, blank=True
    )
    dependente = models.ManyToManyField("Dependent", related_name="dependente_s2300")
    contato_fone_princ = models.CharField(max_length=13, null=True, blank=True)
    contato_email_princ = models.CharField(max_length=60, null=True, blank=True)
    info_tsv_inicio_cad_ini = models.CharField(max_length=1)
    info_tsv_inicio_matricula = models.CharField(max_length=30, null=True, blank=True)
    info_tsv_inicio_cod_categ = models.PositiveIntegerField()
    info_tsv_inicio_dt_inicio = models.DateField()
    info_tsv_inicio_nr_proc_trab = models.CharField(
        max_length=20, null=True, blank=True
    )
    info_tsv_inicio_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    cargo_funcao_nm_cargo = models.CharField(max_length=100, null=True, blank=True)
    cargo_funcao_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    cargo_funcao_nm_funcao = models.CharField(max_length=100, null=True, blank=True)
    cargo_funcao_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=999, null=True, blank=True)
    fgts_dt_opc_fgts = models.DateField(null=True, blank=True)
    info_dirigente_sindical_categ_orig = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_dirigente_sindical_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    info_dirigente_sindical_nr_insc = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_dirigente_sindical_dt_adm_orig = models.DateField(null=True, blank=True)
    info_dirigente_sindical_matric_orig = models.CharField(
        max_length=30, null=True, blank=True
    )
    info_dirigente_sindical_tp_reg_trab = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_dirigente_sindical_tp_reg_prev = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_trab_cedido_categ_orig = models.PositiveIntegerField(null=True, blank=True)
    info_trab_cedido_cnpj_cednt = models.CharField(max_length=14, null=True, blank=True)
    info_trab_cedido_matric_ced = models.CharField(max_length=30, null=True, blank=True)
    info_trab_cedido_dt_adm_ced = models.DateField(null=True, blank=True)
    info_trab_cedido_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
    info_trab_cedido_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_categ_orig = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_cnpj_orig = models.CharField(max_length=14, null=True, blank=True)
    info_mand_elet_matric_orig = models.CharField(max_length=30, null=True, blank=True)
    info_mand_elet_dt_exerc_orig = models.DateField(null=True, blank=True)
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_mand_elet_tp_reg_trab = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_nat_estagio = models.CharField(max_length=1, null=True, blank=True)
    info_estagiario_niv_estagio = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_area_atuacao = models.CharField(
        max_length=100, null=True, blank=True
    )
    info_estagiario_nr_apol = models.CharField(max_length=30, null=True, blank=True)
    info_estagiario_dt_prev_term = models.DateField(null=True, blank=True)
    inst_ensino_cnpj_inst_ensino = models.CharField(
        max_length=14, null=True, blank=True
    )
    inst_ensino_nm_razao = models.CharField(max_length=100, null=True, blank=True)
    inst_ensino_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    inst_ensino_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    inst_ensino_bairro = models.CharField(max_length=90, null=True, blank=True)
    inst_ensino_cep = models.CharField(max_length=8, null=True, blank=True)
    inst_ensino_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    inst_ensino_uf = models.CharField(max_length=2, null=True, blank=True)
    age_integracao_cnpj_agnt_integ = models.CharField(
        max_length=14, null=True, blank=True
    )
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    supervisor_estagio_cpf_supervisor = models.CharField(
        max_length=11, null=True, blank=True
    )
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=255, null=True, blank=True)
    afastamento_dt_ini_afast = models.DateField(null=True, blank=True)
    afastamento_cod_mot_afast = models.CharField(max_length=2, null=True, blank=True)
    termino_dt_term = models.DateField(null=True, blank=True)

    def _search_cache(self):
        return self.trabalhador_nm_trab

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.trabalhador_cpf_trab

    def _base_dependencies(self):
        employer = get_current_config().employer
        return {
            f"{('s1005',)}": [
                {
                    "oid": employer.pk,
                    "registry_employee": None,
                    "acronyms": ("s1005",),
                    "query_filter": None,
                    "filter_query_instance": None,
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": False,
                }
            ]
        }


class S2306(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVAltContr.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVAltContr/v_S_01_03_00"
    GROUP = 2
    NAME = "Alteração contratual (TSV)"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_trab_sem_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_trab_sem_vinculo_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_trab_sem_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_alteracao_dt_alteracao = models.DateField()
    info_tsv_alteracao_nat_atividade = models.PositiveIntegerField(
        null=True, blank=True
    )
    cargo_funcao_nm_cargo = models.CharField(max_length=100, null=True, blank=True)
    cargo_funcao_cbo_cargo = models.CharField(max_length=6, null=True, blank=True)
    cargo_funcao_nm_funcao = models.CharField(max_length=100, null=True, blank=True)
    cargo_funcao_cbo_funcao = models.CharField(max_length=6, null=True, blank=True)
    remuneracao_vr_sal_fx = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remuneracao_und_sal_fixo = models.PositiveIntegerField(null=True, blank=True)
    remuneracao_dsc_sal_var = models.CharField(max_length=999, null=True, blank=True)
    info_dirigente_sindical_tp_reg_prev = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_trab_cedido_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_mand_elet_ind_remun_cargo = models.CharField(
        max_length=1, null=True, blank=True
    )
    info_mand_elet_tp_reg_prev = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_nat_estagio = models.CharField(max_length=1, null=True, blank=True)
    info_estagiario_niv_estagio = models.PositiveIntegerField(null=True, blank=True)
    info_estagiario_area_atuacao = models.CharField(
        max_length=100, null=True, blank=True
    )
    info_estagiario_nr_apol = models.CharField(max_length=30, null=True, blank=True)
    info_estagiario_dt_prev_term = models.DateField(null=True, blank=True)
    inst_ensino_cnpj_inst_ensino = models.CharField(
        max_length=14, null=True, blank=True
    )
    inst_ensino_nm_razao = models.CharField(max_length=100, null=True, blank=True)
    inst_ensino_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    inst_ensino_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    inst_ensino_bairro = models.CharField(max_length=90, null=True, blank=True)
    inst_ensino_cep = models.CharField(max_length=8, null=True, blank=True)
    inst_ensino_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    inst_ensino_uf = models.CharField(max_length=2, null=True, blank=True)
    age_integracao_cnpj_agnt_integ = models.CharField(
        max_length=14, null=True, blank=True
    )
    supervisor_estagio_cpf_supervisor = models.CharField(
        max_length=11, null=True, blank=True
    )
    local_trab_geral_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    local_trab_geral_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    local_trab_geral_desc_comp = models.CharField(max_length=80, null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _search_cache(self):
        return self.description

    def employee_cpf(self):
        return self.ide_trab_sem_vinculo_cpf_trab

    def _base_dependencies(self):
        return {
            f"{('s2300',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2300",),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2205', 's2306')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2205", "s2306"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2399(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTSVTermino.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtTSVTermino/v_S_01_03_00"
    GROUP = 2
    NAME = "Trabalhador Sem Vínculo – Término"
    ACTION_PERM = ACTION_RECTIFICATION
    CLOSE_PREVIOUS_EVENTS = True
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_trab_sem_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_trab_sem_vinculo_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    ide_trab_sem_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_termino_dt_term = models.DateField()
    info_tsv_termino_mtv_deslig_tsv = models.CharField(
        max_length=2, null=True, blank=True
    )
    info_tsv_termino_pens_alim = models.PositiveIntegerField(null=True, blank=True)
    info_tsv_termino_perc_aliment = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_tsv_termino_vr_alim = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_tsv_termino_nr_proc_trab = models.CharField(
        max_length=20, null=True, blank=True
    )
    mudanca_cpf_novo_cpf = models.CharField(max_length=11, null=True, blank=True)
    dm_dev_ide_dm_dev = models.CharField(max_length=30, null=True, blank=True)
    ide_estab_lot_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_estab_lot_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_estab_lot_cod_lotacao = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_cod_rubr = models.CharField(max_length=30, null=True, blank=True)
    det_verbas_ide_tab_rubr = models.CharField(max_length=8, null=True, blank=True)
    det_verbas_qtd_rubr = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    det_verbas_fator_rubr = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    det_verbas_vr_rubr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    det_verbas_ind_apur_ir = models.PositiveIntegerField(null=True, blank=True)

    desc_folha_tp_desc = models.PositiveIntegerField(null=True, blank=True)
    desc_folha_inst_financ = models.CharField(max_length=3, null=True, blank=True)
    desc_folha_nr_doc = models.CharField(max_length=12, null=True, blank=True)
    desc_folha_observacao = models.CharField(max_length=55, null=True, blank=True)

    info_simples_ind_simples = models.PositiveIntegerField(null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="proc_jud_trab_s2399"
    )
    info_mv_ind_mv = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    remun_outr_empr_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    remun_outr_empr_vlr_remun_oe = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    quarentena_dt_fim_quar = models.DateField(null=True, blank=True)
    dm_dev_ind_rra = models.CharField(max_length=1, null=True, blank=True)
    info_rra_tp_proc_rra = models.PositiveIntegerField(null=True, blank=True)
    info_rra_nr_proc_rra = models.CharField(max_length=21, null=True, blank=True)
    info_rra_desc_rra = models.CharField(max_length=50, null=True, blank=True)
    info_rra_qtd_meses_rra = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_custas = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    desp_proc_jud_vlr_desp_advogados = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    ide_adv_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_adv_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    ide_adv_vlr_adv = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    remun_apos_term_ind_remun = models.PositiveIntegerField(null=True, blank=True)
    remun_apos_term_dt_fim_remun = models.DateField(null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.ide_trab_sem_vinculo_cpf_trab

    def _base_dependencies(self):
        return {
            f"{('s2300',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2300",),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2206', 's2230', 's2231')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2206", "s2230", "s2231"),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }

    def _previous_event(self):
        """O evento anterior será o s2300."""
        return (
            S2300.objects.valids_sent()
            .filter(
                registry_employee=self.registry_employee,
                start_validity__lt=self.start_validity,
            )
            .order_by("start_validity")
            .last()
        )


class S3000(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtExclusao.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtExclusao/v_S_01_03_00"
    GROUP = 2
    NAME = "Exclusão de Eventos"
    ACTION_PERM = ACTION
    CLOSE_PREVIOUS_EVENTS = True

    info_exclusao_tp_evento = models.CharField(max_length=6)
    info_exclusao_nr_rec_evt = models.CharField(max_length=23)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11, null=True, blank=True)
    ide_folha_pagto_ind_apuracao = models.PositiveIntegerField(
        choices=Choice.get_choices_for("esocial", "INDICATIVE_ASCERTAINMENT_PERIOD"),
        null=True,
        blank=True,
    )
    ide_folha_pagto_per_apur = models.CharField(max_length=7, null=True, blank=True)

    def _search_cache(self):
        return f"{self.modify_event.search_cache}" if self.modify_event else ""

    def close_previous_events(self, delete=False):
        """Este método fecha(preenche end_validity) do evento que foi modificado ou atualiza o modify_event de acordo com
        as seguintes regras.
            - Removendo(S3000) o S2299, antes quero saber se ele fechou(close_event) alguém e se a remoção(s3000) foi correta,
                ou seja, S3000.process_status (201, 202). Então executa o @close_previous_event do S2299 que fará a limpeza de um S2200.

            - De outra forma, se não deu certo deve-se fazer o update do s3000 removendo o modify_by_event.
        """
        if self.CLOSE_PREVIOUS_EVENTS:
            if (
                hasattr(self.modify_event, "close_event")
                and self.modify_event.close_event
                and self.process_status in PROCESS_STATUS_EVENT_VALIDS_SENT
            ):
                self.modify_event.event.close_previous_events(delete=True)
            elif self.process_status in (401, 402, 403) or delete is True:
                if self.modify_event:
                    Event.objects.filter(pk=self.modify_event.pk).update(
                        modified_by_event_cache=""
                    )
                Event.objects.filter(pk=self.pk).update(modify_event=None)

    def _base_dependencies(self):
        deps = {}

        if self.modify_event.acronym in ("s1200", "s1202", "s1207"):
            buff_exclusion = []
            query = S3000.objects.filter(
                registry_person=self.registry_person
            ).valids_not_sent()
            for event in query:
                buff_exclusion.append(
                    {
                        "events": [event],
                        "registry_person": self.registry_person,
                        "acronyms": ("s3000",),
                        "query_filter": None,
                        "filter_query_instance": None,
                        "create_if_not_exist": False,
                        "required": False,
                        "filter_validity_in": False,
                    }
                )
            deps.update({f"{('s3000', )}": buff_exclusion})

        return deps


class Totalizer(Event):
    CREATE_IDENTIFIER = False

    class Meta:
        abstract = True

    @property
    def file_path(self):
        self._file_path = "%s/%s" % (self.file_directory, self.file_name)
        batch = self.event_connection.batch
        if batch:
            _bt_file_path = batch.file_path.replace("batch.xml", "%s" % self.file_name)
            batch_path = batch.file_path.replace("batch.xml", "")
            if os.path.exists(batch_path):
                self._file_path = _bt_file_path
        return self._file_path

    @property
    def has_exclusion(self):
        if self.event_connection:
            return self.event_connection.has_exclusion
        return super().has_exclusion

    @property
    def is_invalid(self):
        if self.event_connection:
            return self.event_connection.is_invalid
        return super().is_invalid

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class S5001(Totalizer):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtBasesTrab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtBasesTrab/v_S_01_03_00"
    GROUP = 3
    NAME = "Informações das contribuições sociais por trabalhador"
    ACTION_PERM = ACTION
    MAP_CLASS_XML = {"IdeEstabLot": "IdeEstabLot5001"}
    MAP_FIELDS_XML = {"ide_estab_lot5001": "ide_estab_lot"}

    TP_CR = {
        108201: "Contribuição Previdenciária - CP descontada do segurado empregado/avulso",
        108202: "CP descontada do segurado empregado rural curto prazo - Lei 11.718/2008",
        108203: "CP descontada do segurado empregado doméstico",
        108204: "CP descontada do segurado especial curto prazo - Lei 11.718/2008",
        108205: "CP descontada do segurado empregado do segurado especial",
        108207: "CP descontada do segurado empregado do MEI",
        108221: "CP descontada do segurado empregado/avulso 13° salário",
        108222: "CP descontada do segurado empregado rural curto prazo 13° salário - Lei 11.718/2008",
        108223: "CP descontada do segurado empregado doméstico 13° salário",
        108224: "CP descontada do segurado especial curto prazo 13° salário - Lei 11.718/2008",
        108225: "CP descontada do segurado empregado do segurado especial 13° salário",
        109901: "CP descontada do contribuinte individual, alíquota de 11%",
        109902: "CP descontada do contribuinte individual,alíquota de 20%",
    }

    event_connection = models.ForeignKey(
        Event, related_name="eventconnection_s5001", on_delete=models.CASCADE
    )

    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_trabalhador_cpf_trab = models.CharField(max_length=11)
    sucessao_vinc_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    sucessao_vinc_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    sucessao_vinc_matric_ant = models.CharField(max_length=30, null=True, blank=True)
    sucessao_vinc_dt_adm = models.DateField(null=True, blank=True)
    info_interm_dia = models.PositiveIntegerField(null=True, blank=True)
    info_interm_hrs_trab = models.CharField(max_length=4, null=True, blank=True)
    info_compl_cont_cod_cbo = models.CharField(max_length=6, null=True, blank=True)
    info_compl_cont_nat_atividade = models.PositiveIntegerField(null=True, blank=True)
    info_compl_cont_qtd_dias_trab = models.PositiveIntegerField(null=True, blank=True)
    proc_jud_trab = models.ManyToManyField(
        "IdeProcesso", related_name="procjudtrab_s5001"
    )

    info_cp_calc = models.ManyToManyField("InfoCpCalc", related_name="infocpcalc_s5001")

    info_cp_class_trib = models.CharField(max_length=2, null=True, blank=True)

    ide_estab_lot = models.ManyToManyField(
        "IdeEstabLot5001", related_name="ideestablot5001_s5001"
    )

    calc_terc_tp_cr = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    calc_terc_vr_cs_seg_terc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    calc_terc_vr_desc_terc = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    det_info_per_ref_ind13 = models.PositiveIntegerField(null=True, blank=True)
    det_info_per_ref_tp_vr_per_ref = models.PositiveIntegerField(null=True, blank=True)
    det_info_per_ref_vr_per_ref = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_categ_pis_pasep_matricula = models.CharField(
        max_length=30, null=True, blank=True
    )
    info_categ_pis_pasep_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_base_pis_pasep_ind13 = models.PositiveIntegerField(null=True, blank=True)
    info_base_pis_pasep_tp_valor_pis_pasep = models.PositiveIntegerField(
        null=True, blank=True
    )
    info_base_pis_pasep_valor_pis_pasep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    def employee(self):
        return Employee.objects.filter(pessoa_fisica__cpf=self.registry_person)

    def delete(self, *args, **kwargs):
        for obj in self.proc_jud_trab.all():
            obj.delete()
        for obj in self.info_cp_calc.all():
            obj.delete()
        for obj in self.ide_estab_lot.all():
            obj.delete()
        super(S5001, self).delete(*args, **kwargs)

    def update_from_info_cp_calc(self):
        """Este método modifica o process_status para 202 quando houver diferença entre os campos:
        info_cp_calc_vr_cp_seg e info_cp_calc_vr_desc_seg."""
        if self.info_cp_calc.exclude(
            info_cp_calc_vr_cp_seg=F("info_cp_calc_vr_desc_seg")
        ).exists():
            self.update_status(new_status=202, force=True)


class S5002(Totalizer):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtIrrfBenef.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrfBenef/v_S_01_03_00"
    GROUP = 3
    NAME = "Imposto de Renda Retido na Fonte por Trabalhador"
    MAP_CLASS_XML = {
        "DmDev": "DemonstrativeTot",
        "InfoIR": "InfoIrrf",
        "TotApurMen": "MonthlyCalculatedIrrf",
        "TotApurDia": "DayCalculatedIrrf",
    }
    MAP_FIELDS_XML = {
        "demonstrative_tot": "ide_trabalhador_dm_dev",
        "info_irrf": "dm_dev_info_ir",
        "monthly_calculated_irrf": "tot_apur_men",
        "day_calculated_irrf": "apur_dia",
        "info_ir_tp_info_ir": "tp_info_ir",
        "info_ir_valor": "valor",
        "tot_apur_men_cr_men": "cr_men",
        "tot_apur_men_vlr_cr_men": "vlr_cr_men",
        "tot_apur_dia_per_apur_dia": "per_apur_dia",
        "tot_apur_dia_cr_dia": "cr_dia",
        "tot_apur_dia_vlr_cr_dia": "vlr_cr_dia",
    }

    event_connection = models.ForeignKey(
        Event, related_name="eventconnection_s5002", on_delete=models.CASCADE
    )

    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_trabalhador_cpf_benef = models.CharField(max_length=11)
    ide_trabalhador_dm_dev = models.ManyToManyField(
        "DemonstrativeTot", related_name="dmdev_s5002"
    )

    def delete(self, *args, **kwargs):
        for obj in self.ide_trabalhador_dm_dev.all():
            obj.delete()
        super(S5002, self).delete(*args, **kwargs)

    def update_from_tot_apur_men(self, task=None):
        from esocial.extractors.s1210 import S1210Extractor
        from rh.gfp.models import Evento

        tag = "irrf-esocial"

        ir_paycheck = S1210Extractor.total_ir_paycheck(
            month=self.competence_month,
            year=self.competence_year,
            registry_person=self.ide_trabalhador_cpf_benef,
            task=task,
        )

        def get_employee():
            employee = Employee.objects.filter(
                pessoa_fisica__cpf=self.ide_trabalhador_cpf_benef
            )
            if employee.filter(ativo=True).exists():
                employee = employee.filter(ativo=True).last()
            else:
                employee = employee.last()
            return employee

        def total_vlr_cr_men():
            """Calcula valor mensal em S5002."""
            query_apor_men = MonthlyCalculatedIrrf.objects.filter(
                dmdevinfoir_demonstrativetot__dmdev_s5002=self
            )
            vlr_cr_men = (
                query_apor_men.aggregate(sum_vlr_cr_men=Sum("vlr_cr_men")).get(
                    "sum_vlr_cr_men"
                )
                or 0
            )

            if not query_apor_men.exists() and ir_paycheck:
                employee = get_employee()
                msg = f"{self} - Não possui apuração mensal ({self.competence_month}/{self.competence_year})."
                msg += f"\n{employee.type_by_possession} - {employee}"
                task_info(task, msg=msg, type_of=2)
            return vlr_cr_men

        vlr_cr_men = total_vlr_cr_men()

        if ir_paycheck != vlr_cr_men:
            employee = get_employee()
            events_ir = list(
                Evento.objects.filter(tags__label=tag).values_list("numero", flat=True)
            )
            msg = f"{self} ({self.competence_month}/{self.competence_year})"
            msg += f" - Diferença de IR eSocial ({vlr_cr_men}) x Folha ({ir_paycheck})."
            msg += f" Verifique eventos com tag {tag}: {events_ir}."
            msg += f"\n{employee.type_by_possession} - {employee}"
            task_info(task, msg=msg, type_of=2)
            self.update_status(new_status=202, force=True)


class S5011(Totalizer):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCS.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCS/v_S_01_03_00"
    GROUP = 3
    NAME = "Informações das contribuições sociais consolidadas por contribuinte"
    ACTION_PERM = ACTION
    MAP_CLASS_XML = {"IdeEstab": "IdeEstabLot5011"}
    MAP_FIELDS_XML = {
        "ide_estab_lot5011": "ide_estab",
        "info_cr_contrib_tp_cr": "tp_cr",
        "info_cr_contrib_vr_cr": "vr_cr",
        "info_cr_contrib_vr_susp_cr": "vr_cr_susp",
    }

    event_connection = models.ForeignKey(
        Event, related_name="eventconnection_s5011", on_delete=models.CASCADE
    )

    info_cs_nr_rec_arq_base = models.CharField(max_length=23)
    info_cs_ind_exist_info = models.PositiveIntegerField()

    info_cp_seg_vr_desc_cp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    info_cp_seg_vr_cp_seg = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_contrib_class_trib = models.CharField(max_length=2)

    info_pj_ind_coop = models.PositiveIntegerField(null=True, blank=True)
    info_pj_ind_constr = models.PositiveIntegerField(null=True, blank=True)
    info_pj_ind_subst_patr = models.PositiveIntegerField(null=True, blank=True)
    info_pj_perc_red_contrib = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_pj_perc_transf = models.PositiveIntegerField(null=True, blank=True)
    # info_pj_ind_trib_folha_pis_cofins = models.CharField(max_length=1, null=True, blank=True)
    info_pj_ind_trib_folha_pis_pasep = models.CharField(
        max_length=1, null=True, blank=True
    )
    bases_pis_pasep_vr_bc_pis_pasep = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    bases_pis_pasep_vr_bc_pis_pasep_susp = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    info_at_conc_fator_mes = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    info_at_conc_fator_13 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    ide_estab = models.ManyToManyField(
        "IdeEstabLot5011", related_name="ideestab_ideestablot5011"
    )
    info_cr_contrib = models.ManyToManyField(
        "InfoCRContrib", related_name="crcontrib_s5011"
    )

    def delete(self, *args, **kwargs):
        for obj in self.tot_apur_men.all():
            obj.delete()
        super(S5012, self).delete(*args, **kwargs)


class S5012(Totalizer):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtIrrf.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrf/v_S_01_03_00"
    GROUP = 3
    NAME = "S-5012 - Imposto de Renda Retido na Fonte Consolidado por Contribuinte"
    ACTION_PERM = ACTION
    MAP_CLASS_XML = {
        "InfoCRMen": "MonthlyCalculatedIrrf",
        "TotApurDia": "DayCalculatedIrrf",
    }
    MAP_FIELDS_XML = {
        "monthly_calculated_irrf": "tot_apur_men",
        "info_cr_men_cr_men": "cr_men",
        "info_cr_men_vr_cr_men": "vlr_cr_men",
        "day_calculated_irrf": "apur_dia",
        "tot_apur_dia_per_apur_dia": "per_apur_dia",
        "tot_apur_dia_cr_dia": "cr_dia",
        "tot_apur_dia_vlr_cr_dia": "vlr_cr_dia",
    }

    event_connection = models.ForeignKey(
        Event, related_name="eventconnection_s5012", on_delete=models.CASCADE
    )

    info_irrf_nr_rec_arq_base = models.CharField(max_length=23)
    info_irrf_ind_exist_info = models.PositiveIntegerField()

    tot_apur_men = models.ManyToManyField("MonthlyCalculatedIrrf", related_name="s5012")

    def delete(self, *args, **kwargs):
        for obj in self.tot_apur_men.all():
            obj.delete()
        super(S5012, self).delete(*args, **kwargs)

    def update_from_tot_apur_men(self, task=None):
        from esocial.extractors.s1210 import S1210Extractor
        from rh.gfp.models import Evento

        tag = "irrf-esocial"

        events_ir = list(
            Evento.objects.filter(tags__label=tag).values_list("numero", flat=True)
        )

        def total_vlr_cr_men():
            """Calcula valor mensal em S5012."""
            query_apor_men = MonthlyCalculatedIrrf.objects.filter(s5012=self)
            vlr_cr_men = (
                query_apor_men.aggregate(sum_vlr_cr_men=Sum("vlr_cr_men")).get(
                    "sum_vlr_cr_men"
                )
                or 0
            )
            if not query_apor_men.exists() and events_ir:
                msg = f"{self} - Não possui apuração mensal. "
                task_info(task, msg=msg, type_of=2)
            return vlr_cr_men

        ir_paycheck = S1210Extractor.total_ir_paycheck(
            month=self.competence_month, year=self.competence_year
        )
        vlr_cr_men = total_vlr_cr_men()

        if ir_paycheck != vlr_cr_men:
            msg = f"{self} - Diferença de IR eSocial ({vlr_cr_men}) x Folha ({ir_paycheck})."
            msg += f" Verifique eventos com tag {tag}: {events_ir}."
            task_info(task, msg=msg, type_of=2)
            self.update_status(new_status=202, force=True)


class S5501(Totalizer):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtTribProcTrab.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtIrrf/v_S_01_03_00"
    GROUP = 3
    NAME = "S-5501 - Informações Consolidadas de Tributos Decorrentes de Processo Trabalhista"
    ACTION_PERM = ACTION
    MAP_CLASS_XML = {}
    MAP_FIELDS_XML = {}

    event_connection = models.ForeignKey(
        Event, related_name="eventconnection_s5501", on_delete=models.CASCADE
    )

    ide_evento_nr_rec_arq_base = models.CharField(max_length=23)
    ide_proc_nr_proc_trab = models.CharField(max_length=20)
    ide_proc_per_apur = models.CharField(max_length=7)

    info_tributos = models.ManyToManyField(
        "InfoTribute", related_name="infotributos_s5501"
    )

    def delete(self, *args, **kwargs):
        for obj in self.info_tributos.all():
            obj.delete()
        super(S5501, self).delete(*args, **kwargs)


class S2400(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenefIn.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenefIn/v_S_01_03_00"
    GROUP = 2
    NAME = "Cadastro de Beneficiário - Entes Públicos - Início"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    beneficiario_cpf_benef = models.CharField(max_length=11)
    beneficiario_nm_benefic = models.CharField(max_length=70)
    beneficiario_dt_nascto = models.DateField()
    beneficiario_dt_inicio = models.DateField()
    beneficiario_sexo = models.CharField(max_length=1, null=True, blank=True)
    beneficiario_raca_cor = models.PositiveIntegerField(null=True, blank=True)
    beneficiario_est_civ = models.PositiveIntegerField(null=True, blank=True)
    beneficiario_inc_fis_men = models.CharField(max_length=1, null=True, blank=True)
    beneficiario_dt_inc_fis_men = models.DateField(null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2400"
    )

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def employee_cpf(self):
        return self.beneficiario_cpf_benef

    def _search_cache(self):
        return self.beneficiario_nm_benefic

    def delete(self, *args, **kwargs):
        for dependent in self.dependente.all():
            dependent.delete()
        super(S2400, self).delete(*args, **kwargs)

    def _base_dependencies(self):
        employer = get_current_config().employer
        return {
            f"{('s1005',)}": [
                {
                    "oid": employer.pk,
                    "registry_employee": None,
                    "acronyms": ("s1005",),
                    "query_filter": None,
                    "filter_query_instance": None,
                    "create_if_not_exist": True,
                    "required": True,
                    "filter_validity_in": False,
                }
            ]
        }


class S2405(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenefAlt.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenefAlt/v_S_01_03_00"
    GROUP = 2
    NAME = "Cadastro de Beneficiário - Entes Públicos - Alteração"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_benef_cpf_benef = models.CharField(max_length=11)
    alteracao_dt_alteracao = models.DateField()
    dados_benef_nm_benefic = models.CharField(max_length=70, null=True, blank=True)
    dados_benef_sexo = models.CharField(max_length=1, null=True, blank=True)
    dados_benef_raca_cor = models.PositiveIntegerField(null=True, blank=True)
    dados_benef_est_civ = models.PositiveIntegerField(null=True, blank=True)
    dados_benef_inc_fis_men = models.CharField(max_length=1, null=True, blank=True)
    brasil_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    brasil_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    brasil_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    brasil_complemento = models.CharField(max_length=30, null=True, blank=True)
    brasil_bairro = models.CharField(max_length=90, null=True, blank=True)
    brasil_cep = models.CharField(max_length=8, null=True, blank=True)
    brasil_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    brasil_uf = models.CharField(max_length=2, null=True, blank=True)
    exterior_pais_resid = models.CharField(max_length=3, null=True, blank=True)
    exterior_dsc_lograd = models.CharField(max_length=100, null=True, blank=True)
    exterior_nr_lograd = models.CharField(max_length=10, null=True, blank=True)
    exterior_complemento = models.CharField(max_length=30, null=True, blank=True)
    exterior_bairro = models.CharField(max_length=90, null=True, blank=True)
    exterior_nm_cid = models.CharField(max_length=50, null=True, blank=True)
    exterior_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    dependente = models.ManyToManyField(
        "Dependent", related_name="dependente_register_s2405"
    )

    @property
    def json_model_by_action(self):
        return json_model_by_action(
            self.json_model, self.action, not_exclude=["alteracao"]
        )

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _search_cache(self):
        return self.dados_benef_nm_benefic

    def _base_dependencies(self):
        return {
            f"{('s2400',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2400",),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ],
            f"{('s2405',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2405",),
                    "query_filter": None,
                    "filter_query_instance": Q(matricula=self.registry_employee),
                    "create_if_not_exist": False,
                    "required": False,
                    "filter_validity_in": False,
                }
            ],
        }


class S2410(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenIn.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenIn/v_S_01_03_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Início"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    beneficiario_cpf_benef = models.CharField(max_length=11)
    beneficiario_matricula = models.CharField(max_length=30, null=True, blank=True)
    beneficiario_cnpj_origem = models.CharField(max_length=14, null=True, blank=True)
    info_ben_inicio_cad_ini = models.CharField(max_length=1)
    info_ben_inicio_ind_sit_benef = models.PositiveIntegerField(null=True, blank=True)
    info_ben_inicio_nr_beneficio = models.CharField(max_length=20)
    info_ben_inicio_dt_ini_beneficio = models.DateField()
    info_ben_inicio_dt_public = models.DateField(null=True, blank=True)
    dados_beneficio_tp_beneficio = models.CharField(max_length=4, null=True, blank=True)
    dados_beneficio_tp_plan_rp = models.SmallIntegerField()
    dados_beneficio_dsc = models.CharField(max_length=255, null=True, blank=True)
    dados_beneficio_ind_dec_jud = models.CharField(max_length=1, blank=True, null=True)
    info_pen_morte_tp_pen_morte = models.PositiveIntegerField(blank=True, null=True)
    inst_pen_morte_cpf_inst = models.CharField(max_length=11, blank=True, null=True)
    inst_pen_morte_dt_inst = models.DateField(null=True, blank=True)
    sucessao_benef_cnpj_orgao_ant = models.CharField(
        max_length=14, null=True, blank=True
    )
    sucessao_benef_nr_beneficio_ant = models.CharField(
        max_length=20, null=True, blank=True
    )
    sucessao_benef_dt_transf = models.DateField(null=True, blank=True)
    sucessao_benef_observacao = models.CharField(max_length=255, null=True, blank=True)
    mudanca_cpf_cpf_ant = models.CharField(max_length=11, null=True, blank=True)
    mudanca_cpf_nr_beneficio_ant = models.CharField(
        max_length=20, null=True, blank=True
    )
    mudanca_cpf_dt_alt_cpf = models.DateField(null=True, blank=True)
    mudanca_cpf_observacao = models.CharField(max_length=255, null=True, blank=True)
    info_ben_termino_dt_term_beneficio = models.DateField(null=True, blank=True)
    info_ben_termino_mtv_termino = models.CharField(max_length=2, null=True, blank=True)

    def employee(self):
        return Employee.objects.get(matricula=self.registry_employee)

    def _search_cache(self):
        return self.registry_employee

    def _base_dependencies(self):
        return {
            f"{('s2400',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2400",),
                    "query_filter": None,
                    "filter_query_instance": Q(
                        servidor__matricula=self.registry_employee
                    ),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class S2416(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenAlt.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenAlt/v_S_01_03_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Alteração"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_ben_alteracao_dt_alt_beneficio = models.DateField()
    dados_beneficio_tp_beneficio = models.CharField(max_length=4)
    dados_beneficio_tp_plan_rp = models.SmallIntegerField()
    dados_beneficio_dsc = models.CharField(max_length=255, null=True, blank=True)
    dados_beneficio_ind_suspensao = models.CharField(max_length=1)
    info_pen_morte_tp_pen_morte = models.PositiveIntegerField(blank=True, null=True)
    suspensao_mtv_suspensao = models.CharField(max_length=2, null=True, blank=True)
    suspensao_dsc_suspensao = models.CharField(max_length=255, null=True, blank=True)

    def _base_dependencies(self):
        return {
            f"{('s2410',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2410",),
                    "query_filter": None,
                    "filter_query_instance": Q(
                        servidor__matricula=self.registry_employee
                    ),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class S2418(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtReativBen.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtReativBen/v_S_01_03_00"
    GROUP = 2
    NAME = "Reativação de Benefício - Entes Públicos"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_reativ_dt_efet_reativ = models.DateField()
    info_reativ_dt_efeito = models.DateField()

    def _base_dependencies(self):
        return {
            f"{('s2420',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2420",),
                    "query_filter": None,
                    "filter_query_instance": Q(
                        servidor__matricula=self.registry_employee
                    ),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class S2420(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCdBenTerm.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCdBenTerm/v_S_01_03_00"
    GROUP = 2
    NAME = "Cadastro de Benefício - Entes Públicos - Término"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_beneficio_cpf_benef = models.CharField(max_length=11)
    ide_beneficio_nr_beneficio = models.CharField(max_length=20)
    info_ben_termino_dt_term_beneficio = models.DateField()
    info_ben_termino_mtv_termino = models.CharField(max_length=2)
    info_ben_termino_cnpj_orgao_suc = models.CharField(
        max_length=14, null=True, blank=True
    )
    info_ben_termino_novo_cpf = models.CharField(max_length=11, null=True, blank=True)

    def _base_dependencies(self):
        return {
            f"{('s2410',)}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2410",),
                    "query_filter": None,
                    "filter_query_instance": Q(
                        servidor__matricula=self.registry_employee
                    ),
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class S2210(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtCAT.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtCAT/v_S_01_03_00"
    GROUP = 2
    NAME = "Comunicação de Acidente de Trabalho"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    cat_dt_acid = models.DateField()
    cat_tp_acid = models.PositiveIntegerField()
    cat_hr_acid = models.CharField(max_length=4, null=True, blank=True)
    cat_hrs_trab_antes_acid = models.CharField(max_length=4, null=True, blank=True)
    cat_tp_cat = models.PositiveIntegerField()
    cat_ind_cat_obito = models.CharField(max_length=1)
    cat_dt_obito = models.DateField(null=True, blank=True)
    cat_ind_comun_policia = models.CharField(max_length=1)
    cat_cod_sit_geradora = models.PositiveIntegerField()
    cat_iniciat_cat = models.PositiveIntegerField()
    cat_obs_cat = models.CharField(max_length=999, null=True, blank=True)
    cat_ult_dia_trab = models.DateField(null=True, blank=True)
    cat_houve_afast = models.CharField(max_length=1, null=True, blank=True)
    local_acidente_tp_local = models.PositiveIntegerField()
    local_acidente_dsc_local = models.CharField(max_length=255, null=True, blank=True)
    local_acidente_tp_lograd = models.CharField(max_length=4, null=True, blank=True)
    local_acidente_dsc_lograd = models.CharField(max_length=100)
    local_acidente_nr_lograd = models.CharField(max_length=10)
    local_acidente_complemento = models.CharField(max_length=30, null=True, blank=True)
    local_acidente_bairro = models.CharField(max_length=90, null=True, blank=True)
    local_acidente_cep = models.CharField(max_length=8, null=True, blank=True)
    local_acidente_cod_munic = models.PositiveIntegerField(null=True, blank=True)
    local_acidente_uf = models.CharField(max_length=2, null=True, blank=True)
    local_acidente_pais = models.CharField(max_length=3, null=True, blank=True)
    local_acidente_cod_postal = models.CharField(max_length=12, null=True, blank=True)
    ide_local_acid_tp_insc = models.PositiveIntegerField(null=True, blank=True)
    ide_local_acid_nr_insc = models.CharField(max_length=14, null=True, blank=True)
    parte_atingida_cod_parte_ating = models.PositiveIntegerField()
    parte_atingida_lateralidade = models.PositiveIntegerField()
    agente_causador_cod_agnt_causador = models.PositiveIntegerField()
    atestado_dt_atendimento = models.DateField()
    atestado_hr_atendimento = models.CharField(max_length=4)
    atestado_ind_internacao = models.CharField(max_length=1)
    atestado_dur_trat = models.PositiveIntegerField()
    atestado_ind_afast = models.CharField(max_length=1)
    atestado_dsc_lesao = models.PositiveIntegerField()
    atestado_dsc_comp_lesao = models.CharField(max_length=200, null=True, blank=True)
    atestado_diag_provavel = models.CharField(max_length=100, null=True, blank=True)
    atestado_cod_cid = models.CharField(max_length=4)
    atestado_observacao = models.CharField(max_length=255, null=True, blank=True)
    emitente_nm_emit = models.CharField(max_length=70)
    emitente_ide_oc = models.PositiveIntegerField()
    emitente_nr_oc = models.CharField(max_length=14)
    emitente_uf_oc = models.CharField(max_length=2, null=True, blank=True)
    cat_origem_nr_rec_cat_orig = models.CharField(max_length=23, null=True, blank=True)

    def employee(self):
        return Employee.objects.filter(matricula=self.ide_vinculo_matricula)

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    @property
    def instance_outside(self):
        from health.sst.models import WorkAccidentCommunication

        return WorkAccidentCommunication.objects.filter(pk=self.oid).last()

    def _search_cache(self):
        return f"{self.employee()}"

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2300', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2300", "s2298"),
                    "query_filter": None,
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class Exam(Event):

    NAME = "Exam"
    INTERNAL = True

    exame_dt_exm = models.DateField()
    exame_proc_realizado = models.CharField(max_length=4)
    exame_obs_proc = models.CharField(max_length=999, null=True, blank=True)
    exame_ord_exame = models.PositiveIntegerField(null=True, blank=True)
    exame_ind_result = models.PositiveIntegerField(null=True, blank=True)


class S2220(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtMonit.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtMonit/v_S_01_03_00"
    GROUP = 2
    NAME = "Monitoramento da Saúde do Trabalhador"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    ex_med_ocup_tp_exame_ocup = models.PositiveIntegerField()
    aso_dt_aso = models.DateField()
    aso_res_aso = models.PositiveIntegerField(null=True, blank=True)
    exam = models.ManyToManyField("Exam", related_name="s2220")
    medico_nm_med = models.CharField(max_length=70)
    medico_nr_crm = models.CharField(max_length=8)
    medico_uf_crm = models.CharField(max_length=2)
    resp_monit_cpf_resp = models.CharField(max_length=11, null=True, blank=True)
    resp_monit_nm_resp = models.CharField(max_length=70, null=True, blank=True)
    resp_monit_nr_crm = models.CharField(max_length=8, null=True, blank=True)
    resp_monit_uf_crm = models.CharField(max_length=2, null=True, blank=True)

    def employee(self):
        return Employee.objects.filter(matricula=self.ide_vinculo_matricula)

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    @property
    def instance_outside(self):
        from health.sst.models import MonitorOccupationalHealth

        return MonitorOccupationalHealth.objects.filter(pk=self.oid).last()

    def _search_cache(self):
        return f"{self.employee()}"

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2300', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2300", "s2298"),
                    "query_filter": None,
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class Epi(Event):

    NAME = "Epi"
    INTERNAL = True

    epi_doc_aval = models.CharField(max_length=255)


class ResponsibleS2240(Event):

    NAME = "ResponsibleS2240"
    INTERNAL = True

    resp_reg_cpf_resp = models.CharField(max_length=11)
    resp_reg_ide_oc = models.PositiveIntegerField(null=True, blank=True)
    resp_reg_dsc_oc = models.CharField(max_length=20, null=True, blank=True)
    resp_reg_nr_oc = models.CharField(max_length=14, null=True, blank=True)
    resp_reg_uf_oc = models.CharField(max_length=2, null=True, blank=True)
    obs_obs_compl = models.CharField(max_length=999, null=True, blank=True)


class HarmfulAgent(Event):

    NAME = "Agente Nocivo"
    INTERNAL = True

    ag_noc_cod_ag_noc = models.CharField(max_length=9)
    ag_noc_dsc_ag_noc = models.CharField(max_length=100, null=True, blank=True)
    ag_noc_tp_aval = models.PositiveIntegerField(null=True, blank=True)
    ag_noc_int_conc = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    ag_noc_lim_tol = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True
    )
    ag_noc_un_med = models.PositiveIntegerField(null=True, blank=True)
    ag_noc_tec_medicao = models.CharField(max_length=40, null=True, blank=True)
    ag_noc_nr_proc_jud = models.CharField(max_length=21, null=True, blank=True)

    epc_epi_utiliz_epc = models.PositiveIntegerField(null=True, blank=True)
    epc_epi_efic_epc = models.CharField(max_length=1, null=True, blank=True)
    epc_epi_utiliz_epi = models.PositiveIntegerField(null=True, blank=True)
    epc_epi_efic_epi = models.CharField(max_length=1, null=True, blank=True)

    epi_compl_med_protecao = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_cond_functo = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_uso_inint = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_prz_valid = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_periodic_troca = models.CharField(max_length=1, null=True, blank=True)
    epi_compl_higienizacao = models.CharField(max_length=1, null=True, blank=True)

    epi = models.ManyToManyField("epi", related_name="harmfulagent")


class S2240(Event):
    class Meta:
        app_label = "esocial"

    XML_SCHEMA_NAME = "evtExpRisco.xsd"
    XMLNS = "http://www.esocial.gov.br/schema/evt/evtExpRisco/v_S_01_03_00"
    GROUP = 2
    NAME = "Condições Ambientais do Trabalho - Agentes Nocivos"
    ACTION_PERM = ACTION_RECTIFICATION
    EXCLUSION_TYPE = EXCLUSION_TYPE_S3000

    ide_vinculo_cpf_trab = models.CharField(max_length=11)
    ide_vinculo_matricula = models.CharField(max_length=30, null=True, blank=True)
    ide_vinculo_cod_categ = models.PositiveIntegerField(null=True, blank=True)
    info_exp_risco_dt_ini_condicao = models.DateField()
    info_exp_risco_dt_fim_condicao = models.DateField(null=True, blank=True)
    info_amb_local_amb = models.PositiveIntegerField()
    info_amb_dsc_setor = models.CharField(max_length=100)
    info_amb_tp_insc = models.PositiveIntegerField()
    info_amb_nr_insc = models.CharField(max_length=14)
    info_ativ_dsc_ativ_des = models.CharField(max_length=999)
    ag_noc = models.ManyToManyField("HarmfulAgent", related_name="s2240")
    resp_reg = models.ManyToManyField("ResponsibleS2240", related_name="s2240")

    def employee(self):
        return Employee.objects.filter(matricula=self.ide_vinculo_matricula)

    def employee_cpf(self):
        return self.ide_vinculo_cpf_trab

    @property
    def instance_outside(self):
        from health.sst.models import ExposureEmployeeEnvironment

        return ExposureEmployeeEnvironment.objects.filter(pk=self.oid).last()

    def _search_cache(self):
        return f"{self.employee()}"

    def _base_dependencies(self):
        return {
            f"{('s2200', 's2300', 's2298')}": [
                {
                    "registry_employee": self.registry_employee,
                    "acronyms": ("s2200", "s2300", "s2298"),
                    "query_filter": None,
                    "create_if_not_exist": False,
                    "required": True,
                    "filter_validity_in": True,
                }
            ]
        }


class PayrollPeriod(AuditTimestampModel):
    """Classe de Períodos da Folha do eSocial."""

    class Meta:
        ordering = ("-year", "-month")

    month = models.PositiveIntegerField("Mês")
    year = models.PositiveIntegerField("Ano")
    s1298 = models.ForeignKey(
        "Event",
        on_delete=models.SET_NULL,
        related_name="payrollperiod_s1298",
        null=True,
        blank=True,
    )
    s1299 = models.ForeignKey(
        "Event",
        on_delete=models.SET_NULL,
        related_name="payrollperiod_s1299",
        null=True,
        blank=True,
    )
    sent = models.BooleanField("Enviado", default=False)
    closed = models.BooleanField("Fechado", default=False)
    pendency_cache = models.BooleanField("Pendência", default=False)
    archived = models.BooleanField("Arquivado", default=False)

    def __str__(self):
        month = f"{self.month}"
        return f"{month:0>2}/{self.year}"

    def set_cache(self):
        self.s1298 = (
            S1298.objects.filter(
                competence_month=self.month,
                competence_year=self.year,
                closed_by_event__isnull=True,
            )
            .valids_sent()
            .last()
        )
        if self.s1298:
            self.closed = False

        self.sent = False
        self.s1299 = (
            S1299.objects.filter(
                competence_month=self.month,
                competence_year=self.year,
                closed_by_event__isnull=True,
            )
            .valids_sent()
            .last()
        )
        if self.s1299:
            self.closed = True
            self.sent = True

        self.pendency_cache = False
        if self.pendencies.exists():
            self.pendency_cache = True

        self.archived = False
        if not self.pendency_cache:
            self.archived = True

    def save(self, *args, **kwargs):
        self.set_cache()
        super().save(*args, **kwargs)

    def update_cache(self, save=True):
        """Este método atualiza os campos boleanos.

        Args:
            save (bool, optional): indicativo se save deve ser realizado. Defaults to True.

        """
        self.set_cache()
        if self.diff and save:
            self.save()

    @classmethod
    def update_cache_by_period(cls, month, year):
        """Este método atualiza os campos cache de um período específico.

        Args:
            month (int): mês
            year (int): ano
        """
        for pp in PayrollPeriod.objects.filter(month=month, year=year):
            pp.update_cache()

    @classmethod
    def write_message(
        cls, task=None, msg="", msg_pct=None, pct_progress=None, type_of=1, verbose=True
    ):
        if verbose:
            if task:
                params = {"msg": msg, "type_of": type_of}
                if msg_pct:
                    params.update({"msg_pct": msg_pct})
                if pct_progress:
                    params.update({"pct_progress": pct_progress})
                task.info(**params)
            else:
                print(msg)

    @classmethod
    def update_task_progress(cls, task, progress=0):
        if task:
            Task.objects.filter(uuid=task.uuid).update(progress=progress)
            task.refresh_from_db()

    @classmethod
    def analysis_call_task(cls, period=None):
        from esocial.tasks.generation import analysis_task

        if not task_conflict_with_all():
            return Task.start(analysis_task, period=period, user=get_current_user().pk)

        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def analysis_all_period_call_task(cls, periods=[]):
        from esocial.tasks.generation import analysis_all_period_task

        if not task_conflict_with_all():
            return Task.start(
                analysis_all_period_task, user=get_current_user().pk, periods=periods
            )

        else:
            raise Exception("Existe uma tarefa em execução. Aguarde o término.")

    @classmethod
    def analysis_all_period(cls, task=None, periods=[]):
        from esocial.extractors.s1200 import S1200Extractor
        from esocial.tasks.generation import analysis_period
        from rh.gfp.models import Periodo

        user = get_current_user()
        today = date.today()
        initial_group_date = S1200Extractor.initial_group_date()

        if periods:
            periods = Periodo.objects.filter(pk__in=periods)
        else:
            periods = Periodo.objects.exclude(
                Q(Q(mes__lt=initial_group_date.month) & Q(ano=initial_group_date.year))
                | Q(ano__lt=initial_group_date.year)
            )

            periods = periods.filter(
                Q(Q(ano=today.year) & Q(mes__lte=today.month)) | Q(ano__lte=today.year)
            )

        for period in periods.order_by("-ano", "-mes")[0:12]:
            task.info(msg=f"Iniciando análise de {period}.", type_of=1)
            job = group([analysis_period.s(task.uuid, user.pk, period.pk)])
            # TODO: CONFIGURAÇÃO DE PRIORIDADE result = job.apply_async(queue='low-priority')
            # result = job.apply_async()
            result = job.apply_async(queue="esocial-events")

            start = time.time()

            while not result.ready() and (time.time() - start) < 1800:
                seconds = round(time.time() - start, 2)
                log.info(
                    f">>> WAITING TASK {result} - {period}. Há {seconds} segundos."
                )
                time.sleep(5)
            task.info(msg=f"Finalizando análise de {period}.", type_of=1)

    def analysis_can_close(self, task=None):
        """Este método realiza análise para fechamento da folha.

        Args:
            task (_type_, optional): _description_. Defaults to None."""
        from esocial.extractors.s1200 import ExtractorPayroll

        def info_demonstrative(demonstratives):
            """Este método mostra os demonstrativos(1200, 1202, 1207 e 1210) que estão com problemas."""
            total = demonstratives.count()
            inc_progress = 100.0 / total if total else 0

            PayrollPeriod.update_task_progress(task)

            msg_pct = f"Analisando demonstrativos {demonstratives.model}"

            if total:
                msg = (
                    f"{demonstratives.model.__name__} - Existem {total} com problemas."
                )
                PayrollPeriod.write_message(task=task, msg=msg, type_of=2)

            for dm in demonstratives:
                msg = ""
                if dm.is_invalid_cache or dm.has_exclusion:
                    msg = "(modificado ou excluído)"
                msg = f"{dm} em ({dm.get_process_status_display()}) {msg} aguardando estado válido."
                PayrollPeriod.write_message(
                    task=task,
                    msg=msg,
                    msg_pct=msg_pct,
                    pct_progress=inc_progress,
                    type_of=2,
                )

        def info_entry(entries_not_in_demonstrative_item):
            """Este método mostra os FolhaEvento que não estão em folhas do eSocial."""
            total = entries_not_in_demonstrative_item.count()
            inc_progress = 100.0 / total if total else 0

            PayrollPeriod.update_task_progress(task)

            msg_pct = (
                f"Analisando demonstrativos {entries_not_in_demonstrative_item.model}"
            )

            if total:
                msg = f"{entries_not_in_demonstrative_item.model.__name__} - Existem {total} com problemas."
                PayrollPeriod.write_message(task=task, msg=msg, type_of=2)

            for entry in entries_not_in_demonstrative_item:
                msg = f"{entry} => {entry.contracheque} não está em nenhum demonstrativo válido."
                PayrollPeriod.write_message(
                    task=task,
                    msg=msg,
                    msg_pct=msg_pct,
                    pct_progress=inc_progress,
                    type_of=2,
                )
                self.create_pendency_period(
                    type_pendency=1, event_origin=None, resume=msg, text=msg
                )

        def info_employee_not_found(entries_not_in_demonstrative_item):
            """Este método mostra os servidores que estão em demonstrativos mas não estão em eventos de cadastro."""
            entries_registry_in_registration = Event.objects.filter(
                oid__in=(
                    str(reg)
                    for reg in entries_not_in_demonstrative_item.values_list(
                        "contracheque__servidor__matricula", flat=True
                    )
                ),
                acronym__in=("s2200", "s2300", "s2400", "s2298"),
                is_invalid_cache=False,
                process_status__in=PROCESS_STATUS_EVENT_VALIDS_SENT,
            )

            employees = (
                Employee.objects.filter(
                    matricula__in=(
                        reg
                        for reg in entries_not_in_demonstrative_item.values_list(
                            "contracheque__servidor__matricula", flat=True
                        )
                    )
                )
                .exclude(
                    matricula__in=(
                        int(oid)
                        for oid in entries_registry_in_registration.values_list(
                            "oid", flat=True
                        )
                    )
                )
                .exclude(type_by_possession="COE")
            )

            total = employees.count()
            inc_progress = 100.0 / total if total else 0

            PayrollPeriod.update_task_progress(task)

            msg_pct = "Analisando servidores"

            for employee in employees:
                msg = f"Servidor {employee.type_by_possession} {employee} não foi gerado! Existem pagamentos aguardando."

                PayrollPeriod.write_message(
                    task=task,
                    msg=msg,
                    msg_pct=msg_pct,
                    pct_progress=inc_progress,
                    type_of=2,
                )

                self.create_pendency_period(
                    type_pendency=1, event_origin=None, resume=msg, text=msg
                )

        S1200.update_demonstrative_item(self.month, self.year, task=task)

        entries_not_in_demonstrative_item = (
            ExtractorPayroll.entries_not_in_demonstrative_item(self.month, self.year)
        )
        info_entry(entries_not_in_demonstrative_item)
        info_employee_not_found(entries_not_in_demonstrative_item)

    def summarize(self, task=None):
        """Este método escreve os resulatados de Event.summarize em PendencyPeriod.

        Args:
            task (_type_, optional): _description_. Defaults to None."""

        def _summarize(query):
            total = query.count()
            inc_progress = 100.0 / total if total else 0

            PayrollPeriod.update_task_progress(task)

            msg_pct = "Analisando Sumário de Eventos..."

            for summarize in query:
                total_summarize = (
                    summarize.get("INC") + summarize.get("MOD") + summarize.get("RET")
                )
                total_summarize += summarize.get("EXC") + summarize.get("INV")

                if total_summarize:
                    msg = f'{summarize.get("acronym2")} Inclusões ({summarize.get("INC")}) Modificações ({summarize.get("MOD")})'
                    msg += f' Retificações ({summarize.get("RET")}) Exclusões ({summarize.get("EXC")}) Invál idos ({summarize.get("INV")})'
                    msg += f" TOTAL({total_summarize})"

                    PayrollPeriod.write_message(
                        task=task,
                        msg=msg,
                        msg_pct=msg_pct,
                        pct_progress=inc_progress,
                        type_of=2,
                    )

                    self.create_pendency_period(
                        type_pendency=1, event_origin=None, resume=msg, text=msg
                    )

        """Eventos que serão informados independente do mês folha."""
        acronyms = get_acronyms_from_kind(["EEMP"])
        acronyms += get_acronyms_from_kind(["TI"])
        acronyms += get_acronyms_from_kind(["CF"])
        acronyms += get_acronyms_from_kind(["SST"])
        query = Event.objects.filter(acronym__in=acronyms).summarize()
        _summarize(query)

        """Eventos que serão informados função do mês da folha."""
        acronyms = get_acronyms_from_kind(["FP"])
        query = Event.objects.filter(
            acronym__in=acronyms, competence_month=self.month, competence_year=self.year
        ).summarize()
        _summarize(query)

    def analysis_payroll(self, task=None):
        """Este método realiza análises sobre PayrollPeriod e escreve em PendencyPeriod.

        Args:
            task (_type_, optional): _description_. Defaults to None."""
        from esocial.extractors.s1200 import ExtractorPayroll

        per_apur = ExtractorPayroll._ide_evento_per_apur(self.month, self.year)

        PayrollPeriod.update_task_progress(task)

        messages = []

        if (
            not S1200.objects.by_per_apur(per_apur=per_apur).valids_sent().exists()
            and S1200.objects.by_per_apur(per_apur=per_apur).valids_by_status().exists()
        ):
            messages.append("Aguardando envio de S1200.")
        if (
            not S1202.objects.by_per_apur(per_apur=per_apur).valids_sent().exists()
            and S1202.objects.by_per_apur(per_apur=per_apur).valids_by_status().exists()
        ):
            messages.append("Aguardando envio de S1202.")
        if (
            not S1207.objects.by_per_apur(per_apur=per_apur).valids_sent().exists()
            and S1207.objects.by_per_apur(per_apur=per_apur).valids_by_status().exists()
        ):
            messages.append("Aguardando envio de S1207.")
        if not S1299.objects.by_per_apur(per_apur=per_apur).valids_sent().exists():
            messages.append(f"{self} está aberta!")

        msg_pct = "Analisando Período de Folha do eSocial {payroll_period}..."
        for msg in messages:
            PayrollPeriod.write_message(task=task, msg=msg, msg_pct=msg_pct, type_of=2)
            self.create_pendency_period(
                type_pendency=1, event_origin=None, resume=msg, text=msg
            )

    @classmethod
    def analysis(cls, task=None, period=None):
        """Este método é responsável por construir as PendencyPeriod a partir de algumas fontes:
        - eventos não enviados em demonstrativos;
        - servidores não enviados em demonstrativos;
        - informações da própria folha.

        Args:
            task (_type_, optional): _description_. Defaults to None.
            period (rh.gfp.models.Periodo): período da folha. Deve ser um valor válido.
        """
        from rh.gfp.models import Periodo

        period = Periodo.objects.get(pk=period)

        payroll_period, created = PayrollPeriod.objects.get_or_create(
            month=period.mes, year=period.ano
        )
        payroll_period.pendencies.all().delete()

        """FOLHAS ABERTAS"""
        payroll_period.analysis_payroll(task=task)
        """SUMMARIZE"""
        payroll_period.summarize(task=task)
        """ANALYSIS CAN CLOSE"""
        payroll_period.analysis_can_close(task=task)

        payroll_period.refresh_from_db()
        payroll_period.update_cache()

    def create_pendency_period(
        self, type_pendency=None, event_origin=None, resume=None, text=None
    ):
        pendency_period, created = PendencyPeriod.objects.get_or_create(
            payroll_period=self,
            type_pendency=type_pendency,
            event_origin=event_origin,
            resume=resume[0:256],
            text=text,
        )


class PendencyPeriod(AuditTimestampModel):
    """Classe de Períodos da Folha do eSocial."""

    class Meta:
        ordering = ("created_at",)

    payroll_period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name="pendencies",
        null=True,
        blank=True,
    )
    type_pendency = models.PositiveSmallIntegerField(
        default=1, choices=Choice.get_choices_for("esocial", "TYPE_PENDENCY")
    )  # 1: "ANÁLISE", 2: "SUMMARIZE"
    event_origin = models.ForeignKey(
        "Event",
        on_delete=models.CASCADE,
        related_name="pendencyperiod",
        null=True,
        blank=True,
    )
    resume = models.CharField("Problema", max_length=256)
    text = models.TextField("Texto")

    def __str__(self):
        return f"{self.resume}"
