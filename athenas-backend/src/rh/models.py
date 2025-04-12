# -*- coding: utf-8 -*-

import codecs
import os
from datetime import date, datetime, timedelta
import re
import calendar

from typing import Collection, Optional

from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes import fields as generic
from django.contrib.contenttypes.models import ContentType as ContentTypeDjango
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import SET_NULL, Max, Min, Q, F, Value, IntegerField
from django.db.models.functions import Concat, Cast
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.reverse_related import OneToOneRel
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict
from django.template import loader
from django.template.defaultfilters import slugify

from contrib import documents
from contrib.daterange import NewDateRange
from contrib.decorator import auditable, deprecated, ilru_cache, to_search
from contrib.helpers import clear_to_ascii, get_default_controller_for_model
from contrib.middleware import get_current_user
from contrib.utils import DateUtils, employee_from_user, getLogger, make_phonetic
from engine.notification.models import Message, Notification
from rh import templates
from rh.const import (
    ACOES_TELETRABALHO,
    ACTIVE,
    ADDRESS_CERTIFICATE,
    CANCELED,
    CLASS_ORGAN_OTHER,
    CNH,
    CNH_CATEGORIA,
    CNH_CATEGORY_TYPE,
    CNH_FIRST_DATE,
    CPF,
    CTPS,
    CTPS_SERIE,
    CTPS_UF,
    CUMULATIVE_NOT,
    DIAS_SEMANA,
    DIGITAL_DOCUMENT_TYPE,
    DOCUMENTO_CHOICES,
    ENTRADA_SAIDA,
    ESFERA_GOVERNAMENTAL_CHOICES,
    FINISHED,
    GRAU_INSTRUCAO_CHOICES,
    INDICATIVO,
    INSS,
    IPSEP,
    MAP_FORESIGHT,
    MOTIVO_FIM_DEPENDENCIA,
    MOTIVO_INICIO_DEPENDENCIA,
    NIS,
    NOT_IMMIGRANT,
    PERIODO_FERIAS_CHOICES,
    PIS_PASEP,
    PODER_CHOICES,
    PROFESSIONAL_COUNCIL,
    PROFESSIONAL_COUNCIL_ISSUER,
    REGIME_PREVIDENCIARIO,
    RESERVISTA,
    RESERVISTA_CLASSE,
    RG,
    RG_ISSUER,
    RIC,
    RIC_ISSUER,
    RNE,
    RNE_ISSUER,
    SCHEDULED,
    SEXO_CHOICES,
    STABLE_BONDING,
    STATUS_TELETRABALHO_BLOQUEADO,
    STATUS_TELETRABALHO_CONCLUIDO,
    STATUS_TELETRABALHO_DESBLOQUEADO,
    STATUS_TELETRABALHO_IGNORADO,
    STATUS_TELETRABALHO_PENDENTE,
    STATUS_TELETRABALHO_REVOGADO,
    SUSPENSION,
    TIPO_ANOTACAO_FERIAS,
    TIPO_CARGA_HORARIA,
    TIPO_COMUNICACAO,
    TIPO_EVENTO,
    TIPO_LEI_CARGO,
    TIPO_MOVIMENTACAO_CARREIRA,
    TIPO_NIVEL_ESCOLARIDADE,
    TIPO_ONUS,
    TIPO_PARTICIPACAO_EVENTO,
    TITULO_ELEITOR,
    TITULO_ELEITOR_MUNICIPIO,
    TITULO_ELEITOR_SECAO,
    TITULO_ELEITOR_UF,
    TITULO_ELEITOR_ZONA,
    TRAINEE_LEVEL_FUNDAMENTAL,
    TRAINEE_NATURE_MANDATORY,
    TURNO,
    TYPE_PHONE_EMERGENCY,
    WORK_ASSIGNMENT,
    WORKPLACE,
    TYPE_DEPARTURE_PARCIAL_STUDY,
    TIPO_POSSE,
)
from rh.constants_functional_situations import (
    ACTIVE_SITUATIONS_STR,
    ANYWAY,
    DEPARTURE_SITUATIONS_STR,
    FUNCTIONAL_STATE_INDEX_STR_TO_INT,
    INACTIVE_SITUATIONS_STR,
    INVERT_IF_IN,
    NOT_APPLICABLE_SITUATIONS_STR,
    NOT_VALIDITY,
    SITUACAO_FUNCIONAL,
    SITUATION_APPLICABLE,
    VALIDITY,
)
from rh.exceptions import raise_call
from rh.teletrabalho.notificacoes import (
    enviar_notificacao_alteracao_meta,
    enviar_notificacao_cadastro_plano,
)
from rh.utils import (
    boolean_unicode,
    dump_instance_fields_dict,
    format_situacao_funcional,
    is_active,
    mail_managers,
    notify_employee,
    create_username,
    assign_group_permission,
    assign_func_permission,
    vincular_grupo_permissao_padrao,
    set_employee_user,
    criar_gcpp_aux_creche,
    get_substituicoes,
    notificar_nao_criacao_lotacao,
)
from standard.models import AuditTimestampModel, EmailTemplate, Item
from standard.models import (
    Choice,
    ClassCode,
    CObject,
    ListDatedModel,
    ListDatedModelQuerySet,
    Configuration,
)
from ged.models import Arquivo
from auditlog.registry import auditlog


from rh.utils import enviar_email_notificacao_desligamento_res_vol_est


log = getLogger(__name__)

SIGLAS_LOTACAO = getattr(settings, "SIGLAS_LOTACAO", "")
CACHE_PATH = getattr(settings, "CACHE_PATH", None)


class Mpas(AuditTimestampModel):
    codigo = models.IntegerField(verbose_name="Código")

    def __str__(self):
        return self.codigo


class CountryManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, ddi, *args):
        return self.get(ddi=ddi)


class Pais(CObject):
    ddi = models.CharField(max_length=12, verbose_name="DDI", null=True)
    nome_completo = models.CharField(max_length=100, null=True)
    nacionalidade = models.CharField(max_length=100, null=True, blank=True)
    esocial_code = models.SmallIntegerField(null=True, blank=True)
    objects = CountryManager()

    class Meta:
        ordering = ["nome"]

    def natural_key(self):
        return (self.ddi,)


class Circunscricao(CObject):
    pass


class GrupoComarca(CObject):
    pass


class MesoRegiao(CObject):
    pass


class TipoOrigem(CObject):
    pass


class RacaCor(CObject):
    class Meta:
        ordering = ["nome"]


class GrauInstrucao(CObject):
    """
    Como o Grau de Instrução possui um nome formal para identificá-lo, o label será o nome de apresentação.
    """

    label = models.CharField(max_length=100, null=True)
    ordem = models.IntegerField(null=True)

    def __str__(self):
        return self.label


class Capacidade(CObject):
    pass


class InCapacidade(CObject):
    pass


class BankManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, numero, *args):
        return self.get(numero=numero)


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "numero", "type": "text"},
        {"name": "tem_convenio", "type": "boolean"},
    ]
)
class Banco(CObject):
    pessoajuridica = models.ForeignKey(
        "rh.PessoaJuridica",
        on_delete=models.CASCADE,
        related_name="como_banco",
        null=True,
        blank=True,
    )
    numero = models.CharField(max_length=3, verbose_name="Número", default="")
    sigla = models.CharField(max_length=6, null=True, blank=True)
    principal = models.BooleanField(default=False, verbose_name="Banco Principal")
    objects = BankManager()

    # DEPRECATED
    tem_convenio = models.PositiveIntegerField(
        choices=(
            (0, "NÃO"),
            (1, "SIM"),
            (2, "DOCUMENTO ELETRÔNICO DE CRÉDITO (DOC)"),
        ),
        null=True,
        verbose_name="Tem Convênio?",
    )
    numero_convenio = models.CharField(
        max_length=20, null=True, verbose_name="Número Convênio", blank=True
    )
    agencia = models.CharField(
        max_length=10, null=True, verbose_name="Agência", blank=True
    )
    dv_agencia = models.CharField(
        max_length=2, null=True, verbose_name="DV Agência", blank=True
    )
    conta = models.CharField(max_length=20, null=True, blank=True)
    dv_conta = models.CharField(
        max_length=2, null=True, verbose_name="DV Conta", blank=True
    )
    sequencial_arquivo = models.IntegerField(
        verbose_name="Sequencial", null=False, default=0
    )
    chave_pix = models.CharField("Chave Pix", max_length=255, null=True, blank=True)

    class Meta:
        ordering = ["nome"]

    def natural_key(self):
        return (self.numero,)

    def save(self, force_insert=False, force_update=False):
        if self.tem_convenio == 1 and (
            self.numero_convenio is None or self.agencia is None or self.conta is None
        ):
            raise Exception("As informações do convênio não estão preenchidas!")
        if self.principal == 1:
            if self.tem_convenio != 1:
                raise Exception(
                    "Um banco sem convênio não pode ser marcado como principal!"
                )
        super(Banco, self).save(force_insert, force_update)

    def __str__(self):
        return "%s - %s" % (self.numero, self.nome)

    def _get_conta_completa(self):
        return "%s%s" % (self.conta, self.dv_conta)

    conta_completa = property(_get_conta_completa)

    def get_sequencial(self):
        self.sequencial_arquivo = (
            (self.sequencial_arquivo + 1) if self.sequencial_arquivo < 999999 else 1
        )
        self.save()
        return self.sequencial_arquivo


class Entrancia(CObject):
    """
    Modelo semelhante à entidade ENTRANCIA do Arquimedes.
    """

    class Meta:
        ordering = ["nome"]


class Instancia(CObject):
    """
    Modelo semelhante à entidade INSTANCIA do Arquimedes.
    """

    class Meta:
        ordering = ["nome"]


class CboManager(models.Manager):

    def get_by_natural_key(self, codigo):
        return self.get(codigo=codigo)


class Cbo(AuditTimestampModel):
    # TODO: DIMINUIR TAMANHO PARA 6, EM FUNÇÃO DE NORMATIVA DO GOVERNO FEDERAL PARA O TAMANHO DESTE CAMPO
    codigo = models.CharField(
        max_length=10, verbose_name="Código", default="", blank=False
    )
    descricao = models.CharField(
        max_length=250, verbose_name="Descrição", default="", blank=False
    )
    objects = CboManager()

    def __str__(self):
        return "%s - %s" % (self.codigo, self.descricao)

    def natural_key(self):
        return (self.codigo,)


class EspecialidadeManager(models.Manager):
    def get_queryset(self):
        return (
            super(EspecialidadeManager, self)
            .get_queryset()
            .exclude(nome__icontains="DISPOSIÇÃO")
        )

    def get_by_natural_key(self, sigla):
        return self.get(sigla=sigla)


class Especialidade(CObject):
    objects = EspecialidadeManager()
    sigla = models.CharField(max_length=3, null=True)

    class Meta:
        ordering = ["nome"]

    def natural_key(self):
        return (self.sigla,)


class Patrocinador(CObject):
    pass


class Penalidade(CObject):
    pass


class TempoServicoFinalidade(CObject):
    pass


class NecessidadeEspecial(CObject):
    deficiency_type = models.PositiveSmallIntegerField(
        verbose_name="Tipo de deficiência",
        blank=True,
        null=True,
        choices=Choice.get_choices_for("rh", "DEFICIENCY_TYPE"),
        default=1,
    )

    def __str__(self):
        return self.nome


"""# ----------------- Signals ----------------------------------------------------"""


@receiver(post_save, sender=Banco)
def update_princinpal_bancos(sender, **kargs):
    banco = kargs["instance"]
    # TODO restringir para realizar essa alteração apenas se for uma alteração no campo principal ou um banco novo marcado como principal
    if banco.principal:
        Banco.objects.exclude(pk=banco.pk).update(principal=False)


class SocialSecurity(ListDatedModel, AuditTimestampModel):
    OVERLAP_FIELDS = ["legal_person", "socialsecurity_regime"]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    class Meta:
        ordering = ["-end_validity", "legal_person"]

    legal_person = models.ForeignKey(
        "rh.PessoaJuridica",
        null=True,
        related_name="socialsecurity",
        on_delete=models.CASCADE,
        verbose_name="Previdência",
    )
    identifier = models.PositiveSmallIntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "SOCIALSECURITY_IDENTIFIER"),
        verbose_name="Identificador",
    )
    publication = models.ForeignKey(
        "Publicacao", on_delete=models.CASCADE, null=True, blank=True
    )
    socialsecurity_regime = models.PositiveSmallIntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
        verbose_name="Regime previdenciário",
    )
    percentage_of_employer = models.DecimalField(
        verbose_name="Porcentagem do Patrão", max_digits=5, decimal_places=2, default=0
    )

    class RangeNotFound(Exception):

        def __init__(self):
            Exception.__init__(
                self, "A Previdência %s não possui faixas cadastradas!" % self
            )

    def __str__(self):
        return f'{self.get_socialsecurity_regime_display()} - {self.legal_person} ({self.start_validity.strftime("%d/%m/%Y")} {"..." if not self.end_validity else " - %s" % self.end_validity})'

    @property
    def ranges(self):
        if not self.ranges.all():
            raise self.RangeNotFound()
        return self.ranges.all()


class SocialSecurityRange(AuditTimestampModel):
    class Meta:
        ordering = ["socialsecurity", "lower_limite"]

    socialsecurity = models.ForeignKey(
        SocialSecurity,
        verbose_name="Previdência",
        related_name="ranges",
        on_delete=models.CASCADE,
    )
    lower_limite = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Inferior"
    )
    upper_limite = models.DecimalField(
        max_digits=16, decimal_places=2, verbose_name="Limite Superior"
    )
    percentage = models.DecimalField(
        verbose_name="Porcentagem do Empregado", max_digits=5, decimal_places=2
    )
    # pct_patronal = models.DecimalField(verbose_name="Porcentagem do Patrão", max_digits=5, decimal_places=2, blank=True)
    reducer = models.DecimalField(
        verbose_name="Redutor", max_digits=16, decimal_places=4, blank=True, default=0
    )

    def __str__(self):
        return f"[{self.lower_limite} - {self.upper_limite}] {self.socialsecurity}"


class SocialSecurityEmployeeQuerySet(ListDatedModelQuerySet):

    def by_regime(self, regime):
        return self.filter(social_security_config__regime=regime)

    def by_organ(self, organ):
        return self.filter(social_security_config__organ=organ)


class SocialSecurityEmployee(ListDatedModel, AuditTimestampModel):
    AUTO_CLOSE_PERIOD_OVERLAP = True
    OVERLAP_FIELDS = ["employee", "social_security_config"]

    employee = models.ForeignKey(
        "Servidor", related_name="socialsecurities", on_delete=models.CASCADE
    )
    social_security_config = models.ForeignKey(
        "SocialSecurityConfig", on_delete=models.CASCADE
    )
    # TODO: Quando for o caso de previdência complementar:
    # TODO: extra_percent = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, default=0)

    mass_segregation_plan = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("rh", "MASS_SEGREGATION_PLAN"),
        null=True,
        blank=True,
    )
    ignore_others_ssc = models.BooleanField(
        "Ignorar Outras Configs. Previdenciárias", default=False
    )
    participante_migrado = models.BooleanField("Participante migrado?", default=False)

    objects = SocialSecurityEmployeeQuerySet.as_manager()

    def __str__(self):
        return "%s (%s) : %s - %s" % (
            self.employee,
            self.social_security_config,
            self.start_validity,
            self.end_validity,
        )

    def get_mass_segregation_plan(self):

        ssc = SocialSecurityConfig.objects.filter(
            organ__cnpj=15401381000198,  # SP-PREVICOM
            regime="2",  # RPPS
        ).first()
        if self.social_security_config == ssc:
            return

        types_actives = [
            "MBR",
            "MBR2",
            "MEL",
            "MCM",
            "MEC",
            "MEL2",
            "MCM2",
            "MEC2",
            "EFE",
            "ECM",
            "EFC",
        ]
        types_inactives = ["BFP", "MAP", "SAP", "MAP2", "APO"]

        actives_and_date = (
            self.employee.type_by_possession in types_actives
            and self.start_validity <= datetime(2013, 12, 31).date()
        )

        inactives_and_date = (
            self.employee.type_by_possession in types_inactives
            and self.start_validity <= datetime(2017, 12, 31).date()
        )

        if self.employee.type_by_possession not in types_actives + types_inactives:
            self.mass_segregation_plan = None
        elif actives_and_date or inactives_and_date:
            self.mass_segregation_plan = 2  # Plano Financeiro
        else:
            self.mass_segregation_plan = 1  # Plano Previdenciário

    @classmethod
    def finish_social_security_for_employee(cls, employee, data_desligamento):
        """
        Função que promove o preenchimento do campo de end_validity de SocialSecurityEmployee se houver
        data de desligamento.
        :params: employee (Servidor)
        :params: data_desligamento (Date)
        :returns: (bool)
        """

        if data_desligamento:
            SocialSecurityEmployee.objects.filter(
                employee__matricula=employee.matricula
            ).update(end_validity=data_desligamento)
            return True
        return False

    def validate_social_security_regime(self):
        request_move = (
            RequestMove.objects.filter(servidor=self.employee)
            .assets_in(range=NewDateRange(self.start_validity, self.end_validity))
            .last()
        )
        if (
            request_move
            and MAP_FORESIGHT.get(self.social_security_config.regime)
            != request_move.regime_contract
        ):
            message = f"O Regime de contrato da requisição ({request_move.get_regime_contract_display()}) "
            message += "é diferente do cadastrado em Configurações previdenciárias."
            raise Exception(message)

    def validate(self):
        return self.validate_social_security_regime()

    def save(self, *args, **kargs):
        ssc = SocialSecurityConfig.objects.filter(
            organ__cnpj=15401381000198,  # SP-PREVICOM
            regime="2",  # RPPS
        ).first()
        if self.social_security_config == ssc:
            related_ssc = (
                SocialSecurityEmployee.objects.filter(employee=self.employee)
                .exclude(social_security_config=ssc)
                .order_by("id")
                .first()
            )
            if not related_ssc:
                msg = "SP-PREVICOM só pode ser cadastrado se já houver um registro de previdência existente."
                raise Exception(msg)
            elif related_ssc.social_security_config.regime != 2:  # RPPS = 2
                msg = "SP-PREVICOM só pode ser associado ao regime previdenciário RPPS."
                raise Exception(msg)
            else:
                self.mass_segregation_plan = related_ssc.mass_segregation_plan
        if self.employee.type_by_possession != "COE":
            self.validate()
            self.get_mass_segregation_plan()
        super(SocialSecurityEmployee, self).save(*args, **kargs)


class SocialSecurityConfigQuerySet(ListDatedModelQuerySet):

    def by_organ(self, organ):
        if not isinstance(organ, list):
            organ = [organ]
        return self.filter(organ__in=organ)


class SocialSecurityConfig(ListDatedModel):
    OVERLAP_FIELDS = ["organ", "regime", "mass_segregation_plan"]

    organ = models.ForeignKey("rh.PessoaJuridica", on_delete=models.CASCADE)
    regime = models.PositiveSmallIntegerField(
        "Regime previdenciário",
        default=2,
        choices=Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO"),
    )
    mass_segregation_plan = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("rh", "MASS_SEGREGATION_PLAN"),
        null=True,
        blank=True,
    )

    objects = SocialSecurityConfigQuerySet.as_manager()

    def __str__(self):
        return "{0}, {1} - {2}".format(
            self.get_regime_display(),
            self.get_mass_segregation_plan_display(),
            self.organ,
        )


class RHObject(AuditTimestampModel):
    servidor = models.ForeignKey(
        "rh.Servidor", on_delete=models.PROTECT, verbose_name="Servidor", blank=True
    )
    anotacao_geral = models.ForeignKey(
        "rh.AnotacaoGeral",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Anotação Geral",
    )
    texto = models.TextField(null=True, blank=True)
    anota = models.BooleanField(default=True, verbose_name="Gera Anotação")

    class Meta:
        abstract = True

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.validate()
        try:
            if self.anota:
                self.anotacao(*args, **kwargs)
            super(RHObject, self).save(*args, **kwargs)
        except Exception as err:
            log.exception(err)

    @transaction.atomic
    def delete(self, *args, **kargs):
        try:
            try:
                if self.anotacao_geral:
                    self.anotacao_geral.delete()
            except Exception:
                log.debug("Anotação Geral não encontrada!")
            super(RHObject, self).delete(*args, **kargs)
        except Exception as err:
            log.exception(err)
            raise err

    def validate(self):
        pass

    def anotacao(self, *args, **kargs):
        """
        Este método é o responsável por realizar a anotação.
        """
        return True

    def get_texto(self):
        """
        Este método é responsável por gerar o texto para anotação.
        """
        return ""


class PersonManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, nome, created_at, *args):
        return self.get(nome=nome, created_at=created_at)


@to_search(
    [
        {"name": "nome", "type": "text"},
    ]
)
class Pessoa(AuditTimestampModel):
    """
    Classe abstrata para identificar qualquer Pessoa, seja ela física ou jurídica no âmbito do relacionamento com o MP-TO.
    """

    nome = models.CharField(
        max_length=100, verbose_name="Nome", default="", blank=False
    )
    name_cache = models.CharField(
        max_length=100, verbose_name="Nome", default="", blank=True
    )
    phonetic_name = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=100, verbose_name="Slug", default="", blank=True)
    email = models.EmailField(null=True, blank=True)
    dado_bancario = models.ManyToManyField(
        "DadoBancario",
        verbose_name="Dado Bancário",
        related_name="dados_bancarios_pessoas",
        blank=True,
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    enable_protocol = models.BooleanField(
        default=True, verbose_name="Habilitar protocolo"
    )
    kind = models.CharField(max_length=32, verbose_name="Tipo", blank=True)
    rate_fill = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )
    objects = PersonManager()

    class Meta:
        verbose_name = "Pessoa"
        ordering = ("nome",)

    @classmethod
    def match_weight(cls):
        return {"phonetic_name": 3.0}

    @classmethod
    def weight_max_score(cls):
        if not hasattr(cls, "_cache_weight_max_score"):
            cls._cache_weight_max_score = sum(cls.match_weight().values())

        return cls._cache_weight_max_score

    def match_score_from_target(self, target):
        total = 0.0
        weight = self.match_weight()

        for attr, score in weight.items():
            total += (
                score
                if getattr(self, attr, None) == getattr(target, attr, None)
                else 0.00
            )

        return total / self.weight_max_score()

    def index_repeated(self):
        query = self.__class__.objects.exclude(pk=self.pk).filter(
            phonetic_name=self.phonetic_name
        )

        if query.exists():
            for target in query:
                subquery = RepeatPersonIncident.objects.filter(
                    Q(current_state=1)
                    & Q(Q(main_person=target) | Q(target_person=target))
                )

                if not subquery.exists():
                    ratio = self.match_score_from_target(target)
                    if ratio > 0.0000:
                        RepeatPersonIncident.objects.create(
                            main_person=self, target_person=target, ratio=ratio
                        )

    def natural_key(self):
        return (self.nome, self.created_at)

    def __str__(self):
        return "%s" % self.nome

    def _set_kind(self):
        self.kind = self.specialized_instance._meta.model_name
        if (
            self.specialized_instance._meta.model_name
            == "naturalpersonspecializedemployee"
        ):
            self.kind = "pessoafisica"
        elif self.specialized_instance._meta.model_name in (
            "educationalinstitution",
            "institution",
        ):
            self.kind = "pessoajuridica"
        return self.kind

    def validate_perm_person(self):
        """
        Esse método deve ser sobrescrito, caso seja necessário validar situações onde são necessárias permissões sobre o objeto.
        """
        return True

    @property
    def specialized_instance(self):
        inst = self
        if hasattr(inst, "pessoafisica"):
            inst = inst.pessoafisica
        elif hasattr(inst, "pessoajuridica"):
            inst = inst.pessoajuridica
            if hasattr(inst, "educationalinstitution"):
                inst = inst.educationalinstitution
            elif hasattr(inst, "institution"):
                inst = inst.institution
        elif hasattr(inst, "anonymousperson"):
            inst = inst.anonymousperson
        return inst

    def validate(self):
        self.validate_perm_person()
        return True

    def save(self, *args, **kargs):
        self.slug = slugify(self.nome)
        self.name_cache = clear_to_ascii(self.nome)
        self._set_kind()

        self.phonetic_name = make_phonetic(self.nome)

        self.validate()
        super(Pessoa, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        self.specialized_instance.validate_perm_person()
        super(Pessoa, self).delete(*args, **kargs)

    def is_servidor(self):
        """
        Este método verifica se a Pessoa é um servidor.
        @return True, False.
        """

        return hasattr(self, "pessoafisica") and self.pessoafisica.servidor_set.exists()

    @property
    def dependent(self):
        """
        Este método verifica se a Pessoa é um dependente.
        @return True, False.
        """
        return (
            hasattr(self, "pessoafisica")
            and self.pessoafisica.dependentes_pessoa.exists()
        )

    @property
    def abbreviation(self):
        names = self.nome.split()
        if len(names) > 2:
            abreviates = [
                names[0],
            ]
            for nm in names[1:-1]:
                abrev = nm
                if len(nm) > 3:
                    abrev = "%s." % abrev[0]
                abreviates.append(abrev)
            abreviates.append(names[-1])
            return " ".join(abreviates)
        else:
            return self.nome

    @property
    def verbose_kind(self):
        kind_person_map = {
            "pessoa": "Pessoa",
            "pessoafisica": "Pessoa Física",
            "naturalperson_employee": "Servidor - Pessoa Física",
            "pessoajuridica": "Pessoa Jurídica",
            "anonymousperson": "Pessoa Anônima",
            "lawyer": "Advogado",
        }
        kind = self.kind
        if (
            self.kind == "pessoafisica"
            and hasattr(self, "servidor_set")
            and self.servidor_set.filter(ativo=True).exists()
        ):
            kind = "naturalperson_employee"
        return kind_person_map.get(kind)

    @property
    def can_merge(self):
        return False

    def telefone_pessoal(self):
        telefones = self.phone.filter(tipo_telefone__in=[1, 3])
        if telefones.exists():
            return telefones.first().numero
        return ""

    @property
    def telefone_institucional(self):
        return self.phone.filter(tipo_telefone=5).values_list("numero", flat=True)


class AnonymousPerson(Pessoa):
    pass


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "cpf", "type": "text"},
        {"name": "rg", "type": "text"},
        {"name": "municipio_naturalidade__nome", "type": "text"},
        {"name": "data_nascimento", "type": "date"},
        {"name": "rg_orgao", "type": "text"},
        {"name": "nome_pai", "type": "text"},
        {"name": "nome_mae", "type": "text"},
        {"name": "nome_conjuge", "type": "text"},
    ]
)
class PessoaFisica(Pessoa):
    """ """

    social_name = models.CharField(
        max_length=100, verbose_name="Nome Social", blank=True, null=True
    )
    cpf = models.CharField(max_length=14, null=True, blank=True, verbose_name="CPF")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, null=True, blank=True)
    sexual_orientation = models.PositiveSmallIntegerField(
        verbose_name="Orientação Sexual",
        choices=Choice.get_choices_for("rh", "SEXUAL_ORIENTATION"),
        default=5,
    )
    sangue = models.IntegerField(
        choices=Choice.get_choices_for("rh", "BLOOD"), blank=True, default=5
    )
    documento = models.ManyToManyField(
        "Documento", blank=True, related_name="naturalpersons"
    )
    estado_civil = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "MARITAL_STATUS"),
    )
    municipio_naturalidade = models.ForeignKey(
        "Localidade", null=True, blank=True, on_delete=models.CASCADE
    )
    raca_cor = models.IntegerField(
        default=5,
        choices=Choice.get_choices_for("rh", "TYPE_RACE"),
        verbose_name="Raça/Cor",
    )
    email_institucional = models.EmailField(null=True, blank=True)
    email_pessoal = models.EmailField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    data_obito = models.DateField(null=True, blank=True, verbose_name="Data Óbito")
    rg = models.CharField(max_length=20, null=True, blank=True, verbose_name="RG")
    rg_orgao = models.CharField(
        max_length=10, null=True, blank=True, verbose_name="RG Órgão"
    )
    rg_data_expedicao = models.DateField(
        null=True, blank=True, verbose_name="RG Data Expedição"
    )
    rg_uf = models.ForeignKey(
        "Estado", null=True, blank=True, verbose_name="RG UF", on_delete=models.CASCADE
    )
    fator_rh = models.IntegerField(
        default=3,
        choices=Choice.get_choices_for("rh", "FACTOR_RH"),
        null=True,
        blank=True,
        verbose_name="Fator RH",
    )
    doador = models.BooleanField(
        default=True, blank=True, verbose_name="Doador de órgãos"
    )
    nome_pai = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Pai"
    )
    phonetic_father_name = models.CharField(max_length=80, null=True, blank=True)
    nome_mae = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Mãe"
    )
    phonetic_mother_name = models.CharField(max_length=80, null=True, blank=True)
    nome_conjuge = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nome Cônjuge"
    )
    foto = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.CASCADE
    )
    necessidade_especial = models.BooleanField(
        default=False, blank=True, verbose_name="Necessidade Especial"
    )
    necessidades_especiais = models.ManyToManyField(
        "NecessidadeEspecial", related_name="pessoafisica", blank=True
    )
    grau_instrucao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEGREE_EDUCATION"),
        verbose_name="Grau de Instrução",
        default=8,
    )
    nacionalidade = models.CharField(
        max_length=80, null=True, blank=True, verbose_name="Nacionalidade"
    )
    nationality = models.ForeignKey(
        Pais,
        verbose_name="Nacionalidade",
        on_delete=models.PROTECT,
        related_name="naturalperson_nationality",
        default=1,
        blank=True,
    )
    nationality_birth = models.ForeignKey(
        Pais,
        verbose_name="País de nascimento",
        on_delete=models.PROTECT,
        related_name="naturalperson_nationality_birth",
        default=1,
        blank=True,
    )
    genero = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Gênero"
    )
    profissao = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Profissão"
    )
    renda_familiar = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        verbose_name="Renda Familiar",
        blank=True,
        null=True,
    )
    social_program = models.ManyToManyField(
        "SocialProgram",
        related_name="in_pesssoafisica",
        blank=True,
        verbose_name="Programas Sociais",
    )
    has_serious_diseases = models.BooleanField(
        default=False, blank=True, verbose_name="Doença Grave"
    )
    serious_diseases = models.ManyToManyField(
        "SeriousDiseases",
        related_name="in_pessoafisica",
        verbose_name="Doenças Graves",
        blank=True,
    )
    retired = models.BooleanField("Aposentado", default=False)
    immigrant_residence_time = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_RESIDENCE_TIME"),
        verbose_name="Tempo de residência do imigrante",
        default=NOT_IMMIGRANT,
    )
    immigrant_entry_condition = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_ENTRY_CONDITION"),
        verbose_name="Condição de ingresso do imigrante",
        default=NOT_IMMIGRANT,
    )
    is_lawyer = models.BooleanField(default=False, blank=True, verbose_name="Advogado")
    oab = models.CharField(max_length=20, null=True, blank=True, verbose_name="OAB")
    email_pessoal_verificado = models.BooleanField(
        verbose_name="E-mail secundário verificado?",
        default=False,
        blank=True,
        null=True,
    )
    codigo_email = models.CharField(
        max_length=6,
        verbose_name="Código de verificação do e-mail",
        blank=True,
        null=True,
    )
    data_codigo_email = models.DateTimeField(
        verbose_name="Data código email", blank=True, null=True
    )
    data_alteracao_esocial = models.DateField(
        null=True, blank=True, verbose_name="Data de alteração esocial"
    )

    fields_rate_fill_weight = {
        "cpf": 50,
        "data_nascimento": 12.5,
        "nome_mae": 25,
        "nome_pai": 12.5,
    }

    class Meta:
        verbose_name = "Pessoa Física"
        ordering = ("nome", "cpf")
        permissions = (
            ("can_manage_person_employee", "Permissão para gerenciar Servidor"),
            ("can_merge_naturalperson", "Permissão para mesclar Pessoa Física"),
        )

    @classmethod
    def match_weight(cls):
        if not hasattr(cls, "__cache_match_weight"):
            cls.__cache_match_weight = super().match_weight()
            cls.__cache_match_weight.update(
                {"phonetic_mother_name": 2.0, "phonetic_father_name": 1.0}
            )

        return cls.__cache_match_weight

    def __str__(self):
        return self.nome

    def validate(self):
        self.validate_mandatory_blood_factor()
        self.validate_mandatory_blood()
        self.validate_mandatory_sex()
        self.validate_mandatory_race()
        self.validate_mandatory_degree_education()
        self.validate_mandatory_date_born()
        self.validate_mandatory_municipality_naturalness()
        self.validate_mandatory_cpf()
        self.validate_mandatory_nis_pisep()
        self.validate_mandatory_rg()
        self.validate_documents()
        self.validate_mandatory_sex_information_for_dependent()
        self.validar_email_pessoal()
        self.validar_alteracao_email_pessoal()
        return super(PessoaFisica, self).validate()

    def validar_alteracao_email_pessoal(self):
        if self.pk:
            pf = PessoaFisica.objects.get(pk=self.pk)
            if (
                pf.email_pessoal
                and pf.email_pessoal.lower() != self.email_pessoal.lower()
            ):
                self.email_pessoal_verificado = False

    def validar_email_pessoal(self):
        if self.email_pessoal and "mpmt" in self.email_pessoal:
            raise Exception("Não é permitido inserir e-mail pessoal com domínio: @mpmt")

    def validate_mandatory_sex_information_for_dependent(self):
        if self.pk:
            if self.dependentes_pessoa.exists() and not self.sexo:
                raise Exception(
                    "Obrigatório informar o sexo em cadastro de dependente."
                )
        return True

    def validate_mandatory_blood_factor(self):
        if not self.fator_rh:
            raise Exception("Preencha FATOR RH.")
        return True

    def validate_mandatory_blood(self):
        if not self.sangue:
            raise Exception("Preencha SANGUE.")
        return True

    def validate_documents(self):
        self.validate_mandatory_ctps()
        # self.validate_mandatory_rg_document()
        self.validate_mandatory_ric()
        self.validate_mandatory_rne()
        self.validate_mandatory_professional_council()
        self.validate_mandatory_cnh()
        return True

    def allow_perm_own_person(self):
        user = get_current_user()
        if user:
            employee = employee_from_user(user)
            return (
                employee
                and self.servidor_set.filter(pk=employee.pk, ativo=True).exists()
            )
        return False

    def validate_perm_person(self):
        if self.is_servidor() or self.dependent:
            user = get_current_user()
            has_perms = user and (
                user.has_perm("rh.can_manage_person_employee")
                or user.has_perm("rh.add_servidor")
                or user.has_perm("rh.change_servidor")
            )
            if not has_perms and not (
                "doador" in self.diff and self.allow_perm_own_person()
            ):
                raise Exception(
                    "Você não tem permissão para modificar a Pessoa Física do Servidor."
                )
        return True

    def validate_mandatory_nis_pisep(self):
        if (
            self.is_servidor()
            and self.employee.type_by_possession == "CMS"
            and not self.collaborator
            and not self.pis_pasep
        ):
            raise Exception("Preencha PIS/PASEP.")
        return True

    def validate_mandatory_sex(self):
        if (
            self.is_servidor()
            and not self.sexo
            and self.employee.type_by_possession != "COE"
        ):
            raise Exception("Preencha o campo Sexo.")
        return True

    def validate_mandatory_race(self):
        if self.is_servidor() and not self.raca_cor:
            raise Exception("Preencha o campo Raça.")
        return True

    def validate_mandatory_degree_education(self):
        if self.is_servidor() and not self.estado_civil:
            raise Exception("Preencha o campo Grau de Instrução.")
        return True

    def validate_mandatory_date_born(self):
        if self.is_servidor() and not self.data_nascimento:
            raise Exception("Preencha o campo Data de Nascimento.")
        return True

    def validate_mandatory_municipality_naturalness(self):
        if (
            self.is_servidor()
            and not self.municipio_naturalidade
            and self.employee.type_by_possession != "COE"
        ):
            raise Exception("Preencha o campo Município de Naturalidade.")
        return True

    def validate_mandatory_cpf(self):
        if (self.is_servidor() or self.pensioner) and not self.cpf:
            raise Exception("Preencha o campo CPF.")

        return True

    # Colaborador Eventual - COE
    def validate_coe_employee(self):
        self.validate_mandatory_cpf()
        self.validate_mandatory_birth_date()

    def validate_mandatory_cpf(self):
        if not self.cpf:
            # raise Exception('Preencha o campo CPF.')
            log.error("Preencha o campo CPF.")
        return True

    def validate_mandatory_birth_date(self):
        if not self.data_nascimento:
            # raise Exception('Preencha a Data de Nascimento.')
            log.error("Preencha a Data de Nascimento.")
        return True

    def validate_mandatory_ctps(self):
        self.ctps and self.ctps.validate_mandatory_ctps()
        return True

    def validate_mandatory_rg_document(self):
        self.rg_document and self.rg_document.validate_mandatory_rg()
        return True

    def validate_mandatory_ric(self):
        self.ric and self.ric.validate_mandatory_ric()
        return True

    def validate_mandatory_rg(self):
        rg = self.rg
        if self.is_servidor() and self.employee.type_by_possession != "COE":
            if not rg:
                raise Exception("Preencha o campo RG - Número.")
            if not self.rg_orgao:
                raise Exception("Preencha o campo RG - Órgão Emissor.")
            if not self.rg_uf:
                raise Exception("Preencha o campo RG - UF")
            if not self.rg_data_expedicao:
                raise Exception("Preencha o campo RG - Data Expedição")
        return True

    def validate_mandatory_rne(self):
        self.rne and self.rne.validate_mandatory_rne()
        return True

    def validate_mandatory_professional_council(self):
        self.professional_council and self.professional_council.validate_mandatory_professional_council()
        return True

    def validate_mandatory_cnh(self):
        self.cnh and self.cnh.validate_mandatory_cnh()
        return True

    @classmethod
    def cpf_format(cls, cpf):
        if cpf:
            cpf = cpf.replace(".", "").replace("-", "")
        return cpf

    @classmethod
    def name_format(cls, name_origin):
        name_r = name_origin.strip().replace("  ", " ")
        while name_r != name_origin:
            name_origin = name_r
            name_r = name_origin.strip().replace("  ", " ")
        return name_r

    def save(self, *args, **kargs):
        self.nome = PessoaFisica.name_format(self.nome)
        if self.cpf:
            self.cpf = documents.CPF(self.cpf).clear

        query = PessoaFisica.objects.filter(cpf=self.cpf).exclude(
            Q(cpf="") | Q(cpf=None)
        )
        msg = "Esse CPF já está cadastrado para outra(s) Pessoa(s) Física(s)."

        if self.pk:
            if query.exists() and not query.filter(pk=self.pk).exists():
                raise Exception(msg)
        elif query.exists():
            raise Exception(msg)

        if not self.nationality_id:
            setattr(self, "nationality", Pais.objects.get(pk=1))
        if not self.nationality_birth_id:
            setattr(self, "nationality_birth", Pais.objects.get(pk=1))

        self.phonetic_father_name = (
            None if not self.nome_pai else make_phonetic(self.nome_pai)
        )
        self.phonetic_mother = (
            None if not self.nome_pai else make_phonetic(self.nome_mae)
        )
        self.rate_fill = self._calculate_rate_fill()
        self._registrar_alteracao_esocial()

        super(PessoaFisica, self).save(*args, **kargs)
        self.update_document_rg_cpf()

    def _sum_values_weight_rate_fill(self):
        return sum(self.fields_rate_fill_weight.values())

    def _registrar_alteracao_esocial(self):
        from datetime import datetime

        if self.pk:
            old_registro = PessoaFisica.objects.get(pk=self.pk)
            campos = [
                "cpf",
                "nome",
                "sexo",
                "raca_cor",
                "estado_civil",
                "grau_instrucao",
                "social_name",
                "municipio_naturalidade",
                "data_nascimento",
            ]
            for campo in campos:
                valor = getattr(old_registro, campo)
                novo_valor = getattr(self, campo)
                if valor != novo_valor:
                    self.data_alteracao_esocial = datetime.today()
                    break

    def _calculate_rate_fill(self):
        rate = 0

        for attr, value in self.fields_rate_fill_weight.items():
            if attr in self.__dict__.keys() and self.__dict__.get(attr):
                rate += self.fields_rate_fill_weight.get(attr)

            for related in self._meta.related_objects:
                if attr == related.get_accessor_name():
                    if related.related_model.objects.filter(
                        **{related.field.name: self.pk}
                    ).exists():
                        rate += self.fields_rate_fill_weight.get(attr)

        return rate / self._sum_values_weight_rate_fill()

    def update_document_rg_cpf(self):
        cpf_document = self.cpf_document
        rg_document = self.rg_document
        try:
            if self.cpf:
                if not cpf_document:
                    cpf_document = Documento(
                        numero=self.cpf, tipo_documento=CPF, natural_person=self
                    )
                    cpf_document.save()
                    self.documento.add(cpf_document)
                elif cpf_document.numero != self.cpf:
                    cpf_document.numero = self.cpf
                    cpf_document.save()
        except Exception as err:
            log.exception(err)
        try:
            if self.rg and self.rg_uf:
                if not rg_document:
                    rg_document = Documento(
                        numero=self.rg,
                        tipo_documento=RG,
                        data_expedicao=self.rg_data_expedicao,
                        estado_expedicao=self.rg_uf,
                        natural_person=self,
                    )
                    rg_document.save()
                    self.documento.add(rg_document)
                elif (
                    rg_document.numero != self.rg
                    or rg_document.data_expedicao != self.rg_data_expedicao
                    or rg_document.estado_expedicao != self.rg_uf
                ):
                    rg_document.numero = self.rg
                    rg_document.data_expedicao = self.rg_data_expedicao
                    rg_document.estado_expedicao = self.rg_uf
                    rg_document.save()
                rg_issuer = rg_document.rg_issuer
                if not rg_issuer:
                    rg_issuer = DocsDadosEspecificos(
                        especificidade=RG_ISSUER, valor=self.rg_orgao
                    )
                    rg_issuer.save()
                    rg_document.dados_especificos.add(rg_issuer)
                elif rg_issuer.valor != self.rg_orgao:
                    rg_issuer.valor = self.rg_orgao
                    rg_issuer.save()
        except Exception as err:
            log.exception(err)

    def save_sem_cpf(self, *args, **kargs):
        super(PessoaFisica, self).save(*args, **kargs)

    @property
    def employee(self):
        """
        Este método retorna o servidor ativo.
        """
        employee = None
        if self.pk:
            employee = self.servidor_set.filter(ativo=True).last()
            if not employee:
                employee = self.servidor_set.last()
        return employee

    def is_servidor(self):
        """
        Este método verifica se a Pessoa é um servidor.
        @return True, False.
        """
        if self.pk:
            return self.servidor_set.exists()
        return False

    @property
    def age(self):
        """
        Este método retorna a idade da pessoa.
        """
        now = datetime.now().date()
        diff = now - self.data_nascimento
        return diff.days / 365

    @property
    def collaborator(self):
        """
        Este método verifica se a Pessoa é um servidor.
        @return True, False.
        """
        return self.servidor_set.filter(tipo__in=["T", "V", "E", "A"]).exists()

    @property
    def voter(self):
        """
        Este método retorna o Documento: título de eleitor.
        """
        voter = Documento.objects.none()
        if self.pk:
            voter = self.documento.filter(tipo_documento=TITULO_ELEITOR)
        if voter.exists():
            voter = voter.first()
        else:
            voter = None
        return voter

    @property
    def pis_pasep(self):
        """
        Este método retorna o Documento: pis_pasep.
        """
        pis_pasep = Documento.objects.none()
        if self.pk:
            pis_pasep = self.documento.filter(tipo_documento=PIS_PASEP)
        if pis_pasep.exists():
            pis_pasep = pis_pasep.first()
        else:
            pis_pasep = None
        return pis_pasep

    @property
    def nis(self):
        """
        Este método retorna o Documento: nis.
        """
        nis = Documento.objects.none()
        if self.pk:
            nis = self.documento.filter(tipo_documento=NIS)
        if nis.exists():
            nis = nis.first()
        else:
            nis = None
        return nis

    @property
    def ctps(self):
        ctps = Documento.objects.none()
        if self.pk:
            ctps = self.documento.filter(tipo_documento=CTPS)
        if ctps.exists():
            ctps = ctps.first()
        else:
            ctps = None
        return ctps

    @property
    def ric(self):
        ric = Documento.objects.none()
        if self.pk:
            ric = self.documento.filter(tipo_documento=RIC)
        if ric.exists():
            ric = ric.first()
        else:
            ric = None
        return ric

    @property
    def cnh(self):
        cnh = Documento.objects.none()
        if self.pk:
            cnh = self.documento.filter(tipo_documento=CNH)
        if cnh.exists():
            cnh = cnh.first()
        else:
            cnh = None
        return cnh

    @property
    def rne(self):
        rne = Documento.objects.none()
        if self.pk:
            rne = self.documento.filter(tipo_documento=RNE)
        if rne.exists():
            rne = rne.first()
        else:
            rne = None
        return rne

    @property
    def cpf_document(self):
        cpf_document = Documento.objects.none()
        if self.pk:
            cpf_document = self.documento.filter(tipo_documento=CPF)
        if cpf_document.exists():
            cpf_document = cpf_document.first()
        else:
            cpf_document = None
        return cpf_document

    @property
    def rg_document(self):
        rg_document = Documento.objects.none()
        if self.pk:
            rg_document = self.documento.filter(tipo_documento=RG)
        if rg_document.exists():
            rg_document = rg_document.first()
        else:
            rg_document = None
        return rg_document

    @property
    def reservist(self):
        reservist = Documento.objects.none()
        if self.pk:
            reservist = self.documento.filter(tipo_documento=RESERVISTA)
        if reservist.exists():
            reservist = reservist.first()
        else:
            reservist = None
        return reservist

    @property
    def professional_council(self):
        professional_council = Documento.objects.none()
        if self.pk:
            professional_council = self.documento.filter(
                tipo_documento=PROFESSIONAL_COUNCIL
            )
        if professional_council.exists():
            professional_council = professional_council.first()
        else:
            professional_council = None
        return professional_council

    @property
    def uniao_estavel(self):
        uniao_estavel = Documento.objects.none()
        if self.pk:
            uniao_estavel = self.documento.filter(tipo_documento=STABLE_BONDING)
        if uniao_estavel.exists():
            uniao_estavel = uniao_estavel.first()
        else:
            uniao_estavel = None
        return uniao_estavel

    def get_idade_em(self, data=None):
        data = datetime.today().date() if not data else data
        return relativedelta(data, self.data_nascimento).years

    @property
    def idade(self):
        return self.get_idade_em()

    @property
    def pensioner(self):
        """
        Este método verifica se a Pessoa é um pensionista.
        @return True, False.
        """
        return (
            hasattr(self, "pessoafisica")
            and self.pessoafisica.pensao_pensionista.exists()
        )

    """SINAIS"""

    def atualiza_cache_necessidade_especial(self):
        """
        Atualiza data de atuação de férias, em Servidor, caso esteja None.
        O valor aplicado será a data de exercício da MovimentacaoPosse.
        """
        message = "atualiza_cache_necessidade_especial"
        try:
            with transaction.atomic():
                pessoa_fisica = PessoaFisica.objects.get(pk=self.pk)
                if (
                    pessoa_fisica.necessidade_especial
                    != pessoa_fisica.necessidades_especiais.exists()
                ):
                    message = "%s CACHE NECESSIDADE ESPECIAL: %s -> %s." % (
                        pessoa_fisica,
                        boolean_unicode(pessoa_fisica.necessidade_especial),
                        boolean_unicode(pessoa_fisica.necessidades_especiais.exists()),
                    )
                    pessoa_fisica.necessidade_especial = (
                        pessoa_fisica.necessidades_especiais.exists()
                    )
                    log.debug(message)
                    pessoa_fisica.save()
        except Exception as err:
            log.exception(err)

    def set_data_obito(self, data_obito=None):
        message = "set_data_obito"
        try:
            with transaction.atomic():
                pessoa_fisica = PessoaFisica.objects.get(pk=self.pk)
                if pessoa_fisica.data_obito != data_obito:
                    message = "%s: data do óbito %s -> %s." % (
                        self,
                        (
                            pessoa_fisica.data_obito
                            if pessoa_fisica.data_obito
                            else "----"
                        ),
                        data_obito,
                    )
                    pessoa_fisica.data_obito = data_obito
                    log.debug(message)
                    pessoa_fisica.save()
        except Exception as err:
            log.exception(err)

    @classmethod
    def _grid_diff(klass, person=[]):
        instance = PessoaFisica.objects.filter(pk__in=person)[0]
        instance_new = PessoaFisica.objects.filter(pk__in=person)[1]
        diff = {"grid": True, "items": []}
        field_to_choose = [
            "phone",
            "address",
            "dadosbancarios",
            "documento",
            "necessidades_especiais",
            "social_program",
            "serious_diseases",
        ]
        fields = [f for f in instance._meta.get_fields() if f.name in field_to_choose]
        for fld in fields:
            diff_field = {"name": fld.name, "label": "", "config": {}, "data": []}
            if fld.is_relation:
                if fld.many_to_many:
                    diff_field.update({"label": fld.related_model._meta.verbose_name})
                    queryset = getattr(instance, fld.name).filter()
                    if queryset.count():
                        diff_field.get("config").update(
                            {
                                "manytomany": True,
                                "model": fld.model,
                                "model_class_refer": fld.related_model,
                                "query": {"pk": "{}".format(instance.pk)},
                                "remote_field_name": fld.name,
                            }
                        )

                    data = []
                    for q in queryset:
                        data.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance}
                        )

                    queryset = getattr(instance_new, fld.name).filter()
                    for q in queryset:
                        data.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance_new}
                        )

                    diff_field.update({"data": data})

                elif (
                    not isinstance(fld, (ForeignKey, OneToOneRel))
                    and getattr(instance, fld.name).count()
                ):
                    data = []
                    diff_field.update({"label": fld.related_model._meta.verbose_name})

                    for q in getattr(instance, fld.name).filter():
                        data.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance}
                        )

                    for q in getattr(instance_new, fld.name).filter():
                        data.append(
                            {"pk": q.pk, "unicode": q, "person_unicode": instance_new}
                        )

                    diff_field.get("config").update(
                        {
                            "reverse": True,
                            "model": fld.related_model,
                            "query": {
                                "{}".format(fld.remote_field.name): "{}".format(
                                    instance.pk
                                )
                            },
                            "remote_field_name": fld.remote_field.name,
                            "pk_add": instance_new.pk,
                            "pk_rm": instance.pk,
                        }
                    )
                    diff_field.update({"data": data})

            if len(diff_field.get("data")):
                diff.get("items").append(diff_field)
        return diff

    @classmethod
    def _available_merge(klass, person=[]):
        instance = PessoaFisica.objects.filter(pk__in=person)[0]
        instance_new = PessoaFisica.objects.filter(pk__in=person)[1]
        candidate = {
            "availableMerge": False,
            "message": "Não é possível mesclar as pessoas escolhidas. Elas possuem ligações complexas. Apenas o DMTI poderá fazê-lo.",
            "persons": {
                instance.pk: {"person": instance.pk, "candidate": instance.can_merge},
                instance_new.pk: {
                    "person": instance_new.pk,
                    "candidate": instance_new.can_merge,
                },
            },
        }

        if candidate.get("persons").get(instance.pk).get(
            "candidate", False
        ) or candidate.get("persons").get(instance_new.pk).get("candidate", False):
            candidate.update({"availableMerge": True, "message": ""})

        return candidate

    @property
    def can_merge(self):
        candidate = True
        field_to_choose = [
            "phone",
            "address",
            "dadosbancarios",
            "documento",
            "necessidades_especiais",
            "social_program",
            "serious_diseases",
            "municipio_naturalidade",
            "rg_uf",
            "foto",
            "created_by",
            "modified_by",
            "pessoa_ptr",
        ]
        fields = [
            f
            for f in self._meta.get_fields()
            if f.name not in field_to_choose and f.is_relation
        ]
        for fld in fields:
            fld_name = fld.name
            if not hasattr(self, fld_name):
                fld_name = "%s_set" % fld_name

            if not hasattr(self, fld_name):
                pass
            elif fld.many_to_many and getattr(self, fld_name).count():
                candidate = False
                break
            elif (
                getattr(self, fld_name, None)
                and fld.get_internal_type() in ["ForeignKey", "OneToOneField"]
                and isinstance(fld, (ForeignKey, OneToOneRel))
            ):
                candidate = False
                break
            elif (
                not isinstance(fld, (ForeignKey, OneToOneRel))
                and getattr(self, fld_name).count()
            ):
                candidate = False
                break
        return candidate


class NaturalPersonSpecializedEmployee(PessoaFisica):
    class Meta:
        proxy = True

    def validate_documents(self):
        return True

    def validate_mandatory_blood_factor(self):
        try:
            super(
                NaturalPersonSpecializedEmployee, self
            ).validate_mandatory_blood_factor()
        except Exception as err:
            raise ValidationError({"fator_rh": err})
        return True

    def validate_mandatory_blood(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_blood()
        except Exception as err:
            raise ValidationError({"sangue": err})
        return True

    def validate_mandatory_nis_pisep(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_nis_pisep()
        except Exception as err:
            raise ValidationError({"pis_pasep": err, "nis": err})
        return True

    def validate_mandatory_sex(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_sex()
        except Exception as err:
            raise ValidationError({"sexo": err})
        return True

    def validate_mandatory_race(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_race()
        except Exception as err:
            raise ValidationError({"raca_cor": err})
        return True

    def validate_mandatory_degree_education(self):
        try:
            super(
                NaturalPersonSpecializedEmployee, self
            ).validate_mandatory_degree_education()
        except Exception as err:
            raise ValidationError({"grau_instrucao": err})
        return True

    def validate_mandatory_date_born(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_date_born()
        except Exception as err:
            raise ValidationError({"data_nascimento": err})
        return True

    def validate_mandatory_municipality_naturalness(self):
        try:
            super(
                NaturalPersonSpecializedEmployee, self
            ).validate_mandatory_municipality_naturalness()
        except Exception as err:
            raise ValidationError({"municipio_naturalidade": err})
        return True

    def validate_mandatory_cpf(self):
        try:
            super(NaturalPersonSpecializedEmployee, self).validate_mandatory_cpf()
        except Exception as err:
            raise ValidationError({"cpf": err})
        return True

    def clean(self):
        errors = {}
        try:
            self.validate_mandatory_nis_pisep()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_sex()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_race()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_degree_education()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_date_born()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_municipality_naturalness()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cpf()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        super(NaturalPersonSpecializedEmployee, self).save(*args, **kwargs)


class Lawyer(PessoaFisica):
    oab_swap = models.CharField(max_length=20, blank=True, verbose_name="OAB")

    def save(self, *args, **kwargs):
        if not self.oab_swap:
            raise Exception("É necessário informar o número da OAB.")

        super(Lawyer, self).save(*args, **kwargs)


class LegalPersonManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, cnpj, *args):
        return self.get(cnpj=cnpj)


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "cnpj", "type": "text"},
        {"name": "razao_social", "type": "text"},
    ]
)
class PessoaJuridica(Pessoa):
    """ """

    cnpj = models.CharField(max_length=14, blank=True, null=True)
    razao_social = models.CharField(
        max_length=255, verbose_name="Razão Social", blank=True
    )
    phonetic_social_name = models.CharField(max_length=255, blank=True, null=True)
    objects = LegalPersonManager()

    fields_rate_fill_weight = {
        "cnpj": 50,
        "razao_social": 30,
        "phone": 10,
        "address": 10,
    }

    def validade_cnpj(self):
        if not self.cnpj:
            raise Exception("Obrigatório Informar o CNPJ.")
        return True

    class Meta:
        verbose_name = "Pessoa Jurídica"
        ordering = ("nome", "cnpj")
        permissions = (
            ("can_manage_legal_person", "Permissão para gerenciar Pessoa Jurídica"),
        )

    @classmethod
    def match_weight(cls):
        if not hasattr(cls, "__cache_match_weight"):
            cls.__cache_match_weight = super().match_weight()
            cls.__cache_match_weight.update({"phonetic_social_name": 3.0})

        return cls.__cache_match_weight

    def natural_key(self):
        return (self.cnpj,)

    def save(self, *args, **kwargs):
        self.validade_cnpj()
        query = self.__class__.objects.filter(cnpj=self.cnpj).exclude(
            Q(cnpj="") | Q(cnpj=None)
        )
        msg = "Esse CNPJ já está cadastrado para outra(s) Pessoa(s) Jurídica(s)."
        if self.cnpj:
            self.cnpj = documents.CNPJ(self.cnpj).clear

        if self.pk:
            if query.count() > 0 and not query.filter(pk=self.pk).exists():
                raise Exception(msg)
        else:
            if query.count() > 0:
                raise Exception(msg)

        if not self.razao_social:
            self.razao_social = self.nome

        self.phonetic_social_name = (
            None if not self.razao_social else make_phonetic(self.razao_social)
        )
        self.rate_fill = self._calculate_rate_fill()

        super(PessoaJuridica, self).save(*args, **kwargs)

    def _sum_values_weight_rate_fill(self):
        return sum(self.fields_rate_fill_weight.values())

    def _calculate_rate_fill(self):
        rate = 0

        for attr, value in self.fields_rate_fill_weight.items():
            if attr in self.__dict__.keys() and self.__dict__.get(attr):
                rate += self.fields_rate_fill_weight.get(attr)

            for related in self._meta.related_objects:
                if attr == related.get_accessor_name():
                    if related.related_model.objects.filter(
                        **{related.field.name: self.pk}
                    ).exists():
                        rate += self.fields_rate_fill_weight.get(attr)

        return rate / self._sum_values_weight_rate_fill()

    def __str__(self):
        return self.razao_social if self.razao_social else self.nome

    def validate_has_perm_legal_person(self):
        if not get_current_user().has_perm("rh.can_manage_legal_person"):
            raise Exception("Você não tem permissão para modificar Pessoa Jurídica")

    """ Uma vez que as alterações dos dados em Pessoa Juridica pode impactar diretamente em outros objetos principamente ligados
         a dados importantes
        do RH, tal método possui um conjunto de condições para havaliar se existe relação da instância com outros objetos, caso haja,
        é verificado se o usuário possui permissão para modificar a instancia.
    """

    def validate_perm_person(self):
        """relação com UnidadeAdministrativa"""
        if (
            self.unidadeadministrativa_set.exists()
            or self.como_previdencia_de_unidade_administrativa.exists()
        ):
            self.validate_has_perm_legal_person()

        """ relação com Servidor """
        if self.socialsecurityconfig_set.filter(
            socialsecurityemployee__isnull=False
        ).exists():
            self.validate_has_perm_legal_person()

        """ relação com DadoBancarioConsignatario """
        if self.dadobancarioconsignatario_set.exists():
            self.validate_has_perm_legal_person()

        """ relação com rh.SocialSecurity """
        if self.socialsecurity.exists():
            self.validate_has_perm_legal_person()

        """ relação com gfp.Evento """
        if self.eventos_consignacoes.exists():
            self.validate_has_perm_legal_person()

        return True


class Municipio(CObject):
    """
    Tornou-se classe abstrata para ser utilizada como modelo para Localidade.
    Pode ser interessante ligar o Municipio e o Estado à entidade UnidadeAdministrativa
    """

    estado = models.ForeignKey("Estado", on_delete=models.CASCADE)
    sigla = models.CharField(max_length=6, null=True, blank=True)
    siafi = models.CharField(max_length=12, null=True, blank=True)
    ibge = models.IntegerField(null=True, blank=True, verbose_name="IBGE")
    valor_vale_transporte = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor vale transporte",
    )

    class Meta:
        verbose_name = "Munícipio"
        abstract = True


class GeneralOrganManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, codigo_igeprev, *args):
        return self.get(codigo_igeprev=codigo_igeprev)


@to_search(
    [
        {"name": "pk", "type": "number"},
        {"name": "nome", "type": "text"},
        {"name": "sigla", "type": "text"},
    ]
)
@auditable(
    exclude=[
        "id",
    ]
)
class OrgaoGeral(CObject):
    class Meta:
        verbose_name = "Órgão Geral"
        ordering = ["nome"]
        permissions = (("can_manage_general_organ", "Pode Gerenciar Órgão Geral"),)

    abreviacao = models.CharField(
        max_length=60, verbose_name="Abreviação", null=True, blank=True
    )
    esfera_governamental = models.IntegerField(
        choices=ESFERA_GOVERNAMENTAL_CHOICES, null=True, blank=True
    )
    poder = models.IntegerField(choices=PODER_CHOICES, null=True, blank=True)
    sigla = models.CharField(max_length=10, null=True, blank=True)
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    codigo_igeprev = models.IntegerField(
        unique=True, blank=True, verbose_name="Código igeprev"
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    publica_doc = models.BooleanField(verbose_name="Publica", default=False)
    habilita_protocolo = models.BooleanField(default=False)
    order_nome = models.SlugField(null=True, blank=True, max_length=100)
    old = models.ForeignKey(
        "OrgaoGeral",
        null=True,
        blank=True,
        verbose_name="Órgão antigo",
        related_name="new",
        on_delete=models.CASCADE,
    )
    publication = models.ForeignKey(
        "Publicacao",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="generalorgan_creating",
        verbose_name="Publicação criação",
    )
    cache_identifier = models.CharField(
        max_length=10, verbose_name="Cache de Id", default="0"
    )
    order_weight = models.SmallIntegerField(
        verbose_name="Peso ordenação", default=0, blank=True
    )

    objects = GeneralOrganManager()

    AUDITABLE = {"fields": ["old_id"]}

    def __str__(self):
        try:
            if self.lotacao and not self.lotacao.organograma:
                return "**%s" % (
                    "%s - %s" % (self.sigla, self.nome) if self.sigla else self.nome
                )
        except Exception:
            pass
        return "%s" % ("%s - %s" % (self.sigla, self.nome) if self.sigla else self.nome)

    def natural_key(self):
        return (self.codigo_igeprev,)

    def sigla_estrutura(self):
        return "%s" % self.sigla

    def new_and_old(self):
        new = self
        if (
            hasattr(self, "lotacao") or hasattr(self, "unidadeadministrativa")
        ) and hasattr(self, "orgaogeral_ptr"):
            new = self.orgaogeral_ptr
        old = self.old
        if self.old_fields.get("old_id", False) and not self.old:
            old = new
            new = self.old_fields.get("old_id", False)
        return new, old

    def validate_has_perm_general_organ(self):
        if not get_current_user().has_perm("rh.can_manage_general_organ"):
            raise Exception("Você não tem permissão para modificar o Órgao Geral")

    def validate_general_organ(self):
        if hasattr(self, "lotacao"):
            self.validate_has_perm_general_organ()

    def validate(self):
        self.validate_general_organ()

    def save(self, *args, **kargs):
        self.codigo_igeprev = (
            self.igeprev_code_generator()
            if not self.codigo_igeprev
            else self.codigo_igeprev
        )
        self.validate()
        self.order_nome = slugify(self.nome)
        super(OrgaoGeral, self).save(*args, **kargs)

    @classmethod
    def igeprev_code_generator(cls):
        code = 1
        general_organs = OrgaoGeral.objects.filter().exclude(codigo_igeprev=None)
        if general_organs.exists():
            code = general_organs.order_by("-codigo_igeprev")[0].codigo_igeprev
        while OrgaoGeral.objects.filter(codigo_igeprev=code).exists():
            code += 1
        return code


class TaxAllocationConfig(ListDatedModel, AuditTimestampModel):
    OVERLAP_FIELDS = ["fpas", "terc_code"]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    administrative_unit = models.ForeignKey(
        "UnidadeAdministrativa",
        on_delete=models.CASCADE,
        related_name="tax_allocation_configs",
    )
    fpas = models.PositiveIntegerField("Código FPAS", default=582)
    terc_code = models.CharField("Código de Terceiros", default="0000", max_length=4)

    def __str__(self):
        final = self.end_validity if self.end_validity else "----"
        return "%s (%s, %s) - %s a %s" % (
            self.administrative_unit.sigla,
            self.fpas,
            self.terc_code,
            self.start_validity.strftime("%d/%m/%Y"),
            final,
        )


class EstablishmentConfig(ListDatedModel, AuditTimestampModel):
    OVERLAP_FIELDS = ["cnae_preponderant", "rat_value", "fap_value"]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    administrative_unit = models.ForeignKey(
        "UnidadeAdministrativa",
        on_delete=models.CASCADE,
        related_name="establishment_configs",
    )
    cnae_preponderant = models.PositiveIntegerField(blank=True, null=True)
    rat_value = models.DecimalField(
        verbose_name="Fator RAT", max_digits=5, decimal_places=2
    )
    fap_value = models.DecimalField(
        verbose_name="Fator FAP", max_digits=8, decimal_places=4
    )
    send_fap = models.BooleanField(
        default=False, verbose_name="Forçar envio FAP ao eSocial?"
    )

    def __str__(self):
        final = self.end_validity if self.end_validity else "----"
        return "%s (%s, %s, %s) - %s a %s" % (
            self.administrative_unit.sigla,
            self.cnae_preponderant,
            self.rat_value,
            self.fap_value,
            self.start_validity.strftime("%d/%m/%Y"),
            final,
        )


class AdministrativeUnitConfig(ListDatedModel, AuditTimestampModel):
    OVERLAP_FIELDS = [
        "tax_classification",
        "eletronic_reg_employees",
        "federative_body",
    ]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    administrative_unit = models.ForeignKey(
        "UnidadeAdministrativa", on_delete=models.CASCADE, related_name="configs"
    )
    tax_classification = models.IntegerField(
        choices=Choice.get_choices_for("esocial", "TABLE_8"),
        verbose_name="Classificação tributária",
    )
    federative_body = models.ForeignKey(
        "PessoaJuridica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Ente federativo",
    )
    legal_nature = models.IntegerField(
        choices=Choice.get_choices_for("esocial", "TABLE_9"),
        verbose_name="Natureza jurídica",
        default=1082,
    )
    eletronic_reg_employees = models.BooleanField(
        "Opta por registro eletrônico de empregados", default=True
    )

    def __str__(self):
        final = self.end_validity if self.end_validity else "----"
        return "%s - %s a %s" % (
            self.administrative_unit.sigla,
            self.start_validity.strftime("%d/%m/%Y"),
            final,
        )


class AdministrativeUnitManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, codigo_igeprev, *args):
        return self.get(codigo_igeprev=codigo_igeprev)


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "descricao", "type": "text"},
        {"name": "esfera_governamental", "type": "choices"},
        {"name": "poder", "type": "choices"},
    ]
)
class UnidadeAdministrativa(OrgaoGeral):
    pessoa_juridica = models.ForeignKey(
        "PessoaJuridica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Pessoa Jurídica",
    )
    responsavel = models.OneToOneField(
        "PessoaFisica",
        null=True,
        blank=True,
        verbose_name="Responsável",
        on_delete=models.CASCADE,
    )
    numero = models.CharField(
        max_length=3, verbose_name="Número", null=True, blank=True
    )
    email = models.EmailField(null=True, blank=True)
    previdencia = models.ForeignKey(
        PessoaJuridica,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="como_previdencia_de_unidade_administrativa",
    )
    main = models.BooleanField(default=False, blank=True, verbose_name="Próprio órgão?")
    federative_body_owner = models.BooleanField(
        default=False, blank=True, verbose_name="Ente federativo responsável?"
    )
    federative_body = models.ForeignKey(
        "UnidadeAdministrativa",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Ente federativo",
    )
    rpps = models.BooleanField(default=False, blank=True, verbose_name="Possui RPPS?")
    subtetus_reference = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CHOICE_SUBTETUS"),
        verbose_name="Poder que se refere o subteto",
    )
    subtetus_value = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, verbose_name="Valor do subteto"
    )
    siafi = models.CharField(
        max_length=6, verbose_name="Número SIAFI", blank=True, default="000001"
    )

    # DEPRECATED: foram pro config
    tax_classification = models.IntegerField(
        choices=Choice.get_choices_for("esocial", "TABLE_8"),
        verbose_name="Classificação tributária",
        null=True,
        blank=True,
    )
    cnae_preponderant = models.PositiveIntegerField(blank=True, null=True)
    legal_nature = models.IntegerField(
        choices=Choice.get_choices_for("esocial", "TABLE_9"),
        verbose_name="Natureza jurídica",
        null=True,
        blank=True,
    )

    veiculo_publicacao = models.IntegerField(
        verbose_name="Veículo Publicação",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "VEICULO_PUBLICACAO"),
    )

    objects = AdministrativeUnitManager()

    class Meta:
        verbose_name = "Unidade Administrativa"

    def natural_key(self):
        return (self.codigo_igeprev,)

    def save(self, *args, **kargs):
        if (
            UnidadeAdministrativa.objects.filter(
                veiculo_publicacao=self.veiculo_publicacao, ativo=True
            )
            .exclude(pk=self.pk)
            .exclude(veiculo_publicacao=None)
            .exists()
        ):
            raise Exception(
                "É permitido apenas um veículo de publicação por unidade administrativa ativa."
            )
        super(UnidadeAdministrativa, self).save(*args, **kargs)


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "descricao", "type": "text"},
    ]
)
class Lotacao(OrgaoGeral):
    TIPOS_LOTACAO = (
        (0, ""),
        (1, "Administração"),
        (2, "Execução"),
    )

    class Meta:
        verbose_name = "Lotação"
        ordering = ["nome"]
        permissions = (
            (
                "can_allow_lawsuit",
                "Pode habilitar tramitação de procedimentos extrajudiciais",
            ),
        )

    """
        Entidade 'Entidade' deixou de existir, utilizei apenas 'UnidadeAdministrativa'
    """
    comarca = models.ForeignKey(
        "Comarca", null=True, blank=True, on_delete=models.CASCADE
    )
    localidade = models.ForeignKey("Localidade", on_delete=models.CASCADE)
    grupo = models.ManyToManyField("Lotacao")
    entrancia = models.ForeignKey(
        "Entrancia",
        null=True,
        blank=True,
        verbose_name="Entrância",
        on_delete=models.CASCADE,
    )
    instancia = models.ForeignKey(
        "Instancia",
        null=True,
        blank=True,
        verbose_name="Instância",
        on_delete=models.CASCADE,
    )
    pai = models.ForeignKey(
        "Lotacao",
        on_delete=models.CASCADE,
        related_name="lotacoes_subordinadas",
        null=True,
        blank=True,
        verbose_name="Lotação superior",
    )
    responsavel = models.ForeignKey(
        "Servidor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Responsável",
        related_name="responsavel_por",
    )
    andar = models.CharField(max_length=3, null=True, blank=True)
    sala = models.CharField(max_length=6, null=True, blank=True)
    codigo = models.CharField(
        max_length=15, verbose_name="Código", null=True, blank=True
    )
    executivo = models.BooleanField(verbose_name="Executivo", default=False)
    administrativo = models.BooleanField(verbose_name="Administrativo", default=False)
    grupo_lotacao = models.BooleanField(
        verbose_name="Grupo de Lotações", default=False, blank=True
    )
    acesso_protocolo_geral = models.BooleanField(
        verbose_name="Ver todos Protocolos", default=False
    )
    organograma = models.BooleanField(default=False, blank=True)
    lotacionograma = models.BooleanField(default=True, blank=True)
    designacao = models.BooleanField(default=False, blank=True)
    ouvidoria = models.BooleanField(default=False, blank=True)
    responsible_substituted = models.ForeignKey(
        "Servidor",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responsavel_substituido",
        verbose_name="Responsável substituído",
    )
    characteristic = models.ForeignKey(
        "CharacteristicWorkplace",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Característica",
    )
    orgao_arquimedes = models.IntegerField(null=True, blank=True)
    replacements = models.ManyToManyField(
        "self", through="Replacement", symmetrical=False, related_name="+"
    )
    code_cnmp = models.CharField(max_length=4, null=True, blank=True)
    id_itop = models.SmallIntegerField(null=True, blank=True)
    organizational_classification = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "ORGANIZATIONAL_CLASSIFICATION"),
        verbose_name="Classificação do Organograma",
    )
    allow_lawsuit = models.BooleanField(
        verbose_name="Habilita para Procedimentos Extrajudiciais", default=False
    )
    electoral_zone = models.BooleanField("Zona Eleitoral", default=False, blank=True)
    electoral_zone_coverage = models.TextField(
        "Abrangência da Zona Eleitoral", null=True, blank=True
    )
    office_hours = models.ForeignKey(
        "OfficeHoursWorkplace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Horário de Expediente",
    )
    is_contact_displayed = models.BooleanField(
        "Exibir nos contatos do Site?", default=False, blank=True
    )
    portal_approver = models.BooleanField(
        verbose_name="Aprovador Portal", blank=True, null=True
    )
    nucleo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "NUCLEO_CHOICES"), null=True, blank=True
    )
    prioridade = models.IntegerField(
        null=True, blank=True, verbose_name="Prioridade (Lotacionograma)"
    )
    gestor_plantao_dti = models.BooleanField(
        null=True, blank=True, verbose_name="Gestor plantão DTI"
    )
    gestor_plantao_final_semana = models.BooleanField(
        null=True, blank=True, verbose_name="Gestor plantão final de Semana"
    )
    gestor_plantao_recesso = models.BooleanField(
        null=True, blank=True, verbose_name="Gestor plantão recesso"
    )
    gestor_plantao_eleitoral = models.BooleanField(
        null=True, blank=True, verbose_name="Gestor plantão eleitoral"
    )
    gestor_plantao_pgj = models.BooleanField(
        null=True, blank=True, verbose_name="Gestor plantão PGJ"
    )
    tipo_lotacao = models.SmallIntegerField(
        default=0, choices=TIPOS_LOTACAO, blank=True, null=True
    )
    atribuicao = models.ManyToManyField(
        "Atribuicao", verbose_name="Atribuição", related_name="lotacao"
    )
    dimensionamento = models.BooleanField(
        "Dimensionamento BI", default=False, blank=True
    )
    classificacao = models.IntegerField(
        verbose_name="Classificação",
        choices=Choice.get_choices_for("rh", "CLASSIFICACAO_LOTACAO"),
        null=True,
        blank=True,
    )

    AUDITABLE = {"fields": ["responsavel_id"]}

    def __str__(self):
        if not self.organograma:
            return "**%s" % (
                "%s - %s" % (self.sigla, self.nome) if self.sigla else self.nome
            )
        return "%s" % ("%s - %s" % (self.sigla, self.nome) if self.sigla else self.nome)

    def __str__responsible__(self):
        return "%s - Responsável: %s" % (
            (self.nome if self.organograma is True else ("** %s" % self.nome)),
            self.responsavel if self.responsavel else "Não há",
        )

    def _employee_workplaces(self, date=None, active=None, option=None):
        """
        :py:function:: _employee_workplaces(self, date=None, active=None, option=None)

        This method returns a queryset of the all EmployeeWorkplace.

        :param date date: Date to determine a period of EmployeeWorkplace
        :param boolean active: active
        :param int option: Option param defines which designations to return:
            -WORKPLACE: 1 - Workplace;
            -WORK_ASSIGNMENT: 2 - Work Assignment;
            -None - Those above, DEFAULT.
        :return: queryset of EmployeeWorkplace
        """
        query = self.servidores_lotacao
        if date:
            query = query.filter(
                Q(data_vigencia_inicio__lte=date)
                & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
            )

        if option == WORKPLACE:
            query = query.filter(designacao=False)
        elif option == WORK_ASSIGNMENT:
            query = query.filter(designacao=True)

        if active is not None:
            query = query.filter(ativo=active)

        return query.order_by("-data_vigencia_inicio")

    @classmethod
    def workplace_with_exercises(cls, date=None):
        date = date if date else datetime.now().date()
        return (
            Lotacao.objects.filter(
                Q(servidores_lotacao__servidor__tipo__in=["M"])
                & Q(servidores_lotacao__designacao=True)
                & Q(servidores_lotacao__data_vigencia_inicio__lte=date)
                & (
                    Q(servidores_lotacao__data_vigencia_fim__gte=date)
                    | Q(servidores_lotacao__data_vigencia_fim=None)
                )
            )
            .distinct()
            .values("pk")
        )

    @property
    def employees(self):
        return Servidor.objects.filter(
            pk__in=ServidorLotacao.work_assignment_exercise(workplace=[self.pk])
            .filter(servidor__ativo=True, lotacao=self)
            .values("servidor_id")
        )

    @property
    def employee_workplaces_responsible(self):
        """responsaveis"""
        """
            :py:function:: employee_workplaces_responsible(self)

            This method returns a Employee.queryset that has responsible True.
            Uses _employee_workplaces.

            :return: queryset of Employee
            :rtype: queryset
        """
        date = datetime.now().date()
        return self._employee_workplaces(date=date, option=WORK_ASSIGNMENT).filter(
            responsible=True
        )

    @property
    def employee_exercise(self):
        return self._employee_workplaces(active=True, option=WORK_ASSIGNMENT)

    @property
    def owner(self):
        """titular"""
        """
            :py:function:: owner(self)

            This method returns a Employee.queryset that's has JobPosition active.
            And the JobPosition is the owner of the Workplace.

            Employee is owner through Cargo.

            It uses ServidorLotacao.work_assignment() and active .

            :return: queryset of Employee
            :rtype: queryset
        """
        employees = []
        if self.cargo_responsavel.exists():
            employees = MovimentacaoPosse.objects.filter(
                quadro__cargo__lotacao_responsavel=self,
                ativo=True,
                servidor__pk__in=ServidorLotacao.workplace_only_exercise(
                    workplace=self
                ).values("servidor__pk"),
            ).values("servidor__pk")
        return Servidor.objects.filter(pk__in=employees)

    @property
    def employee_workplace_owner(self):
        return (
            ServidorLotacao.workplace_only_exercise(workplace=self)
            .filter(owner=True)
            .last()
        )

    @property
    def owner_for_cache(self):
        """
        :py:function:: owner_for_cache(self)

        This method returns a Employee owner of the Workplace.

        :return: Employee
        :rtype: Employee
        """
        return getattr(self.employee_workplace_owner, "servidor", None)

    @property
    def owner_publication(self):
        return getattr(self.employee_workplace_owner, "publicacao", None)

    @property
    def responsible_name(self):
        if self.responsavel:
            return self.responsavel.pessoa_fisica.nome
        return None

    def my_replacement(self, date=None, owner=True):
        """
        :py:function:: my_replacement(self, date=None, owner=True)

        This method returns Replacement QuerySet from Servidor.
        Considers if exist a validity document.

        :param date date - default is datetime.now().date()
        :param bool owner - default is True

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        date = datetime.now().date() if not date else date

        replacements = Replacement.objects.filter(
            replaced=self,
        )
        return replacements.distinct()

    def my_replacement_substitute(
        self, date=None, owner=False, employee=None, workplace=None
    ):
        """
        :py:function:: my_replacement_substitute(self, date=None, owner=False)

        This method verifies substitutes that are at ExecutionOrgan.
        Considers EmployeeWorkplace.owner and date validity.

        :param date date - default is datetime.now().date()
        :param bool owner - default is False
        :param Employee employee:
        :param Workplace workplace:

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        date = datetime.now().date() if not date else date
        substitutes = self.my_replacement(date=date).filter(
            substitute__servidores_lotacao__ativo=True,
            substitute__servidores_lotacao__responsible=True,
            substitute__servidores_lotacao__designacao=True,
        )
        return substitutes

    def my_replacement_employee_workplace(self):
        """
        :py:function:: my_replacement_employee_workplace(self)

        This method returns a ServidorLotacao QuerySet from my_replacement_substitute method.

        :return: QuerySet of EmployeeWorkplace
        :rtype: QuerySet
        """
        my_replacement_substitute = self.my_replacement_substitute()
        my_replacement_substitute = my_replacement_substitute.values(
            "substitute__servidores_lotacao__pk",
            "substitute__servidores_lotacao__servidor__pk",
        )
        employee_workplaces = []
        employees = []
        for rs in my_replacement_substitute:
            employee_workplaces.append(rs.get("substitute__servidores_lotacao__pk"))
            employees.append(rs.get("substitute__servidores_lotacao__servidor__pk"))
        return ServidorLotacao.objects.filter(
            pk__in=employee_workplaces,
            servidor__pk__in=employees,
            ativo=True,
        )

    def my_substitute_employee(self):
        """
        :py:function:: my_substitute_employee(self)

        This method returns a Servidor QuerySet from my_replacement_substitute method.

        :return: QuerySet of Servidor
        :rtype: QuerySet
        """
        return Servidor.objects.filter(
            matricula__in=self.my_replacement_substitute().values(
                "substitute__servidores_lotacao__servidor__matricula"
            )
        )

    def my_substitute_by_employee_order(self, employee):
        identify = {
            "registry": employee.matricula,
            "workplace": self.pk,
            "workplace_substitute": [],
            "order": 0,
        }
        replacements = (
            self.my_replacement()
            .filter(
                substitute__servidores_lotacao__owner=True,
                substitute__servidores_lotacao__designacao=False,
                substitute__servidores_lotacao__servidor__tipo="M",
            )
            .distinct()
        )
        replacements_employee_workplace = ServidorLotacao.objects.filter(
            lotacao__pk__in=replacements.values(
                "substitute__servidores_lotacao__lotacao__pk"
            ),
            servidor__tipo="M",
            designacao=True,
            ativo=True,
            servidor=employee,
        ).exclude(ordinance=True)
        for employee_workplace in replacements_employee_workplace.filter().distinct():
            rpl = (
                self.my_replacement()
                .filter(
                    substitute__servidores_lotacao__lotacao=employee_workplace.lotacao,
                    substitute__servidores_lotacao__servidor=employee_workplace.servidor,
                )
                .distinct()
            )
            if rpl.exists():
                rpl = rpl.earliest("order")
                identify.get("workplace_substitute").append(
                    {"order": rpl.order, "substitute": rpl.substitute.pk}
                )
                if identify.get("order") < rpl.order:
                    identify.update({"order": rpl.order})
        return identify

    def my_substitute_workplace(self):
        """
        :py:function:: my_substitute_workplace(self)

        This method returns Workplace querset that substitutes a Employee according the replacement table.

        :return: queryset of Workplace
        :rtype: queryset of Workplace
        """
        return Lotacao.objects.filter(
            pk__in=self.my_replacement_substitute().values("substitute__pk")
        )

    def my_substitute_workplace_only(self):
        """
        :py:function:: my_substitute_workplace_only(self)

        This method returns Workplace querset that substitutes a Employee according the replacement table.

        :return: queryset of Workplace
        :rtype: queryset of Workplace
        """
        return Lotacao.objects.filter(
            pk__in=self.my_replacement().values("substitute__pk")
        )

    def validate(self):
        self.validate_code_cnmp()
        self.validar_classificacao()

    def validar_classificacao(self):
        if not self.classificacao:
            raise Exception("O campo Classificação da aba Outros deve ser selecionado!")

    def validate_code_cnmp(self):
        if self.code_cnmp:
            if not self.code_cnmp.isdigit():
                raise Exception(
                    "O campo Código CNMP deve ser preenchido apenas com dígitos numéricos."
                )
            elif len(self.code_cnmp) > 4:
                raise Exception("O campo Código CNMP deve conter no máximo 4 dígitos.")
            else:
                self.code_cnmp = "%04d" % int(self.code_cnmp)

            if (
                Lotacao.objects.filter(code_cnmp=self.code_cnmp)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise Exception("O campo Código CNMP não pode ser repetido.")
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        if (
            self.responsible_substituted
            and self.old_fields.get("responsavel_id", False)
            and not kargs.get("mandatory", False)
        ):
            raise Exception(
                "Enquanto houver substituição ativa não é permitido alterar o responsável da lotação."
            )

        if "mandatory" in kargs:
            kargs.pop("mandatory")

        self.validate()

        super(Lotacao, self).save(*args, **kargs)

        self.update_chief_immediate(old_fields=self.old_fields)

    def update_responsible(self, responsible=None, responsible_new=None):
        """
        :py:function:: update_responsible(self, responsible_old, workplace)

        This method updates the responsible of the workplace. If responsible parameter was not provided then
        will be set responsible_new parameter as the responsible. Otherwise if responsible_new was not provided then
        will be set responsible parameter as the responsible.

        :param Servidor responsible: responsible
        :param Servidor responsible_new: responsible_new
        """
        message = "Atualizando responsável de %s." % self
        try:
            with transaction.atomic():
                workplace = Lotacao.objects.get(pk=self.pk)
                if not responsible:
                    workplace.responsavel = responsible_new
                    message += "\n===>>>>>Novo responsável %s." % responsible_new
                    log.info(message)
                    workplace.save(mandatory=True)
                elif not responsible_new and responsible == workplace.responsavel:
                    workplace.responsavel = responsible_new
                    message += "\n===>>>>>Novo responsável %s." % responsible_new
                    log.info(message)
                    workplace.save(mandatory=True)
        except Exception as err:
            log.exception(err)
            mail_managers(
                "Erro em Lotacao.update_responsible",
                "%s : -> %s" % (message, err),
                fail_silently=True,
            )

    def update_employee_chief_immediate_from_workplace(self, responsible_old):
        """
        :py:function:: update_employee_chief_immediate_from_workplace(self, responsible_old)

        This method updates the chief immediate of the employees from the workplace that its responsible was
        changed.

        The method Servidor.update_chief_immediate will verify if the current chief immediate is equal to the old
        responsible from the workplace.

        :param Servidor responsible_old: responsible_old
        """
        _employee_workplaces = self._employee_workplaces().filter(ativo=True)
        log.info(
            """ATUALIZANDO CHEFIA \n LOTAÇÃO: %s \n RESPONSÁVEL ANTIGO: %s \n TOTAL SUBORDINADOS: (%s) RESPONSÁVEL NOVO: %s"""
            % (
                self,
                responsible_old if responsible_old else "----",
                _employee_workplaces.count(),
                self.responsavel if self.responsavel else "----",
            )
        )
        for employee in _employee_workplaces.values("servidor").distinct():
            Servidor.objects.get(pk=employee.get("servidor")).update_chief_immediate(
                old_chief=(
                    Servidor.objects.get(pk=responsible_old)
                    if responsible_old
                    else None
                )
            )

    def update_chief_immediate_of_old_responsible(self, responsible_old):
        """
        :py:function:: update_chief_immediate_of_old_responsible(self, responsible_old)

        This method updates the chief immediate of the old responsible.

        :param Servidor responsible_old: responsible_old
        """
        if responsible_old:
            responsible_old = Servidor.objects.get(pk=responsible_old)
            log.info(
                "ATUALIZANDO CHEFIA DO RESPONSÁVEL ANTIGO: %s  %s >> %s"
                % (
                    responsible_old if responsible_old else "----",
                    responsible_old.chefe_imediato if responsible_old else "----",
                    (
                        responsible_old._get_chefe_imediato()
                        if responsible_old
                        else "----"
                    ),
                )
            )
            responsible_old.update_chief_immediate(mandatory=True)

    def update_chief_immediate_of_new_responsible(self):
        """
        :py:function:: update_chief_immediate_of_new_responsible(self)

        This method updates the chief immediate of the new responsible.
        """
        if self.responsavel:
            log.info(
                "ATUALIZANDO CHEFIA DO NOVO RESPONSÁVEL: \n%s \n# DE # \n%s \n>> PARA >> \n%s"
                % (
                    self.responsavel,
                    self.responsavel.chefe_imediato,
                    self.responsavel._get_chefe_imediato(),
                )
            )
            self.responsavel.update_chief_immediate(mandatory=True)

    def update_telework_approver(self, approver=None):
        """
        Atualiza o aprovador das movimentações de teletrabalho com base nos locais de trabalho
        dos funcionários e na pessoa responsável.

        Esta função filtra os locais de trabalho ativos dos funcionários e as movimentações
        de teletrabalho ativas para esses funcionários. Em seguida, atualizao aprovador dessas
        movimentações para ser a pessoa responsável por esta instância do método
        `update_telework_approver`.

        :return: None
        """
        if not approver:
            approver = self.responsavel

        _employee_workplaces = self._employee_workplaces().filter(ativo=True)
        telework_movs = MovimentacaoTeletrabalho.objects.filter(
            Q(Q(data_fim__gte=datetime.now().date()) | Q(data_fim__isnull=True)),
            servidor__in=_employee_workplaces.values_list("servidor", flat=True),
            ativo=True,
        )
        telework_movs.update(aprovador=approver)

        # Update the sending report
        from rh.pvf.models import SendingTelework

        SendingTelework.update_approver_from_existing_telework_report(
            telework_movs, approver
        )

    def update_chief_immediate(self, old_fields={}):
        """
        :py:function:: update_chief_immediate(self, old_fields=[])

        This method updates the chief immediate of the employees from the workplace that its responsible was
        changed.

        Use the methods:
            * update_employee_chief_immediate_from_workplace;
            * update_chief_immediate_of_old_responsible;
            * update_chief_immediate_of_new_responsible;

        :param list old_fields: old_fields, default is []
        """
        message = "Lotacao.update_chief_immediate %s" % self
        if not self.responsible_substituted:
            try:
                responsible_old = old_fields.get("responsavel_id", None)
                if (
                    self.responsavel
                    and responsible_old
                    and self.responsavel.pk != responsible_old[0]
                ):
                    self.update_employee_chief_immediate_from_workplace(
                        responsible_old[0]
                    )
                    self.update_chief_immediate_of_old_responsible(responsible_old[0])
                    self.update_chief_immediate_of_new_responsible()
                    self.update_telework_approver()
                else:
                    log.info(
                        "Responsável atual e o antigo não são diferentes: %s"
                        % self.responsavel
                    )
            except Exception as err:
                log.exception(err)
                mail_managers(
                    "Erro em Lotacao.update_chief_immediate",
                    "%s : -> %s" % (message, "%s" % err),
                    fail_silently=True,
                )
        else:
            log.info(
                "A modificação do chefe imediato dos servidores só roda após o encerramento da substituição."
            )

    @classmethod
    def update_chief_immediate_from_new_member(
        cls, work_assignment, propagate_resp=True
    ):
        """
        :py:function:: update_chief_immediate_from_new_member(cls, work_assignment)

        This method updates the chief immediate of the employees from the workplace that its responsible was
        changed.

        :param EmployeeWorkplace work_assignment:
        :raises Exception: if workplace has a responsible substituted
        """
        message = ""
        if (
            work_assignment.is_active()
            and work_assignment.designacao
            and work_assignment.responsible
            and work_assignment.servidor.member_type_by_possession
            and work_assignment.servidor.is_ativo()
        ):
            workplace = Lotacao.objects.get(pk=work_assignment.lotacao.pk)
            if not workplace.responsible_substituted:
                workplace.responsavel = work_assignment.servidor
                try:
                    workplace.save()
                except Exception as err:
                    message = err
            elif not workplace.responsible_substituted:
                message = "Não é possível adicionar um novo responsável enquanto o antigo estiver afastado e possuir substituto."

            if propagate_resp and message:
                raise Exception(message)
            else:
                log.info(message)

    def toggle_allow_lawsuit(self):
        toggle = not self.allow_lawsuit

        if get_current_user().has_perm("rh.can_allow_lawsuit"):
            self.__class__.objects.filter(pk=self.pk).update(
                allow_lawsuit=toggle,
                modified_by=get_current_user(),
                modified_at=datetime.now(),
            )
        else:
            raise Exception("Você não tem permissão para executar essa ação")


class WorkplaceConfigTag(ListDatedModel):
    OVERLAP_FIELDS = ["workplace", "tag"]
    AUTO_CLOSE_PERIOD_OVERLAP = True

    workplace = models.ForeignKey(
        "Lotacao",
        verbose_name="Lotação",
        related_name="workplace_config_tags",
        on_delete=models.CASCADE,
    )
    tag = models.CharField(
        max_length=5,
        choices=Choice.get_choices_for(
            app_label="rh", name="WORKPLACE_TAG", char_field=True
        ),
        db_index=True,
    )


class ChoiceWorkplaceMigrate(Choice):
    class Meta:
        proxy = True


class WorkplaceMigrate(AuditTimestampModel):
    workplace = models.ForeignKey(
        Lotacao,
        verbose_name="Lotação",
        related_name="workplace_workplacemigrate",
        on_delete=models.PROTECT,
    )
    workplace_destiny = models.ForeignKey(
        Lotacao,
        verbose_name="Lotação de destino",
        null=True,
        blank=True,
        related_name="workplace_destiny_workplacemigrate",
        on_delete=models.PROTECT,
    )
    publication = models.ForeignKey(
        "Publicacao",
        verbose_name="Publicação",
        related_name="publication_workplacemigrate",
        on_delete=models.PROTECT,
    )
    signed_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    type_of_migrate = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_OF_MIGRATE"),
        verbose_name="Tipo",
        default=1,
    )
    description = models.CharField(
        max_length=400, verbose_name="Decrição", default="", blank=True
    )

    def __str__(self):
        return "%s - %s" % (self.get_type_of_migrate_display(), self.workplace)

    def perform_migration(self):
        from rh.signals.workplacemigrate import (
            workplacemigrate_post,
            workplacemigrate_pre,
        )

        workplacemigrate_pre.send(sender=self.__class__, instance=self)
        WorkplaceMigrate.objects.filter(pk=self.pk).update(
            signed_by=get_current_user(), signed_at=datetime.now()
        )
        workplacemigrate_post.send(sender=self.__class__, instance=self)


class TargetWorkplaceMigrate(AuditTimestampModel):
    workplace_migrate = models.ForeignKey(
        WorkplaceMigrate,
        verbose_name="Migração de Lotação",
        related_name="workplace_migrate_targetworkplacemigrate",
        on_delete=models.CASCADE,
    )
    type_of_target = models.IntegerField(
        choices=Choice.get_choices_for("rh", "APP_TO_MIGRATE"),
        verbose_name="Tipo",
        default=1,
    )
    done_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    done_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.get_type_of_target_display(), self.workplace_migrate)


class Atribuicao(AuditTimestampModel):
    descricao = models.CharField(
        max_length=400, verbose_name="Decrição", null=True, blank=True
    )
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.descricao)

    class Meta:
        verbose_name = "Atribuição"
        ordering = ["descricao"]

    def save(self, *args, **kargs):
        self.validate()
        super(Atribuicao, self).save(*args, **kargs)

    def validate(self):
        self.validate_descricao()

    def validate_descricao(self):
        if self.descricao == "":
            raise Exception("Favor preencher o campo: Descrição.")


class ExperienciaProfissional(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor",
        on_delete=models.CASCADE,
        verbose_name="Servidor",
        null=True,
        blank=True,
        related_name="experiencia_profissional",
    )
    cargo = models.CharField(
        max_length=256, verbose_name="Cargo", null=True, blank=True
    )
    empregador = models.CharField(
        max_length=256, verbose_name="Empregador", null=True, blank=True
    )
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.cargo)

    class Meta:
        verbose_name = "Experiência Profissional"
        ordering = ["cargo"]

    def save(self, *args, **kargs):
        self.validate()
        super(ExperienciaProfissional, self).save(*args, **kargs)

    def validate(self):
        self.validate_cargo()
        self.validate_empregador()

    def validate_cargo(self):
        if self.cargo == "":
            raise Exception("Favor preencher o campo: Cargo.")

    def validate_empregador(self):
        if self.empregador == "":
            raise Exception("Favor preencher o campo: Empregador.")


@to_search(
    [
        {"name": "banco__nome", "type": "text"},
        {"name": "tipo_conta", "type": "choices"},
        {"name": "agencia", "type": "text"},
        {"name": "conta_corrente_completa", "type": "text"},
    ]
)
class DadoBancario(AuditTimestampModel):
    class Meta:
        verbose_name = "Dado Bancário"
        ordering = ["banco"]

    class ValidateAgencia(Exception):
        def __init__(self):
            Exception.__init__("Número de agência inválido.")

    class ValidateConta(Exception):
        def __init__(self):
            Exception.__init__("Número de conta bancária inválido.")

    banco = models.ForeignKey("Banco", on_delete=models.CASCADE)
    tipo_conta = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_CONTA"), verbose_name="Tipo de Conta"
    )
    agencia = models.CharField(
        max_length=15, verbose_name="Agência com DV", default="", blank=False
    )
    conta_corrente_completa = models.CharField(
        max_length=15, verbose_name="Conta Corrente com DV", default="", blank=False
    )
    agencia_numero = models.CharField(
        "Número da agência", max_length=50, null=True, blank=True
    )
    agencia_dv = models.CharField("DV da agência", max_length=5, null=True, blank=True)
    conta_numero = models.CharField(
        "Número da conta", max_length=50, null=True, blank=True
    )
    conta_dv = models.CharField("DV da conta", max_length=5, null=True, blank=True)

    def __str__(self):
        if self.agencia_numero and self.conta_numero:
            ag = self.agencia_str
            conta = self.conta_str
            return f"{self.banco} - {self.tipo_conta} - Ag: {ag} - Conta: {conta}"
        else:
            return "{banco} - {tipo} - Ag: {agencia} - Conta: {numero}".format(
                banco=self.banco,
                tipo=self.tipo_conta,
                agencia=self.agencia,
                numero=self.conta_corrente_completa,
            )

    def _validate(self):
        return True

    def validate(self):
        if (
            self.agencia_numero not in ["", None]
            or self.agencia_dv not in ["", None]
            or self.conta_numero not in ["", None]
            or self.conta_dv not in ["", None]
        ):
            if self.agencia_numero is None:
                raise Exception("Por favor preencha o campo 'Número da agência'.")
            # elif self.agencia_dv is None:
            #     raise Exception("Por favor preencha o campo 'DV da agência'.")
            elif self.conta_numero is None:
                raise Exception("Por favor preencha o campo 'Número da conta'.")
            # elif self.conta_dv is None:
            #     raise Exception("Por favor preencha o campo 'DV da conta'.")
        else:
            if hasattr(self, "_validate%s" % self.banco.numero):
                getattr(self, "_validate%s" % self.banco.numero)()
            else:
                self._validate()

    def clean(self):
        self.validate()

    @property
    def banco_str(self):
        return f"{self.banco.nome}({self.banco.numero})"

    @property
    def agencia_str(self):
        if self.agencia_numero:
            agencia = f"{self.agencia_numero}"
            if self.agencia_dv and self.agencia_dv != "" and self.agencia_dv != "None":
                agencia += f"-{self.agencia_dv}"
            return agencia
        else:
            return f"{self.agencia}"

    @property
    def conta_str(self):
        if self.conta_numero:
            conta = f"{self.conta_numero}"
            if self.conta_dv and self.conta_dv != "" and self.conta_dv != "None":
                conta += f"-{self.conta_dv}"

            return conta
        else:
            return f"{self.conta_corrente_completa}"


class StateManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, sigla, *args):
        return self.get(sigla=sigla)

    def get_queryset(self):
        return super().get_queryset().exclude(pk__in=[131, 132])


class Estado(CObject):
    class Meta:
        verbose_name = "Estado"
        ordering = ["nome"]

    pais = models.ForeignKey("Pais", verbose_name="País", on_delete=models.CASCADE)
    sigla = models.CharField(max_length=2, default="")
    siafi = models.CharField(max_length=12, null=True, blank=True, verbose_name="SIAFI")
    tse = models.CharField(max_length=12, null=True, blank=True, verbose_name="TSE")
    ibge = models.IntegerField(verbose_name="IBGE", null=True, blank=True)
    objects = StateManager()

    def natural_key(self):
        return (self.sigla,)

    def __str__(self):
        return "%s" % self.nome


class Comarca(CObject):
    circunscricao = models.ForeignKey(
        "Circunscricao", null=True, blank=True, on_delete=models.CASCADE
    )
    grupo_comarca = models.ForeignKey(
        "GrupoComarca", null=True, blank=True, on_delete=models.CASCADE
    )
    validacao = models.BooleanField(default=True, verbose_name="Validação")

    class Meta:
        verbose_name = "Comarca"


class MicroRegiao(CObject):
    meso_regiao = models.ForeignKey("MesoRegiao", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Micro Região"


class LocalityManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, ibge, *args):
        return self.get(ibge=ibge)

    def get_queryset(self):
        ids_exclude = [12374, 12362, 8933, 12380, 12385, 12379, 8933]
        return (
            super().get_queryset().exclude(pk__in=ids_exclude)
        )  # .exclude(ibge__isnull=True)


@to_search(
    [
        {"name": "nome", "type": "text"},
        {"name": "sigla", "type": "text"},
        {"name": "cep", "type": "text"},
        {"name": "ibge", "type": "text"},
    ]
)
class Localidade(Municipio):
    microregiao = models.ForeignKey(
        "MicroRegiao", null=True, blank=True, on_delete=models.CASCADE
    )
    comarca = models.ForeignKey(
        "Comarca", null=True, blank=True, on_delete=models.CASCADE
    )
    cep = models.CharField(max_length=9, null=True, blank=True)
    distancia_capital = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Distância Capital",
    )
    indicador_municipio = models.BooleanField(
        default=False, verbose_name="Indicador Município", blank=True
    )
    sede_termo = models.BooleanField(default=False, blank=True)
    objects = LocalityManager()

    class Meta:
        verbose_name = "Localidade"

    def natural_key(self):
        return (self.ibge,)

    def __str__(self):
        return "%s/%s" % (self.nome, self.estado.sigla)

    @property
    def get_sigla_estado(self):
        return self.estado.sigla

    @property
    def get_comarca(self):
        if self.comarca:
            return self.comarca.nome
        return None

    @property
    def qtd_lotacao(self):
        return self.lotacao_set.filter(ativo=True).count()


class ServidorQueryset(models.QuerySet):
    def on_period_and_main_payroll(self, month, year):
        return self.filter(
            paychecks__folha__periodo__mes=month,
            paychecks__folha__periodo__ano=year,
            paychecks__folha__tipo_folha__principal=True,
        )

    def by_type_job_position(self, types):
        return self.filter(
            movimentacaopessoal__movimentacaoposse__quadro__cargo__tipo_lei_cargo__in=types
        ).distinct()

    def by_type_possession(self, types):
        return self.filter(type_by_possession__in=types)

    def without_required(self):
        return self.exclude(
            movimentacaopessoal__movimentacaoposse__quadro__cargo__tipo_lei_cargo="AC"
        )

    def active(self):
        return self.filter(ativo=True)

    def active_in(self, start_date=None, end_date=None, date_range=None):
        """Esse método retorna os servidores ativos em um determinado periodo, que pode ser passado pelas
        datas de inicio e fim ou por um date_range. Caso uma das datas não seja informada ela não será considerada
        no filtro, tendo como resultado um range aberto, se a duas datas não forem informadas, será considerada a data do dia.
        """
        if date_range:
            start_date = date_range.first
            end_date = date_range.last
        if not (start_date and end_date):
            start_date = end_date = datetime.now().date()

        query = self.all()
        if start_date:
            query = query.filter(
                Q(termination_date__isnull=True)
                | (
                    Q(termination_date__isnull=False)
                    & Q(termination_date__gt=start_date)
                )
            )
        if end_date:
            query = query.filter(
                Q(exercise_date__isnull=False) & Q(exercise_date__lte=end_date)
            )
        return query

    def active_requested(self, *args, **kwargs):
        requested_active = RequestMove.objects.assets_in(*args, **kwargs).values_list(
            "servidor"
        )
        return self.filter(pk__in=requested_active)

    def matricula_greater_than(self, size):
        mats = []
        for x in self:
            if len(str(x.matricula)) > size:
                mats.append(x.matricula)
        return self.filter(matricula__in=mats)

    def no_requested_without_onus(self):
        return self.exclude(movimentacaopessoal__movimentacaoposse__requestmove__onus=1)

    def by_type_provisions(self, provisions):
        return self.filter(
            movimentacaopessoal__movimentacaoposse__tipo_movcarreira__in=provisions
        )

    def departured_on(self, **kwargs):
        start_date = kwargs.get("start_date", datetime.today())
        end_date = kwargs.get("end_date", None)
        range_ = kwargs.get("range", NewDateRange(start_date, end_date))
        return self.filter(
            Q(movimentacaopessoal__baselicencaafastamento__data_inicio__lte=range_.last)
            & (
                Q(
                    movimentacaopessoal__baselicencaafastamento__data_fim__gte=range_.first
                )
                | Q(movimentacaopessoal__baselicencaafastamento__data_fim=None)
            )
        ).exclude(movimentacaopessoal__baselicencaafastamento__estado=CANCELED)


@to_search(
    [
        {"name": "pessoa_fisica__nome", "type": "text"},
        {"name": "pessoa_fisica__nome_pai", "type": "text"},
        {"name": "pessoa_fisica__nome_mae", "type": "text"},
        {"name": "matricula", "type": "text"},
        {"name": "user__username", "type": "text"},
        {"name": "data_referencia_ferias", "type": "date"},
        {"name": "data_referencia_ferias", "type": "date_time"},
    ]
)
class Servidor(AuditTimestampModel):
    """
    Classe de abstração de servidor

    @data_referencia_ferias -> data de referência de férias para o servidor, será utilizado para saber a partir
        de qual data o servidor pode usufruir as férias referente a um determinado período
    @tipo -> Atributo cache para armazena o tipo do servidor (M ou S)
        OBS.: Este atributo NÃO DEVE ser setado via sistema, pois ele será atualizado automaticamente
              quando o servidor tomar posse `em um cargo de servidor ou membro
    @ativo -> Atributo cache para informar se um servidor está ativo ou não
        OBS.: Este atributo NÃO DEVE ser setado via sistema, pois ele será atualizado automaticamente
              quando servidor tomar posse ou for exonerado, logo para um servidor esta ativo ele deve possuir
              pelo menos uma posse ativa
    @notificacoes -> queryset com todas as notificações enviadas para o servidor
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuário",
        null=True,
        blank=True,
        related_name="servidor",
    )
    pessoa_fisica = models.ForeignKey(
        "PessoaFisica", verbose_name="Pessoa Física", on_delete=models.CASCADE
    )
    capacidade = models.ForeignKey(
        "Capacidade", null=True, blank=True, on_delete=models.CASCADE
    )
    incapacidade = models.ForeignKey(
        "InCapacidade", null=True, blank=True, on_delete=models.CASCADE
    )
    curso = models.ManyToManyField("Curso")
    matricula = models.IntegerField(
        unique=True, blank=True, verbose_name="Matrícula", help_text="Apenas números"
    )
    matricula_origem = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Matrícula de Origem"
    )
    numero_cartao_ponto = models.IntegerField(
        null=True, blank=True, verbose_name="N° Cartão de Ponto"
    )
    classificacao = models.IntegerField(
        verbose_name="Classificação", null=True, blank=True
    )
    data_registro = models.DateField(auto_now_add=True, null=True, blank=True)
    vpi = models.DecimalField(max_digits=18, decimal_places=2, blank=True, default=0)
    # TODO: Este campo deve ser inicializado no ato do exercício com a mesma data do exercício
    # TODO: e deve-se verificar todas as formas legais que podem alterar essa data
    # TODO: Ex.: licença para interesses particulares, licenças não remuneradas, etc
    data_referencia_ferias = models.DateField(null=True, blank=True)
    tipo = models.CharField(default="S", max_length=1, blank=True, choices=INDICATIVO)
    type_by_possession = models.CharField(
        default="EFE",
        max_length=5,
        blank=True,
        choices=Choice.get_choices_for(
            "rh", "CLASSIF_EMPLOYEE_BY_POSSESSION", char_field=True
        ),
        verbose_name="Tipo do Servidor",
    )
    ativo = models.BooleanField(default=False, blank=True)
    notificacoes = generic.GenericRelation(
        Notification, content_type_field="target_ct", object_id_field="target_id"
    )
    molestia = models.OneToOneField(
        "Molestia",
        null=True,
        blank=True,
        verbose_name="Moléstia",
        on_delete=models.CASCADE,
    )
    lotacoes = models.ManyToManyField("rh.Lotacao", through="rh.ServidorLotacao")
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    chefe_imediato = models.ForeignKey(
        "rh.Servidor",
        on_delete=models.CASCADE,
        verbose_name="Chefe imediato",
        null=True,
        blank=True,
        related_name="subordinados",
    )
    situacao_funcional_cache = models.CharField(
        max_length=40, default="NOT_FOUND", choices=list(SITUACAO_FUNCIONAL.items())
    )
    categoria_cache = models.CharField(max_length=200, blank=True)
    bond = models.BooleanField(default=False, blank=True, verbose_name="Cria Vínculo?")
    social_securities = models.ManyToManyField(
        SocialSecurityConfig, through="SocialSecurityEmployee"
    )
    public_service_entry = models.DateField(
        "Data de entrada no serviço público", null=True, blank=True
    )
    stay_allowance = models.DateField(
        "Data de vigência de abono de permanência", null=True, blank=True
    )
    founder_employee = models.ForeignKey(
        "Servidor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="beneficiaries",
    )
    """CNMP DADOS"""
    graduation = models.ManyToManyField(
        "GraduationCNMP", related_name="employee", verbose_name="Graduação"
    )
    improvement_and_graduate = models.ManyToManyField(
        "ImprovementAndGraduateCNMP",
        related_name="employee",
        verbose_name="Aperfeiçoamento e Pós-graduação",
    )
    published_works = models.ManyToManyField(
        "PublishedWorksCNMP",
        related_name="employee",
        verbose_name="Trabalhos publicados",
    )
    exercise_date = models.DateField(
        null=True, blank=True, verbose_name="Data Exercício"
    )
    termination_date = models.DateField(
        null=True, blank=True, verbose_name="Data Desligamento"
    )

    # deprecated
    regime_previdenciario = models.PositiveSmallIntegerField(
        default=2,
        choices=list(REGIME_PREVIDENCIARIO.items()),
        verbose_name="Regime previdenciário",
        null=True,
        blank=True,
    )
    organ_social_security = models.ForeignKey(
        "PessoaJuridica",
        on_delete=models.CASCADE,
        verbose_name="Órgão previdenciário",
        null=True,
        blank=True,
        related_name="employees_organ_social_security",
    )
    social_security = models.ForeignKey(
        SocialSecurityConfig,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="employee_social_security",
    )
    documento_digital = models.ManyToManyField(
        "DocumentoDigital", related_name="servidor", verbose_name="Documentos digitais"
    )
    event_esocial = models.PositiveIntegerField(blank=True, null=True)
    category_esocial = models.IntegerField(
        default=1,
        verbose_name="Categoria eSocial",
        choices=Choice.get_choices_for("rh", "CATEGORY_WORKER"),
    )
    quota_system = models.IntegerField(
        default=1,
        verbose_name="Regime de Cotas",
        choices=Choice.get_choices_for("rh", "QUOTA_SYSTEM_TYPE"),
    )
    posicao_concurso = models.IntegerField(
        null=True, blank=True, verbose_name="Posição no Concurso"
    )
    verificado_mastiff = models.BooleanField(
        verbose_name="Verificado no Mastiff", default=False, blank=True
    )
    id_usuario_mastiff = models.IntegerField(
        verbose_name="id do usuário mastiff", null=True, blank=True
    )

    cargo_eventual = models.ForeignKey(
        "diarias.CargoDiarias",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Cargo Colaborador Eventual",
        related_name="colaborador_eventual",
    )

    objects = ServidorQueryset.as_manager()

    class Meta:
        verbose_name = "Servidor"
        ordering = ("pessoa_fisica__nome", "pessoa_fisica__cpf", "matricula")

    def __str__(self):
        return "{matricula} : {nome}".format(
            nome=self.pessoa_fisica.nome,
            matricula=(
                self.matricula if self.matricula is not None else self.matricula_origem
            ),
        )

    @staticmethod
    def como_label_value(queryset):
        return queryset.annotate(
            label=Concat(
                "matricula",
                Value(": "),
                "pessoa_fisica__nome",
                output_field=models.CharField(),
            ),
            value=F("pk"),
        ).values("label", "value")

    def validate_unique_cpf(self):
        """
        Quando MANY_EMPLOYEE_ACTIVE_SAME_PERSON == True, ou seja, quando estiver permitido que se crie
        múltiplos employee ativo para o mesmo CPF é necessário fazer validação para não permitir criar o
        employee com o mesmo tipo de servidor ativo
        """
        if settings.MANY_EMPLOYEE_ACTIVE_SAME_PERSON:

            type_by_possession_to_find = self.type_by_possession
            tipo_to_find = self.tipo
            if self.tipo in ["T", "X", "A", "V"]:
                types_colaborator = {
                    "T": "TCR",  # TERCEIRIZADO
                    "X": "EXT",  # EXTERNO SEM VÍNVULO
                    "A": "JCA",  # JOVEM CIDADÃO - APRENDIZ
                    "V": "VOL",  # VOLUNTÁRIO
                }
                type_by_possession_to_find = types_colaborator[self.tipo]
            elif self.type_by_possession == "MBR" and self.tipo == "S":
                tipo_to_find = "M"
            elif (
                self.type_by_possession == "SAP"
                and self.tipo == "S"
                or self.type_by_possession == "MAP"
                and self.tipo == "S"
            ):
                tipo_to_find = "O"

            query = Servidor.objects.filter(
                pessoa_fisica__cpf=self.pessoa_fisica.cpf,
                type_by_possession__in=[type_by_possession_to_find],
                tipo__in=[tipo_to_find],
                ativo=True,
            )

            exception_msg = "Existe uma matrícula ativa com este tipo de servidor para este CPF informado."
        else:
            query = Servidor.objects.filter(
                pessoa_fisica__cpf=self.pessoa_fisica.cpf, ativo=True
            )

            exception_msg = "Existe uma matrícula ativa para este CPF informado."

        if query.exists() and not self.pk:
            raise Exception(exception_msg)

    def validate_type_by_possession_presence(self):
        if not self.type_by_possession:
            raise Exception("Por favor preencha o Tipo de Servidor.")

    def validate_type_by_possession(self):
        if self.type_by_possession_validate:
            diff = self.diff
            if (
                "type_by_possession" in diff
                and len(diff.get("type_by_possession")) > 1
                and diff.get("type_by_possession")[0] != "XXX"
                and self.posses.exists()
            ):
                raise Exception(
                    "Para modificar o Tipo do Servidor é necessário apagar os provimentos."
                )
        return True

    def validate_type_by_possession_change(self):
        servidor = Servidor.objects.get(pk=self.pk)
        if servidor.type_by_possession != self.type_by_possession:
            raise Exception("Não é permitido alterar Tipo de Servidor")

    def validate(self):
        self.validate_unique_cpf()
        self.validate_type_by_possession_presence()
        # self.validate_type_by_possession()

        if self.pk:
            if not self.__class__.objects.filter(
                pk=self.pk, pessoa_fisica=self.pessoa_fisica
            ).exists():
                raise Exception("Não é possível alterar Pessoa Física")
        elif settings.MANY_EMPLOYEE_ACTIVE_SAME_PERSON is False:
            self.pessoa_fisica.validate_has_employee_possession()

        if not self.matricula:
            message = """Uma matrícula precisa ser informada ou o módulo de geração automática de matricula deve ser ativado(Solicite à TI
                nesse caso)!"""
            raise Exception(message)
        return True

    @property
    def name(self):
        return self.pessoa_fisica.nome

    @property
    def office(self):
        job_position = self.job_position()
        if job_position:
            return job_position.cargo.nome
        return None

    @property
    def auto_registration_class(self):
        slug = settings.CLASSCODE_AUTO_REGISTRATION_NUMBER_SLUG
        ccode = ClassCode.objects.filter(typeof="REGISTRATION", slug=slug).first()
        if ccode:
            return ccode.cls(self.type_by_possession)
        return None

    @property
    def is_bond(self):
        return self.posses_ativas.filter(bond=True).exists()

    @property
    def is_teletrabalho_bloqueado(self):
        return MovimentacaoTeletrabalho.objects.filter(
            servidor=self, situacao=STATUS_TELETRABALHO_BLOQUEADO
        ).exists()

    @property
    def ultimo_teletrabalho_revogado(self):
        ultimo_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            servidor=self
        ).last()
        if (
            ultimo_teletrabalho
            and ultimo_teletrabalho.situacao == STATUS_TELETRABALHO_REVOGADO
        ):
            return True
        return False

    def afastamento_mes_str(self, data_inicio_mes, data_fim_mes):
        from rh.afastamento.models import BaseLicencaAfastamento

        afastamentos = BaseLicencaAfastamento.objects.filter(
            Q(data_inicio__lte=data_fim_mes)
            & Q(servidor=self)
            & Q(data_fim__gte=data_inicio_mes)
        ).exclude(estado__in=[CANCELED])
        tipo_afastamento = ""
        afastamentos_str = []
        for afastamento in afastamentos:
            situacao = afastamento.situation_unicode
            data_inicio_afastamento = afastamento.data_inicio
            data_fim_afastamento = afastamento.data_fim
            if data_fim_afastamento:
                afastamento_str = f"{situacao} de {data_inicio_afastamento.strftime('%d/%m/%Y')} a {data_fim_afastamento.strftime('%d/%m/%Y')}"
            else:
                afastamento_str = (
                    f"{situacao} de {data_inicio_afastamento.strftime('%d/%m/%Y')}"
                )
            afastamentos_str.append(afastamento_str)
        tipo_afastamento = ", ".join(afastamentos_str)
        return tipo_afastamento

    def save(self, *args, **kargs):
        try:
            self.type_by_possession_validate = True
            if "type_by_possession_validate" in kargs:
                self.type_by_possession_validate = kargs.pop(
                    "type_by_possession_validate"
                )

            if not self.pk and not self.type_by_possession:
                raise Exception(
                    "Favor preencher o campo Tipo de Servidor na aba Dados Funcionais"
                )

            if not self.categoria_cache:
                self.categoria_cache = "XXX"

            if not self.matricula and self.auto_registration_class:
                self.matricula = self.auto_registration_class.next_registration_number()

            if self.type_by_possession != "COE":
                self.ativo = self.is_ativo()
            self.bond = self.is_bond

            self.exercise_date = self.data_exercicio
            self.termination_date = self.data_desligamento
            ssc = self.get_socialsecurity_by_validity()
            if ssc:
                self.regime_previdenciario = ssc.regime
                self.organ_social_security = ssc.organ
                self.social_security = ssc

            self.set_category_esocial()

            self.validate()

            super(Servidor, self).save(*args, **kargs)
            if not self.user:
                set_employee_user(self)
            if not self.user and (
                settings.AUTO_PERMISSIONS_GROUPS or settings.AUTO_PERMISSIONS_FUNCS
            ):
                self.create_new_user()

                if settings.AUTO_PERMISSIONS_GROUPS:
                    assign_group_permission(self.user)

                if settings.AUTO_PERMISSIONS_FUNCS:
                    assign_func_permission(self.user)

            if not self.grupos_permissao.exists():
                vincular_grupo_permissao_padrao(self)

        except Exception as err:
            log.exception(err)
            raise err

    def set_category_esocial(self):
        if self.type_by_possession == "CMS":
            self.category_esocial = 302
        elif self.type_by_possession == "EST":
            self.category_esocial = 901
        elif self.type_by_possession in ("REQ", "RCM", "RFC", "REX"):
            self.category_esocial = 410
        elif self.type_by_possession in (
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
            "MAP",
            "SAP",
        ):
            self.category_esocial = 301
        elif self.category_esocial == 1 and self.type_by_possession == "COE":
            ssc = self.get_socialsecurity_by_validity()
            if ssc and ssc.regime == 1:
                self.category_esocial = 701
            elif ssc and ssc.regime in (2, 3):
                self.category_esocial = 313

    @classmethod
    def with_job_position(klass, job_position):
        query = klass.objects.filter(
            movimentacaopessoal__movimentacaoposse__ativo=True,
            movimentacaopessoal__movimentacaoposse__quadro__cargo=job_position,
        )

        return query

    @classmethod
    def with_job_position_for_distribution(klass, job_position):
        query = klass.objects.filter(
            movimentacaopessoal__movimentacaoposse__ativo=True,
            movimentacaopessoal__movimentacaoposse__quadro__cargo=job_position,
            movimentacaopessoal__movimentacaoposse__out_off_distribution_list=False,
        )

        return query

    @classmethod
    def from_user(klass, user, ignore_ativo=False, ativo=True):
        query = (
            klass.objects.filter()
            if ignore_ativo
            else klass.objects.filter(ativo=ativo)
        ).filter(user=user)
        return query.latest("pk") if query.exists() else None

    def create_new_user(self):
        username_type = getattr(settings, "USERNAME_TYPE", "")

        username = create_username(self.pessoa_fisica.nome, username_type)
        username = f"{self.current_time()}{username}"

        if username:
            try:
                user = User.objects.create_user(username=username)
                user.is_active = True

                self.user = user
                self.save()

            except Exception as e:
                log.exception(e)
                raise e
        else:
            raise Exception("Ocorreu um erro ao criar o usuário.")

    def current_time(self, string_time="%Y%m%d%H%M%S"):
        now = datetime.now()
        time = now.strftime(string_time)
        return time

    @classmethod
    def unlink_user(klass, user):
        """
        Optou-se por fazer de modo unitário para poder disparar os sinais que existam
        eventualmente para servidor.
        """
        for obj in klass.objects.filter(user=user):
            obj.user = None
            obj.save()

    def link_user(self, user):
        self.user = user
        self.save()

    @property
    def member_substitute(self):
        """
        Property que retorna se o Servidor é um 'PROMOTOR DE JUSTICA SUBSTITUTO' ativo
        """
        return self.movimentacaopessoal_set.filter(
            Q(
                Q(
                    movimentacaoposse__quadro__cargo__nome__icontains="PROMOTOR DE JUSTICA SUBSTITUTO"
                )
                | Q(
                    movimentacaoposse__quadro__cargo__nome__icontains="PROMOTOR DE JUSTIÇA SUBSTITUTO"
                )
            ),
            movimentacaoposse__ativo=True,
        ).exists()

    @property
    def requested(self):
        return self.is_requested()

    def is_requested(self):
        return self.type_by_possession in ("RCM", "REQ", "RFC", "REX")

    @deprecated
    def get_is_requested(self, start_date=None, end_date=None):
        return self.get_requestmove_at(start_date, end_date).exists()

    def get_requestmove_at(self, start_date=None, end_date=None):
        start_date = datetime.now().date() if not start_date else start_date
        end_date = start_date if not end_date or end_date < start_date else end_date
        periods = PeriodoRequisicao.objects.filter(request_move__servidor=self).exclude(
            Q(data_inicio__gt=end_date)
            | (Q(data_fim__isnull=False) & Q(data_fim__lt=start_date))
        )
        return RequestMove.objects.filter(pk__in=(p.request_move.pk for p in periods))

    @property
    def general_protocol(self):
        return self.work_locations.filter(acesso_protocolo_geral=True)

    def workload(self, date=None):
        date = date if date else datetime.now().date()
        return self.cargahoraria_set.currents_in(data=date)

    @classmethod
    def has_perm(cls, app_label, permissions=None):
        query = []

        if permissions is not None:
            query = Servidor.objects.filter(
                Q(user__user_permissions__content_type__app_label=app_label)
                | Q(
                    user__groups__permissions__content_type__app_label=app_label,
                )
            ).distinct()
        elif isinstance(permissions, (list, set, tuple)) is True:
            query = Servidor.objects.filter(
                Q(
                    user__user_permissions__content_type__app_label=app_label,
                    user__user_permissions__codename__in=permissions,
                )
                | Q(
                    user__groups__permissions__content_type__app_label=app_label,
                    user__groups__permissions__codename__in=permissions,
                )
            ).distinct()
        elif isinstance(permissions, str) is True:
            query = Servidor.objects.filter(
                Q(
                    user__user_permissions__content_type__app_label=app_label,
                    user__user_permissions__codename__in=permissions,
                )
                | Q(
                    user__groups__permissions__content_type__app_label=app_label,
                    user__groups__permissions__codename__in=permissions,
                )
            ).distinct()
        return query

    @classmethod
    def employees_departured(cls, date=None):
        from rh.afastamento.models import BaseLicencaAfastamento

        return Servidor.objects.filter(
            pk__in=BaseLicencaAfastamento._raw_employee_departures(date=date).values(
                "servidor"
            )
        )

    @classmethod
    def employee_with_exercises(cls, date=None):
        """
        :py:function:: employee_with_exercises(cls, date=None)

        This method returns all Servidor with exercises.

        :param date date: Date to determine a period of EmployeeWorkplace
        :return: queryset of Employee
        """
        date = date if date else datetime.now().date()
        return Servidor.objects.filter(
            pk__in=ServidorLotacao.objects.filter(
                Q(designacao=True)
                & Q(data_vigencia_inicio__lte=date)
                & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
            ).values("servidor")
        )

    def _raw_locations(self, date=None, active=None, option=None):
        """
        :py:function:: _raw_locations(self, date=None, active=None, option=None)

        This method returns a queryset of the all EmployeeWorkplace.

        :param date date: Date to determine a period of EmployeeWorkplace
        :param boolean active: active array
        :param int option: Option param defines which designations to return:
            -WORKPLACE: 1 - Workplace;
            -WORK_ASSIGNMENT: 2 - Work Assignment;
            -None - Those above, DEFAULT.
        :return: queryset of EmployeeWorkplace
        """
        query = self.servidor_lotacao.filter(servidor=self)
        if date:
            query = query.filter(
                Q(data_vigencia_inicio__lte=date)
                & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
            )

        if option == WORKPLACE:
            query = query.filter(designacao=False)
        elif option == WORK_ASSIGNMENT:
            query = query.filter(designacao=True)

        if active is not None:
            query = query.filter(ativo=active)

        return query.order_by("-data_vigencia_inicio")

    def get_workplace_only(self, date=None):
        """
        :py:function:: get_workplace_only(self, date=None)

        This method returns all employee workplaces.
        Default date is None.

        :param date: date
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        return self._raw_locations(date=date, option=WORKPLACE)

    @property
    def workplace_only_active(self):
        """
        :py:function:: workplace_only(self)

        This method returns employee workplaces active ONLY.
        Default date is datetime.now().date().

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        return self.get_workplace_only(date=datetime.now().date())

    @property
    def workplace_only(self):
        """
        :py:function:: workplace_only(self)

        This method returns all employee workplaces active.
        Default date is None.

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        return self.get_workplace_only(date=None)

    def get_workplace(self, date=None):
        """
        :py:function:: get_workplace(self)

        This method returns all employee workplaces.
        The workplace may have a work assignment active.
        Default date is datetime.now().

        :param date: date
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        workplace = self._raw_locations(date=date, option=WORKPLACE).filter(
            Q(father_of__data_vigencia_inicio__lte=date)
            & (
                Q(father_of__data_vigencia_fim__gte=date)
                | Q(father_of__data_vigencia_fim=None)
            )
        )
        return workplace

    def get_workplace_departured(self, date=None):
        """
        :py:function:: get_workplace_departured(self, date=None)

        This method returns all employee workplaces.
        The workplace may have a work assignment active at period of the departure.
        The workplace may have belong to a work_assignment departured.
        Default date is datetime.now().

        :param date: date
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        workplace = (
            self._raw_locations(date=date, option=WORKPLACE)
            .filter(
                Q(father_of__data_vigencia_fim__lte=date)
                & ~Q(father_of__changed_by_departure=None)
            )
            .distinct()
        )
        return workplace

    @property
    def workplace(self):
        """
        :py:function:: workplace(self)

        This method returns all employee workplaces.
        The workplace may have a work assignment active.
        Default date is datetime.now().

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        return self.get_workplace(date=datetime.now().date())

    def get_work_assignment(self, date=None):
        """
        :py:function:: get_work_assignment(self)

        This method returns all employee work assignments.
        Default date is None and returns all employee work assignments.

        :param date: date
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        return self._raw_locations(date=date, option=WORK_ASSIGNMENT)

    def get_work_assignment_departured(self, date=None):
        """
        :py:function:: get_work_assignment_departured(self, date=None)

        This method returns all employee work assignments.
        The work assignment should be changed by a departure.
        Uses the method BaseLicencaAfastamento.find_departure_concatenated to catch
        departures in a period.

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        departures = self.departures(start_date=date).exclude(
            ~Q(desempenhofuncao=None) | ~Q(atuacaogrupotrabalho=None)
        )
        if departures.exists():
            departures = [
                dep.pk
                for dep in departures.latest(
                    "data_inicio"
                ).find_departure_concatenated()
            ]
        return self.get_work_assignment().filter(
            changed_by_departure__pk__in=departures
        )

    @deprecated
    def owner_locations_changed_by_departure(self, departure):
        """
        :py:function:: owner_locations_changed_by_departure(self, departure)

        This method returns all employee work assignments changed by departure parameter.
        Uses the method BaseLicencaAfastamento.find_departure_concatenated to catch
        departures in a period.

        :param: BaseLicencaAfastamento, departure
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        departures = [dep.pk for dep in departure.find_departure_concatenated()]
        return self.get_work_assignment().filter(
            changed_by_departure__pk__in=departures
        )

    def work_assignments_changed_by_departure(self, departure):
        """
        :py:function:: work_assignments_changed_by_departure(self, departure)

        This method returns all employee work assignments changed by departure parameter.
        Uses the method BaseLicencaAfastamento.find_departure_concatenated to catch
        departures in a period.

        :param: BaseLicencaAfastamento, departure
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        departures = [dep.pk for dep in departure.find_departure_concatenated()]
        return self.get_work_assignment().filter(
            changed_by_departure__pk__in=departures
        )

    @property
    def work_assignment_effective_exercise(self):
        """
        :py:function:: work_assignment_effective_exercise(self)

        This method returns all employee work assignments in effective exercise.

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        empl_workplaces = []
        query = self.work_assignment
        for workplace in query:
            empl_workplaces.append(workplace.pk)

        query = self.get_work_assignment_departured().exclude(
            ~Q(changed_by_departure__desempenhofuncao=None)
            | ~Q(changed_by_departure__atuacaogrupotrabalho=None)
        )
        for workplace in query:
            empl_workplaces.append(workplace.pk)

        return ServidorLotacao.objects.filter(pk__in=empl_workplaces)

    @property
    def work_locations_effective_exercise(self):
        """
        :py:function:: work_locations_effective_exercise(self)

        This method returns all Workplace where is effective exercise.
        Uses work assignments in effective exercise.

        :return: queryset, Lotacao
        :rtype: queryset
        """
        workplaces = (
            wk.get("lotacao__pk")
            for wk in self.work_assignment_effective_exercise.values("lotacao__pk")
        )
        return Lotacao.objects.filter(pk__in=workplaces)

    @property
    def work_assignment(self):
        """
        :py:function:: work_assignment(self)

        This method returns all employee work assignments.
        In default returns today employee work assignments.

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date()
        return self.get_work_assignment(date=date)

    @property
    def work_locations(self):
        """
        :py:function:: work_locations(self)

        This method returns all workplaces based on Servidor.work_assignment.

        :return: queryset, Lotacao
        :rtype: queryset
        """
        return Lotacao.objects.filter(
            pk__in=(wk.get("lotacao") for wk in self.work_assignment.values("lotacao"))
        )

    def workplace_by_date(self, date=None):
        """
        :py:function:: workplace_by_date(self, date=None)

        This method returns the Workplace found per date.
        For employee finds first the work_assignment. If not found, gets workplace.
        In case of a member finds first the workplace. If not found, gets work_assignment.
        If no one is found, returns None.

        :param date date: date
        :return: Workplace
        :rtype: Workplace
        """
        date = datetime.now().date() if not date else date
        workplace = None
        if self.tipo != "M":
            workplace = self._workplace_by_date_employee(date=date)
        else:
            workplace = self._workplace_by_date_member(date=date, main=True)
            if not workplace:
                workplace = self._workplace_by_date_member(date=date, main=False)
        return workplace

    def _workplace_by_date_employee(self, date, main=False):
        workplace = None
        work_assignment = self.get_work_assignment(date=date).filter(
            commission=False, main=False
        )
        workplace_only = self.get_workplace_only(date=date).filter(main=False)
        if work_assignment.exists():
            workplace = work_assignment.latest("data_vigencia_inicio").lotacao

        elif workplace_only.exists():
            workplace = workplace_only.latest("data_vigencia_inicio").lotacao

        elif self.work_locations_effective_exercise.exists():
            workplace = self.work_locations_effective_exercise.last()

        return workplace

    def _workplace_by_date_member(self, date, main=False):
        workplace = None
        work_assignment = self.get_work_assignment(date=date).filter(
            commission=False, main=main
        )
        workplace_only = self.get_workplace_only(date=date).filter(main=main)
        if workplace_only.filter(
            lotacao__pk__in=work_assignment.values("lotacao")
        ).exists():
            """LOTAÇÃO DO LOCAL ONDE POSSUI EXERCÍCIO"""
            workplace = (
                workplace_only.filter(lotacao__pk__in=work_assignment.values("lotacao"))
                .latest("data_vigencia_inicio")
                .lotacao
            )
        elif workplace_only.exists() and not work_assignment.exists():
            """LOTAÇÃO somente"""
            workplace = workplace_only.latest("data_vigencia_inicio").lotacao
        elif work_assignment.filter(responsible=True).exists():
            """EXERCÍCIO ONDE É RESPONSÁVEL"""
            workplace = (
                work_assignment.filter(responsible=True)
                .latest("data_vigencia_inicio")
                .lotacao
            )
        elif work_assignment.exists():
            """EXERCÍCIO somente"""
            workplace = work_assignment.latest("data_vigencia_inicio").lotacao
        # else:
        #     log.info('Servidor %s não tem uma lotação ativa para o momento.' % self)
        return workplace

    @property
    def workplace_current(self):
        """
        :py:function:: workplace_current(self)

        This method returns the Workplace current. Default date today.

        :return: Workplace
        :rtype: Workplace
        """
        return self.workplace_by_date()

    def responsible(self, date=None):
        """
        :py:function:: responsible(self, date=None)

        This method returns a queryset of the EmployeeWorkplace if responsible is True.

        :param date date: date
        :return: queryset of EmployeeWorkplace
        """
        return self.work_assignment.filter(responsible=True)

    def _check_owner_location(self, employee_workplace=None):
        """
        :py:function:: _check_owner_location(self, employee_workplace=None)

        This method returns True when employee is owner of JobPosition and Workplace.
        Employee is owner through JobPosition.

        :param EmployeeWorkplace employee_workplace: employee_workplace
        :return: boolean
        """
        query = self.posses_ativas.filter(
            quadro__cargo__lotacao_responsavel=employee_workplace.lotacao
        ).assets_in(
            range=NewDateRange(
                employee_workplace.data_vigencia_inicio,
                employee_workplace.data_vigencia_fim,
            )
        )
        return query.exists()

    def get_owner_locations_can_substitute(self, date=None):
        """
        :py:function:: get_owner_locations_can_substitute(self, date=None)

        This method returns a EmployeeWorkplace.queryset where the member can be sustituted.

        :param date date: date
        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        empl_workplaces = []
        if self.member_type_by_possession:
            query = self.owner_locations
            for workplace in query:
                empl_workplaces.append(workplace.pk)

            query = self.get_work_assignment_departured().filter(owner=True)
            for workplace in query:
                empl_workplaces.append(workplace.pk)
        else:
            empl_workplaces = self.work_assignment.filter(
                lotacao__in=self.responsavel_por.filter()
            )
        return ServidorLotacao.objects.filter(pk__in=empl_workplaces)

    @property
    def owner_locations_can_substitute(self):
        """
        :py:function:: owner_locations_can_substitute(self)

        Property hook for method get_owner_locations_can_substitute.
        Returns a EmployeeWorkplace.queryset where the member can be sustituted.

        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        return self.get_owner_locations_can_substitute()

    def get_owner_locations(self, date=None):
        """
        :py:function:: get_owner_locations(self, date=None)

        This method returns a Workplace.queryset when employee has a Workplace.owner True.
        Property hook for method get_owner_locations.

        :param date date: date
        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        return self._raw_locations(date=date).filter(owner=True)

    @property
    def owner_locations(self):
        """
        :py:function:: owner_locations(self)

        This method returns a EmployeeWorkplace.queryset where Cargo is owner.
        Property hook for method get_owner_locations.

        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        return self.get_owner_locations(date=datetime.now().date())

    def get_owner_location_workplace(self, date=None):
        """
        :py:function:: get_owner_location_workplace(self)

        This method returns a Workplace.queryset when employee has a Workplace.owner True.
        Property hook for method get_owner_locations.

        :param date date: date
        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        return Lotacao.objects.filter(
            pk__in=(
                pk
                for pk in self.get_owner_locations(date=date).values_list(
                    "lotacao__pk", flat=True
                )
            )
        )

    def get_owner_location_workplace_from_workassignment(self, date=None):
        """
        :py:function:: get_owner_location_workplace_from_workassignment(self)

        This method returns a Workplace.queryset when employee has a (WorkAssignment)Workplace.owner True.
        Property hook for method get_owner_locations.

        :param date date: date
        :return: queryset of EmployeeWorkplace
        :rtype: queryset
        """
        return Lotacao.objects.filter(
            pk__in=(
                pk
                for pk in self._raw_locations(date=date, option=WORK_ASSIGNMENT)
                .filter(owner=True)
                .values_list("lotacao__pk", flat=True)
            )
        )

    def substitutions_per_date(self, start_date=None, end_date=None):
        """
        :py:function:: substitutions_per_date(self)

        This method returns employee's substitutions.

        :return: querydict of MovimentacaoSubstituicao
        """
        start_date = datetime.now().date() if not start_date else start_date
        end_date = start_date if not end_date or end_date < start_date else end_date
        return MovimentacaoSubstituicao.objects.filter(
            pk__in=self.movimentacaopessoal_set.filter(
                Q(movimentacaosubstituicao__data_inicio__lte=end_date)
                & (
                    Q(movimentacaosubstituicao__data_fim__gte=start_date)
                    | Q(movimentacaosubstituicao__data_fim=None)
                )
            ).values("pk")
        )

    def substitutions(self, job_position=None, date=None):
        """
        :py:function:: substitutions(self)

        This method searchs for substitutions that match a job_position. In case of member,
        the field lotacao_responsavel must match with his workplace.
        Always considering date.

        :param: Cargo job_position
        :param: date date
        :return: queryset MovimentacaoSubstituicao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        substitutions_list = []
        query = Q(servidor_substituido=self) & Q(
            Q(data_inicio__lte=date) & (Q(data_fim=None) | Q(data_fim__gte=date))
        )
        possessions = self.posses.filter(
            Q(data_exercicio__lte=date)
            & (Q(data_desligamento=None) | Q(data_desligamento__gte=date))
        )
        if job_position:
            possessions = possessions.filter(quadro__cargo=job_position)
        for possesion in possessions:
            if not self.member_type_by_possession:
                substitutions = MovimentacaoSubstituicao.objects.filter(query)
                if job_position:
                    substitutions = substitutions.filter(posse=job_position)
            else:
                substitutions = MovimentacaoSubstituicaoMembro.objects.filter(query)
                if job_position:
                    substitutions = substitutions.filter(
                        Q(
                            designation_substituted__lotacao=job_position.lotacao_responsavel
                        )
                    )
            [
                substitutions_list.append(substituition)
                for substituition in substitutions
            ]
        return MovimentacaoSubstituicao.objects.filter(pk__in=substitutions_list)

    def work_assignment_from_departure(self, departure):
        """
        :py:function:: work_assignment_from_departure(self, departure)

        This property gives work assignments that matches active through the departure.
        Disregarding those are in MovimentacaoSubstituicaoMembro or InativacaoCargoMembro.

        :param: BaseLicencaAfastamento departure
        :return: queryset EmployeeWorkplace
        :rtype: queryset
        """
        employee_workplace = self.get_work_assignment().filter(
            Q(data_vigencia_fim__gte=departure.data_inicio)
            | Q(data_vigencia_fim=None)
            | Q(changed_by_departure=departure)
        )
        if departure.data_fim:
            employee_workplace = employee_workplace.exclude(
                data_vigencia_inicio__gt=departure.data_fim
            )
        return employee_workplace

    def _get_sms(self):
        sms = ""
        if self.pessoa_fisica.phone.filter(tipo_telefone=3):
            sms = self.pessoa_fisica.phone.filter(tipo_telefone=3)[0].numero
        return sms

    numero_sms = property(_get_sms)

    def _get_posses(self, ativas=False):
        posses = MovimentacaoPosse.objects.filter(
            servidor__matricula__exact=self.matricula
        )
        # TODO: promover verificação dos cargos_lei tipo AC

        # posses = MovimentacaoPosse.objects.filter(servidor__matricula__exact=self.matricula).exclude(
        #     quadro__cargo__tipo_lei_cargo='AC',
        #     movimentacaopessoal_ptr__my_type='movimentacaoposse'
        # )
        if ativas:
            posses = posses.filter(ativo=True)
        return posses.order_by("data_exercicio")

    def _get_posses_ativas(self):
        return self.get_posses_ativas()

    def get_posses_ativas(self, data_inicio=None, data_fim=None):
        data_inicio = datetime.now().date() if not data_inicio else data_inicio
        if data_fim is None:
            data_fim = data_inicio
        return (
            self._get_posses()
            .exclude(
                Q(data_exercicio__gt=data_fim)
                | Q(
                    ~Q(desligamento=None)
                    & Q(desligamento__data_desligamento__lte=data_inicio)
                )
            )
            .exclude(data_exercicio=None)
            .order_by("-data_exercicio")
        )

    @property
    def last_possession(self, main=True):
        possessions = self._get_posses().only_original()
        if main:
            p = possessions.order_by("data_exercicio")
            pm = p.filter(quadro__cargo__tipo_lei_cargo__in=["EF", "AC"])
            ps = p.filter(quadro__cargo__tipo_lei_cargo__in=["CM", "FC"])
            return pm.last() if pm.exists() else ps.last()
        return possessions.last()

    @deprecated
    def get_declarationactivity(self, date=None):
        """
        :py:function:: get_declarationactivity(self)

        This method returns the MovimentacaoPessoal of the DeclaracaoAtividade.
        Default date_start and date_end set today.

        :param date date:
        :return: Workplace
        :rtype: Workplace
        """
        if self.tipo == "O":
            # Se for APOSENTADO
            # query = self.movimentacaopessoal_set.filter(declarationactivityretiree__isnull=False)
            # if date:
            #     query = query.filter(
            #         Q(declarationactivityretiree__data_inicio__lte=date) & (
            #             Q(declarationactivityretiree__data_encerramento__gte=date) | Q(declarationactivityretiree__data_encerramento=None)
            #         )
            #     )
            pass
        else:
            query = self.movimentacaopessoal_set.filter(
                declaracaoatividade__isnull=False
            )
            if date:
                query = query.filter(
                    Q(declaracaoatividade__data_exercicio__lte=date)
                    & (
                        Q(declaracaoatividade__data_encerramento__gte=date)
                        | Q(declaracaoatividade__data_encerramento=None)
                    )
                )
        return query

    def job_position(self, date=None):
        """
        :py:function:: job_position(self, date=None)

        This method returns unicode representation of MovimentacaoPosse.quadro.
        Utilize date param to determine which possession choose.

        :param date date: date default is datetime.now().date()
        :return: unicode of MovimentacaoPosse.quadro or None
        :rtype: unicode
        """
        possessions = self.get_posses_ativas(data_inicio=date)
        job_position = None
        if possessions.exists():
            possession = possessions.latest("data_exercicio")
            job_position = possession.quadro
            if not possession.quadro:
                job_position = possession.description_possession
        return job_position

    @property
    def data_exercicio(self):
        # TODO: AVALIAR se para, REINTEGRADO E RECONDUZIDO, a data de exercício será a de origem
        date_exercise = None
        posses = self.posses
        # query = mr.servidor.posses_ativas.exclude(quadro__cargo__tipo_lei_cargo='AC')
        # if not query.exists():
        #     print(mr.servidor.exercise_date, mr.servidor.termination_date, mr.servidor)
        # FIXME: CONVERSAR COM RAYSON E RAINE SOBRE IMPACTO NA FOLHA`
        # if self.type_by_possession in ('REQ', 'RCM', 'RFC', 'REX'):
        #     mr = MovimentacaoRequisicao.objects.filter(servidor=self)
        #     date_exercise = mr.filter(
        #         pk=mr.filter(servidor=self).order_by('data_inicio').last()
        #     ).aggregate(data_inicio=Min('data_inicio'))['data_inicio']
        # XXX: MPMT Observar o comportamento
        # if self.type_by_possession in ('REQ', 'RCM', 'RFC', 'REX'):
        #     posses = posses.filter(requestmove__isnull=False)

        if posses.exists():
            date_exercise = posses.aggregate(data_exercicio=Min("data_exercicio"))[
                "data_exercicio"
            ]
        return date_exercise

    @property
    def dismissal_date(self):
        dt = None
        posses = self.posses
        # FIXME: CONVERSAR COM RAYSON E RAINE SOBRE IMPACTO NA FOLHA`
        # if self.type_by_possession in ('REQ', 'RCM', 'RFC', 'REX'):
        #     mr = MovimentacaoRequisicao.objects.filter(servidor=self)
        #     dt = mr.filter(
        #         pk=mr.filter(servidor=self).order_by('data_inicio').last()
        #     ).aggregate(data_fim=Min('data_fim'))['data_fim']
        #     if dt:
        #         dt += timedelta(days=1)
        # XXX: MPMT Observar o comportamento
        # if self.type_by_possession in ('REQ', 'RCM', 'RFC', 'REX'):
        #     posses = posses.filter(requestmove__isnull=False)
        if posses.exists():
            dt = (
                None
                if posses.filter(data_desligamento=None)
                else posses.aggregate(data_desligamento=Max("data_desligamento"))[
                    "data_desligamento"
                ]
            )
        return dt

    @property
    def data_desligamento(self):
        return self.dismissal_date

    @property
    def last_day_worked(self):
        dismissal_date = self.dismissal_date
        return (dismissal_date - relativedelta(days=1)) if dismissal_date else None

    @property
    def first_possession_date(self):
        # TODO: AVALIAR se para, REINTEGRADO E RECONDUZIDO, a data de exercício será a de origem
        date = None
        posses = self.posses
        if posses.exists():
            date = posses.aggregate(data_posse=Min("data_posse"))["data_posse"]
        return date

    def _get_servidor_ativo(self):
        return self.posses_ativas.count() > 0

    # TODO: Verificar, de acordo com a legalidade, em que momentos e quais situações
    # TODO: pode-se BLOQUEAR a marcação e/ou fruição de férias
    def _get_ferias_bloqueada(self):
        return False

    def _get_indicativo(self):
        return self.tipo

    indicativo = property(_get_indicativo)

    @property
    def situacao_funcional(self):
        """
        Esta propriedade retorna situação funcional vigente em unicode.
        """
        return format_situacao_funcional(self.situacao_funcional_cache)

    @ilru_cache()
    def get_afastamentos(self, start_date=None, end_date=None):
        """
        :py:function:: get_afastamentos(self, start_date=None, end_date=None)

        This method returns all departures based on start_date and end_date.
        If end_date is not suplied start_date is set as default end.

        :return: movimentacaopessoal.queryset
        :rtype: queryset
        """
        start_date = datetime.now().date() if not start_date else start_date
        end_date = start_date if not end_date or end_date < start_date else end_date
        return self.movimentacaopessoal_set.filter(
            Q(baselicencaafastamento__data_inicio__lte=end_date)
            & (
                Q(baselicencaafastamento__data_fim__gte=start_date)
                | Q(baselicencaafastamento__data_fim=None)
            )
        ).exclude(baselicencaafastamento__estado=CANCELED)

    @property
    def get_days_departure(self):
        """
        Função que verifica a quantidade de dias que o servidor ficou afastado
        desde a data da sua primeira posse.
        OBS: Segundo a Resolução 280/2023-CNMP, licença maternidade é considerado como efetivo exercício.

        :returns: int Quantidade em Dias de afastamentos
        """
        tipo_licenca_maternidade = 12

        departures = self.departures(
            start_date=self.first_possession_date,
            end_date=datetime.now().date(),
        )
        days_in_departure = 0
        for departure in departures:
            if departure.tipo == tipo_licenca_maternidade:
                continue
            date_end = (
                departure.data_fim
                if departure.data_fim
                else (departure.data_prevista if departure.data_prevista else None)
            )
            days_in_range = NewDateRange(departure.data_inicio, date_end)
            days_in_departure = days_in_departure + days_in_range.days
        return days_in_departure

    @property
    def get_worked_days_if_employee_be_in_probationary_phase(self):
        """
        Função que verifica se o Membro é 'PROMOTOR SUBSTITUTO' e retorna a quantidade de dias
        desde a primeira posse até a data atual (detetime.now)

        :returns: int Quantidade em dias entre o lapso da primeira posse até a data atual
        """
        worked_days_in_probationary_phase = 0
        if self.member_substitute:
            days_in_period = NewDateRange(
                self.first_possession_date, datetime.now().date()
            )
            worked_days_in_probationary_phase = (
                days_in_period.days - self.get_days_departure
            )
        return worked_days_in_probationary_phase

    def date_when_complete_the_probationary_phase(self):
        """
        Função que verifica se o Membro é 'PROMOTOR SUBSTITUTO' e retorna a data
        em que finalizará o estágio probatório

        :returns: date Data em que finalizará o estágio probatório
        """
        probationary_years = (
            Choice.objects.filter(
                app_label="rh", name="PROBATIONARY_PHASE_MEMBERS_YEARS", active=True
            )
            .first()
            .value
        )
        if self.member_substitute:
            return (
                self.first_possession_date
                + relativedelta(years=probationary_years)
                + relativedelta(days=self.get_days_departure)
                - relativedelta(days=1)
            )
        return None

    def days_for_complete_the_probationary_phase(self):
        """
        Função que verifica se o Membro é 'PROMOTOR SUBSTITUTO' e retorna a
        quantidade de dias para finalizar o estágio probatório

        :returns: int quantidade de dias para finalizar o Estágio probatório
        """
        if self.member_substitute:
            return NewDateRange(
                self.first_possession_date,
                self.date_when_complete_the_probationary_phase(),
            ).days - (
                self.get_worked_days_if_employee_be_in_probationary_phase
                + self.get_days_departure
            )
        return None

    def afastamento_ativo(self, data=None):
        """
        Verifica se existe um afastamento ativo naquela data informada.
        Não pode ser CANCELADO.
        """
        return self.get_afastamentos(data).exists()

    def departures(self, start_date=None, end_date=None):
        departures = self.get_afastamentos(start_date=start_date, end_date=end_date)
        try:
            from rh.afastamento.models import BaseLicencaAfastamento

            departures = BaseLicencaAfastamento.objects.filter(
                pk__in=departures.values("baselicencaafastamento__pk")
            )
        except Exception as err:
            log.exception(err)
        return departures

    def has_another_departure(self, date_start=None, date_end=None):
        """
        :py:function:: has_another_departure(self, date_start=None, date_end=None)

        This method verifies if exists another departure for the period suplied on the date_start and date_end parameter.
        Uses BaseLicencaAfastamento.match_date_range.

        :param: date, date_start
        :param: date, date_end
        :return: boolean, True if exists, False otherwise
        :rtype: boolean
        """
        has_another_departure = False
        try:
            from rh.afastamento.models import BaseLicencaAfastamento

            BaseLicencaAfastamento.match_date_range(
                date_start,
                date_end,
                self.departures().exclude(
                    ~Q(desempenhofuncao=None) | ~Q(atuacaogrupotrabalho=None)
                ),
            )
        except Exception:
            has_another_departure = True
        return has_another_departure

    def moved_away(self, date=None):
        return (
            self.get_afastamentos(start_date=date)
            .filter(~Q(baselicencaafastamento__afastamento__afastamentooutroorgao=None))
            .exclude(baselicencaafastamento__estado__in=[SCHEDULED, FINISHED, CANCELED])
            .exists()
        )

    @ilru_cache()
    def departures_from_date(self, start_date=None, end_date=None):
        """Este método todos afastamentos do servidor que se encaixem em start_date e end_date.
        Utiliza date como default para start_date.
        Retornará todos afastamentos a partir de start_date caso end_date.

        Args:
            start_date (date):
            end_date (date):
        Returns:
            BaseLicencaAfastamento.queryset
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        start_date = datetime.now().date() if not start_date else start_date
        q = Q(data_fim__gte=start_date) | Q(data_fim=None)
        if end_date:
            q = q & Q(data_inicio__lte=end_date)
        return (
            BaseLicencaAfastamento.objects.filter(servidor=self)
            .filter(q)
            .exclude(estado=CANCELED)
        )

    def _get_chefe_imediato(self, lotacao_inf=None):
        """
        Este método retorna o chefe imediato baseado no responsável da lotação.
        """
        SIGLAS_LOTACAO = getattr(settings, "SIGLAS_LOTACAO", None)
        if self.tipo == "M":
            if (
                SIGLAS_LOTACAO
                and "CHEFIA-MEMBROS" in SIGLAS_LOTACAO
                and SIGLAS_LOTACAO["CHEFIA-MEMBROS"]
            ):
                return Lotacao.objects.get(
                    sigla=SIGLAS_LOTACAO["CHEFIA-MEMBROS"][-1]
                ).responsavel
        lotacao = lotacao_inf
        if not lotacao_inf:
            lotacao = self.workplace_only_active
            if lotacao.exists():
                lotacao = lotacao.first().lotacao
            else:
                lotacao = None
        responsavel = None
        while lotacao and lotacao.responsavel:
            if lotacao.responsavel and lotacao.responsavel != self:
                responsavel = lotacao.responsavel
                break
            lotacao = lotacao.pai if lotacao.pai else None
        return responsavel

    @property
    def _chefe_imediato(self):
        """
        Este método retorna o chefe imediato baseado no responsável da lotação.
        """
        return self._get_chefe_imediato()

    def _get_subordinados_ids(self):
        return [s.id for s in self.subordinados.all()]

    def _get_subordinados_indiretos(self):
        if not self.responsavel_por:
            return []
        if self.member_type_by_possession:
            return []
        else:
            return []

    def is_subordinado(self, chefe):
        """
        Verifica se o servidor atual é subordinado de servidor_id
        """
        value = False
        SIGLAS_LOTACAO = getattr(settings, "SIGLAS_LOTACAO", None)
        if self == chefe:
            value = False
        elif (
            chefe.responsavel_por.filter(
                sigla__in=SIGLAS_LOTACAO["CHEFIA-MEMBROS"]
            ).count()
            > 0
        ):
            value = True
        else:
            servidor = self
            while servidor.chefe_imediato:
                if servidor.chefe_imediato == chefe:
                    value = True
                    break
                elif (
                    servidor.chefe_imediato
                    and servidor.chefe_imediato.chefe_imediato
                    and servidor.chefe_imediato
                    == servidor.chefe_imediato.chefe_imediato.chefe_imediato
                ):
                    break
                servidor = servidor.chefe_imediato
        return value

    def is_mediate_chief(self, chief):
        """Verifica se o chief(Servidor) atual é chefe mediato de self(Servidor)
        Returns:
            bool
        """
        SIGLAS_LOTACAO = getattr(settings, "SIGLAS_LOTACAO", None)
        value = False
        if self == chief:
            value = False
        elif (
            chief
            and chief.responsavel_por.filter(
                sigla__in=SIGLAS_LOTACAO["CHEFIA-MEMBROS"]
            ).count()
            > 0
        ):
            value = True
        elif self.chefe_imediato:
            employee = self.chefe_imediato
            while employee.chefe_imediato:
                if employee.chefe_imediato == chief:
                    value = True
                    break
                elif (
                    employee.chefe_imediato
                    and employee.chefe_imediato.chefe_imediato
                    and employee.chefe_imediato
                    == employee.chefe_imediato.chefe_imediato.chefe_imediato
                ):
                    break
                employee = employee.chefe_imediato
        return value

    def is_immediate_chief(self, chief):
        """Verifica se o chief(Servidor) atual é chefe imediato de self(Servidor)
        Returns:
            bool
        """
        value = False
        if self == chief:
            value = False
        elif self.chefe_imediato == chief:
            value = True
        return value

    @property
    def tipo_servidor(self):
        if self.is_efetivo:
            return "EF"
        elif self.is_trainee():
            return "ES"
        # elif self.is_retiree():
        #     return 'AP'
        elif self.is_resident:
            return "RS"
        elif self.is_voluntary():
            return "VL"
        elif self.is_outsourced():
            return "TE"
        elif self.is_external():
            return "EX"
        elif self.is_apprentice():
            return "JC"
        elif self.is_acordo_cooperacao:
            return "AC"
        elif self.is_comissionado:
            return "CM"
        else:
            return None

    @property
    def is_efetivo(self):
        return self.type_by_possession in ("EFE", "ECM", "EFC")

    @property
    def is_comissionado(self):
        return self.type_by_possession == "CMS"

    def get_is_comissionado(self, date=None):
        """Este método verifica se o servidor possui um cargo comissionado numa date específica.

        Args:
            date (date)

        Returns:
            bool: quando possuir um cargo comissionado na data especificada, retorna True.
        """
        date = datetime.now().date() if not date else date
        return (
            self.get_posses_ativas(date)
            .filter(quadro__cargo__tipo_lei_cargo="CM")
            .exists()
        )

    @property
    def is_funcaoconfianca(self):
        return self.get_is_funcaoconfianca()

    def get_is_funcaoconfianca(self, data=None):
        data = datetime.now().date() if not data else data
        return (
            self.get_posses_ativas(data)
            .filter(quadro__cargo__tipo_lei_cargo="FC")
            .exists()
        )

    def is_trainee(self):
        return self.type_by_possession == "EST"

    # def is_retiree(self, date=None):
    #     date = datetime.now().date() if not date else date
    #     return self.get_declarationactivity(date=date).filter(declarationactivityretiree__activity_as='O').exists()

    def is_voluntary(self):
        return self.type_by_possession == "VOL"

    def is_outsourced(self):
        return self.type_by_possession == "TCR"

    def is_external(self, date=None):
        # date = datetime.now().date() if not date else date
        # return self.get_declarationactivity(date=date).filter(declaracaoatividade__activity_as='X').exists()
        return self.type_by_possession in ["EXT", "REQ", "REX"]

    def is_apprentice(self):
        return self.type_by_possession == "JCA"

    @property
    def is_resident(self):
        return bool(self.type_by_possession == "RES")

    @property
    def is_occasional_collaborator(self):
        return self.type_by_possession == "COE"

    @property
    def is_acordo_cooperacao(self):
        return self.type_by_possession in ("REQ", "RCM", "RFC")

    def get_is_acordo_cooperacao(self, data=None):
        data = datetime.now().date() if not data else data
        return (
            self.get_posses_ativas(data)
            .filter(quadro__cargo__tipo_lei_cargo="AC")
            .exists()
        )

    @property
    def is_eletivo(self):
        return self.get_is_eletivo()

    def get_is_eletivo(self, data=None):
        data = datetime.now().date() if not data else data
        return (
            self.get_posses_ativas(data)
            .filter(quadro__cargo__tipo_lei_cargo="EL")
            .exists()
        )

    @property
    def member_type_by_possession(self):
        """
        :py:function:: member_type_by_possession(self)

        Este método verifica se o servidor é membro em função do campo type_by_possession.

        :return: True/False
        :rtype: boolean
        """
        return self.type_by_possession in [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "MAP",
        ]

    @property
    def membro(self):
        return self.is_membro

    @property
    def is_membro(self):
        return self.member_type_by_possession

    @property
    def is_member(self):
        return self.member_type_by_possession

    def get_is_membro(self, data_inicio=None, data_fim=None):
        data_inicio = datetime.now().date() if not data_inicio else data_inicio
        return (
            self.get_posses_ativas(data_inicio, data_fim)
            .filter(quadro__cargo__tipo_lei_cargo="EF", quadro__cargo__indicativo="M")
            .exists()
        )

    @property
    def is_procurador_or_procurador_geral(self):
        return self.is_procurador or self.is_procurador_geral

    @property
    def is_procurador_geral(self):
        return self.posses_ativas.filter(quadro__cargo__codigo="PROCGERAL").exists()

    @property
    def is_procurador(self):
        return self.get_is_procurador()

    def get_is_procurador(self, data=None):
        """
        Verifica se o servidor é procurador.
        """
        data = datetime.now().date() if not data else data
        return (
            self.get_posses_ativas(data)
            .filter(
                Q(quadro__cargo__tipo_lei_cargo="EF")
                & Q(quadro__cargo__configs__instance=2)
                & Q(quadro__cargo__indicativo="M")
            )
            .exists()
        )

    @property
    def is_promotor(self):
        """
        Verifica se o servidor é promotor.
        """
        return self.member_type_by_possession and not self.get_is_procurador()

    def get_is_promotor(self, data=None):
        """
        Verifica se o servidor é promotor.
        """
        data = datetime.now().date() if not data else data
        return (
            not self.get_is_procurador(data=data)
            and self.posses.filter(Q(quadro__cargo__tipo_lei_cargo="EF"))
            .exclude(
                Q(quadro__cargo__tipo_lei_cargo="EF")
                & Q(quadro__cargo__nome__icontains="PROCURADOR")
            )
            .exists()
        )

    @property
    def is_servidor(self):
        """
        Verifica se o servidor é promotor.
        """
        return self.get_is_servidor()

    def get_is_servidor(self, data=None):
        """
        Verifica se o servidor é promotor.
        """
        data = datetime.now().date() if not data else data
        return (
            self.is_acordo_cooperacao
            or self.is_efetivo
            or self.get_is_comissionado(date=data)
        )

    @classmethod
    def teste_votacao(cls):
        count = 0
        matriculas_propriedade = []
        for s in Servidor.objects.all():
            if s.is_servidor_efetivo_nao_membro:
                count += 1
                matriculas_propriedade.append(s.matricula)
                if not s.is_ativo():
                    print("servidor nao esta ativo", s)
                if s.indicativo == "M":
                    print("membro ", s)
        print(matriculas_propriedade)
        print("quantidade ", count)

    @property
    def is_servidor_efetivo_nao_membro(self):
        """
        Este método verifica se o servidor é efetivo e não é membro.
        """
        return self.is_efetivo and not self.member_type_by_possession

    @property
    def aposentado(self):
        """
        Este método verifica se o servidor é aposentado.
        """
        if not hasattr(self, "_aposentado_cache"):
            self._aposentado_cache = (
                self.movimentacaopessoal_set.filter(
                    ~Q(movimentacaodesligamento__movimentacaoaposentadoria=None)
                ).exists()
                and self.posses_ativas.exists() is False
            )

        return self._aposentado_cache

    @ilru_cache()
    def my_replacement(self, date=None, owner=True):
        """
        :py:function:: my_replacement(self, date=None, owner=True)

        This method returns Replacement QuerySet from Servidor.
        Considers if exist a validity document.

        :param date date - default is datetime.now().date()
        :param bool owner - default is True

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        date = datetime.now().date() if not date else date
        replacements = Replacement.objects.filter(
            replaced__servidores_lotacao__servidor=self,
            replaced__servidores_lotacao__designacao=False,
            replaced__servidores_lotacao__ativo=True,
        )
        if owner:
            replacements = replacements.filter(replaced__servidores_lotacao__owner=True)
        return Replacement.objects.filter(
            pk__in=(pk for pk in replacements.distinct().values_list("pk", flat=True))
        )

    @ilru_cache()
    def my_replacement_substitute(
        self, date=None, owner=False, employee=None, workplace=None
    ):
        """
        :py:function:: my_replacement_substitute(self, date=None, owner=False)

        This method verifies substitutes that are at ExecutionOrgan.
        Considers EmployeeWorkplace.owner and date validity.

        :param date date - default is datetime.now().date()
        :param bool owner - default is False
        :param Employee employee:
        :param Workplace workplace:

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        date = datetime.now().date() if not date else date
        substitutes = self.my_replacement(date=date)
        substitutes = substitutes.filter(
            substitute__servidores_lotacao__ativo=True,
            substitute__servidores_lotacao__responsible=True,
            substitute__servidores_lotacao__servidor__tipo=self.tipo,
            substitute__servidores_lotacao__ordinance=False,
        )
        if owner is True:
            substitutes = substitutes.filter(substitute__servidores_lotacao__owner=True)

        if workplace:
            substitutes = substitutes.filter(
                substitute__servidores_lotacao__lotacao=workplace
            )
        if employee:
            substitutes = substitutes.filter(
                substitute__servidores_lotacao__servidor=employee
            )
        return substitutes

    def my_replacement_employee_workplace(self):
        """
        :py:function:: my_replacement_employee_workplace(self)

        This method returns a ServidorLotacao QuerySet from my_replacement_substitute method.

        :return: QuerySet of EmployeeWorkplace
        :rtype: QuerySet
        """
        my_replacement_substitute = self.my_replacement_substitute()
        my_replacement_substitute = my_replacement_substitute.values(
            "substitute__servidores_lotacao__pk",
            "substitute__servidores_lotacao__servidor__pk",
        )
        employee_workplaces = []
        employees = []
        for rs in my_replacement_substitute:
            employee_workplaces.append(rs.get("substitute__servidores_lotacao__pk"))
            employees.append(rs.get("substitute__servidores_lotacao__servidor__pk"))
        return ServidorLotacao.objects.filter(
            pk__in=employee_workplaces,
            servidor__pk__in=employees,
            ativo=True,  # TODO: OBSERVAR SE O ATIVO PODE SER TRUE
        )

    def my_substitute_employee(self):
        """
        :py:function:: my_substitute_employee(self)

        This method returns a Servidor QuerySet from my_replacement_substitute method.

        :return: QuerySet of Servidor
        :rtype: QuerySet
        """
        return Servidor.objects.filter(
            matricula__in=self.my_replacement_substitute().values(
                "substitute__servidores_lotacao__servidor__matricula"
            )
        )

    def my_substitute_workplace(self):
        """
        :py:function:: my_substitute_workplace(self)

        This method returns Workplace querset that substitutes a Employee according the replacement table.

        :return: queryset of Workplace
        :rtype: queryset of Workplace
        """
        return Lotacao.objects.filter(
            pk__in=self.my_replacement_substitute().values("substitute__pk")
        )

    def where_replacement(self, date=None, owner=True):
        """
        :py:function:: where_replacement(self, date=None, owner=True)

        This method returns Replacement QuerySet from Servidor where should have to substitute.
        Considers if exist a validity document.

        :param date date - default is datetime.now().date()
        :param bool owner - default is True

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        date = datetime.now().date() if not date else date

        replacements = Replacement.objects.filter(
            substitute__pk__in=self.get_owner_location_workplace_from_workassignment(
                date=date
            )
        )
        return replacements.distinct()

    def where_replacement_substitute(
        self, date=None, owner=True, employee=None, workplace=None
    ):
        """
        :py:function:: where_replacement_substitute(self, date=None, owner=True, employee=None, workplace=None)

        This method verifies substitutes that are at ExecutionOrgan.
        Considers EmployeeWorkplace.owner(ONLY) to True and date validity.

        :param date date: default is datetime.now().date()
        :param bool owner: default is True
        :param Employee employee:
        :param Workplace workplace:

        :return: QuerySet of Replacement
        :rtype: QuerySet
        """
        # TODO: VERIFICAR QUEM PODERÁ SER SUBSTITUTO NESTE CASO: APENAS O TITULAR DO LOCAL OU TODOS QUE ESTIVEREM EM EXERCÍCIO
        # TODO: PRESTAR ATENÇÃO NO PARAMETRO OWNER PARA QUAL UTILIZAÇÃO EXIGE OWNER=TRUE

        date = datetime.now().date() if not date else date
        replaceds = self.where_replacement(date=date)
        if owner is True:
            replaceds = replaceds.filter(replaced__servidores_lotacao__owner=True)
        replaceds = replaceds.exclude(
            ~Q(substitute__servidores_lotacao__servidor__tipo=self.tipo)
        )
        replaceds = replaceds.filter(substitute__servidores_lotacao__ordinance=False)
        if workplace:
            replaceds = replaceds.filter(
                replaced__servidores_lotacao__lotacao=workplace
            )
        if employee:
            replaceds = replaceds.filter(
                replaced__servidores_lotacao__servidor=employee
            )
        return replaceds

    @deprecated
    def substitutos_list(self):
        """
        :py:function:: substitutos_list(self)

        This method is a hook for substitutos. Return list of the Servidor.

        :return: list of Servidor
        :rtype: list
        """
        substitutes = []
        for sub in self.my_substitute():
            for ser in sub.get("substitutos"):
                substitutes.append(ser.get("servidor"))
        return substitutes

    def membro_verifica_entrancia(self, entrancia="PRIMEIRA", data=None):
        data = datetime.now().date() if not data else data
        posses = self.posses.exclude(Q(quadro__cargo__tipo_lei_cargo__in=("CM", "EL")))
        ultima_posse = posses.latest("data_exercicio") if posses.exists() else None
        return (
            (
                ultima_posse.quadro.cargo.entrancia
                and ultima_posse.quadro.cargo.entrancia.nome.find(entrancia) != -1
            )
            if ultima_posse
            else False
        )

    """------------- PROPERTYs ----------------------------------------------------------------------"""
    """Retorna todas as POSSES desse servidor ordenadas por data de exercicio."""
    posses = property(_get_posses)

    """Retorna todas as POSSES ATIVAS desse servidor ordenadas por data de exercicio."""
    posses_ativas = property(_get_posses_ativas)

    """Retorna se as férias de um servidor está bloqueada ou não, nesse caso o servidor não pode marcar ou usufruir."""
    ferias_bloqueada = property(_get_ferias_bloqueada)

    """Retorna os servidores subordinados ao servidor atual."""
    subordinados_ids = property(_get_subordinados_ids)

    def get_situacao_previdenciaria(self, data_inicio, data_fim, ultimo):
        """
        Este método retorna a situação previdenciária do servidor de acordo com a tabela 01 do manual do IGEPREV(ver @igeprev.const).
        @param Servidor - self.
        @return int - situacao.
        """
        situacao = 0
        if self.is_ativo():
            situacao = 0
        if self.is_inativo():
            situacao = 1
        if self.is_instituidor_pensao(data_inicio, data_fim, ultimo):
            situacao = 2
        if self.is_falecido_sem_pensionista():
            situacao = 4
        if self.is_ex_pensionista(data_fim, ultimo):
            situacao = 5
        if self.is_instituidor_auxilio_reclusao():
            situacao = 6
        return situacao

    def is_inativo(self):
        """
        Este método verifica se existe aposentadoria para o servidor.
        @return boolean - True caso seja inativo(aposentado), de outra forma False.
        """
        inativo = False
        try:
            if self.movimentacaopessoal_set.filter(
                ~Q(movimentacaodesligamento__movimentacaoaposentadoria=None)
            ).filter():
                inativo = True
        except Exception:
            pass
        return inativo

    def is_instituidor_pensao(self, data_inicio, data_fim, ultimo):
        """
        Este método verifica se o servidor paga pensão entre um intervalo de datas.
        Data de início deve ser <= data_inicio, e a data de fim > data_fim.
        @param datetime - data_inicio.
        @param datetime - data_fim.
        """
        instituidor = False
        try:
            if ultimo and self.pensao_pagador.filter():
                instituidor = False
            elif self.pensao_pagador.filter(
                Q(pensao_pagador__data_inicio__lte=data_inicio)
                & Q(pensao_pagador__data_fim__gt=data_fim)
            ):
                instituidor = True
        except Exception:
            pass
        return instituidor

    def settlor_pension_deth(self, date=None):
        date = datetime.now().date() if not date else date
        return self.pensao_pagador.filter(
            Q(data_inicio__lte=date) & Q(Q(data_fim__gte=date) | Q(data_fim=None))
        ).exists()

    def is_falecido_sem_pensionista(self):
        sem_pensionista = False
        try:
            if self.data_obito and self.pensao_pagador.filter().count() == 0:
                sem_pensionista = True
        except Exception:
            pass
        return sem_pensionista

    def is_ex_pensionista(self, data_fim, ultimo):
        ex_pensionista = False
        try:
            if (
                ultimo
                and self.pensao_pagador.filter().count() > 0
                and self.pensao_pagador.filter().count() == 0
            ):
                ex_pensionista = False
            elif (
                self.pensao_pagador.filter().count() > 0
                and self.pensao_pagador.filter(
                    Q(pensao_pagador__data_fim__lt=data_fim)
                ).count()
                == 0
            ):
                ex_pensionista = True
        except Exception:
            pass
        return ex_pensionista

    def is_instituidor_auxilio_reclusao(self):
        # TODO: VERIFICAR DE ONDE VEM AUXILIO RECLUSAO
        return False

    def is_ativo(self, data=None):
        data = datetime.now().date() if not data else data
        posses_ativas = self.get_posses_ativas(data)
        return posses_ativas.exists()

    @property
    def giver(self):
        return self.relationship_giver.filter()

    @property
    def receiver(self):
        return self.relationship_receiver.filter()

    def texto_servidor(self):
        return "Servidor(a)" if not self.member_type_by_possession else "Membro"

    def update_dates(self):
        self.exercise_date = self.data_exercicio
        self.termination_date = self.dismissal_date
        if "exercise_date" in self.diff or "termination_date" in self.diff:
            self.save()

    def atualiza_cache_ativo(self):
        """
        Este método deve ser chamado no post_save/post_delete de MovimentacaoPosse e MovimentacaoDesligamento
        para atualizar o cache ativo do Servidor.
        """
        message = ""
        servidor = Servidor.objects.get(pk=self.pk)
        is_active = self.is_ativo()
        if servidor.ativo != is_active:
            message = "Atualizando CACHE ACTIVE: %s -> %s" % (
                boolean_unicode(servidor.ativo),
                boolean_unicode(is_active),
            )
            log.debug(message)
            try:
                servidor.save()
            except Exception as err:
                log.exception(err)

    def employee_type(self):
        emp_type = "S"
        possessions_active = self.posses_ativas.exists()
        # declarationactivity = self.get_declarationactivity()
        possessions = self.posses
        if self.type_by_possession in (
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
            "MAP",
        ):
            emp_type = "M"
        elif (
            self.posses.filter(quadro__cargo__indicativo="P").exists()
            and not self.posses.filter(quadro__cargo__indicativo="S").exists()
        ):
            emp_type = "P"
        elif self.type_by_possession == "EST":
            emp_type = "E"
        elif self.type_by_possession == "TCR":
            emp_type = "T"
        elif self.type_by_possession == "VOL":
            emp_type = "V"
        elif self.type_by_possession == "JCA":
            emp_type = "A"
        # elif declarationactivity.filter(declaracaoatividade__quadro__cargo__indicativo='X').exists() and not possessions_active:
        #     emp_type = 'X'
        return emp_type

    def atualiza_cache_tipo(self):
        """
        Atualiza o @tipo sempre que o servidor tiver uma posse nova
        Se o servidor tiver pelo menos um cargo do tipo 'M' (membro),
        tipo recebe 'M', caso contrário recebe 'S' ou 'E' para estagiário.
        """
        message = ""
        tipo = self.employee_type()
        message = "Servidor Tipo atual: %s -> novo: %s" % (self.tipo, tipo)
        employee = Servidor.objects.get(pk=self.pk)
        if employee.tipo != tipo:
            employee.tipo = tipo
            log.debug(message)
            try:
                with transaction.atomic():
                    employee.save()
            except Exception as err:
                log.exception(err)
        else:
            message = "Tipo do servidor não modificou: %s." % employee.tipo
        log.debug(message)

    def set_data_referencia_ferias(self, data_referencia_ferias):
        """
        Atualiza data de atuação de férias, em Servidor, caso esteja None.
        O valor aplicado será a data de exercício da MovimentacaoPosse.
        """
        message = "set_data_referencia_ferias"
        try:
            with transaction.atomic():
                servidor = Servidor.objects.get(pk=self.pk)
                if servidor.data_referencia_ferias is None:
                    servidor.data_referencia_ferias = data_referencia_ferias
                    message = "%s nova data referência de férias %s." % (
                        self,
                        (
                            DateUtils.date_to_str(data_referencia_ferias)
                            if data_referencia_ferias
                            else "----"
                        ),
                    )
                    log.debug(message)
                    servidor.save()
        except Exception as err:
            log.exception(err)

    def set_chief_immediate(self, chief_immediate=None):
        """
        :py:function:: set_chief_immediate(self, chief_immediate=None)

        This method updates the chief immediate if it's different.

        :param Servidor chief_immediate: chief_immediate default is None
        """
        message = "set_chief_immediate"
        try:
            with transaction.atomic():
                employee = Servidor.objects.get(pk=self.pk)
                if (
                    employee.chefe_imediato != chief_immediate
                    and employee != chief_immediate
                ):
                    message = "%s - CHEFE IMEDIATO - ATUAL: %s >> NOVO: %s" % (
                        employee,
                        employee.chefe_imediato,
                        chief_immediate,
                    )
                    employee.chefe_imediato = chief_immediate
                    employee.save_base()
                    log.info(message)
                else:
                    message = "O chefe do servidor %s não mudou." % self
                    log.info(message)
        except Exception as err:
            log.exception(err)
            notify_employee(sender=self, mensagem=err)

    @deprecated
    def set_organ_social_security(self, possession):
        """
        :py:function:: set_organ_social_security(self)

        This method sets Servidor.organ_social_security. Using Cargo.unidade_administrativa.previdencia to set the
        value.
        It acts only if organ_social_security is None.

        Persisting through Servidor.save.

        :param MovimentacaoPosse possession:
        :return: bool True if not problem
        :rtype: bool
        """
        try:
            employee = Servidor.objects.get(pk=self.pk)
            with transaction.atomic():
                if possession.quadro and not employee.organ_social_security:
                    employee.organ_social_security = (
                        possession.quadro.cargo.unidade_administrativa.previdencia
                    )
                    employee.save()
        except Exception as err:
            log.exception(err)
            return False
        return True

    def update_bond(self):
        """
        :py:function:: update_bond(self)

        This method sets True if there are at least possession bond True, otherwise False.

        :return: bool True if not problem
        :rtype: bool
        """
        try:
            if self.bond != self.is_bond:
                self.save()
        except Exception as err:
            log.exception(err)
            return False
        return True

    def set_functional_status(self, functional_status):
        """
        :py:function:: set_functional_status(cls, functional_status)

        This method sets the Employee.situacao_funcional_cache as parameter functional_status.
        Returns True if functional_status is valid and set.

        :param str functional_status, SituacaoFuncional.situacao
        :return: bool True if not problem
        :rtype: bool
        """
        try:
            fs = (
                Servidor.objects.filter(pk=self.pk)
                .values("situacao_funcional_cache")
                .get()
                .get("situacao_funcional_cache")
            )
            if fs != functional_status:
                Servidor.objects.filter(pk=self.pk).update(
                    situacao_funcional_cache=functional_status
                )
        except Exception as err:
            log.exception(err)
            return False
        return True

    def update_vacation_reference(self, departure=None):
        """Método que altera a data de referência das férias de um servidor quando houver licenças/afastamentos sem remuneração.

        Tipos de Licença:
        1) Licença para interesses particulares
        2) Licenças para Acompanhar Conjuge e
        3) Afastamento para mandado eletivo.
        """
        try:
            with transaction.atomic():
                from rh.afastamento.models import (
                    AfastamentoMandatoEletivo,
                    LicencaAfastamentoConjuge,
                    LicencaInteresseParticular,
                )

                if (
                    self.tipo == "S"
                    and departure
                    and (
                        isinstance(departure, LicencaAfastamentoConjuge)
                        or isinstance(departure, LicencaInteresseParticular)
                        or isinstance(departure, AfastamentoMandatoEletivo)
                    )
                ):
                    range_license_total = NewDateRange()
                    STATES = [1, 4]
                    old_date_reference = self.data_exercicio

                    license_spouse = LicencaAfastamentoConjuge.objects.filter(
                        servidor=self
                    ).exclude(estado__in=STATES)

                    for license in license_spouse:
                        range_spouse = NewDateRange(
                            license.data_inicio, license.data_fim
                        )
                        range_license_total += range_spouse

                    license_particular = LicencaInteresseParticular.objects.filter(
                        servidor=self
                    ).exclude(estado__in=STATES)

                    for license in license_particular:
                        range_particular = NewDateRange(
                            license.data_inicio, license.data_fim
                        )
                        range_license_total += range_particular

                    afastamento_elective = AfastamentoMandatoEletivo.objects.filter(
                        servidor=self
                    ).exclude(estado__in=STATES)

                    for license in afastamento_elective:
                        range_elective = NewDateRange(
                            license.data_inicio, license.data_fim
                        )
                        range_license_total += range_elective

                    new_date_reference = old_date_reference

                    if not isinstance(range_license_total.days, float):
                        new_date_reference += relativedelta(
                            days=range_license_total.days
                        )

                    if self.data_referencia_ferias != new_date_reference:
                        log.info(
                            "----> ATUALIZANDO DATA DE REFERENCIA DE FÉRIAS DO SERVIDOR: %s. Data Antiga: %s, Nova Data: %s "
                            % (self, old_date_reference, new_date_reference)
                        )
                        self.data_referencia_ferias = new_date_reference
                        self.save()
        except Exception as err:
            log.exception(err)

    def update_chief_immediate(self, mandatory=False, old_chief=None, new_chief=None):
        """
        :py:function:: update_chief_immediate(self)

        This method verifies if employee is active and does not have chief immediate. Assume the responsible as
        workplace responsible when employee is not a member, otherwise use
            self.servidor._get_chefe_imediato(lotacao_inf=self).
        Then call self.servidor.set_chief_immediate(responsible).
        """
        new_chief = self._get_chefe_imediato() if not new_chief else new_chief
        if (
            not self.chefe_imediato
            or not self.chefe_imediato
            and not old_chief
            or self.chefe_imediato == old_chief
            or mandatory
        ):
            self.set_chief_immediate(new_chief)
        else:
            log.info(
                "Nada mudou para %s - chefe imediato atual: %s."
                % (self, self.chefe_imediato)
            )

    @property
    def is_dead(self):
        if hasattr(self, "pessoa_fisica"):
            return bool(self.pessoa_fisica.data_obito)
        return False

    def is_traveling(self, date=None):
        if not date:
            date = datetime.now()

        return self.pessoa_fisica.diarias.filter(
            solicitacao__data_de_saida__lte=date, solicitacao__data_de_retorno__gte=date
        ).exists()

    def owner_of_job_position_effective(self):
        """
        :py:function:: owner_of_job_position_effective(self)

        This method verifies if employee has work assignment as owner and job position at this places.
        Also verifies if exists a departure DesempenhoFuncao or AtuacaoGrupoTrabalho.

        Method to avoid vacation conflicts.

        :return: bool True if not found
        :rtype: bool
        """
        exists = False
        for work_assignment in (
            self.work_assignment_effective_exercise.filter(owner=True)
            .filter(lotacao__in=self.work_locations_effective_exercise)
            .values("lotacao")
        ):
            exists = MovimentacaoPosse.objects.filter(
                servidor=self,
                quadro__cargo__tipo_lei_cargo="EF",
                quadro__cargo__lotacao_responsavel=work_assignment.get("lotacao"),
                ativo=True,
            ).exists()
        return exists

    def _update_type_by_possession(self, save=True):
        # EFE - SERVIDOR EFETIVO *
        # ECM - SERVIDOR EFETIVO E COMISSIONADO *
        # EFC - SERVIDOR EFETIVO COM FUNÇÃO CONFIANÇA *
        # MBR - MEMBRO *
        # MEL - MEMBRO COM CARGO ELETIVO *
        # MCM - MEMBRO COM CARGO COMISSIONADO *
        # MEC - MEMBRO COM CARGO ELETIVO E COMISSIONADO
        # MBR2 - MEMBRO *
        # MEL2 - MEMBRO COM CARGO ELETIVO *
        # MCM2 - MEMBRO COM CARGO COMISSIONADO *
        # MEC2 - MEMBRO COM CARGO ELETIVO E COMISSIONADO
        # CMS - SERVIDOR COMISSIONADO
        # REQ - SERVIDOR REQUISITADO *
        # RCM - SERVIDOR REQUISITADO COMISSIONADO *
        # RFC - SERVIDOR REQUISITADO COM FUNÇÃO CONFIANÇA *
        # REX - SERVIDOR REQUISITADO EXTERNO SEM REQUISIÇÃO*
        # CTR - SERVIDOR CONTRATADO
        # EST - ESTAGIÁRIO *
        # TCR - TERCEIRIZADO *
        # VOL - VOLUNTÁRIO *
        # JCA - JOVEM APRENDIZ
        # EXT - EXTERNO SEM VÍNVULO
        # MAP - MEMBRO APOSENTADO
        # SAP - SERVIDOR EFETIVO APOSENTADO
        # APO - SERVIDOR APOSENTADO
        # BFP - BENEFICIÁRIO DE PENSÃO
        # JCA - JOVEM CIDADÃO - APRENDIZ
        # COE - COLABORADOR EVENTUAL
        dt_endr = dt_end = dt_now = datetime.now().date()
        if not self.is_ativo():
            dt_end = self.posses.filter(
                data_desligamento__isnull=False, data_desligamento__lte=dt_now
            ).aggregate(dt=Max("data_desligamento"))["dt"]
            if dt_end:
                dt_end = dt_end - relativedelta(days=1)
                # dt_enc = self.get_declarationactivity().aggregate(dt=Max('declaracaoatividade__data_encerramento'))['dt']
            dt_endr = MovimentacaoRequisicao.objects.filter(servidor=self).aggregate(
                dt=Max("data_fim")
            )["dt"]

        cm = self.get_is_comissionado(dt_end) and self.is_ativo()
        fc = self.get_is_funcaoconfianca(dt_end) and self.is_ativo()

        if self.type_by_possession in (
            "BFP",
            "MAP",
            "MAP2",
            "SAP",
            "APO",
            "EST",
            "VOL",
            "TCR",
            "JCA",
            "CMS",
            "EXT",
            "REX",
            "COE",
            "",
        ):
            pass
        elif self.tipo == "E":  # self.is_trainee(dt_enc):
            self.type_by_possession = "EST"
        elif self.tipo == "V":  # self.is_voluntary(dt_enc):
            self.type_by_possession = "VOL"
        elif self.tipo == "T":  # self.is_outsourced(dt_enc):
            self.type_by_possession = "TCR"
        elif self.tipo == "J":  # self.is_apprentice(dt_enc):
            self.type_by_possession = "JCA"
        elif self.get_is_requested(dt_endr):
            if cm:
                self.type_by_possession = "RCM"
            elif fc:
                self.type_by_possession = "RFC"
            else:
                self.type_by_possession = "REQ"
        elif self.type_by_possession in ("EFE", "ECM", "EFC"):
            if cm:
                self.type_by_possession = "ECM"
            elif fc:
                self.type_by_possession = "EFC"
            else:
                self.type_by_possession = "EFE"
        elif self.type_by_possession in (
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
        ):
            el = self.get_is_eletivo(dt_end) and self.is_ativo()
            pos = "2" if self.get_is_procurador(dt_end) else ""
            if cm:
                self.type_by_possession = "MCM{}".format(pos)
            elif el:
                self.type_by_possession = "MEL{}".format(pos)
            else:
                self.type_by_possession = "MBR{}".format(pos)
        else:
            self.type_by_possession = "XXX"

        if save and "type_by_possession" in self.diff:
            self.categoria_cache = self.type_by_possession
            self.save(type_by_possession_validate=False)

        return self.type_by_possession

    @property
    def query_pas_day_sell(self):
        from rh.ferias.models import PAS_FRUIDA

        to_exclude = [
            pas.pk
            for pas in self.periodos_aquisitivos.filter()
            if pas.dias_ausufruir == 0
        ]
        query = (
            Q(estado=PAS_FRUIDA)
            | Q(pk__in=to_exclude)
            | Q(data_inicio_usufruto__gt=datetime.now().date())
            | Q(bloqueado=True)
        )
        return query

    @property
    def job_position_daily_payment(self):
        """
        :py:function:: job_position_daily_payment(self)

        Este método retorna os cargos que podem ser utilizados pelo servidor para assinatura de diárias.

        Utiliza as @posses_ativas e as posses das substituições vigentes no momento.

        :return: QuerySet Cargo
        :rtype: QuerySet
        """
        job_positions = [
            job.quadro.cargo.pk
            for job in self.posses_ativas.exclude(quadro__isnull=True)
        ]
        for job in self.substitutions_per_date():
            job_positions.append(job.posse.quadro.cargo.pk)
        return Cargo.objects.filter(pk__in=job_positions)

    def get_socialsecurity_by_validity(self, *args, **kwargs):
        # TODO: avaliar se precisaria alterar no caso de mais de uma configuração de previdência vigente no período/data
        at_range = kwargs.get("range", None)
        at_date = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        sse = None
        if self.pk and at_date:
            sse = self.socialsecurities.currents_at(at_date).first()
        if self.pk and at_range:
            sse = self.socialsecurities.currents_between(
                at_range.first, at_range.last
            ).first()
        return sse.social_security_config if sse else None

    @property
    def regime_social_security(self, *args, **kwargs):
        ssc = self.get_socialsecurity_by_validity(*args, **kwargs)
        return ssc.regime if ssc else None

    def organ_social_security_employee(self, *args, **kwargs):
        ssc = self.get_socialsecurity_by_validity(*args, **kwargs)
        return ssc.organ if ssc else None

    def teletrabalho_ativo(self, data=None):

        if data:
            return self.movimentacaopessoal_set.filter(
                movimentacaoteletrabalho__isnull=False,
                movimentacaoteletrabalho__data_inicio__lte=data,
                movimentacaoteletrabalho__data_fim__gte=data,
            ).exists()

        return self.movimentacaopessoal_set.filter(
            movimentacaoteletrabalho__isnull=False, movimentacaoteletrabalho__ativo=True
        ).exists()


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "vinculo", "type": "choices"},
    ]
)
class ServidorVinculo(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="servidor_vinculo",
        on_delete=models.CASCADE,
    )
    servidor_vinculado = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor vinculado",
        related_name="servidor_vinculado",
        on_delete=models.CASCADE,
    )
    vinculo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Tipo de Vínculo",
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Vinculo do Servidor"

    def __str__(self):
        return "%s - %s" % (self.get_vinculo_display(), self.servidor_vinculado)


class DependenteQuerySet(models.QuerySet):
    def dependencies_active_in(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        return (
            self.filter(dependencias__suspenso=False)
            .exclude(
                Q(dependencias__data_inicio__gt=end_date)
                | (
                    Q(dependencias__data_fim__isnull=False)
                    & Q(dependencias__data_fim__lt=start_date)
                )
            )
            .distinct()
        )

    def dependencies(self):
        return Dependencia.objects.of_dependents(self.all())


class DependenteManager(models.Manager):
    def get_queryset(self):
        return DependenteQuerySet(self.model, using=self._db)

    def dependencies_active_in(self, start_date=None, end_date=None):
        return self.get_queryset().dependencies_active_in(start_date, end_date)


class Dependente(AuditTimestampModel):
    pessoa_fisica = models.ForeignKey(
        "PessoaFisica",
        related_name="dependentes_pessoa",
        verbose_name="Pessoa Física",
        on_delete=models.PROTECT,
    )
    responsavel = models.ForeignKey(
        "PessoaFisica",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="responsavel_dependentes",
        verbose_name="Responsável",
    )
    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="dependentes",
        on_delete=models.CASCADE,
    )
    # DEPRECATED
    motivo_inicio_dependencia = models.IntegerField(
        choices=list(MOTIVO_INICIO_DEPENDENCIA.items()),
        null=True,
        blank=True,
        verbose_name="Motivo Início Dependência",
    )
    # DEPRECATED
    motivo_fim_dependencia = models.IntegerField(
        choices=list(MOTIVO_FIM_DEPENDENCIA.items()),
        null=True,
        blank=True,
        verbose_name="Motivo Fim Dependência",
    )
    grau_parentesco = models.IntegerField(
        choices=Choice.get_choices_for("rh", "GRAU_PARENTESCO_CHOICES"),
        verbose_name="Tipo de Parentesco",
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    dep_ir = models.BooleanField(default=False, verbose_name="Imposto de Renda")
    dep_sf = models.BooleanField(default=False, verbose_name="Salário Família")
    dependente_direto = models.BooleanField(
        default=False, verbose_name="Dependente Direto"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    auxilio_creche = models.BooleanField(
        default=False, verbose_name="Recebe Auxílio Creche"
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    tipo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEPENDENT_TYPE"),
        null=True,
        verbose_name="Tipo",
    )
    capacidade = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CAPACITY"), null=True, default=1
    )
    incapacity = models.BooleanField(
        default=False, blank=True, verbose_name="Incapacidade física/mental"
    )

    objects = DependenteManager()

    class Meta:
        verbose_name = "Dependente"
        unique_together = (("pessoa_fisica", "servidor"),)

    def __str__(self):
        return "%s - %s" % (self.get_grau_parentesco_display(), self.pessoa_fisica)

    def validate(self):
        self.validate_cpf()
        self.validate_sexo_dependente()

    def validate_cpf(self):
        if self.pessoa_fisica and not self.pessoa_fisica.cpf:
            raise Exception("O CPF do dependente é obrigatório.")

    def validate_sexo_dependente(self):
        if self.pessoa_fisica and not self.pessoa_fisica.sexo:
            raise Exception("Obrigatóirio informar o sexo do dependente.")

    def validate_date_born(self):
        if self.pessoa_fisica and not self.pessoa_fisica.data_nascimento:
            raise Exception("A data de nascimento é obrigatória.")

    def save(self, *args, **kargs):
        self.validate()
        self.responsavel = self.servidor.pessoa_fisica
        super(Dependente, self).save(*args, **kargs)
        log.debug("SAVING DEPENDENTE >>> %s" % self)

    def tem_dependencia(self, tipo, data=None):
        data = datetime.today().date() if not data else data
        return self.dependencias.filter(
            Q(tipo=tipo, suspenso=False, data_inicio__lte=data)
            & (Q(data_fim=None) | Q(data_fim__gte=data))
        ).exists()


class DependenciaQuerySet(models.QuerySet):
    def active_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio__gt=range_.last)
                | (~Q(data_fim=None) & Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio__gt=data) | (~Q(data_fim=None) & Q(data_fim__lt=data))
            )

    def esocial_valid(self):
        return self.filter(tipo__in=[1, 3])

    def of_dependents(self, deps):
        return self.filter(dependente__in=deps)

    def irrf_actives(self, employee, limit_date):
        return self.filter(
            Q(
                tipo=1,
                suspenso=False,
                data_inicio__lte=limit_date,
                dependente__servidor=employee,
            )
            & (Q(data_fim=None) | Q(data_fim__gte=limit_date))
        )


class Dependencia(AuditTimestampModel):
    dependente = models.ForeignKey(
        "Dependente",
        related_name="dependencias",
        verbose_name="Dependência",
        on_delete=models.CASCADE,
    )
    tipo = models.SmallIntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_OF_DEPENDENCE"), default=1
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data de Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data de Fim")
    idade_limite = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Idade limite"
    )
    estudante = models.BooleanField(default=False, verbose_name="Estudante")
    suspenso = models.BooleanField(default=False, verbose_name="Suspenso")
    origem = models.CharField(
        choices=(("vdf", "VDF"), ("manual", "MANUAL")),
        default="manual",
        max_length=50,
        verbose_name="Origem",
    )

    objects = DependenciaQuerySet.as_manager()

    class Meta:
        db_table = "rh_dependencia"

    def __str__(self):
        return "%s - %s" % (self.get_tipo_display(), self.dependente)

    @property
    def is_ativo(self):
        data = datetime.now().date()
        if self.data_fim is not None:
            return True if self.data_inicio <= data and data <= self.data_fim else False
        return True if data >= self.data_inicio else False

    def conflicts(self):
        return []

    def get_state_icons(self):
        status = []
        if self.is_ativo and not self.suspenso:
            status.append(
                {"iconCls": "icon-progressoes icon-progressoes-status", "alt": "Ativo"}
            )
        else:
            status.append(
                {
                    "iconCls": "icon-progressoes icon-progressoes-status-busy",
                    "alt": "Inativo",
                }
            )
        conflicts = self.conflicts()
        if conflicts:
            status.append(
                {
                    "iconCls": "icon-core icon-core-warn",
                    "alt": "O depedente possui a mesma dependência com o(s) seguinte(s) servidor(es):<br /> %s"
                    % "".join(["%s<br />" % d.dependente.servidor for d in conflicts]),
                }
            )

        return status

    def atribui_idade_limite(self):
        query = Choice.objects.filter(app_label="gfp", name="DATA_LIMITE_AUX_CRECHE")
        if query.exists():
            self.idade_limite = query.first().value

    def calcula_datas_aux_creche(self):
        if self.origem == "vdf":
            self.data_inicio = self.auxilio_creche_data_inicio
        else:
            self.validar_data_inicio()

        self.validar_data_nascimento()
        self.data_fim = self.dependente.pessoa_fisica.data_nascimento + relativedelta(
            years=self.idade_limite, days=-1
        )

    def save(self, *args, **kargs):
        gcpp_aux_creche = False
        # Tipo 4 = Auxílio Creche
        if self.tipo == 4:
            self.atribui_idade_limite()
            self.calcula_datas_aux_creche()

            if not self.pk:
                gcpp_aux_creche = True

            self.validar_dt_inicio_menor_dt_fim()

        range_ = NewDateRange(self.data_inicio, self.data_fim)
        for dependence in self.dependente.dependencias.filter(tipo=self.tipo).exclude(
            pk=self.pk
        ):
            if range_.intersect(
                NewDateRange(dependence.data_inicio, dependence.data_fim)
            ).days:
                raise Exception(
                    f"""O dependente ({self.dependente.pessoa_fisica}) já possui uma dependência ({self.get_tipo_display()})
                     ativa nesse período ({self.data_inicio.strftime("%d/%m/%Y")} - {self.data_fim.strftime("%d/%m/%Y")})."""
                )

        super(Dependencia, self).save(*args, **kargs)

        if gcpp_aux_creche:
            criar_gcpp_aux_creche(self)

        log.debug("SAVING DEPENDENCIA >>> %s" % self)

    def delete(self, *args, **kwargs):
        from rh.gfp.gcpp_utils import remove_dependencia_gcpp

        remove_dependencia_gcpp(self)
        super(Dependencia, self).delete(*args, **kwargs)

    @property
    def auxilio_creche_data_inicio(self):
        data_nascimento = self.dependente.pessoa_fisica.data_nascimento
        servidor_data_posse = self.dependente.servidor.first_possession_date
        if (
            servidor_data_posse and data_nascimento
        ) and data_nascimento > servidor_data_posse:
            return data_nascimento
        return servidor_data_posse

    def validar_data_inicio(self):
        if not self.data_inicio:
            raise Exception("Favor informar data de início.")

    def validar_data_nascimento(self):
        data_nascimento = self.dependente.pessoa_fisica.data_nascimento
        if not data_nascimento:
            raise Exception("Favor preencher a data de nascimento do(a) dependente.")
        if data_nascimento > date.today():
            raise Exception("A data de nascimento do dependente não pode ser futura.")

    def validar_dt_inicio_menor_dt_fim(self):
        if self.data_inicio > self.data_fim:
            raise Exception(
                f'Data início não pode ser maior que data fim: {self.data_inicio.strftime("%d/%m/%Y")} - {self.data_fim.strftime("%d/%m/%Y")}'
            )

    def validar_origem_aux_creche(self, *, vdf=False, manual=False):
        if vdf:
            return self.tipo == 4 and self.origem == "vdf"
        if manual:
            return self.tipo == 4 and self.origem == "manual"
        return None


class DocsDadosEspecificos(AuditTimestampModel):
    especificidade = models.IntegerField(
        choices=Choice.get_choices_for("rh", "SPECIFICITY_DOCUMENT"),
        verbose_name="Especificidade",
    )
    valor = models.CharField(
        max_length=256, verbose_name="Valor", default="", blank=False
    )

    class Meta:
        verbose_name = "Documentos de dados específicos"

    def __str__(self):
        return "%s = %s" % (self.get_especificidade_display(), self.valor)

    def validate(self):
        self.validate_type_value()
        return True

    def validate_type_value(self):
        self.validate_type_value_title_voter_zone()
        self.validate_type_value_title_voter_section()
        self.validate_type_value_title_voter_state()
        self.validate_type_value_ctps_uf()
        return True

    def validate_type_value_title_voter_zone(self):
        if self.especificidade == TITULO_ELEITOR_ZONA and not self.valor.isdigit():
            raise Exception(
                "Por favor, informe apenas dígitos em Zona do Título Eleitoral."
            )
        return True

    def validate_type_value_title_voter_section(self):
        if self.especificidade == TITULO_ELEITOR_SECAO and not self.valor.isdigit():
            raise Exception(
                "Por favor, informe apenas dígitos em Seção do Título Eleitoral."
            )
        return True

    def validate_type_value_title_voter_state(self):
        if self.especificidade == TITULO_ELEITOR_UF and len(self.valor) > 2:
            raise Exception(
                "Por favor, informe apenas a sigla do Estado do Título Eleitoral."
            )
        return True

    def validate_type_value_ctps_uf(self):
        if self.especificidade == CTPS_UF and len(self.valor) > 2:
            raise Exception("Por favor, informe apenas a sigla do Estado da CTPS.")
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        self.validate()
        super(DocsDadosEspecificos, self).save(*args, **kargs)

    def update_natural_person_cache(self):
        """
        :py:function:: update_natural_person_cache(self)

        This method updates natural person rg data.

        :return: True if not
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        try:
            naturalperson = self.documentos.get().naturalpersons.get()
            if (
                naturalperson
                and self.especificidade == RG_ISSUER
                and naturalperson.rg_orgao != self.valor
            ):
                PessoaFisica.objects.filter(pk=naturalperson.pk).update(
                    rg_orgao=self.valor
                )
        except Exception as err:
            log.exception(err)


class DocsDataSpecificSpecialized(DocsDadosEspecificos):
    class Meta:
        proxy = True

    def validate(self):
        return True

    def save(self, *args, **kwargs):
        super(DocsDataSpecificSpecialized, self).save(*args, **kwargs)


class Documento(AuditTimestampModel):
    tipo_documento = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DOCUMENT_PERSON"),
        verbose_name="Tipo de Documento",
    )
    numero = models.CharField(
        max_length=30, verbose_name="Número", default="", blank=False
    )
    data_expedicao = models.DateField(
        verbose_name="Data da Expedição", null=True, blank=True
    )
    data_validade = models.DateField(
        verbose_name="Data de Validade", null=True, blank=True
    )
    estado_expedicao = models.ForeignKey(
        Estado,
        verbose_name="Estado de Expedição",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    dados_especificos = models.ManyToManyField(
        "DocsDadosEspecificos",
        verbose_name="Dados Específicos",
        blank=True,
        related_name="documentos",
    )
    arquivo = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.CASCADE
    )
    class_organ = models.IntegerField(
        choices=Choice.get_choices_for("rh", "CLASS_ORGAN"),
        blank=True,
        default=CLASS_ORGAN_OTHER,
    )
    natural_person = models.ForeignKey(
        PessoaFisica,
        verbose_name="Pessoa Física",
        related_name="documents",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    cnh_max_len = 11

    digital_document_mandatory = [
        RG,
        TITULO_ELEITOR,
        PROFESSIONAL_COUNCIL,
        CNH,
        RESERVISTA,
        STABLE_BONDING,
    ]

    class Meta:
        verbose_name = "Documento"

    def __str__(self):
        return "%s - Número: %s" % (self.get_tipo_documento_display(), self.numero)

    @property
    def is_from_employee(self):
        return self.natural_person.is_servidor()

    @property
    def is_from_pensioner(self):
        """
        Este método verifica se o Documento pertence a um pensionista.
        @return True, False.
        """
        return self.natural_person.pensao_pensionista.exists()

    @property
    def is_from_dependent(self):
        """
        Este método verifica se o Documento pertence a um dependente.
        @return True, False.
        """
        return self.natural_person.dependentes_pessoa.exists()

    @property
    def is_voter(self):
        return self.tipo_documento == TITULO_ELEITOR

    @property
    def is_cnh(self):
        return self.tipo_documento == CNH

    @property
    def is_ctps(self):
        return self.tipo_documento == CTPS

    @property
    def is_pis_pasep(self):
        return self.tipo_documento == PIS_PASEP

    @property
    def is_nis(self):
        return self.tipo_documento == NIS

    @property
    def is_ipsep(self):
        return self.tipo_documento == IPSEP

    @property
    def is_inss(self):
        return self.tipo_documento == INSS

    @property
    def is_reservist(self):
        return self.tipo_documento == RESERVISTA

    @property
    def is_professional_council(self):
        return self.tipo_documento == PROFESSIONAL_COUNCIL

    @property
    def is_ric(self):
        return self.tipo_documento == RIC

    @property
    def is_rne(self):
        return self.tipo_documento == RNE

    @property
    def is_cpf(self):
        return self.tipo_documento == CPF

    @property
    def is_rg(self):
        return self.tipo_documento == RG

    @property
    def is_stable_union(self):
        return self.tipo_documento == STABLE_BONDING

    @property
    def ctps_series(self):
        try:
            serie = self.dados_especificos.get(especificidade=CTPS_SERIE)
        except Exception:
            serie = None
        finally:
            return serie

    @property
    def ctps_numero(self):
        try:
            serie = self.dados_especificos.get(especificidade=CTPS_SERIE)
        except Exception:
            serie = None
        finally:
            return serie

    @property
    def ric_issuer(self):
        try:
            ric_issuer = self.dados_especificos.get(especificidade=RIC_ISSUER)
        except Exception:
            ric_issuer = None
        finally:
            return ric_issuer

    @property
    def rne_issuer(self):
        try:
            rne_issuer = self.dados_especificos.get(especificidade=RNE_ISSUER)
        except Exception:
            rne_issuer = None
        finally:
            return rne_issuer

    @property
    def rg_issuer(self):
        try:
            rg_issuer = self.dados_especificos.get(especificidade=RG_ISSUER)
        except Exception:
            rg_issuer = None
        finally:
            return rg_issuer

    @property
    def cnh_category(self):
        try:
            cnh_category = self.dados_especificos.get(especificidade=CNH_CATEGORIA)
        except Exception:
            cnh_category = None
        finally:
            return cnh_category

    @property
    def cnh_first_date(self):
        try:
            cnh_first_date = self.dados_especificos.get(especificidade=CNH_FIRST_DATE)
        except Exception:
            cnh_first_date = None
        finally:
            return cnh_first_date

    @property
    def professional_council_issuer(self):
        try:
            issuer = self.dados_especificos.get(
                especificidade=PROFESSIONAL_COUNCIL_ISSUER
            )
        except Exception:
            issuer = None
        finally:
            return issuer

    @property
    def voter_zone(self):
        zone = None
        try:
            zone = self.dados_especificos.get(especificidade=TITULO_ELEITOR_ZONA)
        except Exception:
            log.warning("Zona de título não encontrado.")
        return zone

    @property
    def voter_section(self):
        section = None
        try:
            section = self.dados_especificos.get(especificidade=TITULO_ELEITOR_SECAO)
        except Exception:
            log.warning("Seção de título não encontrado.")
        return section

    @property
    def voter_city(self):
        city = None
        try:
            city = self.dados_especificos.get(especificidade=TITULO_ELEITOR_MUNICIPIO)
        except Exception:
            log.warning("Município de título não encontrado.")
        return city

    @property
    def voter_city_local(self):
        city = None
        try:
            city = Localidade.objects.get(pk=self.voter_city.valor)
        except Exception:
            log.warning("Município de título não encontrado.")
        return city

    @property
    def voter_state(self):
        uf = None
        if self.voter_city_local and self.voter_city_local.estado:
            uf = self.voter_city_local.estado
        else:
            log.warning("Município de título não encontrado.")
        return uf

    @property
    def reservist_class(self):
        reservist_class = None
        try:
            reservist_class = self.dados_especificos.get(
                especificidade=RESERVISTA_CLASSE
            )
        except Exception:
            log.warning("Município de título não encontrado.")
        return reservist_class

    def validate(self, **kargs):
        if self.pk is not None:
            self.validate_relationship_with_person()
        self.validate_cnh_len()
        self.validate_mandatory(**kargs)
        return True

    def validate_relationship_with_person(self):
        self.natural_person.validate_perm_person()

    def validate_perm_person(self):
        return self.validate_relationship_with_person()

    def validate_cnh_len(self):
        if (
            self.tipo_documento == CNH
            and self.numero
            and len(self.numero) != self.cnh_max_len
        ):
            raise Exception(
                f"Por favor preencha corretamente o campo CNH, deve ser {self.cnh_max_len} caracteres."
            )
        return True

    def validate_mandatory(self, **kargs):
        if kargs.get("validate_mandatory", True):
            self.validate_mandatory_ctps()
            self.validate_mandatory_cpf()
            self.validate_mandatory_professional_council()
            self.validate_mandatory_cnh()
            self.validate_mandatory_voter()
            self.validate_mandatory_rg()
        return True

    @deprecated
    def validate_mandatory_nis(self):
        if (
            (self.is_from_employee or self.is_from_dependent)
            and self.is_nis
            and not self.numero
            and not self.natural_person.pis_pasep
        ):
            raise Exception("Preencha NIS ou PIS/PASEP. Um deles deve ser preenchido.")
        return True

    def validate_mandatory_ctps(self):
        if self.is_from_employee and self.is_ctps:
            self.validate_mandatory_ctps_number()
            self.validate_mandatory_ctps_series()
            self.validate_mandatory_ctps_state()
        return True

    def validate_mandatory_ctps_number(self):
        if self.is_from_employee and self.is_ctps:
            if not self.numero:
                raise Exception("Por favor preencha o campo CTPS - Número.")
        return True

    def validate_mandatory_ctps_series(self):
        if self.is_from_employee and self.is_ctps:
            if self.pk and not self.ctps_series:
                raise Exception("Por favor preencha o campo CTPS - Série.")
        return True

    def validate_mandatory_ctps_state(self):
        if self.is_from_employee and self.is_ctps:
            if self.pk and not self.estado_expedicao:
                raise Exception("Por favor preencha o campo CTPS - UF.")
        return True

    def validate_mandatory_rg(self):
        if self.is_from_employee and self.is_rg:
            self.validate_mandatory_rg_number()
            self.validate_mandatory_rg_issuer()
            self.validate_mandatory_rg_state()
            self.validate_mandatory_rg_date_expedition()
        return True

    def validate_mandatory_rg_number(self):
        if self.is_from_employee and self.is_rg:
            if not self.numero:
                raise Exception("Preencha o campo RG - Número.")
        return True

    def validate_mandatory_rg_issuer(self):
        if self.is_from_employee and self.is_rg:
            if self.pk and not self.rg_issuer:
                raise Exception("Preencha o campo RG - Emissor.")
        return True

    def validate_mandatory_rg_state(self):
        if self.is_from_employee and self.is_rg:
            if self.pk and not self.estado_expedicao:
                raise Exception("Preencha o campo RG - UF")
        return True

    def validate_mandatory_rg_date_expedition(self):
        if self.is_from_employee and self.is_rg:
            if self.pk and not self.data_expedicao:
                raise Exception("Preencha o campo RG - Data Expedição")
        return True

    @deprecated
    def validate_mandatory_ric(self):
        if self.is_from_employee and self.is_ric:
            self.validate_mandatory_ric_number()
            self.validate_mandatory_ric_issuer()
        return True

    @deprecated
    def validate_mandatory_ric_number(self):
        if self.is_from_employee and self.is_ric:
            if not self.numero:
                raise Exception("Preencha o campo RIC - Número.")
        return True

    @deprecated
    def validate_mandatory_ric_issuer(self):
        if self.is_from_employee and self.is_ric:
            if self.pk and not self.ric_issuer:
                raise Exception("Preencha o campo RIC - Emissor.")
        return True

    @deprecated
    def validate_mandatory_rne(self):
        if self.is_from_employee and self.is_rne:
            self.validate_mandatory_rne_number()
            self.validate_mandatory_rne_issuer()
        return True

    @deprecated
    def validate_mandatory_rne_number(self):
        if self.is_from_employee and self.is_rne:
            if not self.numero:
                raise Exception("Preencha o campo RNE - Número.")
        return True

    @deprecated
    def validate_mandatory_rne_issuer(self):
        if self.is_from_employee and self.is_rne:
            if self.pk and not self.rne_issuer:
                raise Exception("Preencha o campo RNE - Emissor.")
        return True

    def validate_mandatory_cpf(self):
        if self.is_from_employee and self.is_cpf and not self.numero:
            raise Exception("Preencha o campo CPF - Número.")
        return True

    def validate_mandatory_professional_council(self):
        if self.is_from_employee and self.is_professional_council:
            self.validate_mandatory_professional_council_number()
            self.validate_mandatory_professional_council_issuer()
        return True

    def validate_mandatory_professional_council_number(self):
        if self.is_from_employee and self.is_professional_council:
            if not self.numero:
                raise Exception("Preencha o campo Conselho profissional - Número.")
        return True

    def validate_mandatory_professional_council_issuer(self):
        if self.is_from_employee and self.is_professional_council:
            if self.pk and not self.professional_council_issuer:
                raise Exception("Preencha o campo Conselho profissional - Emissor.")
        return True

    def validate_mandatory_cnh(self):

        if self.naturalpersons.first().servidor_set.first().type_by_possession != "COE":
            return True

        if self.is_from_employee and self.is_cnh:
            self.validate_mandatory_cnh_number()
            self.validate_mandatory_cnh_date_validity()
            self.validate_mandatory_cnh_state()
            self.validate_mandatory_cnh_category()
        return True

    def validate_mandatory_cnh_number(self):
        if self.is_from_employee and self.is_cnh:
            if not self.numero:
                raise Exception("Preencha o campo CNH - Número.")
        return True

    def validate_mandatory_cnh_category(self):
        if self.is_from_employee and self.is_cnh:
            if self.pk and not self.cnh_category:
                raise Exception("Por favor preencha o campo CNH - Categoria.")
            elif self.cnh_category and self.cnh_category.valor not in list(
                CNH_CATEGORY_TYPE.values()
            ):
                raise Exception(
                    "Por favor preencha o campo CNH - Categoria com valor válido."
                )
        return True

    def validate_mandatory_cnh_date_validity(self):
        if self.is_from_employee and self.is_cnh:
            if not self.data_validade:
                raise Exception("Por favor preencha o campo CNH - Data de validade.")
        return True

    def validate_mandatory_cnh_state(self):
        if self.is_from_employee and self.is_cnh:
            if not self.estado_expedicao:
                raise Exception("Por favor preencha o campo CNH - UF.")
        return True

    def validate_pis_pasep(self):
        if self.is_from_employee and self.is_pis_pasep:
            if (
                not self.numero
                and self.natural_person
                and self.natural_person.employee.type_by_possession == "CMS"
            ):
                raise Exception("Por favor preencha o campo PIS/PASEP.")
        return True

    def validate_mandatory_voter(self):
        if self.is_from_employee and self.is_voter:
            self.validate_mandatory_voter_number()
            self.validate_mandatory_voter_zone()
            self.validate_mandatory_voter_section()
            self.validate_mandatory_voter_city()
            self.validate_mandatory_voter_state()
        return True

    def validate_mandatory_voter_number(self):
        if self.is_from_employee and self.is_voter:
            if not self.numero:
                raise Exception("Preencha o campo Título de Eleitor - Número.")
        return True

    def validate_mandatory_voter_zone(self):
        if self.is_from_employee and self.is_voter:
            if self.pk and not self.voter_zone:
                raise Exception("Preencha o campo Títulor de Eleitor - Zona.")
        return True

    def validate_mandatory_voter_section(self):
        if self.is_from_employee and self.is_voter:
            if self.pk and not self.voter_section:
                raise Exception("Preencha o campo Títulor de Eleitor - Seção.")
        return True

    def validate_mandatory_voter_city(self):
        if self.is_from_employee and self.is_voter:
            if self.pk and not self.voter_city:
                raise Exception("Preencha o campo Títulor de Eleitor - Município.")
        return True

    def validate_mandatory_voter_state(self):
        if self.is_from_employee and self.is_voter:
            if self.pk and not self.voter_state:
                raise Exception("Preencha o campo Títulor de Eleitor - Uf.")
        return True

    @classmethod
    def validate_mandatory_digital_document(cls, employee, exclude=[]):
        # TODO: CRIAR UMA VALIDAÇÃO PARA CADA CAMPO(TIPO)
        from copy import deepcopy

        message = ""
        digital_document_mandatory = deepcopy(Documento.digital_document_mandatory)
        for ex in exclude:
            try:
                digital_document_mandatory.remove(ex)
            except Exception:
                pass
        result = DigitalDocumentNaturalPerson.objects.filter(
            employee=employee, document_type__in=digital_document_mandatory, active=True
        )
        for value in digital_document_mandatory:
            found = result.filter(document_type=value).exists()
            if value in [RG, CPF, TITULO_ELEITOR] and not found:
                message += (
                    " É necessário anexar documento digital %s."
                    % DOCUMENTO_CHOICES.get(value)
                )
            elif (
                value == CNH
                and not found
                and employee.posses_ativas.filter(
                    quadro__cargo__codigo__in=["OFD", "MOT", "XXXMOT", "25c", "MOP"]
                ).exists()
            ):
                message += (
                    " É necessário anexar documento digital %s."
                    % DOCUMENTO_CHOICES.get(value)
                )
            elif (
                value == RESERVISTA
                and not found
                and employee.pessoa_fisica.sexo == "M"
                and (date.today().year - employee.pessoa_fisica.data_nascimento.year)
                < 45
            ):
                message += (
                    " É necessário anexar documento digital %s."
                    % DOCUMENTO_CHOICES.get(value)
                )
            elif (
                value == PROFESSIONAL_COUNCIL
                and not found
                and employee.posses_ativas.filter(
                    quadro__requires_profissional_council=True
                ).exists()
            ):
                message += (
                    " É necessário anexar documento digital %s."
                    % DOCUMENTO_CHOICES.get(value)
                )
        if message:
            raise Exception(message)
        return True

    def validate_document_not_unique(self, naturalpersons=[]):
        type_document_not_unique = []
        if not naturalpersons:
            naturalpersons = [
                nat.get("pk") for nat in self.naturalpersons.filter().values("pk")
            ]
        naturalpersons = PessoaFisica.objects.filter(pk__in=naturalpersons)
        for naturalperson in naturalpersons:
            if naturalperson.is_servidor():
                docs = Documento.objects.filter(
                    tipo_documento=self.tipo_documento,
                    naturalpersons__pk=naturalperson.pk,
                ).exclude(tipo_documento__in=type_document_not_unique)
                if docs.exists():
                    raise Exception(
                        "Não é permitido mais de um %s"
                        % self.get_tipo_documento_display()
                    )
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        if "validate_mandatory" not in kargs:
            kargs.update({"validate_mandatory": True})

        self.validate(**kargs)

        if "validate_mandatory" in kargs:
            kargs.pop("validate_mandatory")
        super(Documento, self).save(*args, **kargs)
        # self.update_natural_person_cache()

    def update_natural_person_cache(self):
        """
        :py:function:: update_natural_person_cache(self)

        This method updates natural person cpf or rg data.

        :return: True if not
        :rtype: boolean
        :raises Exception: if there are at least one
        """
        try:
            naturalperson = self.naturalpersons.get()
            if self.is_rg and (
                naturalperson.rg != self.numero
                or naturalperson.rg_data_expedicao != self.data_expedicao
                or naturalperson.rg_uf != self.estado_expedicao
            ):
                PessoaFisica.objects.filter(pk=naturalperson.pk).update(
                    rg=self.numero,
                    rg_data_expedicao=self.data_expedicao,
                    rg_uf=self.estado_expedicao,
                )
            if self.is_cpf and naturalperson.cpf != self.numero:
                PessoaFisica.objects.filter(pk=naturalperson.pk).update(cpf=self.numero)
        except Exception as err:
            log.exception(err)


class DocumentSpecialized(Documento):
    class Meta:
        proxy = True

    @classmethod
    def _concat_dict(cls, errors={}, err=None):
        if not isinstance(err, ValidationError):
            raise Exception("err parameter is not ValidationError")
        error_dict = err.error_dict
        for key in list(error_dict.keys()):
            errors[key] = error_dict[key]
        return errors

    @property
    def is_from_employee(self):
        return True

    def validate(self, **kargs):
        return True

    def validate_cnh_len(self):
        try:
            super(DocumentSpecialized, self).validate_cnh_len()
        except Exception as err:
            raise ValidationError({"cnh": err})
        return True

    def validate_mandatory_nis(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_nis()
        except Exception as err:
            raise ValidationError({"nis": err})
        return True

    def validate_mandatory_ctps_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_ctps_number()
        except Exception as err:
            raise ValidationError({"ctps": err})
        return True

    def validate_mandatory_ctps_series(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_ctps_series()
        except Exception as err:
            raise ValidationError({"serie_ctps": err})
        return True

    def validate_mandatory_ctps_state(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_ctps_state()
        except Exception as err:
            raise ValidationError({"ctps_state": err})
        return True

    def validate_mandatory_rg_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rg_number()
        except Exception as err:
            raise ValidationError({"rg": err})
        return True

    def validate_mandatory_rg_issuer(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rg_issuer()
        except Exception as err:
            raise ValidationError({"rg_orgao": err})
        return True

    def validate_mandatory_rg_state(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rg_state()
        except Exception as err:
            raise ValidationError({"rg_uf": err})
        return True

    def validate_mandatory_rg_date_expedition(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rg_date_expedition()
        except Exception as err:
            raise ValidationError({"rg_data_expedicao": err})
        return True

    @deprecated
    def validate_mandatory_ric_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_ric_number()
        except Exception as err:
            raise ValidationError({"ric": err})
        return True

    @deprecated
    def validate_mandatory_ric_issuer(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_ric_issuer()
        except Exception as err:
            raise ValidationError({"ric_issuer": err})
        return True

    @deprecated
    def validate_mandatory_rne_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rne_number()
        except Exception as err:
            raise ValidationError({"rne": err})
        return True

    @deprecated
    def validate_mandatory_rne_issuer(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_rne_issuer()
        except Exception as err:
            raise ValidationError({"rne_issuer": err})
        return True

    def validate_mandatory_cpf(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_cpf()
        except Exception as err:
            raise ValidationError({"cpf": err})
        return True

    def validate_mandatory_professional_council_number(self):
        try:
            super(
                DocumentSpecialized, self
            ).validate_mandatory_professional_council_number()
        except Exception as err:
            raise ValidationError({"professional_council": err})
        return True

    def validate_mandatory_professional_council_issuer(self):
        try:
            super(
                DocumentSpecialized, self
            ).validate_mandatory_professional_council_issuer()
        except Exception as err:
            raise ValidationError({"professional_council_issuer": err})
        return True

    def validate_mandatory_cnh_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_cnh_number()
        except Exception as err:
            raise ValidationError({"cnh": err})
        return True

    def validate_mandatory_cnh_category(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_cnh_category()
        except Exception as err:
            raise ValidationError({"cnh_categoria": err})
        return True

    def validate_mandatory_cnh_date_validity(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_cnh_date_validity()
        except Exception as err:
            raise ValidationError({"cnh_validity_date": err})
        return True

    def validate_mandatory_cnh_state(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_cnh_state()
        except Exception as err:
            raise ValidationError({"cnh_state": err})
        return True

    def validate_pis_pasep(self):
        try:
            super(DocumentSpecialized, self).validate_pis_pasep()
        except Exception as err:
            raise ValidationError({"pis_pasep": err})
        return True

    def validate_mandatory_voter_number(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_voter_number()
        except Exception as err:
            raise ValidationError({"titulo_eleitor": err})
        return True

    def validate_mandatory_voter_zone(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_voter_zone()
        except Exception as err:
            raise ValidationError({"zona_eleitor": err})
        return True

    def validate_mandatory_voter_section(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_voter_section()
        except Exception as err:
            raise ValidationError({"secao_titulo": err})
        return True

    def validate_mandatory_voter_city(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_voter_city()
        except Exception as err:
            raise ValidationError({"municipio_titulo": err})
        return True

    def validate_mandatory_voter_state(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_voter_state()
        except Exception as err:
            raise ValidationError({"municipio_titulo": err})
        return True

    def validate_mandatory_digital_document(self):
        try:
            super(DocumentSpecialized, self).validate_mandatory_digital_document()
        except Exception as err:
            raise ValidationError({"err": err})
        return True

    def full_clean_fields(self, exclude=None, validate_unique=True):
        super(DocumentSpecialized, self).full_clean_fields(
            exclude=exclude, validate_unique=validate_unique
        )

    def clean_fields(self, exclude=None):
        super(DocumentSpecialized, self).clean_fields(exclude=exclude)

    def clean(self):
        errors = {}
        try:
            self.validate_cnh_len()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_ctps_number()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_ctps_series()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_ctps_state()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cpf()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_professional_council()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_professional_council_number()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_professional_council_issuer()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_number()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_date_validity()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_state()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_cnh_category()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_pis_pasep()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_number()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_zone()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_section()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_city()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        try:
            self.validate_mandatory_voter_state()
        except ValidationError as err:
            errors = DocumentSpecialized._concat_dict(errors, err)
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        super(DocumentSpecialized, self).save(*args, **kwargs)


class Telefone(AuditTimestampModel):
    tipo_telefone = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_PHONE"),
        verbose_name="Tipo de Telefone",
    )
    numero = models.CharField(
        max_length=15, verbose_name="Número", default="", blank=False
    )
    publico = models.BooleanField(default=False, verbose_name="Público", blank=True)
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    description = models.CharField(
        max_length=80, verbose_name="Descrição", default="", blank=True
    )
    main = models.BooleanField(default=False, verbose_name="Principal", blank=True)
    kinship = models.CharField(
        verbose_name="Grau de Parentesco",
        help_text="Informação de grau de parentesco para o contato de emergência",
        max_length=24,
        blank=True,
        null=True,
    )
    person = models.ForeignKey(
        "Pessoa",
        verbose_name="Pessoa",
        related_name="phone",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    general_organ = models.ForeignKey(
        "OrgaoGeral",
        verbose_name="Orgão Geral",
        related_name="phone",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Telefone"

    def __str__(self):
        return "%s" % self.numero

    def get_number_formated(self):
        numero = re.sub("[^0-9]+", "", self.numero)
        return "(%(ddd)s) %(prefix)s-%(number)s" % {
            "ddd": numero[0:2],
            "prefix": numero[2:7] if len(numero) == 11 else numero[2:6],
            "number": numero[7:] if len(numero) == 11 else numero[6:],
        }

    def validate_relationship_with_person(self):
        if hasattr(self.person, "pessoafisica"):
            employee = self.person.pessoafisica.servidor_set.filter(ativo=True).last()
            user = get_current_user()
            if employee == employee_from_user(user):
                log.info("%s - Permissão para manipular o próprio telefone." % user)
            else:
                self.person.pessoafisica.validate_perm_person()
        elif hasattr(self.person, "pessoajuridica"):
            self.person.pessoajuridica.validate_perm_person()

    def validate_relationship_with_general_organ(self):
        if self.general_organ:
            self.general_organ.validate_general_organ()

    def validate_phone(self):
        if not self.numero:
            raise Exception("Número deve ser preenchido.")
        elif self.numero and len(self.numero) < 8:
            raise Exception("Número deve ter entre 8 e 15 dígitos.")
        return True

    def validate(self):
        self.validate_relationship_with_general_organ()
        self.validate_relationship_with_person()
        self.validate_phone()

    def save(self, *args, **kwargs):
        if not (self.person or self.general_organ):
            raise Exception(
                "Não é possível salvar o Telefone sem definir a quem o pertence."
            )
        self.validate()

        if self.pk:
            self._registrar_alteracao_esocial()

        super(Telefone, self).save(*args, **kwargs)

    def _registrar_alteracao_esocial(self):
        from datetime import datetime

        old_registro = Telefone.objects.get(pk=self.pk)
        valor = getattr(old_registro, "numero")
        novo_valor = getattr(self, "numero")
        if self.person and valor != novo_valor:
            PessoaFisica.objects.filter(pk=self.person.pk).update(
                data_alteracao_esocial=datetime.today()
            )

    def delete(self, *args, **kwargs):
        self.validate()
        super(Telefone, self).delete(*args, **kwargs)


class Endereco(AuditTimestampModel):
    """
    Qualquer entidade que necessite pode ter um endereço.
    """

    outsider = models.BooleanField(verbose_name="Exterior", default=False, blank=True)
    tipo_endereco = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_ADDRESS"),
        verbose_name="Tipo do Endereço",
    )
    tipo_logradouro = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_STREET"),
        verbose_name="Tipo do Logradouro",
    )
    municipio = models.ForeignKey(
        "Localidade", null=True, blank=True, on_delete=models.CASCADE
    )
    cep = models.CharField(max_length=10, verbose_name="CEP", null=True, blank=False)
    logradouro = models.CharField(max_length=100, null=True, blank=False)
    numero = models.CharField(
        max_length=12, blank=True, null=True, verbose_name="Número"
    )
    bairro = models.CharField(max_length=50, null=True, blank=True)
    complemento = models.CharField(max_length=2000, blank=True, null=True)
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    person = models.ForeignKey(
        "Pessoa",
        verbose_name="Pessoa",
        related_name="address",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    general_organ = models.ForeignKey(
        "OrgaoGeral",
        verbose_name="Orgão Geral",
        related_name="address",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    country = models.ForeignKey(
        "Pais",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="address",
        verbose_name="País(Residentes no Exterior)",
    )
    outsider_citty = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Cidade no Exterior"
    )

    class Meta:
        verbose_name = "Endereço"

    def __str__(self):
        end = []
        citty = ""
        if self.municipio:
            citty = self.municipio
        elif self.outsider_citty:
            citty = self.outsider_citty
        end.append(
            " - ".join(
                [
                    "%s" % self.logradouro,
                    self.numero if self.numero else "S/N",
                    "CEP: %s" % self.cep if self.cep else "",
                    "%s" % self.bairro,
                    "%s" % citty,
                ]
            )
        )

        return (
            end[0]
            if not self.country
            else ("%s%s" % (end[0], ". País: %s" % self.country))
        )

    def unicode(self):

        if self.outsider:
            return f"{self.get_tipo_endereco_display()} - {self.logradouro}, {self.numero} - {self.bairro} - / {self.outsider_citty  or ''} - {self.country.nome}"
        else:
            return f"{self.get_tipo_endereco_display()} - {self.logradouro}, {self.numero} - {self.bairro} - {self.municipio.__str__()} - {self.cep}"

    def validate_relationship_with_person(self):
        if hasattr(self.person, "pessoafisica"):
            employee = self.person.pessoafisica.servidor_set.filter(ativo=True).last()
            user = get_current_user()
            if employee == employee_from_user(user):
                log.info("%s - Permissão para manipular o próprio endereço." % user)
            else:
                self.person.pessoafisica.validate_perm_person()
        elif hasattr(self.person, "pessoajuridica"):
            self.person.pessoajuridica.validate_perm_person()

    def validate_relationship_with_general_organ(self):
        if self.general_organ:
            self.general_organ.validate_general_organ()

    def validate_mandatory_for_employee(self):
        if self.person and self.person.is_servidor():
            if not self.logradouro:
                raise Exception("Logradouro é obrigatório.")
            elif not self.numero:
                raise Exception("Número é obrigatório.")
            elif not self.outsider and not self.municipio:
                raise Exception("Município é obrigatório.")

            if self.outsider:
                if not self.country:
                    raise Exception("País é obrigatório.")
                if not self.outsider_citty:
                    raise Exception("Cidade no Exterior é obrigatório.")
            else:
                if not self.tipo_logradouro:
                    raise Exception("Tipo logradouro é obrigatório.")
                elif not self.cep:
                    raise Exception("CEP é obrigatório.")
                elif len(self.cep) < 8:
                    raise Exception("Preencha o campo CEP com 8 dígitos.")
                elif not self.cep.isdigit():
                    raise Exception("Preencha o campo CEP apenas com dígitos.")
                elif self.municipio and not self.municipio.ibge:
                    raise Exception("Município - Código do IBGE é obrigatório.")
                elif self.municipio and not self.municipio.estado:
                    raise Exception("Município - Estado é obrigatório.")
        return True

    def validate(self):
        self.validate_relationship_with_person()
        self.validate_relationship_with_general_organ()
        self.validate_mandatory_for_employee()

    def save(self, *args, **kwargs):
        self.cep = (
            self.cep.lstrip().replace(".", "").replace("-", "").replace(" ", "")
            if self.cep
            else None
        )
        self.logradouro = " ".join(self.logradouro.split()) if self.logradouro else None
        self.numero = self.numero.lstrip() if self.numero else None
        self.bairro = " ".join(self.bairro.split()) if self.bairro else None
        self.complemento = (
            " ".join(self.complemento.split()) if self.complemento else None
        )
        self.outsider_citty = (
            " ".join(self.outsider_citty.split()) if self.outsider_citty else None
        )

        if not (self.person or self.general_organ):
            raise Exception(
                "Não é possível salvar o Endereço sem definir a quem o pertence."
            )
        self.validate()

        if self.outsider:
            self.tipo_logradouro = 100

        if self.pk:
            self._registrar_alteracao_esocial()

        super(Endereco, self).save(*args, **kwargs)

    def _registrar_alteracao_esocial(self):
        from datetime import datetime

        old_registro = Endereco.objects.get(pk=self.pk)
        campos = [
            "tipo_logradouro",
            "tipo_endereco",
            "municipio",
            "logradouro",
            "bairro",
            "cep",
            "numero",
            "complemento",
            "outsider",
            "outsider_citty",
        ]
        for campo in campos:
            valor = getattr(old_registro, campo)
            novo_valor = getattr(self, campo)
            if self.person and valor != novo_valor:
                PessoaFisica.objects.filter(pk=self.person.pk).update(
                    data_alteracao_esocial=datetime.today()
                )
                break

    def delete(self, *args, **kwargs):
        self.validate()
        super(Endereco, self).delete(*args, **kwargs)


class DadoBancarioConsignatario(DadoBancario):
    pessoa_juridica = models.ForeignKey("PessoaJuridica", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Dado bancário de consignatário"
        db_table = "rh_dadobancariocons"


@to_search(
    [
        {"name": "pessoa__nome", "type": "text"},
        {"name": "banco__nome", "type": "text"},
        {"name": "tipo_conta", "type": "choices"},
        {"name": "agencia", "type": "text"},
        {"name": "conta_corrente_completa", "type": "text"},
    ]
)
class DadoBancarioPessoa(DadoBancario):
    pessoa = models.ForeignKey(
        "Pessoa", related_name="dadosbancarios", on_delete=models.CASCADE
    )
    principal = models.BooleanField(verbose_name="Principal", default=False, blank=True)

    class Meta:
        verbose_name = "Dado bancário de pessoa"
        db_table = "rh_dadobancariopessoa"

    def __str__(self):

        if self.agencia_numero and self.conta_numero:
            ag = self.agencia_str
            conta = self.conta_str
            return f"{self.banco} - {self.tipo_conta} - Ag: {ag} - Conta: {conta}"

        return "{banco_numero} - Ag: {agencia} - Número: {numero}".format(
            banco_numero=self.banco.numero,
            agencia=self.agencia,
            numero=self.conta_corrente_completa,
        )


class Curso(CObject):
    area_conhecimento = models.ForeignKey(
        "gecap.AreaConhecimento",
        on_delete=models.CASCADE,
        verbose_name="Área de conhecimento",
        null=True,
    )
    grau_instrucao = models.IntegerField(
        default=1,
        choices=[
            (x[0], x[1]) for x in list(GRAU_INSTRUCAO_CHOICES.items()) if x[0] != 14
        ],
        null=True,
        blank=True,
        verbose_name="Grau de Instrução",
    )

    class Meta:
        verbose_name = "Curso"

    def __str__(self):
        return "%s" % self.nome


class TipoServidor(CObject):
    """
    Modelo semelhante à entidade SERVIDOR_TIPO do Arquimedes.
    """

    class Meta:
        verbose_name = "Tipo de servidor"
        ordering = ["nome"]

    entrancia = models.ForeignKey(
        "Entrancia",
        verbose_name="Entrância",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    instancia = models.ForeignKey(
        "Instancia",
        verbose_name="Instância",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    indicativo = models.CharField(max_length=1, choices=INDICATIVO, default="S")


class CareerManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, codigo, *args):
        return self.get(codigo=codigo)


class Carreira(CObject):
    codigo = models.CharField(
        max_length=10, verbose_name="Código", default="", blank=False
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True)
    publication = models.ForeignKey(
        "Publicacao",
        on_delete=models.CASCADE,
        related_name="career_publication",
        null=True,
        blank=True,
        verbose_name="Publicação",
    )
    active = models.BooleanField(default=True, blank=True)

    # DEPRECATED
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    publication_extinction = models.ForeignKey(
        "Publicacao",
        on_delete=models.CASCADE,
        related_name="career_publication_extinction",
        null=True,
        blank=True,
        verbose_name="Publicação",
    )

    objects = CareerManager()

    class Meta:
        verbose_name = "Carreira"

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.data_inicio, date_end=self.data_fim
        )

    def natural_key(self):
        return (self.codigo,)

    def validate_repeated_cod(self):
        """
        :py:function:: validate_repeated_cod(self)

        This method validates repeated cod of the job_position.

        :return boolean True
        :rtype: boolean
        :raises Exception: if cod is repeated
        """
        if not self.pk and Carreira.objects.filter(codigo=self.codigo).exists():
            raise Exception(
                "Código da Carreira repetido. Por favor escolha outra combinação."
            )
        return True

    def validate(self):
        return self.validate_repeated_cod()

    def save(self, *args, **kargs):
        self.validate()
        self.active = self.is_active()
        super(Carreira, self).save(*args, **kargs)

    def get_configs(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        configs = self.configs.exclude(
            Q(start_validity__gt=end_date)
            | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
        ).order_by("start_validity")
        return configs

    @property
    def current_config(self):
        return self.get_configs().last()


class ConfigCareer(AuditTimestampModel):
    career = models.ForeignKey(
        "Carreira", related_name="configs", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, verbose_name="Código")
    publication_restructuring = models.ForeignKey(
        "Publicacao",
        on_delete=models.CASCADE,
        related_name="config_career_publication_restructuring",
        null=True,
        blank=True,
        verbose_name="Publicação",
    )

    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return "%s - %s: %s" % (
            self.start_validity.strftime("%d/%m/%Y"),
            self.end_validity.strftime("%d/%m/%Y") if self.end_validity else "---",
            self.career,
        )

    @property
    def next(self):
        return (
            self.career.configs.filter(start_validity__gt=self.start_validity)
            .order_by("start_validity")
            .first()
        )

    @property
    def previous(self):
        return (
            self.career.configs.filter(start_validity__lt=self.start_validity)
            .order_by("start_validity")
            .last()
        )

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.start_validity, date_end=self.end_validity
        )

    def save(self, *args, **kwargs):
        if self.previous and self.previous.end_validity is None:
            p = self.previous
            p.end_validity = self.start_validity - relativedelta(days=1)
            p.save()
        if self.next and (
            self.end_validity is None or self.end_validity >= self.next.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo! (%s)"
                % (self.next, self.career.codigo)
            )
        if self.previous and (
            self.previous.end_validity is None
            or self.previous.end_validity >= self.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo(%s)"
                % (self.previous, self.career.codigo)
            )

        active = self.is_active()

        self.active = active

        log.debug("SAVING %s" % self)
        super(ConfigCareer, self).save(*args, **kwargs)

        career = self.career
        career.active = active
        career.data_inicio = (
            self.career.configs.first().start_validity
            if self.career.configs.first()
            else self.start_validity
        )
        career.data_fim = (
            self.career.configs.last().end_validity
            if self.career.configs.last()
            else self.end_validity
        )
        if active:
            career.nome = self.name
            career.codigo = self.code
        career.save()


class JobPositionManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, codigo, *args):
        return self.get(codigo=codigo)


class Cargo(CObject):
    """
    Função está semelhante á entidade CARGO do Arquimedes + informações do sistema da folha.
    Possui relação com GrupoSalarial, através da entidade CargoHasGrupoSalarial em modelos da Folha.
    """

    class TabelaSalarialNotFound(Exception):
        pass

    class Meta:
        verbose_name = "Cargo"
        ordering = ["nome"]

    carreira = models.ForeignKey(
        "Carreira", null=True, blank=True, on_delete=models.CASCADE
    )
    indicativo = models.CharField(
        max_length=1, choices=INDICATIVO, null=False, default="S"
    )
    tipo_lei_cargo = models.CharField(
        max_length=2, choices=(TIPO_LEI_CARGO), default="EF"
    )
    codigo = models.CharField(max_length=12, verbose_name="Código", default="")
    ativo = models.BooleanField(default=True, blank=True)
    lotacao_responsavel = models.ForeignKey(
        "Lotacao",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cargo_responsavel",
        verbose_name="Responsável pela Lotação",
    )
    unidade_administrativa = models.ForeignKey(
        "UnidadeAdministrativa",
        verbose_name="Órgão",
        null=True,
        on_delete=models.CASCADE,
    )
    poder = models.IntegerField(
        default=5, choices=Choice.get_choices_for("rh", "LEVEL_STATE")
    )
    cargo_arquimedes = models.IntegerField(default=0)
    publication = models.ForeignKey(
        "Publicacao", related_name="publication", null=True, on_delete=models.PROTECT
    )
    publication_change = models.ForeignKey(
        "Publicacao",
        related_name="publication_change",
        null=True,
        on_delete=models.PROTECT,
    )
    publication_extinction = models.ForeignKey(
        "Publicacao",
        related_name="publication_extinction",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    order_weight = models.SmallIntegerField(
        verbose_name="Peso ordenação", default=0, blank=True
    )

    objects = JobPositionManager()

    # DEPRECATED
    acumulavel = models.BooleanField(
        verbose_name="Acumulável", default=False, blank=True
    )
    professor = models.BooleanField(default=False, blank=True)
    designa_exercicio = models.BooleanField(
        default=True, blank=True, verbose_name="Designa Exercício"
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    chefia = models.BooleanField(default=False)
    substituivel = models.BooleanField(default=False, verbose_name="Substituível")
    cbo = models.ForeignKey("Cbo", null=True, blank=True, on_delete=models.CASCADE)
    remunerated = models.BooleanField(
        default=True, blank=True, verbose_name="Remunerado"
    )
    cumulative = models.PositiveSmallIntegerField(
        default=CUMULATIVE_NOT,
        verbose_name="Acumulável",
        choices=Choice.get_choices_for("rh", "CUMULATIVE"),
    )
    level_instance = models.PositiveSmallIntegerField(
        verbose_name="Entrância",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "LEVEL_INSTANCE"),
    )
    instance = models.PositiveSmallIntegerField(
        verbose_name="Instância",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "INSTANCE"),
    )
    entrancia = models.ForeignKey(
        "Entrancia",
        null=True,
        blank=True,
        verbose_name="Entrância",
        on_delete=models.CASCADE,
    )
    instancia = models.ForeignKey(
        "Instancia",
        null=True,
        blank=True,
        verbose_name="Instância",
        on_delete=models.CASCADE,
    )
    code_tce = models.IntegerField(verbose_name="Código TCE", null=True, blank=True)

    def __str__(self):
        if self.unidade_administrativa and self.unidade_administrativa.sigla:
            return "%s-%s" % (self.nome, self.unidade_administrativa.sigla)
        else:
            return self.nome

    def natural_key(self):
        return (self.codigo,)

    def validate(self):
        return self.validate_repeated_cod() and self.validate_foresight()

    def validate_repeated_cod(self):
        """
        :py:function:: validate_repeated_cod(self)

        This method validates repeated cod of the job_position.

        :return boolean True
        :rtype: boolean
        :raises Exception: if cod is repeated
        """
        if not self.pk and Cargo.objects.filter(codigo=self.codigo).exists():
            raise Exception(
                "Código do Cargo repetido. Por favor escolha outra combinação."
            )
        return True

    def validate_foresight(self):
        """
        :py:function:: validate_foresight(self)

        This method validates if administrative unit has foresight.

        :return boolean True
        :rtype: boolean
        :raises Exception: if foresight is None
        """
        if (
            self.tipo_lei_cargo in ("S", "M")
            and not self.unidade_administrativa.previdencia
        ):
            raise Exception(
                "A unidade administrativa do cargo não tem uma instituição previdenciária."
            )
        return True

    def validate_responsible(self):
        """
        :py:function:: validate_foresight(self)

        This method validates if job position has a workplace responsible.

        :return boolean True
        :rtype: boolean
        :raises Exception: if lotacao_responsavel is None
        """
        if self.indicativo == "M" and not self.lotacao_responsavel:
            raise Exception("Este cargo deve ser responsável por uma lotação.")
        return True

    def create_initial_config(self):
        if not self.configs.exists():
            self.configs.create(
                name=self.nome, code=self.codigo, start_validity=datetime.now().date()
            )

    def save(self, *args, **kargs):
        self.validate()
        new_obj = not self.pk
        super(Cargo, self).save(*args, **kargs)
        if new_obj:
            self.create_initial_config()

    def get_configs(self, start_date=None, end_date=None):
        dt_now = datetime.now().date()
        if start_date is None:
            start_date = dt_now
        if end_date is None:
            end_date = start_date

        configs = self.configs.exclude(
            Q(start_validity__gt=end_date)
            | (~Q(end_validity=None) & Q(end_validity__lt=start_date))
        ).order_by("start_validity")
        return configs

    @property
    def current_config(self):
        return self.get_configs().last()


class ConfigJobPosition(AuditTimestampModel):
    job_position = models.ForeignKey(
        Cargo, related_name="configs", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    level_instance = models.PositiveSmallIntegerField(
        verbose_name="Entrância",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "LEVEL_INSTANCE"),
    )
    instance = models.PositiveSmallIntegerField(
        verbose_name="Instância",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "INSTANCE"),
    )
    code = models.CharField(
        max_length=12, verbose_name="Código", default="", blank=True
    )
    designates_exercise = models.BooleanField(
        default=True, blank=True, verbose_name="Designa Exercício"
    )
    boss = models.BooleanField(default=False)
    replaceable = models.BooleanField(default=False, verbose_name="Substituível")
    cbo = models.ForeignKey("Cbo", null=True, on_delete=models.CASCADE)
    remunerated = models.BooleanField(
        default=True, blank=True, verbose_name="Remunerado"
    )
    cumulative = models.PositiveSmallIntegerField(
        default=CUMULATIVE_NOT,
        verbose_name="Acumulável",
        choices=Choice.get_choices_for("rh", "CUMULATIVE"),
    )
    publication_restructuring = models.ForeignKey(
        "Publicacao",
        related_name="publication_restructuring",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    quantity = models.IntegerField(
        verbose_name="Quantidade de Vagas", default=0, blank=True
    )
    educational_level = models.IntegerField(
        default=3,
        verbose_name="Nível de Escolaridade",
        choices=TIPO_NIVEL_ESCOLARIDADE,
        null=True,
    )
    workload = models.IntegerField(verbose_name="Carga Horária", default=40, blank=True)
    type_workload = models.IntegerField(
        default=2,
        blank=True,
        verbose_name="Tipo Carga Horária",
        choices=TIPO_CARGA_HORARIA,
    )
    health = models.BooleanField(default=False, blank=True)
    teacher = models.BooleanField(default=False, blank=True)
    military = models.BooleanField(default=False, blank=True)
    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return "%s - %s: %s" % (
            self.start_validity.strftime("%d/%m/%Y"),
            self.end_validity.strftime("%d/%m/%Y") if self.end_validity else "---",
            self.job_position,
        )

    @property
    def next(self):
        return (
            self.job_position.configs.exclude(pk=self.pk)
            .filter(start_validity__gt=self.start_validity)
            .order_by("start_validity")
            .first()
        )

    @property
    def previous(self):
        return (
            self.job_position.configs.exclude(pk=self.pk)
            .filter(start_validity__lt=self.start_validity)
            .order_by("start_validity")
            .last()
        )

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.start_validity, date_end=self.end_validity
        )

    def get_number_of_employees_in_config_job_position(self):
        """
        Função para verificar a quantidade de servidores que estão ativos
        e estão cadastrados sob essa configuração de cargo.
        :returns: (int) Quantidade de servidores/membros ativos que possuem
        essa configuração de cargo.
        """
        number_of_employees_in_config_job_position = 0
        for staff_type in self.job_position.quadro_set.filter(active=True):
            number_of_employees_in_config_job_position += (
                staff_type.vacancy_number_filled()
            )
        return number_of_employees_in_config_job_position

    def validate_number_of_employees(self):
        """
        Validação para impedir a diminuição da quantidade de vagas a um número menor
        que a quantidade hoje existente de servidores ativos.
        """
        if self.get_number_of_employees_in_config_job_position() > self.quantity:
            raise Exception(
                f"""
                Não será possível fazer a alteração, pois a quantidade de vagas preenchidas ({self.get_number_of_employees_in_config_job_position()})
                é maior que a quantidade máxima de vagas definida no cadastro ({self.quantity}).
                """
            )

    def validate(self):
        self.validate_number_of_employees()

    def save(self, *args, **kwargs):
        self.validate()
        if self.previous and self.previous.end_validity is None:
            p = self.previous
            p.end_validity = self.start_validity - relativedelta(days=1)
            p.save()
        if self.next and (
            self.end_validity is None or self.end_validity >= self.next.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo! (%s)"
                % (self.next, self.job_position.codigo)
            )
        if self.previous and (
            self.previous.end_validity is None
            or self.previous.end_validity >= self.start_validity
        ):
            raise Exception(
                "Periodo sobrepondo outro período (%s) não pode ser salvo(%s)"
                % (self.previous, self.job_position.codigo)
            )

        active = self.is_active()

        self.active = active

        log.debug("SAVING %s" % self)
        super(ConfigJobPosition, self).save(*args, **kwargs)

        job_position = self.job_position
        job_position.ativo = active
        if active:
            job_position.entrancia = Entrancia.objects.filter(
                nome=self.get_level_instance_display()
            ).first()
            job_position.instancia = Instancia.objects.filter(
                nome=self.get_instance_display()
            ).first()
            job_position.level_instance = self.level_instance
            job_position.instance = self.instance
            job_position.nome = self.name
            job_position.codigo = self.code
            job_position.professor = self.teacher
            job_position.designa_exercicio = self.designates_exercise
            job_position.data_alteracao = self.modified_at
            job_position.chefia = self.boss
            job_position.substituivel = self.replaceable
            job_position.cbo = self.cbo
            job_position.remunerated = self.remunerated
            job_position.cumulative = self.cumulative
        job_position.save()
        self.update_job_position_table()

    def update_job_position_table(self):
        # Atualiza quadro cargo
        position_table = self.job_position.quadros.first()
        if position_table:
            position_table.nivel_escolaridade = self.educational_level
            position_table.quantidade_vagas = self.quantity
            position_table.carga_horaria = self.workload
            position_table.tipo_carga_horaria = self.type_workload
            position_table.teacher = self.teacher
            position_table.health = self.health
            position_table.cbo = self.cbo
            position_table.save()


class AnotacaoGeral(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="anotacoes",
        on_delete=models.CASCADE,
    )
    tipo_documento = models.IntegerField(
        choices=(Choice.get_choices_for("rh", "TIPO_DOCUMENTO")),
        verbose_name="Tipo Documento",
    )
    numero_documento = models.CharField(
        max_length=20, null=True, blank=True, verbose_name="Número Documento"
    )
    data_documento = models.DateField(
        verbose_name="Data Documento", null=True, blank=True
    )
    publicacao = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        verbose_name="Publicação",
        on_delete=models.CASCADE,
    )
    data_portaria_inicio = models.DateField(
        null=True, blank=True, verbose_name="Data Portaria Início"
    )
    resumo = models.CharField(max_length=150, null=True, blank=True)
    texto = models.TextField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    numero_processo = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Número Processo"
    )
    indireto = models.BooleanField(default=False)
    movimento_origem = models.ForeignKey(
        "rh.MovimentacaoPessoal",
        related_name="anotacoes",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    my_type = models.CharField(max_length=60, db_index=True, null=True, blank=True)

    class Meta:
        verbose_name = "Anotação Geral"
        db_table = "rh_anotgeral"
        ordering = ("-id",)

    def __str__(self):
        return "%s - %s - %s%s" % (
            self.get_tipo_documento_display(),
            self.resumo,
            self.servidor,
            "%s" % ((" - %s" % self.numero_documento) if self.numero_documento else ""),
        )

    def __unicode_especializado__(self):
        return "%s - %s - NÚMERO: %s" % (
            self.get_tipo_documento_display(),
            self.resumo,
            self.numero_documento if self.numero_documento else "",
        )

    @property
    def my_origin(self):
        if self.pk:
            if hasattr(self, self.my_type):
                return getattr(self, self.my_type, self)
        return self

    @property
    def model_by_instance(self):
        """
        Este método é responsável por informar a instância baseado no mapeamento
        dos modelos.
        """
        instance = self
        if hasattr(instance, "anotacaocarreira"):
            instance = instance.anotacaocarreira
        elif hasattr(instance, "anotacaocomunicacao"):
            instance = instance.anotacaocomunicacao
        elif hasattr(instance, "anotacaoelogio"):
            instance = instance.anotacaoelogio
        elif hasattr(instance, "anotacaoenquadramento"):
            instance = instance.anotacaoenquadramento
        elif hasattr(instance, "anotacaoevento"):
            instance = instance.anotacaoevento
        elif hasattr(instance, "anotacaofalta"):
            instance = instance.anotacaofalta
        elif hasattr(instance, "anotacaoferias"):
            instance = instance.anotacaoferias
        elif hasattr(instance, "anotacaogratificacao"):
            instance = instance.anotacaogratificacao
        elif hasattr(instance, "anotacaohorarioespecial"):
            instance = instance.anotacaohorarioespecial
        elif hasattr(instance, "anotacaolicenca"):
            instance = instance.anotacaolicenca
        elif hasattr(instance, "anotacaopenadisciplinar"):
            instance = instance.anotacaopenadisciplinar
        elif hasattr(instance, "anotacaorecesso"):
            instance = instance.anotacaorecesso
        elif hasattr(instance, "anotacaofolgaeleitoral"):
            instance = instance.anotacaofolgaeleitoral
        elif hasattr(instance, "anotacaofolgaaniversario"):
            instance = instance.anotacaofolgaaniversario
        elif hasattr(instance, "anotacaofolgacompensacao"):
            instance = instance.anotacaofolgacompensacao
        elif hasattr(instance, "anotacaoBancodeHoras"):
            instance = instance.anotacaoBancodeHoras
        elif hasattr(instance, "anotacaoplantao"):
            instance = instance.anotacaoplantao
        elif hasattr(instance, "anotacaoviagem"):
            instance = instance.anotacaoviagem
        elif hasattr(instance, "anotacaoremocao"):
            instance = instance.anotacaoremocao
        elif hasattr(instance, "anotacaotempoDobro"):
            instance = instance.anotacaotempoDobro
        elif hasattr(instance, "anotacaotempoServico"):
            instance = instance.anotacaotempoServico
        elif hasattr(instance, "anotacaotransposicao"):
            instance = instance.anotacaotransposicao
        elif hasattr(instance, "anotacaoafastamento"):
            instance = instance.anotacaoafastamento
        elif hasattr(instance, "anotacaoausencia"):
            instance = instance.anotacaoausencia
        return instance

    def validate(self):
        self.validate_wright()
        return True

    def validate_wright(self):
        if self.pk and self.indireto:
            raise Exception("Esta anotação não pode ser alterada diretamente.")
        return True

    def save(self, *args, **kargs):
        try:
            if not self.data_documento:
                self.data_documento = date.today()
            self.my_type = self._meta.model_name
            self.validate()
            if self.pk is None:
                self.ativa = True
            if self.publicacao:
                self.numero_documento = self.publicacao.numero
                self.data_portaria_inicio = self.publicacao.data_vigencia
                self.tipo_documento = self.publicacao.tipo
            # else:
            #     self.tipo_documento = 100
            if not self.tipo_documento:
                self.tipo_documento = 99
            super(AnotacaoGeral, self).save(*args, **kargs)
        except Exception as err:
            log.exception(err)
            raise err

    @classmethod
    def manage_instance(cls, **kargs):
        anotacao_geral = None
        try:
            fieldnames = [field.name for field in cls._meta.get_fields()]
            pop = [k for k in kargs if k not in fieldnames]
            for to_pop in pop:
                kargs.pop(to_pop)
            anotacao_geral = cls(**kargs)
            anotacao_geral.save()
        except Exception as err:
            log.exception(err)
            raise err
        return anotacao_geral


class AnotacaoCarreira(AnotacaoGeral):
    class Meta:
        verbose_name = "Anotação Carreira"
        db_table = "rh_anotcarreira"
        ordering = ("-id",)


class AnotacaoComunicacao(AnotacaoGeral):
    tipo_comunicacao = models.IntegerField(
        default=4, choices=TIPO_COMUNICACAO, verbose_name="Tipo Comunicação"
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Comunicação"
        db_table = "rh_anotcomunicacao"


class AnotacaoElogio(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    responsavel = models.ForeignKey(
        "PessoaFisica", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Anotação Elogio"
        db_table = "rh_anotelogio"


class AnotacaoEnquadramento(AnotacaoGeral):
    quadro = models.ForeignKey("Quadro", on_delete=models.CASCADE)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    complemento_cargo = models.CharField(max_length=50, null=True, blank=True)
    lei = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = "Anotação Enquadramento"
        db_table = "rh_anotenquadramento"


class AnotacaoEvento(AnotacaoGeral):
    nome_evento = models.CharField(
        max_length=100, verbose_name="Nome Evento", default=""
    )
    tipo_participacao = models.IntegerField(
        choices=TIPO_PARTICIPACAO_EVENTO, verbose_name="Tipo de Participação"
    )
    tipo_evento = models.IntegerField(
        choices=TIPO_EVENTO, verbose_name="Tipo de Evento"
    )
    patrocinador = models.ForeignKey(
        "Patrocinador", null=True, blank=True, default=None, on_delete=models.CASCADE
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    carga_horaria = models.IntegerField(
        null=True, blank=True, verbose_name="Carga Horária"
    )
    instituicao = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Instituição"
    )
    efeito_progressao = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Efeito Progressão"
    )
    certificado = models.ForeignKey(
        "ged.Arquivo",
        null=True,
        blank=True,
        related_name="anotacao_evento",
        verbose_name="Certificado",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Anotação Evento"
        db_table = "rh_anotevento"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoEvento, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoFalta(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    abonada = models.BooleanField(default=False)
    dias = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Anotação Falta"
        db_table = "rh_anotfalta"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoFalta, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoFerias(AnotacaoGeral):
    tipo = models.CharField(
        blank=True,
        choices=list(TIPO_ANOTACAO_FERIAS.items()),
        verbose_name="Tipo",
        max_length=20,
        default="HOMOLOGACAO",
    )
    identificador = models.CharField(
        max_length=20, verbose_name="Identificador", null=True, blank=True
    )
    periodo = models.CharField(
        max_length=50, default="---", verbose_name="Período", blank=True
    )

    class Meta:
        verbose_name = "Anotação Férias"
        db_table = "rh_anotferias"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoFerias, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoGratificacao(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Anotação Gratificação"
        db_table = "rh_anotgratificacao"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoGratificacao, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotHorEspDados(AuditTimestampModel):
    dia_semana = models.IntegerField(
        choices=DIAS_SEMANA, null=True, blank=True, verbose_name="Dia da Semana"
    )
    turno = models.IntegerField(
        choices=TURNO, null=True, blank=True, verbose_name="Turno"
    )
    ent_saida = models.IntegerField(
        choices=ENTRADA_SAIDA, null=True, blank=True, verbose_name="Entrada/Saída"
    )
    horario = models.CharField(
        max_length=5, null=True, blank=True, verbose_name="Horário"
    )

    class Meta:
        verbose_name = "Dados específicos de AHE"

    def __str__(self):
        return "%s - %s - %s - %s" % (
            self.get_dia_semana_display(),
            self.get_turno_display(),
            self.get_ent_saida_display(),
            self.horario,
        )

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotHorEspDados, self).save(*args, **kargs)


class AnotacaoHorarioEspecial(AnotacaoGeral):
    dados_horario = models.ManyToManyField(
        "AnotHorEspDados", verbose_name="Dados Horário"
    )

    class Meta:
        verbose_name = "Anotação Horário Especial (AHE)"
        db_table = "rh_anothorarioespecial"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoHorarioEspecial, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoLicenca(AnotacaoGeral):
    prazo_dias = models.IntegerField(null=True, blank=True, verbose_name="Prazo Dias")
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    remunerada = models.BooleanField(default=True)
    quinquenio = models.IntegerField(null=True, blank=True, verbose_name="Quinquênio")

    class Meta:
        verbose_name = "Anotação Licença"
        db_table = "rh_anotlicenca"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoLicenca, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoPenaDisciplinar(AnotacaoGeral):
    penalidade = models.ForeignKey("Penalidade", on_delete=models.CASCADE)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    responsavel = models.ForeignKey(
        "Servidor",
        null=True,
        blank=True,
        verbose_name="Responsável",
        on_delete=models.CASCADE,
    )
    data_decisao = models.DateField(null=True, blank=True, verbose_name="Data Decisão")
    texto_decisao = models.TextField(
        null=True, blank=True, verbose_name="Texto Decisão"
    )

    class Meta:
        verbose_name = "Anotação Pena Disciplinar"
        db_table = "rh_anotpenadisciplinar"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoPenaDisciplinar, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoRecesso(AnotacaoGeral):
    ano = models.IntegerField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    data_reassuncao = models.DateField(
        null=True, blank=True, verbose_name="Data Reassunção"
    )
    periodo = models.CharField(
        max_length=10,
        choices=PERIODO_FERIAS_CHOICES,
        verbose_name="Período",
        default="1",
        blank=False,
    )
    situacao = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Situação"
    )

    class Meta:
        verbose_name = "Anotação Recesso"
        db_table = "rh_anotrecesso"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoRecesso, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoFolgaEleitoral(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Folga Eleitoral"
        db_table = "rh_anotfolgaeleitoral"


class AnotacaoFolgaAniversario(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Folga Aniversário"
        db_table = "rh_anotfolgaaniversario"


class AnotacaoFolgaCompensacao(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Folga Compensação"
        db_table = "rh_anotfolgacompensacao"


class AnotacaoBancoDeHoras(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Usufruto Banco de Horas"
        db_table = "rh_anotbancodehoras"


class AnotacaoPlantao(AnotacaoGeral):
    ano = models.IntegerField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    data_reassuncao = models.DateField(
        null=True, blank=True, verbose_name="Data Reassunção"
    )
    periodo = models.CharField(
        max_length=10,
        choices=PERIODO_FERIAS_CHOICES,
        verbose_name="Período",
        default="1",
    )
    situacao = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Situação"
    )

    class Meta:
        verbose_name = "Anotação Folga Eleitoral"
        db_table = "rh_anotplantao"


class AnotacaoViagem(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Viagem"
        db_table = "rh_anotviagem"


class AnotacaoRemocao(AnotacaoGeral):
    class Meta:
        verbose_name = "Anotação Remoção"
        db_table = "rh_anotremocao"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoRemocao, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoTempoDobro(AnotacaoGeral):
    ano_ferias = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Ano Férias"
    )
    periodo = models.CharField(
        max_length=10,
        default="",
        choices=PERIODO_FERIAS_CHOICES,
        verbose_name="Período",
    )
    total_dias = models.IntegerField(null=True, blank=True, verbose_name="Total Dias")

    class Meta:
        verbose_name = "Anotação Tempo em Dobro"
        db_table = "rh_anottempodobro"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoTempoDobro, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoTempoServico(AnotacaoGeral):
    unidade_administrativa = models.ForeignKey(
        "UnidadeAdministrativa", null=True, blank=True, on_delete=models.CASCADE
    )
    tempo_servico_finalidade = models.ForeignKey(
        "TempoServicoFinalidade", on_delete=models.CASCADE
    )
    pessoa_juridica = models.ForeignKey(
        "PessoaJuridica",
        verbose_name="Pessoa Jurídica",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    tempo_liquido = models.IntegerField(
        null=True, blank=True, verbose_name="Tempo Líquido"
    )
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    responsavel = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Responsável"
    )
    parecer = models.CharField(max_length=100, null=True, blank=True)
    anos = models.IntegerField(null=True, blank=True)
    meses = models.IntegerField(null=True, blank=True)
    dias = models.IntegerField(null=True, blank=True)
    tipo_regime = models.SmallIntegerField(
        verbose_name="Tipo de Regime",
        choices=(Choice.get_choices_for("rh", "REGIME_PREVIDENCIARIO")),
        blank=True,
        null=True,
    )
    tempo_bruto = models.IntegerField(null=True, blank=True, verbose_name="Tempo Bruto")
    deducao = models.IntegerField(null=True, blank=True, verbose_name="Dedução")

    class Meta:
        verbose_name = "Anotação Tempo de Serviço"
        db_table = "rh_anottemposervico"

    def save(self, *args, **kargs):
        self.calcula_tempo_liquido()
        self.indireto = False
        super(AnotacaoTempoServico, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)

    def calcula_tempo_liquido(self):
        self.tempo_liquido = self.tempo_bruto - self.deducao


class AnotacaoTransposicao(AnotacaoGeral):
    data_opcao = models.DateField(null=True, blank=True, verbose_name="Data Opção")

    class Meta:
        verbose_name = "Anotação Transposição"
        db_table = "rh_anottransposicao"

    def save(self, *args, **kargs):
        self.indireto = False
        super(AnotacaoTransposicao, self).save(*args, **kargs)
        AnotacaoGeral.objects.filter(pk=self.pk).update(indireto=True)


class AnotacaoAfastamento(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Afastamento"
        db_table = "rh_anotafastamento"


class AnotacaoAusencia(AnotacaoGeral):
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    class Meta:
        verbose_name = "Anotação Afastamento"
        db_table = "rh_anotausencia"


class AnotacaoEleitoral(AnotacaoGeral):
    data_declinio = models.DateField(verbose_name="Data Declínio")
    lotacao = models.ForeignKey(
        "Lotacao", verbose_name="Lotacão", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Anotação Eleitoral"
        db_table = "rh_anoteleitoral"


"""
    ENTIDADES RELACIONADAS AO SICAP PESSOAL
"""


@to_search(
    [
        {"name": "data_expedicao", "type": "date"},
        {"name": "data_publicacao", "type": "date"},
        {"name": "data_vigencia", "type": "date"},
        {"name": "veiculo_publicacao", "type": "choices"},
        {"name": "numero_publicacao", "type": "choices"},
        {"name": "interessado_nome", "type": "text"},
        {"name": "origem__sigla", "type": "text"},
        {"name": "cache_unicode", "type": "text"},
        {"name": "observacao", "type": "text"},
    ]
)
class Publicacao(AuditTimestampModel):
    """
    Publicacao - Publicacao autorizativa que institui o quadro de pessoal.
    """

    publication_state = models.SmallIntegerField(
        choices=Choice.get_choices_for("rh", "PUBLICATION_STATE"), default=1
    )
    indirect = models.BooleanField(default=False)
    document = models.TextField(null=True, blank=True)
    document_read_only = models.BooleanField(default=False)
    sent_to_publication_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    sent_to_publication_at = models.DateTimeField(null=True, blank=True)
    confirm_publication_by = models.ForeignKey(
        "auth.User", related_name="+", null=True, blank=True, on_delete=models.CASCADE
    )
    confirm_publication_at = models.DateTimeField(null=True, blank=True)
    vehicle_page = models.SmallIntegerField(null=True, blank=True)
    tipo = models.IntegerField(
        verbose_name="Tipo de Publicação",
        choices=Choice.get_choices_for("rh", "TIPO_DOCUMENTO"),
        null=True,
        blank=True,
    )
    origem = models.ForeignKey(
        "OrgaoGeral",
        null=True,
        blank=True,
        verbose_name="Origem",
        on_delete=models.CASCADE,
    )
    numero = models.CharField(
        verbose_name="Número", max_length=20, null=True, blank=True
    )
    ano = models.CharField(verbose_name="Ano", max_length=4, null=True, blank=True)
    data_expedicao = models.DateField(
        verbose_name="Data da Expedição", null=True, blank=False
    )
    lei_autorizativa = models.BooleanField(default=False)
    veiculo_publicacao = models.IntegerField(
        verbose_name="Veículo Publicação",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "VEICULO_PUBLICACAO"),
    )
    numero_publicacao = models.CharField(
        max_length=22, null=True, blank=True, verbose_name="Número Publicação"
    )
    data_publicacao = models.DateField(
        verbose_name="Data da Publicação", null=True, blank=True
    )
    data_vigencia = models.DateField(
        verbose_name="Data da Vigência", null=True, blank=False
    )
    arquivo = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.CASCADE
    )

    """FIXME: Será removido em razão do document"""
    observacao = models.CharField(
        verbose_name="Observação", max_length=300, null=True, blank=True
    )
    """FIXME: Deve ser corrigido para atender sua real necessidade que é publicar no site"""
    interno = models.BooleanField(null=False, default=False)

    interessado_nome = models.CharField(
        verbose_name="Interessado", max_length=200, null=True, blank=True
    )
    cache_unicode = models.CharField(
        verbose_name="Cache", max_length=200, null=True, blank=True
    )
    import_siap = models.BooleanField("De Importação SIAP", default=False)

    class Meta:
        verbose_name = "Publicação"
        ordering = ["-data_expedicao", "origem", "numero"]

    def sent_to_publication(self, vehicle):
        older = Publicacao.objects.get(pk=self.pk)

        if older.publication_state != 1:
            raise Exception(
                "Não posso pedir publicação de um item que esta como %s"
                % self.get_publication_state_display()
            )

        self.sent_to_publication_by = get_current_user()
        self.sent_to_publication_at = datetime.now()
        self.veiculo_publicacao = vehicle
        self.publication_state = 2
        self.save()

    def confirm_publication(self, publication_number, publication_date, page):
        older = Publicacao.objects.get(pk=self.pk)

        if older.publication_state != 2:
            raise Exception(
                "Não posso confirmar publicação de um item que esta como %s"
                % self.get_publication_state_display()
            )

        self.confirm_publication_by = get_current_user()
        self.confirm_publication_at = datetime.now()
        self.data_publicacao = publication_date if publication_date else date.today()
        self.numero_publicacao = publication_number
        self.vehicle_page = page
        self.publication_state = 3
        self.save()

    @classmethod
    def request_publication(
        klass,
        origin,
        number,
        publication_type=None,
        year=None,
        expedition_at=None,
        efective_date=None,
        document="",
        document_read_only=False,
        internal=False,
        interested=[],
        publication_vehicle=None,
    ):
        expedition_at = expedition_at if expedition_at else datetime.now().date()
        efective_date = efective_date if efective_date else expedition_at

        params = {
            "origem": origin,
            "numero": "%05d" % int(number or 0),
            "ano": year,
            "tipo": publication_type,
            "data_expedicao": expedition_at,
            "data_vigencia": efective_date,
            "document": document,
            "document_read_only": document_read_only,
            "interessado_nome": ", ".join(interested),
            "indirect": True,
        }

        if publication_vehicle:
            params.update(veiculo_publicacao=publication_vehicle)

        publication, created = klass.objects.get_or_create(**params)
        return publication

    @property
    def formated_content(self):
        if self.document_read_only:
            return self.document
        else:
            tpl = loader.get_template("rh/publicacao/base.html")
            return tpl.render({"doc": self})

    @property
    def icon_indirect(self):
        return {
            "iconCls": "icon-rh icon-core-%s"
            % ("empty" if not self.indirect else "indirect"),
            "title": "Publicação %s" % ("direta" if not self.indirect else "indireta"),
        }

    @property
    def icon_publication_state(self):
        icon_map = {
            1: {
                "iconCls": "icon-rh icon-core-publication-open",
                "title": "Aguardando para ser publicado",
            },
            2: {
                "iconCls": "icon-rh icon-core-publication-sent",
                "title": "Publicação enviada ao DO",
            },
            3: {
                "iconCls": "icon-rh icon-core-publication-confirmed",
                "title": "Publicação confirmada",
            },
            4: {
                "iconCls": "icon-rh icon-core-publication-canceled",
                "title": "Publicação cancelada",
            },
        }

        return icon_map.get(int(self.publication_state or 0), {})

    @property
    def icons(self):
        return [
            self.icon_publication_state,
            self.icon_indirect,
        ]

    @property
    def formated_number(self):
        if self.numero and self.data_expedicao:
            items = []
            items_number = [str(self.numero), str(self.data_expedicao.year)]

            if self.origem:
                items_number.append(self.origem.sigla_estrutura())

            items.append(self.get_tipo_display())
            items.append("/".join(items_number))

            return " ".join(items)
        else:
            return ""

    def __str__(self):
        return self.cache_unicode if self.cache_unicode else self.make_cache()

    def make_cache(self):
        if not self.veiculo_publicacao:
            return "{0} {1}/{2}{3}".format(
                self.get_tipo_display(),
                self.numero,
                self.data_expedicao.year if self.data_expedicao else "",
                (
                    "-%s" % self.origem.sigla_estrutura()
                    if self.origem and self.origem.sigla
                    else ""
                ),
            )
        else:
            return "{1} {2}/{3}{4} ({0} nº {5})".format(
                self.get_veiculo_publicacao_display(),
                self.get_tipo_display(),
                self.numero,
                self.data_expedicao.year if self.data_expedicao else "",
                (
                    "-%s" % self.origem.sigla_estrutura()
                    if self.origem and self.origem.sigla
                    else ""
                ),
                self.numero_publicacao,
            )

    def zero_fill(self):
        if self.numero is None:
            self.numero = ""

        if len(self.numero) < 5:
            n = 5 - len(self.numero)
            self.numero = "%s%s" % ("0" * n, self.numero)

    def fix_public_file_permission(self):
        if self.interno:
            self.arquivo.acesso = 3
            self.arquivo.save()

    def save(self, *args, **kargs):
        self.zero_fill()

        tipo = int(self.tipo or 0)

        if tipo in [1, 3, 5] and not self.numero.isdigit():
            raise Exception(
                "O numero do documento deve ser composto somente de digitos numéricos."
            )
        if self.data_vigencia is None and self.import_siap is False:
            raise Exception("A data de vigência deve ser informada.")
        if self.data_expedicao is None and self.import_siap is False:
            raise Exception("A data de expedição deve ser informada.")

        self.ano = self.data_expedicao.year if self.import_siap is False else None

        if (
            self.import_siap is False
            and int(self.publication_state or 0) == 1
            and self.veiculo_publicacao
        ):
            self.sent_to_publication_by = get_current_user()
            self.sent_to_publication_at = datetime.now()
            self.publication_state = 2

        if (
            self.import_siap is False
            and int(self.publication_state or 0) == 2
            and self.numero_publicacao
        ):
            self.confirm_publication_by = get_current_user()
            self.confirm_publication_at = datetime.now()
            self.data_publicacao = (
                self.data_publicacao if self.data_publicacao else date.today()
            )
            self.publication_state = 3

        """
        ADICIONADO PARA FAZER A CHAVE ENTRE OS CAMPOS
        LIBERANDO QUANDO O TIPO FOR 98, 97, 96
        """
        if not self.pk and (tipo not in (98, 97, 96) and self.import_siap is False):
            q = Q(
                Q(tipo=tipo)
                & Q(numero__exact=self.numero)
                & Q(ano=self.ano)
                & Q(veiculo_publicacao=self.veiculo_publicacao)
                & Q(numero_publicacao__exact=self.numero_publicacao)
                & Q(origem=self.origem)
            )

            publicacoes = Publicacao.objects.filter(q)

            if publicacoes.count() > 0:
                raise Exception(
                    "A Publicação já foi criada. Procure-a antes de tentar Salvar."
                )

        self.cache_unicode = self.make_cache()
        super(Publicacao, self).save(*args, **kargs)

        if self.interno:
            self.fix_public_file_permission()

    @classmethod
    def get_dados_publicacao(cls, publicacao):
        data_pub = " Não publicado. "
        veic_pub = " Não publicado. "
        num_pub = " Não publicado. "
        try:
            data_pub = DateUtils.date_to_str(publicacao.data_publicacao)
        except Exception:
            pass
        try:
            veic_pub = publicacao.get_veiculo_publicacao_display()
        except Exception:
            pass
        try:
            num_pub = publicacao.numero_publicacao
        except Exception:
            pass
        return data_pub, veic_pub, num_pub

    @classmethod
    def get_tipo(cls, publicacao):
        """
        Este método retorna o tipo com o "de para" já realizado.
        """
        tipo = 99
        try:
            de_para = {4: 3, 7: 5}
            tipo = 3 if publicacao.tipo not in de_para else de_para.get(publicacao.tipo)
        except Exception:
            pass
        return tipo


class ChartManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, cargo, especialidade, *args):
        return self.get(cargo=cargo, especialidade=especialidade)


class Quadro(AuditTimestampModel):
    """
    Quadro - Quadro de pessoal.
    """

    cargo = models.ForeignKey("Cargo", on_delete=models.CASCADE)
    especialidade = models.ForeignKey(
        "Especialidade", null=True, blank=True, on_delete=models.CASCADE
    )
    objects = ChartManager()
    requires_profissional_council = models.BooleanField(
        default=False, blank=True, verbose_name="Exige Conselho Profissional"
    )
    active = models.BooleanField(verbose_name="Ativo", default=True)

    class Meta:
        verbose_name = "Quadro"
        ordering = ("cargo", "especialidade")
        unique_together = ("cargo", "especialidade")

    def natural_key(self):
        return (self.cargo, self.especialidade)

    def __str__(self):
        if self.especialidade is not None:
            return "{0} - {1}".format(self.cargo, self.especialidade)
        else:
            return "{0}".format(self.cargo)

    @property
    def cargo_quadro(self):
        cargo_quadro = None
        try:
            cargo_quadro = CargoQuadro.objects.get(
                cargo=self.cargo, especialidade=self.especialidade
            )
        except Exception as err:
            log.exception(err)
            log.info(
                "Não encontrou CargoQuadro para %s - %s"
                % (self.cargo, self.especialidade)
            )
        return cargo_quadro

    @property
    def vacancy_number(self):
        vacancy_number = 0
        job_position_chart = self.job_position_chart
        if job_position_chart:
            vacancy_number = job_position_chart.quantidade_vagas
        return vacancy_number

    def vacancy_number_filled(self, date=None):
        date = datetime.now().date() if not date else date
        return (
            MovimentacaoPosse.objects.filter(
                Q(quadro=self)
                & Q(
                    Q(data_exercicio__lte=date)
                    & (Q(data_desligamento__gt=date) | Q(data_desligamento=None))
                )
            )
            .exclude(benefitmovement__isnull=False)
            .count()
        )

    @property
    def job_position_chart(self):
        """Este método retorna o CargoQuadro."""
        return self.cargo_quadro

    @property
    def carga_horaria(self):
        try:
            return self.cargo_quadro.carga_horaria
        except Exception:
            return 40.0

    @property
    def tipo_carga_horaria(self):
        try:
            return self.cargo_quadro.tipo_carga_horaria
        except Exception:
            return 1


class ChartJobPositionManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, cargo, especialidade, *args):
        return self.get(cargo=cargo, especialidade=especialidade)


class CargoQuadro(AuditTimestampModel):
    """
    CargoQuadro - Relação entre Cargo, Especialidade e Publicacao
    """

    cargo = models.ForeignKey("Cargo", related_name="quadros", on_delete=models.CASCADE)
    especialidade = models.ForeignKey(
        "Especialidade", null=True, blank=True, on_delete=models.CASCADE
    )
    cbo = models.ForeignKey("Cbo", null=True, blank=True, on_delete=models.CASCADE)
    publicacao_criacao = models.ForeignKey(
        "Publicacao",
        related_name="publicacao_criacao",
        null=True,
        on_delete=models.PROTECT,
    )
    publicacao_extincao = models.ForeignKey(
        "Publicacao",
        related_name="publicacao_extincao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    publicacao_alteracao = models.ForeignKey(
        "Publicacao",
        related_name="publicacao_alteracao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    quantidade_vagas = models.IntegerField(verbose_name="Quantidade de Vagas")
    nivel_escolaridade = models.IntegerField(
        verbose_name="Nível de Escolaridade", choices=TIPO_NIVEL_ESCOLARIDADE, null=True
    )
    carga_horaria = models.IntegerField(verbose_name="Carga Horária", default=40)
    tipo_carga_horaria = models.IntegerField(
        verbose_name="Tipo Carga Horária", choices=TIPO_CARGA_HORARIA
    )
    health = models.BooleanField(default=False, blank=True)
    teacher = models.BooleanField(default=False, blank=True)
    military = models.BooleanField(default=False, blank=True)
    vacancy_number_filled_cache = models.IntegerField(
        verbose_name="Quantidade de Vagas Preenchidas", blank=True
    )

    objects = ChartJobPositionManager()

    class Meta:
        verbose_name = "Quadro do cargo e especialidade"

    def natural_key(self):
        return (self.cargo, self.especialidade)

    def __str__(self):
        if self.especialidade:
            return "%s - %s" % (self.cargo, self.especialidade)
        return "%s" % self.cargo

    @transaction.atomic
    def save(self, *args, **kargs):
        if self.publicacao_alteracao is None:
            self.publicacao_alteracao = self.publicacao_criacao
        self.vacancy_number_filled_cache = self.vacancy_number_filled(date=date)
        # config do cargo
        config_job_position = self.cargo.configs.last()
        self.nivel_escolaridade = config_job_position.educational_level
        self.quantidade_vagas = config_job_position.quantity
        self.carga_horaria = config_job_position.workload
        self.tipo_carga_horaria = config_job_position.type_workload
        self.teacher = config_job_position.teacher
        self.health = config_job_position.health
        self.cbo = config_job_position.cbo
        super(CargoQuadro, self).save(*args, **kargs)
        self.cadastrar_especialidade_quadro()

    @transaction.atomic
    def delete(self, *args, **kwargs):
        params = {"cargo": self.cargo, "especialidade": self.especialidade}
        quadro = Quadro.objects.filter(**params).first()
        if quadro:
            quadro.active = False
            quadro.save()
        super(CargoQuadro, self).delete(*args, **kwargs)

    def cadastrar_especialidade_quadro(self):
        try:
            params = {"cargo": self.cargo, "especialidade": self.especialidade}
            created = Quadro.objects.filter(**params).first()
            # quarter, created = Quadro.objects.get_or_create(**params)
            if created:
                log.info("Cargo e Especialidade já estão em Quadro.")
            else:
                Quadro.objects.create(**params)
                log.info("Cargo e Especialidade adicionados ao Quadro.")
        except Exception as err:
            log.exception(err)
            raise Exception(
                "Não foi possível vincular a especialidade ao cargo na entidade Quadro."
            )

    @classmethod
    def get_data_publication_creation(cls, cargo):
        year = None
        date_created = None
        local = None
        number = None
        """
            Caso existe uma linha apenas para Analista Ministerial Especializado, sem a especialidade.
        """
        job_position_chart = CargoQuadro.objects.filter(
            cargo=cargo, publicacao_extincao=None
        ).values(
            "publicacao_criacao__numero",
            "publicacao_criacao__data_publicacao",
            "publicacao_criacao__data_vigencia",
            "publicacao_criacao__veiculo_publicacao",
        )
        if (
            len(job_position_chart) > 0
            and job_position_chart[0].get("publicacao_criacao__numero") != ""
            and job_position_chart[0].get("publicacao_criacao__data_publicacao")
        ):
            job_position_chart = job_position_chart[0]
        else:
            job_position_chart = CargoQuadro.objects.filter(
                cargo=cargo, publicacao_extincao=None
            ).values(
                "publicacao_criacao__numero",
                "publicacao_criacao__data_publicacao",
                "publicacao_criacao__data_vigencia",
                "publicacao_criacao__veiculo_publicacao",
            )
            if (
                len(job_position_chart) > 0
                and job_position_chart[0].get("publicacao_criacao__numero") != ""
                and job_position_chart[0].get("publicacao_criacao__data_publicacao")
            ):
                job_position_chart = job_position_chart[0]

        number = None
        year = None
        year = None
        local = None
        if job_position_chart:
            number = job_position_chart.get("publicacao_criacao__numero")
            year = job_position_chart.get("publicacao_criacao__data_publicacao")
            year = year.year if year else None
            if job_position_chart.get("publicacao_criacao__data_vigencia"):
                date_created = DateUtils.date_to_str(
                    job_position_chart.get("publicacao_criacao__data_vigencia")
                )
            if job_position_chart.get("publicacao_criacao__veiculo_publicacao"):
                local = Choice.get_dict_choices_for("rh", "VEICULO_PUBLICACAO").get(
                    job_position_chart.get("publicacao_criacao__veiculo_publicacao")
                )
        return number, year, date_created, local

    def vacancy_number_filled(self, date=None):
        date = datetime.now().date()
        vacancy_number_filled = 0
        charts = Quadro.objects.filter(
            cargo=self.cargo, especialidade=self.especialidade
        )
        if charts.exists():
            vacancy_number_filled = sum(
                [chart.vacancy_number_filled(date=date) for chart in charts]
            )
        return vacancy_number_filled

    @classmethod
    def update_all_vacancy_number_filled(cls):
        for jobposition_chart in CargoQuadro.objects.filter():
            if (
                jobposition_chart.vacancy_number_filled()
                != jobposition_chart.vacancy_number_filled_cache
            ):
                jobposition_chart.save()

    @classmethod
    def update_vacancy_number_filled_from_chart(cls, chart):
        vacancy_number_filled = 0
        if chart:
            jobposition_chart = CargoQuadro.objects.filter(
                cargo=chart.cargo, especialidade=chart.especialidade
            )
            if jobposition_chart.exists():
                jobposition_chart = jobposition_chart.last()
                vacancy_number_filled = jobposition_chart.vacancy_number_filled()
                if (
                    vacancy_number_filled
                    != jobposition_chart.vacancy_number_filled_cache
                ):
                    try:
                        with transaction.atomic():
                            jobposition_chart.save()
                    except Exception as err:
                        log.exception(err)

    @property
    def title(self):
        especialidade = ""
        if self.especialidade:
            especialidade = f"- {self.especialidade.nome}"
        return f"{self.cargo.nome}{especialidade}"

    @property
    def accumulate(self):
        return self.health or self.teacher


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "localizacao__nome", "type": "text"},
    ]
)
class ServidorLocalizacao(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="servidor_localizacao",
        on_delete=models.CASCADE,
    )
    localizacao = models.ForeignKey(
        "Lotacao",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Localização",
        related_name="servidor_localizacao",
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    conferido = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Localização do servidor"

    def __str__(self):
        return "%s" % self.localizacao


@auditable(["lotacao", "ativo"])
class ServidorLotacao(AuditTimestampModel):
    ACTION_CHOICES = (
        (0, ""),
        (1, "Coadjuvando"),
        (2, "Colaborando"),
        (3, "Adjunto"),
    )
    PREJUDICE_CHOICES = (
        (0, ""),
        (1, "Com prejuízo"),
        (2, "Sem prejuízo"),
    )

    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="servidor_lotacao",
        on_delete=models.PROTECT,
    )
    movimentacao_posse = models.ForeignKey(
        "MovimentacaoPosse",
        related_name="lotacoes",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    lotacao = models.ForeignKey(
        "Lotacao",
        null=True,
        blank=True,
        verbose_name="Lotação/Designação",
        related_name="servidores_lotacao",
        on_delete=models.PROTECT,
    )
    publicacao = models.ForeignKey(
        "Publicacao", null=True, blank=True, on_delete=models.PROTECT
    )
    anotacao_geral_lotacao = models.ForeignKey(
        "AnotacaoGeral", null=True, blank=True, on_delete=SET_NULL
    )
    provisorio = models.BooleanField(default=False, verbose_name="Lotação Provisória")
    data_vigencia = models.DateField(
        null=True, verbose_name="Data Vigência", blank=True
    )
    data_vigencia_inicio = models.DateField(
        null=True, verbose_name="Data Vigência Início"
    )
    data_vigencia_fim = models.DateField(
        null=True, blank=True, verbose_name="Data Vigência Fim"
    )
    data_cadastro = models.DateField(auto_now_add=True)
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    full_exercise = models.BooleanField(default=False, verbose_name="Exercício pleno")
    responsible = models.BooleanField(default=False, verbose_name="Responsável")
    partial_responsible = models.BooleanField(
        default=False, verbose_name="Responsável Parcial"
    )
    from_substitution = models.BooleanField(default=False)
    child_of = models.ForeignKey(
        "ServidorLotacao",
        null=True,
        blank=True,
        verbose_name="Derivada de",
        related_name="father_of",
        on_delete=models.PROTECT,
    )
    changed_by_departure = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="employee_workplace_changed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_by_departure = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="employee_workplace_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ativo = models.BooleanField(default=True)
    designacao = models.BooleanField(
        default=False, verbose_name="Designação de exercício"
    )
    owner = models.BooleanField(default=False)
    commission = models.BooleanField(default=False)
    main = models.BooleanField(default=False, verbose_name="Principal")
    ordinance = models.BooleanField(
        default=False, blank=True, verbose_name="Por portaria"
    )
    annotate = models.BooleanField(default=True, blank=True, verbose_name="Anotar?")
    provisional_reason = models.TextField(
        blank=True, null=True, verbose_name="Motivo Provisória"
    )
    main_schedule_date = models.DateField(
        null=True, blank=True, verbose_name="Data agendada para marcar principal"
    )
    action = models.SmallIntegerField(
        default=0, choices=ACTION_CHOICES, blank=True, null=True
    )
    prejudice = models.SmallIntegerField(
        default=0, choices=PREJUDICE_CHOICES, blank=True, null=True
    )
    electoral_refused = models.BooleanField(
        default=False, verbose_name="Declínio Eleitoral"
    )
    occup_area = models.PositiveIntegerField(
        "Área de Atuação",
        choices=Choice.get_choices_for("rh", "OCCUPATION_AREA"),
        null=True,
        blank=True,
    )
    coordinator = models.BooleanField(default=False)
    atribuicao = models.ForeignKey(
        "Atribuicao",
        related_name="servidor_lotacao",
        verbose_name="Atribuição",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    origin_register = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "ORIGIN_REGISTER"),
        verbose_name="Origem do registro",
    )
    empenho_gaeco = models.BooleanField(default=False)
    cumulativa = models.BooleanField(default=False)

    must_validate_document = True
    must_validate_employee_departured = True

    class LotacaoDuplicada(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self,
                "%s" % (txt if txt else "É permitido no máximo uma Lotação vigente."),
            )

    class Meta:
        verbose_name = "Lotação do servidor"
        ordering = ["-data_vigencia_inicio"]

    def __str__(self):
        if self.designacao:
            verbose = "EXERCÍCIO"
        else:
            verbose = "LOTAÇÃO"
        if self.provisorio:
            verbose = "%s - PROVISÓRIA" % verbose
        return "%s: %s à %s" % (
            "%s - %s" % (verbose, self.lotacao),
            DateUtils.date_to_str(self.data_vigencia_inicio),
            (
                DateUtils.date_to_str(self.data_vigencia_fim)
                if self.data_vigencia_fim
                else "----"
            ),
        )

    def set_active(self):
        self.ativo = self.is_active()

    def set_main(self):
        today = datetime.now().date()
        if (
            not self.servidor.member_type_by_possession
            and self.is_active()
            and not self.servidor._raw_locations(date=today)
            .filter(main=True)
            .filter(designacao=self.designacao)
            .exists()
        ):
            ServidorLotacao.objects.filter(servidor=self.servidor, main=True).update(
                main=False
            )
            self.main = True

    def set_child_of(self):
        if self.designacao and not self.child_of:
            self.child_of = (
                self.servidor.get_workplace_only(date=self.data_vigencia_inicio)
                .filter(lotacao=self.lotacao)
                .last()
            )

    def _set_child_of_main(self):
        """Este método marca os child_of(exercício) com o main da lotação."""
        work_assignment_child_active = self.work_assignment_child_active()
        if not work_assignment_child_active.exists():
            work_assignment_child_active = self.work_assignment_child_active(
                date=self.data_vigencia_inicio
            )
        work_assignment_child_active.update(main=self.main)

    def _unset_main(self):
        """Este método desmarca o main"""
        if self.designacao:
            work_assignments = (
                self.servidor.get_work_assignment()
                .filter(main=True)
                .exclude(pk=self.pk)
            )
            if self.data_vigencia_fim:
                work_assignments = work_assignments.exclude(
                    Q(data_vigencia_inicio__gt=self.data_vigencia_fim)
                )
            work_assignments = work_assignments.filter(
                Q(data_vigencia_inicio__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim=None)
            )
            work_assignments.update(main=False)
        else:
            workplace_only = (
                self.servidor.get_workplace_only(date=self.data_vigencia_inicio)
                .filter(main=True)
                .exclude(pk=self.pk)
            )
            if self.data_vigencia_fim:
                workplace_only = workplace_only.exclude(
                    Q(data_vigencia_inicio__gt=self.data_vigencia_fim)
                )
            workplace_only = workplace_only.filter(
                Q(data_vigencia_inicio__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim=None)
            )
            pks_change = (pk.get("pk") for pk in workplace_only.values("pk"))
            workplace_only.update(main=False)
            for workplace in ServidorLotacao.objects.filter(pk__in=pks_change):
                workplace._set_child_of_main()

    def action_set_main(self, main):
        try:
            with transaction.atomic():
                ServidorLotacao.objects.filter(
                    servidor=self.servidor, main=True
                ).update(main=False)
                main_lotation = ServidorLotacao.objects.filter(pk=self.pk)
                main_lotation.update(main=main)
                if main_lotation:
                    main_lotation.first().create_substitution_for_electoral_zone()
                inst = ServidorLotacao.objects.get(pk=self.pk)
                inst._set_child_of_main()
        except Exception as err:
            log.exception(err)

    @classmethod
    def workplace_only(cls, workplace=None):
        """
        :py:function:: workplace_only(cls)

        This method returns the work assignments.

        :return: queryset, ServidorLotacao
        :return: queryset
        """
        query = ServidorLotacao.objects.filter(designacao=False)
        return query.filter(lotacao=workplace) if workplace else query

    @classmethod
    def workplace_only_exercise(cls, workplace=None, date=None):
        """
        :py:function:: workplace_only_exercise(cls)

        This method returns the work assignments.

        :param date date: date of
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        return ServidorLotacao.workplace_only(workplace=workplace).filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
        )

    @classmethod
    def work_assignment(cls, workplace=[]):
        """
        :py:function:: work_assignment(cls)

        This method returns the work assignments.

        :return: queryset, ServidorLotacao
        :return: queryset
        """
        if not isinstance(workplace, (list, tuple, set)):
            workplace = [workplace] if workplace else []
        query = ServidorLotacao.objects.filter(designacao=True)
        return query.filter(lotacao__pk__in=workplace) if workplace else query

    @classmethod
    def get_work_assignment_owner(cls, date=None, workplace=None):
        """
        :py:function:: get_work_assignment_owner(cls, date=None)

        This method returns all employee work assignments.
        The work assignment should be active at period of the departure.
        Default date is datetime.now().date().

        :param date: date
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        employee_workplaces = []
        work_assignments = ServidorLotacao.work_assignment(workplace=workplace).filter(
            Q(owner=True)
            & (
                Q(data_vigencia_inicio__lte=date)
                & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
            )
        )
        for work_assignment in work_assignments:
            employee_workplaces.append(work_assignment.pk)

        work_assignments = (
            ServidorLotacao.work_assignment(workplace=workplace)
            .filter(owner=True)
            .filter(Q(changed_by_departure__estado=ACTIVE))
        )

        for work_assignment in work_assignments:
            employee_workplaces.append(work_assignment.pk)

        return ServidorLotacao.work_assignment().filter(pk__in=employee_workplaces)

    @classmethod
    def work_assignment_exercise(cls, date=None, workplace=[]):
        """
        :py:function:: work_assignment_exercise(cls, date=None, workplace=[])

        This method returns all work assignments that matches a date.
        By default returns today work assignments.

        :param date date: date of
        :param list workplace: workplace
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        return ServidorLotacao.work_assignment(workplace=workplace).filter(
            (
                Q(data_vigencia_inicio__lte=date)
                & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
            )
        )

    @classmethod
    def workplace_exercise(cls, date=None, workplace=[]):
        """
        :py:function:: workplace_exercise(cls, date=None, workplace=[])

        This method returns all workplaces that matches a date.
        By default returns today workplaces.

        :param date date: date of
        :param list workplace: workplace
        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        date = datetime.now().date() if not date else date
        return ServidorLotacao.work_assignment_exercise(workplace=workplace).filter(
            Q(child_of__data_vigencia_inicio__lte=date)
            & (
                Q(child_of__data_vigencia_fim__gte=date)
                | Q(child_of__data_vigencia_fim=None)
            )
        )

    @property
    def work_assignment_child(self):
        """
        :py:function:: work_assignment_child(cls)

        This method returns the work assignments child of.

        :return: queryset, ServidorLotacao
        :return: queryset

        """
        return self.father_of.filter()

    def work_assignment_child_active(self, date=None):
        """
        :py:function:: work_assignment_child_active(self, date=None)

        This method returns the work assignments active.

        :param date date: date of
        :return: queryset, ServidorLotacao
        :return: queryset
        """
        date = datetime.now().date() if not date else date
        return self.work_assignment_child.filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
        )

    @property
    def employees(self):
        """
        :py:function:: employees(self)

        This property calls method work_assignment_exercise. Returns arraydict of the employees.
        Assuming active is True.

        :return: arraydict of Employee
        :rtype: arraydict
        """
        return Servidor.objects.filter(
            pk__in=ServidorLotacao.work_assignment_exercise().values("servidor")
        )

    @property
    def employees_judicial(self):
        """
        :py:function:: employees_judicial(self)

        This property calls method work_assignment_exercise. Returns arraydict of the employees.
        Considering only active is True.

        :return: arraydict of Servidor
        :rtype: arraydict
        """
        return Servidor.objects.filter(
            pk__in=ServidorLotacao.work_assignment_exercise().values("servidor")
        )

    def is_active(self, date=None):
        return is_active(
            today=date,
            date_start=self.data_vigencia_inicio,
            date_end=self.data_vigencia_fim,
        )

    @property
    def employee_name(self):
        if self.servidor:
            return self.servidor.pessoa_fisica.nome
        return None

    @property
    def exercise_name(self):
        if self.lotacao:
            return self.lotacao.nome
        return None

    def is_finished(self):
        """
        :py:function:: is_finished(self)

        This method verifies if instance is finished.

        :return: True/False
        :rtype: bool
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        date_end = self.data_vigencia_fim
        if self.pk:
            date_end = self.get_self().data_vigencia_fim
        return BaseLicencaAfastamento._finalizado(date_end=date_end)

    def get_self(self):
        """
        Este método retorna a instância do objeto.
        """
        base = None
        try:
            base = ServidorLotacao.objects.get(pk=self.pk)
        except Exception:
            pass
        return base

    def validate_lotacao_fora_organograma(self):
        if (
            self.designacao is False
            and self.lotacao
            and self.lotacao.organograma is False
        ):
            if self.lotacao.organograma is False:
                raise Exception(
                    "Não posso lotar um servidor em uma lotação que esta fora do organograma."
                )
            elif not self.lotacao:
                raise Exception("Lotação não encontrada.")
        return True

    def validate_lotacao_nao_escolhida(self):
        if self.lotacao is None:
            raise Exception("Por favor escolha uma lotação.")

    def validate_replacement_cache(self):
        # to_check = set(['data_vigencia_inicio', 'data_vigencia_fim', 'lotacao'])
        to_check = set(
            [
                "lotacao",
            ]
        )
        message = ""
        if self.from_substitution and to_check.intersection(set(self.diff.keys())):
            if self.substitution_substitute.exists():
                message = "%s de %s" % (
                    self.substitution_substitute.first(),
                    self.substitution_substitute.first().servidor_substituido,
                )

            if message:
                raise Exception("Informação editável apenas através de: %s." % message)

    def validate_posse(self):
        if self.movimentacao_posse is None:
            raise Exception("Por favor informe a posse do servidor.")
        if (
            self.movimentacao_posse
            and self.servidor != self.movimentacao_posse.servidor
        ):
            raise Exception("Servidor informado é diferente do servidor da posse.")
        return True

    def validate_duplicate_workplace(self):
        """
        :py:function:: validate_duplicate_workplace(self)

        This method validates employee workplaces duplicated.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if not self.designacao and not self.provisorio:
            locations = self.servidor.get_workplace_only().exclude(provisorio=True)
            if self.data_vigencia_fim:
                locations = locations.exclude(
                    Q(data_vigencia_inicio__gt=self.data_vigencia_fim)
                )
            locations = locations.filter(
                Q(data_vigencia_inicio__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim=None)
            )
            if self.pk:
                locations = locations.exclude(pk=self.pk)
            if locations.exists():
                raise self.LotacaoDuplicada()
        return True

    def validate_duplicate_work_assignment(self):
        """
        :py:function:: validate_duplicate_work_assignment(self)

        This method validates employee workplaces assignments duplicated.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if (
            not self.partial_responsible
            and not self.ignore_duplicate_exercise
            and self.designacao
        ):
            locations = (
                self.servidor.get_work_assignment()
                .filter(lotacao=self.lotacao)
                .exclude(partial_responsible=True)
            )
            if self.data_vigencia_fim:
                locations = locations.exclude(
                    Q(data_vigencia_inicio__gt=self.data_vigencia_fim)
                )
            locations = locations.filter(
                Q(data_vigencia_inicio__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim=None)
            )
            if self.pk:
                locations = locations.exclude(pk=self.pk)
            if locations.exists():
                log.info(
                    "Exercício duplicado no mesmo período: %s - %s - %s"
                    % (self.pk, self, self.servidor)
                )
                raise_call(
                    msg="Exercício duplicado no mesmo período: %s - %s"
                    % (self.pk, self)
                )
        return True

    @deprecated
    def validate_duplicate_work_assignment_main(self):
        """
        :py:function:: validate_duplicate_work_assignment_main(self)

        This method validates MAIN employee work assignments duplicated.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if self.designacao and self.main:
            locations = self.servidor.get_work_assignment().filter(main=True)
            if self.data_vigencia_fim:
                locations = locations.exclude(
                    Q(data_vigencia_inicio__gt=self.data_vigencia_fim)
                )
            locations = locations.filter(
                Q(data_vigencia_inicio__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                | Q(data_vigencia_fim=None)
            )
            if self.pk:
                locations = locations.exclude(pk=self.pk)
            if locations.exists():
                log.info(
                    "Exercício Principal duplicado no mesmo período: %s - %s"
                    % (self, self.servidor)
                )
                raise_call(
                    msg="Exercício Principal duplicado no mesmo período: %s" % self
                )
        return True

    def validate_work_assignment_provisional(self):
        """
        :py:function:: validate_work_assignment_provisional(self)

        This method validates employee workplaces assignments and provisional.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if self.designacao and self.provisorio:
            raise_call(msg="Designação de exercício não pode ser provisório: %s" % self)
        return True

    def validate_duplicate_responsible_organ(self):
        """
        :py:function:: validate_duplicate_responsible_organ(self)

        This method validates employee workplaces duplicated for the organ.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if not self.ignore_duplicate_exercise and self.responsible:
            locations = self.lotacao._employee_workplaces().filter(
                Q(data_vigencia_inicio__lte=self.data_vigencia_inicio)
                & (
                    Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                    | Q(data_vigencia_fim=None)
                )
            )
            locations = locations.filter(
                designacao=self.designacao, responsible=True, ativo=True
            )
            if self.pk:
                locations = locations.exclude(pk=self.pk)
            exclude = []
            for loc in locations:
                if loc.data_vigencia_inicio == loc.data_vigencia_fim:
                    exclude.append(loc.pk)
            locations = locations.exclude(pk__in=exclude)
            locations.exists() and raise_call(
                msg="Responsabilidade duplicada! Conflitando com %s: %s."
                % (locations.latest("pk").servidor, locations.latest("pk"))
            )
        return True

    def validate_vigency_location(self):
        return True

    def validate_work_assignment_without_workplace(self):
        """
        :py:function:: validate_work_assignment_without_workplace(self)

        This method validates employee work assignment without workplace active.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if (
            self.designacao
            and self.is_active()
            and self.child_of
            and not self.child_of.is_active()
        ):
            raise_call(msg="Exercício não possui Lotação ativa: %s." % self.lotacao)
        return True

    def validate_publicacao(self):
        if not self.must_validate_document:
            return True

        if self.designacao is False:
            if self.publicacao is None:
                raise Exception("A publicação é obrigatória.")
            if self.publicacao.data_vigencia is None:
                raise Exception(
                    "É necessário que Data de Vigência do Documento seja preenchido."
                )
        return True

    def validate_employee_departured(self):
        if self.must_validate_employee_departured:
            ServidorLotacao._validate_employee_departured(
                employee=self.servidor,
                start_date=self.data_vigencia_inicio,
                end_date=self.data_vigencia_fim,
                exercise=[self.pk],
            )
        return True

    @classmethod
    def _validate_employee_departured(
        cls, employee=None, start_date=None, end_date=None, exercise=[]
    ):
        from rh.afastamento.models import BaseLicencaAfastamento

        departures = (
            employee.departures(start_date=start_date, end_date=end_date)
            .exclude(designation_exercise__pk__in=exercise)
            .exclude(tipo=TYPE_DEPARTURE_PARCIAL_STUDY)
        )
        if departures.filter(
            ~Q(desempenhofuncao=None) | ~Q(atuacaogrupotrabalho=None) | ~Q(viagem=None)
        ).exists():
            departures = BaseLicencaAfastamento.objects.none()
        if departures.exists():
            raise Exception(
                "Não é possível cadastrar pois o servidor está afastado: %s - %s."
                % (employee, departures.latest("pk").__str_restful__())
            )
        return True

    def validate_responsible_owner(self):
        if self.owner and not self.responsible:
            raise Exception("O servidor Afastável deve ser responsável pelo local.")
        return True

    def validate_workplace_owner_active(self):
        """
        :py:function:: validate_workplace_owner_active(self)

        This method validates employee workplace owner active.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if not self.ignore_duplicate_exercise and self.owner:
            locations = self.lotacao._employee_workplaces(
                option=WORKPLACE if not self.designacao else WORK_ASSIGNMENT
            ).filter(
                Q(data_vigencia_inicio__lte=self.data_vigencia_inicio)
                & (
                    Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                    | Q(data_vigencia_fim=None)
                )
            )
            locations = locations.filter(owner=True, ativo=True)
            if self.child_of:
                locations = locations.exclude(pk=self.child_of.pk)
            if self.pk:
                locations = locations.exclude(pk=self.pk)
                locations = locations.exclude(child_of__pk=self.pk)
            exclude = []
            for loc in locations:
                if loc.data_vigencia_inicio == loc.data_vigencia_fim:
                    exclude.append(loc.pk)
            locations = locations.exclude(pk__in=exclude)
            locations.exists() and raise_call(
                msg="Afastável duplicado! Conflitando com %s: %s."
                % (locations.latest("pk").servidor, locations.latest("pk"))
            )
        return True

    def validate_workplace_job_position_owner(self):
        """
        :py:function:: validate_workplace_job_position_owner(self)

        This method validates employee workplace owner active.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        possessions = MovimentacaoPosse.objects.filter(
            Q(quadro__cargo__lotacao_responsavel=self.lotacao)
        )
        employee_workplaces = ServidorLotacao.objects.filter(
            designacao=self.designacao, lotacao=self.lotacao, owner=True
        ).filter(
            (
                Q(data_vigencia_inicio__lte=self.data_vigencia_inicio)
                & (
                    Q(data_vigencia_fim__gte=self.data_vigencia_inicio)
                    | Q(data_vigencia_fim=None)
                )
            )
        )
        if self.pk:
            employee_workplaces = employee_workplaces.exclude(pk=self.pk)
        if (
            self.owner
            and possessions.exists()
            and possessions.latest("data_exercicio").servidor != self.servidor
            and employee_workplaces.exists()
        ):
            raise_call(
                msg="Este local possui um cargo responsável: %s. Para tornar o servidor afastável deve-se criar uma posse no cargo."
                % self.lotacao.cargo_responsavel.first()
            )
        return True

    def validate_date_start_date_end(self):
        if (
            self.data_vigencia_fim
            and self.data_vigencia_inicio > self.data_vigencia_fim
        ):
            raise Exception("Data de início não pode ser maior que a data de fim.")
        return True

    def validate_duplicate_action(self):
        if (
            ServidorLotacao.objects.filter(
                lotacao=self.lotacao, designacao=True, ativo=True, action=self.action
            )
            .exclude(pk=self.pk)
            .exclude(action=0)
            .exists()
        ):
            raise Exception(
                f"Já existe uma designação de exercício <b> com a opção: {self.get_action_display()}</b>"
            )
        return True

    def validate_duplicate_prejudice(self):
        if (
            ServidorLotacao.objects.filter(
                lotacao=self.lotacao,
                designacao=True,
                ativo=True,
                prejudice=self.prejudice,
            )
            .exclude(pk=self.pk)
            .exclude(prejudice=0)
            .exists()
        ):
            raise Exception(
                f"Já existe uma designação de exercício <b>{self.get_prejudice_display()}</b>"
            )
        return True

    def validate_duplicate_partial_responsible(self):
        if self.partial_responsible:
            locations = ServidorLotacao.objects.filter(
                lotacao=self.lotacao,
                designacao=True,
                ativo=True,
                partial_responsible=True,
            ).exclude(pk=self.pk)
            if locations.exists():
                raise Exception(
                    "Responsabilidade parcial duplicada! Conflitando com %s: %s."
                    % (locations.latest("pk").servidor, locations.latest("pk"))
                )
        return True

    def validar_designacao_duplicada(self):

        if self.designacao == False:
            return True

        query = ServidorLotacao.objects.filter(
            servidor=self.servidor,
            lotacao=self.lotacao,
            designacao=True,
            ativo=True,
        )

        if self.data_vigencia_fim:
            query = query.filter(
                Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__gte=self.data_vigencia_inicio,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_fim,
                    data_vigencia_fim__gte=self.data_vigencia_fim,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__isnull=True,
                )
            )
        else:
            query = query.filter(
                Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__gte=self.data_vigencia_inicio,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__isnull=True,
                )
            )

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise Exception(f"O servidor já possui um designação nessa lotação")
        return True

    def validar_designacao_responsavel_multiplo(self):

        if self.designacao == False or self.responsible == False:
            return True

        query = ServidorLotacao.objects.filter(
            lotacao=self.lotacao,
            designacao=True,
            ativo=True,
            responsible=True,
        )

        if self.data_vigencia_fim:
            query = query.filter(
                Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__gte=self.data_vigencia_inicio,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_fim,
                    data_vigencia_fim__gte=self.data_vigencia_fim,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__isnull=True,
                )
            )
        else:
            query = query.filter(
                Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__gte=self.data_vigencia_inicio,
                )
                | Q(
                    data_vigencia_inicio__lte=self.data_vigencia_inicio,
                    data_vigencia_fim__isnull=True,
                )
            )

        if self.pk:
            query = query.exclude(pk=self.pk)

        if query.exists():
            raise Exception(
                f"Já existe um Responsavel no periodo informado de exercício"
            )
        return True

    def validar_data_fim_teletrabalho(self):
        if self.pk:
            if (
                self.data_vigencia_fim
                and self.mov_teletrabalho.filter(ativo=True).exists()
                and self.designacao == False
            ):

                mov_teletrabalho = self.mov_teletrabalho.filter(ativo=True).first()
                plano_teletrabalho = mov_teletrabalho.pvf_work_plan.last()

                if (
                    self.data_vigencia_fim.year == plano_teletrabalho.reference_year
                    and self.data_vigencia_fim.month
                    > plano_teletrabalho.reference_month
                ) or self.data_vigencia_fim.year > plano_teletrabalho.reference_year:
                    mov_teletrabalho.data_fim = self.data_vigencia_fim
                else:

                    if plano_teletrabalho.reference_month == 12:
                        nova_data = datetime(plano_teletrabalho.reference_year, 12, 31)
                    else:
                        nova_data = datetime(
                            plano_teletrabalho.reference_year,
                            plano_teletrabalho.reference_month + 1,
                            1,
                        ) - timedelta(days=1)

                    if mov_teletrabalho.data_fim > nova_data.date():

                        mov_teletrabalho.data_fim = nova_data.date()

                mov_teletrabalho.save()

    def validate(self):
        self.validate_date_start_date_end()
        self.validate_lotacao_nao_escolhida()
        self.validate_lotacao_fora_organograma()
        self.validate_publicacao()
        self.validate_posse()
        self.validate_replacement_cache()
        self.validate_duplicate_workplace()
        # self.validate_duplicate_work_assignment()

        if (
            self.data_vigencia_inicio
            and self.data_vigencia_inicio >= datetime.today().date()
        ):
            self.validate_duplicate_responsible_organ()

        self.validate_vigency_location()
        self.validate_work_assignment_provisional()
        self.validate_responsible_owner()
        self.validate_workplace_owner_active()
        self.validate_workplace_job_position_owner()
        self.validar_data_fim_teletrabalho()
        # self.validate_duplicate_action()
        # self.validate_duplicate_prejudice()
        # self.validate_duplicate_partial_responsible()
        self.validar_designacao_responsavel_multiplo()
        self.validar_designacao_duplicada()

        return True

    @deprecated
    def apply_possession(self):
        raise Exception(
            "escrever o set de posse para membro baseando-se no local que está ligado ao cargo"
        )
        if not self.movimentacao_posse and self.servidor.posses_ativas.exists():
            self.movimentacao_posse = self.servidor.posses_ativas.latest(
                "data_exercicio"
            )

    @transaction.atomic
    def save(self, *args, **kargs):
        new = not self.pk
        active = self.ativo
        self.set_child_of()

        if not self.movimentacao_posse:
            self.movimentacao_posse = (
                self.servidor.posses_ativas.last() or self.servidor.posses.last()
            )

        self.ignore_duplicate_exercise = False
        if "ignore_duplicate_exercise" in kargs:
            self.ignore_duplicate_exercise = kargs.pop("ignore_duplicate_exercise")

        if "must_validate_document" in kargs:
            self.must_validate_document = kargs.pop("must_validate_document")

        if "must_validate_employee_departured" in kargs:
            self.must_validate_employee_departured = kargs.pop(
                "must_validate_employee_departured"
            )
        self.set_from_substitution()
        self.validate()
        propagate_resp = True
        if self.data_vigencia is None:
            self.data_vigencia = self.data_vigencia_inicio

        if "propagate_resp" in kargs:
            propagate_resp = kargs.pop("propagate_resp")

        if self.annotate:
            self.anotacao()

        self.set_active()
        self.set_main()

        super(ServidorLotacao, self).save(*args, **kargs)

        Lotacao.update_chief_immediate_from_new_member(
            self, propagate_resp=propagate_resp
        )

        self._create_history()
        self.update_chief_immediate_employee(new, active)
        self.update_telework_approver(new, active)
        if self.lotacao.electoral_zone or self.main:
            self.create_substitution_for_electoral_zone()

    def create_substitution_for_electoral_zone(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        today = datetime.today().date()

        if self.main:
            servidor_lotacoes = ServidorLotacao.objects.filter(
                servidor=self.servidor, lotacao__electoral_zone=True, ativo=True
            )

            afastamentos = BaseLicencaAfastamento.objects.filter(
                servidor=self.servidor,
                data_fim__gte=today,
            )

            mov_subs = MovimentacaoSubstituicao.objects.filter(
                afastamento__in=afastamentos, designation_substituted=self
            )

            for servidor_lotacao in servidor_lotacoes:
                for mov_sub in mov_subs:
                    mov_dict = model_to_dict(mov_sub)
                    mov_dict["created_by"] = get_current_user()
                    mov_dict["created_by_id"] = get_current_user().id
                    mov_dict["created_at"] = today
                    mov_dict["modified_by"] = get_current_user()
                    mov_dict["modified_by_id"] = get_current_user().id
                    mov_dict["modified_at"] = today
                    mov_dict["servidor"] = mov_sub.servidor
                    mov_dict["anotacao_geral"] = mov_sub.anotacao_geral
                    mov_dict["publicacao_movimentacao"] = (
                        mov_sub.publicacao_movimentacao
                    )
                    mov_dict["movimentacaopessoal_ptr"] = None
                    mov_dict["afastamento"] = mov_sub.afastamento
                    mov_dict["posse"] = mov_sub.posse
                    mov_dict["servidor_substituido"] = mov_sub.servidor_substituido
                    mov_dict["designation_substituted"] = servidor_lotacao
                    mov_dict["designation_substitute"] = self
                    mov_dict["place"] = servidor_lotacao.lotacao
                    mov_dict["origin_register"] = 2
                    try:
                        if self.servidor.is_member:
                            if not MovimentacaoSubstituicaoMembro.objects.filter(
                                servidor_substituido=mov_sub.servidor_substituido,
                                place=servidor_lotacao.lotacao,
                                afastamento=mov_sub.afastamento,
                            ).exists():
                                _movsubs = MovimentacaoSubstituicaoMembro(**mov_dict)
                                _movsubs.id = None
                                _movsubs.save_base()

                        else:
                            if not MovimentacaoSubstituicao.objects.filter(
                                servidor_substituido=mov_sub.servidor_substituido,
                                place=servidor_lotacao.lotacao,
                                afastamento=mov_sub.afastamento,
                            ).exists():
                                _movsubs = MovimentacaoSubstituicao(**mov_dict)
                                _movsubs.id = None
                                _movsubs.save_base()

                    except Exception as e:
                        log.error(e)

        elif self.lotacao.electoral_zone:
            servidor_lotacao = ServidorLotacao.objects.filter(
                servidor=self.servidor, main=True, ativo=True
            ).first()

            afastamentos = BaseLicencaAfastamento.objects.filter(
                servidor=self.servidor,
                data_fim__gte=today,
            )

            mov_subs = MovimentacaoSubstituicao.objects.filter(
                designation_substituted=servidor_lotacao, afastamento__in=afastamentos
            )

            for mov_sub in mov_subs:
                mov_dict = model_to_dict(mov_sub)

                mov_dict["created_by"] = get_current_user()
                mov_dict["created_at"] = today
                mov_dict["modified_by"] = get_current_user()
                mov_dict["modified_at"] = today
                mov_dict["servidor"] = mov_sub.servidor
                mov_dict["anotacao_geral"] = mov_sub.anotacao_geral
                mov_dict["publicacao_movimentacao"] = mov_sub.publicacao_movimentacao
                mov_dict["movimentacaopessoal_ptr"] = None
                mov_dict["afastamento"] = mov_sub.afastamento
                mov_dict["posse"] = mov_sub.posse
                mov_dict["servidor_substituido"] = mov_sub.servidor_substituido
                mov_dict["designation_substituted"] = self
                mov_dict["designation_substitute"] = mov_sub.designation_substitute
                mov_dict["place"] = self.lotacao
                mov_dict["origin_register"] = 2

                try:
                    if self.servidor.is_member:
                        if not MovimentacaoSubstituicaoMembro.objects.filter(
                            servidor_substituido=mov_sub.servidor_substituido,
                            place=self.lotacao,
                            afastamento=mov_sub.afastamento,
                        ).exists():
                            _movsubs = MovimentacaoSubstituicaoMembro(**mov_dict)
                            _movsubs.id = None
                            _movsubs.save_base()

                    else:
                        if not MovimentacaoSubstituicao.objects.filter(
                            servidor_substituido=mov_sub.servidor_substituido,
                            place=self.lotacao,
                            afastamento=mov_sub.afastamento,
                        ).exists():
                            _movsubs = MovimentacaoSubstituicao(**mov_dict)
                            _movsubs.id = None
                            _movsubs.save_base()

                except Exception as e:
                    log.error(e)

    def create_work_assignment(self):
        """
        :py:function:: create_work_assignment(self)

        This method creates work assignment from EmployeeWorkplace instance.

        :raises Exception: If validates raise.
        """
        if self.designacao:
            raise Exception("Apenas uma lotação pode criar um exercício.")
        fields_update = {
            "designacao": True,
            "responsible": self.responsible,
            "child_of": self,
        }
        return self._create_by_copy(self, fields_update)

    def _create_history(self):
        """
        :py:function:: _create_history(self)

        This method creates EmployeeWorkplace from EmployeeWorkplace instance give. It uses fields_update parameter
        to fill fields of the new instance.

        :return: instance of the new EmployeeWorkplace
        :rtype: EmployeeWorkplace
        :raises Exception: If validates raise.
        """
        try:
            with transaction.atomic():
                new_kwargs = dump_instance_fields_dict(self)
                new_kwargs.update({"employee_workplace": self})
                new_kwargs.update({"pk_history": new_kwargs.get("id")})
                new_kwargs.pop("id")
                if new_kwargs.get("action", None):
                    new_kwargs.pop("action")
                created = EmployeeWorkplaceHistory(**new_kwargs)
                created.save()
        except Exception as err:
            log.exception(err)

    @classmethod
    def _create_by_copy(cls, employee_workplace, fields_update={}):
        """
        :py:function:: _create_by_copy(cls, employee_workplace, fields_update={}):

        This method creates EmployeeWorkplace from EmployeeWorkplace instance give. It uses fields_update parameter
        to fill fields of the new instance.

        :param EmployeeWorkplace employee_workplace: The EmployeeWorkplace instance to provide the new instance
        :param dict fields_update: Dict fields_update with values to update on the new instance
        :return: instance of the new EmployeeWorkplace
        :rtype: EmployeeWorkplace
        :raises Exception: If validates raise.
        """
        new_kwargs = dump_instance_fields_dict(employee_workplace)

        pop = [
            "id",
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "anotacao_geral_lotacao",
            "ativo",
            "provisorio",
            "data_cadastro",
            "data_alteracao",
            "from_substitution",
            "designacao",
            "responsible",
            "child_of",
        ]
        for key in pop:
            if key in list(new_kwargs.keys()):
                new_kwargs.pop(key)

        for key in fields_update:
            new_kwargs.update({key: fields_update.get(key)})

        created = ServidorLotacao(**new_kwargs)
        created.save()
        log.info("%s - possui: %s" % (employee_workplace, created))
        return created

    @deprecated
    def update_work_assignment_from_workplace(self):
        """
        :py:function:: update_work_assignment_from_workplace(self)

        This method updates work assignment belonging EmployeeWorkplace instance.

        :raises Exception: If validates raise.
        """
        employee_workplaces = self.work_assignment_child.filter(
            Q(inactivation_jobposition=None) & Q(substitution_substituted=None)
        )
        employee_workplace = None
        if employee_workplaces.exists():
            employee_workplace = employee_workplaces.latest("data_vigencia_inicio")
        if (
            not self.designacao
            and employee_workplaces.exists()
            and employee_workplace
            and not self.work_assignment_child.filter(
                data_vigencia_inicio__gt=employee_workplace.data_vigencia_inicio
            ).exclude(pk=employee_workplace.pk)
        ):
            employee_workplace.data_vigencia_fim = self.data_vigencia_fim
            employee_workplace.from_substitution = False
            employee_workplace.save()

    def call_update_from_departure(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        log.debug("================>call_update_from_departure")
        log.debug("%s - %s" % (self.pk, self))
        if self.designacao:
            departures = (
                BaseLicencaAfastamento.objects.filter(
                    Q(servidor=self.servidor)
                    & (
                        Q(data_inicio__lte=self.data_vigencia_inicio)
                        | (
                            Q(data_fim__gte=self.data_vigencia_inicio)
                            | Q(data_fim=None)
                        )
                    )
                )
                .exclude(estado__in=[CANCELED, SCHEDULED])
                .exclude(designation_exercise=self)
                .exclude(data_fim__lt=self.data_vigencia_inicio)
                .exclude(~Q(viagem=None))
            )

            if self.data_vigencia_fim:
                departures = departures.exclude(data_inicio__gt=self.data_vigencia_fim)
            if not departures.exists():
                log.debug("call none!!")

            for departure in departures.order_by("data_inicio")[0:1]:
                try:
                    if departure.can_run_process:
                        log.debug("*&*&*&*&* begin call...")
                        log.debug(
                            "%s %s %s"
                            % (
                                departure,
                                DateUtils.date_to_str(departure.data_inicio),
                                (
                                    DateUtils.date_to_str(departure.data_fim)
                                    if departure.data_fim
                                    else "----"
                                ),
                            )
                        )
                        departure.instancia_modelo.save(
                            must_validate_employee_departured=False
                        )
                        log.debug("*&*&*&*&* end call...")
                    else:
                        log.debug(f"Não é possível rodar atualização para {departure}.")
                except Exception as err:
                    log.exception(err)
            log.debug("*&*&*&*&* ---> end all calls")

    @classmethod
    def _validate_update_work_assignment_from_departure(cls, departure):
        """
        :py:function:: update_work_assignment_from_departure(cls, departure)

        This method finalizes work assignment belonging employee. It finalizes a day before the begin of departure.

        :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
        :raises Exception: If validates raise.
        """
        if not settings.UPDATE_WORK_ASSIGNMENT_FROM_DEPARTURE:
            return False

        valid = True
        if not departure:
            raise Exception("Afastamento não informado!")

        if not departure.servidor.member_type_by_possession:
            log.info("O servidor %s não é membro." % departure.servidor)
            valid = False
        elif departure.estado == SCHEDULED:
            valid = False
        elif not departure.can_run_process:
            valid = False

        return valid

    @classmethod
    def update_work_assignment_from_departure(
        cls, departure, ignore_duplicate_exercise=False
    ):
        log = getLogger("db")
        """
            :py:function:: update_work_assignment_from_departure(cls, departure)

            This method finalizes work assignment belonging employee. It finalizes a day before the begin of departure.

            :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
            :raises Exception: If validates raise.
        """
        message = ""
        notify = False
        try:
            if ServidorLotacao._validate_update_work_assignment_from_departure(
                departure
            ):
                with transaction.atomic():
                    try:
                        ServidorLotacao._finalize_work_assignment_from_departure(
                            departure
                        )
                        ServidorLotacao._update_work_assignment_to_departure(departure)
                    except Exception as err:
                        log.exception(err)
                        message = "Não foi possível finalizar o exercício: %s" % err
                        raise err
                    try:
                        ServidorLotacao._activate_work_assignment_from_departure_canceled(
                            departure, ignore_duplicate_exercise=True
                        )
                    except Exception as err:
                        log.exception(err)
                        message = (
                            "Não foi possível ativar o exercício de afastamento cancelado: %s"
                            % err
                        )
                    try:
                        ServidorLotacao._activate_work_assignment_from_departure(
                            departure
                        )
                    except Exception as err:
                        log.exception(err)
                        message = "Não foi possível ativar o exercício: %s" % err
                    try:
                        ServidorLotacao._return_work_assignment_from_departured(
                            departure
                        )
                    except Exception as err:
                        log.exception(err)
                        message = "Não foi possível criar o novo exercício: %s" % err
                    try:
                        ServidorLotacao._delete_work_assignment_wrong_from_departure(
                            departure
                        )
                    except Exception as err:
                        log.exception(err)
                        message = "Não foi possível apagar o exercício: %s" % err
        except Exception:
            notify = True

        log.info(message)
        if notify:
            raise Exception(message)

    @classmethod
    def _activate_work_assignment_from_departure_canceled(
        cls, departure, ignore_duplicate_exercise=False
    ):
        """
        :py:function:: _activate_work_assignment_from_departure_canceled(cls, departure, ignore_duplicate_exercise=False)

        This method activates work assignment belonging employee. When the departure was canceled.

        :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
        :raises Exception: If validates raise.
        """
        employee_workplaces = departure.servidor.work_assignment_from_departure(
            departure
        )
        if departure.is_canceled:
            ServidorLotacao._update_work_assignments(
                employee_workplaces,
                None,
                None,
                ignore_duplicate_exercise=ignore_duplicate_exercise,
            )
            ServidorLotacao.objects.filter(
                pk__in=employee_workplaces.values("pk")
            ).update(created_by_departure=None, changed_by_departure=None)
        return True

    @classmethod
    def _activate_work_assignment_from_departure(cls, departure):
        """
        :py:function:: _activate_work_assignment_from_departure(cls, departure)

        This method activate work assignment that's from departure.designation_exercise.

        :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
        :raises Exception: If validates raise.
        """
        log.debug("_activate_work_assignment_from_departure")
        employee_workplaces = departure.servidor.work_assignment_from_departure(
            departure
        ).filter(pk__in=departure.designation_exercise.filter().values("pk"))
        to_exclude = []
        for empl in employee_workplaces:
            if (
                empl.changed_by_departure
                and empl.changed_by_departure.pk != departure.pk
                and not empl.changed_by_departure.is_canceled
                or departure.estado == FINISHED
            ):
                to_exclude.append(empl.pk)
        employee_workplaces = employee_workplaces.exclude(pk__in=to_exclude)
        ServidorLotacao._update_work_assignments(
            employee_workplaces, departure, None, ignore_duplicate_exercise=True
        )
        return True

    @classmethod
    def _finalize_work_assignment_from_departure(cls, departure):
        log = getLogger("db")
        """
            :py:function:: _finalize_work_assignment_from_departure(cls, departure)

            This method finalizes work assignment that's from departure.designation_exercise.
            Catch employee workplaces that is active and not in member substitution or inactivation.
            Disregarding Work assignment that in exercise from departure field designation_exercise.

            :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
            :raises Exception: If validates raise.
        """
        log.debug(f"_finalize_work_assignment_from_departure : {departure}")
        if not departure.is_canceled:
            employee_workplaces = departure.servidor.work_assignment_from_departure(
                departure
            )
            employee_workplaces = employee_workplaces.exclude(
                pk__in=departure.designation_exercise.filter(ativo=False).values("pk")
            )
            for work_assignment in employee_workplaces:
                date_end = departure.data_inicio - relativedelta(days=1)
                ServidorLotacao._update_work_assignments(
                    ServidorLotacao.objects.filter(pk=work_assignment.pk),
                    departure,
                    date_end,
                    ignore_duplicate_exercise=True,
                )
        return True

    @classmethod
    def _update_work_assignment_to_departure(cls, departure):
        log = getLogger("db")
        """
            :py:function:: _update_work_assignment_to_departure(cls, departure)

            This method updates the work assignment that the date_end is equal (date_start -1) of the departure.
            Its reason is to mark the work assignment has changed_by_departure.
            It happens when work assignment is ended by hands, before the departure begin.

            :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
            :raises Exception: If validates raise.
        """
        log.debug("_update_work_assignment_to_departure")
        if not departure.is_canceled:
            employee_workplaces = (
                departure.servidor.get_work_assignment()
                .filter(
                    Q(data_vigencia_fim=(departure.data_inicio - relativedelta(days=1)))
                )
                .exclude(pk__in=departure.designation_exercise.filter().values("pk"))
                .exclude(~Q(changed_by_departure=None))
                .exclude(~Q(created_by_departure__servidor=departure.servidor))
            )
            """IMPLEMENTAÇÃO ADICIONADA PARA IMPEDIR QUE UM AFASTAMENTO DO SERVIDOR MARQUE UM EXERCÍCIO COMO "ALTERADO"
                PODE SER COLOCADA IMPLEMENTAÇÃO NO RETORNO DE EXERCÍCIO PRA NÃO RETORNAR EXERCÍCIOS DE SUBSTITUIÇÃO."""
            log.debug(employee_workplaces.count())
            ServidorLotacao._update_work_assignments(
                employee_workplaces,
                departure,
                (departure.data_inicio - relativedelta(days=1)),
                to_change_departure=True,
                ignore_duplicate_exercise=True,
            )
        return True

    @classmethod
    def _return_work_assignment_from_departured(cls, departure):
        """
        :py:function:: _return_work_assignment_from_departured(cls, departure)

        This method creates a designation for the substituted when the substitution ends.
        Returns the member to his work_assignment origin.

        :return: boolean
        :rtype: boolean
        """
        log.debug("----------->_return_work_assignment_from_departured")

        finished = departure._afastamento_finalizado() or departure.estado == CANCELED

        date_start = departure.data_inicio
        date_end = departure.data_fim
        if date_end:
            date_start = date_end + relativedelta(days=1)
        if not date_end or departure.estado == CANCELED:
            date_end = date_start

        if finished and not departure.servidor.has_another_departure(
            date_start, date_start
        ):
            work_assignments = departure.servidor.work_assignments_changed_by_departure(
                departure
            ).exclude(~Q(substitution_substitute=None))

            for work_assignment in work_assignments:
                owner = work_assignment.lotacao.owner.filter(
                    pk=work_assignment.servidor.pk
                ).exists()
                responsible = work_assignment.responsible
                if (
                    responsible
                    and ServidorLotacao.work_assignment(
                        workplace=[work_assignment.lotacao]
                    )
                    .filter(
                        Q(responsible=True)
                        & (
                            Q(data_vigencia_inicio__lte=date_start)
                            & (
                                Q(data_vigencia_fim__gte=date_start)
                                | Q(data_vigencia_fim=None)
                            )
                        )
                    )
                    .exists()
                ):
                    responsible = False
                work_assignments_employee = (
                    departure.servidor.get_work_assignment().filter(
                        Q(lotacao=work_assignment.lotacao)
                        & (
                            Q(data_vigencia_fim__gt=date_end)
                            | Q(data_vigencia_fim__isnull=True)
                        )
                    )
                )
                try:
                    with transaction.atomic():
                        if not work_assignments_employee.exists():
                            new_designation = ServidorLotacao._create(
                                ordinance=work_assignment.ordinance,
                                child_of=work_assignment.child_of,
                                created_by_departure=departure,
                                annotate=True,
                                must_validate_document=False,
                                propagate_resp=True,
                                designacao=work_assignment.designacao,
                                responsible=responsible or owner,
                                owner=work_assignment.owner or owner,
                                servidor=departure.servidor,
                                lotacao=work_assignment.lotacao,
                                publicacao=work_assignment.publicacao,
                                data_vigencia_inicio=date_start,
                                data_vigencia_fim=None,
                                movimentacao_posse=work_assignment.movimentacao_posse,
                            )
                            if new_designation:
                                log.info("Novo Excício criado %s" % new_designation)
                                departures_exercise = (
                                    work_assignment.departures_exercise.exclude(
                                        estado=CANCELED
                                    )
                                )
                                if departures_exercise.exists():
                                    departures_exercise = departures_exercise.latest(
                                        "data_inicio"
                                    )
                                    departures_exercise.designation_exercise.add(
                                        new_designation
                                    )
                                    log.info(
                                        "Exercício %s adicionado ao afastamento %s"
                                        % (work_assignment, departures_exercise)
                                    )
                            else:
                                message = (
                                    "Novo exercício de afastado não foi criado: %s => %s"
                                    % (departure.servidor, work_assignment)
                                )
                                log.info(message)
                        elif (
                            work_assignments_employee.exists()
                            and not work_assignments_employee.latest(
                                "pk"
                            ).substitution_substitute
                        ):
                            work_ass = work_assignments_employee.latest("pk")
                            log.info(
                                "Existe um exercício vigente %s.\nMandará salvar o exercício para atualizá-lo."
                                % work_ass
                            )
                            work_ass.from_substitution = False
                            work_ass.save(
                                must_validate_employee_departured=False,
                                propagate_resp=False,
                            )
                except Exception as err:
                    log.exception(err)
        else:
            log.info(
                "%s - Não finalizou ainda! Ou possui outro afastamento ativo."
                % departure.__str_restful__()
            )
        return True

    @classmethod
    def _update_work_assignments(
        cls,
        employee_workplaces,
        departure,
        date_end,
        to_change_departure=False,
        ignore_duplicate_exercise=False,
    ):
        """
        :py:function:: _update_work_assignments(
            cls, employee_workplaces, departure, date_end, to_change_departure=False, ignore_duplicate_exercise=False)

        This method finalizes work assignment belonging employee. It finalizes a day before the begin of departure.

        :param ServidorLotacao.queryset employee_workplaces: The ServidorLotacao.queryset
        :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
        :param datetime date_end: datetime date_end to set the end of the employee workplace
        :raises Exception: If validates raise.
        """
        log.debug("_update_work_assignments")
        log.debug("_update_work_assignments count: %s" % employee_workplaces.count())
        for employee_workplace in employee_workplaces:
            to_update = False
            date_end_proposed = date_end
            employee_workplace.changed_by_departure = departure
            if date_end and employee_workplace.data_vigencia_inicio > date_end:
                log.debug("_update_work_assignments first if")
                date_end_proposed = employee_workplace.data_vigencia_inicio

            if (
                employee_workplace.data_vigencia_fim != date_end_proposed
                or not date_end_proposed
            ):
                log.debug("_update_work_assignments ------------------ save")
                log.debug(employee_workplace.servidor)
                log.debug("%s %s" % (employee_workplace.pk, employee_workplace))
                log.debug(
                    "%s mundando para => %s"
                    % (
                        (
                            DateUtils.date_to_str(employee_workplace.data_vigencia_fim)
                            if employee_workplace.data_vigencia_fim
                            else "----"
                        ),
                        (
                            DateUtils.date_to_str(date_end_proposed)
                            if date_end_proposed
                            else "-----"
                        ),
                    )
                )
                employee_workplace.data_vigencia_fim = date_end_proposed
                to_update = True
            if to_change_departure:
                to_update = True
            if to_update and not employee_workplace.substitution_substitute.exists():
                employee_workplace.from_substitution = False
                employee_workplace.save(
                    must_validate_employee_departured=False,
                    propagate_resp=False,
                    ignore_duplicate_exercise=ignore_duplicate_exercise,
                )
            else:
                employee_workplace.save()

    @classmethod
    def _delete_work_assignment_wrong_from_departure(cls, departure):
        """
        :py:function:: _delete_work_assignment_wrong_from_departure(cls, departure)

        This method updates work assignment belonging EmployeeWorkplace instance.

        :param BaseLicencaAfastamento departure: The BaseLicencaAfastamento instance
        :raises Exception: If validates raise.
        """
        log.debug("_delete_work_assignment_wrong_from_departure")
        if not departure:
            raise Exception("Afastamento não informado!")
        employee_workplaces = (
            departure.servidor.get_work_assignment()
            .filter(
                lotacao__in=departure.substituicao.values(
                    "designation_substituted__lotacao__pk"
                ),
                created_by_departure=departure,
            )
            .exclude(
                ~Q(substitution_substitute__afastamento=None)
                | ~Q(substitution_substituted__afastamento=None)
                | ~Q(inactivation_jobposition__afastamento=None)
            )
            .exclude(pk__in=departure.designation_exercise.values("pk"))
        )
        if departure.data_fim:
            employee_workplaces = employee_workplaces.exclude(
                data_vigencia_inicio__gt=departure.data_fim
            )
        log.debug(
            "-------delete: %s"
            % [empl.get("pk") for empl in employee_workplaces.values("pk")]
        )
        employee_workplaces.delete()
        log.debug("_delete_work_assignment_wrong_from_departure ---------- END")

        employee_workplaces = (
            departure.servidor.get_work_assignment()
            .filter(
                created_by_departure=departure,
            )
            .exclude(
                ~Q(substitution_substitute__afastamento=None)
                | ~Q(substitution_substituted__afastamento=None)
                | ~Q(inactivation_jobposition__afastamento=None)
            )
            .exclude(pk__in=departure.designation_exercise.values("pk"))
        )
        if not departure.is_canceled and departure.data_fim:
            employee_workplaces = employee_workplaces.exclude(
                data_vigencia_inicio__gt=departure.data_fim
            )
        log.debug(
            "-------delete: %s"
            % [empl.get("pk") for empl in employee_workplaces.values("pk")]
        )
        employee_workplaces.delete()
        log.debug("_delete_work_assignment_wrong_from_departure ---------- END")

    def from_departures_exercise(self):
        """
        :py:function:: from_departures_exercise(self)

        This method returns a queryset of the BaseLicencaAfastamento.

        :return: queryset of the BaseLicencaAfastamento
        :rtype: queryset
        """
        return self.departures_exercise.filter()

    def from_departures_exercise_active(self):
        """
        :py:function:: from_departures_exercise_active(self)

        This method returns a queryset of the BaseLicencaAfastamento. Uses self.from_departures_exercise.
        Only actives.

        :return: queryset of the BaseLicencaAfastamento
        :rtype: queryset
        """
        date = datetime.now().date()
        return self.from_departures_exercise().filter(
            Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
        )

    def set_from_substitution(self):
        self.from_substitution = (
            self.created_by_departure is not None and not self.owner
        )

    def anotacao(self, *args, **kargs):
        tipo = Publicacao.get_tipo(self.publicacao)
        resumo = self.designacao and "DESIGNAÇÃO EXERCÍCIO" or "LOTAÇÃO"
        data_inicio = self.data_vigencia_inicio
        texto_lotacao = self.get_texto()
        if not self.pk or not self.anotacao_geral_lotacao:
            anotacao_geral_lotacao = AnotacaoGeral.manage_instance(
                servidor=self.servidor,
                tipo_documento=tipo,
                publicacao=self.publicacao,
                data_portaria_inicio=data_inicio,
                texto=texto_lotacao,
                resumo=resumo,
            )
            AnotacaoGeral.objects.filter(pk=anotacao_geral_lotacao.pk).update(
                indireto=True
            )
            self.anotacao_geral_lotacao = anotacao_geral_lotacao
        else:
            anotacao_geral_lotacao = AnotacaoGeral.objects.get(
                pk=self.anotacao_geral_lotacao.pk
            )
            anotacao_geral_lotacao.publicacao = self.publicacao
            anotacao_geral_lotacao.data_portaria_inicio = data_inicio
            anotacao_geral_lotacao.texto = texto_lotacao
            anotacao_geral_lotacao.resumo = resumo
            anotacao_geral_lotacao.servidor = self.servidor
            anotacao_geral_lotacao.tipo_documento = tipo
            anotacao_geral_lotacao.indireto = False
            anotacao_geral_lotacao.save()
        return True

    def get_texto(self):
        texto = ""
        mid = "rh-anotacao-lotacao"
        if self.designacao:
            mid = "rh-anotacao-det-exercicio"
        origem = Message.objects.get(mid=mid)
        texto = origem.formated(
            {
                "portaria": (
                    "%s" % self.publicacao
                    if self.publicacao
                    else " portaria não informada "
                ),
                "data_portaria": DateUtils.date_to_str(self.data_vigencia_inicio),
                "data": DateUtils.date_to_str(self.data_vigencia_inicio),
                "nome": self.servidor.pessoa_fisica.nome,
                "lotacao": self.lotacao,
                "provisorio": "%s" % " provisória" if self.provisorio else "",
            }
        )
        return texto

    def delete(self, *args, **kwargs):
        """
        Delete sobrescrito para apagar a anotação gerada, caso exista.
        """
        if (
            self.anotacao_geral_lotacao
            and AnotacaoGeral.objects.filter(pk=self.anotacao_geral_lotacao.pk).exists()
        ):
            self.anotacao_geral_lotacao.delete()
        super(ServidorLotacao, self).delete(*args, **kwargs)

    @classmethod
    def exist_employee_workplace(
        cls, employee, workplace, designation=False, created_by_departure=None
    ):
        """
        :py:function:: exist_employee_workplace(cls, employee, workplace, designation)

        This method returns the last a ServidorLotacao instance found.
        Considering the parameters informed to search.

        :parameter Servidor employee: Servidor instance
        :parameter Lotacao workplace: Lotacao instance
        :return: The last ServidorLotacao found or None
        :rtype: ServidorLotacao
        """
        employee_workplaces = (
            employee.workplace_only if not designation else employee.work_assignment
        )
        employee_workplaces = employee_workplaces.filter(
            lotacao=workplace, from_substitution=True
        )
        if created_by_departure:
            employee_workplaces = employee_workplaces.filter(from_substitution=True)
        return (
            employee_workplaces.latest("data_vigencia_inicio")
            if employee_workplaces.exists()
            else None
        )

    @classmethod
    def finish_active_workplace(cls, employee, effective_date):
        qs = employee.workplace_only_active
        employee_workplace = qs.last()
        if not employee_workplace:
            err = Exception(
                "Erro finalizando lotação ativa. O servidor %s não possui lotação ativa."
                % employee
            )
            log.exception(err)
            raise err

        end_date = effective_date - relativedelta(days=1)
        start_date = employee_workplace.data_vigencia_inicio
        employee_workplace.data_vigencia_fim = (
            end_date if end_date >= start_date else start_date
        )
        employee_workplace.save()
        return employee_workplace

    @classmethod
    def _create(cls, **kargs):
        """
        :py:function:: _create(cls, **kargs)

        This method tries to find a ServidorLotacao or creates one.
        Also notifies users responsible to solve the problems.

        :parameter dict kargs: Dict with arguments of ServidorLotacao

        :return: ServidorLotacao instance or None
        :rtype: ServidorLotacao
        """
        employee_workplace = None
        notify = False
        err = None
        message = None

        propagate = kargs.get("propagate", False)
        propagate_resp = kargs.get("propagate_resp", False)

        if kargs.get("servidor", None) is None:
            notify = True
            message = "Servidor não informado"
        elif kargs.get("lotacao", None) is None:
            notify = True
            message = (
                "Lotação não informada. Nova lotação do servidor %s não foi criada."
                % kargs.get("servidor")
            )
        elif kargs.get("publicacao", None) is None and kargs.get(
            "must_validate_document", True
        ):
            notify = True
            message = (
                "Publicação não informada. Nova lotação do servidor %s não foi criada."
                % kargs.get("servidor")
            )
        elif kargs.get("data_vigencia_inicio", None) is None:
            notify = True
            message = (
                "Data de início não informada. Nova lotação do servidor %s não foi criada."
                % kargs.get("servidor")
            )
        else:
            try:
                with transaction.atomic():
                    employee_workplace = cls.exist_employee_workplace(
                        kargs.get("servidor"),
                        kargs.get("lotacao"),
                        designation=kargs.get("designacao", False),
                        created_by_departure=kargs.get("created_by_departure", None),
                    )
                    if not employee_workplace:
                        posse = kargs.get("posse", None)
                        if posse is None:
                            posse = (
                                kargs.get("servidor")
                                ._get_posses()
                                .latest("data_exercicio")
                                if kargs.get("servidor")._get_posses().exists()
                                else posse
                            )
                        employee_workplace = ServidorLotacao(
                            ordinance=kargs.get("ordinance", False),
                            child_of=kargs.get("child_of", None),
                            created_by_departure=kargs.get(
                                "created_by_departure", None
                            ),
                            designacao=kargs.get("designacao", False),
                            responsible=kargs.get("responsible", False),
                            owner=kargs.get("owner", False),
                            commission=kargs.get("commission", False),
                            servidor=kargs.get("servidor"),
                            lotacao=kargs.get("lotacao"),
                            publicacao=kargs.get("publicacao"),
                            data_vigencia_inicio=kargs.get("data_vigencia_inicio"),
                            data_vigencia_fim=kargs.get("data_vigencia_fim", None),
                            movimentacao_posse=posse,
                            annotate=kargs.get("annotate", True),
                        )
                        employee_workplace.save(
                            ignore_duplicate_exercise=kargs.get(
                                "ignore_duplicate_exercise", True
                            ),
                            must_validate_document=kargs.get(
                                "must_validate_document", True
                            ),
                            propagate_resp=propagate_resp,
                        )
            except Exception as err:
                log.exception(err)
                employee_workplace = None
                notify = True
                message = (
                    "Erro criando nova lotação %s do servidor não foi criada. %s"
                    % (kargs.get("servidor"), err)
                )
        if notify:
            log.info(message)
        if propagate:
            if err:
                raise err
            elif message:
                raise Exception(message)

        return (
            employee_workplace if employee_workplace and employee_workplace.pk else None
        )

    @classmethod
    def cmd_atualizar_ativo(cls, servidor_lotacao=[]):
        """
        Este método é responsável por atualizar o campo ativo baseando-se na data de vigência.
        """
        today = datetime.now().date()
        query = (
            Q(data_vigencia_fim__lt=today)
            | Q(data_vigencia_fim=None)
            | Q(data_vigencia_inicio=today)
        )
        if len(servidor_lotacao) > 0:
            query = Q(pk__in=servidor_lotacao)

        employee_workplaces = ServidorLotacao.objects.filter(query)
        log.info(
            "ServidorLotacao: quantidade para atualizar %s"
            % employee_workplaces.count()
        )
        for sl in employee_workplaces.order_by("servidor"):
            sl.atualiza_cache_ativo()

    def atualiza_cache_ativo(self):
        """
        Este método deve ser chamado no post_save/post_delete de MovimentacaoPosse, MovimentacaoAposentadoria e
            MovimentacaoDesligamento para atualizar o cache ativo de ServidorLotacao.
        """
        validate_posse = ServidorLotacao.validate_posse
        validate_publicacao = ServidorLotacao.validate_publicacao
        ServidorLotacao.validate_posse = lambda x: True
        ServidorLotacao.validate_publicacao = lambda x: True
        valid = True
        try:
            with transaction.atomic():
                employee_workplace = ServidorLotacao.objects.get(pk=self.pk)
                if employee_workplace.ativo != employee_workplace.is_active():
                    message = (
                        "%s CACHE ACTIVE: %s para %s - %s"
                        % (
                            employee_workplace,
                            employee_workplace.ativo,
                            employee_workplace.is_active(),
                            employee_workplace.servidor,
                        )
                    ).upper()
                    log.info(message)
                    employee_workplace.ativo = employee_workplace.is_active()
                    employee_workplace.from_substitution = False
                    employee_workplace.save(
                        must_validate_employee_departured=False, propagate_resp=False
                    )
        except Exception as err:
            log.exception(err)
            ServidorLotacao.objects.filter(pk=self.pk).update(ativo=self.is_active())
            log.info(
                "Ocorreu erro ao atualizar o campo ativo da lotação %s."
                % employee_workplace
            )
            notify_employee(mensagem=err)
            valid = False
        ServidorLotacao.validate_posse = validate_posse
        ServidorLotacao.validate_publicacao = validate_publicacao
        return valid

    @classmethod
    def cmd_update_owner_field(cls, employee_workplaces=[]):
        hoje = datetime.now().date()
        query = (
            Q(data_vigencia_fim__lt=hoje)
            | Q(data_vigencia_fim=None)
            | Q(data_vigencia_inicio=hoje)
        )
        if len(employee_workplaces) > 0:
            query = Q(pk__in=employee_workplaces)
        employee_workplaces = ServidorLotacao.objects.filter(query)
        log.info(
            "cmd_update_owner_field ServidorLotacao: quantidade para atualizar %s"
            % employee_workplaces.count()
        )
        for sl in employee_workplaces.order_by("servidor"):
            sl._update_owner_field()

    def _update_owner_field(self):
        """
        Este método deve ser chamado no post_save/post_delete de MovimentacaoPosse, MovimentacaoAposentadoria e
            MovimentacaoDesligamento para atualizar o cache ativo de ServidorLotacao.
        """
        valid = True
        employee_workplace = ServidorLotacao.objects.get(pk=self.pk)
        validate_posse = ServidorLotacao.validate_posse
        validate_publicacao = ServidorLotacao.validate_publicacao
        ServidorLotacao.validate_posse = lambda x: True
        ServidorLotacao.validate_publicacao = lambda x: True
        try:
            with transaction.atomic():
                owner = employee_workplace.servidor._check_owner_location(
                    employee_workplace
                )
                if not employee_workplace.owner and owner:
                    message = (
                        "%s CACHE OWNER: %s => %s - %s"
                        % (
                            employee_workplace,
                            employee_workplace.owner,
                            owner,
                            employee_workplace.servidor,
                        )
                    ).upper()
                    log.info(message)
                    employee_workplace.owner = owner
                    employee_workplace.from_substitution = False
                    employee_workplace.save(propagate_resp=False)
        except Exception as err:
            log.exception(err)
            log.info(
                "Ocorreu erro ao atualizar o campo owner de %s." % employee_workplace
            )
            notify_employee(mensagem=err)
            valid = False
        ServidorLotacao.validate_posse = validate_posse
        ServidorLotacao.validate_publicacao = validate_publicacao
        return valid

    def update_chief_immediate_employee(self, new=False, active=False):
        """
        :py:function:: update_chief_immediate_employee(self, new=False)

        This method verifies if the employee workplace ins't exercise. Then looks if its a new employee workplace
        or is comming active from finished situtation.

        Then call self.servidor.update_chief_immediate(mandatory=True).
        """
        if not self.designacao and (
            (new and self.is_active()) or (not active and self.is_active())
        ):
            self.servidor.update_chief_immediate(mandatory=True)

    def update_telework_approver(self, new=False, active=False):
        """
        Função responsável por atualizar o aprovador do teletrabalho.
        """
        now = datetime.now().date()
        mov_teletrabalhos = MovimentacaoTeletrabalho.objects.filter(
            Q(data_inicio__lte=now),
            Q(data_fim__gt=now) | Q(data_fim__isnull=True),
            servidor=self.servidor,
        )
        if not mov_teletrabalhos:
            return
        if not self.designacao and (
            (new and self.is_active()) or (not active and self.is_active())
        ):
            responsible = (
                self.lotacao.responsible_substituted
                if self.lotacao.responsible_substituted
                else self.lotacao.responsavel
            )
            if responsible:
                try:
                    mov_teletrabalhos.update(aprovador=responsible)
                except Exception as e:
                    log.error(e)

    @classmethod
    def finish_workplace_from_fire(cls, fire_move):
        """
        Este método é responsável por aplicar uma data vigência de fim as lotações.
        employee, date_fired, possession_fired
        """
        today = datetime.now().date()
        employee = fire_move.servidor
        date_fired = fire_move.data_desligamento
        possession = fire_move.movimentacao_posse
        message = "Finalizando lotações e exercícios de %s em %s." % (
            employee,
            DateUtils.date_to_str(date_fired),
        )
        if (
            not employee.member_type_by_possession
            and fire_move.termination_process
            and fire_move.data_desligamento <= today
        ):
            log.info(message)
            print(message)
            empl_workplaces = employee._raw_locations(active=True)
            if empl_workplaces.exists() and date_fired and not employee.is_ativo():
                date_fired = date_fired - relativedelta(days=1)
                message = (
                    "\nAplicando a data de fim da vigência %s..."
                    % DateUtils.date_to_str(date_fired)
                )
                for workplace in empl_workplaces:
                    message += "\nLotação do servidor: %s." % workplace
                    if (
                        not workplace.data_vigencia_fim
                        or workplace.data_vigencia_fim > date_fired
                    ):
                        workplace.data_vigencia_fim = date_fired
                        if not workplace.publicacao:
                            workplace.publicacao = possession.publicacao_movimentacao
                        if not workplace.movimentacao_posse:
                            workplace.movimentacao_posse = possession
                        try:
                            with transaction.atomic():
                                workplace.save()
                        except Exception as err:
                            log.exception(err)
                            print(err)
                            message += "\nErro em %s" % err
                log.info(message)
                print(message)

    @classmethod
    def lotacao_por_provimento(cls, provimento):
        """
        Este método é utilizado para modificar a lotação de um servidor com uma nova posse. Os provimentos abordados
        serão: MovimentacaoPosse, MovimentacaoTitularizacao, MovimentacaoPromocao e MovimentacaoRemocaoMembro.
        Apenas provimentos para membros serão tratados.
        """
        if provimento.is_active() and provimento.servidor.member_type_by_possession:
            lotacao = None
            if provimento.my_type in ["movimentacaoremocaomembro"] and hasattr(
                provimento, "lotacao_destino"
            ):
                if MovimentacaoRemocaoMembro.objects.filter(
                    servidor=provimento.servidor
                ):
                    lotacao = provimento.movimentacaoremocaomembro.lotacao_destino
                elif MovimentacaoRemocao.objects.filter(servidor=provimento.servidor):
                    lotacao = provimento.lotacao_destino
            elif provimento.my_type in [
                "movimentacaoposse",
                "movimentacaopromocao",
                "movimentacaotitularizacao",
            ]:
                lotacao = provimento.quadro.cargo.lotacao_responsavel

            if lotacao:
                ServidorLotacao._create(
                    servidor=provimento.servidor,
                    lotacao=lotacao,
                    publicacao=provimento.publicacao_movimentacao,
                    data_vigencia_inicio=provimento.data_exercicio,
                    data_vigencia_fim=provimento.data_desligamento,
                    annotate=True,
                )

    @classmethod
    def work_assignment_effective_exercise(cls, workplace=[]):
        """
        :py:function:: work_assignment_effective_exercise(self)

        This method returns all employee work assignments in effective exercise.

        :return: queryset, ServidorLotacao
        :rtype: queryset
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        empl_workplaces = []
        start_date = end_date = datetime.now().date()
        query = ServidorLotacao.work_assignment(workplace=workplace).filter(
            Q(data_vigencia_inicio__lte=start_date)
            & (Q(data_vigencia_fim__gte=start_date) | Q(data_vigencia_fim=None))
        )
        for wkpl in query:
            empl_workplaces.append(wkpl.pk)

        departures = (
            BaseLicencaAfastamento.objects.filter(
                Q(data_inicio__lte=end_date)
                & (Q(data_fim__gte=start_date) | Q(data_fim=None))
            )
            .exclude(estado=CANCELED)
            .exclude(~Q(desempenhofuncao=None) | ~Q(atuacaogrupotrabalho=None))
        )
        if departures.exists():
            departures = [
                dep.pk
                for dep in departures.latest(
                    "data_inicio"
                ).find_departure_concatenated()
            ]
        _work_assignment = query.filter(
            changed_by_departure__pk__in=departures
        ).exclude(
            ~Q(changed_by_departure__desempenhofuncao=None)
            | ~Q(changed_by_departure__atuacaogrupotrabalho=None)
        )

        for wkpl in _work_assignment:
            empl_workplaces.append(wkpl.pk)

        return ServidorLotacao.objects.filter(pk__in=empl_workplaces)

    @classmethod
    def cmd_main_schedule_date(cls):
        """Este método é responsável por atualizar os exercícios para main = True quando main_schedule_date por preenchido."""
        today = datetime.now().date()
        query = Q(main_schedule_date=today)

        query = ServidorLotacao.objects.filter(query)
        total = query.count()
        count = 0
        print(
            f"Processo de atualização de principal em lotações. Total {count} de {total}."
        )
        for sl in query.order_by("designacao"):
            sl.action_set_main(True)
            count += 1
            print(f"{count} de {total} -> {sl}")


class EmployeeWorkplaceHistory(AuditTimestampModel):
    employee_workplace = models.ForeignKey(
        "ServidorLotacao",
        null=True,
        blank=True,
        related_name="history_servidor_lotacao",
        on_delete=models.SET_NULL,
    )
    pk_history = models.IntegerField()
    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="history_servidor_lotacao",
        on_delete=models.CASCADE,
    )
    movimentacao_posse = models.ForeignKey(
        "MovimentacaoPosse",
        related_name="history_lotacoes",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    lotacao = models.ForeignKey(
        "Lotacao",
        null=True,
        blank=False,
        verbose_name="Lotação/Designação",
        related_name="history_servidores_lotacao",
        on_delete=models.SET_NULL,
    )
    publicacao = models.ForeignKey(
        "Publicacao", null=True, blank=True, on_delete=models.CASCADE
    )
    anotacao_geral_lotacao = models.ForeignKey(
        "AnotacaoGeral", null=True, blank=True, on_delete=models.CASCADE
    )
    designacao = models.BooleanField(
        default=False, verbose_name="Designação de exercício"
    )
    provisorio = models.BooleanField(default=False, verbose_name="Lotação Provisória")
    data_vigencia = models.DateField(
        null=True, verbose_name="Data Vigência", blank=True
    )
    data_vigencia_inicio = models.DateField(
        null=True, verbose_name="Data Vigência Início"
    )
    data_vigencia_fim = models.DateField(
        null=True, blank=True, verbose_name="Data Vigência Fim"
    )
    data_cadastro = models.DateField(auto_now_add=True)
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    full_exercise = models.BooleanField(default=False, verbose_name="Exercício pleno")
    responsible = models.BooleanField(default=False, verbose_name="Responsável")
    partial_responsible = models.BooleanField(
        default=False, verbose_name="Responsável parcial"
    )
    from_substitution = models.BooleanField(default=False)
    child_of = models.ForeignKey(
        "ServidorLotacao",
        null=True,
        blank=True,
        verbose_name="Derivada de",
        related_name="history_father_of",
        on_delete=models.SET_NULL,
    )
    changed_by_departure = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="history_employee_workplace_changed",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_by_departure = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="history_employee_workplace_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    ativo = models.BooleanField(default=True)
    owner = models.BooleanField(default=False)
    commission = models.BooleanField(default=False)
    main = models.BooleanField(default=False, verbose_name="Principal")
    ordinance = models.BooleanField(
        default=False, blank=True, verbose_name="Por portaria"
    )
    annotate = models.BooleanField(default=True, blank=True, verbose_name="Anotar?")
    provisional_reason = models.TextField(
        blank=True, null=True, verbose_name="Motivo Provisória"
    )
    main_schedule_date = models.DateField(
        null=True, blank=True, verbose_name="Data agendada para marcar principal"
    )

    def __str__(self):
        if self.designacao:
            verbose = "EXERCÍCIO"
        else:
            verbose = "LOTAÇÃO"
        if self.provisorio:
            verbose = "%s - PROVISÓRIA" % verbose
        return "HISTÓRICO - %s: %s à %s" % (
            "%s - %s" % (verbose, self.lotacao),
            DateUtils.date_to_str(self.data_vigencia_inicio),
            (
                DateUtils.date_to_str(self.data_vigencia_fim)
                if self.data_vigencia_fim
                else "----"
            ),
        )


class WorkplaceExerciseHistory(AuditTimestampModel):
    class Meta:
        verbose_name = "Histórico de lotações e seus exercícios"
        ordering = ["date"]

    """
        Entidade 'Entidade' deixou de existir, utilizei apenas 'UnidadeAdministrativa'
    """
    workplace = models.ForeignKey(
        Lotacao, related_name="exercise_history", on_delete=models.CASCADE
    )
    employee_workplace = models.ForeignKey(
        EmployeeWorkplaceHistory,
        null=True,
        blank=True,
        on_delete=SET_NULL,
        related_name="exercise_history",
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "HISTÓRICO: %s - LOCAL: %s - EXERCÍCIO: %s" % (
            DateUtils.datetime_to_str(self.date),
            self.workplace,
            self.employee_workplace,
        )

    @classmethod
    def cmd_exercise_per_day(cls, date=None):
        log.info("Lançando histórico de exercícios do local de lotação.")
        date = date if date else datetime.now().date()
        workplace_exercise = (
            Lotacao.objects.filter(
                Q(history_servidores_lotacao__servidor__tipo__in=["M"])
                & Q(history_servidores_lotacao__designacao=True)
                & Q(history_servidores_lotacao__responsible=True)
                & Q(history_servidores_lotacao__data_vigencia_inicio__lte=date)
                & (
                    Q(history_servidores_lotacao__data_vigencia_fim__gte=date)
                    | Q(history_servidores_lotacao__data_vigencia_fim=None)
                )
            )
            .distinct()
            .values("pk")
        )
        for workplace in Lotacao.objects.filter(~Q(executionorgan=None)).exclude(
            pk__in=workplace_exercise
        ):
            WorkplaceExerciseHistory(workplace=workplace).save()

        for employee_workplace in EmployeeWorkplaceHistory.objects.filter(
            ~Q(lotacao__executionorgan=None)
            & Q(servidor__tipo__in=["M"])
            & Q(designacao=True)
            & Q(responsible=True)
            & Q(data_vigencia_inicio__lte=date)
            & (Q(data_vigencia_fim__gte=date) | Q(data_vigencia_fim=None))
        ):
            WorkplaceExerciseHistory(
                workplace=employee_workplace.lotacao,
                employee_workplace=employee_workplace,
            ).save()


class MovimentacaoPessoal(RHObject):
    """
    Movimentação Pessoal.
    """

    publicacao_movimentacao = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Publicação Movimentação",
    )
    data_alteracao = models.DateField(auto_now=True, null=True, blank=True)
    publicacao_alteracao = models.ForeignKey(
        "Publicacao",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="movimentacao",
        verbose_name="Publicação Alteração",
    )
    my_type = models.CharField(max_length=60, db_index=True, null=True, blank=True)

    _map_to_instance = {
        "movimentacaoposse": "",
        "movimentacaoaproveitamento": "movimentacaoposse",
        "movimentacaopromocao": "movimentacaoposse",
        "requestmove": "movimentacaoposse",
        "movimentacaotitularizacao": "movimentacaoposse.movimentacaopromocao",
        "movimentacaoremocaomembro": "movimentacaoposse",
        "movimentacaoreadaptacao": "movimentacaoposse",
        "movimentacaoreconducao": "movimentacaoposse",
        "movimentacaoreintegracao": "movimentacaoposse",
        "movimentacaoreversao": "movimentacaoposse",
        "benefitmovement": "movimentacaoposse",
        "possessiontrainee": "movimentacaoposse",
        "possessioncollaborator": "movimentacaoposse",
        "movimentacaodesligamento": "",
        "movimentacaoaposentadoria": "movimentacaodesligamento",
        "terminationbenefitmovement": "movimentacaodesligamento",
        "movimentacaorequisicao": "",
        "movimentacaosubstituicao": "",
        "movimentacaosubstituicaomembro": "movimentacaosubstituicao",
        "movimentacaoconcessao": "",
        "movimentacaoremocao": "",
        "movimentacaoredistribuicao": "",
        "movimentacaodescontoLegal": "",
        "movimentacaoestabilizacao": "",
        "declaracaoatividade": "",
        # 'declarationactivityretiree': '',
        "movimentacaoprogressao": "",
        "movimentacaoenquadramento": "movimentacaoprogressao",
        "afastamentocompeticao": "baselicencaafastamento.afastamento",
        "afastamentocursoconcurso": "baselicencaafastamento.afastamento",
        "afastamentodeslocamento": "baselicencaafastamento.afastamento",
        "afastamentoeleitoral": "baselicencaafastamento.afastamento",
        "afastamentoestudar": "baselicencaafastamento.afastamento",
        "afastamentomandatoeletivo": "baselicencaafastamento.afastamento",
        "afastamentomissao": "baselicencaafastamento.afastamento",
        "afastamentodisponibilidade": "baselicencaafastamento.afastamento",
        "afastamentooutroorgao": "baselicencaafastamento.afastamento",
        "afastamentoprisao": "baselicencaafastamento.afastamento",
        "afastamentosuspensao": "baselicencaafastamento.afastamento",
        "afastamentosindicanciaadm": "baselicencaafastamento.afastamento",
        "afastamentocomparecimentojuizo": "baselicencaafastamento.afastamento",
        "afastamentocandidatura": "baselicencaafastamento.afastamento",
        "afastamentoservirjuri": "baselicencaafastamento.afastamento",
        "afastamentotreinamento": "baselicencaafastamento.afastamento",
        "licencaafastamentoconjuge": "baselicencaafastamento.licenca",
        "licencaatividadepolitica": "baselicencaafastamento.licenca",
        "licencacapacitacao": "baselicencaafastamento.licenca",
        "licencainteresseparticular": "baselicencaafastamento.licenca",
        "licencamandatoclassista": "baselicencaafastamento.licenca",
        "awardlicense": "baselicencaafastamento.licenca",
        "licencaservicomilitar": "baselicencaafastamento.licenca",
        "licencasaude": "baselicencaafastamento.licenca",
        "licencasaude3dias": "baselicencaafastamento.licenca.licencasaude",
        "licencasaude30dias": "baselicencaafastamento.licenca.licencasaude",
        "baselicencasaudejuntamedica": "baselicencaafastamento.licenca.licencasaude",
        "licencasaudejuntamedica": "baselicencaafastamento.licenca.licencasaude.baselicencasaudejuntamedica",
        "licencaadocao": "baselicencaafastamento.licenca.licencasaude.baselicencasaudejuntamedica",
        "licencadoencapessoafamilia": "baselicencaafastamento.licenca.licencasaude.baselicencasaudejuntamedica",
        "licencamaternidade": "baselicencaafastamento.licenca.licencasaude.baselicencasaudejuntamedica",
        "ausenciacasamento": "baselicencaafastamento.licenca",
        "ausenciaconclusao": "baselicencaafastamento.licenca",
        "ausenciadoacaosangue": "baselicencaafastamento.licenca",
        "ausenciaeleitor": "baselicencaafastamento.licenca",
        "ausencianascimento": "baselicencaafastamento.licenca",
        "ausenciafalecimento": "baselicencaafastamento.licenca",
        "feriasafastamento": "baselicencaafastamento",
        "viagem": "baselicencaafastamento",
        "recesso": "baselicencaafastamento",
        "folgacompensacao": "baselicencaafastamento",
        "folgaeleitoral": "baselicencaafastamento",
        "folgaaniversario": "baselicencaafastamento",
        "atuacaogrupotrabalho": "baselicencaafastamento",
        "desempenhofuncao": "baselicencaafastamento",
        "plantao": "baselicencaafastamento",
        "bancodehoras": "baselicencaafastamento",
        "healthprevent": "baselicencaafastamento",
    }

    class Meta:
        verbose_name = "Movimentação Pessoal"
        db_table = "rh_movpessoal"

    class ErroPublicacaoNaoEncontrada(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Publicação não encontrada.")
            )

    def __str__(self):
        return self.servidor.pessoa_fisica.nome

    @property
    def my_origin(self):
        instance = self
        if self.pk:
            _klass = "%s.%s" % (
                instance._map_to_instance.get(instance.my_type),
                instance.my_type,
            )
            for _k in _klass.split("."):
                if hasattr(instance, _k):
                    instance = getattr(instance, _k, instance)
        return instance

    def get_my_type(self):
        return self.my_type if self.my_type else self.instancia_modelo._meta.model_name

    @property
    def instancia_modelo(self):
        """
        Este método é responsável por informar a instância baseado no mapeamento
        dos modelos.
        """
        instance = self
        if hasattr(instance, "movimentacaoposse"):
            instance = instance.movimentacaoposse
            if hasattr(instance, "movimentacaoaproveitamento"):
                instance = instance.movimentacaoaproveitamento
            elif hasattr(instance, "movimentacaopromocao"):
                instance = instance.movimentacaopromocao
                if hasattr(instance, "movimentacaotitularizacao"):
                    instance = instance.movimentacaotitularizacao
            elif hasattr(instance, "movimentacaoremocaomembro"):
                instance = instance.movimentacaoremocaomembro
            elif hasattr(instance, "movimentacaoreadaptacao"):
                instance = instance.movimentacaoreadaptacao
            elif hasattr(instance, "movimentacaoreconducao"):
                instance = instance.movimentacaoreconducao
            elif hasattr(instance, "movimentacaoreintegracao"):
                instance = instance.movimentacaoreintegracao
            elif hasattr(instance, "movimentacaoreversao"):
                instance = instance.movimentacaoreversao
            elif hasattr(instance, "requestmove"):
                instance = instance.requestmove
            elif hasattr(instance, "possessiontrainee"):
                instance = instance.possessiontrainee
            elif hasattr(instance, "possessionresident"):
                instance = instance.possessionresident
            elif hasattr(instance, "possessioncollaborator"):
                instance = instance.possessioncollaborator
            elif hasattr(instance, "benefitmovement"):
                instance = instance.benefitmovement
        elif hasattr(instance, "movimentacaodesligamento"):
            instance = instance.movimentacaodesligamento
            if hasattr(instance, "movimentacaoaposentadoria"):
                instance = instance.movimentacaoaposentadoria
            if hasattr(instance, "terminationbenefitmovement"):
                instance = instance.terminationbenefitmovement
        elif hasattr(instance, "movimentacaorequisicao"):
            instance = instance.movimentacaorequisicao
        elif hasattr(instance, "movimentacaosubstituicao"):
            instance = instance.movimentacaosubstituicao
            if hasattr(instance, "movimentacaosubstituicaomembro"):
                instance = instance.movimentacaosubstituicaomembro
        elif hasattr(instance, "movimentacaoconcessao"):
            instance = instance.movimentacaoconcessao
        elif hasattr(instance, "movimentacaoremocao"):
            instance = instance.movimentacaoremocao
        elif hasattr(instance, "movimentacaoredistribuicao"):
            instance = instance.movimentacaoredistribuicao
        elif hasattr(instance, "movimentacaodescontoLegal"):
            instance = instance.movimentacaodescontoLegal
        elif hasattr(instance, "movimentacaoestabilizacao"):
            instance = instance.movimentacaoestabilizacao
        elif hasattr(instance, "declaracaoatividade"):
            instance = instance.declaracaoatividade
        # elif hasattr(instance, 'declarationactivityretiree'):
        #     instance = instance.declarationactivityretiree
        elif hasattr(instance, "movimentacaoprogressao"):
            instance = instance.movimentacaoprogressao
            if hasattr(instance, "movimentacaoenquadramento"):
                instance = instance.movimentacaoenquadramento
        elif hasattr(instance, "baselicencaafastamento"):
            instance = instance.baselicencaafastamento
            if hasattr(instance, "afastamento"):
                instance = instance.afastamento
                if hasattr(instance, "afastamentocompeticao"):
                    instance = instance.afastamentocompeticao
                elif hasattr(instance, "afastamentocursoconcurso"):
                    instance = instance.afastamentocursoconcurso
                elif hasattr(instance, "afastamentodeslocamento"):
                    instance = instance.afastamentodeslocamento
                elif hasattr(instance, "afastamentoeleitoral"):
                    instance = instance.afastamentoeleitoral
                elif hasattr(instance, "afastamentoestudar"):
                    instance = instance.afastamentoestudar
                elif hasattr(instance, "afastamentomandatoeletivo"):
                    instance = instance.afastamentomandatoeletivo
                elif hasattr(instance, "afastamentomissao"):
                    instance = instance.afastamentomissao
                elif hasattr(instance, "afastamentodisponibilidade"):
                    instance = instance.afastamentodisponibilidade
                elif hasattr(instance, "afastamentooutroorgao"):
                    instance = instance.afastamentooutroorgao
                elif hasattr(instance, "afastamentoprisao"):
                    instance = instance.afastamentoprisao
                elif hasattr(instance, "afastamentosuspensao"):
                    instance = instance.afastamentosuspensao
                elif hasattr(instance, "afastamentosindicanciaadm"):
                    instance = instance.afastamentosindicanciaadm
                elif hasattr(instance, "afastamentocomparecimentojuizo"):
                    instance = instance.afastamentocomparecimentojuizo
                elif hasattr(instance, "afastamentoservirjuri"):
                    instance = instance.afastamentoservirjuri
                elif hasattr(instance, "afastamentotreinamento"):
                    instance = instance.afastamentotreinamento
                elif hasattr(instance, "afastamentocandidatura"):
                    instance = instance.afastamentocandidatura
            elif hasattr(instance, "licenca"):
                instance = instance.licenca
                if hasattr(instance, "licencaafastamentoconjuge"):
                    instance = instance.licencaafastamentoconjuge
                elif hasattr(instance, "licencaatividadepolitica"):
                    instance = instance.licencaatividadepolitica
                elif hasattr(instance, "licencacapacitacao"):
                    instance = instance.licencacapacitacao
                elif hasattr(instance, "licencainteresseparticular"):
                    instance = instance.licencainteresseparticular
                elif hasattr(instance, "licencamandatoclassista"):
                    instance = instance.licencamandatoclassista
                elif hasattr(instance, "awardlicense"):
                    instance = instance.awardlicense
                elif hasattr(instance, "licencaservicomilitar"):
                    instance = instance.licencaservicomilitar
                elif hasattr(instance, "licencasaude"):
                    instance = instance.licencasaude
                    if hasattr(instance, "licencasaude3dias"):
                        instance = instance.licencasaude3dias
                    elif hasattr(instance, "licencasaudehoras"):
                        instance = instance.licencasaudehoras
                    elif hasattr(instance, "licencasaude30dias"):
                        instance = instance.licencasaude30dias
                    elif hasattr(instance, "baselicencasaudejuntamedica"):
                        instance = instance.baselicencasaudejuntamedica
                        if hasattr(instance, "licencasaudejuntamedica"):
                            instance = instance.licencasaudejuntamedica
                        if hasattr(instance, "licencaadocao"):
                            instance = instance.licencaadocao
                        elif hasattr(instance, "licencadoencapessoafamilia"):
                            instance = instance.licencadoencapessoafamilia
                        elif hasattr(instance, "licencamaternidade"):
                            instance = instance.licencamaternidade
            elif hasattr(instance, "ausencia"):
                instance = instance.ausencia
                if hasattr(instance, "ausenciacasamento"):
                    instance = instance.ausenciacasamento
                elif hasattr(instance, "ausenciaconclusao"):
                    instance = instance.ausenciaconclusao
                elif hasattr(instance, "ausenciadoacaosangue"):
                    instance = instance.ausenciadoacaosangue
                elif hasattr(instance, "ausenciaeleitor"):
                    instance = instance.ausenciaeleitor
                elif hasattr(instance, "ausencianascimento"):
                    instance = instance.ausencianascimento
                elif hasattr(instance, "ausenciafalecimento"):
                    instance = instance.ausenciafalecimento
            elif hasattr(instance, "feriasafastamento"):
                instance = instance.feriasafastamento
            elif hasattr(instance, "viagem"):
                instance = instance.viagem
            elif hasattr(instance, "recesso"):
                instance = instance.recesso
            elif hasattr(instance, "folgacompensacao"):
                instance = instance.folgacompensacao
            elif hasattr(instance, "folgaeleitoral"):
                instance = instance.folgaeleitoral
            elif hasattr(instance, "folgaaniversario"):
                instance = instance.folgaaniversario
            elif hasattr(instance, "atuacaogrupotrabalho"):
                instance = instance.atuacaogrupotrabalho
            elif hasattr(instance, "desempenhofuncao"):
                instance = instance.desempenhofuncao
            elif hasattr(instance, "plantao"):
                instance = instance.plantao
            elif hasattr(instance, "bancodehoras"):
                instance = instance.bancodehoras
            elif hasattr(instance, "healthprevent"):
                instance = instance.healthprevent
        return instance

    def validate(self):
        """
        Este método deve ser sobrescrito para contemplar todas as validações da regra de negócio da movimentacao
        """
        return True

    def anotacao(self, *args, **kargs):
        return True

    def get_texto(self):
        return ""

    def apaga_anotacao(self):
        """
        Método que apaga a anotação caso ela exista.
        """
        if (
            self.anota is False
            and hasattr(self, "anotacao_geral")
            and self.anotacao_geral
        ):
            if AnotacaoGeral.objects.filter(pk=self.anotacao_geral.pk).exists():
                AnotacaoGeral.objects.get(pk=self.anotacao_geral.pk).delete()
                self.anotacao_geral = None

    @transaction.atomic
    def save(self, *args, **kwargs):
        try:
            if not self.my_type:
                self.my_type = self._meta.model_name
            # self.validate()
            super(MovimentacaoPessoal, self).save(*args, **kwargs)
            if self.anota:
                self.anotacao_alteracao()
            self.apaga_anotacao()
        except Exception as err:
            log.exception(err)
            raise err

    @transaction.atomic
    def delete(self, *args, **kargs):
        try:
            super(MovimentacaoPessoal, self).delete(*args, **kargs)
        except models.ProtectedError as err:
            log.exception(err)
            reference = ""
            for r in err.protected_objects:
                reference = " %s %s: %s" % (reference, r._meta.verbose_name, r)
            raise Exception(
                "Impossível apagar este objeto pois ele possui referência(s) de %s"
                % reference
            )
        except Exception as err:
            log.exception(err)
            raise err

    def anotacao_alteracao(self, *args, **kargs):
        try:
            if self.publicacao_alteracao:
                anotacao_geral = AnotacaoGeral.objects.get(pk=self.anotacao_geral.pk)
                anotacao_geral.texto = (
                    self.get_texto() + " " + self.get_texto_alteracao()
                )
                anotacao_geral.indireto = False
                anotacao_geral.save()
                AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
        except Exception as e:
            log.exception(e)

    def get_texto_alteracao(self):
        texto = ""
        if self.publicacao_alteracao:
            """Revoga-se através %(documento)s a partir de %(data_revogacao)s."""
            documento = (
                ("Revoga-se através do documento %s" % self.publicacao_alteracao)
                if self.publicacao_alteracao
                else ""
            )
            data_revogacao = DateUtils.date_to_str(
                self.publicacao_alteracao.data_vigencia
            )
            with codecs.open(
                "%s/revogacao_movpessoal.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {"documento": documento, "data_revogacao": data_revogacao}
        return texto

    def update_workplace_responsible_by_provision(self):
        """
        :py:function:: update_workplace_responsible_by_provision(self)

        This method updates the responsible of the workplace. When the employee assumes a job position this method
        verifies if it is responsible for a workplace.
        Avoid change responsible when there are a substitute.
        Then call workplace.update_responsible(responsible_new=employee).
        """
        workplace = None
        if (
            self.is_ativo()
            and getattr(self, "quadro", None)
            and hasattr(self, "data_desligamento")
        ):
            workplace = self.quadro.cargo.lotacao_responsavel
            date_start = self.data_exercicio
            date_end = self.data_desligamento

            if not is_active(date_start=date_start, date_end=date_end):
                workplace = None
            else:
                employee = self.servidor
                today = datetime.now().date()
                for substitution in MovimentacaoSubstituicao.objects.filter(
                    Q(servidor_substituido=employee)
                    & Q(data_inicio__lte=today)
                    & (Q(data_fim__gte=today) | Q(data_fim=None))
                ):
                    substitution = substitution.instance_model
                    if (
                        self.quadro.cargo.lotacao_responsavel
                        == substitution.workplace_job_position_responsible
                    ):
                        workplace = None
                        break
        workplace and workplace.update_responsible(responsible_new=employee)


class MovimentacaoPosseQueryset(models.QuerySet):

    def assets_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        # XXX: observar a alteção de data_desligamento__lt para data_desligamento__lte
        if range_:
            return self.exclude(
                Q(data_exercicio__gt=range_.last)
                | (~Q(data_desligamento=None) & Q(data_desligamento__lte=range_.first))
            )
        else:
            return self.exclude(
                Q(data_exercicio__gt=data)
                | (~Q(data_desligamento=None) & Q(data_desligamento__lte=data))
            )

    def with_office_valid_in(self, range_):
        # return self.filter(
        #     Q(quadro__cargo__configs__start_validity__lte=range_.last) &
        #     (
        #         Q(quadro__cargo__configs__end_validity__isnull=True) |
        #         Q(quadro__cargo__configs__end_validity__gte=range_.first)
        #     )
        # ).exclude(Q(quadro__cargo__configs__remunerated=False)).distinct()
        return (
            self.filter(
                Q(
                    Q(quadro__isnull=True, requestmove__isnull=False)
                    | Q(
                        Q(quadro__cargo__configs__start_validity__lte=range_.last)
                        & (
                            Q(quadro__cargo__configs__end_validity__isnull=True)
                            | Q(quadro__cargo__configs__end_validity__gte=range_.first)
                        )
                    )
                )
            )
            .exclude(Q(quadro__cargo__configs__remunerated=False))
            .distinct()
        )

    def by_type(self, types):
        return self.filter(quadro__cargo__tipo_lei_cargo__in=types)

    def only_original(self):
        return self.filter(
            movimentacaoreconducao=None,
            movimentacaoreintegracao=None,
            movimentacaoreversao=None,
        )


class MovimentacaoPosse(MovimentacaoPessoal):
    """
    Entidade para posse de efetivo e comissionado.
    Em relação ao SICAP PESSOAL, esta entidade atende aos arquivos de nomeção de efetivo e comissionado.
    """

    """
        NÃO HOUVE A NECESSIDADE DE ESPECIFICAR QUE TIPO DE NOMEAÇÃO É, POIS O CARGO ESPECIFICA.
    """
    quadro = models.ForeignKey(
        "Quadro", null=True, blank=True, on_delete=models.CASCADE
    )
    data_posse = models.DateField(null=True, blank=True, verbose_name="Data Posse")
    data_exercicio = models.DateField(
        null=True, blank=True, verbose_name="Data Exercício"
    )
    data_desligamento = models.DateField(
        null=True, blank=True, verbose_name="Data Desligamento"
    )
    anotacao_geral_nomeacao = models.ForeignKey(
        "AnotacaoGeral",
        blank=True,
        null=True,
        related_name="anotgeral_nomeacao",
        on_delete=models.SET_NULL,
    )
    anotacao_geral_exercicio = models.ForeignKey(
        "AnotacaoGeral",
        blank=True,
        null=True,
        related_name="anotgeral_exercicio",
        on_delete=models.SET_NULL,
    )
    ativo = models.BooleanField(default=True, blank=True)
    tipo_movcarreira = models.CharField(
        verbose_name="Provimento",
        choices=list(TIPO_MOVIMENTACAO_CARREIRA.items()),
        max_length=30,
        default="NOMEACAO",
    )
    bond = models.BooleanField(default=True, blank=True, verbose_name="Gerar vínculo")
    public_concurrence = models.ForeignKey(
        "rh.PublicConcurrence",
        on_delete=models.CASCADE,
        verbose_name="Concurso",
        null=True,
        blank=True,
        related_name="employees",
    )
    publication_possession = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="possessions_publication_possession",
        verbose_name="Publicação de Posse",
    )
    publication_exercise = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="possessions_publication_exercise",
        verbose_name="Publicação de Exercício",
    )
    judicial_decision = models.BooleanField(
        "Decorrente de decisão judicial", default=False
    )
    out_off_distribution_list = models.BooleanField(
        default=False, blank=True, verbose_name="Fora da lista de distribuição"
    )
    number_process = models.CharField(
        verbose_name="Número do Processo Judicial", max_length=20, null=True, blank=True
    )
    judicial_deposit = models.BooleanField(
        "Pagamento realizado em juízo", default=False
    )
    legal_amnesty_process = models.CharField(
        "Número e Ano Lei Anistia", max_length=13, null=True, blank=True
    )
    financial_effect_date_start = models.DateField(
        "Data do Efeito Financeiro", null=True, blank=True
    )
    financial_effect_date_end = models.DateField(
        "Data do Efeito Financeiro", null=True, blank=True
    )
    data_inicio_instancia = models.DateField(
        "Data Início na Instância", null=True, blank=True
    )
    aid_moving_house_paymente_date = models.DateField(
        "Data Autorização Pagamentos do Auxílio Mudança", null=True, blank=True
    )
    aid_moving_house_gedoc = models.CharField(
        verbose_name="GEDOC do Auxílio Mudança", max_length=20, null=True, blank=True
    )
    objects = MovimentacaoPosseQueryset.as_manager()

    ALLOWED_TYPE_BY_POSSESSION = (
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
        "CTR",
        "REQ",
        "RCM",
        "RFC",
        "BFP",
    )

    class Meta:
        verbose_name = "Movimentação de Posse"
        db_table = "rh_movposse"

    class ErroCargoComissaoEncontrado(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self,
                "%s"
                % (
                    txt
                    if txt
                    else "Este servidor já possui um Cargo em Comissão ou uma Função de Confiança."
                ),
            )

    class ErroCargoEfetivoEncontrado(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self,
                "%s" % (txt if txt else "Este servidor já possui um Cargo Efetivo."),
            )

    def __str__(self):
        description = (
            self.quadro
            if self.quadro
            else self.servidor.get_type_by_possession_display()
        )
        return f"{self.servidor} - {description}"

    @property
    def situacao_funcional(self):
        return "ATIVO"

    @property
    def tipo_carreira(self):
        return "NOMEACAO"

    @property
    def _progressoes(self):
        from rh.gfp.models import MovimentacaoProgressao

        return MovimentacaoProgressao.objects.filter(
            Q(servidor=self.servidor)
            & Q(Q(movimentacao_posse=self) | Q(movimentacao_posse__reconducoes=self))
        )

    @property
    def data_admissao(self):
        if hasattr(self, "movimentacaoreconducao"):
            return getattr(self, "movimentacaoreconducao").data_admissao
        return self.data_exercicio

    @property
    def is_reconduction(self):
        return hasattr(self, "movimentacaoreconducao")

    @property
    def is_requestmove(self):
        return hasattr(self, "requestmove") or isinstance(self, RequestMove)

    def is_collaborator(self):
        return (
            hasattr(self, "possessiontrainee")
            or hasattr(self, "possessioncollaborator")
            or isinstance(self, PossessionTrainee)
            or isinstance(self, PossessionCollaborator)
        )

    @property
    def _data_desligamento(self):
        fired = getattr(self, "desligamento", None)
        return fired.data_desligamento if fired else None

    @property
    def controller(self):
        """
        Esta propriedade retornará o primeiro controller deste modelo.
        """
        controller = get_default_controller_for_model(
            self.instancia_modelo.__class__, False
        )
        return controller.controller if controller is not None else None

    @property
    def first_possession(self):
        return MovimentacaoPosse.get_first_possession(self)

    @property
    def description_possession(self):
        my_origin = self.my_origin
        description = (
            my_origin.quadro
            if my_origin.quadro
            else my_origin.servidor.get_type_by_possession_display()
        )
        return f"{description}"

    @classmethod
    def get_first_possession(cls, possession):
        possession = possession.instancia_modelo
        if hasattr(possession, "posse_anterior"):
            possession = MovimentacaoPosse.get_first_possession(
                possession.posse_anterior
            )
        return possession

    def is_ativo(self, data=None):
        """
        Este método verifica se a posse está ativa em relação ao seu desligamento.
        Observando que no dia do desligamento o servidor não trabalhada.
        """
        data = datetime.now().date() if not data else data
        ativo = True
        if (
            self.data_desligamento
            and data >= self.data_desligamento
            or (self.data_exercicio and datetime.now().date() < self.data_exercicio)
            or (self.data_posse and datetime.now().date() < self.data_posse)
        ):
            ativo = False
        return ativo

    def is_active(self, data=None):
        return self.is_ativo()

    def validate_publicacao(self):
        if self.is_requestmove:
            if self.publicacao_movimentacao is None:
                raise self.ErroPublicacaoNaoEncontrada()
        return True

    def validate_data_vigencia(self):
        if self.publicacao_movimentacao.data_vigencia is None:
            raise Exception(
                "É necessário que Data de Vigência do Documento seja preenchido."
            )
        return True

    def validate_base_posse(self):
        query_date = Q(data_desligamento__gt=self.data_posse) | Q(
            data_desligamento=None
        )
        if self.data_exercicio:
            query_date = query_date | Q(data_desligamento__gt=self.data_exercicio)
        mov = MovimentacaoPosse.objects.filter(
            Q(servidor=self.servidor) & query_date
        ).exclude(pk=self.pk)
        if self.data_desligamento:
            mov = mov.filter(Q(data_exercicio__lt=self.data_desligamento))
        if (
            self.quadro
            and self.quadro.cargo.tipo_lei_cargo == "EF"
            and self.servidor.tipo in ("S", "M")
        ):
            mov = mov.filter(Q(quadro__cargo__tipo_lei_cargo__in=("EF", "AC")))
            if (mov.count() >= 1 and not self.pk) or (
                mov.count() >= 1 and mov.filter(pk=self.pk).count() == 0
            ):
                raise self.ErroCargoEfetivoEncontrado()
        elif self.quadro and self.quadro.cargo.tipo_lei_cargo == "CM":
            mov = mov.filter(Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC")))
            if (mov.count() >= 1 and not self.pk) or (
                mov.count() >= 1 and mov.filter(pk=self.pk).count() == 0
            ):
                raise self.ErroCargoComissaoEncontrado()
        elif self.quadro and self.quadro.cargo.tipo_lei_cargo == "FC":
            mov = mov.filter(Q(quadro__cargo__tipo_lei_cargo__in=("CM", "FC")))
            if (mov.count() >= 1 and not self.pk) or (
                mov.count() >= 1 and mov.filter(pk=self.pk).count() == 0
            ):
                raise self.ErroCargoComissaoEncontrado()
        return True

    def validate_type_by_possession(self):
        """Este método verifica se o type_by_possession é válido para o servidor.
        EFE - SERVIDOR EFETIVO *
        ECM - SERVIDOR EFETIVO E COMISSIONADO *
        EFC - SERVIDOR EFETIVO COM FUNÇÃO CONFIANÇA *
        MBR - MEMBRO *
        MEL - MEMBRO COM CARGO ELETIVO *
        MCM - MEMBRO COM CARGO COMISSIONADO *
        MEC - MEMBRO COM CARGO ELETIVO E COMISSIONADO
        MBR2 - MEMBRO *
        MEL2 - MEMBRO COM CARGO ELETIVO *
        MCM2 - MEMBRO COM CARGO COMISSIONADO *
        MEC2 - MEMBRO COM CARGO ELETIVO E COMISSIONADO
        CMS - SERVIDOR COMISSIONADO
        REQ - SERVIDOR REQUISITADO *
        RCM - SERVIDOR REQUISITADO COMISSIONADO *
        RFC - SERVIDOR REQUISITADO COM FUNÇÃO CONFIANÇA *
        CTR - SERVIDOR CONTRATADO
        EST - ESTAGIÁRIO *
        TCR - TERCEIRIZADO *
        VOL - VOLUNTÁRIO *
        JCA - JOVEM APRENDIZ *
        EXT - EXTERNO SEM VÍNVULO
        MAP - MEMBRO APOSENTADO
        SAP - SERVIDOR EFETIVO APOSENTADO
        BFP - BENEFICIÁRIO
        COE - COLABORADOR EVENTUAL"""
        if self.servidor.type_by_possession in (
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
        ):
            query_date = Q(data_desligamento__gt=self.data_posse) | Q(
                data_desligamento=None
            )
            if self.data_exercicio:
                query_date = query_date | Q(data_desligamento__gt=self.data_exercicio)
            mov = MovimentacaoPosse.objects.filter(
                Q(servidor=self.servidor) & query_date
            ).filter(quadro__cargo__tipo_lei_cargo__in=("EF", "AC"))
            if (
                self.quadro.cargo.tipo_lei_cargo not in ("EF", "AC")
                and mov.count() == 0
            ):
                raise Exception("É necessário cadastrar um cargo de efetivo.")
        if (
            self.servidor.type_by_possession == "CMS"
            and self.quadro.cargo.tipo_lei_cargo != "CM"
        ):
            raise Exception("Só é possível cadastrar: COMISSÃO.")
        if (
            self.servidor.type_by_possession in ("REQ", "RCM", "RFC")
            and self.quadro
            and self.quadro.cargo.tipo_lei_cargo not in ("CM", "FC", "AC")
        ):
            raise Exception(
                "Só é possível cadastrar: COMISSÃO, FUNÇÃO DE CONFIANÇA, OU ACORDO DE COOPERAÇÃO ."
            )
        if self.servidor.type_by_possession == "COE":
            raise Exception(
                f"Posse não permitida para: {self.get_type_by_possession_display()}."
            )
        return True

    def validate_posse_ativa(self):
        if not self.is_ativo() and not self.pk:
            raise Exception("Esta posse não está ativa.")
        return True

    def second_provision(self):
        return (
            isinstance(self, MovimentacaoPromocao)
            or isinstance(self, MovimentacaoRemocaoMembro)
            or isinstance(self, MovimentacaoTitularizacao)
        )

    def validate_desligamento_automatico_membro(self):
        """Este método realiza validações para descobrir se deve ser feito ou não o desligamento automático de membro."""
        if not self.servidor.member_type_by_possession or self.base_posse():
            return False

        if self.second_provision():
            if not self.data_exercicio:
                raise Exception("É necessário que a Data de exercício seja preenchida.")
            elif hasattr(self, "posse_anterior"):
                if self.posse_anterior.publicacao_movimentacao is None:
                    raise Exception(
                        "É necessário que a Publicação da Posse atual seja preenchida: %s"
                        % self.posse_anterior
                    )
                if self.posse_anterior.publicacao_movimentacao.data_vigencia is None:
                    raise Exception(
                        "É necessário que a Data de Vigência da Publicação de Posse atual seja preenchida: %s"
                        % self.posse_anterior
                    )
            else:
                raise Exception(
                    "É necessário que a Posse atual seja preenchida: %s"
                    % self.posse_anterior
                )
        return True

    def validate_vacancy_number_filled(self):
        # TODO: Remover validação de relativa ao type_by_possesion != EXT
        if (
            not self.pk
            and self.quadro
            and self.quadro.vacancy_number_filled() >= self.quadro.vacancy_number
            and self.servidor.type_by_possession != "EXT"
        ):
            raise Exception("A quantidade de vagas já foi preenchida.")
        return True

    def validate_if_cargo_is_empty(self):
        if not self.quadro:
            raise Exception("Por favor, preencha o campo Cargo.")

    def validate_if_data_posse_is_empty(self):
        if not self.data_posse:
            raise Exception("Por favor, preencha o campo Data Posse.")

    def validate_job_position_type(self):
        pass

    def validate_permitted_type_by_possession(self):
        if self.servidor.type_by_possession not in self.ALLOWED_TYPE_BY_POSSESSION:
            raise Exception(
                f'A "{self._meta.verbose_name}" não pode ser realizada para o servidor: {self.servidor} ({self.servidor.get_type_by_possession_display()})'
            )

    def validate_req_possession(self):
        if (
            self.base_posse()
            and self.servidor.type_by_possession in ("REQ", "RCM", "RFC")
            and self.quadro.cargo.tipo_lei_cargo not in ("CM")
            and RequestMove.objects.filter(ativo=True, servidor=self.servidor).exists()
        ):
            raise Exception(
                f"""
                O Provimento de nomeação para servidor requisitado é aplicável somente a cargos comissionados e \
                o servidor deve possuir provimento de Requisição anterior.
            """
            )

    def validate_exercise_date(self):
        if not self.data_exercicio:
            raise Exception("Por favor, preencha o campo Data Exercicio.")

    def jornada_por_tipo_posse(self):
        query = HoursWorkContract.objects.filter(
            tipo_posse__contains=self.servidor.type_by_possession, active=True
        )
        if query.exists():
            return query.first()
        else:
            raise Exception(
                f"""Não há Horário de Trabalho cadastrado para o tipo de posse {self.servidor.type_by_possession} deste Servidor!
                                Preencha o tipo de posse em um Horário de Trabalho em: Gestão de Pessoas > Folha de Ponto > Gestor de Horário de Trabalho"""
            )

    def validar_carga_horaria(self):
        """
        Ao cadastrar provimento, verifica se o servidor tem carga horária ativa, se não tiver
            cria uma nova carga horária de acordo com o padrão de tipo de posse.
        """
        if not self.pk:
            query = CargaHoraria.objects.filter(servidor=self.servidor, active=True)
            if not query.exists():
                jornada = self.jornada_por_tipo_posse()
                cg = CargaHoraria(
                    jornada_trabalho=jornada,
                    data_inicio=(
                        self.data_exercicio if self.data_exercicio else self.data_posse
                    ),
                    data_fim=self.data_desligamento,
                    servidor=self.servidor,
                    quantidade=jornada.jornada_semanal,
                )
                cg.save()

    def validate(self):
        if not isinstance(self, RequestMove):
            self.validate_if_cargo_is_empty()
            self.validate_if_data_posse_is_empty()
        self.validate_req_possession()
        self.set_tipo_movcarreira()
        self.set_active()
        self.validate_permitted_type_by_possession()
        self.validate_type_by_possession()
        self.validate_publicacao()
        # self.validate_data_vigencia()
        self.validate_exercise_date()
        self.validate_vacancy_number_filled()
        self.validar_carga_horaria()
        return True

    def full_clean(self):
        pass

    def validate_action_menu(self, label_provision=None):
        type_movement_list = {
            "MovimentacaoAproveitamento": "Aproveitamento",
            "MovimentacaoPromocao": "Promoção",
            "MovimentacaoReadaptacao": "Readaptação",
            "MovimentacaoReconducao": "Recondução",
            "MovimentacaoReintegracao": "Reintegração",
            "MovimentacaoRemocaoMembro": "Remoção",
            "MovimentacaoReversao": "Reversão",
            "MovimentacaoTitularizacao": "Titularização",
        }
        types_permitted = [
            "MBR",
            "MBR2",
            "MEL",
            "MEL2",
            "MCM",
            "MCM2",
            "MEC",
            "MEC2",
            "EFE",
            "CMS",
            "ECM",
            "EFC",
        ]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {
            "MovimentacaoPosse": "Nomeação",
        }
        types_permitted = [
            "RFC",
            "REQ",
            "RCM",
            "MBR",
            "MBR2",
            "MEL",
            "MEL2",
            "MCM",
            "MCM2",
            "MEC",
            "MEC2",
            "EFE",
            "CMS",
            "ECM",
            "EFC",
        ]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {"RequestMove": "Requisição"}
        types_permitted = ["RFC", "REQ", "RCM"]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {"BenefitMovement": "Benefício"}
        types_permitted = ["MAP", "MAP2", "SAP", "APO", "BFP"]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {"PossessionTrainee": "Estagiário"}
        types_permitted = ["EST"]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {"PossessionResident": "Residente"}
        types_permitted = ["RES"]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

        type_movement_list = {"PossessionCollaborator": "Colaborador"}
        types_permitted = ["EXT", "VOL", "TCR", "JCA"]
        if (
            self.servidor.type_by_possession not in types_permitted
            and label_provision in type_movement_list.keys()
        ):
            raise Exception(
                f"Não é permitido cadastrar {type_movement_list[label_provision]} para este Tipo de Servidor."
            )

    def set_tipo_movcarreira(self):
        if not self.pk:
            self.tipo_movcarreira = self.tipo_carreira
        return True

    def set_active(self):
        self.ativo = self.is_ativo()
        return True

    # @transaction.atomic
    def save_base_posse(self, *args, **kargs):
        """
        Este método persiste a primeira posse do servidor.
        """
        types = [
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
        ]
        if (
            self.base_posse() and self.servidor.type_by_possession in types
        ):  # quadro.cargo.tipo_lei_cargo != 'AC':
            self.validate_base_posse()
            super(MovimentacaoPosse, self).save(*args, **kargs)
            self.gera_progressao()  # Gera Progressão inicial apenas se for uma nova movimentacao de posse
            return True
        return False

    # @transaction.atomic
    # def save(self, *args, **kargs):
    #     if not self.financial_effect_date_start:
    #         self.financial_effect_date_start = self.data_exercicio
    #     try:
    #         self.set_tipo_movcarreira()
    #         self.set_active()

    #         self.validate()
    #         self.desligamento_automatico_membro()

    #         super(MovimentacaoPosse, self).save(*args, **kargs)

    #         self.gera_progressao()  # Gera Progressão inicial apenas se for uma nova movimentacao de posse

    #         if not self.anota:
    #             if self.anotacao_geral:
    #                 self.anotacao_geral.delete()
    #             if self.anotacao_geral_exercicio:
    #                 self.anotacao_geral_exercicio.delete()
    #             if self.anotacao_geral_nomeacao:
    #                 self.anotacao_geral_nomeacao.delete()
    #         ServidorLotacao.lotacao_por_provimento(self)
    #     except Exception as err:
    #         log.exception(err)
    #         raise err

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        lotacao = None
        provimento_criado = False
        movimentacao_posse = MovimentacaoPosse.objects.filter(
            servidor=self.servidor
        ).exclude(id=self.id)

        if not self.id and movimentacao_posse.exists() is False:
            provimento_criado = True
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)
        if any("lotacao" in sub for sub in args):
            lotacao = args[0]["lotacao"]
        if not self.financial_effect_date_start:
            self.financial_effect_date_start = self.data_exercicio
        try:
            self.validate()

            if self.save_base_posse() is False:
                self.desligamento_automatico_membro()
                super(MovimentacaoPosse, self).save(*args, **kargs)

            """Gera Progressão inicial apenas se for uma nova movimentacao de posse."""
            self.gera_progressao()

            if not self.anota:
                if self.anotacao_geral:
                    self.anotacao_geral.delete()
                if self.anotacao_geral_exercicio:
                    self.anotacao_geral_exercicio.delete()
                if self.anotacao_geral_nomeacao:
                    self.anotacao_geral_nomeacao.delete()
            ServidorLotacao.lotacao_por_provimento(self)

            if (
                self.servidor.type_by_possession in ["EST", "VOL", "RES"]
                and provimento_criado
            ):
                lotacao = args[0]["lotacao"]
                self.enviar_notificacao_novo_cadastro(lotacao)

        except Exception as err:
            log.exception(err)
            raise err

    def enviar_notificacao_novo_cadastro(self, lotacao):
        from common.util.send_email import EmailNotification
        from rh.pvf.signals import get_emails_approvers

        def supervisor_name():
            if hasattr(self, "employee_supervisor") and self.employee_supervisor:
                return self.employee_supervisor.pessoa_fisica.nome
            if (
                hasattr(self.servidor, "chefe_imediato")
                and self.servidor.chefe_imediato
            ):
                return self.servidor.chefe_imediato.pessoa_fisica.nome
            return "Sem supervisor"

        lotacao = Lotacao.objects.filter(id=lotacao).first()

        email_destinatario = Item.objects.get(
            configuration__application="vdf", key="notificacao_novo_cadastro"
        ).value
        lista_destinatarios = get_emails_approvers(email_destinatario)

        email_template = EmailTemplate.objects.get(code="CRIACAO_NOVO_USUARIO")
        assunto = email_template.subject
        conteudo = (
            email_template.contents.replace(
                "%tipo%", self.servidor.get_type_by_possession_display()
            )
            .replace("%nome%", self.servidor.pessoa_fisica.nome)
            .replace("%CPF%", self.servidor.pessoa_fisica.cpf)
            .replace("%matricula%", str(self.servidor.matricula))
            .replace(
                "%data_nascimento%",
                self.servidor.pessoa_fisica.data_nascimento.strftime("%d/%m/%Y"),
            )
            .replace("%RG%", self.servidor.pessoa_fisica.rg)
            .replace("%orgao%", self.servidor.pessoa_fisica.rg_orgao)
            .replace("%lotacao%", lotacao.nome if lotacao else "-")
            .replace("%supervisor%", supervisor_name())
            .replace(
                "%data_inicio%",
                (
                    self.data_exercicio.strftime("%d/%m/%Y")
                    if self.data_exercicio
                    else "-"
                ),
            )
            .replace(
                "%data_fim%",
                (
                    self.data_desligamento.strftime("%d/%m/%Y")
                    if self.data_desligamento
                    else "-"
                ),
            )
            .replace("%email_pessoal%", self.servidor.pessoa_fisica.email_pessoal or "")
            .replace(
                "%telefone_pessoal%", self.servidor.pessoa_fisica.telefone_pessoal()
            )
        )

        EmailNotification().send_email_default(lista_destinatarios, assunto, conteudo)

    @property
    def has_specialized_possession(self):
        my_type = self.get_my_type()
        return my_type in (
            "movimentacaoaproveitamento",
            "movimentacaopromocao",
            "movimentacaoremocaomembro",
            "movimentacaoreadaptacao",
            "movimentacaoreconducao",
            "movimentacaoreintegracao",
            "movimentacaoreversao",
            "movimentacaopromocao",
            "requestmove",
            "possessiontrainee",
            "possessioncollaborator",
            "movimentacaotitularizacao",
            "benefitmovement",
        )

    def base_posse(self):
        """Este método verifica se o objeto persistido é uma instância exclusivamente de MovimentacaoPosse.

        Returns:
            bool: True se for exclusivamente de MovimentacaoPosse."""
        return self.get_my_type() == "movimentacaoposse"

    def desligamento_automatico_membro(self):
        """Este método é chamado para criar desligamento automático para os métodos de provimento:
        MovimentacaoPromocao, MovimentacaoRemocaoMembro e MovimentacaoTitularizacao."""
        if self.validate_desligamento_automatico_membro():
            if (
                self.second_provision()
                and self.data_exercicio
                and hasattr(self, "posse_anterior")
            ):
                if not hasattr(self.posse_anterior, "desligamento"):
                    desligamento = MovimentacaoDesligamento(
                        publicacao_movimentacao=self.publicacao_movimentacao,
                        data_desligamento=self.data_exercicio,
                        movimentacao_posse=self.posse_anterior,
                        tipo_desligamento=12,
                        opcao=2,
                        desligamento_automatico=True,
                        anota=False,
                    )
                else:
                    desligamento = self.posse_anterior.desligamento
                    desligamento.publicacao_movimentacao = self.publicacao_movimentacao
                    desligamento.data_desligamento = self.data_exercicio
                    desligamento.desligamento_automatico = True
                desligamento.save()
            elif hasattr(self, "posse_anterior") and hasattr(
                self.posse_anterior, "desligamento"
            ):
                aposentadoria = MovimentacaoAposentadoria.objects.filter(
                    pk=self.posse_anterior.desligamento.pk
                )
                if aposentadoria.exists():
                    aposentadoria.latest("pk").save()
                else:
                    self.posse_anterior.desligamento.save()

    def _progressao_salarial(self):
        from rh.gfp.models import MovimentacaoProgressao, ReferenciaNiveis2D

        rs = ReferenciaNiveis2D.get_by_cargo(
            cargo=self.quadro.cargo, data=self.data_exercicio
        )
        mov_prog, created = MovimentacaoProgressao.objects.get_or_create(
            servidor=self.servidor,
            movimentacao_posse=self,
            referencia_nivel2d=rs,
            data_inicio_vigencia=self.data_exercicio,
            publicacao_movimentacao=self.publicacao_movimentacao,
        )
        log.info(
            "Progressão %s %s para o servidor %s"
            % (self.servidor, "criada" if created else "alterada", mov_prog)
        )

    def posse_ef(self):
        texto_nomeacao = ""
        texto_posse = ""
        texto_exercicio = ""
        nome_pessoa = self.servidor.pessoa_fisica.nome
        """SERVIDOR"""
        data_pub, veic_pub, num_pub = Publicacao.get_dados_publicacao(
            self.publicacao_movimentacao
        )
        if self.quadro.cargo.indicativo == "S":
            with codecs.open(
                "%s/nomeacao_efetivo.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_nomeacao = tpl % {
                    "nome": nome_pessoa,
                    "cargo": self.quadro,
                    "veiculo_publicacao": veic_pub,
                    "numero_publicacao": num_pub,
                    "data_publicacao": data_pub,
                }
            with codecs.open(
                "%s/posse_efetivo.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_posse = tpl % {
                    "nome": nome_pessoa,
                    "cargo": self.quadro,
                    "data_posse": DateUtils.date_to_str(self.data_posse),
                }
            if self.data_exercicio:
                with codecs.open(
                    "%s/exercicio_efetivo.txt" % templates.__path__[0], "r", "utf-8"
                ) as fd:
                    tpl = fd.read()
                    texto_exercicio = tpl % {
                        "texto_servidor": self.servidor.texto_servidor(),
                        "data": DateUtils.date_to_str(self.data_exercicio),
                        "data_exercicio": DateUtils.date_to_str(self.data_exercicio),
                        "nome": nome_pessoa,
                        "cargo": self.quadro,
                    }
        elif self.quadro.cargo.indicativo == "M":
            """MEMBRO"""
            try:
                with codecs.open(
                    "%s/nomeacao_membro.txt" % templates.__path__[0], "r", "utf-8"
                ) as fd:
                    tpl = fd.read()
                    texto_nomeacao = tpl % {
                        "nome": nome_pessoa,
                        "cargo": self.quadro,
                        "data_publicacao": data_pub,
                        "veiculo_publicacao": veic_pub,
                        "numero_publicacao": num_pub,
                    }
                with codecs.open(
                    "%s/exercicio_membro.txt" % templates.__path__[0], "r", "utf-8"
                ) as fd:
                    tpl = fd.read()
                    texto_exercicio = tpl % {
                        "nome": nome_pessoa,
                        "cargo": self.quadro,
                        "data_exercicio": DateUtils.date_to_str(
                            self.data_exercicio
                            if self.data_exercicio
                            else self.data_posse
                        ),
                    }
            except Exception as e:
                log.exception(e)
        return texto_nomeacao, texto_posse, texto_exercicio

    def posse_cm(self):
        texto_nomeacao = ""
        texto_posse = ""
        texto_exercicio = ""
        nome_pessoa = self.servidor.pessoa_fisica.nome
        mov_posse = MovimentacaoPosse.objects.filter(
            servidor=self.servidor,
            quadro__cargo__tipo_lei_cargo__exact="EF",
            ativo__exact=True,
        )
        cargo_efetivo = ""
        if len(mov_posse) > 0:
            quadro = Quadro.objects.get(pk=mov_posse[0].quadro.pk)
            cargo_efetivo = quadro
        data_pub, veic_pub, num_pub = Publicacao.get_dados_publicacao(
            self.publicacao_movimentacao
        )
        with codecs.open(
            "%s/nomeacao_comissionado.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto_nomeacao = tpl % {
                "nome": nome_pessoa,
                "texto_servidor": (
                    self.servidor.texto_servidor() if cargo_efetivo else "Sr(a)."
                ),
                "cargo_efetivo": cargo_efetivo,
                "matricula": self.servidor.matricula,
                "cargo_comissao": self.quadro,
                "data": (
                    DateUtils.date_to_str(self.publicacao_movimentacao.data_vigencia)
                    if self.publicacao_movimentacao
                    else ""
                ),
                "data_publicacao": data_pub,
                "veiculo_publicacao": veic_pub,
                "numero_publicacao": num_pub,
            }
        with codecs.open(
            "%s/posse_comissionado.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto_posse = tpl % {
                "texto_servidor": (
                    self.servidor.texto_servidor() if cargo_efetivo else "Sr(a)."
                ),
                "data_posse": DateUtils.date_to_str(self.data_posse),
                "nome": nome_pessoa,
                "cargo_comissao": self.quadro,
            }
        if self.data_exercicio:
            with codecs.open(
                "%s/exercicio_comissionado.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_exercicio = tpl % {
                    "texto_servidor": (
                        self.servidor.texto_servidor() if cargo_efetivo else "Sr(a)."
                    ),
                    "data": DateUtils.date_to_str(self.data_exercicio),
                    "nome": nome_pessoa,
                    "data_exercicio": DateUtils.date_to_str(self.data_exercicio),
                    "cargo_comissao": self.quadro,
                }
        return texto_nomeacao, texto_posse, texto_exercicio

    def posse_fc(self):
        texto_nomeacao = ""
        texto_posse = ""
        texto_exercicio = ""
        nome_pessoa = self.servidor.pessoa_fisica.nome
        mov_posse = MovimentacaoPosse.objects.filter(
            servidor=self.servidor,
            quadro__cargo__tipo_lei_cargo__exact="EF",
            ativo__exact=True,
        )
        cargo_efetivo = ""
        if len(mov_posse) > 0:
            cargo_efetivo = "".format(Quadro.objects.get(pk=mov_posse[0].quadro.pk))
        data_pub, veic_pub, num_pub = Publicacao.get_dados_publicacao(
            self.publicacao_movimentacao
        )
        with codecs.open(
            "%s/nomeacao_fc.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto_nomeacao = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "nome": nome_pessoa,
                "cargo_efetivo": cargo_efetivo,
                "matricula": self.servidor.matricula,
                "funcao": self.quadro,
                "data": (
                    DateUtils.date_to_str(self.publicacao_movimentacao.data_vigencia)
                    if self.publicacao_movimentacao
                    else ""
                ),
                "data_publicacao": data_pub,
                "veiculo_publicacao": veic_pub,
                "numero_publicacao": num_pub,
            }
        with codecs.open("%s/posse_fc.txt" % templates.__path__[0], "r", "utf-8") as fd:
            tpl = fd.read()
            texto_posse = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "data_posse": DateUtils.date_to_str(self.data_posse),
                "nome": nome_pessoa,
                "funcao": self.quadro,
            }
        if self.data_exercicio:
            with codecs.open(
                "%s/exercicio_fc.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_exercicio = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "data": DateUtils.date_to_str(self.data_exercicio),
                    "nome": nome_pessoa,
                    "data_exercicio": DateUtils.date_to_str(self.data_exercicio),
                    "funcao": self.quadro,
                }
        return texto_nomeacao, texto_posse, texto_exercicio

    def anotacao_base_posse(self):
        tipo = Publicacao.get_tipo(self.publicacao_movimentacao)
        texto_exercicio = ""
        texto_nomeacao = ""
        texto_posse = ""
        term = 6
        try:
            """POSSE EFETIVO"""
            if self.quadro.cargo.tipo_lei_cargo == "EF":
                texto_nomeacao, texto_posse, texto_exercicio = self.posse_ef()
            elif self.quadro.cargo.tipo_lei_cargo == "CM":
                """POSSE COMISSIONADO"""
                texto_nomeacao, texto_posse, texto_exercicio = self.posse_cm()
            elif self.quadro.cargo.tipo_lei_cargo == "FC":
                """POSSE FUNÇÃO DE CONFIANÇA"""
                texto_nomeacao, texto_posse, texto_exercicio = self.posse_fc()

            anotacao_geral_exercicio = None
            anotacao_geral_nomeacao = None
            anotacao_geral_posse = None
            if not self.pk:
                """CADASTRO INICIAL"""
                """NOMEAÇÃO"""
                anotacao_geral_nomeacao = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    numero_documento=(
                        (
                            self.publicacao_movimentacao.numero
                            + self.publicacao_movimentacao.ano
                        )
                        if self.publicacao_movimentacao
                        else None
                    ),
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=(
                        self.publicacao_movimentacao.data_vigencia
                        if self.publicacao_movimentacao
                        else None
                    ),
                    texto=texto_nomeacao,
                    resumo="NOMEAÇÃO",
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral_nomeacao.pk).update(
                    indireto=True
                )
                self.anotacao_geral_nomeacao = anotacao_geral_nomeacao
                """POSSE"""
                anotacao_geral_posse = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=term,
                    publicacao=self.publication_possession,
                    data_portaria_inicio=self.data_posse,
                    texto=texto_posse + " " + (self.texto if self.texto else ""),
                    resumo="POSSE",
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral_posse.pk).update(
                    indireto=True
                )
                self.anotacao_geral = anotacao_geral_posse
                """EXERCÍCIO"""
                if self.data_exercicio:
                    anotacao_geral_exercicio = AnotacaoCarreira.manage_instance(
                        servidor=self.servidor,
                        tipo_documento=term,
                        publicacao=self.publication_exercise,
                        data_portaria_inicio=self.data_exercicio,
                        texto=texto_exercicio,
                        resumo="EXERCÍCIO",
                    )
                    AnotacaoCarreira.objects.filter(
                        pk=anotacao_geral_exercicio.pk
                    ).update(indireto=True)
                    self.anotacao_geral_exercicio = anotacao_geral_exercicio
            else:
                """CADASTRO ATUALIZAÇÃO"""
                """EXERCÍCIO"""
                if self.data_exercicio:
                    if not self.anotacao_geral_exercicio:
                        anotacao_geral_exercicio = AnotacaoCarreira.manage_instance(
                            servidor=self.servidor,
                            tipo_documento=term,
                            publicacao=self.publication_exercise,
                            data_portaria_inicio=self.data_exercicio,
                            texto=texto_exercicio,
                            resumo="EXERCÍCIO",
                        )
                        self.anotacao_geral_exercicio = anotacao_geral_exercicio
                        AnotacaoCarreira.objects.filter(
                            pk=anotacao_geral_exercicio.pk
                        ).update(indireto=True)
                        self.anotacao_geral_exercicio = anotacao_geral_exercicio
                    else:
                        anotacao_geral_exercicio = AnotacaoCarreira.objects.get(
                            pk=self.anotacao_geral_exercicio.pk
                        )
                        anotacao_geral_exercicio.servidor = self.servidor
                        anotacao_geral_exercicio.tipo_documento = 6
                        anotacao_geral_exercicio.data_portaria_inicio = (
                            self.data_exercicio
                        )
                        anotacao_geral_exercicio.texto = texto_exercicio
                        anotacao_geral_exercicio.publicacao = self.publication_exercise
                        anotacao_geral_exercicio.indireto = False
                        anotacao_geral_exercicio.save()
                        AnotacaoCarreira.objects.filter(
                            pk=anotacao_geral_exercicio.pk
                        ).update(indireto=True)
                """NOMEAÇÃO"""
                document_number = (
                    (
                        self.publicacao_movimentacao.numero
                        + self.publicacao_movimentacao.ano
                    )
                    if self.publicacao_movimentacao
                    else None
                )
                document_date_start = (
                    self.publicacao_movimentacao.data_vigencia
                    if self.publicacao_movimentacao
                    else None
                )
                if self.anotacao_geral_nomeacao:
                    anotacao_geral_nomeacao = AnotacaoCarreira.objects.get(
                        pk=self.anotacao_geral_nomeacao.pk
                    )
                    anotacao_geral_nomeacao.servidor = self.servidor
                    anotacao_geral_nomeacao.tipo_documento = tipo
                    anotacao_geral_nomeacao.numero_documento = document_number
                    anotacao_geral_nomeacao.publicacao = self.publicacao_movimentacao
                    anotacao_geral_nomeacao.data_portaria_inicio = document_date_start
                    anotacao_geral_nomeacao.texto = texto_nomeacao
                    anotacao_geral_nomeacao.indireto = False
                    anotacao_geral_nomeacao.save()
                    AnotacaoCarreira.objects.filter(
                        pk=anotacao_geral_nomeacao.pk
                    ).update(indireto=True)
                else:
                    anotacao_geral_nomeacao = AnotacaoCarreira.manage_instance(
                        servidor=self.servidor,
                        tipo_documento=tipo,
                        numero_documento=document_number,
                        publicacao=self.publicacao_movimentacao,
                        data_portaria_inicio=document_date_start,
                        texto=texto_nomeacao,
                        resumo="NOMEAÇÃO",
                    )
                    AnotacaoCarreira.objects.filter(
                        pk=anotacao_geral_nomeacao.pk
                    ).update(indireto=True)
                    self.anotacao_geral_nomeacao = anotacao_geral_nomeacao
                """POSSE"""
                if self.anotacao_geral:
                    anotacao_geral_posse = AnotacaoCarreira.objects.get(
                        pk=self.anotacao_geral.pk
                    )
                    anotacao_geral_posse.servidor = self.servidor
                    anotacao_geral_posse.tipo_documento = 6
                    anotacao_geral_posse.data_portaria_inicio = self.data_posse
                    anotacao_geral_posse.texto = (
                        texto_posse + " " + (self.texto if self.texto else "")
                    )
                    anotacao_geral_posse.indireto = False
                    anotacao_geral_posse.publicacao = self.publication_possession
                    anotacao_geral_posse.save()
                    AnotacaoCarreira.objects.filter(pk=anotacao_geral_posse.pk).update(
                        indireto=True
                    )
                else:
                    anotacao_geral_posse = AnotacaoCarreira.manage_instance(
                        servidor=self.servidor,
                        tipo_documento=term,
                        publicacao=self.publication_possession,
                        data_portaria_inicio=self.data_posse,
                        texto=texto_posse + (self.texto != "-" and self.texto or "-"),
                        resumo="POSSE",
                    )
                    AnotacaoCarreira.objects.filter(pk=anotacao_geral_posse.pk).update(
                        indireto=True
                    )
                    self.anotacao_geral = anotacao_geral_posse
        except Exception as err:
            log.exception(err)
            raise Exception("Anotações de posse não criadas.")
        return True

    def gera_progressao(self):
        try:
            if self.pk and self.servidor.type_by_possession == "EFE":
                from rh.gfp.models import MovimentacaoProgressao

                mov_progressao = MovimentacaoProgressao.objects.filter(
                    servidor=self.servidor, movimentacao_posse=self
                )
                if not mov_progressao.exists():
                    self._progressao_salarial()
                else:
                    log.warning("Este servidor já possui progressão salarial.")
            else:
                log.warning("Progressão salarial não criada para membro.")
        except Exception as e:
            log.exception(e)

    def aprovado(self):
        from cesaf.concurso.models import Inscricao

        try:
            if Inscricao.objects.get(
                Q(protocolo__interessado=self.servidor.pessoa_fisica) & Q(aprovado=True)
            ):
                return True
        except Exception:
            pass
        return False

    def anotacao(self, *args, **kargs):
        if not self.quadro or self.quadro.cargo.tipo_lei_cargo == "AC":
            # XXX: Verificar a aplicação
            # if self.quadro and self.quadro.cargo.tipo_lei_cargo == 'AC':
            return None

        if self.base_posse():
            self.anotacao_base_posse()
        else:
            tipo = Publicacao.get_tipo(self.publicacao_movimentacao)

            if self.anotacao_geral is None:
                text = self._meta.verbose_name
                if hasattr(self, "get_tipo_movcarreira_display"):
                    text = self.get_tipo_movcarreira_display().upper()
                anotacao_geral = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=(
                        self.publicacao_movimentacao.data_vigencia
                        if self.publicacao_movimentacao
                        else None
                    ),
                    texto=self.get_texto() + " " + (self.texto if self.texto else ""),
                    resumo=text,
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
                self.anotacao_geral = anotacao_geral
            else:
                anotacao_geral = AnotacaoCarreira.objects.get(pk=self.anotacao_geral.pk)
                anotacao_geral.publicacao = self.publicacao_movimentacao
                anotacao_geral.data_portaria_inicio = (
                    self.publicacao_movimentacao.data_vigencia
                    if self.publicacao_movimentacao
                    else None
                )
                anotacao_geral.texto = (
                    self.get_texto() + " " + (self.texto if self.texto else "")
                )
                anotacao_geral.servidor = self.servidor
                anotacao_geral.tipo_documento = tipo
                anotacao_geral.indireto = False
                anotacao_geral.save()
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
            return anotacao_geral

    @transaction.atomic
    def delete(self, *args, **kargs):
        log.info(
            "Validar se servidor possui pelo menos um contracheque. Caso possua, não deixar apagar a posse."
        )
        if self.anotacao_geral_exercicio:
            self.anotacao_geral_exercicio.delete()
        if self.anotacao_geral_nomeacao:
            self.anotacao_geral_nomeacao.delete()
        if (
            isinstance(self, MovimentacaoPromocao)
            or isinstance(self, MovimentacaoRemocaoMembro)
            or isinstance(self, MovimentacaoTitularizacao)
        ) and hasattr(self.posse_anterior, "desligamento"):
            MovimentacaoDesligamento.objects.filter(
                pk=self.posse_anterior.desligamento.pk
            ).delete()
        super(MovimentacaoPosse, self).delete(*args, **kargs)

    @classmethod
    def cmd_atualizar_cache_ativo(cls, posse=[]):
        """
        Este método é responsável por atualizar o campo ativo baseando-se na data de vigência.
        """
        hoje = datetime.now().date()
        query = (
            Q(Q(data_desligamento__lte=hoje) & Q(ativo=True))
            | Q(data_exercicio__gte=hoje)
            | Q(data_desligamento=None)
        )
        if len(posse) > 0:
            query = Q(pk__in=posse)

        mp = None
        try:
            with transaction.atomic():
                posses = MovimentacaoPosse.objects.filter(query)
                count = 0
                total = posses.count()
                log.info("Posses pendentes %s" % total)
                for mp in posses:
                    count += 1
                    log.info("POSSE - ATUALIZANDO ESTADO %s de %s..." % (count, total))
                    mp.atualiza_cache_ativo()
        except Exception as err:
            log.exception(err)
            notify_employee(sender=mp, mensagem=err)

    def atualiza_cache_ativo(self):
        """
        Este método deve ser chamado no post_save/post_delete de MovimentacaoAposentadoria e
        MovimentacaoDesligamento para atualizar o cache ativo da MovimentacaoPosse.
        """
        message = ""
        try:
            with transaction.atomic():
                posse = self.instancia_modelo.__class__.objects.get(pk=self.pk)
                if posse.ativo != posse.is_ativo():
                    message = "%s - ACTIVE: %s para %s desligamento %s" % (
                        self,
                        boolean_unicode(posse.ativo),
                        boolean_unicode(posse.is_ativo()),
                        (
                            DateUtils.date_to_str(posse.data_desligamento)
                            if posse.data_desligamento
                            else "----"
                        ),
                    )
                    log.info(message)
                    posse.ativo = posse.is_ativo()
                    posse.save()
        except Exception as err:
            log.exception(err)
            notify_employee(sender=self, mensagem=err)

    def set_data_desligamento(self):
        """
        Este método atualiza a data de desligamento da MovimentacaoPosse a partir da MovimentacaoDesligamento.
        """
        message = "%s atualizando a data desligamento." % self
        try:
            with transaction.atomic():
                possession = self.instancia_modelo.__class__.objects.get(pk=self.pk)
                fired = getattr(possession, "desligamento", None)
                nova_data_desligamento = fired.data_desligamento if fired else None
                if possession.data_desligamento != nova_data_desligamento:
                    message = (
                        "%s: Data de desligamento: %s para %s"
                        % (
                            possession,
                            (
                                DateUtils.date_to_str(possession.data_desligamento)
                                if possession.data_desligamento
                                else "----"
                            ),
                            (
                                DateUtils.date_to_str(nova_data_desligamento)
                                if fired
                                else "----"
                            ),
                        )
                    ).upper()
                    log.info(message)
                    possession.data_desligamento = nova_data_desligamento
                    financial_end_date = nova_data_desligamento
                    if financial_end_date is not None:
                        financial_end_date -= timedelta(days=1)
                    possession.financial_effect_date_end = financial_end_date
                    possession.save()
        except Exception as err:
            log.exception(err)


class MovimentacaoDesligamento(MovimentacaoPessoal):
    movimentacao_posse = models.OneToOneField(
        "MovimentacaoPosse", related_name="desligamento", on_delete=models.CASCADE
    )
    tipo_desligamento = models.IntegerField(
        verbose_name="Tipo de Desligamento",
        default=1,
        choices=Choice.get_choices_for("rh", "TYPE_FIRED"),
    )
    opcao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_FIRED_DOC"),
        default=2,
        blank=True,
        verbose_name="Opção",
    )
    data_desligamento = models.DateField(null=True, blank=True)
    vacancia = models.BooleanField(default=False, verbose_name="Vacância")
    termination_process = models.BooleanField(
        default=True, verbose_name="Finaliza férias, afastamentos e lotação"
    )
    desligamento_automatico = models.BooleanField(
        default=False, verbose_name="Desligamento Automático"
    )

    class Meta:
        verbose_name = "Movimentação de Desligamento"
        db_table = "rh_movdesligamento"

    def __str__(self):
        return f"Desligamento: {self.servidor} - {self.movimentacao_posse.description_possession} - {DateUtils.date_to_str(self.data_desligamento)}"

    @property
    def situacao_funcional(self):
        situacao = "INATIVO_EXONERADO_OFICIO"
        tipo = 0
        try:
            tipo = int(self.tipo_desligamento)
        except Exception:
            pass
        if tipo in (1, 2, 3, 12):
            situacao = (
                "INATIVO_EXONERADO_PEDIDO"
                if self.opcao == 1
                else "INATIVO_EXONERADO_OFICIO"
            )
        elif tipo == 4:
            situacao = "INATIVO_APO_INVALIDEZ"
        elif tipo == 5:
            situacao = "INATIVO_APO_VOLUNTARIO"
        elif tipo == 6:
            situacao = "INATIVO_OUTRO_CARGO"
        elif tipo == 7:
            situacao = "INATIVO_FALECIDO"
        elif tipo in (8, 9):
            situacao = "INATIVO_DEMITIDO"
        elif tipo == 13:
            situacao = "INATIVO_DEVOLVIDO"
        elif tipo == 14:
            situacao = "INATIVO_APO_COMPULSORIO"
        elif tipo == 15:
            situacao = "INATIVO_APO_ESPECIAL"
        elif tipo == 16:
            situacao = "INATIVO_APO_TEMPO_CONTRIBUICAO"
        elif tipo == 17:
            situacao = "INATIVO_APO_IDADE"
        elif tipo == 21:
            situacao = "INATIVO_TSVE"
        elif tipo == 24:
            situacao = "INATIVO_BENEFICIO"
        return situacao

    def validate(self):
        opcao = 0
        try:
            opcao = int(self.opcao)
        except Exception:
            pass
        self.validate_type_not_allowed()
        self.validate_publicacao_posse()
        self.validate_date_exercise()
        self.validate_date_shutdown()
        self.validate_possession_before_turn_off()
        self.validate_publicacao()
        self.validate_date_exercise_lt_fired()
        self.validate_type_shutdown_by_office()
        if self.pk and not self.servidor.member_type_by_possession:
            if (
                MovimentacaoDesligamento.objects.get(pk=self.pk).movimentacao_posse
                != self.movimentacao_posse
            ):
                raise Exception("Não é possível modificar a posse neste desligamento.")
        if opcao == 1 and self.data_desligamento is None:
            raise Exception("É necessário que Data de Desligamento seja preenchida.")
        if (
            self.movimentacao_posse.quadro
            and self.movimentacao_posse.quadro.cargo.tipo_lei_cargo == "EF"
            and MovimentacaoPosse.objects.filter(
                servidor=self.servidor, ativo=True, quadro__cargo__tipo_lei_cargo="FC"
            ).exists()
        ):
            raise Exception(
                "Para realizar este procedimento é necessário desligar do cargo em comissão ou da função."
            )
        return super(MovimentacaoDesligamento, self).validate()

    def validate_type_not_allowed(self):
        if not self.pk and self.tipo_desligamento in [3, 5, 8, 10, 11, 15]:
            raise Exception(
                "Não é permitido novos cadastros com a opção %s"
                % self.get_tipo_desligamento_display()
            )

    def validate_possession_before_turn_off(self):
        if self.movimentacao_posse.data_exercicio > self.data_desligamento:
            raise Exception(
                "A data de desligamento não pode ser anterior à data de exercício."
            )
        return True

    def validate_date_exercise(self):
        if not self.movimentacao_posse.data_exercicio:
            raise Exception(
                "Não é possível realizar o desligamento sem o preenchimento da Data de Exercício!"
            )

    def validate_date_shutdown(self):
        if not self.data_desligamento:
            raise Exception(
                "Não é possível realizar o desligamento sem o preenchimento da Data de Desligamento!"
            )

    def validate_date_exercise_lt_fired(self):
        if self.movimentacao_posse.data_exercicio > self.data_desligamento:
            raise Exception(
                "A data de desligamento não pode ser anterior à data de exercício."
            )

    def validate_publicacao(self):
        if not (
            self.movimentacao_posse.is_requestmove
            or self.movimentacao_posse.is_collaborator
        ):
            if (
                self.publicacao_movimentacao is None
                or self.publicacao_movimentacao.data_vigencia is None
            ):
                raise Exception(
                    "É necessário que Data de Vigência do Documento de Desligamento seja preenchido."
                )
        return True

    def validate_publicacao_posse(self):
        if not (
            self.movimentacao_posse.is_requestmove
            or self.movimentacao_posse.is_collaborator
        ):
            if self.movimentacao_posse.publicacao_movimentacao is None:
                raise Exception(
                    "É necessário que a Publicação da Posse seja preenchida."
                )
            if self.movimentacao_posse.publicacao_movimentacao.data_vigencia is None:
                raise Exception(
                    "É necessário que a Data de Vigência da Publicação de Posse seja preenchida."
                )
        return True

    def validate_type_shutdown_by_office(self):
        if (
            self.tipo_desligamento == 1
            and self.movimentacao_posse.quadro.cargo.tipo_lei_cargo == "CM"
        ) or (
            self.tipo_desligamento == 2
            and self.movimentacao_posse.quadro.cargo.tipo_lei_cargo == "EF"
        ):
            raise Exception("Tipo Desligamento inválido para este Tipo Cargo.")

    def texto_efetivo(self, *args, **kargs):
        if self.vacancia:
            """DECLARAR, a partir de %(data_portaria)s pela Portaria %(portaria_exoneracao)s, vacância em decorrência de
            %(tipo_desligamento)s %(tipo)s, o(a) %(texto_servidor)s %(nome)s, matrícula nº %(matricula)s,
            do Cargo de %(cargo_efetivo)s, para o qual fora nomeado(a) pela Portaria n° %(portaria)s,
            nos termos do artigo 32, da Lei 1.818/2007."""
            with codecs.open(
                "%s/exonerar_efetivo_vacancia.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "tipo": kargs.get("tipo_nome"),
                    "nome": kargs.get("nome_pessoa"),
                    "matricula": kargs.get("matricula"),
                    "cargo_efetivo": self.movimentacao_posse.quadro,
                    "portaria_exoneracao": kargs.get("portaria_exoneracao"),
                    "tipo_desligamento": kargs.get("tipo_desligamento"),
                    "data_portaria": kargs.get("data_portaria_desligamento"),
                    "data_desligamento": kargs.get("data_desligamento"),
                }
        else:
            with codecs.open(
                "%s/exonerar_efetivo.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "texto_servidor": self.servidor.texto_servidor(),
                    "tipo": kargs.get("tipo_nome"),
                    "nome": kargs.get("nome_pessoa"),
                    "matricula": kargs.get("matricula"),
                    "cargo_efetivo": self.movimentacao_posse.quadro,
                    "portaria": kargs.get("portaria"),
                    "data_portaria": kargs.get("data_portaria_nomeacao"),
                    "data_desligamento": kargs.get("data_desligamento"),
                }
        return texto

    def texto_comissao(self, *args, **kargs):
        mov_posse = MovimentacaoPosse.objects.filter(
            servidor=self.servidor,
            quadro__cargo__tipo_lei_cargo__exact="EF",
            data_posse__lte=self.movimentacao_posse.data_posse,
        )
        cargo_efetivo = ""
        if len(mov_posse) > 0:
            quadro = Quadro.objects.get(pk=mov_posse[0].quadro.pk)
            cargo_efetivo = quadro
        with codecs.open(
            "%s/exonerar_comissionado.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "nome": kargs.get("nome_pessoa"),
                "cargo_efetivo": cargo_efetivo,
                "matricula": kargs.get("matricula"),
                "tipo": kargs.get("tipo_nome"),
                "cargo_comissionado": self.movimentacao_posse.quadro,
                "portaria": kargs.get("portaria"),
                "data_portaria": kargs.get("data_portaria_nomeacao"),
                "data_desligamento": kargs.get("data_desligamento"),
            }
        return texto

    def base_text(self, *args, **kargs):
        job_position = self.movimentacao_posse.description_possession

        msg = Message.objects.get(mid="RH_ANNOTATION_FIRE")
        text = msg.formated(
            {
                "type_of": self.get_tipo_desligamento_display().upper(),
                "employee_text": self.servidor.texto_servidor(),
                "name": f"{self.servidor.pessoa_fisica}",
                "registry": f"{self.servidor.matricula}",
                "job_position": f"{job_position}",
                "termination_date": DateUtils.date_to_str(self.data_desligamento),
            }
        )
        return text

    def anotacao(self, *args, **kargs):
        try:
            texto_exoneracao = ""
            data_portaria_nomeacao = ""
            data_portaria_desligamento = ""
            possession_number_year = ""
            fired_number_year = ""

            possession = self.movimentacao_posse

            tipo_desligamento = self.get_tipo_desligamento_display()
            tipo = Publicacao.get_tipo(self.publicacao_movimentacao)
            tipo_nome = "a pedido," if self.opcao == 1 else ""
            data_desligamento = DateUtils.date_to_str(self.data_desligamento)
            fired_date_start = (
                self.publicacao_movimentacao.data_vigencia
                if self.publicacao_movimentacao
                else None
            )
            nome_pessoa = possession.servidor.pessoa_fisica.nome

            fired_type = f"{self.get_tipo_desligamento_display()}"

            if possession.publicacao_movimentacao:
                data_portaria_nomeacao = DateUtils.date_to_str(
                    possession.publicacao_movimentacao.data_vigencia
                )
                possession_number_year = "%s/%s" % (
                    possession.publicacao_movimentacao.numero,
                    possession.publicacao_movimentacao.ano,
                )

            if self.publicacao_movimentacao:
                if self.publicacao_movimentacao.data_vigencia is None:
                    data_portaria_desligamento = data_desligamento
                else:
                    data_portaria_desligamento = DateUtils.date_to_str(
                        self.publicacao_movimentacao.data_vigencia
                    )

                fired_number_year = "%s/%s" % (
                    self.publicacao_movimentacao.numero,
                    self.publicacao_movimentacao.ano,
                )

            if possession.quadro and possession.quadro.cargo.tipo_lei_cargo == "EF":
                fired_type = "EXONERAR"
                texto_exoneracao = self.texto_efetivo(
                    matricula=possession.servidor.matricula,
                    portaria=possession_number_year,
                    portaria_exoneracao=fired_number_year,
                    tipo_nome=tipo_nome,
                    tipo_desligamento=tipo_desligamento,
                    data_desligamento=data_desligamento,
                    data_portaria_nomeacao=data_portaria_nomeacao,
                    data_portaria_desligamento=data_portaria_desligamento,
                    nome_pessoa=nome_pessoa,
                )
            elif possession.quadro and possession.quadro.cargo.tipo_lei_cargo in (
                "CM",
                "FC",
            ):
                fired_type = "EXONERAR"
                texto_exoneracao = self.texto_comissao(
                    matricula=possession.servidor.matricula,
                    portaria=possession_number_year,
                    tipo_nome=tipo_nome,
                    data_desligamento=data_desligamento,
                    data_portaria_nomeacao=data_portaria_nomeacao,
                    nome_pessoa=nome_pessoa,
                )
            else:
                texto_exoneracao = self.base_text(
                    matricula=possession.servidor.matricula,
                    portaria=possession_number_year,
                    tipo_nome=tipo_nome,
                    data_desligamento=data_desligamento,
                    data_portaria_nomeacao=data_portaria_nomeacao,
                    nome_pessoa=nome_pessoa,
                )

            if hasattr(self, "movimentacaoaposentadoria"):
                fired_type = "APOSENTAR"

            if hasattr(self, "terminationbenefitmovement"):
                fired_type = "ENCERRAR BENEFÍCIO"

            if self.anotacao_geral is None:
                anotacao_geral = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    numero_documento=fired_number_year,
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=fired_date_start,
                    texto=texto_exoneracao + (self.texto if self.texto else ""),
                    resumo=fired_type,
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
                self.anotacao_geral = anotacao_geral
            else:
                anotacao_geral = AnotacaoCarreira.objects.get(pk=self.anotacao_geral.pk)
                anotacao_geral.servidor = self.servidor
                anotacao_geral.tipo_documento = tipo
                anotacao_geral.numero_documento = fired_number_year
                anotacao_geral.publicacao = self.publicacao_movimentacao
                anotacao_geral.data_portaria_inicio = fired_date_start
                anotacao_geral.texto = texto_exoneracao + (
                    self.texto if self.texto else ""
                )
                anotacao_geral.indireto = False
                anotacao_geral.resumo = fired_type
                anotacao_geral.save()
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
        except Exception as err:
            log.exception(err)
            raise Exception("Anotações de desligamento não criadas.")
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        from rh.utils import atualizar_data_fim_carga_horaria

        self.servidor = self.movimentacao_posse.servidor
        super(MovimentacaoDesligamento, self).save(*args, **kargs)
        self.verificar_desligamento_atrasado()

        log.info(
            """
            colocar validação para não permitir cadastro de desligamento com as opções de aposentadoria
            [4, 5, 14, 15, 16, 17]
        """
        )
        if self.tipo_desligamento not in [6, 12, 18, 19, 20, 23]:
            # Não gerar Data Fim para a Contribuição Previdenciária quando o
            # Tipo de Desligamento for PROMOÇÃO/REMOÇÃO, REDISTRIBUIÇÃO, REVERSÃO,
            # FIM DE MANDATO, POSSE EM OUTRO CARGO e REVISÃO DE BENEFÍCIO
            SocialSecurityEmployee.finish_social_security_for_employee(
                self.servidor, self.data_desligamento
            )

        if not self.servidor.type_by_possession in TIPO_POSSE["membros"]:
            atualizar_data_fim_carga_horaria(self.servidor, self.data_desligamento)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        from rh.utils import remover_data_fim_carga_horaria

        servidor = self.servidor

        try:
            super(MovimentacaoPessoal, self).delete(*args, **kwargs)
        except models.ProtectedError as err:
            reference = ""
            for r in err.protected_objects:
                reference += " %s %s: %s" % (r._meta.verbose_name, r, "")
            raise Exception(
                "Impossível apagar este objeto pois ele possui referência(s) de %s"
                % reference
            )
        except Exception as err:
            raise err

        remover_data_fim_carga_horaria(servidor)

    def verificar_desligamento_atrasado(self):
        if self.servidor.type_by_possession in ["RES", "EST", "VOL"]:
            hoje = date.today()
            if self.data_desligamento <= hoje:
                # Envia notificação de desligamento para o suporte e apara os emails configurados
                enviar_email_notificacao_desligamento_res_vol_est(self.servidor)

                # altera a data de fim da vigencia da lotacao e da designação ativas  para a data de desligamento  do provimento e as desativas
                self.servidor.servidor_lotacao.filter(ativo=True).update(
                    ativo=False, data_vigencia_fim=self.data_desligamento
                )

    def termination_trainee_acq_periods(self, demission_date: datetime.date):
        """
        Função que altera a data fim último periodo aquisitivo ABERTO com a data fim do descredenciamento do estagiário,
        em desligamentos manuais ou automaticos do estagiário.

        :param datetime.date demission_date: Data de Descrendeciamento
        """
        from rh.dayoff.const import ACQP_PROGRESS, ACQP_WAIT
        from rh.dayoff.models import AcquisitionPeriod, AcquisitionPeriodAttachment
        from dateutil import relativedelta

        acq_per = (
            AcquisitionPeriod.objects.filter(
                employee=self.servidor, status__in=[ACQP_WAIT, ACQP_PROGRESS]
            )
            .order_by("-start_date_acquisition")
            .first()
        )

        if demission_date < acq_per.end_date_acquisition:
            delta = relativedelta.relativedelta(
                demission_date, acq_per.start_date_acquisition
            )
            months = (delta.years * 12) + delta.months
            enjoyment_days = (months * 2.5) + ((delta.days / 30) * 2.5)
            enjoyment_days_rounded = round(enjoyment_days + 0.5)

            acq_per.end_date_acquisition = demission_date
            acq_per.days = enjoyment_days_rounded

            attachment = AcquisitionPeriodAttachment.objects.filter(
                acquisition_period=acq_per
            ).first()
            attachment.date_end = demission_date
            attachment.days_law = enjoyment_days_rounded

            acq_per.save_base()
            attachment.save()

    def termination_resident_acq_periods(self, demission_date: datetime.date):
        """
        Função que altera a data fim último periodo aquisitivo ABERTO com a data fim do descredenciamento do residente,
        em desligamentos manuais ou automaticos do residente.

        :param datetime.date demission_date: Data de Descrendeciamento
        """
        from rh.dayoff.const import ACQP_PROGRESS, ACQP_WAIT
        from rh.dayoff.models import AcquisitionPeriod, AcquisitionPeriodAttachment
        from dateutil import relativedelta

        acq_per = (
            AcquisitionPeriod.objects.filter(
                employee=self.servidor, status__in=[ACQP_WAIT, ACQP_PROGRESS]
            )
            .order_by("-start_date_acquisition")
            .first()
        )

        if demission_date < acq_per.end_date_acquisition:
            delta = relativedelta.relativedelta(
                demission_date, acq_per.start_date_acquisition
            )
            months = (delta.years * 12) + delta.months
            enjoyment_days = (months * 2.5) + ((delta.days / 30) * 2.5)
            enjoyment_days_rounded = round(enjoyment_days + 0.5)

            acq_per.end_date_acquisition = demission_date
            acq_per.days = enjoyment_days_rounded

            attachment = AcquisitionPeriodAttachment.objects.filter(
                acquisition_period=acq_per
            ).first()
            attachment.date_end = demission_date
            attachment.days_law = enjoyment_days_rounded

            acq_per.save_base()
            attachment.save()

    def run_termination_process(self):
        """Este método chama todos os procedimentos que devem ser realizados quando
        ocorrer um desligamento com termination_process true."""
        log = getLogger("db")
        try:
            ServidorLotacao.finish_workplace_from_fire(self)
        except Exception as err:
            log.exception(err)

        def change_vacation():
            try:
                from rh.ferias.models import AlteracaoPASU

                AlteracaoPASU.change_vacation_by_fire(
                    get_current_user(),
                    self,
                    self.servidor,
                    self.data_desligamento,
                    self,
                    self.publicacao_movimentacao,
                )
            except Exception as err:
                log.exception(err)
                print(err)

        def interrupt_departures():
            from rh.afastamento.models import BaseLicencaAfastamento

            try:
                if not self.desligamento_automatico:
                    BaseLicencaAfastamento.interrupt(
                        self.servidor,
                        self.data_desligamento,
                        self.publicacao_movimentacao,
                    )
            except Exception as err:
                log.exception(err)
                print(err)

        def resignation_move_do():
            from rh.gfp.models import MovimentacaoProgressao

            try:
                MovimentacaoProgressao.finish_progression_by_fire(self)
            except Exception as err:
                log.exception(err)
                print(err)

        def interrupt_or_change_vacation():
            from rh.dayoff.models import AcquisitionPeriod, Activity, Usufruct

            try:
                if not self.desligamento_automatico:
                    Activity.cancel_if_changing_status_on_turnoff(self.servidor)
                    AcquisitionPeriod.change_homologated_autorized_to_opportune_time(
                        self.servidor
                    )
                    Usufruct.interrupt_if_enjoying_on_turnoff(self.servidor)
            except Exception as err:
                log.exception(err)
                print(err)

        today = datetime.now().date()
        if (
            self.termination_process
            and self.data_desligamento <= today
            and not self.servidor.is_ativo()
            and self.servidor.type_by_possession
            not in ("EST", "TCR", "VOL", "EXT", "JCA")
        ):
            change_vacation()
            interrupt_departures()
            interrupt_or_change_vacation()
        if (
            self.termination_process
            and not self.servidor.member_type_by_possession
            and not self.servidor.is_ativo()
            and self.servidor.type_by_possession in ("EST",)
        ):
            self.termination_trainee_acq_periods(self.data_desligamento)

        resignation_move_do()

    @classmethod
    def cmd_termination_process(cls, fired=[]):
        log = getLogger("db")
        """Este método é responsável por chamar a execução de run_termination_process de cada desligamento."""
        today = datetime.now().date()
        query = Q(data_desligamento=today)
        if len(fired) > 0:
            query = Q(pk__in=fired)

        query = MovimentacaoDesligamento.objects.filter(query)
        total = query.count()
        count = 0
        log.info(
            "Processo de finalização de lotação, exercício, afastamentos e férias. Total: total"
        )
        for md in query:
            count += 1
            log.info(f"{count} de {total} -> {md}")
            md.run_termination_process()


class PeriodoRequisicao(AuditTimestampModel):
    requisicao = models.ForeignKey(
        "MovimentacaoRequisicao",
        null=True,
        blank=True,
        related_name="periodo",
        on_delete=models.SET_NULL,
    )
    request_move = models.ForeignKey(
        "RequestMove", related_name="periods", null=True, on_delete=models.SET_NULL
    )
    data_inicio = models.DateField(blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    publicacao = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        related_name="periodo_requisicao",
        verbose_name="Publicação",
        on_delete=models.PROTECT,
    )
    anotacao_geral = models.ForeignKey(
        "AnotacaoGeral",
        blank=True,
        null=True,
        related_name="periodo_requisicao",
        verbose_name="Anotação Geral",
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Período de requisição"
        ordering = ["data_inicio"]

    def __str__(self):
        return "Início: %s Fim: %s - %s%s" % (
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "",
            self.publicacao.numero if self.publicacao else "",
            self.publicacao.data_expedicao.year if self.publicacao else "",
        )

    def validate_continuous_perios(self):
        if self.request_move:
            periods = PeriodoRequisicao.objects.filter(
                request_move__pk=self.request_move.pk
            )
            if periods.exists():
                start_date = periods.aggregate(data_inicio=Min("data_inicio"))[
                    "data_inicio"
                ]
                end_date = periods.aggregate(data_fim=Max("data_fim"))["data_fim"]
                dr_general = NewDateRange(start_date, end_date)
                dr_periods = NewDateRange()
                for periods in PeriodoRequisicao.objects.filter(
                    request_move__pk=self.request_move.pk
                ).order_by("data_inicio"):
                    dr_periods += NewDateRange(periods.data_inicio, periods.data_fim)
                if dr_general.days != dr_periods.days:
                    raise Exception(
                        "Período não é contínuo. Para períodos não contínuos uma nova requisição deve ser criada."
                    )

    def validate(self):
        self.validate_continuous_perios()
        if self.publicacao is None or self.publicacao.data_vigencia is None:
            raise Exception(
                "É necessário que Data de Vigência da Publicação seja preenchida."
            )
        return True

    def save(self, *args, **kargs):
        self.validate()
        self.anotacao()
        if self.request_move:
            pass
        super(PeriodoRequisicao, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        if self.anotacao_geral:
            self.anotacao_geral.delete()
        super(PeriodoRequisicao, self).delete(*args, **kargs)

    def anotacao(self):
        try:
            if self.request_move:
                tipo = 3
                if self.publicacao.tipo == 4:
                    tipo = 3
                elif self.publicacao.tipo == 7:
                    tipo = 5

                texto_requisicao = ""
                with codecs.open(
                    "%s/requisicao.txt" % templates.__path__[0], "r", "utf-8"
                ) as fd:
                    tpl = fd.read()
                    texto_requisicao = tpl % {
                        "texto_servidor": self.request_move.servidor.texto_servidor(),
                        "nome": self.request_move.servidor,
                        "orgao_origem": self.request_move.organ_origin,
                        "onus": "sem" if self.request_move.onus == 1 else "com",
                        "inicio": (
                            DateUtils.date_to_str(self.data_inicio)
                            if self.data_inicio
                            else "início não cadastrado"
                        ),
                        "fim": (
                            DateUtils.date_to_str(self.data_fim)
                            if self.data_fim
                            else "fim não cadastrado"
                        ),
                    }

                if self.anotacao_geral is None:
                    anotacao_geral = AnotacaoGeral.manage_instance(
                        servidor=self.request_move.servidor,
                        tipo_documento=tipo,
                        numero_documento=self.publicacao.numero + self.publicacao.ano,
                        publicacao=self.publicacao,
                        data_portaria_inicio=self.data_inicio,
                        texto=texto_requisicao + self.request_move.texto,
                        resumo="REQUISIÇÃO",
                    )
                    AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(
                        indireto=True
                    )
                    self.anotacao_geral = anotacao_geral
                    self.save()
                else:
                    anotacao_geral = AnotacaoGeral.objects.get(
                        pk=self.anotacao_geral.pk
                    )
                    anotacao_geral.servidor = self.request_move.servidor
                    anotacao_geral.tipo_documento = tipo
                    anotacao_geral.numero_documento = (
                        self.publicacao.numero + self.publicacao.ano
                    )
                    anotacao_geral.publicacao = self.publicacao
                    anotacao_geral.data_portaria_inicio = self.publicacao.data_vigencia
                    anotacao_geral.texto = texto_requisicao + self.request_move.texto
                    anotacao_geral.indireto = False
                    anotacao_geral.save()
                    AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(
                        indireto=True
                    )
        except (
            RequestMove.DoesNotExist,
            PeriodoRequisicao.DoesNotExist,
            Servidor.DoesNotExist,
        ) as err:
            log.exception(err)
        except Exception as err:
            log.exception(err)
            log.warning("Não gerou/atualizou anotação de requisição.")


class FinancialBurdenQueryset(models.QuerySet):
    def of_possession(self, possession):
        return self.filter(request_move=possession)

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio__gt=range_.last)
                | (~Q(data_fim=None) & Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio__gt=data) | (~Q(data_fim=None) & Q(data_fim__lt=data))
            )


@auditable("data_fim", "data_fim")
class EncargoFinanceiro(AuditTimestampModel):
    requisicao = models.ForeignKey(
        "MovimentacaoRequisicao",
        related_name="encargos_financeiros",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    request_move = models.ForeignKey(
        "RequestMove",
        related_name="encargos_financeiros",
        null=True,
        on_delete=models.SET_NULL,
    )
    remuneracao = models.DecimalField(default=0, max_digits=16, decimal_places=2)
    base_previdenciaria = models.DecimalField(
        default=0, max_digits=16, decimal_places=2
    )
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")

    objects = FinancialBurdenQueryset.as_manager()

    class Meta:
        verbose_name = "Encargo Financeiro"
        ordering = ["data_inicio"]

    def __str__(self):
        return "Início: %s Fim: %s" % (
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "",
        )

    def validate(self):
        if (
            EncargoFinanceiro.objects.filter(request_move=self.request_move)
            .filter(Q(data_fim=None) | Q(data_fim__gte=self.data_inicio))
            .exclude(pk=self.pk)
            .exists()
        ):
            raise Exception(
                "Por favor, finalize um Encargo Financeiro antes de cadastrar um novo."
            )
        return True

    def save(self, *args, **kargs):
        self.validate()
        if (
            self.request_move
            and not self.data_fim
            and self.request_move.periods.last().data_fim
        ):
            self.data_fim = self.request_move.periods.last().data_fim
        super(EncargoFinanceiro, self).save(*args, **kargs)


class MovimentacaoRequisicaoQueryset(models.QuerySet):
    def of_possession(self, possession):
        return self.filter(posse_origem=possession)

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio__gt=range_.last)
                | (~Q(data_fim=None) & Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio__gt=data) | (~Q(data_fim=None) & Q(data_fim__lt=data))
            )


class MovimentacaoRequisicao(MovimentacaoPessoal):
    orgao_origem = models.ForeignKey(
        "UnidadeAdministrativa",
        related_name="requisicao_origem",
        blank=True,
        on_delete=models.PROTECT,
    )
    posse_origem = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=True,
        related_name="requisicao",
        on_delete=models.PROTECT,
    )
    onus = models.IntegerField(default=2, choices=TIPO_ONUS, verbose_name="Ônus")
    ativo = models.BooleanField(default=True)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    category = models.IntegerField(
        default=301,
        verbose_name="Categoria eSocial origem",
        choices=Choice.get_choices_for("rh", "CATEGORY_WORKER"),
    )

    objects = MovimentacaoRequisicaoQueryset.as_manager()

    class Meta:
        verbose_name = "Movimentação de Requisição"
        db_table = "rh_movrequisicao"

    class ErroCargoACNaoEncontrado(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self,
                "%s"
                % (
                    txt
                    if txt
                    else "Erro no tipo do cargo. Para posse de origem só é permitido o tipo de cargo AC."
                ),
            )

    def __str__(self):
        return "ORIGEM: %s - ÔNUS: %s" % (
            self.orgao_origem,
            "ORIGEM" if self.onus == 1 else "REQUISITANTE",
        )

    def validate(self):
        self.verifica_requisicao_ativa()
        if self.posse_origem.quadro.cargo.tipo_lei_cargo != "AC":
            raise self.ErroCargoACNaoEncontrado()
        if (
            self.orgao_origem is None
            and self.posse_origem.quadro.cargo.unidade_administrativa is None
        ):
            raise Exception("O órgão de origem é obrigatório.")
        return super(MovimentacaoRequisicao, self).validate()

    def verifica_requisicao_ativa(self):
        """
        Este método verifica se existe uma requisição ativa. Não permite
        que nada seja alterado caso exista.
        """
        quantidade_requisicao_ativa = self.existe_outra_requisicao_ativa(
            self.posse_origem, self.data_inicio
        )
        if (
            quantidade_requisicao_ativa.count() == 1
            and not {"pk": self.pk} in quantidade_requisicao_ativa
        ) or quantidade_requisicao_ativa.count() > 1:
            raise Exception("Existe uma requisição ativa para esta posse de origem.")

    @transaction.atomic
    def save(self, *args, **kargs):
        self.servidor = self.posse_origem.servidor
        self.orgao_origem = self.posse_origem.quadro.cargo.unidade_administrativa
        super(MovimentacaoRequisicao, self).save(*args, **kargs)

    @classmethod
    def execute(cls):
        """
        Este método é o responsável por invocar os métodos que criam e
        removem desligamento.
        """
        pass

    @classmethod
    def filtro_periodo_nao_vigente(cls):
        """
        Este método retorna um filtro para encontrar requisições que não estejam
        vigentes.
        """
        return Q(periodo__data_fim__lte=datetime.now())

    @classmethod
    def filtro_periodo_vigente(cls):
        """
        Este método retorna um filtro de vigência da requisição.
        """
        return Q(periodo__data_fim__gte=datetime.now()) | Q(periodo__data_fim=None)

    @classmethod
    def filtro_periodo_nao_vigente_sem_vigentes(cls):
        """
        Este método retorna um filtro para encontrar requisições que não estejam
        vigentes sem as que possuírem períodos vigentes.
        """
        return cls.filtro_periodo_nao_vigente() & ~cls.filtro_periodo_vigente()

    @classmethod
    def requisicao_finalizada_sem_desligamento(cls):
        """
        Este método retorna todas as requisições que:
            -possuem posse em cargo AC;
            -foram finalizadas(ou não possuem período cadastrado);
            -não possuem desligamento;
            -que não sejam ativas e possuam outras requisições com a mesma
            posse de origem.
        """
        q = Q(posse_origem__quadro__cargo__tipo_lei_cargo="AC") & Q(
            cls.filtro_periodo_nao_vigente_sem_vigentes()
            | Q(
                pk__in=MovimentacaoRequisicao.objects.filter()
                .exclude(~Q(periodo=None))
                .values("pk")
            )
        )
        return MovimentacaoRequisicao.objects.filter(q).exclude(
            Q(
                posse_origem__in=MovimentacaoRequisicao.objects.filter(
                    cls.filtro_periodo_vigente()
                ).values("posse_origem")
            )
            | Q(~Q(posse_origem__desligamento=None) & Q(ativo=False))
        )

    @classmethod
    def verifica_desligamento_com_requisicao_vigente(cls):
        """
        Este método retorna todos desligamentos que devem ser removidos.
        Obedecendo:
        - posse com cargo do tipo AC;
        - requisição com período vigente.
        """
        desligamento_posse_ac = Q(
            Q(movimentacao_posse__quadro__cargo__tipo_lei_cargo="AC")
            & Q(movimentacao_posse__requisicao__periodo__data_fim__gte=datetime.now())
        )
        return MovimentacaoDesligamento.objects.filter(desligamento_posse_ac).values(
            "pk"
        )

    @classmethod
    def uma_requisicao_nenhum_desligamento(cls, requisicao):
        """
        Este método retorna:
        - True, se a posse de origem possuir apenas uma requisição E
        a posse de origem não possuir desligamento;
        - False de outra forma.
        """
        return requisicao.posse_origem.requisicao.filter().count() == 1 and not hasattr(
            requisicao.posse_origem, "desligamento"
        )

    @classmethod
    def muitas_requisicao_nenhum_desligamento(cls, requisicao):
        """
        Este método retorna:
        - True, se a posse de origem possuir mais de uma requisição E
        a posse de origem não possuir desligamento;
        - False de outra forma.
        """
        return requisicao.posse_origem.requisicao.filter().count() > 1 and not hasattr(
            requisicao.posse_origem, "desligamento"
        )

    @classmethod
    def nenhum_periodo_vigente(cls, requisicao):
        """
        Este método retorna:
        - True, se a requisição não possuir período vigente;
        - False de outra forma.
        """
        return (
            requisicao.posse_origem.requisicao.filter(
                cls.filtro_periodo_vigente()
            ).count()
            == 0
        )

    @classmethod
    def muitas_requisicao_nenhum_periodo_vigente_nenhum_desligamento(cls, requisicao):
        """
        Este método retorna:
        - True, cls.muitas_requisicao_nenhum_desligamento E cls.nenhum_periodo_vigente;
        - False de outra forma.
        """
        return (
            cls.muitas_requisicao_nenhum_desligamento(requisicao)
            and cls.nenhum_periodo_vigente(requisicao)
            and not requisicao.posse_origem.requisicao.filter(
                Q(data_fim__gte=datetime.now().date())
            ).exists()
        )

    @classmethod
    def criar_desligamento(cls):
        """
        Este método cria os desligamentos para as requisições que não possuem desligamento do cargo de origem para inativar o servidor.
        Implementação de acordo
        """
        for requisicao in cls.requisicao_finalizada_sem_desligamento():
            try:
                if cls.uma_requisicao_nenhum_desligamento(
                    requisicao
                ) or cls.muitas_requisicao_nenhum_periodo_vigente_nenhum_desligamento(
                    requisicao
                ):
                    periodo = cls.dados_desligamento(requisicao)
                    data_fim = datetime.now().date()
                    if periodo:
                        data_fim = periodo.data_fim + relativedelta(days=1)
                    desligamento = MovimentacaoDesligamento(
                        movimentacao_posse=requisicao.posse_origem,
                        tipo_desligamento=13,
                        opcao=2,
                        data_desligamento=data_fim,
                        publicacao_movimentacao=(
                            periodo.publicacao
                            if periodo
                            else requisicao.publicacao_movimentacao
                        ),
                        texto=cls.get_texto(requisicao, data_fim),
                    )
                    desligamento.save()
                cls.atualiza_requisicao(requisicao)
            except Exception as e:
                log.exception(e)
                log.warning(
                    "Problemas na criação do desligamento para requisição %s"
                    % requisicao
                )

    @classmethod
    def dados_desligamento(cls, requisicao):
        """
        Este método
        """
        periodo = None
        try:
            now = datetime.now().date()
            periodo = PeriodoRequisicao.objects.filter(
                Q(requisicao=requisicao) & Q(data_fim__lte=now) & ~Q(data_fim__gte=now)
            ).order_by("-data_fim")[0]
        except Exception:
            log.warning(
                "Não existe período cadastrado para a requisição %s" % requisicao
            )
        return periodo

    @classmethod
    def get_texto(cls, requisicao, data_fim):
        """
        Este método formata o texto para a movimentação de desligamento.
        """
        return (
            "Desligamento da posse %s de origem, pois a requisição foi finalizada em %s."
            % (requisicao.posse_origem, DateUtils.date_to_str(data_fim))
        )

    @classmethod
    def remover_desligamento(cls):
        MovimentacaoDesligamento.objects.filter(
            pk__in=cls.verifica_desligamento_com_requisicao_vigente()
        ).delete()

    @classmethod
    def atualiza_requisicao(cls, requisicao):
        try:
            ativo = False
            if MovimentacaoRequisicao.objects.filter(
                Q(pk=requisicao) & cls.filtro_periodo_vigente()
            ):
                ativo = True
            log.info(
                "Requisição status: %s - mudando para: %s"
                % (
                    MovimentacaoRequisicao.objects.filter(Q(pk=requisicao))[0].ativo,
                    ativo,
                )
            )
            MovimentacaoRequisicao.objects.filter(pk=requisicao).update(ativo=ativo)
        except Exception as e:
            log.warning("Problemas na atualização da requisição %s" % requisicao)
            log.exception(e)

    @classmethod
    def existe_outra_requisicao_ativa(cls, posse_origem, date_start):
        """
        Este método verifica se existe para o mesmo período.
        """
        return (
            MovimentacaoRequisicao.objects.filter(
                Q(posse_origem=posse_origem) & cls.filtro_periodo_vigente()
            )
            .exclude(data_fim__lt=date_start)
            .distinct()
            .values("pk")
        )

    @classmethod
    def atualiza_data_inicio_fim(cls, requisicao):
        periodos = PeriodoRequisicao.objects.filter(requisicao__pk=requisicao.pk)
        if periodos.exists():
            data_inicio = periodos.order_by("data_inicio")[0].data_inicio
            data_fim = periodos.latest("data_fim").data_fim
            cls.verifica_periodo_continuo(requisicao, data_inicio, data_fim)
            MovimentacaoRequisicao.objects.filter(pk=requisicao.pk).update(
                data_inicio=data_inicio,
                data_fim=data_fim,
            )

    @classmethod
    def verifica_periodo_continuo(cls, requisicao, data_inicio, data_fim):
        dr_geral = NewDateRange(data_inicio, data_fim)
        dr_periodos = NewDateRange()
        for periodo in PeriodoRequisicao.objects.filter(
            requisicao__pk=requisicao.pk
        ).order_by("data_inicio"):
            dr_periodos += NewDateRange(periodo.data_inicio, periodo.data_fim)
        if dr_geral.days != dr_periodos.days:
            raise Exception(
                "Período não é contínuo. Para períodos não contínuos uma nova requisição deve ser criada."
            )
        return True

    def create_period_first(self, **period):
        if not self.periodo.exists():
            period = PeriodoRequisicao(**period)
            period.save()
            self.periodo.add(period)


class RequestMove(MovimentacaoPosse):
    organ_origin = models.ForeignKey(
        "UnidadeAdministrativa",
        related_name="requestmove_organ_origin",
        on_delete=models.PROTECT,
    )
    possession_origin_date = models.DateField(
        null=True, verbose_name="Data posse na origem"
    )
    onus = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_ONUS"),
        default=2,
        verbose_name="Ônus",
    )
    category = models.IntegerField(
        default=301,
        verbose_name="Categoria eSocial origem",
        choices=Choice.get_choices_for("rh", "CATEGORY_WORKER"),
    )

    # deprecated
    possession_origin = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=True,
        related_name="requestmove_possession_origin",
        on_delete=models.PROTECT,
    )
    job_position_origin = models.CharField(
        max_length=255, null=True, verbose_name="Cargo na origem", blank=True
    )
    cbo = models.ForeignKey("Cbo", null=True, blank=True, on_delete=models.SET_NULL)
    regime_contract = models.IntegerField(
        default=2,
        blank=True,
        verbose_name="Regime de contrato",
        choices=Choice.get_choices_for("rh", "REGIME_CONTRACT"),
    )

    ALLOWED_TYPE_BY_POSSESSION = ("REQ", "RCM", "RFC", "REX")

    def __str__(self):
        description = f"{self.servidor.get_type_by_possession_display()}"
        if self.job_position_origin:
            description = self.job_position_origin
        return f"{description} - {self.organ_origin} - ÔNUS: {self.get_onus_display()}".upper()

    @property
    def tipo_carreira(self):
        return "REQUISICAO"

    @property
    def description_possession(self):
        description = "SEM INFORMAÇÃO DO CARGO"
        if self.job_position_origin:
            description = f"{self.job_position_origin} - {self.organ_origin}".upper()
        return description

    def get_texto(self):
        onus = f"ônus para {self.get_onus_display()}"
        cfg = Configuration.get_or_create("gfp")
        organ = cfg.get("orgao", "")
        try:
            organ = f"{UnidadeAdministrativa.objects.filter(pk=int(organ)).last()}"
        except Exception as err:
            log.exception(err)
            organ = "Órgão local não configurado em: gfp.orgao."

        msg = Message.objects.get(mid="RH_REQUESTMOVEMENT")
        text = msg.formated(
            {
                "employee_text": self.servidor.texto_servidor(),
                "name": f"{self.servidor.pessoa_fisica}",
                "organ_origin": f"{self.organ_origin}",
                "destiny": organ,
                "onus": onus,
                "start_date": DateUtils.date_to_str(self.data_exercicio),
                "end_date": (
                    DateUtils.date_to_str(
                        self.data_desligamento - relativedelta(days=1)
                    )
                    if self.data_desligamento
                    else ""
                ),
            }
        )
        return text

    def validate_publicacao(self):
        return True

    def validate_data_vigencia(self):
        return True

    def validate_vacancy_number_filled(self):
        return True

    def validate_job_position_type(self):
        if not self.quadro:
            raise Exception(
                "É necessário selecionar o cargo/quadro do órgão de origem do servidor. \
                Caso não exista no Athenas, crie-o e selecione!"
            )
        if self.quadro.cargo.tipo_lei_cargo != "AC":
            raise Exception(
                f"O cargo/quadro cadastro precisar ser do tipo: Acordo de Cooperação (AC) Selecionado: {self.quadro.cargo}"
            )
        return True

    def validate_organ_origin(self):
        if not hasattr(self, "organ_origin") or self.organ_origin is None:
            raise Exception("É necessário selecionar o órgão de origem do servidor.")

    def validate_onus(self):
        if not hasattr(self, "onus") or self.onus is None:
            raise Exception("É necessário selecionar o ônus do provimento.")

    def validate_regime_contract(self):
        if not hasattr(self, "regime_contract") or self.regime_contract is None:
            raise Exception("É necessário selecionar o Regime do Contrato.")

    def validate_category(self):
        if not hasattr(self, "category") or self.category is None:
            raise Exception("É necessário selecionar a Categoria origem (eSocial).")

    def validate_social_security_regime(self):
        sse = (
            SocialSecurityEmployee.objects.currents_in(
                range=NewDateRange(self.data_exercicio, self.data_desligamento)
            )
            .filter(employee=self.servidor)
            .last()
        )
        if sse:
            if (
                MAP_FORESIGHT.get(sse.social_security_config.regime)
                != self.regime_contract
            ):
                message = "O Regime de contrato é diferente do cadastrado em"
                message += f"Configurações previdenciárias ({sse.social_security_config.get_regime_display()})."
                raise Exception(message)

    def validate_possession_origin_date(self):
        if not self.possession_origin_date:
            raise Exception(
                """ Informar a data de posse na origem que deverá ser anterior
            às preenchidas em Data Exercício e Efeito Financeiro-Início"""
            )
        elif (
            self.possession_origin_date
            and self.possession_origin_date >= self.data_exercicio
            or self.possession_origin_date >= self.financial_effect_date_start
        ):
            raise Exception(
                """ A data de posse na origem deverá ser anterior às preenchidas
                 em "Data Exercício" e "Efeito Financeiro-Início"""
            )
        return True

    def validate_cnpj_organ_origin(self):
        if self.organ_origin and not self.organ_origin.pessoa_juridica.cnpj:
            raise Exception("Informar o CNPJ do órgão selecionado")
        return True

    def validate(self):
        self.validate_organ_origin()
        self.validate_cnpj_organ_origin()
        self.validate_onus()
        self.validate_category()
        self.validate_regime_contract()
        self.validate_possession_origin_date()
        super().validate()
        return self.validate_social_security_regime()

    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.data_posse = self.data_exercicio
        self.validate()
        self.job_position_origin = f"{self.quadro.cargo}"
        self.cbo = self.quadro.cargo.cbo
        super(RequestMove, self).save(*args, **kargs)

    def update_or_create_fire(self, end_date=None):
        """Este método atualiza ou cria o Desligamento da RequestMove."""
        if end_date and end_date < date.today():
            # defaults = {
            #     'tipo_desligamento': 21,  # FIM TSVE
            #     'opcao': 2,  # OFÍCIO
            #     'data_desligamento': end_date + relativedelta(days=1)

            # }
            # _fired_obj, _fired_created = MovimentacaoDesligamento.objects.update_or_create(
            #     servidor=self.servidor, movimentacao_posse=self, defaults=defaults)

            md = MovimentacaoDesligamento(
                # servidor=employee, movimentacao_posse=_possession, defaults=defaults)
                servidor=self.servidor,
                movimentacao_posse=self,
                tipo_desligamento=21,
                opcao=2,
                data_desligamento=end_date,
                created_by_id=1,
                modified_by_id=1,
            )
            # print(_fired_obj)
            md.save_base()
            self.servidor.save()

    def update_request_move(self, end_date=None):
        """Este método atualiza a RequestMove"""
        self.update_or_create_fire(end_date)

    def create_first_period(self):
        """Cria o primeiro período caso não exista."""
        if not self.periods.exists():
            PeriodoRequisicao.objects.get_or_create(
                request_move=self,
                **{
                    "data_inicio": self.data_exercicio,
                    "data_fim": self.data_desligamento,
                    "publicacao": self.publicacao_movimentacao,
                },
            )


class MovimentacaoAproveitamento(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_aproveitamento",
        on_delete=models.PROTECT,
    )

    ALLOWED_TYPE_BY_POSSESSION = ("EFE", "ECM", "EFC")

    class Meta:
        verbose_name = "Movimentação de Aprovietamento"
        db_table = "rh_movaproveitamento"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "APROVEITAMENTO"

    def validate_effective_employee(self):
        if self.posse_anterior.quadro.cargo.tipo_lei_cargo != "EF":
            raise Exception("Apenas servidores efetivos podem ser aproveitados.")

    def validate(self, label_provision):
        self.validate_if_cargo_is_empty()
        self.validate_if_data_posse_is_empty()
        self.validate_effective_employee()

        return super(MovimentacaoAproveitamento, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.validate(label_provision)

        self.servidor = self.posse_anterior.servidor
        super(MovimentacaoAproveitamento, self).save(*args, **kargs)

    def get_texto(self):
        try:
            with codecs.open(
                "%s/aproveitamento.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "numero_publicacao": "%s"
                    % self.publicacao_movimentacao.numero_publicacao,
                    "data_publicacao": "%s"
                    % DateUtils.date_to_str(
                        self.publicacao_movimentacao.data_expedicao
                    ),
                    "veiculo_publicacao": "%s"
                    % self.publicacao_movimentacao.get_veiculo_publicacao_display(),
                    "servidor": "%s" % self.servidor,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class MovimentacaoPromocao(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_promocao",
        on_delete=models.PROTECT,
    )
    criterio = models.IntegerField(
        default=1, choices=Choice.get_choices_for("rh", "LEVEL_PROMOTION")
    )

    ALLOWED_TYPE_BY_POSSESSION = (
        "MBR",
        "MEL",
        "MCM",
        "MEC",
        "MBR2",
        "MEL2",
        "MCM2",
        "MEC2",
    )

    class Meta:
        verbose_name = "Movimentação de Promoção"
        db_table = "rh_movpromocao"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "PROMOCAO"

    def validate_criterio(self):
        if not self.criterio:
            raise Exception("Preencha o campo Critério")

    def validate(self):
        self.validate_criterio()
        return super().validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.servidor = self.posse_anterior.servidor
        prev_possession = self.posse_anterior
        pdate = self.financial_effect_date_start or self.data_exercicio
        if pdate:
            pdate = pdate - relativedelta(days=1)
        if not self.pk and prev_possession.financial_effect_date_end != pdate:
            prev_possession.financial_effect_date_end = pdate
            prev_possession.save()
        super(MovimentacaoPromocao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            PROMOVER, pelo critério de %(criterio)s,
            o %(cargo_origem)s - %(servidor)s para o cargo de %(cargo_destino)s, conforme %(publicacao)s.
            """
            texto_exercicio = (
                (
                    "com exercício a partir de %s,"
                    % (DateUtils.date_to_str(self.data_exercicio))
                )
                if self.data_exercicio
                else ""
            )
            with codecs.open(
                "%s/promocao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "servidor": "%s" % self.servidor.pessoa_fisica.nome,
                    "cargo_origem": "%s" % self.posse_anterior.quadro.cargo,
                    "cargo_destino": "%s" % self.quadro.cargo,
                    "criterio": "%s" % self.get_criterio_display(),
                    "texto_exercicio": "%s" % texto_exercicio,
                    "publicacao": "%s" % self.publicacao_movimentacao,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class MovimentacaoTitularizacao(MovimentacaoPromocao):
    class Meta:
        verbose_name = "Movimentação de Titularização"
        db_table = "rh_movtitularizacao"

    @property
    def tipo_carreira(self):
        return "TITULARIZACAO"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)
        self.servidor = self.posse_anterior.servidor
        prev_possession = self.posse_anterior
        pdate = self.financial_effect_date_start or self.data_exercicio
        if pdate:
            pdate = pdate - relativedelta(days=1)
        if not self.pk and prev_possession.financial_effect_date_end != pdate:
            prev_possession.financial_effect_date_end = pdate
            prev_possession.save()
        super(MovimentacaoTitularizacao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            TITULARIZAR, %(texto_exercicio)s o(a) Promotor(a) de Justiça Substituto(a) - %(servidor)s
            no cargo de %(cargo_destino)s, conforme %(publicacao)s.
            """
            texto_exercicio = (
                (
                    "com exercício a partir de %s,"
                    % (DateUtils.date_to_str(self.data_exercicio))
                )
                if self.data_exercicio
                else ""
            )
            with codecs.open(
                "%s/titularizacao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "servidor": "%s" % self.servidor.pessoa_fisica.nome,
                    "cargo_destino": "%s" % self.quadro.cargo,
                    "texto_exercicio": "%s" % texto_exercicio,
                    "publicacao": "%s" % self.publicacao_movimentacao,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class MovimentacaoRemocaoMembro(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_remocaomembro",
        on_delete=models.PROTECT,
    )
    criterio = models.IntegerField(
        default=1, choices=Choice.get_choices_for("rh", "LEVEL_REMOVAL_MEMBER")
    )
    lotacao_destino = models.ForeignKey(
        Lotacao,
        on_delete=models.CASCADE,
        related_name="lotacao_remocao_membro",
        verbose_name="Lotação de destino",
        null=True,
        blank=True,
    )
    servidor_permuta = models.ForeignKey(
        Servidor,
        on_delete=models.CASCADE,
        related_name="permuta_remocao_membro",
        verbose_name="Servidor da permuta",
        null=True,
        blank=True,
    )

    ALLOWED_TYPE_BY_POSSESSION = (
        "MBR",
        "MEL",
        "MCM",
        "MEC",
        "MBR2",
        "MEL2",
        "MCM2",
        "MEC2",
    )

    class Meta:
        verbose_name = "Movimentação de Remoção de Membro"
        db_table = "rh_movremocaomembro"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "REMOCAO"

    def validate_criterio(self):
        if not self.criterio:
            raise Exception("Preencha o campo Critério")

    def validate_is_member(self):
        if self.servidor.tipo != "M":
            raise Exception(
                "Apenas membros podem ser removidos atravès de %s."
                % self._meta.verbose_name
            )

    def validate(self):
        self.validate_is_member()
        self.validate_criterio()
        return super(MovimentacaoRemocaoMembro, self).validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.validate()

        self.servidor = self.posse_anterior.servidor
        prev_possession = self.posse_anterior
        pdate = self.financial_effect_date_start or self.data_exercicio
        if pdate:
            pdate = pdate - relativedelta(days=1)
        if not self.pk and prev_possession.financial_effect_date_end != pdate:
            prev_possession.financial_effect_date_end = pdate
            prev_possession.save()
        super(MovimentacaoRemocaoMembro, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            REMOVER, pelo critério de %(criterio)s,
            o %(cargo_origem)s - %(servidor)s para o cargo de %(cargo_destino)s.
            Conforme %(publicacao)s.
            """
            texto_exercicio = (
                (
                    "com exercício a partir de %s,"
                    % (DateUtils.date_to_str(self.data_exercicio))
                )
                if self.data_exercicio
                else ""
            )
            with codecs.open(
                "%s/remocao_membro.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "servidor": "%s" % self.servidor.pessoa_fisica.nome,
                    "cargo_origem": "%s" % self.posse_anterior.quadro.cargo,
                    "cargo_destino": "%s" % self.quadro.cargo,
                    "criterio": "%s" % self.get_criterio_display(),
                    "texto_exercicio": "%s" % texto_exercicio,
                    "publicacao": "%s" % self.publicacao_movimentacao,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto

    @transaction.atomic
    def delete(self, *args, **kargs):
        super(MovimentacaoRemocaoMembro, self).delete(*args, **kargs)


class MovimentacaoReadaptacao(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_readaptacao",
        on_delete=models.PROTECT,
    )

    ALLOWED_TYPE_BY_POSSESSION = (
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
    )

    class Meta:
        verbose_name = "Movimentação de Readaptação"
        db_table = "rh_movreadaptacao"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "READAPTACAO"

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.servidor = self.posse_anterior.servidor
        super(MovimentacaoReadaptacao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            Conforme a publicação nº %(numero_publicacao)s,
            de %(data_publicacao)s no %(veiculo_publicacao)s READAPTAÇÃO do
            servidor %(servidor)s.
            """
            with codecs.open(
                "%s/readaptacao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "numero_publicacao": "%s"
                    % self.publicacao_movimentacao.numero_publicacao,
                    "data_publicacao": "%s"
                    % DateUtils.date_to_str(
                        self.publicacao_movimentacao.data_publicacao
                    ),
                    "veiculo_publicacao": "%s"
                    % self.publicacao_movimentacao.get_veiculo_publicacao_display(),
                    "servidor": "%s" % self.servidor,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class MovimentacaoReconducao(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_reconducao",
        on_delete=models.PROTECT,
    )

    ALLOWED_TYPE_BY_POSSESSION = (
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
    )

    class Meta:
        verbose_name = "Movimentação de Recondução"
        db_table = "rh_movreconducao"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "RECONDUCAO"

    @property
    def data_admissao(self):
        return self.posse_reconduzida.data_admissao

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.servidor = self.posse_anterior.servidor
        if not self.quadro:
            self.quadro = self.posse_anterior.quadro
        if not self.data_posse:
            self.data_posse = self.posse_anterior.data_posse
        super(MovimentacaoReconducao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            with codecs.open(
                "%s/reconducao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_reconducao = tpl % {
                    "publicacao": "%s" % self.publicacao_movimentacao,
                    "data_publicacao": "%s"
                    % self.publicacao_movimentacao.data_expedicao,
                    "servidor": "%s" % self.servidor,
                    "cargo": "%s" % self.quadro,
                    "publicacao_posse_anterior": "%s"
                    % self.posse_anterior.publicacao_movimentacao,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto_reconducao

    def gera_progressao(self):
        log.debug("atualizando progressoes do cargo")

    def progression_generator(self):
        try:
            from rh.gfp.models import MovimentacaoProgressao

            progression_old = MovimentacaoProgressao.objects.filter(
                servidor=self.servidor,
                data_fim_vigencia__lte=self.posse_anterior.data_desligamento,
            ).latest("data_inicio_vigencia")
            dr_lapse = NewDateRange(
                self.posse_anterior.data_desligamento, self.data_exercicio
            )
            lapse_days = dr_lapse.days - 1
            expected_date = progression_old.expected_date + relativedelta(
                days=lapse_days
            )
            new, created = MovimentacaoProgressao.objects.get_or_create(
                data_inicio_vigencia=self.data_exercicio,
                expected_date=expected_date,
                referencia_nivel2d=progression_old.next_reference,
                movimentacao_posse=self,
                publicacao_movimentacao=self.publicacao_movimentacao,
            )
        except Exception as err:
            log.exception(err)


class MovimentacaoReintegracao(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_reintegracao",
        on_delete=models.PROTECT,
    )

    ALLOWED_TYPE_BY_POSSESSION = (
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
    )

    class Meta:
        verbose_name = "Movimentação de Reintegração"
        db_table = "rh_movreintegracao"

    def __str__(self):
        return "%s em %s" % (self.get_tipo_movcarreira_display(), self.quadro)

    @property
    def tipo_carreira(self):
        return "REINTEGRACAO"

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.servidor = self.posse_anterior.servidor
        super(MovimentacaoReintegracao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            Conforme a publicação nº %(numero_publicacao)s,
            de %(data_publicacao)s no %(veiculo_publicacao)s
            REINTEGRAÇÃO do servidor %(servidor)s.
            """
            dt_publicacao = self.publicacao_movimentacao.data_publicacao

            if dt_publicacao is None:
                dt_publicacao = self.data_posse

            txt_dt_publicacao = (
                "" if dt_publicacao is None else DateUtils.date_to_str(dt_publicacao)
            )

            with codecs.open(
                "%s/reintegracao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "numero_publicacao": "%s"
                    % self.publicacao_movimentacao.numero_publicacao,
                    "data_publicacao": "%s" % txt_dt_publicacao,
                    "veiculo_publicacao": "%s"
                    % self.publicacao_movimentacao.get_veiculo_publicacao_display(),
                    "servidor": "%s" % self.servidor,
                }
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class MovimentacaoReversao(MovimentacaoPosse):
    posse_anterior = models.ForeignKey(
        "MovimentacaoPosse",
        null=True,
        blank=False,
        related_name="posse_reversao",
        on_delete=models.PROTECT,
    )

    ALLOWED_TYPE_BY_POSSESSION = (
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
    )

    class Meta:
        verbose_name = "Movimentação de Reversão"
        db_table = "rh_movreversao"

    @property
    def tipo_carreira(self):
        return "REVERSAO"

    @transaction.atomic
    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)

        self.servidor = self.posse_anterior.servidor
        super(MovimentacaoReversao, self).save(*args, **kargs)

    def get_texto(self):
        try:
            """
            REVERSÃO %(servidor)s.
            """
            with codecs.open(
                "%s/reversao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {"servidor": "%s" % self.servidor}
        except Exception as err:
            log.exception(err)
            raise err
        return texto


class PossessionTrainee(MovimentacaoPosse):
    """Posse de Estagiário."""

    employee_supervisor = models.ForeignKey(
        "Servidor",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Supervisor",
        related_name="possessiontrainee_supervisor",
    )
    educational_institution = models.ForeignKey(
        "PessoaJuridica",
        verbose_name="Instituição Educacional",
        on_delete=models.PROTECT,
        related_name="possessiontrainee_educational_institution",
        null=True,
        blank=True,
    )
    integration_agent = models.ForeignKey(
        "PessoaJuridica",
        null=True,
        blank=True,
        verbose_name="Agente de Integração",
        on_delete=models.PROTECT,
        related_name="possessiontrainee_educational_integration_agent",
    )
    nature = models.IntegerField(
        default=TRAINEE_NATURE_MANDATORY,
        choices=Choice.get_choices_for("rh", "TRAINEE_NATURE"),
        verbose_name="Natureza",
    )
    level = models.IntegerField(
        default=TRAINEE_LEVEL_FUNDAMENTAL,
        choices=Choice.get_choices_for("rh", "TRAINEE_LEVEL"),
        verbose_name="Nível",
    )
    occupation_area = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Área de ocupação"
    )
    insurance_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Número de seguro"
    )
    value = models.DecimalField(
        decimal_places=2, max_digits=14, null=True, blank=True, verbose_name="Valor"
    )
    institution_inep = models.ForeignKey(
        "HigherEducationInstitution",
        verbose_name="Instituição (INEP)",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    course_cine_brasil = models.ForeignKey(
        "CourseCineBrasil",
        verbose_name="Curso (INEP)",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    ALLOWED_TYPE_BY_POSSESSION = ("EST",)

    class Meta:
        verbose_name = "Posse de Estagiário"

    @property
    def tipo_carreira(self):
        return "POSSE_ESTAGIARIO"

    def anotacao(self, *args, **kargs):
        pass

    def validate_publicacao(self):
        return True

    def validate_data_vigencia(self):
        return True

    def validate_job_position_type(self):
        if self.quadro and self.quadro.cargo.tipo_lei_cargo != "ES":
            raise Exception("Posse permitida em cargo do tipo: ESTAGIÁRIO")
        return True

    def validate_educational_institution(self):
        if not self.educational_institution:
            raise Exception("Cadastre uma Instituição Educacional")
        if not self.educational_institution.cnpj:
            raise Exception("Cadastre o CNPJ para a Instituição Educacional")
        if not self.educational_institution.razao_social:
            raise Exception("Cadastre a razão social para a Instituição Educacional")

    def validate_employee_supervisor(self):
        if not self.employee_supervisor:
            raise Exception("Preencha o campo do Supervisor")

    def validate_integration_agent(self):
        if not self.integration_agent:
            raise Exception("Preencha o campo do Agente de Integração.")
        if not self.integration_agent.cnpj:
            raise Exception("Cadastre o CNPJ do agente de integração.")
        if not self.integration_agent.razao_social:
            raise Exception("Cadastre a razão social do agente de integração.")
        address = self.integration_agent.address.filter()
        if address.exists():
            address = address.last()
            if not address.municipio:
                raise Exception(
                    "Cadastre endereço para o agente de integração - MUNICÍPIO."
                )
            if not address.cep:
                raise Exception("Cadastre endereço para o agente de integração - CEP.")
            if not address.logradouro:
                raise Exception(
                    "Cadastre endereço para o agente de integração - LOGRADOURO."
                )
            if not address.numero:
                raise Exception(
                    "Cadastre endereço para o agente de integração - NÚMERO."
                )
        else:
            raise Exception("Cadastre endereço para o agente de integração.")

    def validate_insurance_number(self):
        if not self.insurance_number:
            raise Exception("Preencha o campo do Número do Seguro.")

    def validate_nature(self):
        if not self.nature:
            raise Exception("Preencha o campo da Natureza.")

    def validate_occupation_area(self):
        if not self.occupation_area:
            raise Exception("Preencha o campo da Área de Ocupação.")

    def validate_level(self):
        if not self.level:
            raise Exception("Preencha o campo do Nível.")

    def validate(self):
        self.validate_educational_institution()
        self.validate_employee_supervisor()
        self.validate_integration_agent()
        self.validate_insurance_number()
        self.validate_nature()
        self.validate_occupation_area()
        self.validate_level()

        self.validate_job_position_type()
        super(PossessionTrainee, self).validate()

    @classmethod
    def terminate_trainee_by_end_contract(cls):
        log = getLogger("db")
        for possession in PossessionTrainee.objects.filter():
            try:
                if (
                    possession.data_desligamento
                    and possession.data_desligamento < date.today()
                ):
                    possession.validate()
                    possession.servidor.validate()
                    if not MovimentacaoDesligamento.objects.filter(
                        movimentacao_posse=possession
                    ).exists():
                        log.info(
                            f"## Desligando - {possession.servidor} do provimento {possession}"
                        )
                        md = MovimentacaoDesligamento(
                            servidor=possession.servidor,
                            movimentacao_posse=possession,
                            tipo_desligamento=22,  # Fim de Contrato
                            opcao=2,  # De Ofício
                            data_desligamento=possession.data_desligamento,
                            created_by_id=1,
                            modified_by_id=1,
                        )
                        md.save_base()
                        if md:
                            md.termination_trainee_acq_periods(
                                possession.data_desligamento
                            )
                        possession.save()
                        possession.servidor.save()
                    elif possession in PossessionTrainee.objects.filter(ativo=True):
                        try:
                            possession.save()
                            possession.servidor.save()
                        except Exception as e:
                            log.info(
                                f"## Erro - {possession.servidor} do provimento {possession} - {e}"
                            )
            except Exception as e:
                log.info(
                    f"## Erro - {possession.servidor} do provimento {possession} - {e}"
                )

    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)
        self.data_exercicio = self.data_posse
        self.validate()
        super(PossessionTrainee, self).save(*args, **kargs)


class PossessionResident(MovimentacaoPosse):
    """Posse de Residente."""

    employee_supervisor = models.ForeignKey(
        "Servidor",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Supervisor",
        related_name="possessionresident_supervisor",
    )
    educational_institution = models.ForeignKey(
        "PessoaJuridica",
        verbose_name="Instituição Educacional",
        on_delete=models.PROTECT,
        related_name="possessionresident_educational_institution",
        null=True,
        blank=True,
    )
    integration_agent = models.ForeignKey(
        "PessoaJuridica",
        null=True,
        blank=True,
        verbose_name="Agente de Integração",
        on_delete=models.PROTECT,
        related_name="possessionresident_educational_integration_agent",
    )
    nature = models.IntegerField(
        default=TRAINEE_NATURE_MANDATORY,
        choices=Choice.get_choices_for("rh", "TRAINEE_NATURE"),
        verbose_name="Natureza",
    )
    level = models.IntegerField(
        default=TRAINEE_LEVEL_FUNDAMENTAL,
        choices=Choice.get_choices_for("rh", "TRAINEE_LEVEL"),
        verbose_name="Nível",
    )
    occupation_area = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Área de ocupação"
    )
    insurance_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Número de seguro"
    )
    value = models.DecimalField(
        decimal_places=2, max_digits=14, null=True, blank=True, verbose_name="Valor"
    )
    institution_inep = models.ForeignKey(
        "HigherEducationInstitution",
        verbose_name="Instituição (INEP)",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    course_cine_brasil = models.ForeignKey(
        "CourseCineBrasil",
        verbose_name="Curso (INEP)",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    ALLOWED_TYPE_BY_POSSESSION = ("RES",)

    class Meta:
        verbose_name = "Posse de Residente"

    @property
    def tipo_carreira(self):
        return "POSSE_RESIDENTE"

    @property
    def situacao_funcional(self):
        return "ATIVO"

    def anotacao(self, *args, **kargs):
        pass

    def validate_publicacao(self):
        return True

    def validate_data_vigencia(self):
        return True

    def validate_job_position_type(self):
        if self.quadro and self.quadro.cargo.tipo_lei_cargo != "RS":
            raise Exception("Posse permitida em cargo do tipo: RESIDENTE")
        return True

    def validate_educational_institution(self):
        if not self.educational_institution:
            raise Exception("Cadastre uma Instituição Educacional")
        if not self.educational_institution.cnpj:
            raise Exception("Cadastre o CNPJ para a Instituição Educacional")
        if not self.educational_institution.razao_social:
            raise Exception("Cadastre a razão social para a Instituição Educacional")

    def validate_employee_supervisor(self):
        if not self.employee_supervisor:
            raise Exception("Preencha o campo do Supervisor")

    def validate_integration_agent(self):
        if not self.integration_agent:
            raise Exception("Preencha o campo do Agente de Integração.")
        if not self.integration_agent.cnpj:
            raise Exception("Cadastre o CNPJ do agente de integração.")
        if not self.integration_agent.razao_social:
            raise Exception("Cadastre a razão social do agente de integração.")
        address = self.integration_agent.address.filter()
        if address.exists():
            address = address.last()
            if not address.municipio:
                raise Exception(
                    "Cadastre endereço para o agente de integração - MUNICÍPIO."
                )
            if not address.cep:
                raise Exception("Cadastre endereço para o agente de integração - CEP.")
            if not address.logradouro:
                raise Exception(
                    "Cadastre endereço para o agente de integração - LOGRADOURO."
                )
            if not address.numero:
                raise Exception(
                    "Cadastre endereço para o agente de integração - NÚMERO."
                )
        else:
            raise Exception("Cadastre endereço para o agente de integração.")

    def validate_insurance_number(self):
        if not self.insurance_number:
            raise Exception("Preencha o campo do Número do Seguro.")

    def validate_nature(self):
        if not self.nature:
            raise Exception("Preencha o campo da Natureza.")

    def validate_occupation_area(self):
        if not self.occupation_area:
            raise Exception("Preencha o campo da Área de Ocupação.")

    def validate_level(self):
        if not self.level:
            raise Exception("Preencha o campo do Nível.")

    def validate(self):
        self.validate_educational_institution()
        self.validate_employee_supervisor()
        self.validate_integration_agent()
        self.validate_insurance_number()
        self.validate_nature()
        self.validate_occupation_area()
        self.validate_level()

        self.validate_job_position_type()
        super(PossessionResident, self).validate()

    def save(self, *args, **kargs):
        self.data_exercicio = self.data_posse
        self.validate()
        super(PossessionResident, self).save(*args, **kargs)

    @classmethod
    def terminate_resident_by_end_contract(cls):
        log = getLogger("db")
        for possession in PossessionResident.objects.filter():
            try:
                if (
                    possession.data_desligamento
                    and possession.data_desligamento < date.today()
                ):
                    possession.validate()
                    possession.servidor.validate()
                    if not MovimentacaoDesligamento.objects.filter(
                        movimentacao_posse=possession
                    ).exists():
                        log.info(
                            f"## Desligando - {possession.servidor} do provimento {possession}"
                        )
                        md = MovimentacaoDesligamento(
                            servidor=possession.servidor,
                            movimentacao_posse=possession,
                            tipo_desligamento=22,  # Fim de Contrato
                            opcao=2,  # De Ofício
                            data_desligamento=possession.data_desligamento,
                            created_by_id=1,
                            modified_by_id=1,
                        )
                        md.save_base()
                        if md:
                            md.termination_resident_acq_periods(
                                possession.data_desligamento
                            )
                        possession.save()
                        possession.servidor.save()
                    elif possession in PossessionResident.objects.filter(ativo=True):
                        try:
                            possession.save()
                            possession.servidor.save()
                        except Exception as e:
                            log.info(
                                f"## Erro - {possession.servidor} do provimento {possession} - {e}"
                            )
            except Exception as e:
                log.info(
                    f"## Erro - {possession.servidor} do provimento {possession} - {e}"
                )


class PossessionCollaborator(MovimentacaoPosse):
    """Posse de Colaborador."""

    number_gedoc = models.BigIntegerField(
        null=True, blank=True, verbose_name="Número GEDOC"
    )
    number_insurance = models.BigIntegerField(
        null=True, blank=True, verbose_name="Número de Seguro"
    )

    ALLOWED_TYPE_BY_POSSESSION = ("EXT", "TCR", "VOL", "JCA")

    class Meta:
        verbose_name = "Posse de Colaborador"

    def __str__(self):
        return "%s em %s" % (
            self.get_tipo_movcarreira_display(),
            self.description_possession,
        )

    @property
    def tipo_carreira(self):
        return "POSSE_COLABORADOR"

    def anotacao(self, *args, **kargs):
        pass

    def validate_publicacao(self):
        return True

    def validate_data_vigencia(self):
        return True

    def validate_ext_possession_cargo(self):
        if self.servidor.type_by_possession in (
            "EXT"
        ) and self.quadro.cargo.tipo_lei_cargo not in ("EX"):
            raise Exception(
                "É necessário selecionar o cargo/quadro cujo tipo seja EXTERNO - SEM VÍNCULO"
            )

    def validate_job_position_type(self):
        if self.quadro and self.quadro.cargo.tipo_lei_cargo not in (
            "TE",
            "VL",
            "JC",
            "EX",
        ):
            raise Exception(
                "Posse permitida em cargo do tipo: TERCEIRIZADO, VOLUNTÁRIO, EXTERNO - SEM VÍNCULO ou JOVEM CIDADÃO - APRENDIZ"
            )
        return True

    def validate_office(self):
        # Validando pelo cargo: 12917 - VOLUNTARIO-MPMT
        if self.quadro.cargo.id != 12917:
            log.info("entrou")
            self.number_gedoc = None
            self.number_insurance = None

    def save(self, *args, **kargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)
        self.data_exercicio = self.data_posse
        self.validate()

        super(PossessionCollaborator, self).save(*args, **kargs)

    def validate(self):
        self.validate_type_by_possession()
        self.validate_publicacao()
        self.validate_vacancy_number_filled()
        self.validate_office()
        self.validate_ext_possession_cargo()
        # self.validate_job_position_type() # TODO: Refatorar para não aceitar somente estagiário
        super().validate()
        return True


class MovimentacaoAposentadoria(MovimentacaoDesligamento):
    tipo_aposentadoria = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_RETIREMENT"), default=1
    )
    reversao = models.IntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        verbose_name="Reversão",
    )

    def validate(self):
        return self.validate_possession()

    def validate_possession(self):
        possessions = MovimentacaoPosse.objects.filter(
            servidor=self.servidor, ativo=True
        ).exclude(pk=self.movimentacao_posse)
        if possessions.exists():
            raise Exception(
                "Antes de aposentar o servidor é necessário finalizar os demais provimentos."
            )
        return True

    def texto_efetivo(self, *args, **kargs):
        texto = ""
        with codecs.open(
            "%s/aposentar_efetivo.txt" % templates.__path__[0], "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "tipo": "APOSENTAR %s" % (self.get_tipo_aposentadoria_display()),
                "nome": kargs.get("nome_pessoa"),
                "matricula": kargs.get("matricula"),
                "cargo_efetivo": self.movimentacao_posse.quadro,
                "portaria": kargs.get("portaria"),
                "data_portaria": kargs.get("data_portaria_nomeacao"),
                "data_desligamento": kargs.get("data_desligamento"),
            }
        return texto

    def set_tipo_desligamento(self):
        self.tipo_desligamento = 14
        tipo_aposentadoria = 0
        try:
            tipo_aposentadoria = int(self.tipo_aposentadoria)
        except Exception:
            pass
        if tipo_aposentadoria == 1:
            self.tipo_desligamento = 14
        elif tipo_aposentadoria == 2:
            self.tipo_desligamento = 15
        elif tipo_aposentadoria == 3:
            self.tipo_desligamento = 17
        elif tipo_aposentadoria == 4:
            self.tipo_desligamento = 4
        elif tipo_aposentadoria == 5:
            self.tipo_desligamento = 16
        elif tipo_aposentadoria == 6:
            self.tipo_desligamento = 5

    @transaction.atomic
    def save(self, *args, **kargs):
        self.set_tipo_desligamento()
        super(MovimentacaoAposentadoria, self).save(*args, **kargs)


class TerminationBenefitMovement(MovimentacaoDesligamento):

    def set_tipo_desligamento(self):
        self.tipo_desligamento = 24

    def set_termination_benefit_fields(self):
        benefit = self.movimentacao_posse.my_origin
        if getattr(self, "_termination_reason"):
            benefit.termination_reason_id = int(self._termination_reason)
        if getattr(self, "_after_organ"):
            benefit.after_organ_id = int(self._after_organ)

        benefit.save()

    def validate(self):
        if not getattr(self, "_termination_reason", False):
            raise Exception("Informe o Motivo do Término.")

    @transaction.atomic
    def save(self, *args, **kwargs):
        self.validate()
        self.set_tipo_desligamento()
        self.set_termination_benefit_fields()

        super().save(*args, **kwargs)


class SituacaoFuncional(AuditTimestampModel):
    class Meta:
        verbose_name = "Situação funcional"
        unique_together = (
            "servidor",
            "situacao",
            "data_inicio",
            "content_type",
            "objeto_pk",
        )

    servidor = models.ForeignKey(
        Servidor, on_delete=models.PROTECT, related_name="historico_situacao_funcional"
    )
    situacao = models.CharField(
        max_length=30, default="ATIVO", choices=list(SITUACAO_FUNCIONAL.items())
    )
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True)
    data_alteracao = models.DateField(auto_now_add=True)
    content_type = models.ForeignKey(ContentTypeDjango, on_delete=models.CASCADE)
    objeto_pk = models.PositiveIntegerField()
    classe_origem = generic.GenericForeignKey("content_type", "objeto_pk")
    active = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return format_situacao_funcional(self.situacao)

    def __unicode_full__(self):
        return "%s de %s -> %s: %s" % (
            self,
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "-----------",
            "VIGENTE" if self.ativo() else "FINALIZADO",
        )

    @transaction.atomic
    def save(self, *args, **kargs):
        self.active = is_active(date_start=self.data_inicio, date_end=self.data_fim)
        super(SituacaoFuncional, self).save(*args, **kargs)

    @transaction.atomic
    def delete(self, *args, **kargs):
        super(SituacaoFuncional, self).delete(*args, **kargs)

    @classmethod
    def _get_from_model(cls, model, pk=[]):
        """
        :py:function:: _get_from_model(cls, model, pk)

        This method returns SituacaoFuncional instance. Uses model and pk to search a valid answer.

        :param str model: str representation of the model
        :param list pk: list pk identification of the model
        :raises Exception: Raise exception when model or pk is not set
        :return: SituacaoFuncional situation found from get
        :rtype: SituacaoFuncional
        """
        return SituacaoFuncional.objects.filter(
            content_type__in=ContentTypeDjango.objects.filter(model=model).values("pk"),
            objeto_pk__in=pk,
        )

    @classmethod
    def _validate(cls, instance=None):
        valid = True
        if (
            isinstance(instance, MovimentacaoPosse)
            and instance.base_posse()
            and instance.has_specialized_possession
        ):
            log.info(
                "SitucaoFuncional %s não realiza para base posse quando possuir especialização"
                % instance
            )
            valid = False
        elif hasattr(instance, "alteracao") and instance.alteracao in (
            CANCELED,
            SUSPENSION,
        ):
            log.info(
                "SitucaoFuncional %s não realiza para CANCELADO OU SUSPENSO" % instance
            )
            valid = False
        return valid

    @classmethod
    def _get(cls, employee=None, situation=None, date_start=None, instance=None):
        """
        :py:function:: _get(cls, employee=None, situation=None, date_start=None, instance=None)

        This method returns SituacaoFuncional instance. Base on paremeters informed.

        :param Servidor employee: employee
        :param str situation: str situation
        :param date date_start: date start
        :param Model instance: Model instance
        :return: SituacaoFuncional situation found from get
        :rtype: SituacaoFuncional
        """
        return SituacaoFuncional.objects.filter(
            servidor=employee,
            data_inicio=date_start,
            situacao=situation,
            content_type__pk__in=ContentTypeDjango.objects.filter(
                model=instance.__class__.__name__.lower()
            ).values("pk"),
            objeto_pk=instance.pk,
        ).last()

    @classmethod
    def _remove_duplicate(cls, model, pk):
        """
        :py:function:: _remove_duplicate(cls, model, pk)

        This method may deletes the funcional status instance. Base on paremeters informed.

        :param str model: str model
        :param int pk: int pk
        """
        SituacaoFuncional.objects.filter(
            content_type__in=ContentTypeDjango.objects.filter(model=model).values("pk"),
            objeto_pk=pk,
        ).delete()

    @classmethod
    def create_functional_status(
        cls,
        employee=None,
        situation=None,
        date_start=None,
        date_end=None,
        instance=None,
    ):
        """
        :py:function:: create_functional_status(
            cls, employee=None, situation=None, date_start=None, date_end=None, instance=None)

        This method returns SituacaoFuncional instance. Base on paremeters informed.

        :param Servidor employee: employee
        :param str situation: str situation
        :param date date_start: date start
        :param date date_end: date end
        :param Model instance: Model instance
        :return: SituacaoFuncional functional_status created or that was found
        :rtype: SituacaoFuncional
        :raises Exception: Raise exception if someone is not set
        """
        functional_status = None
        if SituacaoFuncional._validate(instance):
            functional_status = SituacaoFuncional._do_create(
                employee, situation, date_start, date_end, instance
            )
            SituacaoFuncional.run_updates(
                employee, situation, date_start, date_end, instance
            )
        return functional_status

    @classmethod
    def _do_create(
        cls,
        employee=None,
        situation=None,
        date_start=None,
        date_end=None,
        instance=None,
    ):
        """
        :py:function:: _do_create(cls, employee=None, situation=None, date_start=None, date_end=None, instance=None)

        This method creates SituacaoFuncional instance. Base on paremeters informed.

        :param Servidor employee: employee
        :param str situation: str situation
        :param date date_start: date start
        :param date date_end: date end
        :param Model instance: Model instance
        :return: SituacaoFuncional functional_status created or that was found
        :rtype: SituacaoFuncional
        :raises Exception: Raise exception if someone is not set
        """
        functional_status = None
        try:
            functional_status = SituacaoFuncional._get(
                employee, situation, date_start, instance
            )
            if functional_status is None:
                SituacaoFuncional._remove_duplicate(
                    instance.__class__.__name__.lower(), instance.pk
                )
                functional_status = SituacaoFuncional(
                    servidor=employee,
                    data_inicio=date_start,
                    data_fim=date_end,
                    situacao=situation,
                    classe_origem=instance,
                )
                functional_status.save()
                log.debug(
                    "Situação Funcional %s do Servidor %s criada com sucesso."
                    % (situation, employee)
                )
            elif functional_status.data_fim != date_end:
                functional_status.data_fim = date_end
                log.debug(
                    "Situação Funcional %s do Servidor %s mudou a data fim de %s para %s."
                    % (
                        situation,
                        employee,
                        (
                            DateUtils.date_to_str(functional_status.data_fim)
                            if functional_status.data_fim
                            else "----"
                        ),
                        DateUtils.date_to_str(date_end) if date_end else "----",
                    )
                )
                functional_status.save()
        except IntegrityError as err:
            log.exception(err)
            log.debug(
                "Situação Funcional %s do Servidor %s já foi criada."
                % (situation, employee)
            )
        except Exception as err:
            log.exception(err)
            log.debug(
                "Situação Funcional %s do Servidor %s não foi criada no dia %s"
                % (situation, employee, DateUtils.date_to_str(datetime.now().date()))
            )
        return functional_status

    @classmethod
    def delete_functional_status(
        cls,
        employee=None,
        situation=None,
        date_start=None,
        date_end=None,
        instance=None,
    ):
        """
        :py:function:: delete_functional_status(
            cls, employee=None, situation=None, date_start=None, date_end=None, instance=None)

        This method deletes SituacaoFuncional instance. Base on paremeters informed.

        :param Servidor employee: employee
        :param str situation: str situation
        :param date date_start: date start
        :param Model instance: Model instance
        """
        try:
            for functional_status in SituacaoFuncional._get_from_model(
                instance.__class__.__name__.lower(), [instance.pk]
            ):
                functional_status.delete()
                SituacaoFuncional.run_updates(
                    employee, situation, date_start, date_end, instance, created=False
                )
        except Exception as err:
            log.exception(err)
            log.info("Não apagou a Situação Funcional.")

    @classmethod
    def run_updates(
        cls,
        employee=None,
        situation=None,
        date_start=None,
        date_end=None,
        instance=None,
        created=True,
    ):
        """
        :py:function:: run_updates(
            cls, employee=None, situation=None, date_start=None, date_end=None, instance=None, created=True)

        This method updates functional status from possessions and possessions fired.
        Also calls update_functional_status_effective to update situacao_funcional_cache at Servidor.
        Base on paremeters informed.

        :param Servidor employee: employee
        :param str situation: str situation
        :param date date_start: date start
        :param date date_end: date end
        :param Model instance: Model instance
        :param bool created: created default is True
        """
        if SituacaoFuncional.is_fired_possessions(instance):
            SituacaoFuncional._update_functional_status_possession(
                instance, created=created
            )
        elif SituacaoFuncional.is_possessions(instance):
            SituacaoFuncional._update_functional_status_possession_fired(
                instance, date_start, created=created
            )
        return True

    @classmethod
    def is_fired_possessions(cls, instance):
        """
        :py:function:: is_fired_possessions(cls, instance)

        This method indentifies instance as fired ou retirement.

        :param Model instance: Model instance
        :return: bool
        :rtype: bool
        """
        return isinstance(instance, MovimentacaoDesligamento) or isinstance(
            instance, MovimentacaoAposentadoria
        )

    @classmethod
    def is_possessions(cls, instance):
        """
        :py:function:: is_possessions(cls, instance)

        This method indentifies instance as possessions.

        :param Model instance: Model instance
        :return: bool
        :rtype: bool
        """
        return (
            isinstance(instance, MovimentacaoPosse)
            or isinstance(instance, MovimentacaoRemocaoMembro)
            or isinstance(instance, MovimentacaoPromocao)
            or isinstance(instance, MovimentacaoReadaptacao)
            or isinstance(instance, MovimentacaoReintegracao)
            or isinstance(instance, MovimentacaoReconducao)
            or isinstance(instance, MovimentacaoReversao)
            or isinstance(instance, RequestMove)
            or isinstance(instance, PossessionTrainee)
            or isinstance(instance, PossessionCollaborator)
            or isinstance(instance, BenefitMovement)
            or isinstance(instance, MovimentacaoAproveitamento)
        )

    @classmethod
    def _update_functional_status_possession(cls, fired, created=True):
        """
        :py:function:: _update_functional_status_possession(cls, fired, created=True):

        This method updates the funcional status of the possession.

        :param (MovimentacaoDesligamento, MovimentacaoAposentadoria) fired: Model fired
        :param bool created:
        """
        try:
            for functional_status in SituacaoFuncional._get_from_model(
                fired.movimentacao_posse.instancia_modelo.__class__.__name__.lower(),
                [fired.movimentacao_posse.pk],
            ):
                date_end = None
                if created:
                    date_end = fired.data_desligamento - relativedelta(days=1)
                    date_end = (
                        date_end
                        if functional_status.data_inicio <= date_end
                        else fired.data_desligamento
                    )
                functional_status.data_fim = date_end
                if (
                    functional_status.data_inicio == functional_status.data_fim
                    and fired.data_desligamento == functional_status.data_fim
                ):
                    functional_status.delete()
                else:
                    functional_status.save()
            else:
                log.info(
                    "Não existe Situação Funcional da posse %s."
                    % fired.movimentacao_posse.instancia_modelo
                )
        except Exception as err:
            log.exception(err)

    @classmethod
    def _update_functional_status_possession_fired(
        cls, instance, date_start, created=True
    ):
        """
        :py:function:: _update_functional_status_possession_fired(cls, instance, date_start, created=True):

        This method updates the funcional status of the possession fired.

        :param Model instance: Model instance
        :param date date_start: date start
        :param bool created:
        """
        try:
            date_end = date_start - relativedelta(days=1)
            fired_situations_pk = []
            if (
                hasattr(instance, "desligamento")
                and SituacaoFuncional.objects.filter(
                    Q(servidor=instance.servidor)
                    & Q(data_inicio__gte=date_start)
                    & Q(situacao="ATIVO")
                ).exists()
            ):
                fired_situations_pk.append(instance.desligamento.pk)

            if len(fired_situations_pk) > 0:
                fired_situations = SituacaoFuncional._get_from_model(
                    "movimentacaodesligamento", fired_situations_pk
                )
            else:
                fired_situations = SituacaoFuncional.objects.filter(
                    Q(data_inicio__lte=date_start)
                    & Q(servidor=instance.servidor)
                    & Q(situacao__icontains="INATIVO")
                )
                if created:
                    fired_situations = fired_situations.filter(data_fim=None)

            for fired_st in fired_situations.order_by("data_inicio"):
                if created:
                    date_end = (
                        date_end if fired_st.data_inicio <= date_end else date_start
                    )
                else:
                    date_end = None
                if fired_st.data_fim != date_end:
                    fired_st.save()
        except Exception as err:
            log.exception(err)

    @classmethod
    def prepare_parameter_functional_status(cls, origin_instance):
        """
        Este método deverá preparar os valores para os métodos
        create_functional_status e apagar_situacao_funcional
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        date_start = None
        date_end = None

        situation = origin_instance.situacao_funcional
        employee = origin_instance.servidor
        if isinstance(origin_instance, BaseLicencaAfastamento):
            date_start = origin_instance.data_inicio
            date_end = origin_instance.data_fim
            origin_instance = origin_instance.instancia_modelo
        elif SituacaoFuncional.is_possessions(origin_instance):
            date_start = origin_instance.data_exercicio
            if (
                hasattr(origin_instance, "desligamento")
                and origin_instance.desligamento
            ):
                date_end = origin_instance.desligamento.data_desligamento
        elif isinstance(origin_instance, DeclaracaoAtividade):
            date_start = origin_instance.data_exercicio
            date_end = origin_instance.data_encerramento
        # elif isinstance(origin_instance, DeclarationActivityRetiree):
        #     date_start = origin_instance.data_inicio
        #     date_end = origin_instance.data_encerramento
        elif isinstance(origin_instance, MovimentacaoDesligamento) or isinstance(
            origin_instance, MovimentacaoAposentadoria
        ):
            date_start = origin_instance.data_desligamento
            possessions = MovimentacaoPosse.objects.filter(
                Q(servidor=origin_instance.servidor)
                & (
                    Q(data_exercicio__gte=origin_instance.data_desligamento)
                    | Q(data_desligamento=None)
                )
            )
            if possessions.exists():
                possessions = possessions.first()
                date_end = (
                    possessions.data_exercicio
                    if possessions.data_exercicio >= date_start
                    else date_start
                )
        return employee, date_start, date_end, situation, origin_instance

    @classmethod
    def update_from_origin(cls, registry=None):
        """
        :py:function:: update_from_origin(cls)

        This method updates the functional status of Employees or all of situations that ends today and yesterday.

        """
        query = SituacaoFuncional.objects.filter(data_fim=None)
        if registry:
            query = query.filter(servidor__matricula=registry)
        count = 1
        total = query.count()
        for st in query.order_by("servidor", "-data_inicio"):
            model = apps.get_model(st.content_type.app_label, st.content_type.model)
            log.info(
                "Atualizando situação que não possui data fim %s => %s" % (count, total)
            )
            count += 1
            if model and model != "NoneType" and st.objeto_pk:
                try:
                    instance = model.objects.get(pk=st.objeto_pk).instancia_modelo
                    employee, date_start, date_end, situation, instance = (
                        SituacaoFuncional.prepare_parameter_functional_status(instance)
                    )
                    SituacaoFuncional.create_functional_status(
                        employee=employee,
                        date_start=date_start,
                        date_end=date_end,
                        situation=situation,
                        instance=instance,
                    )
                except ObjectDoesNotExist:
                    SituacaoFuncional.objects.filter(pk=st.pk).delete()
                except Exception as err:
                    log.exception(err)

        def __update_from_possession(registry=None):
            query = MovimentacaoPosse.objects.filter(ativo=True)
            if registry:
                query = query.filter(servidor__matricula=registry)
            count = 1
            total = query.count()
            for possession in query.order_by("servidor", "-data_exercicio"):
                log.info(
                    "Atualizando situação funcional a partir de posses ativas %s => %s"
                    % (count, total)
                )
                count += 1
                try:
                    employee, date_start, date_end, situation, possession = (
                        SituacaoFuncional.prepare_parameter_functional_status(
                            possession.instancia_modelo
                        )
                    )
                    SituacaoFuncional.create_functional_status(
                        employee=employee,
                        date_start=date_start,
                        date_end=date_end,
                        situation=situation,
                        instance=possession,
                    )
                except Exception as err:
                    log.exception(err)

        __update_from_possession(registry=registry)

    def _check_validity(self, applicable_conditions=None):
        """
        :py:function:: _check_validity(self, applicable_conditions=None)

        This method checks the validity of the functional status based on applicable_conditions.

        Take applicable_conditions:
            {
                'name': 'INACTIVE_SITUATIONS',
                'situations': INACTIVE_SITUATIONS_RAW,
                'validity': ANYWAY,
                'applicable': True
            }
            'name' => group to go situations
            'situations' => list of situations to go
            'validity' => validity required for group situations
            'applicable' => applicable value when validity is satisfied

            and check if 'situations' is correspondent to 'validity' and set 'applicable'.

        If applicable is defined as False then decision will be False.

        Analyzes if its is active.

        Then returns active and decision.

        :param applicable_conditions applicable_conditions: applicable_conditions is described at
        constants_functional_situations module like,
            * ACTIVE_SITUATIONS;
            * DEPARTURE_SITUATIONS;
            * INACTIVE_SITUATIONS;
            * NOT_APPLICABLE_SITUATIONS;
        :return: bool: active and decision of the checks
        :rtype: bool
        """
        if not applicable_conditions:
            applicable_conditions = SITUATION_APPLICABLE(
                FUNCTIONAL_STATE_INDEX_STR_TO_INT.get(self.situacao)
            )
        active = is_active(date_start=self.data_inicio, date_end=self.data_fim)
        decision = True
        if not isinstance(applicable_conditions, bool):
            decision = self._checks_applicable_conditions(applicable_conditions)
        else:
            decision = applicable_conditions
        return active and decision

    def _checks_applicable_conditions(self, applicable_conditions):
        """
        :py:function:: _checks_applicable_conditions(self, applicable_conditions)

        This method runs all of applicable_conditions to check if they satisfy the rules.

        :param list applicable_conditions: list of applicable_conditions
        :return: bool, applicable:
        :rtype: bool
        """
        applicable = True
        for app in applicable_conditions:
            if not SituacaoFuncional.__appplicable(self.servidor, app):
                applicable = False
                break
        return applicable

    @classmethod
    def __appplicable(cls, employee, condition):
        """
        :py:function:: __appplicable(cls, employee, condition)

        This method checks if the situations satisfy the rules and are applicable.

        :param Employee employee:
        :param dict condition: like
            {
                'name': 'INACTIVE_SITUATIONS',
                'situations': INACTIVE_SITUATIONS_RAW,
                'validity': ANYWAY,
                'applicable': True
            }
        :return: bool, applicable
        :rtype: bool
        """
        validity = condition.get("validity")
        applicable = condition.get("applicable")
        if validity != ANYWAY:
            check_validity = SituacaoFuncional.__check_situations_validity(
                employee, condition.get("situations")
            )
            if (validity == VALIDITY and not check_validity) or (
                validity == NOT_VALIDITY and check_validity
            ):
                applicable = not applicable
        return applicable

    @classmethod
    def __check_situations_validity(cls, employee, situations):
        """
        :py:function:: __check_situations_validity(cls, employee, situations)

        This method checks the validity(considering today) of the functional status based on situations parameter
        for the employee supplied.
        Returns True if found something.

        :param Employee employee:
        :param list situations: List of situations is described at constants_functional_situations module like,
            * ACTIVE_SITUATIONS;
            * DEPARTURE_SITUATIONS;
            * INACTIVE_SITUATIONS;
            * NOT_APPLICABLE_SITUATIONS;
        :return: bool: if exists someone
        :rtype: bool:
        """
        today = datetime.now().date()
        query = (
            Q(servidor=employee)
            & Q(
                situacao__in=list(
                    INVERT_IF_IN(FUNCTIONAL_STATE_INDEX_STR_TO_INT, situations).values()
                )
            )
            & (Q(data_inicio__lte=today) & (Q(data_fim__gte=today) | Q(data_fim=None)))
        )
        return SituacaoFuncional.objects.filter(query).exists()

    def set_functional_status(self):
        """
        :py:function:: set_functional_status(self)

        This method sets the functional_status valid.
        Returns True if there validity and can set the value.

        :return: bool
        :rtype: bool
        """
        if self._check_validity():
            return self.servidor.set_functional_status(self.situacao)
        return False

    def ativo(self, hoje=None):
        """
        Este método verifica se a situação funcional está ativa.
        """
        return is_active(
            today=hoje, date_start=self.data_inicio, date_end=self.data_fim
        )

    @classmethod
    def _manager_situations(cls, employee=None, date=None):
        active_status = (
            ACTIVE_SITUATIONS_STR
            + DEPARTURE_SITUATIONS_STR
            + NOT_APPLICABLE_SITUATIONS_STR
        )
        date = datetime.now().date() if not date else date
        qdates = Q(data_inicio__lte=date) & Q(Q(data_fim__gte=date) | Q(data_fim=None))
        sts = SituacaoFuncional.objects.filter(qdates)
        if not employee:
            employees = sts.values("servidor__pk")
            employees = Servidor.objects.filter(pk__in=employees)
        else:
            employees = Servidor.objects.filter(pk=employee.pk)

        count = 1
        total = employees.count()
        for employee in employees:
            log.info(
                "Organizando situação funcional do servidor %s %s => %s"
                % (employee, count, total)
            )
            count += 1
            situacao_funcional_cache = employee.situacao_funcional_cache
            sts_employee = sts.filter(servidor=employee)
            employee_active = employee.ativo
            to_set = None
            sort = "-data_inicio" if employee_active else "-created_at"

            for st in sts_employee.order_by(sort):
                if str(st.situacao) in INACTIVE_SITUATIONS_STR and (
                    not sts_employee.exclude(situacao__in=active_status).exists()
                    or not employee_active
                ):
                    to_set = str(st.situacao)
                    break
                elif (
                    str(st.situacao) in ACTIVE_SITUATIONS_STR
                    and employee_active
                    and st.active
                    and not sts_employee.exclude(situacao__in=ACTIVE_SITUATIONS_STR)
                    .exclude(
                        situacao__in=DEPARTURE_SITUATIONS_STR
                        + NOT_APPLICABLE_SITUATIONS_STR,
                        active=False,
                    )
                    .exists()
                ):
                    to_set = str(st.situacao)
                    break
                elif (
                    str(st.situacao)
                    in DEPARTURE_SITUATIONS_STR + NOT_APPLICABLE_SITUATIONS_STR
                    and employee_active
                    and st.active
                ):
                    to_set = str(st.situacao)
                    break

            if not to_set:
                if not sts_employee.exists():
                    to_set = (
                        str(
                            SituacaoFuncional.objects.filter(servidor=employee)
                            .last()
                            .situacao
                        )
                        if SituacaoFuncional.objects.filter(servidor=employee).exists()
                        else "NOT_FOUND"
                    )

            if to_set:
                employee.set_functional_status(to_set)

            new = Servidor.objects.get(pk=employee.pk).situacao_funcional_cache
            if situacao_funcional_cache != new:
                log.info(
                    "SITUAÇÃO FUNCIONAL: %s - %s => %s"
                    % (employee, situacao_funcional_cache, new)
                )

    @classmethod
    def cmd_update_active(cls, functional_status=[], all=False):
        """
        Este método é responsável por atualizar o campo ativo baseando-se na data de vigência.
        """
        today = datetime.now().date()
        query = Q(data_fim__lt=today) | Q(data_fim=None) | Q(data_inicio=today)
        if all:
            query = Q()
        elif len(functional_status) > 0:
            query = Q(pk__in=functional_status)

        fss = SituacaoFuncional.objects.filter(query)
        log.info("SituacaoFuncional: quantidade para atualizar %s" % fss.count())
        for fs in fss.order_by("-data_inicio"):
            fs._update_active_cache()

    def _update_active_cache(self):
        try:
            if self.active != self.ativo():
                self.save()
        except Exception as err:
            log.exception(err)


class MovimentacaoSubstituicaoQuerySet(models.QuerySet):

    def validity_in(self, start_date, end_date=None):
        query = self.exclude(Q(data_fim__isnull=False) & Q(data_fim__lt=start_date))
        if end_date:
            query = query.exclude(data_inicio__gt=end_date)
        return query


class MovimentacaoSubstituicao(MovimentacaoPessoal):
    afastamento = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        null=True,
        on_delete=models.CASCADE,
        related_name="substituicao",
    )
    posse = models.ForeignKey(
        MovimentacaoPosse,
        related_name="substituicoes",
        null=True,
        on_delete=models.CASCADE,
    )
    servidor_substituido = models.ForeignKey(
        "Servidor",
        on_delete=models.CASCADE,
        verbose_name="Servidor substituído",
        blank=True,
        related_name="substituido",
    )
    data_inicio = models.DateField(verbose_name="Início")
    publicacao_fim = models.ForeignKey(
        Publicacao, null=True, blank=True, on_delete=models.PROTECT
    )
    data_prevista = models.DateField(
        null=True, blank=True, verbose_name="Data Prevista Fim"
    )
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    designation_substitute = models.ForeignKey(
        "ServidorLotacao",
        verbose_name="Designação substituto",
        related_name="substitution_substitute",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    designation_substituted = models.ForeignKey(
        "ServidorLotacao",
        verbose_name="Designação do substituído",
        related_name="substitution_substituted",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
    )
    ordinance = models.BooleanField(
        default=False, blank=True, verbose_name="Por portaria"
    )
    place = models.ForeignKey(
        "Lotacao",
        related_name="substitution_place",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    state = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "ESTADO_BASE_LICENCA_AFASTAMENTO"),
        blank=True,
        db_index=True,
    )
    status_change_date = models.DateField(
        null=True,
        blank=True,
        help_text="Será gravado quando o estado mudar para ATIVO, FINALIZADO",
        verbose_name="Data de mudança de estado",
    )
    pay_month = models.PositiveIntegerField(
        "Mês de Pagamento",
        choices=Choice.get_choices_for("rh", "MONTHS"),
        null=True,
        blank=True,
    )
    pay_year = models.PositiveIntegerField("Ano de Pagamento", null=True, blank=True)
    gedoc = models.CharField(max_length=100, null=True, blank=True)
    payment_installments = models.IntegerField(
        "Parcelas de Pagamento", null=True, blank=True
    )
    able_to_pay = models.BooleanField("Apto a Pagamento", default=False, blank=True)
    consolidated = models.BooleanField("Consolidado", default=False, blank=True)
    paid_out = models.BooleanField("Pago", default=False, blank=True)
    defer = models.BooleanField("Deferido", default=False, blank=True)
    financial_effect_date_start = models.DateField(
        verbose_name="Data Efeito Financeiro Início", null=True, blank=True
    )
    financial_effect_date_end = models.DateField(
        verbose_name="Data Efeito Financeiro Fim", null=True, blank=True
    )
    origin_register = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "ORIGIN_REGISTER"),
        verbose_name="Origem do registro",
    )
    retroativo = models.BooleanField("Retroativo", default=False, blank=True)
    indeferido = models.BooleanField("Indeferido", default=False, blank=True)
    periodo_cumul_subs = models.ForeignKey(
        "rh.ConfigPeriodoCumulativoSubstituicao",
        related_name="periodo_cumul_subs",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    usuario_nao_informa = []

    must_validate_document = True

    objects = MovimentacaoSubstituicaoQuerySet.as_manager()

    class Meta:
        verbose_name = "Movimentação de Substituição"
        db_table = "rh_movsubstituicao"
        ordering = ["-data_inicio"]

    class FinalizedErr(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Substituição finalizada.")
            )

    def __str__(self):
        return "%s a %s - %s" % (
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
            self.posse.quadro if self.posse is not None else "----",
        )

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.data_inicio, date_end=self.data_fim
        )

    @property
    def financial_date_start(self):
        if self.financial_effect_date_start:
            return DateUtils.date_to_str(self.financial_effect_date_start)
        else:
            return DateUtils.date_to_str(self.data_inicio)

    @property
    def financial_date_end(self):
        if self.financial_effect_date_end:
            return DateUtils.date_to_str(self.financial_effect_date_end)
        else:
            return DateUtils.date_to_str(self.data_fim)

    @property
    def instance_model(self):
        instance = self
        if hasattr(self, "movimentacaosubstituicaomembro"):
            instance = self.movimentacaosubstituicaomembro
        return instance

    @property
    def get_texto_servidor(self):
        return f"{self.servidor.matricula}: {self.servidor.pessoa_fisica.nome}"

    @property
    def get_texto_servidor_substituido(self):
        return f"{self.servidor_substituido.matricula}: {self.servidor_substituido.pessoa_fisica.nome}"

    @property
    def get_titularidade(self):
        lotacoes = ServidorLotacao.objects.filter(
            servidor=self.servidor, ativo=True, designacao=True
        )

        q = lotacoes.filter(main=True)
        if q.exists():
            return self.get_lotacao_from_q(q)

        q = lotacoes.filter(owner=True)
        if q.exists():
            return self.get_lotacao_from_q(q)

        return self.get_lotacao_from_q(q) if q.exists() else ""

    @property
    def get_cumulativa(self):
        if self.designation_substituted:
            return str(self.designation_substituted.lotacao)
        else:
            return ""

    @property
    def get_lotacao(self):
        return str(self.place)

    def get_lotacao_from_q(self, q):
        if q.count() == 1:
            q_lotacao = q.first().lotacao
            return str(q_lotacao) if q_lotacao else ""
        else:
            return str(self.get_lotacao_mais_antiga(q))

    def get_lotacao_mais_antiga(self, lotacoes):
        return lotacoes.order_by("data_vigencia_inicio").first()

    @property
    def workplace_job_position_responsible(self):
        return self.posse.quadro.cargo.lotacao_responsavel if self.posse else None

    @property
    def can_run_process(self):
        """Esta propriedade verifica retorna um boolean.
        True quando: status_change_date < today e estado for ativo, ou status_change_date igual a today e estado em
            ATIVO, FINALIZADO
        False nos outros casos
        """
        today = datetime.now().date()
        can = False
        if self.status_change_date:
            if self.status_change_date < today and self.state == ACTIVE:
                can = True
            elif self.status_change_date == today and self.state in (ACTIVE, FINISHED):
                can = True
        return can

    @classmethod
    def update_from_departure(cls, departure):
        """
        :py:function:: update_from_departure(cls, departure)

        This method updates MovimentacaoSubstituicao and MovimentacaoSubstituicaoMembro from departure changes.
        Organizes substitutions according its day of the begin. Deletes if necessary, when the departure was interrupted.

        :param BaseLicencaAfastamento instance: instance of BaseLicencaAfastamento especialized.
        """
        message = "Atualizando substituições do afastamento %s: %s" % (
            departure.servidor,
            departure,
        )
        log.info(message)
        if departure.data_fim:
            for substitution in departure.substituicao.filter().order_by("data_inicio"):
                message = ""
                try:
                    with transaction.atomic():
                        sub = substitution.instance_model
                        if (
                            departure.data_fim
                            and sub.data_inicio <= departure.data_fim
                            and (
                                sub.data_fim
                                and sub.data_fim > departure.data_fim
                                or not sub.data_fim
                            )
                        ):
                            message = "%s - Novo fim: %s" % (
                                sub,
                                (
                                    DateUtils.date_to_str(departure.data_fim)
                                    if departure.data_fim
                                    else "----"
                                ),
                            )
                            log.info(message)
                            sub.data_fim = departure.data_fim
                            sub.save()
                        elif (
                            departure.data_fim and sub.data_inicio > departure.data_fim
                        ):
                            message = (
                                "%s - Será apagada pois excede o período de fim do afastamento."
                                % sub
                            )
                            log.info(message)
                            sub.delete()
                except Exception as err:
                    log.exception(err)

    @classmethod
    def call_update_responsible_workplace(
        cls, instance=None, delete=False, date=None, lapse=1
    ):
        """
        :py:function:: call_update_responsible_workplace(cls, instance=None, delete=False, date=None)

        This method updates the responsible of the workplace calling Workplace.update_responsible(
            responsible_new=responsible_new).
        Sets the substitute as the new responsible for the workplace when periods starts.
        And when the periods ends the substituted come back to responsibility.
        If there are a member involved, his job position will determine witch workplace has to change.
        Otherwise, to normal employees the workplaces will be those under his responsibility.

        Parameter lapse is 1 has default value. It means that the interval will be 1 day before the date informed
        and 1 day after.

        :param (MovimentacaoSubstituicao, MovimentacaoSubstituicaoMembro)  instance: instance of
            MovimentacaoSubstituicao or MovimentacaoSubstituicaoMembro, default = None
        :param boolean delete: default False
        :param date date: default is today
        """
        log = getLogger("db")
        # TODO: OBSERVAR SE ESTE MÉTODO PRECISA DE UM COMMIT DE ISOLAÇÃO, POIS É CHAMADO COMO SINAL
        date = datetime.now().date() if not date else date
        lapse_day = date - relativedelta(days=lapse)
        log.info(
            """=> Executando comando para atualizar reponsável por lotação a partir da substituição.
            De %s a %s"""
            % (DateUtils.date_to_str(lapse_day), DateUtils.date_to_str(date))
        )
        if instance:
            substitutions = MovimentacaoSubstituicao.objects.filter(pk=instance.pk)
        else:
            substitutions = get_substituicoes(date=date, lapse=lapse)
            if substitutions.filter(designation_substituted__ativo=False).exists():
                for sub in substitutions.filter(designation_substituted__ativo=False):
                    notificar_nao_criacao_lotacao(sub)

            substitutions = substitutions.filter(designation_substituted__ativo=True)

        count = 1
        total = substitutions.count()
        log.info(
            "call_update_responsible_workplace ATUALIZANDO %s de %s... "
            % (count, total)
        )
        for substitution in substitutions.order_by("data_fim"):
            responsible_new = None
            responsible_old = None
            workplaces = Lotacao.objects.none()
            active = True
            if substitution.substituicao_finalizada() or delete:
                active = False
                workplaces = (
                    substitution.servidor_substituido.responsavel_substituido.filter()
                )
                responsible_new = substitution.servidor_substituido
                responsible_old = substitution.servidor
            elif (
                substitution.substituicao_iniciada()
                and not substitution.substituicao_finalizada()
            ):
                workplaces = substitution.servidor_substituido.responsavel_por.filter()
                responsible_new = substitution.servidor
                responsible_old = substitution.servidor_substituido

                workplaces = substitution._get_workplace_member(workplaces)

            log.info(
                "%s - ATUALIZANDO %s de %s... \n Novo: %s - Antigo: %s - Lotações(%s)"
                % (
                    substitution,
                    count,
                    total,
                    responsible_new,
                    responsible_old,
                    len(workplaces),
                )
            )

            cls._change_workplace_responsible(
                workplaces=workplaces,
                active=active,
                responsible_new=responsible_new,
                responsible_old=responsible_old,
            )

            cls._change_subordinate_chief_immediate(responsible_old=responsible_old)

            # chama da função que atualiza o aprodador das MovimentaacaoTeletrabalho
            # for workplace in workplaces:
            # workplace.update_telework_approver(responsible_new)
            count += 1
        return True

    def _get_workplace_member(self, workplaces):
        """
        :py:function:: _get_workplace_member(self, workplaces)

        This method gets only workplaces that matches job position for the member.

        :param (MovimentacaoSubstituicao, MovimentacaoSubstituicaoMembro) substitution: instance of
            MovimentacaoSubstituicao or MovimentacaoSubstituicaoMembro
        :param QuerySet workplaces:
        :return: workplaces
        :rtype: list
        """
        if (
            self.designation_substituted
            and self.designation_substituted.servidor.member_type_by_possession
        ):
            workplaces = workplaces.filter(pk=self.designation_substituted.lotacao)
        return workplaces

    @classmethod
    def _change_workplace_responsible(
        cls, workplaces=[], active=False, responsible_new=None, responsible_old=None
    ):
        """
        :py:function:: _change_workplace_responsible(
            cls, workplaces=[], active=False, responsible_new=None, responsible_old=None)

        This method calls workplace.update_responsible and sets responsible_substituted when active is True.
        Otherwise, change responsibility for the older.

        :param QuerySet workplaces:
        :param boolean active: default False
        :param Servidor responsible_new: New responsible
        :param Servidor responsible_old: Old responsible
        """
        if responsible_new:
            for workplace in workplaces:
                if active:
                    ServidorLotacao.objects.filter(
                        servidor=responsible_old, lotacao=workplace, ativo=True
                    ).update(responsible=False, from_substitution=False)
                    Lotacao.objects.filter(pk=workplace).update(
                        responsible_substituted=responsible_old
                    )
                    workplace.update_responsible(responsible_new=responsible_new)
                elif responsible_new == workplace.responsible_substituted:
                    ServidorLotacao.objects.filter(
                        servidor=responsible_new, lotacao=workplace, ativo=True
                    ).update(responsible=True, from_substitution=False)
                    ServidorLotacao.objects.filter(
                        servidor=responsible_old, lotacao=workplace
                    ).update(
                        responsible=False
                    )  # Removido from_substitution=True
                    Lotacao.objects.filter(pk=workplace).update(
                        responsible_substituted=None
                    )
                    workplace.update_responsible(responsible_new=responsible_new)
        else:
            log.info("Responsável não foi informado.")

    @classmethod
    def _change_subordinate_chief_immediate(cls, responsible_old=None):
        """
        :py:function:: _change_subordinate_chief_immediate(cls, responsible_old=None)

        This method finds the suborndinates and calls
            employee_workplace.servidor.update_chief_immediate(mandatory=True).

        :param Servidor responsible_old: Old responsible
        """
        if responsible_old:
            for employee in Servidor.objects.filter(
                pk__in=ServidorLotacao.work_assignment_exercise()
                .filter(ativo=True, servidor__chefe_imediato=responsible_old)
                .values("servidor__pk")
            ):
                employee.update_chief_immediate(mandatory=True)
        else:
            log.info(
                "Subordinados não encontrados, pois responsável não foi informado."
            )

    @staticmethod
    def get_departamento(servidor):
        try:
            return servidor.responsavel_por.get()
        except Exception:
            return servidor.work_locations.filter(
                servidores_lotacao__ativo=True,
                servidores_lotacao__designacao=False,
                organograma=True,
            )[0]

    def substituicao_iniciada(self):
        """
        Este método verifica se a substituição foi iniciada.
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        data_inicio, data_fim = self.data_inicio, self.data_fim
        if self.pk is not None:
            data_inicio, data_fim = (
                self.get_self().data_inicio,
                self.get_self().data_fim,
            )
        return BaseLicencaAfastamento._iniciado(data_inicio, data_fim)

    def substituicao_finalizada(self):
        """
        Este método verifica se a substituição foi finalizada.
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        data_fim = self.data_fim
        if self.pk:
            data_fim = self.get_self().data_fim
        return BaseLicencaAfastamento._finalizado(date_end=data_fim)

    def validate(self):
        """ "
        Faz validações da substituição.
        """
        # self.validate_intervalo_pertence_afastamento()
        self.validate_employee()
        self.validate_employee_possession()
        self.validate_data_prevista()
        self.validate_publicacao()
        self.validate_data_inicio_maior_data_fim()
        self.validate_periodo()
        self.validate_substitute_departured()
        self.validate_cant_change_substitute()
        self.validate_pay_period_fields_relation()
        self.validate_pay_year_is_int()
        self.validate_pay_year_values()

        if self.pk:
            self.validate_if_can_update()
            self.validate_if_financial_fields_changed()

        if not self.servidor_substituido.member_type_by_possession:
            self.validate_data_fim()
            self.validate_conflito_substituido()
            self.validate_replaceable()
            self.validate_conflito()

        self.validar_pagamento_retroativo()
        return True

    def validate_if_financial_fields_changed(self):
        mov_sub = MovimentacaoSubstituicao.objects.get(pk=self.pk)
        if (self.consolidated or self.paid_out) and (
            self.financial_effect_date_start != mov_sub.financial_effect_date_start
            or self.financial_effect_date_end != mov_sub.financial_effect_date_end
        ):
            raise Exception(
                """
            Não é permitido alterar as datas de efeito financeiro de início ou fim se a Movimentação
            estiver 'Consolidada' ou 'Paga'.
            """
            )

    def validate_if_can_update(self):
        if self.pk:
            mov_sub = MovimentacaoSubstituicao.objects.get(pk=self.pk)
            if mov_sub.consolidated or mov_sub.paid_out:
                raise Exception(
                    """
                Não é permitido alterar as informações se a Movimentação estiver 'Consolidada' ou 'Paga'.
                """
                )

    def validate_pay_period_fields_relation(self):
        if self.pay_year and self.pay_month is None:
            raise Exception(
                "Você preencheu o Ano de Pagamento, com isso o campo Mês de Pagamento é obrigatório."
            )

        if self.pay_month and self.pay_year is None:
            raise Exception(
                "Você preencheu o Mês de Pagamento, com isso o campo Ano de Pagamento é obrigatório."
            )

    def validate_pay_year_is_int(self):
        if self.pay_year:
            try:
                int(self.pay_year)
            except:
                raise Exception(
                    "Valor do campo Ano de Pagamento é inválido. Deve ser apenas números."
                )

    def validate_pay_year_values(self):
        min_year = date.today().year - 5
        max_year = date.today().year + 5
        if self.pay_year and (self.pay_year < min_year or self.pay_year > max_year):
            raise Exception(
                f"Valor do campo de Pagamento é inválido. Deve ser entre {min_year} e {max_year}"
            )

    def validate_cant_change_substitute(self):
        if (
            self.pk
            and self.old_fields.get("servidor_id", False)
            and (self.substituicao_finalizada() or self.substituicao_iniciada())
        ):
            raise Exception(
                "Não é possível alterar o substituto, tente remover e adicionar novamente."
            )
        return True

    def validate_substitute_departured(self):
        try:
            ServidorLotacao._validate_employee_departured(
                employee=self.servidor,
                start_date=self.data_inicio,
                end_date=self.data_fim,
            )
        except Exception as err:
            raise err
        return True

    def validate_employee(self):
        if self.servidor_substituido != self.afastamento.servidor:
            raise Exception(
                "O Servidor substituído deve ser o mesmo escolhido no afastamento."
            )
        if self.posse and self.servidor_substituido != self.posse.servidor:
            raise Exception(
                "O Servidor substituído deve ser o mesmo escolhido na posse."
            )
        return True

    def validate_employee_possession(self):
        if (
            self.servidor_substituido
            and self.posse
            and self.servidor_substituido != self.posse.servidor
        ):
            raise Exception("A posse deve pertencer ao servidor afastado.")
        if not self.posse:
            raise Exception("Posse não informada.")

    def validate_data_prevista(self):
        if (
            self.publicacao_alteracao
            and self.data_prevista
            and self.data_fim
            and self.data_fim == self.data_prevista
        ):
            raise Exception(
                "Quando houver Documento de Revogação/Alteração a Data Fim deve ser diferente da Data Prevista."
            )
        if self.data_fim and not self.data_prevista:
            raise Exception(
                "Quando houver Data Fim a Data Prevista deve ser preenchida."
            )
        return True

    def validate_intervalo_pertence_afastamento(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        if not self.afastamento:
            raise Exception("Afastanento não informado.")
        if not BaseLicencaAfastamento._intervalo_pertence_afastamento(
            self.afastamento, self.data_inicio, self.data_fim
        ):
            raise Exception(
                "Substituição %s a %s, do(a) %s, não pertence à %s."
                % (
                    DateUtils.date_to_str(self.data_inicio),
                    DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
                    self.servidor,
                    "%s de %s a %s"
                    % (
                        self.afastamento,
                        DateUtils.date_to_str(self.afastamento.data_inicio),
                        (
                            DateUtils.date_to_str(self.afastamento.data_fim)
                            if self.afastamento.data_fim
                            else "----"
                        ),
                    ),
                )
            )
        return True

    def validate_publicacao(self):
        if not self.must_validate_document:
            return True

        if not self.publicacao_movimentacao:
            raise Exception("É necessário que a publicação seja preenchida.")
        if (
            self.publicacao_movimentacao
            and self.publicacao_movimentacao.data_vigencia is None
        ):
            raise Exception(
                "É necessário que Data de Vigência do Documento seja preenchido."
            )
        return True

    def validate_data_fim(self):
        if not self.data_fim:
            raise Exception("Data de fim é obrigatória.")
        return True

    def validate_data_inicio_maior_data_fim(self):
        if self.data_fim and self.data_inicio > self.data_fim:
            raise Exception(
                "Ocorreu um problema validando as datas. Corrija a ordem das datas."
            )
        return True

    def validate_conflito_substituido(self):
        if self.servidor_substituido == self.servidor:
            raise Exception("Um servidor não pode substituir a si mesmo.")
        return True

    def validate_replaceable(self):
        """
        :py:function:: validate_replaceable(self)

        This method validates if exists a replaceable.

        :return: boolean
        :rtype: True
        """
        if not self.posse:
            raise Exception("Por favor, escolha uma posse para validar a substituição.")

        if not is_active(
            today=self.data_fim,
            date_start=self.posse.data_exercicio,
            date_end=self.posse.data_desligamento,
        ):
            raise Exception(
                "Favor verificar as datas: Fim da substituição, Exercício da posse e Desligamento da posse!"
            )

        if not self.pk and (
            (
                self.posse.quadro.cargo.current_config
                and not self.posse.quadro.cargo.current_config.replaceable
            )
            and self.afastamento.tipo != 12  # Licença Maternidade
        ):
            raise Exception("O cargo %s não é substituível." % self.posse)
        return True

    def validate_conflito(self):
        """
        Valida se existe o cargo de chefia pode sofrer substituição.
         * Checa se a nova substituicao não começa dentro de uma substituição.
         * Checa se a nova substituicao não termina dentro de outra substituiçao.
        """
        query = Q(data_inicio__lte=self.data_inicio, data_fim__gte=self.data_inicio)
        if self.data_fim:
            query = Q(data_inicio__lte=self.data_fim, data_fim__gte=self.data_fim) | Q(
                data_inicio__gt=self.data_inicio, data_fim__lt=self.data_fim
            )
        query = self.posse.substituicoes.filter(query).exclude(pk=self.pk)
        if query.exists():
            raise Exception(
                "Esta substituicão conflita com outra substituição, onde o substituto é o servidor %s."
                % (query[0].servidor.pessoa_fisica)
            )
        return True

    def validate_substituicao_iniciada(self):
        """
        Este valida se a substituição já foi iniciada.
        """
        if self.substituicao_iniciada():
            raise Exception("Substituição iniciada.")
        return True

    def validar_pagamento_retroativo(self):
        hoje = datetime.today().date()

        if self.pay_month and self.pay_year and not self.paid_out or self.indeferido:

            if self.pay_month < hoje.month and self.pay_year <= hoje.year:
                self.paid_out = True
                self.retroativo = True
                return True
            else:
                self.paid_out = True
                return True

    def validate_periodo(self):
        return True

    def get_self(self):
        """
        Este método retorna a instância do objeto.
        """
        base = None
        try:
            base = MovimentacaoSubstituicao.objects.get(pk=self.pk)
        except Exception:
            pass
        return base

    def anotacao(self, *args, **kargs):
        texto_substituicao = self.get_texto_substituicao()
        if self.servidor_substituido.member_type_by_possession:
            texto_substituicao = self.get_texto_substituicao_membro()
        tipo = Publicacao.get_tipo(self.publicacao_movimentacao)

        if self.anotacao_geral is None:
            anotacao_geral = AnotacaoGeral.manage_instance(
                servidor=self.servidor,
                tipo_documento=tipo,
                publicacao=self.publicacao_movimentacao,
                data_portaria_inicio=self.data_inicio,
                texto=texto_substituicao,
                resumo="SUBSTITUIÇÃO",
            )
            self.anotacao_geral = anotacao_geral
        else:
            anotacao_geral = AnotacaoGeral.objects.get(pk=self.anotacao_geral.pk)
            anotacao_geral.servidor = self.servidor
            anotacao_geral.publicacao = self.publicacao_movimentacao
            anotacao_geral.data_portaria_inicio = self.data_inicio
            anotacao_geral.texto = texto_substituicao
            anotacao_geral.indireto = False
            anotacao_geral.save()
            AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)

    @transaction.atomic
    def delete(self, *args, **kargs):
        if self.consolidated or self.paid_out:
            raise Exception(
                "Não é permitido apagar se a Movimentação estiver 'Consolidada' ou 'Paga'."
            )
        else:
            MovimentacaoSubstituicao().call_update_responsible_workplace(
                self, delete=True
            )
            if self.servidor_substituido.member_type_by_possession:
                self.validate_delete_membro()
            if (
                self.designation_substitute
                and self.designation_substitute.created_by_departure
            ):
                self.designation_substitute.delete()
            super(MovimentacaoSubstituicao, self).delete(*args, **kargs)

    def validate_delete_membro(self):
        return True

    def apply_possession(self):
        if (
            not self.posse
            and self.afastamento.servidor
            and self.afastamento.servidor.posses_ativas.filter(
                quadro__cargo__configs__replaceable=True,
                quadro__cargo__configs__active=True,
            ).exists()
        ):
            self.posse = self.afastamento.servidor.posses_ativas.filter(
                quadro__cargo__configs__replaceable=True,
                quadro__cargo__configs__active=True,
            ).latest("data_exercicio")

    def define_state(self):
        """Este método define o state atual da substituição.

        Returns:
            state(int):
        """
        today = datetime.now().date()
        state = SCHEDULED
        active = self.is_active()
        if active:
            state = ACTIVE
        elif self.data_fim and self.data_fim < today:
            state = FINISHED
        return state

    def set_state(self):
        """Este método realiza o set do campo state."""
        self.state = self.define_state()

    def set_status_change_date(self):
        """Este método definir status_change_date.
        Será marcado com a datetime.now() quando:
            - o estado mudar para ATIVO, FINALIZADO, CANCELADO.
            - a data_fim <= datetime.now() e não houver designação do substituto
        """
        old_status = self.old_fields.get("state", self.state)
        new_status = self.state
        log.info(f"old_status {old_status}")
        log.info(f"new_status {new_status}")
        log.info(f"status_change_date {self.status_change_date}")
        if isinstance(old_status, (list, tuple)):
            old_status = old_status[0]

        today = datetime.now().date()
        if (old_status != new_status and new_status in (ACTIVE, FINISHED)) or (
            self.data_fim <= today and self.designation_substitute is None
        ):
            self.status_change_date = today
            # if not self.pk and self.data_fim and self.data_fim < self.status_change_date:
            #     self.status_change_date = self.data_fim
        log.info(f"status_change_date {self.status_change_date}")

    @classmethod
    def update_state(cls, instance=None, date=None):
        """Este método é responsável por atualizar o state das substituições."""
        from rh.const import ESTADO_BASE_LICENCA_AFASTAMENTO

        date = datetime.now() if not date else date
        try:
            yesterday = date - relativedelta(days=7)
            today = datetime.now().date()
            if instance:
                subs = MovimentacaoSubstituicao.objects.filter(pk=instance.pk)
            else:
                subs = get_substituicoes(
                    date=date, yesterday=yesterday, today=today
                ).filter(designation_substituted__ativo=True)
            count = 1
            total = subs.count()
            log.info(
                f"______________________UPDATE_STATE_SUBSTITUTION______________________{total}"
            )
            for sub in subs.order_by("pk"):
                state = sub.define_state()
                if sub.state != state:
                    log.info(
                        "SUBSTITUIÇÃO - ATUALIZANDO ESTADO %s de %s..." % (count, total)
                    )
                    message = "%s de %s para %s" % (
                        sub,
                        sub.get_state_display(),
                        ESTADO_BASE_LICENCA_AFASTAMENTO.get(state),
                    )
                    log.info(message)
                    try:
                        sub = sub.instance_model
                        sub.save()
                    except Exception as err:
                        log.exception(err)
                        MovimentacaoSubstituicao.objects.filter(pk=sub.pk).update(
                            state=state
                        )
                count += 1
        except Exception as err:
            log.exception(err)

    @transaction.atomic
    def save(self, *args, **kargs):
        if self.pk and self.financial_effect_date_start is None and self.data_inicio:
            self.financial_effect_date_start = self.data_inicio

        if self.pk and self.financial_effect_date_end is None and self.data_fim:
            self.financial_effect_date_end = self.data_fim

        self.must_validate_document = False
        self.servidor_substituido = (
            self.afastamento.servidor if self.afastamento else None
        )
        if not self.place or (
            self.designation_substituted and self.place != self.designation_substituted
        ):
            self.place = (
                self.designation_substituted.lotacao
                if self.designation_substituted
                else None
            )
        if self.data_fim is None:
            self.data_fim = self.data_prevista
        if self.data_prevista is None:
            self.data_prevista = self.data_fim
        self.apply_possession()

        self.set_state()
        self.set_status_change_date()
        if self.servidor.type_by_possession not in ["EFE", "ECM", "CMS", "REQ", "RCM"]:
            self.validar_alteracao_substituto()

        super(MovimentacaoSubstituicao, self).save(*args, **kargs)

        self.replacement_manager()
        self.atualizar_designacao_substituicao()

    def validar_alteracao_substituto(self):
        from rh.pvf.models import PortalRequestSubstitute

        sol_substituicao = None
        if self.afastamento.dayoff_usufructs.exists():
            usufruto_atividade = (
                self.afastamento.dayoff_usufructs.first().activity.activity_requests
            )
            portal_request_usufruct = (
                usufruto_atividade.first() if usufruto_atividade else None
            )
            if portal_request_usufruct:
                sol_substituicao = (
                    portal_request_usufruct.portal_request_substitute.filter(
                        exercise__lotacao=self.place
                    ).first()
                )
        else:
            portal_request_afastamento = self.afastamento.portal_request_absence.first()
            if portal_request_afastamento:
                sol_substituicao = (
                    portal_request_afastamento.portal_request_substitute.filter(
                        exercise__lotacao=self.place
                    ).first()
                )

        if sol_substituicao:
            PortalRequestSubstitute.objects.filter(pk=sol_substituicao.pk).update(
                substitute=self.servidor
            )

    def get_texto_substituicao(self):
        try:
            with codecs.open(
                "%s/substituicao.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_substituicao = tpl % {
                    "servidor_substituto": self.servidor.pessoa_fisica.nome,
                    "matricula": self.servidor.matricula,
                    "periodo": "%s à %s"
                    % (
                        DateUtils.date_to_str(self.data_inicio),
                        (
                            DateUtils.date_to_str(self.data_fim)
                            if self.data_fim
                            else "----"
                        ),
                    ),
                    "departamento": (
                        self.designation_substituted.lotacao
                        if self.designation_substituted
                        else self.place
                    ),
                    "motivo": self.afastamento.situation_unicode,
                    "servidor_substituido": self.servidor_substituido.pessoa_fisica.nome,
                    "matricula_substituido": self.servidor_substituido.matricula,
                }
        except Exception as e:
            texto_substituicao = "OCORREU UM ERRO PREENCHENDO ANOTAÇÃO SUBSTITUIÇÃO"
            log.exception(e)
        return texto_substituicao

    def get_texto_substituicao_membro(self):
        try:
            with codecs.open(
                "%s/substituicao_membro.txt" % templates.__path__[0], "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto_substituicao = tpl % {
                    "servidor_substituto": self.servidor,
                    "local": self.instance_model.designation_substituted.lotacao,
                    "periodo": "%s %s"
                    % (
                        DateUtils.date_to_str(self.data_inicio),
                        (
                            " à " + DateUtils.date_to_str(self.data_fim)
                            if self.data_fim
                            else "----"
                        ),
                    ),
                    "motivo": self.afastamento.situation_unicode,
                    "servidor_substituido": self.servidor_substituido,
                }
        except Exception as e:
            texto_substituicao = "OCORREU UM ERRO PREENCHENDO ANOTAÇÃO SUBSTITUIÇÃO"
            log.exception(e)
        return texto_substituicao

    def alteracao_ferias(self):
        """
        Este método é responsável por alterar as férias dos substitutos que possuem férias intercedendo no
        no afastamento do substituído.
        As férias do substituto irão automaticamente para época oportuna.
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        return BaseLicencaAfastamento.alteracao_ferias(
            afastamento=self.afastamento,
            servidor=self.servidor,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
            instancia_verbose_name=self._meta.verbose_name,
            publicacao=self.publicacao_movimentacao,
        )

    @classmethod
    def cmd_replacement_manager(cls, date=None, lapse=None):
        """
        :py:function:: cmd_replacement_manager(cls, date=datetime.now().date())

        This method manages the replacement. It acts on replacement starting at date or through replacement list
        informed. Tries to create a designation and set on designation field. Also updates the designation according
        to replacement.

        :return: boolean
        :rtype: boolean
        """
        log.info("COMANDO => cmd_replacement_manager")
        log.info("=> Executando comando para gerenciar exercícios da substituição.")

        date = datetime.now().date() if not date else date
        lapse = 1 if not lapse else lapse
        substitutions = get_substituicoes(date=date, lapse=lapse).filter(
            designation_substituted__ativo=True
        )
        count = 1
        total = substitutions.count()
        log.info("Total: %s..." % total)
        for substitution in substitutions.order_by("data_inicio"):
            situation = "ATIVA"
            if substitution.substituicao_finalizada():
                situation = "FINALIZADA"
            elif substitution.data_inicio > date:
                situation = "AGENDADA"
            log.info(
                "%s: %s - ATUALIZANDO %s de %s..."
                % (substitution, situation, count, total)
            )
            try:
                substitution.instance_model.save()
            except Exception as err:
                log.exception(err)
            count += 1
        return True

    def replacement_manager(self):
        """
        :py:function:: replacement_manager(self)

        This method manages the replacement. It acts on replacement starting at date or through replacement list
        informed. Tries to create a designation and set on designation field. Also updates the designation according
        to replacement.

        :return: boolean
        :rtype: boolean
        """
        notify = False
        try:
            if self.can_run_process:
                ServidorLotacao.update_work_assignment_from_departure(
                    self.afastamento.instancia_modelo, ignore_duplicate_exercise=True
                )
        except Exception as err:
            log.exception(err)
            message = "Erro finalizando exercícios de %s." % self.afastamento.servidor
            message += " %s" % err
        try:
            if self.can_run_process:
                self._create_designation_substitute()
        except Exception as err:
            notify = True
            log.exception(err)
            message = "Erro criando o exercício para o substituto %s - %s." % (
                self.servidor,
                self,
            )
            message += " %s" % err
        if notify:
            log.info(message)
            raise Exception(message)

    def atualizar_designacao_substituicao(self):
        if self.designation_substitute:
            self.designation_substitute.data_vigencia_inicio = self.data_inicio
            self.designation_substitute.data_vigencia_fim = self.data_fim
            self.designation_substitute.save()

    def _validate_replacement_manager(self):
        """
        :py:function:: _validate_replacement_manager(self)

        This method validates fields required to create the designation. Considering if servidor, designation and
        publication has value.

        :return: True
        :rtype: boolean
        :raises Exception: If validates is wrong.
        """
        if self.servidor is None:
            raise Exception(
                "Cadastre o substituto da substituição %s - %s"
                % (self.servidor_substituido, self)
            )
        if not self.designation_substituted:
            raise Exception(
                "Cadastre o local da substituição %s - %s"
                % (self.servidor_substituido, self)
            )
        if not self.designation_substituted.lotacao:
            raise Exception(
                "Cadastre o local da substituição %s - %s"
                % (self.servidor_substituido, self)
            )
        return True

    def _create_designation_substitute(self):
        """
        :py:function:: _create_designation_substitute(self)

        This method creates a designation for substitute. Uses Servidor Lotacao._create to find an
        instance or to create one.

        :return: boolean
        :rtype: boolean
        """
        today = datetime.now().date()
        if self._validate_replacement_manager() and self not in get_substituicoes():
            designation_substitute = None
            if not self.designation_substitute and self.data_inicio <= today:
                resp = False if self.data_fim <= today else True
                designation_substitute = ServidorLotacao._create(
                    ignore_duplicate_exercise=True,
                    created_by_departure=self.afastamento,
                    annotate=True,
                    must_validate_document=False,
                    propagate_resp=False,
                    designacao=True,
                    responsible=resp,
                    ordinance=self.ordinance,
                    servidor=self.servidor,
                    lotacao=self.designation_substituted.lotacao,
                    publicacao=self.publicacao_movimentacao,
                    data_vigencia_inicio=self.data_inicio,
                    data_vigencia_fim=self.data_fim,
                    movimentacao_posse=(
                        self.servidor.posses_ativas.filter(
                            quadro__cargo__tipo_lei_cargo="EF"
                        ).latest("data_exercicio")
                        if self.servidor.posses_ativas.filter(
                            quadro__cargo__tipo_lei_cargo="EF"
                        ).exists()
                        else None
                    ),
                )
            else:
                designation_substitute = self.designation_substitute

            if (
                not designation_substitute
                and self.data_fim
                and self.data_fim > today
                and self.data_inicio <= today
            ):
                raise Exception(
                    "Designação de exercício não criada para substituto: %s!"
                    % self.servidor
                )

            if designation_substitute:
                log.info(
                    "=>Designação de substituição criada: %s - %s"
                    % (designation_substitute.servidor, designation_substitute)
                )
                self._update_substitute_designation(designation_substitute)
                self._set_substitute_designation(designation_substitute)

            return True
        elif not self.is_active():
            log.info(
                "Substituição encerrada. Não é mais possível alterar a designação do substituído."
            )
        return False

    def _update_substitute_designation(self, designation):
        """
        :py:function:: _update_substitute_designation(self, designation)

        This method updates designation if there are changes.

        :parameter ServidorLotacao designation: The designation
        :return: boolean
        :rtype: boolean
        """
        to_update = False
        if (
            self.designation_substituted.lotacao != designation.lotacao
            or self.publicacao_movimentacao != designation.publicacao
            or self.ordinance != designation.ordinance
            or self.data_inicio != designation.data_vigencia_inicio
            or self.data_fim != designation.data_vigencia_fim
        ):
            date_start = self.data_inicio
            date_end = self.data_fim
            if (
                not designation.servidor.member_type_by_possession
                and self.afastamento.data_inicio > designation.data_vigencia_inicio
            ):
                date_start = designation.data_vigencia_inicio
                date_end = designation.data_vigencia_fim
            else:
                to_update = True
            designation.lotacao = self.designation_substituted.lotacao
            designation.publicacao = self.publicacao_movimentacao
            designation.ordinance = self.ordinance
            designation.data_vigencia_inicio = date_start
            designation.data_vigencia_fim = date_end
        if to_update:
            designation.from_substitution = False
            designation.save(propagate_resp=False, ignore_duplicate_exercise=True)
        return True

    def _set_substitute_designation(self, designation):
        """
        :py:function:: _set_substitute_designation(self, designation)

        This method updates MovimentacaoSubstituicao.designation_substitute setting the new ServidorLotacao
        of the employee replacement.

        :parameter EmployeeWorkplace designation: The designation
        :return: boolean
        :rtype: boolean
        """
        try:
            if self.designation_substitute != designation:
                MovimentacaoSubstituicao.objects.filter(pk=self.pk).update(
                    designation_substitute=designation
                )
                MovimentacaoSubstituicao.objects.get(pk=self.pk).save()
        except Exception as err:
            log.exception(err)
        return True

    @classmethod
    def verifica_sobreposicao_periodo(
        cls,
        pk=None,
        servidor=None,
        designation_substituted=None,
        cargo_arquimedes=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        return False


class MovesSubstitutionsConsolidated(AuditTimestampModel):
    employee = models.ForeignKey(
        "rh.Servidor", on_delete=models.PROTECT, verbose_name="Servidor"
    )
    substitutions = models.ManyToManyField(
        "MovimentacaoSubstituicao",
        verbose_name="Substituições Consolidado",
        related_name="substitutions_consolidated",
    )
    days_consolidated = models.PositiveIntegerField(
        "Total Dias Consolidado", null=True, blank=True
    )
    qtd_max = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    installments_paid = models.PositiveIntegerField(
        "Parcela", null=True, blank=True, default=0
    )
    installments = models.PositiveIntegerField(
        "Prazo", null=True, blank=True, default=0
    )
    pct = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True, default=0
    )
    base_value = models.DecimalField(
        "Valor Base", max_digits=16, decimal_places=2, null=True, blank=True, default=0
    )
    value_calculated = models.DecimalField(
        "Valor Calculado", max_digits=16, decimal_places=2, null=True, blank=True
    )
    contribution_base = models.DecimalField(
        "Base Previdenciária",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    employer_value = models.DecimalField(
        "Patronal", max_digits=16, decimal_places=2, null=True, blank=True, default=0
    )
    paid_out = models.BooleanField("Pago", default=False, blank=True)
    defer = models.BooleanField("Deferido", default=False, blank=True)
    info = models.TextField("Informações", null=True, blank=True)
    paycheck_applied = models.ForeignKey(
        "gfp.ContraCheque",
        verbose_name="Contra Cheque Aplicado",
        related_name="paycheck_applied_consolidated",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    gcpp = models.ForeignKey(
        "ControlePagamentoPessoal",
        verbose_name="GCPP",
        related_name="move_subs_consolidated",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Movimentação de Substituição - Consolidado"
        db_table = "rh_movsubstituicaoconsolidado"
        ordering = ["employee"]

    def __str__(self):
        qtd_days = "-" if self.days_consolidated is None else self.days_consolidated
        return f"{self.employee} - Qtd Dias Consolidado: {qtd_days}"


class SubstitutionSendArquimedes(AuditTimestampModel):
    substitution = models.ForeignKey(
        "MovimentacaoSubstituicaoMembro",
        on_delete=models.CASCADE,
        related_name="sended_arquimedes",
    )

    class Meta:
        db_table = "rh_subssendarquimedes"
        verbose_name = "Movimentação enviada ao Arquimedes"


class MovimentacaoSubstituicaoMembro(MovimentacaoSubstituicao):
    cargo_arquimedes = models.IntegerField(default=0, blank=True)
    automatic_substitute = models.BooleanField(default=True, blank=True)

    class Meta:
        db_table = "rh_movsubsmembro"
        verbose_name = "Movimentação Substituição Membro"

    def __str__(self):
        job_position = self.posse
        if (
            self.cargo_arquimedes
            and Cargo.objects.filter(cargo_arquimedes=self.cargo_arquimedes).exists()
        ):
            job_position = Cargo.objects.get(cargo_arquimedes=self.cargo_arquimedes)
        return "INÍCIO: %s FIM: %s - %s" % (
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
            job_position,
        )

    @property
    def workplace_job_position_responsible(self):
        workplace = None
        if (
            self.cargo_arquimedes
            and Cargo.objects.filter(cargo_arquimedes=self.cargo_arquimedes).exists()
        ):
            job_position = Cargo.objects.filter(
                cargo_arquimedes=self.cargo_arquimedes
            ).latest("pk")
            workplace = job_position.lotacao_responsavel if job_position else workplace
        return workplace

    @classmethod
    def verifica_sobreposicao_periodo_base(
        cls,
        pk=None,
        servidor=None,
        designation_substituted=None,
        cargo_arquimedes=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        if servidor is None:
            raise Exception("Servidor é obrigatório.")
        if data_inicio is None:
            raise Exception("Data de início obrigatória.")
        if designation_substituted is None:
            raise Exception(
                "O servidor %s lotação/designação com responsabilidade." % servidor
            )
        sobreposicao = False
        query = (
            Q(Q(servidor_substituido__pk=servidor.pk) | Q(servidor__pk=servidor.pk))
            & (
                Q(data_inicio__gte=data_inicio)
                | Q(data_fim__gte=data_inicio)
                | Q(data_fim=None)
            )
            & Q(designation_substituted__lotacao=designation_substituted.lotacao)
        )
        substituicoes = MovimentacaoSubstituicaoMembro.objects.filter(query)
        if pk:
            substituicoes = substituicoes.exclude(pk=pk)
        dr_novo = NewDateRange(data_inicio, data_fim)
        msg_conflict = []
        for substituicao in substituicoes:
            dr_antigo = NewDateRange(substituicao.data_inicio, substituicao.data_fim)
            if dr_novo.intersect(dr_antigo).days > 0:
                sobreposicao = True
                msg_conflict.append(
                    f"O servidor {substituicao.afastamento.servidor} substituirá o servidor {substituicao.servidor_substituido} - {substituicao.afastamento.__str_restful__()}"
                )
        return sobreposicao, msg_conflict

    @classmethod
    def verifica_sobreposicao_periodo(
        cls,
        pk=None,
        servidor=None,
        designation_substituted=None,
        cargo_arquimedes=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        return MovimentacaoSubstituicaoMembro.verifica_sobreposicao_periodo_base(
            pk=pk,
            servidor=servidor,
            designation_substituted=designation_substituted,
            cargo_arquimedes=cargo_arquimedes,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )[0]

    def validate(self):
        self.validate_employee_not_member()
        self.validate_designation_substituted()
        self.validate_responsible()
        return super(MovimentacaoSubstituicaoMembro, self).validate()

    def validate_responsible(self):
        """
        This method validates designation_substituted.responsible is True.
        """
        if (
            self.designation_substituted.responsible is False
            and not self.designation_substituted.owner
        ):
            raise Exception(
                "Responsabilidade é requerida em %s." % self.designation_substituted
            )
        return True

    def validate_designation_substituted(self):
        """
        This method validates designation_substituted informed.
        """
        if not self.designation_substituted:
            raise Exception(
                "Exercício do substituído %s não foi preenchido."
                % self.servidor_substituido
            )
        elif not self.designation_substituted.owner:
            raise Exception(
                "O substituído %s deve ser afastável." % self.servidor_substituido
            )
        return True

    def validate_employee_not_member(self):
        if not self.servidor_substituido.member_type_by_possession:
            raise Exception("O servidor deve ser um MEMBRO.")
        return True

    def validate_periodo(self):
        """
        Este método verifica se existe alguma substituição/inativação vigente comparando
        com o período de cadastro.
        """
        sobreposicao, msg_conflict = (
            MovimentacaoSubstituicaoMembro.verifica_sobreposicao_periodo_base(
                pk=self.pk,
                servidor=self.servidor_substituido,
                designation_substituted=self.designation_substituted,
                cargo_arquimedes=self.cargo_arquimedes,
                data_inicio=self.data_inicio,
                data_fim=self.data_fim,
            )
        )
        if not sobreposicao:
            if InativacaoCargoMembro.verifica_sobreposicao_periodo(
                servidor=self.servidor_substituido,
                designation=self.designation_substitute,
                cargo_arquimedes=self.cargo_arquimedes,
                data_inicio=self.data_inicio,
                data_fim=self.data_fim,
            ):
                sobreposicao = True
        if sobreposicao:
            msg = "Existe uma substituição vigente neste período."
            for err in msg_conflict:
                msg += " %s" % err
            raise Exception(msg)
        return True

    def apply_possession(self):
        if (
            not self.posse
            and self.afastamento.servidor.posses_ativas.filter(
                quadro__cargo__cargo_arquimedes=self.cargo_arquimedes
            ).exists()
        ):
            self.posse = self.afastamento.servidor.posses_ativas.filter(
                quadro__cargo__cargo_arquimedes=self.cargo_arquimedes
            ).latest("data_exercicio")

    @transaction.atomic
    def save(self, *args, **kargs):
        if not self.cargo_arquimedes:
            self.cargo_arquimedes = self.posse.quadro.cargo.cargo_arquimedes
        self.must_validate_document = True
        super(MovimentacaoSubstituicaoMembro, self).save(*args, **kargs)


@auditable("data_fim", "publicacao_fim")
class InativacaoCargoMembro(AuditTimestampModel):
    afastamento = models.ForeignKey(
        "afastamento.BaseLicencaAfastamento",
        related_name="inativacaocargomembro",
        on_delete=models.CASCADE,
    )
    cargo_arquimedes = models.IntegerField(default=0, blank=True)
    publicacao_inativacao = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        related_name="agendamentoinativacao_publicacao_inativacao",
        on_delete=models.PROTECT,
    )
    publicacao_ativacao = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        related_name="agendamentoinativacao_publicacao_ativacao",
        on_delete=models.PROTECT,
    )
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    data_prevista = models.DateField(
        null=True, blank=True, verbose_name="Data Prevista Fim"
    )
    publicacao_alteracao = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        related_name="inativacao",
        verbose_name="Documento Revogação",
        on_delete=models.PROTECT,
    )
    possession = models.ForeignKey(
        "MovimentacaoPosse",
        related_name="inativacaocargo",
        verbose_name="Posse",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    designation = models.ForeignKey(
        "ServidorLotacao",
        related_name="inactivation_jobposition",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    usuario_nao_informa = []

    class Meta:
        verbose_name = "Inativação de Cargo de Membro"

    def __str__(self):
        if self.designation:
            return "%s" % self.designation
        return "%s" % self.afastamento

    @classmethod
    def verifica_sobreposicao_periodo(
        cls,
        pk=None,
        servidor=None,
        designation=None,
        cargo_arquimedes=None,
        data_inicio=None,
        data_fim=None,
    ):
        """
        Este método verifica se há sobreposição de um novo período (início, fim)
        com um período já cadastrado.
        """
        if servidor is None:
            raise Exception("Servidor é obrigatório.")
        if data_inicio is None:
            raise Exception("Data de início obrigatória.")
        sobreposicao = False
        query = (
            Q(afastamento__servidor__pk=servidor.pk)
            & (
                Q(data_inicio__gte=data_inicio)
                | Q(data_fim__gte=data_inicio)
                | Q(data_fim=None)
            )
            & Q(cargo_arquimedes=cargo_arquimedes)
            & Q(designation=designation)
        )
        inativacoes = InativacaoCargoMembro.objects.filter(query)
        if pk:
            inativacoes = inativacoes.exclude(pk=pk)
        dr_novo = NewDateRange(data_inicio, data_fim)
        for inativacao in inativacoes:
            if (
                dr_novo.intersect(
                    NewDateRange(inativacao.data_inicio, inativacao.data_fim)
                ).days
                > 0
            ):
                sobreposicao = True
        return sobreposicao

    def validate(self):
        self.validate_intervalo_pertence_afastamento()
        self.validate_publicacao()
        self.validate_periodo()
        return True

    def validate_intervalo_pertence_afastamento(self):
        from rh.afastamento.models import BaseLicencaAfastamento

        if not BaseLicencaAfastamento._intervalo_pertence_afastamento(
            self.afastamento, self.data_inicio, self.data_fim
        ):
            raise Exception(
                "Inativação %s a %s, do(a) %s, não pertence à %s."
                % (
                    DateUtils.date_to_str(self.data_inicio),
                    DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
                    self.afastamento.servidor,
                    "%s de %s a %s"
                    % (
                        self.afastamento,
                        DateUtils.date_to_str(self.afastamento.data_inicio),
                        (
                            DateUtils.date_to_str(self.afastamento.data_fim)
                            if self.afastamento.data_fim
                            else "----"
                        ),
                    ),
                )
            )
        return True

    def validate_publicacao(self):
        if (
            self.publicacao_inativacao is None
            or self.publicacao_inativacao.data_vigencia is None
        ):
            raise Exception(
                "É necessário que Data de Vigência do Documento seja preenchido."
            )
        return True

    def validate_periodo(self):
        """
        Este método verifica se existe alguma inativação vigente comparando com o período de cadastro.
        """
        sobreposicao = False
        if self.verifica_sobreposicao_periodo(
            pk=self.pk,
            servidor=self.afastamento.servidor,
            designation=self.designation,
            cargo_arquimedes=self.cargo_arquimedes,
            data_inicio=self.data_inicio,
            data_fim=self.data_fim,
        ):
            sobreposicao = True
        else:
            for (
                designation_owner
            ) in self.afastamento.servidor.owner_locations_can_substitute:
                if MovimentacaoSubstituicaoMembro.verifica_sobreposicao_periodo(
                    servidor=self.afastamento.servidor,
                    designation_substituted=designation_owner,
                    cargo_arquimedes=self.cargo_arquimedes,
                    data_inicio=self.data_inicio,
                    data_fim=self.data_fim,
                ):
                    sobreposicao = True
        if sobreposicao:
            raise Exception("Existe uma inativação/substituição vigente neste período.")
        return True

    def validate_inativacao_iniciada(self):
        """
        Este valida se a inativação já foi iniciada.
        """
        if self.inativacao_iniciada():
            raise Exception("Inativação iniciada.")
        return True

    def validate_inativacao_finalizada(self):
        """
        Este valida se a inativação já foi finalizada.
        """
        if self.inativacao_finalizada():
            raise Exception("Inativação Finalizada.")
        return True

    def inativacao_iniciada(self):
        """
        Este método verifica se a inativação foi iniciada.
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        data_inicio, data_fim = self.data_inicio, self.data_fim
        if self.pk:
            data_inicio, data_fim = (
                self.get_self().data_inicio,
                self.get_self().data_fim,
            )
        return BaseLicencaAfastamento._iniciado(data_inicio, data_fim)

    def inativacao_finalizada(self):
        """
        Este método verifica se a inativação foi finalizada.
        """
        from rh.afastamento.models import BaseLicencaAfastamento

        data_fim = self.data_fim
        if self.pk:
            data_fim = self.get_self().data_fim
        return BaseLicencaAfastamento._finalizado(date_end=data_fim)

    def get_self(self):
        base = None
        try:
            base = InativacaoCargoMembro.objects.get(pk=self.pk)
        except Exception:
            pass
        return base

    @transaction.atomic
    def save(self, *args, **kargs):
        try:
            if self.data_fim is None:
                self.data_fim = self.data_prevista
            self.validate()
            super(InativacaoCargoMembro, self).save(*args, **kargs)
        except Exception as err:
            log.exception()
            raise err

    @transaction.atomic
    def delete(self, *args, **kargs):
        try:
            self.validate_inativacao_iniciada()
            self.validate_inativacao_finalizada()
            super(InativacaoCargoMembro, self).delete(*args, **kargs)
        except Exception as err:
            log.exception()
            raise err


@to_search(
    [
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "publicacao_movimentacao__numero", "type": "text"},
    ]
)
class MovimentacaoConcessao(MovimentacaoPessoal):
    class Meta:
        verbose_name = "Movimentação de Concessão"
        db_table = "rh_movconcessao"

    def __str__(self):
        return "CONCESSÃO %s" % (self.servidor)


class MovimentacaoRemocao(MovimentacaoPessoal):
    remocao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "LEVEL_REMOVAL_REASON"),
        verbose_name="Remoção",
    )
    lotacao_destino = models.ForeignKey(
        Lotacao,
        on_delete=models.CASCADE,
        related_name="lotacao_remocao",
        verbose_name="Lotação de destino",
        null=True,
        blank=True,
    )
    servidor_permuta = models.ForeignKey(
        Servidor,
        on_delete=models.CASCADE,
        related_name="permuta_remocao",
        verbose_name="Servidor da permuta",
        null=True,
        blank=True,
    )
    permuta = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    data_vigencia = models.DateField(null=True, blank=False)

    class Meta:
        verbose_name = "Movimentação de Remoção"
        db_table = "rh_movremocao"

    def __str__(self):
        return "%s PARA %s" % (self.get_remocao_display(), self.lotacao_destino)

    @staticmethod
    def get_template_directory():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

    def _anotar_remocao_permuta(self):
        filepath = os.path.join(self.get_template_directory(), "remocao-permuta.txt")
        texto = ""

        servidor_cargo_efetivo = None
        servidor_permuta_cargo_efetivo = None
        try:
            servidor_cargo_efetivo = self.servidor.posses_ativas.get(
                quadro__cargo__tipo_lei_cargo="EF"
            ).quadro.cargo
            servidor_permuta_cargo_efetivo = self.servidor_permuta.posses_ativas.get(
                quadro__cargo__tipo_lei_cargo="EF"
            ).quadro.cargo
        except Exception:
            if servidor_cargo_efetivo is None:
                raise Exception(
                    "O servidor %s não possui cargo efetivo." % self.servidor
                )
            else:
                raise Exception(
                    "O servidor %s não possui cargo efetivo." % self.servidor_permuta
                )
        else:
            with codecs.open(filepath, "r", "utf-8") as fd:
                texto = fd.read()

            texto = texto % {
                "servidor": self.servidor.pessoa_fisica.nome,
                "cargo": servidor_cargo_efetivo,
                "matricula": self.servidor.matricula,
                "lotacao": self.servidor.workplace_current,
                "servidor_permuta": self.servidor_permuta.pessoa_fisica.nome,
                "cargo_permuta": servidor_permuta_cargo_efetivo,
                "matricula_permuta": self.servidor_permuta.matricula,
                "lotacao_permuta": self.servidor_permuta.workplace_current,
                "data_vigencia": DateUtils.date_to_str(self.data_vigencia),
            }
            tipo = Publicacao.get_tipo(self.publicacao_movimentacao)

            anot = AnotacaoRemocao()
            anot.servidor = self.servidor
            anot.tipo_documento = tipo
            anot.numero_documento = self.publicacao_movimentacao.numero
            anot.data_documento = self.publicacao_movimentacao.data_expedicao
            anot.publicacao = self.publicacao_movimentacao
            anot.data_portaria_inicio = self.publicacao_movimentacao.data_vigencia
            anot.resumo = "REMOÇÃO POR PREMUTA"
            anot.texto = texto
            anot.indireto = True
            self.anotacoes.add(anot, bulk=False)

            self._anotar_lotacao_remocao(
                self.servidor,
                self.servidor_permuta.workplace_current,
                self.publicacao_movimentacao,
                self,
            )

            anot = AnotacaoRemocao()
            anot.servidor = self.servidor_permuta
            anot.tipo_documento = tipo
            anot.numero_documento = self.publicacao_movimentacao.numero
            anot.data_documento = self.publicacao_movimentacao.data_expedicao
            anot.publicacao = self.publicacao_movimentacao
            anot.data_portaria_inicio = self.publicacao_movimentacao.data_vigencia
            anot.resumo = "REMOÇÃO POR PREMUTA"
            anot.texto = texto
            anot.indireto = True
            self.permuta.anotacoes.add(anot, bulk=False)

            self._anotar_lotacao_remocao(
                self.servidor_permuta,
                self.servidor.workplace_current,
                self.publicacao_movimentacao,
                self.permuta,
            )

    def _anotar_lotacao_remocao(self, servidor, lotacao, publicacao, movimentacao):
        filepath = os.path.join(self.get_template_directory(), "lotacao-remocao.txt")
        texto = ""

        with codecs.open(filepath, "r", "utf-8") as fd:
            texto = fd.read()

        texto = texto % {
            "texto_servidor": self.servidor.texto_servidor(),
            "nome": servidor.pessoa_fisica.nome,
            "lotacao": lotacao,
            "portaria": publicacao.numero,
            "data_portaria": DateUtils.date_to_str(publicacao.data_expedicao),
        }

        anot = AnotacaoGeral()
        anot.servidor = servidor
        anot.tipo_documento = publicacao.tipo
        anot.numero_documento = publicacao.numero
        anot.data_documento = publicacao.data_publicacao
        anot.publicacao = publicacao
        anot.data_portaria_inicio = publicacao.data_vigencia
        anot.resumo = "LOTAÇÃO POR REMOÇÃO"
        anot.texto = texto
        anot.indireto = True
        movimentacao.anotacoes.add(anot, bulk=False)

    def _process_remocao(self):
        workplace_old = ServidorLotacao.finish_active_workplace(
            self.servidor, self.data_vigencia
        )

        employee_workplace = ServidorLotacao._create(
            designacao=False,
            servidor=self.servidor,
            lotacao=self.lotacao_destino,
            publicacao=self.publicacao_movimentacao,
            data_vigencia_inicio=self.data_vigencia,
            propagate=True,
        )

        if (
            not ServidorLotacao.objects.filter(
                designacao=True, servidor=self.servidor, lotacao=self.lotacao_destino
            )
            .filter(
                Q(data_vigencia_inicio__lte=self.data_vigencia)
                & (
                    Q(data_vigencia_fim__gte=self.data_vigencia)
                    | Q(data_vigencia_fim=None)
                )
            )
            .exists()
        ):
            employee_workplace.create_work_assignment()

        self._anotar_remocao(workplace_old)
        return True

    def _anotar_remocao(self, workplace_old=None):
        filepath = os.path.join(self.get_template_directory(), "remocao.txt")
        texto = ""

        servidor_cargo_efetivo = None
        try:
            servidor_cargo_efetivo = self.servidor.posses_ativas.get(
                quadro__cargo__tipo_lei_cargo="EF"
            ).quadro.cargo
        except Exception:
            raise Exception("O servidor %s não possui cargo efetivo." % self.servidor)
        else:
            with codecs.open(filepath, "r", "utf-8") as fd:
                texto = fd.read()

            if not workplace_old:
                workplace_old = self.servidor.get_workplace_only(
                    date=(self.data_vigencia - relativedelta(days=1))
                )
                if workplace_old.exists():
                    workplace_old = workplace_old.last().lotacao

            if not workplace_old:
                raise Exception(
                    "Servidor não tem uma lotação definida, primeiro lote este servidor."
                )
            texto = texto % {
                "servidor": self.servidor.pessoa_fisica.nome,
                "cargo": servidor_cargo_efetivo,
                "matricula": self.servidor.matricula,
                "lotacao_origem": workplace_old,
                "lotacao_destino": self.lotacao_destino,
                "data_vigencia": DateUtils.date_to_str(self.data_vigencia),
            }

            tipo = Publicacao.get_tipo(self.publicacao_movimentacao)
            anot = AnotacaoRemocao()
            anot.servidor = self.servidor
            anot.tipo_documento = tipo
            anot.numero_documento = self.publicacao_movimentacao.numero
            anot.data_documento = self.publicacao_movimentacao.data_expedicao
            anot.publicacao = self.publicacao_movimentacao
            anot.data_portaria_inicio = self.publicacao_movimentacao.data_vigencia
            anot.resumo = "REMOÇÃO POR %s" % self.get_remocao_display()
            anot.texto = texto
            anot.indireto = True

            self.anotacoes.all().delete()
            self.anotacoes.add(anot, bulk=False)

            self._anotar_lotacao_remocao(
                self.servidor, self.lotacao_destino, self.publicacao_movimentacao, self
            )

    def _process_remocao_permuta(self):

        if not self.servidor_permuta:
            raise Exception(
                "Remoção do tipo permuta, deve ser indicado o servidor permutado."
            )
        else:
            """
            Processa a permuta ignorando a lotação indicada, caso tenha sido indicada deve explodir uma
            exceção avisando ao usuário que a Lotação que ele pensa é diferente da lotação do servidor permutado.
            """
            lotacao_permutado = False
            lotacao_origem = False
            try:
                lotacao_permutado = self.servidor_permuta.workplace_current
                lotacao_origem = self.servidor.workplace_current
            except Exception:
                if lotacao_permutado is None:
                    raise Exception(
                        "Servidor permutado não tem uma lotação definida, primeiro lote este servidor."
                    )
                else:
                    raise Exception(
                        "Servidor não tem uma lotação definida, primeiro lote este servidor."
                    )
            else:
                if (
                    self.lotacao_destino is not None
                    and lotacao_permutado != self.lotacao_destino
                ):
                    raise Exception(
                        "A lotação destino selecionada é diferente da lotação do permutado, na duvida deixe nova lotação em branco."
                    )
                else:
                    ServidorLotacao.finish_active_workplace(
                        self.servidor, self.data_vigencia
                    )
                    ServidorLotacao.finish_active_workplace(
                        self.servidor_permuta, self.data_vigencia
                    )

                    employee_workplace = ServidorLotacao._create(
                        designacao=False,
                        servidor=self.servidor,
                        lotacao=lotacao_permutado,
                        publicacao=self.publicacao_movimentacao,
                        data_vigencia_inicio=self.data_vigencia,
                        propagate=True,
                    )
                    employee_workplace.create_work_assignment()

                    employee_workplace = ServidorLotacao._create(
                        designacao=False,
                        servidor=self.servidor_permuta,
                        lotacao=lotacao_origem,
                        publicacao=self.publicacao_movimentacao,
                        data_vigencia_inicio=self.data_vigencia,
                        propagate=True,
                    )

                    employee_workplace.create_work_assignment()

                    permuta = MovimentacaoRemocao()
                    permuta.remocao = 3
                    permuta.servidor = self.servidor_permuta
                    permuta.servidor_permuta = self.servidor
                    permuta.lotacao_destino = lotacao_origem
                    permuta.data_vigencia = self.data_vigencia
                    permuta.permuta = self
                    permuta.publicacao_movimentacao = self.publicacao_movimentacao
                    permuta.save(escape_movements=True)

                    self.permuta = permuta
                    self.lotacao_destino = lotacao_permutado
                    self.save(escape_movements=True)

                    self._anotar_remocao_permuta()
        return True

    def delete(self, *args, **kargs):
        """
        Processa a limpeza da movimentação
        """
        try:
            with transaction.atomic():

                escape_permuta = False
                if "escape_permuta" in kargs:
                    escape_permuta = kargs.pop("escape_permuta")

                qs = self.servidor.workplace_only_active
                if qs.exists():
                    qs = qs.last()
                    if qs.father_of.exists():
                        qs.father_of.filter().delete()
                    qs.delete()

                """Limpa todas as anotações"""
                self.anotacoes.all().delete()

                """Caso a movimentação seja por permuta, deleta a permuta também"""
                if self.permuta and not escape_permuta:
                    self.permuta.delete(escape_permuta=True)

                query = ServidorLotacao.objects.filter(
                    servidor=self.servidor, designacao=False
                )

                if query.exists():
                    sl = query.latest("data_vigencia_inicio")
                    sl.data_vigencia_fim = None
                    sl.save()

        except Exception as ex:
            log.exception(ex)
            raise ex
        super(MovimentacaoRemocao, self).delete(*args, **kargs)

    def save(self, *args, **kargs):
        try:
            escape_movements = False
            if "escape_movements" in kargs:
                escape_movements = kargs.pop("escape_movements")

            self.remocao = int(self.remocao)

            with transaction.atomic():
                super(MovimentacaoRemocao, self).save(*args, **kargs)

                if self.pk and not escape_movements:
                    if self.remocao == 3 and not self.permuta:
                        self._process_remocao_permuta()
                    elif self.lotacao_destino:
                        self._process_remocao()
                    else:
                        raise Exception(
                            "O servidor a ser removido ainda não tem informações da lotação atual."
                        )

        except Exception as err:
            log.exception(err)
            raise err


class MovimentacaoRedistribuicao(MovimentacaoPessoal):
    movimentacao_posse = models.ForeignKey(
        "MovimentacaoPosse",
        related_name="posse",
        verbose_name="Posse",
        on_delete=models.CASCADE,
    )
    orgao_destino = models.ForeignKey(
        "UnidadeAdministrativa",
        on_delete=models.CASCADE,
        verbose_name="Órgão Destino",
        related_name="orgao_destino",
        null=True,
        blank=True,
    )
    quadro = models.ForeignKey(
        "Quadro", related_name="quadro", verbose_name="Cargo", on_delete=models.CASCADE
    )
    redistribuicao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_REDISTRIBUTION"),
        verbose_name="Redistribuição",
    )

    class Meta:
        verbose_name = "Movimentação de Redistribuição"
        db_table = "rh_movredistribuicao"

    def __str__(self):
        return "%s - %s PARA: %s" % (
            self.movimentacao_posse,
            self.redistribuicao,
            self.orgao_destino if self.orgao_destino else "",
        )

    @transaction.atomic
    def save(self, *args, **kargs):
        self.servidor = self.movimentacao_posse.servidor
        super(MovimentacaoRedistribuicao, self).save(*args, **kargs)


class MovimentacaoDescontoLegal(MovimentacaoPessoal):
    desconto = models.IntegerField(choices=((1, "REPOSIÇÃO"), (2, "INDENIZAÇÃO")))
    valor = models.DecimalField(max_digits=16, decimal_places=2)
    parcela = models.IntegerField()

    class Meta:
        verbose_name = "Movimentação de Desconto Legal"
        db_table = "rh_movdesclegal"

    def __str__(self):
        return "%s - %s - %s" % (self.get_desconto_display(), self.parcela, self.valor)


class MovimentacaoEstabilizacao(MovimentacaoPessoal):
    class Meta:
        verbose_name = "Movimentação de Estabilização"
        db_table = "rh_movestabilizacao"

    class AlreadyExists(Exception):
        pass

    data_vigencia = models.DateField(
        verbose_name="Início vigência", null=True, blank=True
    )
    posse = models.ForeignKey(
        MovimentacaoPosse,
        related_name="estabilizacoes",
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "ESTABILIZAÇÃO %s - %s" % (
            self.posse,
            DateUtils.date_to_str(self.data_vigencia),
        )

    def validate(self):
        if not self.pk and self.posse.estabilizacoes.exists():
            raise self.AlreadyExists(
                "O servidor %s já é estável no cargo %s"
                % (self.servidor, self.posse.quadro.cargo)
            )
        return super(MovimentacaoEstabilizacao, self).validate()

    def get_texto(self):
        """
        DECLARAR ESTÁVEL no serviço público estadual, conforme dispõe o Art. 20 da Lei nº 1.818, de 23/08/2007,
        o(a) servidor(a) {servidor} inscrito sob a matrícula {matricula}, a partir de {data_vigencia},
        conforme {doc}, em virtude do atendimento dos requisitos relativos à disciplina, idoneidade moral,
        aptidão para a função, conduta e integração do servidor ao serviço e às atribuições do cargo,
        bem como pelo decurso de 03(três) anos de efetivo exercício no cargo de {cargo}.
        """
        texto_progressao = ""
        file_template = (
            "estabilizacaoS" if self.servidor.tipo == "S" else "estabilizacaoM"
        )
        with codecs.open(
            "%s/%s.txt" % (templates.__path__[0], file_template), "r", "utf-8"
        ) as fd:
            tpl = fd.read()
            texto_progressao = tpl % {
                "texto_servidor": self.servidor.texto_servidor(),
                "data_vigencia": self.data_vigencia.strftime("%d/%m/%Y"),
                "doc": "%s" % self.publicacao_movimentacao,
                "servidor": "%s" % self.servidor.pessoa_fisica.nome,
                "matricula": self.servidor.matricula,
                "cargo": "%s - %s"
                % (self.posse.quadro.cargo.nome, self.posse.quadro.especialidade),
            }
        return texto_progressao

    def anotacao(self, *args, **kargs):
        log = getLogger("MovimentacaoEstabilizacao:Model")
        texto_anotacao = self.get_texto()

        try:
            tipo = Publicacao.get_tipo(self.publicacao_movimentacao)
            if self.anotacao_geral is None:
                anotacao_geral = AnotacaoCarreira.manage_instance(
                    servidor=self.servidor,
                    tipo_documento=tipo,
                    publicacao=self.publicacao_movimentacao,
                    data_portaria_inicio=self.publicacao_movimentacao.data_vigencia,
                    texto=texto_anotacao,
                    resumo="ESTABILIZAÇÃO",
                    data_documento=self.publicacao_movimentacao.data_expedicao,
                )
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
                self.anotacao_geral = anotacao_geral
            else:
                anotacao_geral = AnotacaoCarreira.objects.get(pk=self.anotacao_geral.pk)
                anotacao_geral.publicacao = self.publicacao_movimentacao
                anotacao_geral.data_portaria_inicio = (
                    self.publicacao_movimentacao.data_vigencia
                )
                anotacao_geral.texto = texto_anotacao
                anotacao_geral.servidor = self.servidor
                anotacao_geral.tipo_documento = tipo
                anotacao_geral.indireto = False
                anotacao_geral.resumo = "ESTABILIZAÇÃO"
                anotacao_geral.save()
                AnotacaoCarreira.objects.filter(pk=anotacao_geral.pk).update(
                    indireto=True
                )
        except Exception as e:
            log.exception(e)
            raise Exception(
                "Falha na criação da Anotação de Estabilização do servidor %s."
                % self.servidor
            )

    @transaction.atomic
    def save(self, *args, **kargs):
        self.servidor = self.posse.servidor
        super(MovimentacaoEstabilizacao, self).save(*args, **kargs)


class PeriodoGratMembros(AuditTimestampModel):
    """
    Model responsável pelos Períodos de Gratificações de Membros
    """

    mes = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS")
    )
    ano = models.PositiveIntegerField("Ano")
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )

    class Meta:
        unique_together = ("mes", "ano")
        ordering = ("-ano", "-mes")

    def __str__(self):
        return f"{self.mes}/{self.ano}"

    def validar_campo_ano(self):
        if len(str(self.ano)) != 4 or isinstance(self.ano, int) is False:
            raise Exception(
                f"O campo ano dever conter apenas números e com 4 caracteres. Ex: {date.today().ano}."
            )

    def validar_campo_mes(self):
        if self.mes == "" or self.mes is None:
            raise Exception(f"O preenchimento do campo mês é obrigatório.")

    def validar_periodo_min(self):
        if self.ano < 2022:
            raise Exception("Não é permitido criar períodos antes do ano de 2022.")

    def validar_se_periodo_existente(self):
        if PeriodoGratMembros.objects.filter(mes=self.mes, ano=self.ano).exists():
            raise Exception("Já existe um período com esse mês e ano.")

    def validate(self):
        self.validar_campo_ano()
        self.validar_campo_mes()
        self.validar_periodo_min()

        if self.pk is None:
            self.validar_se_periodo_existente()

    def save(self, *args, **kwargs):
        self.validate()
        super(PeriodoGratMembros, self).save(*args, **kwargs)


class GratMembros(AuditTimestampModel):
    """
    Model responsável pelos Membros consolidados do Período de Gratificações de Membros
    """

    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="gratificacoes_membros",
        on_delete=models.PROTECT,
    )
    periodo = models.ForeignKey(
        PeriodoGratMembros, related_name="membros", on_delete=models.CASCADE
    )
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )
    designacoes = models.ManyToManyField(
        "ServidorLotacao", related_name="designacoes_grat_membro"
    )

    class Meta:
        ordering = ("-periodo", "servidor", "-created_at")

    def __str__(self):
        return f"{self.periodo} - {self.servidor}"


class Gratificacao(AuditTimestampModel):
    """
    Model responsável pelas Gratificações do Membro consolidado de um Período de Gratificações de Membros
    """

    tipos_status = (
        ("AVAL", "Avaliar"),
        ("DEFER", "Deferido"),
        ("INDEFER", "Indeferido"),
    )

    grat_membro = models.ForeignKey(
        GratMembros, related_name="gratificacoes", on_delete=models.CASCADE
    )
    evento = models.ForeignKey(
        "gfp.Evento",
        verbose_name="Evento",
        related_name="gratificacoes_membro",
        on_delete=models.PROTECT,
    )
    qtd_dias_consolidado = models.IntegerField(
        "Qtd Dias - Consolidado", null=True, blank=True
    )
    qtd_dias_deferido = models.IntegerField(
        "Qtd Dias - Deferido", null=True, blank=True
    )
    ordem = models.IntegerField("Ordem", null=True, blank=True)
    status = models.CharField(
        "Status", max_length=10, choices=tipos_status, blank=True, default="AVAL"
    )
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )
    cumulativa = models.BooleanField("Cumulativa", default=False)
    principal = models.BooleanField("Principal", default=False)

    class Meta:
        ordering = ("ordem", "evento")

    def __str__(self):
        return f"{self.ordem} - {self.evento} - {self.grat_membro.servidor} - {self.get_status_display()}"

    def validar_campo_qtd_dias_deferido(self):
        if self.qtd_dias_deferido is not None:
            try:
                int(self.qtd_dias_deferido)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido inválido. Por favor utilize somente números inteiros."
                )

    def validar_gcpp_em_avaliar(self, gcpp):
        if gcpp.exists():
            if gcpp.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validate(self, gcpp):
        self.validar_campo_qtd_dias_deferido()
        self.validar_gcpp_em_avaliar(gcpp)

    def save(self):
        if self.pk:
            grat = Gratificacao.objects.get(pk=self.pk)

            if self.qtd_dias_deferido != 0 and grat.qtd_dias_deferido == 0:
                self.status = "AVAL"
            else:
                gcpp = ControlePagamentoPessoal.objects.filter(
                    periodo_ano=self.grat_membro.periodo.ano,
                    periodo_mes=self.grat_membro.periodo.mes,
                    evento=self.evento,
                    servidor=self.grat_membro.servidor,
                )
                self.validate(gcpp)

                if gcpp.exists() and gcpp.first().status in ["analise", "apto"]:
                    qtd_dias = (
                        self.qtd_dias_deferido
                        if self.qtd_dias_deferido is not None
                        else self.qtd_dias_consolidado
                    )
                    gcpp.update(qtd_dias_confirmado=qtd_dias)
                    gcpp.update(qtd_dias_calculado=None)
                    gcpp.update(valor_calculado=None)
                    gcpp.update(qtd_dias_pgto=None)
                    gcpp.update(valor_pgto=None)
                    gcpp.update(status="analise")

        super().save()


class PeriodoExercCumulPermanente(AuditTimestampModel):
    """
    Model responsável pelos Períodos de Exercícios Cumulativos Permanentes
    """

    mes = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS")
    )
    ano = models.PositiveIntegerField("Ano")
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )

    class Meta:
        unique_together = ("mes", "ano")
        ordering = ("-ano", "-mes")

    def __str__(self):
        return f"{self.mes}/{self.ano}"

    def validar_campo_ano(self):
        if len(str(self.ano)) != 4 or isinstance(self.ano, int) is False:
            raise Exception(
                f"O campo ano dever conter apenas números e com 4 caracteres. Ex: {date.today().ano}."
            )

    def validar_campo_mes(self):
        if self.mes == "" or self.mes is None:
            raise Exception(f"O preenchimento do campo mês é obrigatório.")

    def validar_periodo_min(self):
        if self.ano < 2022:
            raise Exception("Não é permitido criar períodos antes do ano de 2022.")

    def validar_se_periodo_existente(self):
        if PeriodoExercCumulPermanente.objects.filter(
            mes=self.mes, ano=self.ano
        ).exists():
            raise Exception("Já existe um período com esse mês e ano.")

    def validate(self):
        self.validar_campo_ano()
        self.validar_campo_mes()
        self.validar_periodo_min()

        if self.pk is None:
            self.validar_se_periodo_existente()

    def save(self, *args, **kwargs):
        self.validate()

        super(PeriodoExercCumulPermanente, self).save(*args, **kwargs)


class ExercCumulPermanente(AuditTimestampModel):
    """
    Model responsável pelos Exercícios Cumulativos Permanentes
    """

    tipos_status = (
        ("AVAL", "Avaliar"),
        ("DEFER", "Deferido"),
        ("INDEFER", "Indeferido"),
    )

    servidor = models.ForeignKey(
        "Servidor",
        verbose_name="Servidor",
        related_name="exerc_cumul_perm",
        on_delete=models.PROTECT,
    )
    periodo = models.ForeignKey(
        PeriodoExercCumulPermanente,
        related_name="exercs_cumul_perm",
        on_delete=models.CASCADE,
    )
    qtd_dias_afastamento = models.IntegerField(
        "Qtd Dias Afastamento", null=True, blank=True
    )
    qtd_dias_consolidado = models.IntegerField(
        "Qtd Dias Consolidado", null=True, blank=True
    )
    qtd_dias_deferido = models.IntegerField(
        "Qtd Dias - Deferido", null=True, blank=True
    )
    pct_consolidado = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True
    )
    pct_deferido = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True, default=None
    )
    status = models.CharField(
        "Status", max_length=10, choices=tipos_status, blank=True, default="AVAL"
    )

    class Meta:
        ordering = ("-periodo", "servidor", "-created_at")

    def __str__(self):
        return f"{self.periodo} - {self.servidor} - {self.get_status_display()}"

    def validar_campo_qtd_dias_deferido(self):
        if self.qtd_dias_deferido is not None:
            try:
                int(self.qtd_dias_deferido)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido inválido. Por favor utilize somente números inteiros."
                )

    def validar_gcpp_em_avaliar(self, gcpp):
        if gcpp.exists():
            if gcpp.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validate(self, gcpp):
        self.validar_campo_qtd_dias_deferido()
        self.validar_gcpp_em_avaliar(gcpp)

    def save(self):
        from rh.gfp.models import Evento

        if self.pk:
            gcpp = ControlePagamentoPessoal.objects.filter(
                periodo_ano=self.periodo.ano,
                periodo_mes=self.periodo.mes,
                evento=Evento.objects.get(numero="00800"),
                servidor=self.servidor,
            )
            self.validate(gcpp)

            if gcpp.exists() and gcpp.first().status in ["analise", "apto"]:
                qtd_dias = (
                    self.qtd_dias_deferido
                    if self.qtd_dias_deferido is not None
                    else self.qtd_dias_consolidado
                )
                gcpp.update(qtd_dias_confirmado=qtd_dias)
                gcpp.update(pct=self.pct_deferido)
                gcpp.update(qtd_dias_calculado=None)
                gcpp.update(valor_calculado=None)

        super().save()


class DesigsExercCumulPermanente(AuditTimestampModel):
    """
    Model responsável pelas Designações vinculadas ao Exercício Cumulativo Permanente
    """

    ACAO_CHOICES = (
        (0, ""),
        (1, "Coadjuvando"),
        (2, "Colaborando"),
        (3, "Adjunto"),
    )

    PREJUIZO_CHOICES = (
        (0, ""),
        (1, "Com prejuízo"),
        (2, "Sem prejuízo"),
    )

    exerc_cumul_perm = models.ForeignKey(
        ExercCumulPermanente, related_name="designacoes", on_delete=models.CASCADE
    )
    designacao = models.ForeignKey(
        "Lotacao",
        null=True,
        blank=True,
        verbose_name="Designação",
        related_name="exerc_cumul_perm_desigs",
        on_delete=models.PROTECT,
    )
    substituicao = models.BooleanField(default=False)
    ativo = models.BooleanField(default=False)
    principal = models.BooleanField(default=False)
    responsavel = models.BooleanField(default=False)
    titular = models.BooleanField(default=False)
    coordenador = models.BooleanField(default=False)
    prejuizo = models.SmallIntegerField(
        default=0, choices=PREJUIZO_CHOICES, blank=True, null=True
    )
    acao = models.SmallIntegerField(
        default=0, choices=ACAO_CHOICES, blank=True, null=True
    )
    pct = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    base_calculo = models.BooleanField(default=False)
    data_vigencia_inicio = models.DateField(
        null=True, verbose_name="Data Vigência Início"
    )
    data_vigencia_fim = models.DateField(
        null=True, blank=True, verbose_name="Data Vigência Fim"
    )
    cumulativa = models.BooleanField(default=False)

    class Meta:
        ordering = ("-data_vigencia_inicio", "-created_at")

    def __str__(self):
        return f"{self.exerc_cumul_perm.periodo} - {self.exerc_cumul_perm.servidor} - {self.designacao}"


class MovimentacaoDiligencia(MovimentacaoPessoal):
    """
    Model responsável pelo controle das Designações para Diligência
    """

    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data Fim")
    comarca = models.ForeignKey(
        Comarca, verbose_name="Comarca", on_delete=models.CASCADE
    )
    substituto = models.ForeignKey(
        Servidor,
        null=True,
        blank=True,
        related_name="diligencias",
        verbose_name="Substituto",
        on_delete=models.CASCADE,
    )
    publicacao = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        related_name="diligencias",
        verbose_name="Publicação",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Movimentação de Verba de Diligência"
        db_table = "rh_movdiligencias"
        ordering = ["comarca"]

    def __str__(self):
        ret = "..."
        return f'{self.comarca} - {self.data_inicio.strftime("%d/%m/%Y")} a {self.data_fim.strftime("%d/%m/%Y") if self.data_fim else ret}'

    @property
    def diligence_period(self):
        return NewDateRange(
            self.data_inicio, self.data_fim if self.data_fim else self.data_inicio
        )

    def validate_date_start_greater_than_date_end(self):
        if self.data_fim and self.data_fim < self.data_inicio:
            raise Exception("A data fim deve ser maior que a data de início.")

    def validate_unique_end_date_movement(self):
        if (
            not self.data_fim
            and MovimentacaoDiligencia.objects.filter(
                Q(data_fim__isnull=True), servidor=self.servidor
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise Exception(
                "O servidor poderá ter somente uma diligência sem data fim."
            )

    def validate_date_conflict(self):
        diligences = MovimentacaoDiligencia.objects.filter(
            servidor=self.servidor
        ).exclude(pk=self.pk)
        for diligence in diligences:
            if (
                diligence.diligence_period.contains(self.diligence_period)
                or self.diligence_period.contains(diligence.diligence_period)
            ) or self.data_inicio == diligence.data_inicio - timedelta(days=1):
                raise Exception(f"O período conflita com a diligência: {diligence}.")

    def validate_start_dif_end_in_comarca(self):
        """A data de início não pode ser igual que a data de fim do registro anterior na mesma Comarca"""
        movimentacoes = MovimentacaoDiligencia.objects.filter(comarca=self.comarca)
        for movimentacao in movimentacoes:
            if self.data_inicio == movimentacao.data_fim:
                raise Exception(
                    "A data de início deve ser maior que a data fim de outro registro na mesma Comarca."
                )

    def validate_end_dif_start_in_comarca(self):
        """A data de fim não pode ser igual que a data de início do próximo registro na mesma Comarca"""
        movimentacoes = MovimentacaoDiligencia.objects.filter(comarca=self.comarca)
        for movimentacao in movimentacoes:
            if self.data_fim == movimentacao.data_inicio:
                raise Exception(
                    "A data fim deve ser menor que a data de início de outro registro na mesma Comarca."
                )

    def validate(self):
        self.validate_unique_end_date_movement()
        self.validate_date_start_greater_than_date_end()
        self.validate_date_conflict()
        self.validate_start_dif_end_in_comarca()
        self.validate_end_dif_start_in_comarca()

    def save(self):
        self.validate()
        super().save()


class GratDiligencia(AuditTimestampModel):
    """
    Model responsável pela Gratificação de Designação para Diligência de um período
    """

    tipos_status = (
        ("AVAL", "Avaliar"),
        ("DEFER", "Deferido"),
        ("INDEFER", "Indeferido"),
    )

    mov_diligencia = models.ForeignKey(
        MovimentacaoDiligencia, related_name="grat_diligencia", on_delete=models.PROTECT
    )
    evento = models.ForeignKey(
        "gfp.Evento",
        verbose_name="Evento",
        related_name="grat_diligencia",
        on_delete=models.PROTECT,
    )
    qtd_dias_consolidado_titular = models.IntegerField(
        "Qtd Dias - Consolidado - Titular", null=True, blank=True
    )
    qtd_dias_deferido_titular = models.IntegerField(
        "Qtd Dias - Deferido - Titular", null=True, blank=True
    )
    qtd_dias_consolidado_substituto = models.IntegerField(
        "Qtd Dias - Consolidado - Substituto", null=True, blank=True
    )
    qtd_dias_deferido_substituto = models.IntegerField(
        "Qtd Dias - Deferido - Substituto", null=True, blank=True
    )
    status = models.CharField(
        "Status", max_length=10, choices=tipos_status, blank=True, default="AVAL"
    )
    ano = models.PositiveIntegerField("Ano")
    mes = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS")
    )
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )

    class Meta:
        unique_together = ["mov_diligencia", "ano", "mes"]
        ordering = ("-ano", "-mes")

    def __str__(self):
        return f"{self.ano}/{self.mes} - {self.mov_diligencia.servidor} - {self.get_status_display()}"

    def validar_campo_qtd_dias_deferido_titular(self):
        if self.qtd_dias_deferido_titular is not None:
            try:
                int(self.qtd_dias_deferido_titular)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido Titular inválido. Por favor utilize somente números inteiros."
                )

    def validar_campo_qtd_dias_deferido_substituto(self):
        if self.qtd_dias_deferido_substituto is not None:
            try:
                int(self.qtd_dias_deferido_substituto)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido Substituto inválido. Por favor utilize somente números inteiros."
                )

    def validar_gcpp_titular_em_avaliar(self):
        gcpp_titular = ControlePagamentoPessoal.objects.filter(
            periodo_ano=self.ano,
            periodo_mes=self.mes,
            evento=self.evento,
            servidor=self.mov_diligencia.servidor,
        )
        if gcpp_titular.exists():
            if gcpp_titular.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do titular já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp_titular.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do tituar já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validar_gcpp_substituto_em_avaliar(self):
        gcpp_substituto = ControlePagamentoPessoal.objects.filter(
            periodo_ano=self.ano,
            periodo_mes=self.mes,
            evento=self.evento,
            servidor=self.mov_diligencia.substituto,
        )
        if gcpp_substituto.exists():
            if gcpp_substituto.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do substituto já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp_substituto.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do substituto já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validate(self):
        self.validar_campo_qtd_dias_deferido_titular()
        self.validar_campo_qtd_dias_deferido_substituto()

        if self.pk:
            self.validar_gcpp_titular_em_avaliar()
            self.validar_gcpp_substituto_em_avaliar()

    def save(self):
        self.validate()
        if self.pk:
            grat = GratDiligencia.objects.get(pk=self.pk)

            if (
                self.qtd_dias_deferido_titular != 0
                and grat.qtd_dias_deferido_titular == 0
            ) or (
                self.qtd_dias_deferido_substituto != 0
                and grat.qtd_dias_deferido_substituto == 0
            ):
                self.status = "AVAL"

            gcpp_titular = ControlePagamentoPessoal.objects.filter(
                periodo_ano=self.ano,
                periodo_mes=self.mes,
                evento=self.evento,
                servidor=self.mov_diligencia.servidor,
            )

            if self.qtd_dias_deferido_titular not in [0, None]:
                if gcpp_titular.exists() and gcpp_titular.first().status in [
                    "analise",
                    "apto",
                ]:
                    qtd_dias = (
                        self.qtd_dias_deferido_titular
                        if self.qtd_dias_deferido_titular is not None
                        else self.qtd_dias_consolidado_titular
                    )
                    gcpp_titular.update(qtd_dias_confirmado=qtd_dias)
                    gcpp_titular.update(qtd_dias_calculado=None)
                    gcpp_titular.update(valor_calculado=None)
                    gcpp_titular.update(qtd_dias_pgto=None)
                    gcpp_titular.update(valor_pgto=None)
                    gcpp_titular.update(status="analise")
                elif gcpp_titular.exists() is False:
                    ControlePagamentoPessoal.objects.create(
                        servidor=self.mov_diligencia.servidor,
                        evento=self.evento,
                        qtd_dias_confirmado=self.qtd_dias_deferido_titular,
                        periodo_ano=self.ano,
                        periodo_mes=self.mes,
                        conferido=True,
                        conferido_por=Servidor.objects.get(user=get_current_user()),
                        modulo_origem="diligencia",
                    )
            elif (
                gcpp_titular.exists()
                and gcpp_titular.first().status in ["analise", "apto"]
                and self.qtd_dias_deferido_titular == 0
            ):
                gcpp_titular.delete()

            if self.mov_diligencia.substituto:
                gcpp_substituto = ControlePagamentoPessoal.objects.filter(
                    periodo_ano=self.ano,
                    periodo_mes=self.mes,
                    evento=self.evento,
                    servidor=self.mov_diligencia.substituto,
                )

                if self.qtd_dias_deferido_substituto not in [0, None]:
                    if gcpp_substituto.exists() and gcpp_substituto.first().status in [
                        "analise",
                        "apto",
                    ]:
                        qtd_dias = (
                            self.qtd_dias_deferido_substituto
                            if self.qtd_dias_deferido_substituto is not None
                            else self.qtd_dias_consolidado_substituto
                        )
                        gcpp_substituto.update(qtd_dias_confirmado=qtd_dias)
                        gcpp_substituto.update(qtd_dias_calculado=None)
                        gcpp_substituto.update(valor_calculado=None)
                        gcpp_substituto.update(qtd_dias_pgto=None)
                        gcpp_substituto.update(valor_pgto=None)
                        gcpp_substituto.update(status="analise")
                    elif gcpp_substituto.exists() is False:
                        ControlePagamentoPessoal.objects.create(
                            servidor=self.mov_diligencia.substituto,
                            evento=self.evento,
                            qtd_dias_confirmado=self.qtd_dias_deferido_substituto,
                            periodo_ano=self.ano,
                            periodo_mes=self.mes,
                            conferido=True,
                            conferido_por=Servidor.objects.get(user=get_current_user()),
                            modulo_origem="diligencia",
                        )
                elif (
                    gcpp_substituto.exists()
                    and gcpp_substituto.first().status in ["analise", "apto"]
                    and self.qtd_dias_deferido_substituto == 0
                ):
                    gcpp_substituto.delete()

        super().save()


class ControlePagamentoPessoal(AuditTimestampModel):
    """
    Model responsável pela Gestão de Controle de Pagamento de Pessoal
    """

    STATUS = (
        ("analise", "Em Análise"),
        ("calculado", "Calculado"),
        ("apto", "Apto para pgto"),
        ("inapto", "Inapto para pgto"),
        ("pago", "Pago"),
    )

    servidor = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="pag_pessoal_servidor",
        on_delete=models.PROTECT,
    )
    evento = models.ForeignKey(
        "gfp.Evento",
        verbose_name="Evento",
        related_name="pgtos_pessoal_evento",
        on_delete=models.PROTECT,
    )
    qtd_dias_confirmado = models.IntegerField(
        "Qtd Dias Confirmado", null=True, blank=True
    )
    qtd_dias_pgto = models.IntegerField("Qtd Dias para Pgto", null=True, blank=True)
    valor_pgto = models.DecimalField(
        "Valor para Pgto", max_digits=10, decimal_places=2, null=True, blank=True
    )
    qtd_max_dias = models.DecimalField(
        "Qtd Máxima de Dias Calculado",
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
    )
    qtd_dias_calculado = models.IntegerField(
        "Qtd Dias Calculado", null=True, blank=True
    )
    valor_base = models.DecimalField(
        "Valor Base", max_digits=16, decimal_places=2, null=True, blank=True, default=0
    )
    valor_calculado = models.DecimalField(
        "Valor Calculado", max_digits=16, decimal_places=2, null=True, blank=True
    )
    valor_base_prev = models.DecimalField(
        "Base Previdenciária",
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
    )
    valor_patronal = models.DecimalField(
        "Patronal", max_digits=16, decimal_places=2, null=True, blank=True, default=0
    )
    parcela = models.PositiveIntegerField("Parcela", null=True, blank=True, default=0)
    prazo = models.PositiveIntegerField("Prazo", null=True, blank=True, default=0)
    pct = models.DecimalField(
        max_digits=10, decimal_places=6, null=True, blank=True, default=0
    )
    info = models.TextField("Informações", null=True, blank=True)
    periodo_mes = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS")
    )
    periodo_ano = models.PositiveIntegerField("Ano")
    conferido = models.BooleanField("Conferido", default=False, blank=True)
    conferido_por = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="controle_pag_pessoal_conferido_por",
        on_delete=models.PROTECT,
    )
    conferido_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        "Status", max_length=10, choices=STATUS, blank=True, default="analise"
    )
    contracheque_aplicado = models.ForeignKey(
        "gfp.ContraCheque",
        verbose_name="Contra Cheque Aplicado",
        related_name="pag_pessoal_aplicado",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    modulo_origem = models.CharField(
        "Módulo de origem", max_length=255, null=True, blank=True
    )
    faltas = models.ManyToManyField(
        "ponto.Falta", verbose_name="Faltas", related_name="pag_pessoal_faltas"
    )
    dependencia = models.ForeignKey(
        "rh.Dependencia",
        verbose_name="Dependencia",
        related_name="pag_pessoal_dependencia",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    contracheque_removido = models.BooleanField(
        verbose_name="Contracheque removido?",
        default=False,
        blank=True,
    )
    contracheque_removido_texto = models.CharField(
        verbose_name="Texto do contracheque removido",
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Controle Pagamento de Pessoal"
        ordering = ["-periodo_ano", "-periodo_mes", "servidor", "evento", "status"]

    def __str__(self):
        return f"{self.servidor}: {self.evento} - {self.qtd_dias_confirmado} - Conferido: {'sim' if self.conferido else 'não'}"


class MovimentacaoAuxiliarCoordenacao(MovimentacaoPessoal):
    """
    Model responsável pelo controle da Designação para Auxiliar de Coordenação
    """

    data_inicio = models.DateField(verbose_name="Data Início", db_index=True)
    data_fim = models.DateField(
        verbose_name="Data Fim", blank=True, null=True, db_index=True
    )
    gedoc = models.CharField(
        verbose_name="GEDOC", max_length=128, blank=True, null=True
    )
    nucleo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "NUCLEO_CHOICES"), blank=True, null=True
    )
    substituto = models.ForeignKey(
        Servidor,
        null=True,
        blank=True,
        related_name="auxiliar_coordenacao",
        verbose_name="Substituto",
        on_delete=models.CASCADE,
    )
    publicacao = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        related_name="auxiliar_coordenacao",
        verbose_name="Publicação",
        on_delete=models.PROTECT,
    )
    servidor_designacao = models.ForeignKey(
        ServidorLotacao,
        null=True,
        blank=True,
        verbose_name="Designação para gratificação",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Designação para Auxiliar de Coordenação"
        db_table = "rh_mov_auxiliar_coordenacao"
        ordering = ["servidor"]

    @property
    def ativo(self):
        if not self.data_fim or self.data_fim <= datetime.today():
            return False
        return True

    def validate_unique_designation_local(self):
        """O servidor não pode ter duas designações ativas na mesma comarca/nucleo"""
        date = datetime.now().date()
        if self.nucleo:
            query = Q(nucleo=self.nucleo) | Q(
                servidor_designacao__lotacao__comarca=self.servidor_designacao.lotacao.comarca
            )
        else:
            query = Q(
                servidor_designacao__lotacao__comarca=self.servidor_designacao.lotacao.comarca
            )

        if (
            MovimentacaoAuxiliarCoordenacao.objects.filter(
                Q(data_fim__isnull=True) | Q(data_fim__gt=date),
                Q(query),
                servidor=self.servidor,
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise Exception(
                "O servidor já possui uma designação ativa na mesma comarca/nucleo."
            )

    def validate_date_end_greater_than_date_start(self):
        """A data de fim não pode ser menor que a data de início"""
        if self.data_fim and self.data_fim < self.data_inicio:
            raise Exception("A data fim deve ser maior que a data de início.")

    def validate_remote_work(self):
        """Titular não pode estar em teletrabalho(Depende de implementação futura de controle de teletrabalho)"""
        pass

    def validate_start_dif_end_in_comarca(self):
        """A data de início não pode ser igual que a data de fim do registro anterior na mesma Comarca"""
        if self.validate_comarca():
            movimentacoes = MovimentacaoAuxiliarCoordenacao.objects.filter(
                servidor_designacao__lotacao__comarca=self.servidor_designacao.lotacao.comarca
            )

            # Se for comarca de Cuiba, filtra por servidor
            if self.servidor_designacao.lotacao.comarca.id == 8477:
                movimentacoes = movimentacoes.filter(
                    servidor_designacao=self.servidor_designacao
                )

            for movimentacao in movimentacoes:
                if self.data_inicio == movimentacao.data_fim:
                    raise Exception(
                        "A data de início deve ser maior que a data fim de outro registro na mesma Comarca."
                    )

    def validate_end_dif_start_in_comarca(self):
        """A data de fim não pode ser igual que a data de início do próximo registro na mesma Comarca"""
        if self.validate_comarca():
            movimentacoes = MovimentacaoAuxiliarCoordenacao.objects.filter(
                servidor_designacao__lotacao__comarca=self.servidor_designacao.lotacao.comarca
            )

            # Se for comarca de Cuiba, filtra por servidor
            if self.servidor_designacao.lotacao.comarca.id == 8477:
                movimentacoes = movimentacoes.filter(
                    servidor_designacao=self.servidor_designacao
                )

            for movimentacao in movimentacoes:
                if self.data_fim == movimentacao.data_inicio:
                    raise Exception(
                        "A data fim deve ser menor que a data de início de outro registro na mesma Comarca."
                    )

    def validate_comarca(self):
        if (
            self.servidor_designacao
            and self.servidor_designacao.lotacao
            and self.servidor_designacao.lotacao.comarca
        ):
            return True
        return False

    def get_nucleo(self):
        if self.servidor_designacao:
            self.nucleo = self.servidor_designacao.lotacao.nucleo

    def validate(self):
        if self.validate_comarca():
            self.validate_unique_designation_local()
        self.validate_date_end_greater_than_date_start()
        self.validate_start_dif_end_in_comarca()
        self.validate_end_dif_start_in_comarca()
        return super().validate()

    def save(self):
        self.validate()
        self.get_nucleo()
        super().save()


class GratAuxiliarCoordenacao(AuditTimestampModel):
    """
    Model responsável pela Gratificação de Auxiliar Coordenação de um período
    """

    tipos_status = (
        ("AVAL", "Avaliar"),
        ("DEFER", "Deferido"),
        ("INDEFER", "Indeferido"),
    )

    mov_aux_coord = models.ForeignKey(
        MovimentacaoAuxiliarCoordenacao,
        related_name="grat_aux_coord",
        on_delete=models.PROTECT,
    )
    evento = models.ForeignKey(
        "gfp.Evento",
        verbose_name="Evento",
        related_name="grat_aux_coord",
        on_delete=models.PROTECT,
    )
    qtd_dias_consolidado_titular = models.IntegerField(
        "Qtd Dias - Consolidado - Titular", null=True, blank=True
    )
    qtd_dias_deferido_titular = models.IntegerField(
        "Qtd Dias - Deferido - Titular", null=True, blank=True
    )
    qtd_dias_consolidado_substituto = models.IntegerField(
        "Qtd Dias - Consolidado - Substituto", null=True, blank=True
    )
    qtd_dias_deferido_substituto = models.IntegerField(
        "Qtd Dias - Deferido - Substituto", null=True, blank=True
    )
    status = models.CharField(
        "Status", max_length=10, choices=tipos_status, blank=True, default="AVAL"
    )
    ano = models.PositiveIntegerField("Ano")
    mes = models.PositiveIntegerField(
        "Mês", choices=Choice.get_choices_for("rh", "MONTHS")
    )
    data_ultimo_calculo = models.DateTimeField(
        "Data do Último Cálculo", null=True, blank=True
    )

    class Meta:
        unique_together = ["mov_aux_coord", "ano", "mes"]
        ordering = ("-ano", "-mes")

    def __str__(self):
        return f"{self.ano}/{self.mes} - {self.mov_aux_coord.servidor} - {self.get_status_display()}"

    def validar_campo_qtd_dias_deferido_titular(self):
        if self.qtd_dias_deferido_titular is not None:
            try:
                int(self.qtd_dias_deferido_titular)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido Titular inválido. Por favor utilize somente números inteiros."
                )

    def validar_campo_qtd_dias_deferido_substituto(self):
        if self.qtd_dias_deferido_substituto is not None:
            try:
                int(self.qtd_dias_deferido_substituto)
            except:
                raise Exception(
                    "Valor do campo Qtd Dias Deferido Substituto inválido. Por favor utilize somente números inteiros."
                )

    def validar_gcpp_titular_em_avaliar(self):
        gcpp_titular = ControlePagamentoPessoal.objects.filter(
            periodo_ano=self.ano,
            periodo_mes=self.mes,
            evento=self.evento,
            servidor=self.mov_aux_coord.servidor,
        )
        if gcpp_titular.exists():
            if gcpp_titular.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do titular já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp_titular.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do tituar já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validar_gcpp_substituto_em_avaliar(self):
        gcpp_substituto = ControlePagamentoPessoal.objects.filter(
            periodo_ano=self.ano,
            periodo_mes=self.mes,
            evento=self.evento,
            servidor=self.mov_aux_coord.substituto,
        )
        if gcpp_substituto.exists():
            if gcpp_substituto.first().status == "inapto":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do substituto já foi avaliada no GCPP e está INAPTA para pagamento.
                """
                )
            elif gcpp_substituto.first().status == "pago":
                raise Exception(
                    """
                    Não é possível alterar o registro de gratificação selecionado.
                    A gratificação do substituto já foi avaliada no GCPP e já está PAGA.
                """
                )

    def validate(self):
        self.validar_campo_qtd_dias_deferido_titular()
        self.validar_campo_qtd_dias_deferido_substituto()

        if self.pk:
            self.validar_gcpp_titular_em_avaliar()
            self.validar_gcpp_substituto_em_avaliar()

    def save(self):
        self.validate()
        if self.pk:
            grat = GratAuxiliarCoordenacao.objects.get(pk=self.pk)

            if (
                self.qtd_dias_deferido_titular != 0
                and grat.qtd_dias_deferido_titular == 0
            ) or (
                self.qtd_dias_deferido_substituto != 0
                and grat.qtd_dias_deferido_substituto == 0
            ):
                self.status = "AVAL"

            gcpp_titular = ControlePagamentoPessoal.objects.filter(
                periodo_ano=self.ano,
                periodo_mes=self.mes,
                evento=self.evento,
                servidor=self.mov_aux_coord.servidor,
            )

            if self.qtd_dias_deferido_titular not in [0, None]:
                if gcpp_titular.exists() and gcpp_titular.first().status in [
                    "analise",
                    "apto",
                ]:
                    qtd_dias = (
                        self.qtd_dias_deferido_titular
                        if self.qtd_dias_deferido_titular is not None
                        else self.qtd_dias_consolidado_titular
                    )
                    gcpp_titular.update(qtd_dias_confirmado=qtd_dias)
                    gcpp_titular.update(qtd_dias_calculado=None)
                    gcpp_titular.update(valor_calculado=None)
                    gcpp_titular.update(qtd_dias_pgto=None)
                    gcpp_titular.update(valor_pgto=None)
                    gcpp_titular.update(status="analise")
                elif gcpp_titular.exists() is False:
                    ControlePagamentoPessoal.objects.create(
                        servidor=self.mov_aux_coord.servidor,
                        evento=self.evento,
                        qtd_dias_confirmado=self.qtd_dias_deferido_titular,
                        periodo_ano=self.ano,
                        periodo_mes=self.mes,
                        conferido=True,
                        conferido_por=Servidor.objects.get(user=get_current_user()),
                        modulo_origem="aux_coord",
                    )
            elif (
                gcpp_titular.exists()
                and gcpp_titular.first().status in ["analise", "apto"]
                and self.qtd_dias_deferido_titular == 0
            ):
                gcpp_titular.delete()

            if self.mov_aux_coord.substituto:
                gcpp_substituto = ControlePagamentoPessoal.objects.filter(
                    periodo_ano=self.ano,
                    periodo_mes=self.mes,
                    evento=self.evento,
                    servidor=self.mov_aux_coord.substituto,
                )

                if self.qtd_dias_deferido_substituto not in [0, None]:
                    if gcpp_substituto.exists() and gcpp_substituto.first().status in [
                        "analise",
                        "apto",
                    ]:
                        qtd_dias = (
                            self.qtd_dias_deferido_substituto
                            if self.qtd_dias_deferido_substituto is not None
                            else self.qtd_dias_consolidado_substituto
                        )
                        gcpp_substituto.update(qtd_dias_confirmado=qtd_dias)
                        gcpp_substituto.update(qtd_dias_calculado=None)
                        gcpp_substituto.update(valor_calculado=None)
                        gcpp_substituto.update(qtd_dias_pgto=None)
                        gcpp_substituto.update(valor_pgto=None)
                        gcpp_substituto.update(status="analise")
                    elif gcpp_substituto.exists() is False:
                        ControlePagamentoPessoal.objects.create(
                            servidor=self.mov_aux_coord.substituto,
                            evento=self.evento,
                            qtd_dias_confirmado=self.qtd_dias_deferido_substituto,
                            periodo_ano=self.ano,
                            periodo_mes=self.mes,
                            conferido=True,
                            conferido_por=Servidor.objects.get(user=get_current_user()),
                            modulo_origem="aux_coord",
                        )
                elif (
                    gcpp_substituto.exists()
                    and gcpp_substituto.first().status in ["analise", "apto"]
                    and self.qtd_dias_deferido_substituto == 0
                ):
                    gcpp_substituto.delete()

        super().save()


class MovimentacaoTeletrabalho(MovimentacaoPessoal):
    """
    Model responsável pelo controle de teletrabalho
    """

    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim", blank=True, null=True)
    presencial = models.IntegerField(verbose_name="Presencial")
    gedoc = models.TextField(verbose_name="GEDOC", blank=True, null=True)
    aprovador = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        verbose_name="Aprovador do Teletrabalho",
        related_name="aprovador_teletrabalho",
        blank=True,
        null=True,
    )
    tipo_ato = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_ACT"), verbose_name="Tipo Ato"
    )
    ativo = models.BooleanField(
        verbose_name="Ativo",
        default=False,
        blank=True,
    )
    tipo_pedido = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_PEDIDO"),
        verbose_name="Tipo do Pedido",
        default=1,  # Adesão
    )
    lotacao = models.ForeignKey(
        ServidorLotacao,
        on_delete=models.PROTECT,
        verbose_name="lotacao",
        related_name="mov_teletrabalho",
        null=True,
        blank=True,
    )
    situacao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "STATUS_TELETRABALHO"),
        verbose_name="Status do teletrabalho",
        default=1,
    )
    qtd_bloqueios = models.IntegerField(
        verbose_name="Qtd bloqueios", blank=True, null=True
    )
    qtd_meses_impedido = models.IntegerField(
        verbose_name="Qtd meses impedido", blank=True, null=True
    )
    possui_saldo_devedor = models.BooleanField(
        verbose_name="Possui saldo devedor",
        default=False,
        blank=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        ret = "..."
        return f'{self.servidor} - {self.data_inicio.strftime("%d/%m/%Y")} a {self.data_fim.strftime("%d/%m/%Y") if self.data_fim else ret}'

    def validate_date_end_greater_than_date_start(self):
        """A data de fim não pode ser menor que a data de início"""
        if self.data_fim and self.data_fim < self.data_inicio:
            raise Exception("A data fim deve ser maior que a data de início.")

    def validate_last_plan_date_start_greater_end_date(self):
        last_mov = MovimentacaoTeletrabalho.objects.filter(
            servidor=self.servidor
        ).last()
        if not self.pk and last_mov:
            if not last_mov.data_fim:
                raise Exception("Preencha a data fim do último plano de trabalho.")
            else:
                if not self.data_inicio > last_mov.data_fim:
                    raise Exception(
                        "Data inicio tem que ser maior que a data fim do último plano de trabalho."
                    )
        return True

    def validate_update_end_date(self):
        if self.pk:
            mov = MovimentacaoTeletrabalho.objects.get(pk=self.pk)
            last_mov = MovimentacaoTeletrabalho.objects.filter(
                servidor=self.servidor
            ).last()
            if mov.data_fim and not self.data_fim and mov != last_mov:
                raise Exception(
                    "Data fim é obrigatória quando há um plano de trabalho mais recente."
                )
        return True

    def validar_data_situacao(self):
        from rh.pvf.const import STS_CANCELED_APPLICANT, STS_CANCELED_DGP

        if self.pk:
            planos = self.pvf_work_plan.filter(cancelado_solicitacao=False).exclude(
                status__in=[STS_CANCELED_APPLICANT, STS_CANCELED_DGP]
            )
            for plano in planos:
                if (
                    self.data_fim.month < plano.reference_month
                    and self.data_fim.year <= plano.reference_year
                ):
                    raise Exception(
                        "Data Fim não pode ser menor que o mês de referência quando o plano já foi Efetivado ou com uma solicitação em aberto no VDF."
                    )
        return True

    def validar_periodo_conflitante(self):

        q_mov_teletrabalho = MovimentacaoTeletrabalho.objects.filter(
            servidor=self.servidor
        )

        if self.pk:
            q_mov_teletrabalho = q_mov_teletrabalho.exclude(pk=self.pk)

        if self.data_fim is not None:
            q_mov_teletrabalho = q_mov_teletrabalho.filter(
                Q(data_inicio__lte=self.data_inicio, data_fim__gte=self.data_inicio)
                | Q(data_inicio__gte=self.data_inicio, data_inicio__lte=self.data_fim)
                | Q(data_inicio__lte=self.data_inicio, data_fim__isnull=True)
                | Q(data_inicio__lte=self.data_fim, data_fim__isnull=True)
            )

        if q_mov_teletrabalho.exists():
            raise Exception("Houve um conflito no periodo informado.")
        return True

    def validar_lotacao_vazia(self):
        if self.lotacao is None:
            raise Exception("O campo Lotação deve ser preenchido!")

    def validar_tipo_pedido(self):
        if not self.pk:
            query = MovimentacaoTeletrabalho.objects.filter(servidor=self.servidor)
            if not query.exists():
                self.tipo_pedido = 1  # Adesão
            else:
                self.tipo_pedido = 2  # Prorrogação

    def validar_teletrabalho_ativo(self):
        """
        Função para validar se o Teletrabalho deve ou não estar ativo de acordo com a data de início, fim e
        data de hoje.
        """
        hoje = datetime.today().date()
        if not self.data_fim:
            if self.data_inicio <= hoje:
                self.ativo = True
            else:
                self.ativo = False
        elif self.data_inicio <= hoje and self.data_fim >= hoje:
            self.ativo = True
        else:
            self.ativo = False

    def validar_periodo_revogacao(self):
        """
        Função para validar se o teletrabalho está revogado e o período que não poderá solicitar novo plano.
        """

        ultimo_plano = MovimentacaoTeletrabalho.objects.filter(
            servidor=self.servidor
        ).last()
        if ultimo_plano and ultimo_plano.situacao == STATUS_TELETRABALHO_REVOGADO:
            qtd_meses = (
                ultimo_plano.qtd_meses_impedido
                if ultimo_plano.qtd_meses_impedido
                else 0
            )
            data_referencia_revogacao = ultimo_plano.data_fim + relativedelta(
                months=qtd_meses
            )
            if self.data_inicio <= data_referencia_revogacao:
                data_permitida = data_referencia_revogacao + relativedelta(days=1)
                raise Exception(
                    f"Só será permitido cadastrar um novo plano para o servidor a partir de {data_permitida.strftime('%d/%m/%Y')}."
                )
        return True

    @property
    def qtd_dias_bloqueados(self):
        if self.situacao not in [
            STATUS_TELETRABALHO_BLOQUEADO,
            STATUS_TELETRABALHO_PENDENTE,
        ]:
            return 0
        historico = self.historico_movteletrabalho.filter(
            acao__in=["BLOQUEAR", "PENDENTE"]
        ).last()
        return (
            abs((historico.created_at.date() - datetime.today().date()).days)
            if historico
            else 0
        )

    def atualizar_data_fim_metas(self, old_plano):
        if (
            old_plano
            and self.data_fim != old_plano.data_fim
            and old_plano.data_fim > self.data_fim
        ):
            self.mov_teletrabalho.all().update(data_fim=self.data_fim)

    @property
    def icons(self):
        icons = []

        if self.situacao == STATUS_TELETRABALHO_BLOQUEADO:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-error",
                    "title": "Plano bloqueado",
                    "alt": "Bloqueado",
                }
            )

        elif self.situacao == STATUS_TELETRABALHO_DESBLOQUEADO:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-info",
                    "title": "Plano desbloqueado",
                    "alt": "Desbloqueado",
                }
            )

        elif self.situacao == STATUS_TELETRABALHO_REVOGADO:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-minus",
                    "title": "Plano revogado",
                    "alt": "Revogado",
                }
            )

        elif self.situacao == STATUS_TELETRABALHO_IGNORADO:
            icons.append(
                {
                    "iconCls": "icon-rh icon-core-publication-open",
                    "title": "Plano Ignorado",
                    "alt": "Ignorado",
                }
            )

        elif self.situacao == STATUS_TELETRABALHO_CONCLUIDO:
            icons.append(
                {
                    "iconCls": "icon-esocial icon-consult-icons",
                    "title": "Plano Concluído",
                    "alt": "Concluído",
                }
            )

        elif self.situacao == STATUS_TELETRABALHO_PENDENTE:
            icons.append(
                {
                    "iconCls": "icon-core icon-core-run-with-error",
                    "title": "Plano pendente devido à solicitação de cancelamento.",
                    "alt": "Plano pendente devido à solicitação de cancelamento.",
                }
            )
        else:
            icons.append(
                {
                    "iconCls": "icon-fopag icon-status",
                    "title": "Plano regular ",
                    "alt": "Regular",
                }
            )

        return icons

    def validate(self):
        self.validate_date_end_greater_than_date_start()
        self.validate_last_plan_date_start_greater_end_date()
        self.validate_update_end_date()
        self.validar_data_situacao()
        self.validar_periodo_conflitante()
        self.validar_lotacao_vazia()
        self.validar_tipo_pedido()
        self.validar_teletrabalho_ativo()
        self.validar_periodo_revogacao()
        return super().validate()

    def save(self):
        is_create = self.pk is None
        old_plano = (
            MovimentacaoTeletrabalho.objects.get(pk=self.pk) if self.pk else None
        )
        self.validate()
        super().save()
        self.atualizar_data_fim_metas(old_plano)
        if is_create:
            enviar_notificacao_cadastro_plano(self)


class HistoricoMovTeletrabalho(AuditTimestampModel):

    mov_teletrabalho = models.ForeignKey(
        MovimentacaoTeletrabalho,
        on_delete=models.PROTECT,
        related_name="historico_movteletrabalho",
        verbose_name="Movimentação Teletrabalho",
    )
    observacao = models.TextField(blank=True, null=True)
    acao = models.CharField(
        "Ação", max_length=50, choices=ACOES_TELETRABALHO, db_index=True
    )
    anexos = models.ManyToManyField(
        Arquivo, related_name="historico_movteletrabalhos", verbose_name="Anexos"
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def get_anexo_id(self):
        if self.anexos.exists():
            return self.anexos.first().pk
        return None

    @property
    def get_anexo_nome(self):
        if self.anexos.exists():
            return self.anexos.last().filename
        return None


class ActiveMetaTeletrabalhoManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class AllMetaTeletrabalhoManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset()


class MetaTeletrabalho(models.Model):
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim", blank=True, null=True)
    descricao = models.TextField(verbose_name="Descrição")
    meta = models.IntegerField(verbose_name="Meta")
    periodicity = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TELE_WORK_META_PERIODICITY"),
        blank=False,
        null=True,
    )
    mov_teletrabalho = models.ForeignKey(
        MovimentacaoTeletrabalho,
        related_name="mov_teletrabalho",
        verbose_name="Movimentação Teletrabalho",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        blank=True,
    )

    objects = ActiveMetaTeletrabalhoManager()
    manager = AllMetaTeletrabalhoManager()

    def __str__(self):
        return f"{self.descricao} - Meta: {self.meta}"

    class Meta:
        ordering = ["id"]

    def validate_date_end_greater_than_date_start(self):
        """A data de fim não pode ser menor que a data de início"""
        if self.data_fim and self.data_fim < self.data_inicio:
            raise Exception("A data fim deve ser maior que a data de início.")

    def validate_date_end_greater_than_date_start_work_plan(self):
        """A data inicio da meta seja maior ou igual a data inicio do plano de trabalho"""
        if self.data_inicio < self.mov_teletrabalho.data_inicio:
            raise Exception(
                " A data inicio da meta tem que ser maior ou igual a data inicio do plano de trabalho."
            )
        return True

    def validate(self):
        self.validate_date_end_greater_than_date_start()
        self.validate_date_end_greater_than_date_start_work_plan()

    def get_meta_atual(self):
        if self.pk:
            return MetaTeletrabalho.objects.get(pk=self.pk).meta
        return self.meta

    def meta_dias_mes(self, ano, mes):
        meta_dias_mes = calendar.monthrange(ano, mes)[1]
        primeiro_dias_mes = datetime(ano, mes, 1).date()
        ultimo_dia_mes = datetime(ano, mes, meta_dias_mes).date()
        if ultimo_dia_mes > self.data_fim:
            meta_dias_mes = NewDateRange(primeiro_dias_mes, self.data_fim).days
        elif self.data_inicio > primeiro_dias_mes:
            meta_dias_mes = NewDateRange(self.data_inicio, ultimo_dia_mes).days
        return meta_dias_mes

    def save(self):
        alteracao_meta = True if self.get_meta_atual() != self.meta else False
        self.validate()
        super().save()
        if alteracao_meta:
            enviar_notificacao_alteracao_meta(self.mov_teletrabalho, self)

    def inactivate(self):
        """
        Função para inativar uma instância de MetaTeletrabalho
        :returns: self (MetaTeletrabalho) Instância inativada
        """
        self.active = False
        self.save_base()
        enviar_notificacao_alteracao_meta(self.mov_teletrabalho, self)
        return self


class MembersTelecommuting(AuditTimestampModel):
    """
    Model responsável pelo controle de trabalho remoto de membros
    """

    employee = models.ForeignKey(
        Servidor,
        on_delete=models.PROTECT,
        verbose_name="Membro em trabalho remoto",
        related_name="member_teleworks",
        blank=True,
        null=True,
    )
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(verbose_name="Data Fim", blank=True, null=True)
    status = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TELECOMMUTING_STATUS"),
        verbose_name="Status",
        default=1,
    )
    telecommuting_reasons = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TELECOMMUTING_REASONS"),
        verbose_name="Razão do Trabalho Remoto",
        default=1,
    )
    publication = models.ForeignKey(
        Publicacao,
        on_delete=models.PROTECT,
        verbose_name="Publicação de trabalho remoto",
        null=True,
        blank=True,
    )

    @property
    def telecommuting_reason_description(self):
        if self.telecommuting_reasons:
            reason = Choice.objects.filter(
                app_label="rh",
                name="TELECOMMUTING_REASONS",
                value=self.telecommuting_reasons,
            ).first()
            return reason.description if reason else None
        return None

    def validate_if_is_member(self):
        if not self.employee.is_member:
            raise Exception("Somente membros podem ser cadastrados.")
        return True

    def validate_if_not_same_time(self):

        q_members_telecommuting = MembersTelecommuting.objects.filter(
            employee=self.employee,
            data_inicio__gte=self.data_inicio,
        )
        if self.data_fim is not None:
            q_members_telecommuting = q_members_telecommuting.filter(
                data_fim__lte=self.data_fim
            )

        q_members_telecommuting = q_members_telecommuting.exclude(id=self.id)
        if q_members_telecommuting.exists():
            raise Exception("Já existe um trabalho remoto cadastrado para esta data.")
        return True

    def validate(self):
        self.validate_if_is_member()
        self.validate_if_not_same_time()

    def save(self, *args, **kwargs):
        self.validate()
        hoje = date.today()
        if self.data_inicio > hoje:
            self.status = 3  # AGENDADO
        elif self.data_fim and self.data_fim < hoje:
            self.status = 2  # INATIVO
        else:
            self.status = 1  # ATIVO

        super(MembersTelecommuting, self).save(*args, **kwargs)


class DeclaracaoAtividadeQueryset(models.QuerySet):

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_exercicio__gt=range_.last)
                | (~Q(data_encerramento=None) & Q(data_encerramento__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_exercicio__gt=data)
                | (~Q(data_encerramento=None) & Q(data_encerramento__lt=data))
            )


class DeclaracaoAtividade(MovimentacaoPessoal):
    quadro = models.ForeignKey(
        "Quadro", null=True, blank=True, on_delete=models.CASCADE
    )
    data_exercicio = models.DateField(verbose_name="Exercício")
    data_encerramento = models.DateField(
        null=True, blank=True, verbose_name="Encerramento"
    )
    lotacao = models.ForeignKey(
        "Lotacao",
        null=True,
        blank=True,
        verbose_name="Local de trabalho",
        on_delete=models.CASCADE,
    )
    ativo = models.BooleanField(default=True, blank=True)
    turno = models.IntegerField(
        default=4, choices=Choice.get_choices_for("rh", "TURNO")
    )
    activity_as = models.CharField(
        default="I", max_length=1, blank=True, choices=INDICATIVO
    )
    main = models.BooleanField(default=False, verbose_name="Principal")
    main_schedule_date = models.DateField(
        null=True, blank=True, verbose_name="Data agendada para marcar principal"
    )

    objects = DeclaracaoAtividadeQueryset.as_manager()

    class Meta:
        verbose_name = "Declaração de Atividade"
        ordering = ("-data_exercicio",)

    def __str__(self):
        return self.servidor.pessoa_fisica.nome

    @property
    def situacao_funcional(self):
        return "ATIVO" if self.ativo else "INATIVO_DEMITIDO"

    def is_active(self, date=None):
        return is_active(
            today=date, date_start=self.data_exercicio, date_end=self.data_encerramento
        )

    def anotacao(self, *args, **kargs):
        professional = "Terceirizado"
        if self.quadro.cargo.indicativo == "E":
            professional = "Estagiário"
        elif self.quadro.cargo.indicativo == "V":
            professional = "Voluntário"
        elif self.quadro.cargo.indicativo == "A":
            professional = "Jovem Cidadão - Aprendiz"
        text = """Declaro, para os devidos fins de direito, que o(a) senhor(a) %s
        , credenciado(a) para exercer a função de %s, entrou em exercício junto à (ao) %s
        , no dia %s no turno %s.""" % (
            self.servidor.pessoa_fisica,
            professional,
            self.lotacao.nome,
            DateUtils.date_to_str(self.data_exercicio),
            self.get_turno_display(),
        )
        if self.data_encerramento:
            text = (
                text
                + "<p>Exercício encerrado no dia %s.<p/>"
                % DateUtils.date_to_str(self.data_encerramento)
            )
        text = text + (self.texto if self.texto else "")
        if self.anotacao_geral is None:
            anotacao_geral = AnotacaoGeral.manage_instance(
                servidor=self.servidor,
                tipo_documento=95,
                numero_documento=None,
                publicacao=None,
                data_portaria_inicio=self.data_exercicio,
                texto=text,
                resumo="Declaração de Entrada em Atividade: %s" % professional,
            )
            AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
            self.anotacao_geral = anotacao_geral
        else:
            anotacao_geral = AnotacaoGeral.objects.get(pk=self.anotacao_geral.pk)
            anotacao_geral.servidor = self.servidor
            anotacao_geral.tipo_documento = 95
            anotacao_geral.data_portaria_inicio = self.data_exercicio
            anotacao_geral.texto = text
            anotacao_geral.resumo = (
                "Declaração de Entrada em Atividade: %s" % professional
            )
            anotacao_geral.indireto = False
            anotacao_geral.save()
            AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)

    def validate_job_position(self):
        log.info(f"{self.quadro.cargo.indicativo}: {self.quadro.cargo}")
        if self.quadro.cargo.indicativo not in ("E", "T", "V", "A", "X"):
            raise Exception("Cargos aceitos: Estagiário, Terceirizado ou Voluntário")

        if self.servidor.tipo != self.quadro.cargo.indicativo:
            raise Exception(
                "Selecione um cargo do tipo %s"
                % self.servidor.get_tipo_display().title()
            )

    def validate_employee(self):
        da = DeclaracaoAtividade.objects.filter(
            servidor=self.servidor, lotacao=self.lotacao, ativo=True
        )
        if self.pk:
            da = da.exclude(pk=self.pk)
        if da.exists():
            raise Exception(
                "Não é permitido mais de um exercício ativo no mesmo local."
            )
        return True

    def validate_trainee(self):
        if self.servidor.tipo == "E" and not self.data_encerramento:
            raise Exception("Preencha a data de encerramento.")
        return True

    def validate(self):
        self.validate_trainee()
        self.validate_job_position()
        self.validate_employee()
        return super().validate()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.activity_as = self.quadro.cargo.indicativo
        self.ativo = self.is_active()
        self.set_main()
        super().save(*args, **kargs)

    def update_active(self):
        try:
            is_active = self.is_active()
            if self.ativo != is_active:
                message = f"{self} - atualiza ativo: {self.ativo} => {is_active}"
                log.info(message)
                print(message)
                DeclaracaoAtividade.objects.filter(pk=self.pk).update(ativo=is_active)
        except Exception as err:
            log.exception(err)
            print(err)

    @classmethod
    def cmd_update_active(cls, pk=[]):
        log.info("Atualizando campo ativo de Declarações de Atividade.")
        print("Atualizando campo ativo de Declarações de Atividade.")
        today = datetime.now().date()
        query = (
            Q(data_encerramento__lt=today)
            | Q(data_encerramento=None)
            | Q(data_exercicio=today)
        )
        if pk:
            query = Q(pk__in=pk)
        query = DeclaracaoAtividade.objects.filter(query)
        for da in query.order_by("servidor"):
            da.update_active()

    def set_main(self):
        date = datetime.now().date()
        if (
            not self.servidor.member_type_by_possession
            and self.is_active()
            and not DeclaracaoAtividade.objects.filter(
                Q(data_exercicio__lte=date)
                & (Q(data_encerramento__gte=date) | Q(data_encerramento=None))
            )
            .filter(main=True)
            .exists()
        ):
            self.main = True

    @classmethod
    def cmd_main_schedule_date(cls):
        """Este método é responsável por atualizar os exercícios para main = True quando main_schedule_date por preenchido."""
        today = datetime.now().date()
        query = Q(main_schedule_date=today)

        query = DeclaracaoAtividade.objects.filter(query)
        total = query.count()
        count = 0
        print(
            f"Processo de atualização de principal em declaração de atividade. Total {count} de {total}."
        )
        for dec_ativ in query:
            dec_ativ.action_set_main(True)
            count += 1
            print(f"{count} de {total} -> {dec_ativ}")

    def action_set_main(self, main):
        try:
            with transaction.atomic():
                DeclaracaoAtividade.objects.filter(
                    servidor=self.servidor, main=True
                ).update(main=False)
                DeclaracaoAtividade.objects.filter(pk=self.pk).update(main=main)
        except Exception as err:
            log.exception(err)


class BenefitMovementQueryset(models.QuerySet):

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_exercicio__gt=range_.last)
                | (~Q(data_encerramento=None) & Q(data_desligamento__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_exercicio__gt=data)
                | (~Q(data_desligamento=None) & Q(data_desligamento__lt=data))
            )


class BenefitMovement(MovimentacaoPosse):
    benefit_number = models.CharField(
        "Número do Benefício", max_length=20, blank=True, null=True
    )
    founder_employee = models.ForeignKey(
        "Servidor",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mov_beneficiaries",
    )
    legal_representative = models.ForeignKey(
        "PessoaFisica", on_delete=models.PROTECT, null=True, blank=True
    )
    type_legal_representative = models.IntegerField(
        "Tipo de representante",
        choices=Choice.get_choices_for("rh", "TIPO_REPRESENTANTE_LEGAL"),
        default=1,
        null=True,
        blank=True,
    )
    quota = models.DecimalField(
        max_digits=10, decimal_places=6, default=100, null=True, blank=True
    )
    benefit_base_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True
    )
    benefit_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True
    )
    reference_parity = models.ForeignKey(
        "gfp.ReferenciaNiveis2D", on_delete=models.SET_NULL, null=True, blank=True
    )
    benefit_role = models.ForeignKey(
        "esocial.ItemTable",
        verbose_name="Regra do benefício",
        related_name="benefit_movements_types",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    termination_reason = models.ForeignKey(
        "esocial.ItemTable",
        verbose_name="Motivo da cessação do benefício.",
        related_name="benefit_movements_reasons",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    type_pension_death = models.IntegerField(
        "Tipo de Pensão por Morte",
        choices=Choice.get_choices_for("rh", "TYPE_PENSION_DEATH"),
        null=True,
        blank=True,
    )
    reactivated_benefit = models.ForeignKey(
        "BenefitMovement",
        related_name="reactivations",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    situation = models.IntegerField(
        "Situação do Benefício",
        choices=Choice.get_choices_for("rh", "BENEFIT_SITUATION"),
        default=1,
        blank=True,
        null=True,
    )
    previous_organ = models.ForeignKey(
        "UnidadeAdministrativa",
        related_name="benefit_movements_previous_organs",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    previous_benefit_number = models.CharField(
        "Número do Benefício Anterior", max_length=20, blank=True, null=True
    )
    transfer_date = models.DateField(
        verbose_name="Data de Transferência", blank=True, null=True
    )
    after_organ = models.ForeignKey(
        "UnidadeAdministrativa",
        related_name="benefit_movements_after_organs",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    paridade_salarial = models.BooleanField(
        verbose_name="Paridade Salarial", default=False
    )
    beneficio_integral = models.BooleanField(
        verbose_name="Beneficio Integral", default=False
    )

    objects = BenefitMovementQueryset.as_manager()

    ALLOWED_TYPE_BY_POSSESSION = ("MAP", "MAP2", "SAP", "APO", "BFP")

    SAME_ORGAN = 1
    TRANFER_ORGAN = 2
    CPF_CHANGE = 3

    class Meta:
        verbose_name = "Movimentação de Benefício"
        ordering = ("-data_exercicio",)

    def __str__(self):
        return f"{self.servidor} - {self.benefit_number}"

    @property
    def tipo_carreira(self):
        return "BENEFICIO"

    def validate_reactivated(self):
        if (
            self.reactivated_benefit is not None
            and BenefitMovement.objects.filter(
                reactivated_benefit=self.reactivated_benefit
            ).count()
            > 1
        ):
            raise Exception("Esse benefício já foi reativado.")
        return True

    def validate_fields_reactivated(self):
        if self.reactivated_benefit:
            if (
                self.financial_effect_date is None
                or self.financial_effect_date is None
                or self.publicacao_movimentacao is None
            ):
                raise Exception("Preencha todos os campos corretamente.")
        return True

    def reactivation(self, params):

        values = (
            "servidor",
            "benefit_number",
            "founder_employee",
            "situation",
            "benefit_role",
            "legal_representative",
            "type_legal_representative",
            "type_pension_death",
            "reference_parity",
            "benefit_base_value",
            "benefit_value",
            "quota",
            "quadro",
            "previous_organ",
            "previous_benefit_number",
            "transfer_date",
            "data_posse",
        )

        try:
            benefit = self.__class__()

            for field in values:
                setattr(benefit, field, getattr(self, field, None))

            benefit.reactivated_benefit = self
            benefit.data_exercicio = datetime.strptime(
                params.get("data_exercicio"), "%d/%m/%Y"
            ).date()
            benefit.financial_effect_date = datetime.strptime(
                params.get("financial_effect_date"), "%d/%m/%Y"
            ).date()
            benefit.publicacao_movimentacao = Publicacao.objects.get(
                pk=params.get("publicacao_movimentacao")
            )
            benefit.number_process = params.get("number_process")
            benefit.judicial_decision = (
                True if params.get("judicial_decision") else False
            )
            benefit.anota = True if params.get("anota") else False
            benefit.texto = params.get("texto")

            benefit.save()
        except Exception as e:
            raise e

    def set_benefit_number(self):
        """Este método cria um número do benefício válido. Também checa se já foi utilizado.
            - Campo incremental, 2 (pos)
            - Tipo da tabela de benefício (Tabela 25), 4 (pos)
            - CPF do beneficiário, 11 (pos)

        Este método também seta o número do benefício.

        Returns:
            self.benefit_number (str): Número gerado.
        """

        def _generate_benefit_number(sequential=1):
            self.benefit_number = (
                f"{sequential:02}{self.benefit_role.code:0>4}{self.servidor.pessoa_fisica.cpf:0>11}"
                if self.benefit_role
                else None
            )

        _generate_benefit_number()
        sequential = 1
        benefits = list(
            self.__class__.objects.filter(servidor=self.servidor).values_list(
                "benefit_number", flat=True
            )
        )
        while self.benefit_number in benefits:
            sequential += 1
            _generate_benefit_number(sequential=sequential)

        return self.benefit_number

    def validate_if_cargo_is_empty(self):
        pass

    def validate_tranfer_fields(self):
        if self.situation == self.TRANFER_ORGAN and (
            not self.previous_organ
            and not self.previous_benefit_number
            and self.transfer_date is None
        ):
            raise Exception(
                "Preencha os campos relativos ao órgão de origem do benefício"
            )

    def validate_required_fields(self):
        required_fields = [
            "benefit_number",
            "situation",
            "benefit_role_id",
            "data_exercicio",
        ]
        error_fields = []

        for field in self._meta.concrete_fields:
            if (
                field.attname in required_fields
                and getattr(self, field.attname, None) is None
            ):
                error_fields.append(f'"{field.verbose_name}"')

        if len(error_fields) > 0:
            message = ", ".join(error_fields)
            raise Exception(
                (
                    f"O campo {error_fields} é obrigatório."
                    if len(error_fields) == 0
                    else f"Os campos {message} são obrigatórios."
                ),
            )

    def validate_cargo(self):
        if not hasattr(self, "quadro") or self.quadro is None:
            raise Exception("É necessário selecionar o cargo paridade do servidor.")

    def validate(self):
        self.validate_cargo()
        self.validate_required_fields()
        self.validate_tranfer_fields()
        self.validate_fields_reactivated()
        self.validate_reactivated()

    def shutdown_extrapaymentperiod(self):
        mov_beneficio = BenefitMovement.objects.get(pk=self.pk)
        if not mov_beneficio.data_desligamento and self.data_desligamento:
            extra_payment_period = self.servidor.extrapaymentperiods.filter(
                extra_payment__slug="BENEFICIO", end_validity__isnull=True
            )
            if (
                extra_payment_period.exists()
                and extra_payment_period.first().end_validity is None
            ):
                extra_payment_period.update(end_validity=self.data_desligamento)

    @transaction.atomic
    def save(self, *args, **kwargs):
        label_provision = None
        if any("label_provision" in sub for sub in args):
            label_provision = args[0]["label_provision"]
            self.validate_action_menu(label_provision)
        if not self.benefit_number:
            self.benefit_number = self.set_benefit_number()
        self.set_tipo_movcarreira()
        self.validate()
        if self.pk:  # Isn't a create execution
            self.shutdown_extrapaymentperiod()
        super().save(*args, **kwargs)


class SuspensionBenefit(ListDatedModel):
    REASON_TYPE = (
        ("01", "Suspensão por não recadastramento"),
        ("99", "Outros motivos de suspensão"),
    )

    benefit_movement = models.ForeignKey(
        "rh.BenefitMovement",
        related_name="benefit_suspensions",
        on_delete=models.PROTECT,
    )
    reason = models.CharField("Motivo da Suspensão", max_length=2, choices=REASON_TYPE)
    reason_description = models.TextField(
        "Descrição do motivo da suspensão", null=True, blank=True
    )

    def __str__(self):
        return str(self.benefit_movement)


class Molestia(AuditTimestampModel):
    data_laudo = models.DateField(verbose_name="Data do laudo", null=True, blank=True)
    publicacao = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        verbose_name="Laudo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_vigencia = models.DateField(
        verbose_name="Data da vigência", null=True, blank=True
    )
    data_revisao = models.DateField(
        verbose_name="Data de revisão", null=True, blank=True
    )
    origem = models.SmallIntegerField(
        choices=Choice.get_choices_for("rh", "TIPO_ORIGEM_MOLESTIA"),
        verbose_name="Origem",
        blank=True,
        null=True,
    )
    cid = models.CharField(max_length=20, null=True, blank=True, verbose_name="CID")

    class Meta:
        verbose_name = "Pessoa"

    def __str__(self):
        return (
            f"Moléstia - {DateUtils.date_to_str(self.data_laudo)} - {self.publicacao}"
        )

    @transaction.atomic
    def save(self, *args, **kargs):
        self.validate()
        super(Molestia, self).save(*args, **kargs)

    def validate(self):
        self.validate_data_laudo()
        self.validate_data_vigencia()
        self.validate_data_revisao()
        self.validate_origem()

    def validate_data_laudo(self):
        if not self.data_laudo:
            raise Exception("Favor preencher o campo Data do laudo")

    def validate_data_vigencia(self):
        if not self.data_vigencia:
            raise Exception("Favor preencher o campo Data da vigência")

    def validate_data_revisao(self):
        if not self.data_revisao:
            raise Exception("Favor preencher o campo Data de revisão")

    def validate_origem(self):
        if not self.origem:
            raise Exception("Favor selecionar a Origem")


class DocumentoDigital(AuditTimestampModel):
    name = models.CharField(default="", max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, null=True, verbose_name="Descrição")
    arquivo = models.ForeignKey(
        "ged.Arquivo",
        null=True,
        blank=True,
        verbose_name="Arquivo",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Documento Digital"

    def __str__(self):
        return self.arquivo.filename if self.arquivo else ""

    @transaction.atomic
    def save(self, *args, **kargs):
        if self.name == "":
            self.name = self.arquivo.filename
        super(DocumentoDigital, self).save(*args, **kargs)


class DigitalDocument(AuditTimestampModel):
    name = models.CharField(default="", blank=True, max_length=260, verbose_name="Nome")
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")
    employee = models.ForeignKey(
        Servidor,
        null=True,
        blank=True,
        verbose_name="Servidor",
        related_name="digital_document",
        on_delete=models.SET_NULL,
    )
    person = models.ForeignKey(
        Pessoa,
        null=True,
        blank=True,
        verbose_name="Servidor",
        related_name="digital_document",
        on_delete=models.SET_NULL,
    )
    file = models.ForeignKey(
        "ged.Arquivo",
        verbose_name="Arquivo",
        related_name="digital_document",
        on_delete=models.PROTECT,
    )
    document_type = models.IntegerField(
        default=57,
        choices=Choice.get_choices_for("rh", "DIGITAL_DOCUMENT_TYPE"),
        verbose_name="Tipo de Documento",
    )
    date_start = models.DateField(
        auto_now_add=True, blank=True, verbose_name="Data início"
    )
    date_end = models.DateField(null=True, blank=True, verbose_name="Data fim")
    active = models.BooleanField(default=False, blank=True, verbose_name="Ativo")
    my_origin_cache_unicode = models.CharField(
        verbose_name="Cache", max_length=200, null=True, blank=True
    )

    personal_moviment = models.ForeignKey(
        "MovimentacaoPessoal",
        verbose_name="Afastamento",
        blank=True,
        null=True,
        related_name="digital_document",
        on_delete=models.CASCADE,
    )
    annotation = models.ForeignKey(
        "AnotacaoGeral",
        verbose_name="Anotação",
        blank=True,
        null=True,
        related_name="digital_document",
        on_delete=models.CASCADE,
    )

    digital_document_mandatory = [
        ADDRESS_CERTIFICATE,
    ]

    class Meta:
        verbose_name = "Documento Digital"
        ordering = ("-date_end",)

    def __str__(self):
        return self.file.filename if self.file else ""

    def is_active(self, date=None):
        return is_active(today=date, date_start=self.date_start, date_end=self.date_end)

    def set_active(self, date=None):
        self.active = self.is_active()

    def make_cache(self):
        cache = "%s %s" % (self.employee, self.get_document_type_display())
        if self.personal_moviment:
            cache = "%s : %s" % (
                self.employee.matricula,
                self.personal_moviment.my_origin,
            )
        elif self.annotation:
            cache = "%s" % (self.annotation.my_origin)
        return cache[0:199]

    def validate(self):
        return True

    @classmethod
    def validate_mandatory_digital_document(cls, employee, exclude=[]):
        # TODO: CRIAR UMA VALIDAÇÃO PARA CADA CAMPO(TIPO)
        from copy import deepcopy

        message = ""
        digital_document_mandatory = deepcopy(
            DigitalDocument.digital_document_mandatory
        )
        for ex in exclude:
            try:
                digital_document_mandatory.remove(ex)
            except Exception:
                pass
        digital_documents = DigitalDocument.objects.filter(
            employee=employee, document_type__in=digital_document_mandatory, active=True
        )
        for value in digital_document_mandatory:
            found = digital_documents.filter(document_type=value).exists()
            if value == ADDRESS_CERTIFICATE and not found:
                message += (
                    " É necessário anexar documento digital %s."
                    % DIGITAL_DOCUMENT_TYPE.get(value)
                )
        if message:
            raise Exception(message)
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        self.set_active()
        if not self.name:
            self.name = self.file.filename

        self.my_origin_cache_unicode = self.make_cache()

        if self.employee and not self.person:
            self.person = self.employee.pessoa_fisica

        if self.person and not self.employee:
            if hasattr(self.person, "pessoafisica"):
                employee = Servidor.objects.filter(
                    pessoa_fisica=self.person.pessoafisica, ativo=True
                ).last()
                self.employee = employee

        self.validate()
        super(DigitalDocument, self).save(*args, **kargs)

    @classmethod
    def _update_cache_active(cls, digital_document):
        if digital_document.active != digital_document.is_active():
            DigitalDocument.objects.filter(pk=digital_document.pk).update(
                active=digital_document.is_active()
            )

    @classmethod
    def cmd_update_active(cls, digital_document=[]):
        today = datetime.now().date()
        query = Q(date_end__lt=today) | Q(date_end=None) | Q(date_start=today)
        if len(digital_document) > 0:
            query = Q(pk__in=digital_document)

        digital_documents = DigitalDocument.objects.filter(query)
        log.info(
            "DigitalDocument: quantidade para atualizar %s" % digital_documents.count()
        )
        for digital_document in digital_documents.order_by("employee"):
            DigitalDocument._update_cache_active(digital_document)


class DigitalDocumentNaturalPerson(DigitalDocument):
    document_natural_person = models.ForeignKey(
        Documento,
        verbose_name="Documento da Pessoa Física",
        related_name="digital_document_natural_person",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Documento Digital da Pessoa Física"

    def __str__(self):
        return "%s - %s" % (
            self.file.filename if self.file else "",
            self.document_natural_person,
        )

    @transaction.atomic
    def save(self, *args, **kargs):
        if not self.employee:
            employee = (
                self.document_natural_person.naturalpersons.last().servidor__set.filter()
            )
            self.employee = (
                employee.filter(ativo=True).last()
                if employee.filter(ativo=True).exists()
                else employee.last()
            )
        if not self.person and self.employee:
            self.person = self.employee.pessoa_fisica
        super(DigitalDocumentNaturalPerson, self).save(*args, **kargs)


class Prorrogacao(AuditTimestampModel):
    class Meta:
        verbose_name = "Prorrogação"
        db_table = "rh_prorrogacao"

    data_inicio = models.DateField(blank=True, verbose_name="Data Início")
    data_fim = models.DateField(blank=True, verbose_name="Data Fim")
    publicacao = models.ForeignKey(
        Publicacao,
        null=True,
        blank=True,
        related_name="prorrogacao",
        verbose_name="Publicação",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        if self.publicacao:
            return "Prorrogação número %s de %s a %s" % (
                Publicacao.get_dados_publicacao(self.publicacao)[2],
                DateUtils.date_to_str(self.data_inicio),
                DateUtils.date_to_str(self.data_fim),
            )
        else:
            return "Prorrogação de %s a %s" % (
                DateUtils.date_to_str(self.data_inicio),
                DateUtils.date_to_str(self.data_fim),
            )

    def full_clean(self, exclude=None, validate_unique=True):
        self._validate_if_data_inicio_is_empty()
        self._validate_if_data_fim_is_empty()
        self._validate_if_publicacao_is_empty()

        try:
            super(Prorrogacao, self).full_clean(exclude, validate_unique)
        except ValidationError as validation_error:
            raise ValidationError(validation_error)

    def _validate_if_data_inicio_is_empty(self):
        if not self.data_inicio:
            raise Exception("Por favor, preencha o campo Data Início.")

    def _validate_if_data_fim_is_empty(self):
        if not self.data_fim:
            raise Exception("Por favor, preencha o campo Data Fim.")

    def _validate_if_publicacao_is_empty(self):
        if not self.publicacao:
            raise Exception("Por favor, preencha o campo Publicação.")

    @transaction.atomic
    def save(self, *args, **kargs):
        super(Prorrogacao, self).save(*args, **kargs)


class ProfissionalSaude(AuditTimestampModel):
    pessoa_fisica = models.ForeignKey(
        PessoaFisica,
        related_name="profissionalsaude",
        verbose_name="Pessoa",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        message = "%s" % self.pessoa_fisica
        if self.pessoa_fisica.professional_council:
            message = "%s - %s" % (
                self.pessoa_fisica.professional_council.get_class_organ_display(),
                message,
            )
        return message


class CargaHorariaQueryset(models.QuerySet):
    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(data_inicio__gt=range_.last)
                | (~Q(data_fim=None) & Q(data_fim__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(data_inicio__gt=data) | (~Q(data_fim=None) & Q(data_fim__lt=data))
            )


class CargaHoraria(RHObject):
    publicacao = models.ForeignKey(
        Publicacao, null=True, blank=True, on_delete=models.CASCADE
    )
    tipo = models.IntegerField(
        choices=Choice.get_choices_for("rh", "WORKLOAD_TYPE"), default=1
    )
    quantidade = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )
    data_inicio = models.DateField(verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    active = models.BooleanField(default=False, verbose_name="Ativo")
    duration = models.PositiveIntegerField(
        default=0, verbose_name="Duração em Minutos", blank=True
    )
    jornada_trabalho = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        verbose_name="Jornada de Trabalho",
        on_delete=models.SET_NULL,
    )

    objects = CargaHorariaQueryset.as_manager()

    class Meta:
        ordering = ("servidor", "-data_inicio")

    def __str__(self):
        return "%s: %s horas %s - Início %s Fim %s" % (
            self.servidor,
            self.quantidade,
            self.get_tipo_display(),
            DateUtils.date_to_str(self.data_inicio),
            DateUtils.date_to_str(self.data_fim) if self.data_fim else "----",
        )

    def activate_workload_by_date(self):
        """
        Função que ativa a Carga Horária se a data inicial for superior a data de hoje
        """
        if self.data_inicio == date.today() and self.active is False:
            try:
                self.active = True
                self.save()
                log.info(f"Ativando Carga horária do servidor - {self}")
                print(f"Ativando Carga horária do servidor - {self}")
            except Exception as e:
                log.info(f"Erro ao ativar a Carga horária do servidor - {self} - {e}")
                print(f"Erro ao ativar a Carga horária do servidor - {self} - {e}")

    def inactivate_workload_by_date(self):
        """
        Função que inativa a Carga Horária se a data for for superior a data de hoje
        """
        if self.data_fim and self.data_fim <= date.today() and self.active is True:
            try:
                self.active = False
                self.save()
                log.info(f"Desativando Carga horária do servidor - {self}")
                print(f"Desativando Carga horária do servidor - {self}")
            except Exception as e:
                log.info(
                    f"Erro ao desativar a Carga horária do servidor - {self} - {e}"
                )
                print(f"Erro ao desativar a Carga horária do servidor - {self} - {e}")

    def manage_employee_workload(self):
        empl_employee = CargaHoraria.objects.filter(
            Q(servidor=self.servidor)
            & (
                Q(data_inicio__lte=self.data_inicio)
                | Q(data_fim__gte=self.data_inicio)
                | Q(data_fim=None)
            )
        ).exclude(data_fim__lt=self.data_inicio)
        if self.data_fim:
            empl_employee = empl_employee.exclude(data_inicio__gt=self.data_fim)
        if self.pk:
            empl_employee = empl_employee.exclude(pk=self.pk)
        for empl in empl_employee.filter():
            dat_end_new = self.data_inicio - relativedelta(days=1)
            if empl.data_inicio > dat_end_new:
                empl.delete(force=True)
            else:
                empl.data_fim = dat_end_new
                empl.save()

    @property
    def jornada_semanal(self):
        if self.jornada_trabalho:
            return self.jornada_trabalho.jornada_semanal
        return 0

    @property
    def day(self):
        if self.quantidade is None:
            return 0.0
        return (float(self.quantidade) / 5.0) if self.tipo == 1 else 8.0

    @transaction.atomic
    def save(self, *args, **kargs):
        from rh.scripts.atualizar_carga_horaria import buscar_data_fim_carga

        if (
            self.servidor
            and MovimentacaoPosse.objects.filter(servidor=self.servidor).exists()
        ):
            self.validar_inicio_carga()

        self.active = self.is_active()

        if not self.data_fim and self.jornada_trabalho:
            self.data_fim = buscar_data_fim_carga(self.servidor, self.jornada_trabalho)

        if not self.quantidade and self.jornada_trabalho:
            self.quantidade = self.jornada_trabalho.jornada_semanal
        self.duration = int(self.quantidade * 60)

        self.manage_employee_workload()

        super(CargaHoraria, self).save(*args, **kargs)

    def validar_inicio_carga(self):
        """
        Valida se a data de início da carga horária (self.data_inicio):
        - É maior ou igual à data de início de vigência da jornada (self.jornada_trabalho.date_start);
        - E não é anterior à data de exercício do servidor (self.servidor.data_exercicio).

        Se alguma dessas condições não for atendida, lança uma exceção.
        """
        if not self.jornada_trabalho or not self.jornada_trabalho.date_start:
            raise Exception(
                "Jornada de trabalho não definida corretamente ou sem data de início."
            )

        dt_jornada = self.jornada_trabalho.date_start
        dt_carga = self.data_inicio

        if not self.servidor or not self.servidor.data_exercicio:
            raise Exception("Data de exercício do servidor não definida.")
        dt_exercicio = self.servidor.data_exercicio

        if dt_carga < dt_jornada:
            raise Exception(
                "A data de início da carga horária deve ser maior ou igual à data de início da vigência da Jornada de Trabalho ("
                + dt_jornada.strftime("%d/%m/%Y")
                + ")."
            )

        if dt_carga < dt_exercicio:
            raise Exception(
                "A data de início da carga horária não pode ser anterior à data de exercício do servidor ("
                + dt_exercicio.strftime("%d/%m/%Y")
                + ")."
            )

        return True

    def validar_servidores_carga_inativa(self):
        """
        Este método valida a Carga Horária para que nenhum Servidor fique sem Carga Horária ativa.
        """
        if (
            self.servidor.ativo == True
            and CargaHoraria.objects.filter(servidor=self.servidor, active=True).count()
            == 1
        ):
            raise Exception(
                f"""Não é possível inativar a Carga Horária, pois o Servidor ficará sem Carga Horária ativa.
                                Cadastre uma nova Carga Horária para substituir essa: {self.servidor}."""
            )

    def delete(self, force=False, *args, **kargs):
        if not force:
            self.validar_servidores_carga_inativa()
        CargaHoraria.objects.filter(pk=self.pk).update(active=False)

    def is_active(self, data=None):
        return is_active(
            today=data, date_start=self.data_inicio, date_end=self.data_fim
        )

    def anotacao(self, *args, **kargs):
        tipo = Publicacao.get_tipo(self.publicacao)
        if self.anotacao_geral is None:
            anotacao_geral = AnotacaoGeral.manage_instance(
                servidor=self.servidor,
                tipo_documento=tipo,
                publicacao=self.publicacao,
                data_portaria_inicio=self.data_inicio,
                texto=self.get_texto() + " " + (self.texto if self.texto else ""),
                resumo="CARGA HORÁRIA",
            )
            AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
            self.anotacao_geral = anotacao_geral
        else:
            anotacao_geral = AnotacaoGeral.objects.get(pk=self.anotacao_geral.pk)
            anotacao_geral.publicacao = self.publicacao
            anotacao_geral.data_portaria_inicio = self.data_inicio
            anotacao_geral.texto = (
                self.get_texto() + " " + (self.texto if self.texto else "")
            )
            anotacao_geral.servidor = self.servidor
            anotacao_geral.tipo_documento = tipo
            anotacao_geral.indireto = False
            anotacao_geral.save()
            AnotacaoGeral.objects.filter(pk=anotacao_geral.pk).update(indireto=True)
        return True

    def get_texto(self):
        texto = ""
        try:
            """
            Estabelecer carga horária, para %(texto_servidor)s, de %(carga_horaria)s %(tipo_carga_horaria)s
            conforme %(numero_lei)s a partir de %(data_inicio)s.

            Alterar carga horária, do(a) %(texto_servidor)s, para %(carga_horaria)s %(tipo_carga_horaria)s
            conforme %(numero_lei)s a partir de %(data_inicio)s.
            """
            arquivo = "cargahoraria.txt"
            if CargaHoraria.objects.filter(servidor=self.servidor).exists():
                arquivo = "cargahoraria_alteracao.txt"
            with codecs.open(
                "%s/%s" % (templates.__path__[0], arquivo), "r", "utf-8"
            ) as fd:
                tpl = fd.read()
                texto = tpl % {
                    "carga_horaria": self.quantidade,
                    "tipo_carga_horaria": self.get_tipo_display(),
                    "numero_lei": (
                        ("%s%s" % (self.publicacao.numero, self.publicacao.ano))
                        if self.publicacao
                        else ""
                    ),
                    "data_inicio": DateUtils.date_to_str(self.data_inicio),
                    "texto_servidor": "%s %s"
                    % (self.servidor.texto_servidor(), self.servidor),
                }
        except Exception as err:
            log.exception(err)
        return texto

    @classmethod
    def cmd_update_workload(cls, workload=[]):
        """ """
        log.info(
            "Comando para criar/atualizar carga horária do servidor caso esteja pendente."
        )
        today = datetime.now().date()
        query = Q(data_fim__lt=today)
        if len(workload) > 0:
            query = Q(pk__in=workload)
        for workload in CargaHoraria.objects.filter(Q(servidor__ativo=True) & query):
            try:
                CargaHoraria.create_workload_by_possession(workload.servidor)
            except Exception as err:
                log.exception(err)

    @classmethod
    def do_create_workload(cls, **kwargs):
        date_start = kwargs.get("data_inicio")
        workload = None
        created = False
        try:
            workloads = CargaHoraria.objects.filter(
                Q(servidor=kwargs.get("servidor"))
                & Q(data_inicio__lte=date_start)
                & (Q(data_fim__gte=date_start) | Q(data_fim=None))
            )
            if not workloads.exists():
                workload, created = CargaHoraria.objects.get_or_create(
                    servidor=kwargs.get("servidor"),
                    data_inicio=date_start,
                    defaults={
                        "publicacao": kwargs.get("publicacao"),
                        "tipo": kwargs.get("tipo", 1),
                        "quantidade": kwargs.get("quantidade"),
                        "data_fim": kwargs.get("data_fim"),
                    },
                )
        except Exception as err:
            log.exception(err)
        return workload, created

    @classmethod
    def create_workload_by_possession(cls, employee):
        """
        Este método cria a nova carga horária baseada na posse ativa que possuir a
        maior carga horária.
        """
        workload = None
        created = False
        possessions = employee.posses_ativas
        possession = possessions.filter(
            quadro__cargo__tipo_lei_cargo__in=("CM", "FC")
        ).last()
        if not possession:
            possession = possessions.last()
        if possession and possession.quadro:
            workload, created = CargaHoraria.do_create_workload(
                servidor=employee,
                publicacao=possession.publicacao_movimentacao,
                data_inicio=possession.data_exercicio,
                quantidade=possession.quadro.carga_horaria if possession.quadro else 35,
                tipo=possession.quadro.tipo_carga_horaria if possession.quadro else 1,
            )
        else:
            log.info("Servidor %s não possui provimento." % employee)
        return created


class HoursWorkContract(AuditTimestampModel):
    title = models.CharField(
        default="NÃO INFORMADO", max_length=100, verbose_name="Título"
    )
    code = models.CharField(
        unique=True, max_length=30, verbose_name="Código", null=True, blank=True
    )
    # mudar esse trem
    date_start = models.DateField(verbose_name="Data Início")
    date_end = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    time_start = models.CharField(max_length=4, verbose_name="Horário de Início")
    time_end = models.CharField(max_length=4, verbose_name="Horário de Fim")
    duracao_intervalo = models.CharField(
        max_length=4, default="0200", verbose_name="Duração do Intervalo", blank=True
    )
    duration = models.PositiveIntegerField(
        default=0, verbose_name="Duração da Jornada em Minutos", blank=True
    )
    duration_hour = models.DecimalField(
        default=0,
        max_digits=14,
        decimal_places=2,
        verbose_name="Duração da Jornada em Horas",
        blank=True,
    )
    flexible = models.BooleanField(default=True, verbose_name="Flexível")
    publication = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        verbose_name="Publicação",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(default=False)
    tipo_posse = models.CharField(
        verbose_name="Tipos de posse", max_length=250, null=True, blank=True
    )

    class Meta:
        verbose_name = "Contrato de Horário de Trabalho"

    def __str__(self):
        return f"{self.title} - {self.time_start_formated} -> {self.time_end_formated}"

    @property
    def time_start_formated(self):
        return f"{self.time_start[0:2]}:{self.time_start[2:4]}"

    @property
    def time_end_formated(self):
        return f"{self.time_end[0:2]}:{self.time_end[2:4]}"

    @property
    def duracao_intervalo_formatado(self):
        return f"{self.duracao_intervalo[0:2]}:{self.duracao_intervalo[2:4]}"

    def is_active(self, date=None):
        return is_active(today=date, date_start=self.date_start, date_end=self.date_end)

    @classmethod
    def update_duration(cls, instance):
        if instance.duration != instance.duration_counter:
            instance.save()

    @classmethod
    def convert_timestring_to_minute(cls, start="", end=""):
        result = 0
        hour_start = start[0:2]
        hour_end = end[0:2]
        minute_start = start[2:4]
        minute_end = end[2:4]
        now = datetime.now()
        start = datetime(
            now.year, now.month, now.day, int(hour_start), int(minute_start), 0
        )
        end = datetime(now.year, now.month, now.day, int(hour_end), int(minute_end), 0)
        result = end - start
        return result.total_seconds() / 60

    @property
    def duration_interval_count(self):
        duration = 0
        for interval in self.intervals.filter():
            duration += interval.duration
        return duration

    @property
    def duracao_intervalo_minutos(self):
        horas = int(self.duracao_intervalo[0:2])
        minutos = int(self.duracao_intervalo[2:4])
        return horas * 60 + minutos

    @property
    def duration_counter(self):
        return (
            HoursWorkContract.convert_timestring_to_minute(
                self.time_start, self.time_end
            )
            - self.duracao_intervalo_minutos
        )

    @property
    def jornada_semanal(self):
        duracao_semanal = self.duration * 5
        return duracao_semanal / 60

    def validar_codigo_unico(self):
        """
        Se for cadastro (não está alterando um registro), cria um novo código (sequencial)
        """
        if not self.pk:
            ultimo_codigo = (
                HoursWorkContract.objects.annotate(
                    code_int=Cast("code", IntegerField())
                )
                .order_by("code_int")
                .last()
            )
            self.code = int(ultimo_codigo.code) + 1

    def validate(self):
        start = self.time_start[0:2]
        end = self.time_end[0:2]
        if start > end:
            raise Exception("O final deve ser menor que o início.")

        duracao = HoursWorkContract.convert_timestring_to_minute(
            self.time_start, self.time_end
        )
        if self.duracao_intervalo_minutos > duracao:
            raise Exception(
                "A duração do intervalo não pode ser maior que o período entre o início e o fim."
            )

        self.validar_codigo_unico()

        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        self.active = self.is_active()
        self.time_start = self.time_start.replace(":", "")
        self.time_end = self.time_end.replace(":", "")
        self.duracao_intervalo = self.duracao_intervalo.replace(":", "")
        log.info(self.duracao_intervalo)
        self.duration = self.duration_counter
        self.duration_hour = self.duration / 60

        self.validate()

        super(HoursWorkContract, self).save(*args, **kargs)

    def full_clean(self, exclude=None, validate_unique=True):
        try:
            super(HoursWorkContract, self).full_clean(
                exclude=exclude, validate_unique=validate_unique
            )
        except ValidationError as err:
            err.error_dict.pop("time_start")
            err.error_dict.pop("time_end")
            err.error_dict.pop("duracao_intervalo")
            if list(err.error_dict.keys()):
                raise err


class WorkHourInterval(AuditTimestampModel):
    hours_work_contract = models.ForeignKey(
        HoursWorkContract, related_name="intervals", on_delete=models.PROTECT
    )
    code = models.CharField(unique=True, max_length=30, verbose_name="Código")
    title = models.CharField(max_length=100, verbose_name="Título")
    type_interval = models.IntegerField(
        default=2, choices=Choice.get_choices_for("rh", "TYPE_INTERVAL")
    )
    time_start = models.CharField(max_length=4, verbose_name="Horário de Início")
    time_end = models.CharField(max_length=4, verbose_name="Horário de Fim")
    duration = models.PositiveIntegerField(
        default=0, verbose_name="Duração em Minutos", blank=True
    )
    duration_hour = models.DecimalField(
        default=0,
        max_digits=14,
        decimal_places=2,
        verbose_name="Duração em Horas",
        blank=True,
    )

    class Meta:
        verbose_name = "Intervalo de Horário de Trabalho"

    def __str__(self):
        return "%s - %s -> %s - %s" % (
            self.title,
            self.time_start_formated,
            self.time_end_formated,
            self.hours_work_contract,
        )

    @property
    def time_start_formated(self):
        return "%s:%s" % (self.time_start[0:2], self.time_start[2:4])

    @property
    def time_end_formated(self):
        return "%s:%s" % (self.time_end[0:2], self.time_end[2:4])

    @transaction.atomic
    def save(self, *args, **kargs):
        self.time_start = self.time_start.replace(":", "")
        self.time_end = self.time_end.replace(":", "")

        self.duration = HoursWorkContract.convert_timestring_to_minute(
            self.time_start, self.time_end
        )
        self.duration_hour = self.duration / 60

        super(WorkHourInterval, self).save(*args, **kargs)

    def full_clean(self, exclude=None, validate_unique=True):
        try:
            super(WorkHourInterval, self).full_clean(
                exclude=exclude, validate_unique=validate_unique
            )
        except ValidationError as err:
            err.error_dict.pop("time_start")
            err.error_dict.pop("time_end")
            if list(err.error_dict.keys()):
                raise err


class HoursWorkContractWorkload(AuditTimestampModel):
    title = models.CharField(max_length=100)
    texto = models.CharField(max_length=400, null=True, blank=True)
    day_1 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day1",
        verbose_name="Domingo",
        on_delete=models.PROTECT,
    )
    day_2 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day2",
        verbose_name="Segunda",
        on_delete=models.PROTECT,
    )
    day_3 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day3",
        verbose_name="Terça",
        on_delete=models.PROTECT,
    )
    day_4 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day4",
        verbose_name="Quarta",
        on_delete=models.PROTECT,
    )
    day_5 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day5",
        verbose_name="Quinta",
        on_delete=models.PROTECT,
    )
    day_6 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day6",
        verbose_name="Sexta",
        on_delete=models.PROTECT,
    )
    day_7 = models.ForeignKey(
        "HoursWorkContract",
        null=True,
        blank=True,
        related_name="workloads_day7",
        verbose_name="Sábado",
        on_delete=models.PROTECT,
    )
    employees = models.ManyToManyField(
        "rh.Servidor",
        through="EmployeeHoursWorkContractWorkload",
        verbose_name="Servidores",
        related_name="hoursworkcontractworkloads",
    )
    quantity_active = models.PositiveIntegerField(default=0)
    duration = models.PositiveIntegerField(
        default=0, verbose_name="Duração da Jornada em Minutos", blank=True
    )
    duration_hour = models.DecimalField(
        default=0,
        max_digits=14,
        decimal_places=2,
        verbose_name="Duração da Jornada em Horas",
        blank=True,
    )

    DAYS = {1: "Domingo", 2: "Seg", 3: "Ter", 4: "Qua", 5: "Qui", 6: "Sex", 7: "Sábado"}

    def __str__(self):
        return "%s - %s - %s" % (self.title, self.duration_hour, self.unicode_week_days)

    @classmethod
    def day(cls, day):
        for d in list(cls.DAYS.keys()):
            if day.find(str(d)) > -1:
                return d
        return 0

    @property
    def week_days(self):
        field_days = {
            "day_1": self.day_1,
            "day_2": self.day_2,
            "day_3": self.day_3,
            "day_4": self.day_4,
            "day_5": self.day_5,
            "day_6": self.day_6,
            "day_7": self.day_7,
        }
        return field_days

    @property
    def unicode_week_days(self):
        keys = list(self.week_days.keys())
        keys.sort()
        return ", ".join(
            a
            for a in [
                self.DAYS.get(int(key.split("_")[1]))
                for key in keys
                if self.week_days.get(key)
            ]
        )

    @property
    def parse_week_days(self):
        return ["true" if i in self.week_days else "false" for i in self.DAYS]

    @property
    def duration_counter(self):
        count = 0
        if self.day_1:
            count += self.day_1.duration
        if self.day_2:
            count += self.day_2.duration
        if self.day_3:
            count += self.day_3.duration
        if self.day_4:
            count += self.day_4.duration
        if self.day_5:
            count += self.day_5.duration
        if self.day_6:
            count += self.day_6.duration
        if self.day_7:
            count += self.day_7.duration
        return int(count)

    @classmethod
    def update_quantity_active(cls, hours_work_contract_workload):
        hours_work_contract_workload.save()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.quantity_active = EmployeeHoursWorkContractWorkload.objects.filter(
            hours_work_contract_workload=self, active=True
        ).count()
        self.duration = self.duration_counter
        self.duration_hour = self.duration / 60
        super(HoursWorkContractWorkload, self).save(*args, **kargs)


class EmployeeHoursWorkContractWorkload(AuditTimestampModel):
    employee = models.ForeignKey(Servidor, on_delete=models.PROTECT)
    hours_work_contract_workload = models.ForeignKey(
        HoursWorkContractWorkload, on_delete=models.PROTECT
    )
    date_start = models.DateField(verbose_name="Início de Vigência")
    date_end = models.DateField(null=True, blank=True, verbose_name="Fim de Vigência")
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ("employee", "date_start")

    def __str__(self):
        return "%s - %s" % (self.employee, self.hours_work_contract_workload)

    def is_active(self, date=None):
        return is_active(today=date, date_start=self.date_start, date_end=self.date_end)

    def validate_workload_not_found(self):
        workload = CargaHoraria.objects.filter(
            servidor=self.employee,
            duration=self.hours_work_contract_workload.duration,
            active=True,
        )
        if not workload.exists():
            raise Exception(
                "Carga Horária de %s incompatível para %s."
                % (self.hours_work_contract_workload.duration / 60, self.employee)
            )
        return True

    def validate_date_start_date_end(self):
        if self.date_end and self.date_start > self.date_end:
            raise Exception("Data início maior que data fim.")
        return True

    def validate(self):
        self.validate_workload_not_found()
        self.validate_date_start_date_end()
        return True

    def manage_employee_workload(self):
        empl_employee = EmployeeHoursWorkContractWorkload.objects.filter(
            Q(employee=self.employee)
            & (
                Q(date_start__lte=self.date_start)
                | Q(date_end__gte=self.date_start)
                | Q(date_end=None)
            )
        ).exclude(date_end__lt=self.date_start)
        if self.date_end:
            empl_employee = empl_employee.exclude(date_start__gt=self.date_end)
        if self.pk:
            empl_employee = empl_employee.exclude(pk=self.pk)
        for empl in empl_employee.filter():
            date_end_new = self.date_start - relativedelta(days=1)
            if empl.date_start > date_end_new:
                empl.delete()
            else:
                empl.date_end = date_end_new
                empl.save()

    @transaction.atomic
    def save(self, *args, **kargs):
        self.active = self.is_active()
        self.validate()

        self.manage_employee_workload()

        super(EmployeeHoursWorkContractWorkload, self).save(*args, **kargs)

    def delete(self, *args, **kargs):
        super(EmployeeHoursWorkContractWorkload, self).delete(*args, **kargs)

    @classmethod
    def apply_employee_workload(
        cls,
        workplace=None,
        date_start=None,
        date_end=None,
        reapply=False,
        hwc_workload_origin=None,
        hwc_workload_destiny=None,
        all_employee=False,
        locality=None,
        feedback=None,
    ):

        from engine.mq.models import Task
        from rh.task.hoursworkcontractworkload import apply_employee_workload

        if not date_start:
            raise Exception("Data de início não informada.")
        if not hwc_workload_destiny:
            raise Exception("Escala de Destino não informada.")

        hwc_workload_destiny = HoursWorkContractWorkload.objects.get(
            pk=int(hwc_workload_destiny)
        )
        if not hwc_workload_origin:
            hwc_workload_origin = hwc_workload_destiny.pk

        Task.start(
            apply_employee_workload,
            hwc_workload_origin=(
                hwc_workload_origin
                if type(hwc_workload_origin) is int
                else hwc_workload_origin.pk
            ),
            hwc_workload_destiny=(
                hwc_workload_destiny
                if type(hwc_workload_destiny) is int
                else hwc_workload_destiny.pk
            ),
            date_start=DateUtils.date_to_str(date_start),
            date_end=DateUtils.date_to_str(date_end) if date_end else date_end,
            locality=locality,
            workplace=workplace,
            all_employee=all_employee,
            reapply=reapply,
            user=get_current_user().pk,
            success="""<p>
                RH - Escalas criadas com sucesso. Verifique resultado no arquivo
                <a href="/athenas/RHEmployeeHoursWorkContractWorkload/file/?uuid=%(uuid)s">link</a>.
                </p>
                <p>
                Este arquivo está disponível para download até dia
                <span style="font-weight:bold">%(deadline)s</span>
                </p>""",
        )

    @classmethod
    def _apply(
        cls,
        hoursworkcontractworkload,
        date_start,
        date_end=None,
        employees=[],
        task=None,
    ):
        from engine.mq.models import Task

        task = Task.objects.get(pk=task)

        if type(employees) == list:
            employees = Servidor.objects.filter(pk__in=employees)
        if type(hoursworkcontractworkload) == int:
            hoursworkcontractworkload = HoursWorkContractWorkload.objects.get(
                pk=hoursworkcontractworkload
            )

        def write_file(text, mode="w"):
            """
            Método responsável por escrever em file_write.
            """
            try:
                file_write = codecs.open(
                    "%s/escalas-%s.csv" % (settings.CACHE_PATH, task.uuid),
                    mode,
                    "utf-8",
                )
                file_write.write(text)
                file_write.close()
            except Exception as err:
                log.exception(err)

        params = {
            "hours_work_contract_workload": hoursworkcontractworkload,
            "date_start": DateUtils.str_to_date(date_start),
            "date_end": DateUtils.str_to_date(date_end) if date_end else None,
        }
        for employee in employees:
            params.update({"employee": employee})
            try:
                new, created = (
                    EmployeeHoursWorkContractWorkload.objects.update_or_create(**params)
                )
            except Exception as err:
                message = "Tentando lançar %s do dia %s a %s" % (
                    hoursworkcontractworkload,
                    date_start,
                    date_end if date_end else "----",
                )
                write_file(
                    "%s|%s|%s|%s\n"
                    % (employee.matricula, employee.pessoa_fisica, err, message),
                    mode="a",
                )
                log.exception(err)

    @classmethod
    def remove_by_date_start(
        cls,
        date_start=None,
        date_end=None,
        hours_work_contract_workload=None,
        feedback=None,
    ):
        if not date_start:
            raise Exception("Data de início não informada.")
        if not hours_work_contract_workload:
            raise Exception("Escala não informada.")

        empl_workloads = EmployeeHoursWorkContractWorkload.objects.filter(
            date_start=date_start,
            hours_work_contract_workload__pk=int(hours_work_contract_workload),
        )
        for empl in empl_workloads:
            try:
                empl.delete()
            except Exception as err:
                log.exception(err)


class CensoEstudo(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor", verbose_name="Servidor", on_delete=models.CASCADE
    )
    nivel_escolaridade = models.IntegerField(
        choices=(
            (1, "MÉDIO"),
            (2, "TÉCNICO"),
            (3, "SUPERIOR"),
            (4, "PÓS-GRADUAÇÃO"),
            (5, "MESTRADO"),
            (6, "DOUTORADO"),
            (7, "PÓS-DOUTORADO"),
        ),
        default=0,
    )
    instituicao = models.TextField(blank=True, null=True)
    curso = models.TextField(blank=True, null=True)
    ano_conclusao = models.SmallIntegerField(default=0)
    cidade = models.ForeignKey(
        "Localidade", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        permissions = (("escol_admin", "administra escolaridade"),)

    def __str__(self):
        return "%s: Nível %s. Instituição %s" % (
            self.servidor,
            self.get_nivel_escolaridade_display(),
            self.instituicao,
        )


class CensoPrevidenciario(AuditTimestampModel):
    servidor = models.ForeignKey(
        "Servidor", verbose_name="Servidor", on_delete=models.CASCADE
    )
    tipo_regime = models.IntegerField(
        choices=(
            (1, "REGIME GERAL DE PREVIDÊNCIA"),
            (2, "REGIME PRÓPRIO DE PREVIDÊNCIA"),
        ),
        default=0,
    )
    empresa_orgao = models.TextField(blank=True, null=True)
    data_inicio = models.DateField(null=True, blank=True, verbose_name="Data Início")
    data_fim = models.DateField(null=True, blank=True, verbose_name="Data Fim")
    dias = models.SmallIntegerField(default=0)

    class Meta:
        ordering = ("servidor",)
        permissions = (("previd_adm", "Adm Censo Prev"),)

    def __str__(self):
        return "%s: Regime %s. Empresa/Orgão %s" % (
            self.servidor,
            self.get_tipo_regime_display(),
            self.empresa_orgao,
        )


class PublicConcurrence(AuditTimestampModel):
    name = models.CharField(max_length=200, verbose_name="Nome")
    number_mpe = models.CharField(max_length=4, verbose_name="Número MPE")
    year_mpe = models.CharField(max_length=4, verbose_name="Ano MPE")
    number_tce = models.CharField(
        max_length=20, verbose_name="Número TCE", blank=True, null=True
    )
    resume = models.TextField(null=True, blank=True)
    type_concurrence = models.IntegerField(
        verbose_name="Tipo",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "PUBLICCONCURRENCE_TYPE"),
    )
    publication = models.ForeignKey(
        "Publicacao", on_delete=models.CASCADE, null=True, blank=True
    )
    job_positions = models.ManyToManyField(
        "rh.Cargo",
        verbose_name="Cargos",
        related_name="public_concurrence",
        blank=True,
    )
    date_public = models.DateField(verbose_name="Data do Edital", null=True, blank=True)

    number_mpe_max_length = 4

    class Meta:
        unique_together = ("number_mpe", "year_mpe")
        ordering = ("number_mpe", "year_mpe")

    def __str__(self):
        return "%s%s - %s" % (self.number_mpe, self.year_mpe, self.name)

    @classmethod
    def zero_fill(cls, par, max_length=4):
        if par is None:
            par = ""
        if len(par) < max_length:
            n = max_length - len(par)
            par = "%s%s" % ("0" * n, par)
        return par

    def _validate(self):
        return self._validate_is_digit()

    def _validate_is_digit(self):
        if not self.number_mpe.isdigit():
            raise Exception("O campo Número deve ser composto somente de dígitos.")
        if not self.year_mpe.isdigit():
            raise Exception("O campo Ano deve ser composto somente de dígitos.")
        return True

    def save(self, *args, **kargs):
        self.number_mpe = PublicConcurrence.zero_fill(
            self.number_mpe, self.number_mpe_max_length
        )
        self._validate()
        super(PublicConcurrence, self).save(*args, **kargs)


class SocialProgram(AuditTimestampModel):
    name = models.CharField(max_length=200, verbose_name="Nome")

    class Meta:
        ordering = ("name",)
        permissions = (("social_program", "Administrar Programa Social"),)

    def __str__(self):
        return "%s" % self.name


class SeriousDiseases(AuditTimestampModel):
    name = models.CharField(max_length=200, verbose_name="Nome")

    class Meta:
        ordering = ("name",)
        permissions = (("serious_diseases", "Administrar Doenças Graves"),)

    def __str__(self):
        return "%s" % self.name


class CourseAreaCNMP(AuditTimestampModel):
    area = models.CharField(max_length=200, verbose_name="Área do Curso")
    value = models.SmallIntegerField(default=0)

    def __str__(self):
        return "%s" % self.area


class GraduationCNMP(AuditTimestampModel):
    course = models.CharField(max_length=200, verbose_name="Curso")
    institution = models.CharField(
        max_length=200, verbose_name="Instituicao", blank=True
    )
    course_area = models.ForeignKey(
        "CourseAreaCNMP", verbose_name="Area do Curso", on_delete=models.CASCADE
    )
    course_cine_brasil = models.ForeignKey(
        "CourseCineBrasil",
        verbose_name="Curso Cine Brasil",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    institution_inep = models.ForeignKey(
        "HigherEducationInstitution",
        verbose_name="Instituição (INEP)",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    conclusion_year = models.SmallIntegerField(
        default=0, verbose_name="Ano de conclusão"
    )
    anexo = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="anexo_graduationcnmp",
    )


class ImprovementAndGraduateCNMP(AuditTimestampModel):
    course = models.CharField(max_length=200, verbose_name="Curso")
    institution = models.CharField(max_length=200, verbose_name="Instituição")
    course_area = models.ForeignKey(
        "CourseAreaCNMP", verbose_name="Área do Curso", on_delete=models.CASCADE
    )
    conclusion_year = models.SmallIntegerField(
        default=0, verbose_name="Ano de conclusão"
    )
    nivel = models.IntegerField(
        verbose_name="Nível",
        choices=Choice.get_choices_for("rh_cnmp", "IMPROVMENT_NIVEL"),
    )
    anexo = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="anexo_improvementandgraduatecnmp",
    )


class PublishedWorksCNMP(AuditTimestampModel):
    title = models.CharField(max_length=200, verbose_name="Título")
    area = models.CharField(max_length=200, verbose_name="Área")
    institution = models.CharField(max_length=200, verbose_name="Instituição")
    work_type = models.IntegerField(
        verbose_name="Tipo", choices=Choice.get_choices_for("rh_cnmp", "WORK_TYPE")
    )
    year = models.SmallIntegerField(default=0, verbose_name="Ano")
    publication_place = models.CharField(
        max_length=50,
        verbose_name="Meio de Publicação",
        choices=[
            ("IMPRESSO", "IMPRESSO"),
            ("INTERNET", "INTERNET"),
            ("MAGNETICO", "MAGNETICO"),
        ],
    )
    anexo = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="anexo_publishedworkscnmp",
    )


# @deprecated
class TraineeQuerySet(ServidorQueryset):
    def active_in(self, *args, **kwargs):
        all_currents = DeclaracaoAtividade.objects.currents_in(
            *args, **kwargs
        ).values_list("servidor")
        return self.filter(pk__in=all_currents)


# @deprecated
class Trainee(Servidor):
    """
    Estagiario
    """

    employee_supervisor = models.ForeignKey(
        "Servidor",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Supervisor",
        related_name="trainee_supervisor",
    )
    educational_institution = models.ForeignKey(
        "PessoaJuridica",
        verbose_name="Instituição Educacional",
        on_delete=models.PROTECT,
        related_name="trainee_educational_institution",
        null=True,
        blank=True,
    )
    integration_agent = models.ForeignKey(
        "PessoaJuridica",
        null=True,
        blank=True,
        verbose_name="Agente de Integração",
        on_delete=models.PROTECT,
        related_name="trainee_educational_integration_agent",
    )
    nature = models.IntegerField(
        default=TRAINEE_NATURE_MANDATORY,
        choices=Choice.get_choices_for("rh", "TRAINEE_NATURE"),
        verbose_name="Natureza",
    )
    level = models.IntegerField(
        default=TRAINEE_LEVEL_FUNDAMENTAL,
        choices=Choice.get_choices_for("rh", "TRAINEE_LEVEL"),
        verbose_name="Nível",
    )
    occupation_area = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Área de ocupação"
    )
    insurance_number = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Número de seguro"
    )
    value = models.DecimalField(
        decimal_places=2, max_digits=14, null=True, blank=True, verbose_name="Valor"
    )

    objects = TraineeQuerySet.as_manager()

    class Meta:
        verbose_name = "Estagiário"

    def validate(self):
        if self.educational_institution and not self.educational_institution.cnpj:
            raise Exception("Cadastre o CNPJ.")
        if (
            self.educational_institution
            and not self.educational_institution.razao_social
        ):
            raise Exception("Cadastre a razão social.")
        if self.integration_agent:
            if not self.integration_agent.cnpj:
                raise Exception("Cadastre o CNPJ do agente de integração.")
            if not self.integration_agent.razao_social:
                raise Exception("Cadastre a razão social do agente de integração.")
            address = self.integration_agent.address.filter()
            if address.exists():
                address = address.last()
                if not address.municipio:
                    raise Exception(
                        "Cadastre endereço para o agente de integração - MUNICÍPIO."
                    )
                if not address.cep:
                    raise Exception(
                        "Cadastre endereço para o agente de integração - CEP."
                    )
                if not address.logradouro:
                    raise Exception(
                        "Cadastre endereço para o agente de integração - LOGRADOURO."
                    )
                if not address.numero:
                    raise Exception(
                        "Cadastre endereço para o agente de integração - NÚMERO."
                    )
            else:
                raise Exception("Cadastre endereço para o agente de integração.")
        super(Trainee, self).validate()

    def full_clean(self, exclude=None, validate_unique=True):
        self._validate_if_trainee_is_empty()
        self._validate_if_matricula_is_empty()
        self._validate_if_nature_is_empty()
        self._validate_if_level_is_empty()

        try:
            super(Trainee, self).full_clean(exclude, validate_unique)
        except ValidationError as validation_error:
            raise ValidationError(validation_error)

    def _validate_if_trainee_is_empty(self):
        if not hasattr(self, "pessoa_fisica"):
            raise Exception("Por favor, preencha o campo Estagiário.")

    def _validate_if_matricula_is_empty(self):
        if not self.matricula and not self.auto_registration_class:
            raise Exception("Por favor, preencha o campo Matrícula.")

    def _validate_if_nature_is_empty(self):
        if not self.nature:
            raise Exception("Por favor, preencha o campo Natureza.")

    def _validate_if_level_is_empty(self):
        if not self.level:
            raise Exception("Por favor, preencha o campo Nível.")

    def save(self, *args, **kargs):
        self.chefe_imediato = self.employee_supervisor
        self.type_by_possession = "EST"
        super(Trainee, self).save(*args, **kargs)


class CharacteristicWorkplace(AuditTimestampModel):
    """
    Propriedade da Lotação
    """

    class Meta:
        verbose_name = "Propriedade da Lotação"

    name = models.CharField(max_length=200, verbose_name="Nome")

    def __str__(self):
        return self.name


class OfficeHoursWorkplace(AuditTimestampModel):
    """
    Horário de Expediente
    """

    description = models.CharField(max_length=200, verbose_name="Nome")
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Horário de Expediente"

    def __str__(self):
        return self.description


class DeficiencyInformation(AuditTimestampModel):
    """
    Informações de deficiência.
    """

    class Meta:
        verbose_name = "Informações de deficiência"

    naturalperson = models.OneToOneField(
        PessoaFisica,
        verbose_name="Pessoa",
        related_name="deficiencyinformation",
        on_delete=models.CASCADE,
    )
    rehabilitation = models.BooleanField(
        default=False, blank=True, verbose_name="Reabilitação"
    )
    quota = models.BooleanField(
        default=False, blank=True, verbose_name="Pertencente a cota"
    )
    note = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Informações de deficiência: %s" % self.naturalperson


class ForeignInformation(AuditTimestampModel):
    """
    Informações de estrangeiro.
    """

    class Meta:
        verbose_name = "Informações de Estrangeiro"

    naturalperson = models.OneToOneField(
        PessoaFisica,
        verbose_name="Pessoa",
        related_name="foreigninformation",
        on_delete=models.CASCADE,
    )
    classification_permanence = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "CLASSIFICATION_PERMANENCE"),
        verbose_name="Classificação de ingresso",
    )
    date_arrived = models.DateField(verbose_name="Data de chegada")
    married_br = models.BooleanField(
        default=False, blank=True, verbose_name="Casado(a) com brasileiro(a)"
    )
    son_br = models.BooleanField(
        default=False, blank=True, verbose_name="Filhos brasileiros"
    )

    def __str__(self):
        return "Informações de deficiência: %s" % self.naturalperson


class TipoDocumento(AuditTimestampModel):
    tipo = models.CharField(max_length=200, verbose_name="Tipo Documento")


class Relationship(AuditTimestampModel):
    giver = models.ForeignKey(
        Servidor,
        verbose_name="Quem dá",
        related_name="relationship_giver",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        Servidor,
        verbose_name="Quem recebe",
        related_name="relationship_receiver",
        on_delete=models.CASCADE,
    )
    workplace = models.ForeignKey(
        Lotacao,
        null=True,
        blank=True,
        verbose_name="Lotação concedida",
        on_delete=models.CASCADE,
    )
    date_start = models.DateField(verbose_name="Início")
    date_end = models.DateField(null=True, blank=True, verbose_name="Fim")
    app = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "RELATIONSHIP_APP"),
        verbose_name="Aplicativo",
    )

    class Meta:
        verbose_name = "Relação de Confiança"
        permissions = (
            (
                "can_establish_any_trust_relationship",
                "Pode estabelecer qualquer relação de confiança",
            ),
        )

    def __str__(self):
        return "De: %s - Para: %s %s - App: %s" % (
            self.giver,
            self.receiver,
            "- %s" % (self.workplace if self.workplace else ""),
            self.get_app_display(),
        )

    def validate(self):
        if employee_from_user(
            get_current_user()
        ) != self.giver and not get_current_user().has_perm(
            "can_establish_any_trust_relationship"
        ):
            raise Exception(
                "Você não possui permissão para criar Relação de Confiança em nome de 3º"
            )

        if (
            self.workplace
            and not self.giver.responsavel_por.filter(pk=self.workplace).exists()
        ):
            raise Exception(
                "%s não é responsável por %s. É necessário escolher local onde seja responsável."
                % (self.giver, self.workplace)
            )

    def save(self, *args, **kargs):
        self.giver = (
            employee_from_user(get_current_user()) if not self.giver else self.giver
        )
        self.validate()
        super(Relationship, self).save(*args, **kargs)


def conf_to_serialize():
    for field in UnidadeAdministrativa._meta.concrete_model._meta.local_fields:
        if field.attname == "orgaogeral_ptr_id":
            field.serialize = True
    for field in PessoaJuridica._meta.concrete_model._meta.local_fields:
        if field.attname == "pessoa_ptr_id":
            field.serialize = True


class Replacement(AuditTimestampModel):
    replaced = models.ForeignKey(
        Lotacao, related_name="replacement_replaceds", on_delete=models.PROTECT
    )
    substitute = models.ForeignKey(
        Lotacao, related_name="replacement_substitutes", on_delete=models.PROTECT
    )
    order = models.PositiveIntegerField(default=1)
    document = models.ForeignKey(
        "rh.Publicacao", related_name="replacement", on_delete=models.PROTECT
    )

    class PublicationNotFoundError(Exception):
        def __init__(self, txt=None):
            Exception.__init__(
                self, "%s" % (txt if txt else "Não existe publicação de vigência.")
            )

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return "Replaced: %s - %s Substitute: %s" % (
            self.replaced,
            self.order,
            self.substitute,
        )

    @classmethod
    def get_document_validity(cls, date=None):
        date = date.today() if not date else date
        replacements = Replacement.objects.filter(document__data_vigencia__lte=date)
        return (
            replacements.latest("document__data_vigencia").document
            if replacements.exists()
            else None
        )

    def validate_document_date_validity(self):
        if self.document.data_vigencia is None:
            raise Exception("A data de vigência deve ser informada.")
        return True

    def validate_repeated_substitute(self):
        query = (
            Replacement.objects.filter(
                replaced=self.replaced, substitute=self.substitute
            )
            .exclude(pk=self.pk)
            .exclude(document__data_vigencia__lt=self.document.data_vigencia)
        )

        if query.exists():
            raise Exception(
                "Substituto repetido %s para %s " % (self.substitute, self.replaced)
            )
        return True

    def validate_substitute_more_than_two(self):
        query = (
            Replacement.objects.filter(replaced=self.replaced)
            .exclude(pk=self.pk)
            .exclude(document__data_vigencia__lt=self.document.data_vigencia)
        )

        if query.count() > 2:
            raise Exception("More than 2 substitutes for %s" % self.replaced)
        return True

    def validate(self):
        self.validate_document_date_validity()
        return True

    @transaction.atomic
    def save(self, *args, **kargs):
        self.validate()
        super(Replacement, self).save(*args, **kargs)


class ProcessQueryset(models.QuerySet):
    def currents_in(self, date_validity=None, drange=None):
        if drange:
            return self.exclude(
                Q(start_validity__gt=drange.last)
                | (~Q(end_validity=None) & Q(end_validity__lt=drange.first))
            )
        else:
            date_validity = (
                datetime.now().date() if not date_validity else date_validity
            )
            return self.exclude(
                Q(start_validity__gt=date_validity)
                | (~Q(end_validity=None) & Q(end_validity__lt=date_validity))
            )


class LegalProcess(AuditTimestampModel):
    class Meta:
        verbose_name = "Tabela de Processos Administrativos/Judiciais"

    type_process = models.PositiveIntegerField(
        verbose_name="Tipo de processo",
        choices=Choice.get_choices_for("esocial", "PROCESS_TPPROC"),
    )
    number_process = models.CharField(verbose_name="Número processo", max_length=21)
    start_validity = models.DateField(verbose_name="Início da validade")
    end_validity = models.DateField(
        verbose_name="Fim da validade", null=True, blank=True
    )
    cod_authorship = models.PositiveSmallIntegerField(
        verbose_name="Autoria",
        choices=Choice.get_choices_for("esocial", "INDICATIVE_AUTHORSHIP"),
        null=True,
        blank=True,
    )
    matter_process = models.PositiveSmallIntegerField(
        verbose_name="Matéria do processo",
        choices=Choice.get_choices_for("esocial", "MATTER_PROCESS"),
    )
    note = models.CharField(
        verbose_name="Descrição", max_length=255, null=True, blank=True
    )
    judicial_process_locality = models.ForeignKey(
        "Localidade",
        verbose_name="Município",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    judicial_process_id_local = models.PositiveIntegerField(
        verbose_name="Número Vara", null=True, blank=True
    )
    all_employees = models.BooleanField(verbose_name="Todos servidores?", default=False)
    employees = models.ManyToManyField(
        "rh.Servidor", verbose_name="Servidores", related_name="suspension_process"
    )
    third_party_code = models.CharField(
        max_length=4, verbose_name="Código de Terceiro", null=True, blank=True
    )

    objects = ProcessQueryset.as_manager()

    def __str__(self):
        map_tp = {1: "ADM", 2: "JUD", 3: "INSS", 4: "FAP"}
        return "%s: %s" % (map_tp.get(self.type_process, "XXX"), self.number_process)

    def save(self, *args, **kwargs):
        """Se não for JUDICIAL não pode haver informações de vara judicial."""
        if self.type_process != 2:
            self.judicial_process_locality = None
            self.judicial_process_id_local = None
        super(LegalProcess, self).save(*args, **kwargs)
        for susp in self.suspensions.filter(end_validity__isnull=True):
            susp.end_validity = self.end_validity
            susp.save()


class ProcessSuspensionQueryset(models.QuerySet):
    def currents_in(self, date_validity=None, drange=None):
        if drange:
            return self.exclude(
                Q(start_validity__gt=drange.last)
                | (~Q(end_validity=None) & Q(end_validity__lt=drange.first))
            )
        else:
            date_validity = (
                datetime.now().date() if not date_validity else date_validity
            )
            return self.exclude(
                Q(start_validity__gt=date_validity)
                | (~Q(end_validity=None) & Q(end_validity__lt=date_validity))
            )

    def by_employee(self, employee):
        return self.filter(process__employees=employee)

    def by_event(self, event_number, drange):
        return (
            self.filter(process__gfp_events__numero=event_number)
            .filter(process__matter_process=1, scope_decision__in=(1, 2))
            .currents_in(drange=drange)
        )


class ProcessSuspension(AuditTimestampModel):
    process = models.ForeignKey(
        "LegalProcess",
        verbose_name="Processo",
        related_name="suspensions",
        on_delete=models.CASCADE,
    )
    indicative_suspension = models.PositiveSmallIntegerField(
        verbose_name="Indicativo suspensão",
        choices=Choice.get_choices_for("esocial", "INDICATIVE_SUSPENSION"),
        null=True,
        blank=True,
    )
    start_validity = models.DateField("Data Início Suspensão")
    end_validity = models.DateField("Data Fim Suspensão", null=True, blank=True)
    integral_deposit = models.BooleanField(verbose_name="Depósito integral?")
    scope_decision = models.PositiveSmallIntegerField(
        verbose_name="Abrangência",
        choices=Choice.get_choices_for("esocial", "SCOPE_DECISION"),
        default=1,
    )
    extension_decision = models.PositiveSmallIntegerField(
        verbose_name="Extensão",
        choices=Choice.get_choices_for("esocial", "EXTENSION_DECISION"),
        default=1,
    )
    rat_modified = models.BooleanField(default=False, verbose_name="RAT mudou?")
    fap_modified = models.BooleanField(default=False, verbose_name="FAP mudou?")

    objects = ProcessSuspensionQueryset.as_manager()

    def __str__(self):
        start_validity = (
            DateUtils.date_to_str(self.start_validity)
            if self.start_validity
            else "----"
        )
        return f"Suspensão ({start_validity})"


class RepeatPersonIncident(models.Model):
    main_person = models.ForeignKey(
        Pessoa, related_name="repeat_incidents", on_delete=models.PROTECT
    )
    target_person = models.ForeignKey(
        Pessoa, related_name="as_target_in_repeat_incidets", on_delete=models.PROTECT
    )
    current_state = models.SmallIntegerField(
        choices=((1, "Pendente"), (2, "Mesclado"), (3, "Descartado")), default=1
    )
    asigned_by = models.ForeignKey(
        "auth.User", related_name="+", on_delete=models.PROTECT, null=True
    )
    asigned_at = models.DateTimeField(null=True)
    ratio = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)

    class Meta:
        permissions = (
            ("can_mark_repeatincident_discarted", "Pode marcar como discartado"),
            ("can_mark_repeatincident_simple_merged", "Pode marcar como mesclado"),
            (
                "can_mark_repeatincident_merged",
                "Pode marcar como mesclado (Empregado/Dependente)",
            ),
        )

    def _user_is_allowed_discard(self):
        user = get_current_user()
        return user.has_perm("rh.can_mark_repeatincident_discarted")

    def _user_is_allowed_merge(self):
        log.warn("not implemented (mock)")
        return True

    def _validate_change_of_state(self, new_state):
        wf = {1: tuple({2, 3}), 2: tuple({}), 3: tuple({})}
        current_wf = wf.get(self.current_state)
        return new_state in current_wf

    def __merge_related_field(self, related_field):
        from django.db.models.fields.reverse_related import ManyToManyRel

        query = related_field.related_model.objects.filter(
            **{related_field.field.name: self.target_person.pk}
        )

        target_model = related_field.related_model
        target_path = ".".join(
            [
                target_model._meta.app_label,
                target_model._meta.model_name,
                related_field.field.name,
            ]
        )

        not_allowed = (
            "rh.pessoafisica.pessoa_ptr",
            "rh.repeatpersonincident.target_person",
            "rh.repeatpersonincident.main_person",
        )

        if not target_path in not_allowed and query.exists():
            log.info(
                f"Change field {target_path} from {self.target_person.pk} to {self.main_person.pk}"
            )
            log.info(f"{query.count()} lines changed")
            if isinstance(related_field, ManyToManyRel):
                remote_field = related_field.field.remote_field
                for item in query:
                    m2m = getattr(item, remote_field.field.name)
                    m2m.set(
                        [
                            (
                                person
                                if person.pk != self.target_person.pk
                                else self.main_person
                            )
                            for person in m2m.all()
                        ]
                    )
            else:
                query.update(**{related_field.field.name: self.main_person.pk})

    def __merge_relations(self):
        target = getattr(self.target_person, self.target_person.kind)

        for related in target._meta.related_objects:
            self.__merge_related_field(related)

    def __merge_empty_fields(self):
        not_allowed = (
            "id",
            "pk",
            "pessoa_ptr",
            "rate_fill",
            "kind",
            "created_by",
            "created_at",
            "modified_by",
            "modified_at",
            "data_cadastro",
            "data_alteracao",
            "name_cache",
            "phonetic_name",
            "phonetic_father_name",
            "phonetic_mother_name",
            "phonetic_social_name",
            "slug",
        )

        target = getattr(self.target_person, self.target_person.kind)
        main = getattr(self.main_person, self.main_person.kind)

        target_fields = [
            field for field in target._meta.fields if not field.name in not_allowed
        ]
        conflicted_fields = []

        for field in target_fields:
            target_value = getattr(target, field.name, None)
            main_value = getattr(main, field.name, None)

            if target_value and main_value and target_value != main_value:
                conflicted_fields.append(field.name)

            if not main_value and target_value:
                setattr(main, field.name, target_value)

        log.info("Com conflito de valores em:")
        for field in conflicted_fields:
            log.info(" ".join(["->", field]))

        main.save()

    def _mark_as_merged(self):
        if not self._validate_change_of_state(2):
            raise Exception("Ação não permitida para este item.")
        if not self._user_is_allowed_merge():
            raise Exception("Você não tem permissão para mesclar esta pessoa.")

        with transaction.atomic():
            self.__merge_empty_fields()
            self.__merge_relations()
            self.current_state = 2
            self.sign()

    def sign(self):
        if self.asigned_by:
            raise Exception("Incidente já foi assinado por outro usuário.")

        self.asigned_by = get_current_user()
        self.asigned_at = datetime.now()
        self.save()

    def _mark_as_discarded(self):
        if not self._validate_change_of_state(3):
            raise Exception("Ação não permitida para este item.")
        if not self._user_is_allowed_discard():
            raise Exception("Você não tem permissão para descartar este incidente.")

        self.current_state = 3
        self.sign()

    def mark_as(self, state):
        states = {
            2: lambda: self._mark_as_merged(),
            3: lambda: self._mark_as_discarded(),
        }

        fn = states.get(state, None)
        if not fn:
            raise Exception("Estado desconhecido.")
        else:
            fn()


class BKP_MovimentacaoPosseReq(MovimentacaoPessoal):
    quadro = models.ForeignKey(
        "Quadro", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_posse = models.DateField(null=True, blank=True, verbose_name="Data Posse")
    data_exercicio = models.DateField(
        null=True, blank=True, verbose_name="Data Exercício"
    )
    data_desligamento = models.DateField(
        null=True, blank=True, verbose_name="Data Desligamento"
    )
    anotacao_geral_nomeacao = models.ForeignKey(
        "AnotacaoGeral",
        blank=True,
        null=True,
        related_name="bkp_anotgeral_nomeacao",
        on_delete=models.SET_NULL,
    )
    anotacao_geral_exercicio = models.ForeignKey(
        "AnotacaoGeral",
        blank=True,
        null=True,
        related_name="bkp_anotgeral_exercicio",
        on_delete=models.SET_NULL,
    )
    ativo = models.BooleanField(default=True, blank=True)
    tipo_movcarreira = models.CharField(
        verbose_name="Provimento",
        choices=list(TIPO_MOVIMENTACAO_CARREIRA.items()),
        max_length=30,
        default="NOMEACAO",
    )
    bond = models.BooleanField(default=True, blank=True, verbose_name="Gerar vínculo")
    public_concurrence = models.ForeignKey(
        "rh.PublicConcurrence",
        on_delete=models.CASCADE,
        verbose_name="Concurso",
        null=True,
        blank=True,
        related_name="bkp_employees",
    )  # Parametro "on_delete" adicionado. (Django 2)
    publication_possession = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="bkp_possessions_publication_possession",
        verbose_name="Publicação de Posse",
    )
    publication_exercise = models.ForeignKey(
        "Publicacao",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="bkp_possessions_publication_exercise",
        verbose_name="Publicação de Exercício",
    )
    judicial_decision = models.BooleanField(
        "Decorrente de decisão judicial", default=False
    )
    out_off_distribution_list = models.BooleanField(
        default=False, blank=True, verbose_name="Fora da lista de distribuição"
    )
    number_process = models.CharField(
        verbose_name="Número do Processo Judicial", max_length=20, null=True, blank=True
    )
    judicial_deposit = models.BooleanField(
        "Pagamento realizado em juízo", default=False
    )
    legal_amnesty_process = models.CharField(
        "Número e Ano Lei Anistia", max_length=13, null=True, blank=True
    )
    financial_effect_date_start = models.DateField(
        "Data do Efeito Financeiro", null=True, blank=True
    )
    financial_effect_date_end = models.DateField(
        "Data do Efeito Financeiro", null=True, blank=True
    )

    def validate_type_by_possession(self):
        return True

    def validate_vacancy_number_filled(self):
        return True


class NaturalPersonHistory(AuditTimestampModel):
    """Histórico de informações do servidor."""

    natural_person = models.ForeignKey(
        PessoaFisica,
        related_name="history",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    when = models.DateField(default=date.today)
    send_esocial = models.BooleanField(
        "Enviar para eSocial?", default=False, blank=True
    )

    tipo_logradouro = models.IntegerField(
        "Endereço - Tipo do Logradouro",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "TYPE_STREET"),
    )
    tipo_endereco = models.IntegerField(
        "Endereço - Tipo do Endereço",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "TYPE_ADDRESS"),
    )
    municipio = models.ForeignKey(
        "rh.Localidade",
        verbose_name="Endereço - Cidade",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    logradouro = models.CharField(
        "Endereço - Logradouro", max_length=100, null=True, blank=True
    )
    bairro = models.CharField("Endereço - Bairro", max_length=50, null=True, blank=True)
    cep = models.CharField("CEP", max_length=10, null=True, blank=True)
    numero = models.CharField("Endereço - Número", max_length=12, null=True, blank=True)
    complemento = models.CharField(
        "Endereço - Complemento", max_length=2000, null=True, blank=True
    )
    outsider = models.BooleanField("Endereço no exterior", null=True, blank=True)
    country = models.ForeignKey(
        "rh.Pais",
        on_delete=models.SET_NULL,
        related_name="NaturalPersonHistory_address_country",
        verbose_name="País(Residentes no Exterior)",
        null=True,
        blank=True,
    )
    outsider_citty = models.CharField(
        "Cidade no Exterior", max_length=50, null=True, blank=True
    )

    phone_main = models.CharField(
        "Telefone Principal", max_length=15, null=True, blank=True
    )
    phone_type = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_PHONE"),
        verbose_name="Tipo de Telefone",
        null=True,
        blank=True,
    )
    phone_public = models.BooleanField("Público", null=True, blank=True)
    phone_description = models.CharField(
        max_length=80, verbose_name="Descrição", null=True, blank=True
    )
    phone_contact_emergency = models.CharField(
        "Telefone de Emergência", max_length=15, null=True, blank=True
    )
    contact_emergency_name = models.CharField(
        "Nome do Contato de Emergência", max_length=100, null=True, blank=True
    )

    cnh = models.CharField("CNH", max_length=11, null=True, blank=True)
    cnh_categoria = models.CharField(
        "CNH - Categoria", max_length=30, null=True, blank=True
    )
    cnh_expedition_date = models.DateField(
        "CNH - Data da Expedição", null=True, blank=True
    )
    cnh_first_date = models.DateField(
        "CNH - Data da primeira habilitação", null=True, blank=True
    )
    cnh_state = models.ForeignKey(
        "rh.Estado",
        verbose_name="CNH - Estado",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cnh_validity_date = models.DateField(
        "CNH - Data de Validade", null=True, blank=True
    )

    professional_council = models.CharField(
        "Conselho Profissional", max_length=30, null=True, blank=True
    )
    professional_council_state = models.ForeignKey(
        "rh.Estado",
        verbose_name="Conselho Profissional - Estado",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    professional_council_expedition_date = models.DateField(
        "Conselho Profissional - Data da Expedição", null=True, blank=True
    )
    professional_council_validity_date = models.DateField(
        "Conselho Profissional - Data de Validade", null=True, blank=True
    )
    professional_council_issuer = models.CharField(
        "Conselho Profissional - Orgão de Expedição",
        max_length=256,
        null=True,
        blank=True,
    )

    nis = models.CharField("NIS", max_length=30, null=True, blank=True)

    reservista = models.CharField("Reservista", max_length=30, null=True, blank=True)
    classe_reservista = models.CharField(
        "Reservista - Classe", max_length=30, null=True, blank=True
    )

    ric = models.CharField("RIC", max_length=30, null=True, blank=True)
    ric_expedition_date = models.DateField(
        "RIC - Data da Expedição", null=True, blank=True
    )
    ric_issuer = models.CharField(
        "RIC - Orgão Emissor", max_length=256, null=True, blank=True
    )
    ric_state = models.ForeignKey(
        "rh.Estado",
        verbose_name="RIC - Estado",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    rne = models.CharField("RNE", max_length=30, null=True, blank=True)
    rne_expedition_date = models.DateField(
        "RNE - Data da Expedição", null=True, blank=True
    )
    rne_issuer = models.CharField(
        "RNE - Orgão Emissor", max_length=256, null=True, blank=True
    )
    rne_state = models.ForeignKey(
        "rh.Estado",
        verbose_name="RNE - Estado",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    titulo_eleitor = models.CharField(
        "Título Eleitor", max_length=30, null=True, blank=True
    )
    municipio_titulo = models.ForeignKey(
        "rh.Localidade",
        related_name="+",
        verbose_name="Título de Eleitor - Municipio",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    secao_titulo = models.CharField(
        "Título de Eleitor - Seção", max_length=30, null=True, blank=True
    )
    zona_titulo = models.CharField(
        "Título de Eleitor - Zona", max_length=30, null=True, blank=True
    )

    ctps = models.CharField("CTPS", max_length=30, null=True, blank=True)
    ctps_state = models.ForeignKey(
        "rh.Estado",
        verbose_name="CTPS - Estado",
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    serie_ctps = models.CharField("CTPS - Série", max_length=30, null=True, blank=True)
    pis_pasep = models.CharField("PIS/PASEP", max_length=30, null=True, blank=True)

    cpf = models.CharField("CPF", max_length=14, null=True, blank=True)

    data_nascimento = models.DateField("Data de Nascimento", null=True, blank=True)
    data_obito = models.DateField("Data Óbito", null=True, blank=True)
    doador = models.BooleanField("Doador de órgãos", null=True, blank=True)
    uniao_estavel = models.BooleanField("União Estável", null=True, blank=True)
    email_institucional = models.CharField(
        "E-mail Institucional", max_length=60, null=True, blank=True
    )
    email_pessoal = models.CharField(
        "E-mail Pessoal", max_length=60, null=True, blank=True
    )
    estado_civil = models.IntegerField(
        choices=Choice.get_choices_for("rh", "MARITAL_STATUS"),
        verbose_name="Estado civíl",
        null=True,
        blank=True,
    )
    fator_rh = models.IntegerField(
        choices=Choice.get_choices_for("rh", "FACTOR_RH"),
        verbose_name="Fator RH",
        null=True,
        blank=True,
    )
    foto = models.ForeignKey(
        "ged.Arquivo",
        related_name="+",
        verbose_name="Foto",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    grau_instrucao = models.IntegerField(
        choices=Choice.get_choices_for("rh", "DEGREE_EDUCATION"),
        verbose_name="Grau de Instrução",
        null=True,
        blank=True,
    )
    municipio_naturalidade = models.ForeignKey(
        "rh.Localidade",
        related_name="+",
        verbose_name="Naturalidade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    nationality = models.ForeignKey(
        "rh.Pais",
        verbose_name="Nacionalidade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    nationality_birth = models.ForeignKey(
        "rh.Pais",
        verbose_name="País de nascimento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="NaturalPersonHistory_nationality_birth",
    )
    immigrant_residence_time = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_RESIDENCE_TIME"),
        verbose_name="Tempo de residência do imigrante",
        null=True,
        blank=True,
    )
    immigrant_entry_condition = models.IntegerField(
        choices=Choice.get_choices_for("rh", "IMMIGRANTE_ENTRY_CONDITION"),
        verbose_name="Condição de ingresso do imigrante",
        null=True,
        blank=True,
    )

    nome = models.CharField("Nome", max_length=100, null=True, blank=True)
    nome_conjuge = models.CharField(
        "Nome Cônjuge", max_length=80, null=True, blank=True
    )
    nome_mae = models.CharField("Nome Mãe", max_length=80, null=True, blank=True)
    phonetic_father_name = models.CharField(max_length=80, null=True, blank=True)
    nome_pai = models.CharField("Nome Pai", max_length=80, null=True, blank=True)
    phonetic_mother_name = models.CharField(max_length=80, null=True, blank=True)
    genero = models.CharField("Gênero", max_length=100, null=True, blank=True)
    raca_cor = models.IntegerField(
        choices=Choice.get_choices_for("rh", "TYPE_RACE"),
        verbose_name="Raça/Cor",
        null=True,
        blank=True,
    )

    rg = models.CharField("RG", max_length=30, null=True, blank=True)
    rg_data_expedicao = models.DateField(
        "RG - Data da Expedição", null=True, blank=True
    )
    rg_orgao = models.CharField("RG - Orgão", max_length=30, null=True, blank=True)
    rg_uf = models.ForeignKey(
        "rh.Estado",
        verbose_name="RG - UF",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    sangue = models.IntegerField(
        choices=Choice.get_choices_for("rh", "BLOOD"),
        verbose_name="Tipo Sanguíneo",
        null=True,
        blank=True,
    )
    sexo = models.CharField(
        "Sexo", max_length=1, choices=SEXO_CHOICES, null=True, blank=True
    )
    sexual_orientation = models.PositiveSmallIntegerField(
        "Orientação Sexual",
        choices=Choice.get_choices_for("rh", "SEXUAL_ORIENTATION"),
        null=True,
        blank=True,
    )

    social_name = models.CharField("Nome Social", max_length=100, blank=True, null=True)

    necessidade_especial = models.BooleanField(
        "Necessidade Especial", null=True, blank=True
    )

    profissao = models.CharField("Profissão", max_length=100, null=True, blank=True)
    renda_familiar = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        verbose_name="Renda Familiar",
        null=True,
        blank=True,
    )
    has_serious_diseases = models.BooleanField("Doença Grave", null=True, blank=True)
    retired = models.BooleanField("Aposentado", null=True, blank=True)
    is_lawyer = models.BooleanField(
        default=False, verbose_name="Advogado", null=True, blank=True
    )
    oab = models.CharField("OAB", max_length=20, null=True, blank=True)

    name_cache = models.CharField("Cache Name", max_length=100, null=True, blank=True)
    phonetic_name = models.CharField(max_length=100, null=True, blank=True)
    slug = models.SlugField("Slug", max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    enable_protocol = models.BooleanField("Habilitar protocolo", null=True, blank=True)
    kind = models.CharField("Tipo", max_length=32, null=True, blank=True)
    rate_fill = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )

    EXCLUDE_FIELD = (
        "data_alteracao",
        "data_cadastro",
        "nacionalidade",
        "general_organ",
        "person",
    )

    MAP_FIELD_NAME = {
        "telefone": {
            "phone_main": "numero",
            "phone_type": "tipo_telefone",
            "phone_public": "publico",
            "phone_description": "description",
        }
    }

    FIELDS_TO_HISTORY = {
        "pessoafisica": [
            "cpf",
            "nome",
            "sexo",
            "raca_cor",
            "estado_civil",
            "grau_instrucao",
            "social_name",
            "municipio_naturalidade",
            "data_nascimento",
        ],
        "telefone": [True],
        "endereco": [True],
        "dependencia": [True],
    }

    @classmethod
    def _cnh(cls, person, value=None):
        cnh = person.cnh
        return cnh.numero if cnh else None

    @classmethod
    def _cnh_categoria(cls, person, value=None):
        cnh = person.cnh
        return cnh.cnh_category.valor if cnh and cnh.cnh_category else None

    @classmethod
    def _cnh_expedition_date(cls, person, value=None):
        cnh = person.cnh
        if cnh:
            return cnh.data_expedicao
        return None

    @classmethod
    def _cnh_first_date(cls, person, value=None):
        cnh = person.cnh
        if cnh:
            try:
                return (
                    DateUtils.str_to_date(cnh.cnh_first_date.valor)
                    if cnh and cnh.cnh_first_date
                    else None
                )
            except Exception as e:
                pass
        return None

    @classmethod
    def _cnh_state(cls, person, value=None):
        cnh = person.cnh
        if cnh:
            return cnh.estado_expedicao
        return None

    @classmethod
    def _cnh_validity_date(cls, person, value=None):
        cnh = person.cnh
        if cnh:
            return cnh.data_validade
        return None

    @classmethod
    def _professional_council(cls, person, value=None):
        professional_council = person.professional_council
        if professional_council:
            return professional_council.numero
        return None

    @classmethod
    def _professional_council_state(cls, person, value=None):
        professional_council = person.professional_council
        if professional_council:
            return professional_council.estado_expedicao
        return None

    @classmethod
    def _professional_council_expedition_date(cls, person, value=None):
        professional_council = person.professional_council
        if professional_council:
            return professional_council.data_expedicao
        return None

    @classmethod
    def _professional_council_validity_date(cls, person, value=None):
        professional_council = person.professional_council
        if professional_council:
            return professional_council.data_validade
        return None

    @classmethod
    def _professional_council_issuer(cls, person, value=None):
        professional_council = person.professional_council
        if professional_council and professional_council.professional_council_issuer:
            return professional_council.professional_council_issuer.valor
        return None

    @classmethod
    def _pis_pasep(cls, person, value=None):
        if value:
            return value.numero
        return None

    @classmethod
    def _titulo_eleitor(cls, person, value=None):
        voter = person.voter
        if voter:
            return voter.numero
        return None

    @classmethod
    def _municipio_titulo(cls, person, value=None):
        voter = person.voter
        if voter:
            return voter.voter_city_local
        return None

    @classmethod
    def _secao_titulo(cls, person, value=None):
        voter = person.voter
        if voter:
            voter_section = voter.voter_section
            if voter_section:
                return voter_section.valor
        return None

    @classmethod
    def _zona_titulo(cls, person, value=None):
        voter = person.voter
        if voter:
            voter_zone = voter.voter_zone
            if voter_zone:
                return voter_zone.valor
        return None

    @classmethod
    def _ctps_state(cls, person, value=None):
        ctps = person.ctps
        if ctps:
            return ctps.estado_expedicao
        return None

    @classmethod
    def _serie_ctps(cls, person, value=None):
        ctps = person.ctps
        if ctps:
            return ctps.ctps_series.valor
        return None

    @classmethod
    def _ctps(cls, person, value=None):
        ctps = person.ctps
        if ctps:
            return ctps.numero
        return None

    @classmethod
    def _reservista(cls, person, value=None):
        reservist = person.reservist
        if reservist:
            return reservist.numero
        return None

    @classmethod
    def _classe_reservista(cls, person, value=None):
        reservist = person.reservist
        if reservist:
            return (
                reservist.reservist_class.valor if reservist.reservist_class else None
            )
        return None

    @classmethod
    def _foto(cls, person, value=None):
        from ged.models import Arquivo

        if value:
            return Arquivo.objects.filter(pk=value).last()
        return None

    @classmethod
    def _municipio_naturalidade(cls, person, value=None):
        if value:
            return Localidade.objects.filter(pk=value).last()
        return None

    @classmethod
    def _nationality(cls, person, value=None):
        if value:
            return Pais.objects.filter(pk=value).last()
        return None

    @classmethod
    def _rg_uf(cls, person, value=None):
        if value:
            return Estado.objects.filter(pk=value).last()
        return None

    @classmethod
    def method_evaluate(cls):
        def _default_not_none(person, value):
            return value is not None

        return {
            "cnh": cls._cnh,
            "cnh_categoria": cls._cnh_categoria,
            "cnh_expedition_date": cls._cnh_expedition_date,
            "cnh_first_date": cls._cnh_first_date,
            "cnh_state_id": cls._cnh_state,
            "cnh_validity_date": cls._cnh_validity_date,
            "professional_council": cls._professional_council,
            "professional_council_state_id": cls._professional_council_state,
            "professional_council_expedition_date": cls._professional_council_expedition_date,
            "professional_council_validity_date": cls._professional_council_validity_date,
            "professional_council_issuer": cls._professional_council_issuer,
            "pis_pasep": cls._pis_pasep,
            "nis": cls._pis_pasep,
            "uniao_estavel": _default_not_none,
            "titulo_eleitor": cls._titulo_eleitor,
            "municipio_titulo_id": cls._municipio_titulo,
            "secao_titulo": cls._secao_titulo,
            "zona_titulo": cls._zona_titulo,
            "ctps": cls._ctps,
            "ctps_state_id": cls._ctps_state,
            "serie_ctps": cls._serie_ctps,
            "reservista": cls._reservista,
            "classe_reservista": cls._classe_reservista,
            "foto_id": cls._foto,
            "municipio_naturalidade_id": cls._municipio_naturalidade,
            "country_id": cls._nationality,
            "nationality_id": cls._nationality,
            "nationality_birth_id": cls._nationality,
            "rg_uf_id": cls._rg_uf,
        }

    def __str__(self):
        return f"{self.natural_person} modificado em {DateUtils.date_to_str(self.when)}"

    @classmethod
    def _natural_person_from_instance(cls, instance):
        if isinstance(instance, (Endereco, Telefone)):
            if isinstance(
                instance.person, (PessoaFisica, PessoaJuridica, AnonymousPerson)
            ):
                return instance.person
            return instance.person.pessoafisica
        if isinstance(instance, Dependencia):
            return instance.dependente.servidor.pessoa_fisica
        return instance

    @classmethod
    def _values_from_instance(cls, instance):
        return instance.diff

    @classmethod
    def _check_send_esocial(cls, instance):
        """Verifica se o objeto deve ser enviado para o eSocial a partir das diferenças do objeto que foi modificado.
        Aplica o resultado no dicionário field_value.

        Args:
            diff (dict): difenças."""
        fields_to_history = NaturalPersonHistory.FIELDS_TO_HISTORY.get(
            instance._meta.model_name, [False]
        )
        diff = NaturalPersonHistory._values_from_instance(instance)
        send_esocial = False
        for key in diff:
            _len_history = len(fields_to_history)
            if _len_history == 1 and fields_to_history[0] is True:
                send_esocial = True
                break
            elif _len_history > 1 and key in fields_to_history:
                send_esocial = True
                break

        _len_history = len(fields_to_history)
        if _len_history == 1 and fields_to_history[0] is True:
            send_esocial = True
        return send_esocial

    @classmethod
    def _fill_from_instance(cls, instance):
        """Este método preenche um dicionário com os valores do objeto.

        Args:
            instance (PessoaFisica, Telefone, Endereco, Dependencia): PessoaFisica, Telefone, Endereco, Dependencia.

        Returns:
            dict: valores para serem salvos no histórico."""
        from copy import deepcopy

        field_value = {}

        def _default_method(person, value):
            return value

        _diff = NaturalPersonHistory._values_from_instance(instance)
        _diff_original = deepcopy(_diff)
        person = cls._natural_person_from_instance(instance)

        send_esocial = NaturalPersonHistory._check_send_esocial(instance)

        def _get_values_natural_person(_diff):
            _method_evaluate = NaturalPersonHistory.method_evaluate()
            for fld in NaturalPersonHistory._meta.fields:
                value = getattr(person, fld.attname, None)
                value = _method_evaluate.get(fld.attname, _default_method)(
                    person, value
                )
                if fld.attname in _diff_original:
                    value = _diff_original.get(fld.attname, (None,))
                _diff.update({fld.attname.replace("_id", ""): (value, value)})

        def _get_values_phone(_diff):
            diff_numero = None
            diff_tipo_telefone = (None, None)
            diff_publico = None
            diff_description = None
            if "phone_main" in _diff and _diff_original.get(
                "phone_main", (None, None)
            ) != (None, None):
                diff_numero = _diff_original.get("phone_main")

            if "tipo_telefone" in _diff_original and _diff_original.get(
                "tipo_telefone", (None, None)
            ) != (None, None):
                diff_tipo_telefone = _diff_original.get("tipo_telefone")
            elif "tipo_telefone" in instance._nph_diff and instance._nph_diff.get(
                "tipo_telefone", (None, None)
            ) != (None, None):
                diff_tipo_telefone = instance._nph_diff.get("tipo_telefone")

            if "publico" in _diff_original and _diff_original.get(
                "publico", (None, None)
            ) != (None, None):
                diff_publico = _diff_original.get("publico")
            if "description" in _diff_original and _diff_original.get(
                "description", (None, None)
            ) != (None, None):
                diff_description = _diff_original.get("description")

            for phone in person.phone.all():
                if phone.tipo_telefone == TYPE_PHONE_EMERGENCY:
                    contact_emergency_name = (
                        diff_description
                        if diff_description
                        else (phone.description, phone.description)
                    )
                    _diff.update({"contact_emergency_name": contact_emergency_name})
                    phone_contact_emergency = (
                        diff_numero if diff_numero else (phone.numero, phone.numero)
                    )
                    _diff.update({"phone_contact_emergency": phone_contact_emergency})
                elif phone.main:
                    phone_main = (
                        diff_numero if diff_numero else (phone.numero, phone.numero)
                    )
                    _diff.update({"phone_main": phone_main})
                    phone_type = (
                        diff_tipo_telefone
                        if diff_tipo_telefone != (None, None)
                        and TYPE_PHONE_EMERGENCY not in diff_tipo_telefone
                        else (phone.tipo_telefone, phone.tipo_telefone)
                    )
                    _diff.update({"phone_type": phone_type})
                    phone_public = (
                        diff_publico if diff_publico else (phone.publico, phone.publico)
                    )
                    _diff.update({"phone_public": phone_public})
                    phone_description = (
                        diff_description
                        if diff_description
                        else (phone.description, phone.description)
                    )
                    _diff.update({"phone_description": phone_description})

        def _get_values_address(_diff):
            address = person.address.last()

            tipo_logradouro = getattr(address, "tipo_logradouro", None)
            tipo_logradouro = (tipo_logradouro, tipo_logradouro)
            tipo_endereco = getattr(address, "tipo_endereco", None)
            tipo_endereco = (tipo_endereco, tipo_endereco)
            municipio = getattr(address, "municipio", None)
            municipio = (municipio, municipio)
            logradouro = getattr(address, "logradouro", None)
            logradouro = (logradouro, logradouro)
            bairro = getattr(address, "bairro", None)
            bairro = (bairro, bairro)
            cep = getattr(address, "cep", None)
            cep = (cep, cep)
            numero = getattr(address, "numero", None)
            numero = (numero, numero)
            complemento = getattr(address, "complemento", None)
            complemento = (complemento, complemento)
            outsider = getattr(address, "outsider", None)
            outsider = (outsider, outsider)
            country = getattr(address, "country", None)
            country = (country, country)
            outsider_citty = getattr(address, "outsider_citty", None)
            outsider_citty = (outsider_citty, outsider_citty)

            if "tipo_logradouro" in _diff and _diff_original.get(
                "tipo_logradouro", (None, None)
            ) != (None, None):
                tipo_logradouro = _diff_original.get("tipo_logradouro", (None, None))
            if "tipo_endereco" in _diff and _diff_original.get(
                "tipo_endereco", (None, None)
            ) != (None, None):
                tipo_endereco = _diff_original.get("tipo_endereco", (None, None))
            if "municipio" in _diff and _diff_original.get(
                "municipio", (None, None)
            ) != (None, None):
                municipio = _diff_original.get("municipio", (None, None))
            if "logradouro" in _diff and _diff_original.get(
                "logradouro", (None, None)
            ) != (None, None):
                logradouro = _diff_original.get("logradouro", (None, None))
            if "bairro" in _diff and _diff_original.get("bairro", (None, None)) != (
                None,
                None,
            ):
                bairro = _diff_original.get("bairro", (None, None))
            if "cep" in _diff and _diff_original.get("cep", (None, None)) != (
                None,
                None,
            ):
                cep = _diff_original.get("cep", (None, None))
            if "numero" in _diff and _diff_original.get("numero", (None, None)) != (
                None,
                None,
            ):
                numero = _diff_original.get("numero", (None, None))
            if "complemento" in _diff and _diff_original.get(
                "complemento", (None, None)
            ) != (None, None):
                complemento = _diff_original.get("complemento", (None, None))
            if "outsider" in _diff and _diff_original.get("outsider", (None, None)) != (
                None,
                None,
            ):
                outsider = _diff_original.get("outsider", (None, None))
            if "country" in _diff and _diff_original.get("country", (None, None)) != (
                None,
                None,
            ):
                country = _diff_original.get("country", (None, None))
            if "outsider_citty" in _diff and _diff_original.get(
                "outsider_citty", (None, None)
            ) != (None, None):
                outsider_citty = _diff_original.get("outsider_citty", (None, None))

            _diff.update({"tipo_logradouro": tipo_logradouro})
            _diff.update({"tipo_endereco": tipo_endereco})
            _diff.update({"municipio": municipio})
            _diff.update({"logradouro": logradouro})
            _diff.update({"bairro": bairro})
            _diff.update({"cep": cep})
            _diff.update({"numero": numero})
            _diff.update({"complemento": complemento})
            _diff.update({"outsider": outsider})
            _diff.update({"country": country})
            _diff.update({"outsider_citty": outsider_citty})

        _get_values_natural_person(_diff)
        _get_values_phone(_diff)
        _get_values_address(_diff)

        def _fill(_diff):
            """Preenche os valores de _diff em field_value.

            Args:
                _diff (dict): dict com os valores dos campos do objeto."""
            for key in _diff:
                value = _diff.get(key, (None, None))
                value = value[0] if len(value) == 1 else value[1]
                field_value.update({key: value})

        _fill(_diff)

        for key in (
            "id",
            "created_by",
            "modified_by",
            "created_at",
            "modified_at",
            "pessoa_ptr",
            "when",
            "natural_person",
            "data_alteracao",
        ):
            field_value.pop(key, None)

        field_value.update({"send_esocial": send_esocial})

        return field_value

    @classmethod
    def _when(cls, *args):
        """Retorna a data de hoje.

        Returns:
            date: date.today()"""
        return date.today()

    @classmethod
    def validate(cls, instance):
        if not cls._natural_person_from_instance(instance).is_servidor():
            log.info("Histórico apenas para servidor.")
            return False
        return True

    @classmethod
    def write_history(cls, instance_changed, when=None):
        """Escreve o histórico da instância(instance_changed).

        Args:
            instance_changed (object): instância que foi modificada.
            when (date, optional): quando ocorreu a mudança. Defaults to None, e será date.today().

        Returns:
            NaturalPersonHistory, bool: NaturalPersonHistory, bool(False, True) encontrada ou criada.
        """
        if not instance_changed:
            return

        instance_changed._nph_diff = {}
        if isinstance(instance_changed, Telefone):
            if (
                instance_changed.tipo_telefone == TYPE_PHONE_EMERGENCY
                and "tipo_telefone" not in instance_changed.diff
            ):
                instance_changed._nph_diff.update(
                    {"tipo_telefone": (None, TYPE_PHONE_EMERGENCY)}
                )

        if not when:
            when = NaturalPersonHistory._when(instance_changed)

        created = False
        history = None

        if (
            hasattr(instance_changed, "servidor_set")
            and instance_changed.servidor_set.exists()
            and instance_changed.servidor_set.first().type_by_possession == "COE"
        ):
            return

        if NaturalPersonHistory.validate(instance_changed):
            history, created = NaturalPersonHistory.objects.get_or_create(
                natural_person=NaturalPersonHistory._natural_person_from_instance(
                    instance_changed
                ),
                when=when,
                defaults=NaturalPersonHistory._fill_from_instance(instance_changed),
            )
        return history, created

    @classmethod
    def cmd_create_history_dependence(cls, dependence=[]):
        """Este script criará NaturalPersonHistory baseado em na vigência de Dependencia.

        Args:
            dependence(list): lista de pk de Dependencia.
        """
        today = date.today()

        def _validate_date(_date):
            """Validar a data de criação do histórico. Não criará histórico para datas anteriores a 22/11/2021."""
            return today >= _date > date(2021, 11, 22)

        def _create(dep, _date):
            if _validate_date(_date):
                history, created = NaturalPersonHistory.write_history(dep, when=_date)
                msg = "Criou" if created else "Encontrou"
                msg = f"{msg} histórico para {dep} em {_date}: {history}\n"
                print(msg)
                log.info(msg)

        def _create_for_dependence():
            """Criará histórico para Dependencia. Utilizando a data de início e fim como referência."""
            dependencies = Dependencia.objects.esocial_valid()
            if dependence:
                dependencies = dependencies.filter(pk__in=dependence)

            for dep in dependencies.order_by("data_fim"):
                _create(dep, dep.data_inicio)
                if dep.data_fim:
                    _create(dep, dep.data_fim + relativedelta(days=1))

        _create_for_dependence()


class HigherEducationInstitution(models.Model):
    code = models.IntegerField("Código", unique=True)
    name = models.CharField("Nome", max_length=150)
    acronym = models.CharField("Sigla", max_length=50, null=True, blank=True)
    municipality = models.ForeignKey(
        Localidade, null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.code} - {self.name} - {self.acronym}"


class CourseCineBrasil(models.Model):
    code = models.CharField("Código", unique=True, max_length=20)
    label = models.CharField("Rótulo", max_length=150)

    def __str__(self):
        return f"{self.code} - {self.label}"


class ConfigPeriodoCumulativoSubstituicao(AuditTimestampModel):
    """Configuração do periodo de vendas do cumulativos de substituições"""

    titulo = models.CharField(max_length=250, verbose_name="Título")
    data_inicio_periodo = models.DateField(verbose_name="Data Início de Venda")
    data_fim_periodo = models.DateField(
        verbose_name="Data Fim de Venda", null=True, blank=True
    )
    data_inicio_abrangencia = models.DateField(
        verbose_name="Data Início da Abrangência"
    )
    data_fim_abrangencia = models.DateField(
        verbose_name="Data Fim da Abrangência", null=True, blank=True
    )

    class Meta:
        unique_together = ("titulo", "data_inicio_periodo", "data_inicio_abrangencia")
        ordering = ("-data_inicio_periodo", "-data_fim_periodo")

    def __str__(self):
        return f"{self.titulo}"

    def validar_periodo_vendas_inicio_fim(self):
        if self.data_fim_periodo and self.data_fim_periodo < self.data_inicio_periodo:
            raise Exception(
                "A data final do período de vendas não pode ser menor que a inicial."
            )

    def validar_periodo_abrangencia_inicio_fim(self):
        if (
            self.data_fim_abrangencia
            and self.data_fim_abrangencia < self.data_inicio_abrangencia
        ):
            raise Exception(
                "A data final do período de abrangência não pode ser menor que a inicial."
            )

    def validar_periodo_vendas_concomitante(self):
        q_periodos = ConfigPeriodoCumulativoSubstituicao.objects.filter(
            Q(
                data_inicio_periodo__gte=self.data_inicio_periodo,
                data_fim_periodo__lte=self.data_fim_periodo,
            )
            | Q(
                data_inicio_periodo__gte=self.data_inicio_periodo,
                data_inicio_periodo__lte=self.data_fim_periodo,
            )
            | Q(
                data_inicio_periodo__lte=self.data_inicio_periodo,
                data_fim_periodo__lte=self.data_fim_periodo,
            )
        ).exclude(data_fim_periodo__lte=self.data_inicio_periodo)

        if self.pk:
            q_periodos = q_periodos.exclude(pk=self.pk)

        if q_periodos.exists():
            raise Exception("Já existe um Período de vendas na data informada.")

    def validar_registro_unico(self):
        q_periodos = ConfigPeriodoCumulativoSubstituicao.objects.filter(
            titulo=self.titulo,
            data_inicio_periodo=self.data_inicio_periodo,
            data_inicio_abrangencia=self.data_inicio_abrangencia,
        )
        if self.pk:
            q_periodos = q_periodos.exclude(pk=self.pk)

        if q_periodos.exists():
            raise Exception(
                """Registro já existente, não pode existir registros com título,
                            data início de período de vendas e data de início de abrangência de substituições iguais."""
            )

    def validar_venda_abrangencia(self):
        if self.data_fim_abrangencia > self.data_fim_periodo:
            raise Exception(
                """ O período de abrangência não pode ser superior ao período de vendas."""
            )

    def validacao(self):
        self.validar_periodo_vendas_inicio_fim()
        self.validar_periodo_abrangencia_inicio_fim()
        self.validar_periodo_vendas_concomitante()
        self.validar_venda_abrangencia()

    def save(self, *args, **kargs):
        self.validacao()
        return super().save(*args, **kargs)

    def full_clean(self):
        self.validar_registro_unico()
        return super().full_clean()


conf_to_serialize()

Workplace = Lotacao
EmployeeWorkplace = ServidorLotacao
Employee = Servidor
JobPosition = Cargo

auditlog.register(Servidor)
auditlog.register(Lotacao)
auditlog.register(Cargo)
auditlog.register(CargoQuadro)
auditlog.register(Quadro)
auditlog.register(ConfigJobPosition)
auditlog.register(ServidorLotacao)
auditlog.register(MovimentacaoPessoal)
auditlog.register(MovimentacaoSubstituicao)
auditlog.register(MovimentacaoTeletrabalho)
auditlog.register(MetaTeletrabalho)
auditlog.register(Localidade)
auditlog.register(Dependente)
auditlog.register(Dependencia)
auditlog.register(PessoaFisica)
auditlog.register(CargaHoraria)
auditlog.register(HoursWorkContract)
