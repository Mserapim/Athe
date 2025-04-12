# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes:

:Classes:
    :class:`DocumentType`,
    :class:`ControlType`,
    :class:`Log`,
    :class:`Control`,
    :class:`ProtocolControl`,
    :class:`AllowedListItem`,
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import Permission, User
from django.db import models, transaction
from django.template import loader
from django.utils.html import strip_tags
from django.utils.text import slugify

# from adm.diarias.models import Solicitacao as Daily
from common.saci.models import Attendance
from contrib.middleware import get_current_user
from contrib.nil import nil_datetime
from contrib.utils import getLogger, has_direct_perm, person_from_user
from edocs.protocolo.models import Protocolo as Protocol
from ged.models import Arquivo as File
from rh.models import OrgaoGeral as PublicEntity, Pessoa as Person
from standard.models import AuditTimestampModel, Choice


log = getLogger(__name__)


class DocumentType(AuditTimestampModel):
    """Classe Tipo de Documento.

    O propósito deste modelo é unificar os tipos de documentos já utilizados
    nos modelos dos softwares diversos que lidam com documento.

    """

    title = models.CharField(max_length=100, verbose_name="Título")
    slug = models.SlugField(
        max_length=100, db_index=True, verbose_name="Slug", null=True, blank=True
    )
    description = models.TextField(null=True, blank=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Tipo de Documento"

    def __str__(self):
        return self.title

    @classmethod
    def request(cls, title):
        """Retorna uma instância para o tipo de documento
        requisitado. Se o tipo não existir, será cadastrado.
        """
        instance, created = cls.objects.get_or_create(title=title)
        return instance

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(DocumentType, self).save(*args, **kwargs)


class ControlType(AuditTimestampModel):
    """Classe Nível de Acesso.

    Essa classe define os atributos de classificação de acesso a um documento.

    """

    title = models.CharField(max_length=50, verbose_name="Título")
    is_secret = models.BooleanField(default=False, verbose_name="É sigiloso")
    not_allow_admin_access = models.BooleanField(
        default=False, verbose_name="Desautoriza acesso da comissão"
    )
    required_permission = models.ForeignKey(
        Permission, on_delete=models.PROTECT, verbose_name="Permissão necessária"
    )
    quantity = models.PositiveSmallIntegerField(
        verbose_name="Número máximo de aditamentos"
    )
    weight = models.PositiveSmallIntegerField(verbose_name="Peso")
    max_period = models.PositiveSmallIntegerField(verbose_name="Prazo máximo (anos)")
    enabled = models.BooleanField(default=True, verbose_name="Habilitado")

    class Meta:
        verbose_name = "Nível de Acesso"
        ordering = ("weight",)
        permissions = (
            ("can_use_level_1_classification", "Pode usar classificação nível 1"),
            ("can_use_level_2_classification", "Pode usar classificação nível 2"),
            ("can_use_level_3_classification", "Pode usar classificação nível 3"),
            ("can_use_level_4_classification", "Pode usar classificação nível 4"),
            ("can_use_level_5_classification", "Pode usar classificação nível 5"),
            ("can_use_level_6_classification", "Pode usar classificação nível 6"),
            ("can_use_level_7_classification", "Pode usar classificação nível 7"),
            ("can_use_level_8_classification", "Pode usar classificação nível 8"),
            ("can_use_level_9_classification", "Pode usar classificação nível 9"),
            ("can_use_level_10_classification", "Pode usar classificação nível 10"),
        )

    def __str__(self):
        return self.title

    def can_be_used_by(self, user):
        """can_be_used_by(user)

        Checks if user has permission to use this ControlType.
        Keyword arguments:
        user: An instance from User.
        """
        if not isinstance(user, User):
            raise TypeError("You must specify an instance from User.")

        permission = ".".join(
            [
                self.required_permission.content_type.app_label,
                self.required_permission.codename,
            ]
        )

        return has_direct_perm(user, permission)


class LegalPrerogative(AuditTimestampModel):
    """Hipótese Legal.

    Essa classe pode ser pensada como um sub nível de acesso.

    """

    title = models.CharField(max_length=150, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    control_type = models.ForeignKey(
        ControlType,
        verbose_name="Nível de Acesso",
        related_name="prerogatives",
        on_delete=models.CASCADE,
    )
    enabled = models.BooleanField(default=True, verbose_name="Habilitado")

    class Meta:
        verbose_name = "Hipótese Legal"
        ordering = ("created_at",)

    def __str__(self):
        return "{} : {}".format(self.control_type.title, self.title)


class Control(AuditTimestampModel):
    """Classe de controle de Acesso a Documento (Base).

    O propósito deste modelo é representar um documento que teve sua informação classificada.
    Ele agrupa as informações mais comuns que podem ser encontradas em um documento qualquer,
    e o tipo de classificação que foi realizada.

    """

    control_type = models.ForeignKey(
        ControlType,
        verbose_name="Nível de Acesso",
        related_name="controls",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    legal_prerogative = models.ForeignKey(
        LegalPrerogative,
        verbose_name="Hipótese legal",
        related_name="controls",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    document_type = models.ForeignKey(
        DocumentType,
        verbose_name="Tipo de Documento",
        related_name="controls",
        on_delete=models.PROTECT,
    )
    final_term = models.DateTimeField(verbose_name="Termo Final", null=True, blank=True)
    document_number = models.CharField(max_length=50, verbose_name="Nº do Documento")
    source = models.ForeignKey(
        PublicEntity, verbose_name="Origem", on_delete=models.PROTECT
    )
    subject = models.CharField(max_length=255, verbose_name="Assunto")
    production_date = models.DateTimeField(verbose_name="Data de produção")
    month = models.PositiveSmallIntegerField(
        verbose_name="Mês", db_index=True, null=True, blank=True
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Ano", db_index=True, null=True, blank=True
    )
    special_type = models.CharField(max_length=60, db_index=True, null=True, blank=True)

    # Adicionado para atender a classificação/reclassificação de EDOCs no modo edição.
    is_committed = models.BooleanField(default=True, verbose_name="Efetivado")

    class Meta:
        verbose_name = "Controle de Acesso"
        permissions = (
            ("is_admin", "É administrador"),
            (
                "is_allowed_to_classify",
                "Está autorizado a classificar controle de acesso",
            ),
            (
                "is_allowed_to_reclassify",
                "Está autorizado a reclassificar controle de acesso",
            ),
            (
                "is_allowed_to_declassify",
                "Está autorizado a desclassificar controle de acesso",
            ),
            ("is_allowed_to_reduce_deadline", "Está autorizado a reduzir prazo"),
            ("is_allowed_to_extend_deadline", "Está autorizado a prorrogar prazo"),
        )

    def __str__(self):
        return self.document_number

    @property
    def can_read(self):
        """Retorna True se o usuário corrente pode ler o documento.

        O documento só poderá ser lido quando:
            - Nível de Acesso não tiver grau de sigilo (is_secret==False).
            - Usuário corrente for um admin e o Nível de Acesso permitir seu acesso.
            - Usuário corrente estiver na lista de credenciais.
        """
        answer = False
        if self.control_type:
            if not self.control_type.is_secret:
                answer = True
            if (
                not answer
                and self.is_admin
                and not self.control_type.not_allow_admin_access
            ):
                answer = True
            if not answer and self.has_current_user_in_allowedlist():
                answer = True
        else:
            answer = True

        return answer

    def has_person_in_allowedlist(self, person):
        """has_person_in_allowedlist

        Retorna True se person pode acessar o documento, caso contrário retorna False.
        Keywork arguments:
        person: Instância de rh.models.Pessoa
        """
        return AllowedListItem.objects.filter(
            control=self, person=person, revoked_at=None
        ).exists()

    def has_current_user_in_allowedlist(self):
        """Retorna True se o usuário corrente pode acessar o documento, caso contrário retorna False."""
        return self.has_person_in_allowedlist(
            person=person_from_user(get_current_user())
        )

    def grant_person_access(self, person, bypass_validation=False):
        """Grants access to `person`.

        Arguments:
          person: Any instance from rh.models.Pessoa.
          bypass_validation: Do you want to ignore validations?

        """
        AllowedListItem.add_person(
            control=self, person=person, bypass_validation=bypass_validation
        )

    def revoke_person_access(self, person):
        """revoke_person_access(person=None)

        Revoga acesso de person ao documento.
        Keywork arguments:
        person: Instância de rh.models.Pessoa
        """
        AllowedListItem.revoke_person(control=self, person=person)

    @property
    def allowedlist(self):
        """
        Retorna lista de pessoas que podem acessar o documento restrito.
        """
        return AllowedListItem.objects.filter(control=self, revoked_at=None)

    @property
    def my_origin(self):
        if self.special_type and hasattr(self, self.special_type):
            return getattr(self, self.special_type)
        return self

    @property
    def rendered(self):
        template = loader.get_template("common/document_access/control.html")
        return template.render(
            {
                "instance": self,
                "legal_prerogative": (
                    self.legal_prerogative.title if self.legal_prerogative else "-"
                ),
            }
        )

    @property
    def rendered_content(self):
        raise NotImplementedError(
            f"Implementar retorno do renderizador na classe {self.my_origin._meta.object_name}."
        )

    @property
    def appends_of_document(self):
        raise NotImplementedError(
            f"Implementar retorno de apêndices na classe {self.my_origin._meta.object_name}."
        )

    # _TODO_ Desenvolver a lógica na próxima sprint.
    def _last_movement_date(self):
        # raise NotImplementedError('Abstract method not implemented.')
        return datetime(1900, 1, 1, 0, 0)

    @property
    def last_movement_date(self):
        return self.my_origin._last_movement_date()

    @property
    def is_admin(self):
        """
        Retorna True se o usuário corrente for admin (fizer parte da comissão ou meramente admin).
        """

        return has_direct_perm(get_current_user(), "document_access.is_admin")

    @property
    def is_public(self):
        return not bool(self.control_type)

    @property
    def is_secret(self):
        return self.control_type.is_secret if self.control_type else False

    @property
    def control_type_title(self):
        return self.control_type.title if self.control_type is not None else "Público"

    def _validate_justification(self):
        if not self.justification or not strip_tags(self.justification):
            raise Exception("É necessário informar uma justificativa.")

    @classmethod
    def validate_classify(cls, control_type, legal_prerogative):
        if not control_type:
            raise Exception("É necessário informar um Nível de Acesso.")

        if not legal_prerogative:
            raise Exception("É necessário informar um Hipótese Legal.")

        if not control_type.enabled:
            raise Exception(
                f"Não consegui classificar o documento, pois o Nível de Acesso '{control_type.title}' está desabilitado."
            )

        if not legal_prerogative.enabled:
            raise Exception(
                f"Não consegui classificar o documento, pois a Hipótese Legal '{legal_prerogative.title}' está desabilitada."
            )

        current_user = get_current_user()
        if not has_direct_perm(current_user, "document_access.is_allowed_to_classify"):
            raise Exception(
                "Usuário não autorizado a classificar informações de documentos."
            )

        if not control_type.can_be_used_by(user=current_user):
            raise Exception(
                f'Usuário não autorizado a classificar com o Nível de Acesso "{control_type.title}".'
            )

    def validate_declassify(self):
        if not self.can_read or not has_direct_perm(
            get_current_user(), "document_access.is_allowed_to_declassify"
        ):
            raise Exception("Usuário não autorizado a desclassificar documentos.")

        self._validate_justification()

    def validate_reclassify(self):
        if not self.control_type:
            raise Exception("É necessário informar um Nível de Acesso.")

        if not self.legal_prerogative:
            raise Exception("É necessário informar um Hipótese Legal.")

        if not self.control_type.enabled:
            raise Exception(
                f"Não consegui reclassificar o documento, pois o Nível de Acesso '{self.control_type.title}' está desabilitado."
            )

        if not self.legal_prerogative.enabled:
            raise Exception(
                f"Não consegui reclassificar o documento, pois a Hipótese Legal '{self.legal_prerogative.title}' está desabilitada."
            )

        old = self.__class__.objects.get(pk=self.pk)

        if self.control_type == old.control_type:
            raise Exception("O Nível de Acesso deve ser diferente do anterior.")

        if not old.can_read or not has_direct_perm(
            get_current_user(), "document_access.is_allowed_to_reclassify"
        ):
            raise Exception("Usuário não autorizado a reclassificar documentos.")

        self._validate_justification()

    def validate_deadline_change(self):
        if not self.control_type:
            raise Exception(
                "Não faz sentido alterar o prazo de um documento sem controle de acesso."
            )
        if not self.final_term:
            raise Exception("É necessário informar um novo prazo final.")
        if self.final_term < datetime.now():
            raise Exception("O novo prazo final não pode ser data do passado.")
        if self.final_term < self.old_final_term:
            if has_direct_perm(
                get_current_user(), "document_access.is_allowed_to_reduce_deadline"
            ):
                self.label_action = "Redução de prazo"
            else:
                raise Exception(
                    "Você não tem permissão para reduzir o prazo deste controle."
                )
        elif self.final_term > self.old_final_term:
            if has_direct_perm(
                get_current_user(), "document_access.is_allowed_to_extend_deadline"
            ):
                self.label_action = "Prorrogação de prazo"
            else:
                raise Exception(
                    "Você não tem permissão para prorrogar o prazo deste controle."
                )
        else:
            raise Exception("O novo prazo não difere do antigo.")

        self._validate_justification()

    @classmethod
    def calculates_final_term(cls, control_type, production_date):

        final_term = None

        if control_type and control_type.max_period > 0:
            final_term = production_date + relativedelta(years=control_type.max_period)

        return final_term

    @classmethod
    def classify(
        cls,
        document,
        control_type,
        legal_prerogative,
        justification,
        is_committed=True,
        bypass_validation=False,
    ):
        raise NotImplementedError("Implementar o método classify.")

    def reclassify(
        self, control_type, legal_prerogative, justification, is_committed=True
    ):
        self.justification = justification
        self.control_type = control_type
        self.legal_prerogative = legal_prerogative
        self.is_committed = is_committed
        self.validate_reclassify()
        self.final_term = self.__class__.calculates_final_term(
            control_type, self.production_date
        )

        with transaction.atomic():
            self.save()

            # Adiciona usuário corrente na AllowedList.
            if self.control_type.is_secret:
                person = person_from_user(get_current_user())
                if person:
                    self.grant_person_access(person=person, bypass_validation=True)

            # Registra a ação.
            Log.register(
                control=self,
                log_type=Log.logtype_by_label("Reclassificação"),
                description=justification,
            )

            self.my_origin.post_reclassify()

    def declassify(self, justification, bypass_validation=False):
        self.justification = justification

        if not bypass_validation:
            self.validate_declassify()

        self.control_type = None
        self.legal_prerogative = None
        self.final_term = None

        with transaction.atomic():
            self.save()

            Log.register(
                control=self,
                log_type=Log.logtype_by_label("Desclassificação"),
                description=justification,
            )

            self.my_origin.post_declassify()

    def sync_attachment_access(self):
        raise NotImplementedError(
            f"Implementar o método na classe {self.my_origin._meta.object_name}."
        )

    def post_classify(self):
        raise NotImplementedError(
            f"Implementar o método na classe {self.my_origin._meta.object_name}."
        )

    def post_reclassify(self):
        raise NotImplementedError(
            f"Implementar o método na classe {self.my_origin._meta.object_name}."
        )

    def post_declassify(self):
        raise NotImplementedError(
            f"Implementar o método na classe {self.my_origin._meta.object_name}."
        )

    def deadline_change(self, final_term=None, justification=""):
        self.old_final_term = self.final_term
        self.label_action = None
        self.final_term = final_term
        self.justification = justification
        self.validate_deadline_change()
        self.justification = "%s - O antigo prazo era %s e o atual é %s" % (
            self.justification,
            self.old_final_term,
            self.final_term,
        )

        with transaction.atomic():
            self.save()

            Log.register(
                control=self,
                log_type=Log.logtype_by_label(self.label_action),
                description=justification,
            )

    def commit(self):
        if self.control_type and not self.is_committed:
            with transaction.atomic():
                self.is_committed = True
                self.save()

                classification = Log.logtype_by_label("Classificação")
                reclassification = Log.logtype_by_label("Reclassificação")

                latest_log = self.logs.filter(
                    control_type=self.control_type,
                    legal_prerogative=self.legal_prerogative,
                    log_type__in=[classification, reclassification],
                ).latest("signed_at")

                latest_log.log_type = classification
                latest_log.is_committed = True
                latest_log.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.special_type = self._meta.model_name
            self.year = self.production_date.year
            self.month = self.production_date.month

        super(Control, self).save(*args, **kwargs)


class Log(models.Model):
    """Este modelo representa todas as mudanças na classificação de
    documentos refletidas no modelo Control.

    """

    description = models.TextField(verbose_name="Descrição", null=True, blank=True)
    log_type = models.PositiveSmallIntegerField(
        choices=Choice.get_choices_for("document_access", "LOG_TYPE"),
        verbose_name="Tipo",
    )
    control = models.ForeignKey(
        Control, verbose_name="Controle", related_name="logs", on_delete=models.CASCADE
    )
    control_type = models.ForeignKey(
        ControlType,
        verbose_name="Nível de Acesso",
        related_name="logs",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    legal_prerogative = models.ForeignKey(
        LegalPrerogative,
        verbose_name="Hipótese legal",
        related_name="logs",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    signed_by = models.ForeignKey(
        User, verbose_name="Registrado por", on_delete=models.PROTECT
    )
    signed_at = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")
    validation_bypassed = models.BooleanField(
        default=False, verbose_name="Validação ignorada"
    )
    is_committed = models.BooleanField(default=True, verbose_name="Efetivado")

    class Meta:
        verbose_name = "Registro de Mudanças"
        ordering = ("-signed_at",)

    def __str__(self):
        return "Documento número {} de {}.".format(
            self.control.document_number, self.control.source
        ).upper()

    @property
    def rendered(self):
        template = loader.get_template("common/document_access/log.html")

        return template.render(
            {
                "description": self.description or "",
                "log_type_display": self.get_log_type_display(),
                "document_number": self.control.document_number,
                "control_type": self.control_type.title if self.control_type else "",
                "legal_prerogative": (
                    self.legal_prerogative.title if self.legal_prerogative else ""
                ),
                "signed_by": self.signed_by,
                "signed_at": self.signed_at,
                "validation_bypassed": self.validation_bypassed,
                "is_committed": self.is_committed,
            }
        )

    @classmethod
    def logtype_by_label(cls, label):
        logtype = Choice.objects.get(
            app_label="document_access", name="LOG_TYPE", label=label
        )

        return logtype.value

    @classmethod
    def register(cls, control, log_type, description="", validation_bypassed=False):
        """Add a person to a control's AllowedList

        Keyword arguments:
          control: An instance from Control.
          log_type: The type of register of the action performed.
          description: An extra detail of the register.
        """
        log = cls()
        log.description = description
        log.log_type = log_type
        log.control = control
        log.control_type = control.control_type
        log.legal_prerogative = control.legal_prerogative
        log.signed_by = get_current_user()
        log.validation_bypassed = validation_bypassed
        log.is_committed = control.is_committed
        log.save()


class AllowedListItem(AuditTimestampModel):
    """Registra a associação das pessoas ao control.
    Este modelo representa todas as pessoas autorizadas a acessar um determinado documento.
    """

    control = models.ForeignKey(
        Control,
        on_delete=models.CASCADE,
        verbose_name="Controle",
        related_name="allowedlistitems",
    )
    person = models.ForeignKey(Person, on_delete=models.PROTECT, verbose_name="Pessoa")

    granted_by = models.ForeignKey(
        User,
        verbose_name="Autorizado por",
        related_name="+",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    granted_at = models.DateTimeField(
        verbose_name="Autorizado em", null=True, blank=True
    )

    revoked_by = models.ForeignKey(
        User,
        verbose_name="Revogado por",
        related_name="+",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    revoked_at = models.DateTimeField(verbose_name="Revogado em", null=True, blank=True)

    class Meta:
        verbose_name = "Item de Lista de Credenciais"
        ordering = ("control", "granted_at")
        unique_together = ("control", "person", "revoked_at")

    class AccessAlreadyGranted(Exception):
        pass

    class AccessAlreadyRevoked(Exception):
        pass

    class ControlTypeDoesNotExist(Exception):
        pass

    class ControlTypeIsNotSecret(Exception):
        pass

    class CurrentUserNotAllowed(Exception):
        pass

    class AdminNotAllowed(Exception):
        pass

    def __str__(self):
        can_or_not = "não pode" if self.revoked_at else "pode"
        return f"{str(self.person)} {can_or_not} acessar {self.control.document_number}"

    @classmethod
    def add_person(cls, control, person, bypass_validation=False):
        """Adds a person to a control's AllowedList.

        Arguments:
          control: Any instance from Control.
          person: Any instance from rh.models.Pessoa.
          bypass_validation: Do you want to ignore validations?

        """
        if control.control_type and not control.has_person_in_allowedlist(person):
            granted = cls(control=control, person=person)
            granted.save(bypass_validation=bypass_validation)
            return True

        return False

    @classmethod
    def revoke_person(cls, control, person):
        """Revokes a person from a control's AllowedList.

        Arguments:
        control: Any instance from Control.
        person: Any instance from rh.models.Pessoa.
        """
        if control.has_person_in_allowedlist(person):
            revoked = cls.objects.get(control=control, person=person, revoked_at=None)
            revoked.revoke()
            return True
        return False

    def revoke(self):
        if self.revoked_at:
            raise self.__class__.AccessAlreadyRevoked(
                f"Essa credencial já foi revogada em {nil_datetime(self.revoked_at, 'N/A')}"
            )

        self.revoked_by = get_current_user()
        self.revoked_at = datetime.now()

        self.save()

    def validate_new_item(self):
        cls = self.__class__

        if not self.control.control_type:
            raise cls.ControlTypeDoesNotExist(
                "Não é possível gerar uma credencial para um documento sem restrição de acesso."
            )

        if not self.control.control_type.is_secret:
            raise cls.ControlTypeIsNotSecret(
                "As credencias são somente para documentos classificados com grau de sigilo."
            )

        if self.control.has_person_in_allowedlist(person=self.person):
            raise cls.AccessAlreadyGranted(
                "Esta pessoa já estava credenciada para acessar o documento."
            )

    def validate_allowedlist_with_not_allow_admin_access(self):
        """Não permitir alteração da lista de credenciais quando o tipo
        de controle estiver com a flag not_allow_admin_access habilitada
        e o usuário corrente não estiver na lista.
        """
        if (
            self.control.control_type
            and self.control.control_type.not_allow_admin_access
            and not self.control.has_current_user_in_allowedlist()
        ):
            raise self.__class__.AdminNotAllowed(
                "Não foi possível alterar a lista de credenciais. "
                "O Nível de Acesso tem grau de sigilo ultrassecreto ou similar. "
                "É preciso constar na lista para alterá-la."
            )

    def validate_can_manage_list(self):
        """O usuário corrente pode gerenciar a lista de credenciais?

        Por gerenciar eu quero dizer fazer CRUD e revogar pessoas.

        A princípio, essa validação pode parecer desnecessária, devido à
        existência das permissões de CRUD básicas do Django.

        Porém, por motivos de praticidade, as permissões básicas, muito
        provavelmente, serão atribuídas a todos os usuários do Athenas,
        e, sendo assim, qualquer usuário, tendo acesso ao Grid desse
        modelo, poderia realizar operações de CRUD, e é aí que entra em
        ação a validação implementada aqui.
        """
        if (
            not self.control.has_current_user_in_allowedlist()
            and not self.control.is_admin
        ):
            raise self.__class__.CurrentUserNotAllowed(
                "Não foi possível alterar a lista de credenciais. "
                "Você precisa constar nela para alterá-la."
            )

    def save(self, bypass_validation=False, *args, **kwargs):
        if not bypass_validation:
            self.validate_can_manage_list()
            self.validate_allowedlist_with_not_allow_admin_access()

        if not self.pk:
            self.validate_new_item()

            self.granted_by = get_current_user()
            self.granted_at = datetime.now()

        super().save(*args, **kwargs)


class ProtocolMixin:
    """Mixin para subclasses de Control cujo atributo document seja uma chave-estrangeira para Protocolo."""

    @classmethod
    def classify(
        cls,
        document,
        control_type,
        legal_prerogative,
        justification,
        is_committed=True,
        bypass_validation=False,
    ):
        if not bypass_validation:
            cls.validate_classify(control_type, legal_prerogative)

        with transaction.atomic():
            control, created = cls.objects.get_or_create(
                document=document,
                defaults={
                    "document_type": DocumentType.request(document.tipo_documento.nome),
                    "document_number": document.codigo,
                    "source": document.orgao_geral_origem,
                    "subject": document.assunto,
                    "production_date": document.data_criacao,
                    "control_type": control_type,
                    "legal_prerogative": legal_prerogative,
                    "is_committed": is_committed,
                    "final_term": cls.calculates_final_term(
                        control_type=control_type, production_date=document.data_criacao
                    ),
                },
            )

            if created:
                # Adiciona usuário corrente na AllowedList.
                if control.control_type.is_secret:
                    person = person_from_user(get_current_user())
                    if person:
                        AllowedListItem.add_person(
                            control=control, person=person, bypass_validation=True
                        )

                # Registra a ação.
                Log.register(
                    control=control,
                    log_type=Log.logtype_by_label("Classificação"),
                    description=justification,
                    validation_bypassed=bypass_validation,
                )

                # Atualiza campos de flags legados.
                control.my_origin.post_classify()

        return control, created


class ProtocolControl(ProtocolMixin, Control):
    """Classe de controle de Acesso a Documento (Protocolo)."""

    document = models.OneToOneField(
        Protocol,
        verbose_name="Protocolo",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="protocol_control",
    )

    class Meta:
        verbose_name = "Controle de Sigilo de Protocolo"

    @property
    def rendered_content(self):
        content = None

        if self.can_read:
            content = self.document.rendered
        else:
            content = loader.get_template(
                "common/document_access/access-denied.html"
            ).render({"instance": self})

        return content

    @property
    def appends_of_document(self):
        appends_of_document = None

        if self.can_read:
            appends_of_document = self.document.appends_of_document
        else:
            appends_of_document = []

        return appends_of_document

    def _update_document(self, sigiloso):
        if self.document.cache_rendered:  # Protocolo não está mais em "modo de edição"?
            Protocol.objects.filter(pk=self.document.pk).update(
                sigiloso=sigiloso, cache_rendered=self.document.my_origin._renderer()
            )
        else:
            Protocol.objects.filter(pk=self.document.pk).update(sigiloso=sigiloso)

    def post_classify(self):
        self._update_document(sigiloso=True)
        self.sync_attachment_access()

    def post_reclassify(self):
        self._update_document(sigiloso=True)
        self.sync_attachment_access()

    def post_declassify(self):
        self._update_document(sigiloso=False)
        self.sync_attachment_access()

    def sync_attachment_access(self):
        access = File.GROUP if self.control_type else File.PUBLIC
        with transaction.atomic():
            for attachment in self.document.attachments.all():
                if attachment.attach.acesso != access:
                    attachment.attach.acesso = access
                    attachment.attach.save()


class AttendanceControl(Control):
    """Classe de controle de Acesso a Documento (Atendimento)."""

    document = models.OneToOneField(
        Attendance,
        verbose_name="Atendimento",
        related_name="attendance_control",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Controle de Sigilo de Atendimento"

    @property
    def rendered_content(self):
        content = None

        if self.can_read:
            content = self.document.rendered
        else:
            filename = "common/document_access/access-denied.html"
            content = loader.get_template(filename).render({"instance": self})

        return content

    @property
    def appends_of_document(self):
        appends_of_document = []

        if self.can_read:
            appends_of_document = self.document.appends_of_document

        return appends_of_document

    @classmethod
    def classify(
        cls,
        document,
        control_type,
        legal_prerogative,
        justification,
        is_committed=True,
        bypass_validation=False,
    ):
        if not bypass_validation:
            cls.validate_classify(control_type, legal_prerogative)

        with transaction.atomic():
            control, created = cls.objects.get_or_create(
                document=document,
                defaults={
                    "document_type": DocumentType.request(
                        document.protocol.tipo_documento.nome
                    ),
                    "document_number": document.protocol.codigo,
                    "source": document.protocol.orgao_geral_origem,
                    "subject": document.protocol.assunto,
                    "production_date": document.protocol.data_criacao,
                    "control_type": control_type,
                    "legal_prerogative": legal_prerogative,
                    "is_committed": is_committed,
                    "final_term": cls.calculates_final_term(
                        control_type=control_type,
                        production_date=document.protocol.data_criacao,
                    ),
                },
            )

            if created:
                # Adiciona usuário corrente na AllowedList.
                if control.control_type.is_secret:
                    person = person_from_user(get_current_user())
                    if person:
                        AllowedListItem.add_person(
                            control=control, person=person, bypass_validation=True
                        )

                # Registra a ação.
                Log.register(
                    control=control,
                    log_type=Log.logtype_by_label("Classificação"),
                    description=justification,
                    validation_bypassed=bypass_validation,
                )

                # Atualiza campos de flags legados.
                control.my_origin.post_classify()

        return control, created

    def _update_flags(self, value):
        Attendance.objects.filter(pk=self.document.pk).update(confidential=value)
        Protocol.objects.filter(pk=self.document.protocol.pk).update(sigiloso=value)

    def sync_attachment_access(self):
        access = File.GROUP if self.control_type else File.PUBLIC
        with transaction.atomic():
            for attachment in self.document.attached.all():
                if attachment.file_descriptor.acesso != access:
                    attachment.file_descriptor.acesso = access
                    attachment.file_descriptor.save()

    def post_classify(self):
        self._update_flags(value=True)
        self.sync_attachment_access()

    def post_reclassify(self):
        self._update_flags(value=True)
        self.sync_attachment_access()

    def post_declassify(self):
        self._update_flags(value=False)
        self.sync_attachment_access()
