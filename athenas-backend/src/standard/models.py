# -.- coding: utf-8 -.-
import decimal
import hashlib
import importlib
import math
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Q
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.utils import encoding
from auditlog.registry import auditlog

from contrib.middleware import get_current_user
from contrib.utils import getLogger

log = getLogger(__name__)


TYPEOFEXECUTION = {
    "CALCULO": "Cálculos para FOPAG",
    "LOADER": "Carregadores de arquivos",
    "JOB": "Executor de Tarefas",
}

CONFIGURATION_ITEM_CHOICE_NUMBER = 1
CONFIGURATION_ITEM_CHOICE_YES_NO = 2
CONFIGURATION_ITEM_CHOICE_TEXT = 3

CONFIGURATION_ITEM_CHOICE = {
    CONFIGURATION_ITEM_CHOICE_TEXT: "Texto",
    CONFIGURATION_ITEM_CHOICE_NUMBER: "Númerico",
    CONFIGURATION_ITEM_CHOICE_YES_NO: "Sim ou Não",
}


def norm(value):
    cast = {
        decimal.Decimal: lambda x: float(x or 0),
        int: lambda x: int(x or 0),
        float: lambda x: x or 0,
        models.BooleanField: lambda x: int(x or 0) == 1,
    }
    fn = cast.get(value.__class__, lambda x: x)
    return fn(value)


class InstallApplication:
    # prefixo_controller  = "FOLHA" #TODO: CASO SEJA OMITIDO, SERÁ UTILIZADO O NOME DA APPLICATION
    # itle_application   = "RH"     #TODO: TÍTULO QUE A APLICAÇÃO TERÁ NO MENU
    install_application = (
        False  # TODO: SERVIRÁ PARA DEFINIR SE O MODELO SERÁ INSTALADO COMO APLICAÇÃO
    )


class AuditableModel(models.Model):
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="created_by_user",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    modified_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="modified_by_user",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)


class AuditableMixins(object):

    AUDITABLE = {}

    @property
    def diff(self):
        d1 = self._initial_fields
        d2 = self.__dict__
        diffs = {}
        for k, v in list(d1.items()):
            if k in self.audit_fields:
                try:
                    if math.isclose(norm(v), norm(d2[k])) is False:
                        diffs[k] = (norm(v), norm(d2[k]))
                except TypeError:
                    if v != d2[k]:
                        diffs[k] = (v, d2[k])

        return diffs

    @property
    def old_fields(self):
        """
        Retorna um dicionário com os valores antigos dos campos,
        mas somente para os campos que estão sendo modificados.
        """

        return {k: v[0] for k, v in list(self.diff.items())}

    def _detect_auditable_fields(self):
        self.audit_fields = [
            f
            for f in self.AUDITABLE.get("fields", [])
            if f not in self.AUDITABLE.get("exclude", [])
        ]

    def _set_initial_fields(self):
        self._initial_fields = {
            k: self.__dict__[k] for k in self.__dict__ if k in self.audit_fields
        }

    def __init__(self, *args, **kargs):
        super(AuditableMixins, self).__init__(*args, **kargs)
        self._detect_auditable_fields()
        self._set_initial_fields()

    def _equals(self, other, exclude=[], only=[]):
        only = only if only else self.audit_fields
        audit_fields = set(self.audit_fields).intersection(only) - set(exclude)
        for key in audit_fields:
            try:
                if not math.isclose(getattr(self, key, 0), getattr(other, key, 0)):
                    return False
            except Exception:
                if getattr(self, key, None) != getattr(other, key, None):
                    return False
        return True

    def _differences(self, other, exclude=[], only=[]):
        diffs = []
        only = only if only else self.audit_fields
        audit_fields = set(self.audit_fields).intersection(only) - set(exclude)
        for key in audit_fields:
            try:
                if not math.isclose(getattr(self, key, 0), getattr(other, key, 0)):
                    diffs.append(key)
            except Exception:
                if getattr(self, key, None) != getattr(other, key, None):
                    diffs.append(key)
        return diffs

    @property
    def is_dirty(self):
        return (self.old_fields and True) or False

    @property
    def changed(self):
        return (self.old_fields and True) or False

    def clear_changes(self, keys=[]):
        keys_old_fields = (
            set(keys).intersection(set(self.old_fields.keys()))
            if keys
            else list(self.old_fields.keys())
        )
        for key in keys_old_fields:
            setattr(self, key, self.old_fields[key])


class AuditTimestampModel(AuditableMixins, models.Model):
    """ """

    class Meta:
        abstract = True

    DEFAULT_USER = None

    created_by = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    modified_by = models.ForeignKey(
        User, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def _set_initial_fields(self):
        super(AuditTimestampModel, self)._set_initial_fields()
        for field in AuditTimestampModel._meta.fields:
            if field.name in self.audit_fields:
                self.audit_fields.remove(field.name)

    def _detect_auditable_fields(self):
        fields = self.AUDITABLE.get("fields", [])
        if not fields:
            for f in self._meta.fields:
                fields.append(f.name)
                if (
                    f.is_relation
                    or isinstance(f, (ForeignKey, OneToOneField))
                    and self.__dict__.get(f"{f.name}_id", None)
                ):
                    # if hasattr(self, f'{f.name}_id'):
                    fields.append(f"{f.name}_id")

        self.audit_fields = [
            f for f in fields if f not in self.AUDITABLE.get("exclude", [])
        ]

    @classmethod
    def get_default_user(cls):
        user = None
        if cls.DEFAULT_USER:
            try:
                user = User.objects.get(username=cls.DEFAULT_USER)
            except Exception as e:
                log.exception(
                    "User %s does not exist! Configuration AuditTimestampModel.DEFAULT_USER with error."
                    % cls.DEFAULT_USER
                )

        return user

    def save(self, *args, **kargs):
        if not self.pk:
            self.created_by = get_current_user() or self.get_default_user()
        self.modified_by = get_current_user() or self.get_default_user()
        super(AuditTimestampModel, self).save(*args, **kargs)

        if self.AUDITABLE.get("clear_after_save", False):
            self._set_initial_fields()


class ListDatedModelQuerySet(models.QuerySet):

    def currents_at(self, start):
        return self.currents_between(start, start)

    def currents_between(self, start=None, end=None):
        # end_p = end if end else start
        if not (start and end):
            start = end = datetime.now().date()

        if end and start > end:
            raise Exception(
                f"Data de início ({start}) maior que data de fim ({end}) não é permitido!"
            )

        if start:
            q_currents = ~Q(end_validity=None) & Q(end_validity__lt=start)
        if end:
            q_currents = (
                (q_currents | Q(start_validity__gt=end))
                if q_currents
                else Q(start_validity__gt=end)
            )
        return self.exclude(q_currents)

    def filter_overlap(self, fields, obj):
        if not fields:
            return self.filter()

        lookup = {}
        for field in fields:
            value = getattr(obj, field)
            if value is None:
                lookup[f"{field}__isnull"] = True
            else:
                lookup[field] = value
        return self.filter(**lookup)

    def currents_in(self, *args, **kwargs):
        range_ = kwargs.get("range", None)
        data = kwargs.get("data", datetime.now() if len(args) == 0 else args[0])
        if range_:
            return self.exclude(
                Q(start_validity__gt=range_.last)
                | (~Q(end_validity=None) & Q(end_validity__lt=range_.first))
            )
        else:
            return self.exclude(
                Q(start_validity__gt=data)
                | (~Q(end_validity=None) & Q(end_validity__lt=data))
            )


class ListDatedModel(models.Model):

    # NO_OVERLAP = True
    OVERLAP_FIELDS = []
    AUTO_CLOSE_PERIOD_OVERLAP = False
    AUTO_CREATE_WHEN_INTERNAL = False
    ONLY_CONTINUOUS_PERIOD = False

    start_validity = models.DateField(verbose_name="Início vigência")
    end_validity = models.DateField(verbose_name="Fim vigência", null=True, blank=True)
    deleted = models.BooleanField(default=False)

    objects = ListDatedModelQuerySet.as_manager()

    class Meta:
        abstract = True

    def filter_with_overlap_fields(self):
        if not self.OVERLAP_FIELDS:
            return self._meta.model.objects.exclude(pk=self.pk)

        lookup = {}
        for field in self.OVERLAP_FIELDS:
            value = getattr(self, field)
            if value is None:
                lookup[f"{field}__isnull"] = True
            else:
                lookup[field] = value
        return self._meta.model.objects.filter(**lookup).exclude(pk=self.pk)

    def filter_conflicts(self):
        return self.filter_with_overlap_fields().currents_between(
            self.start_validity, self.end_validity
        )

    @property
    def next(self):
        return (
            self.filter_with_overlap_fields()
            .exclude(pk=self.pk)
            .filter(start_validity__gt=self.start_validity)
            .order_by("start_validity")
            .first()
        )

    @property
    def previous(self):
        return (
            self.filter_with_overlap_fields()
            .exclude(pk=self.pk)
            .filter(start_validity__lt=self.start_validity)
            .order_by("start_validity")
            .last()
        )

    def save(self, *args, **kwargs):
        identical = (
            self.filter_conflicts().filter(start_validity=self.start_validity).first()
        )
        if identical:
            raise Exception("Período com mesmo início ja existe (%s)!" % identical)
        if self.next:
            if self.end_validity is None:
                if self.AUTO_CLOSE_PERIOD_OVERLAP:
                    self.end_validity = self.next.start_validity - relativedelta(days=1)
                else:
                    raise Exception(
                        "Periodo sobrepondo outro período (%s) não pode ser salvo!"
                        % self.next
                    )
                if self.filter_conflicts().count() != 1:
                    raise Exception(
                        "Periodo sobrepondo outros períodos não pode ser salvo!"
                    )
        if self.previous:
            if self.previous.end_validity is None:
                if self.AUTO_CLOSE_PERIOD_OVERLAP:
                    update_previous = self.previous
                else:
                    raise Exception(
                        "Periodo sobrepondo outro período (%s) não pode ser salvo!"
                        % self.previous
                    )
            if not self.AUTO_CLOSE_PERIOD_OVERLAP and (
                self.previous.end_validity is not None
                and self.previous.end_validity >= self.start_validity
            ):
                raise Exception(
                    "Periodo sobrepondo outro período (%s) não pode ser salvo"
                    % self.previous
                )

        super(ListDatedModel, self).save(*args, **kwargs)

        if self.previous:
            if self.previous.end_validity is None or (
                self.AUTO_CLOSE_PERIOD_OVERLAP
                and self.previous.end_validity >= self.start_validity
            ):
                p = self.previous
                p.end_validity = self.start_validity - relativedelta(days=1)
                p.save()


class ChoiceManager(models.Manager):

    def get_by_natural_key(self, app_label, name, value):
        return self.get(app_label=app_label, name=name, value=value)

    def get_options(self, app_label, name):
        return self.filter(app_label=app_label, name=name, active=True).values(
            "cvalue", "label"
        )


class Choice(models.Model):
    app_label = models.CharField(
        max_length=60, db_index=True, verbose_name="Aplicativo"
    )
    name = models.CharField(
        max_length=60, db_index=True, verbose_name="Nome da constante"
    )
    label = models.CharField(max_length=120, verbose_name="Label")
    value = models.SmallIntegerField(verbose_name="Valor", blank=True)
    cvalue = models.CharField(
        max_length=5,
        db_index=True,
        verbose_name="Identificador",
        blank=True,
        default="",
    )
    cache_path = models.CharField(max_length=120, db_index=True, blank=True)
    description = models.CharField(max_length=400, blank=True, default="")
    order_weight = models.SmallIntegerField(
        verbose_name="Peso ordenação", default=0, blank=True
    )
    active = models.BooleanField(verbose_name="Ativo?", default=True)
    #  TODO Refatorar Choice e TransparencyChoice, avaliar possibilidade da classe Choice substituir a TransparencyChoice
    # group = models.PositiveSmallIntegerField(verbose_name='Grupos', null=True, blank=True, choices=Choice.get_choices_for('gfp', 'GROUP_TRANSPARENCY'))

    objects = ChoiceManager()

    class Meta:
        unique_together = (
            ("app_label", "name", "value"),
            ("app_label", "name", "cvalue"),
            ("app_label", "name", "label"),
        )
        ordering = (
            # 'cache_path', 'value'
            "app_label",
            "name",
            "-order_weight",
            "value",
        )

    def natural_key(self):
        return (self.app_label, self.name, self.value)

    def __str__(self):
        return self.label

    @classmethod
    def get_dict_choices_for(
        klass,
        app_label,
        name,
        empty=False,
        empty_label="Nenhum",
        query_dict=None,
        query_args=None,
        char_field=False,
    ):
        return dict(
            klass.get_choices_for(
                app_label, name, empty, empty_label, query_dict, query_args, char_field
            )
        )

    @classmethod
    def get_choices_for(
        klass,
        app_label,
        name,
        empty=False,
        empty_label="Nenhum",
        query_dict=None,
        query_args=None,
        char_field=False,
    ):
        try:
            query = klass.objects.filter(app_label=app_label, name=name)

            if query_dict:
                query = query.filter(**query_dict)

            if query_args:
                query = query.filter(*query_args)

            if empty:
                yield (None, empty_label)

            for choice in query:
                yield (choice.value if not char_field else choice.cvalue, choice.label)
        except Exception as e:
            pass

    @property
    def next_value(self):
        query = self.__class__.objects.filter(app_label=self.app_label, name=self.name)
        return (
            query.order_by("pk")
            .aggregate(max_value=models.Max("value"))
            .get("max_value")
            or 0
        ) + 1

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.next_value
        if not self.cvalue:
            self.cvalue = str(self.value)

        self.cache_path = ".".join([self.app_label, self.name])
        self.app_label = self.app_label.lower()

        super(Choice, self).save(*args, **kwargs)


class CObject(AuditTimestampModel):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(null=True, blank=True, verbose_name="Descrição")

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome


class Item(models.Model):
    configuration = models.ForeignKey(
        "Configuration",
        verbose_name="Configuração",
        related_name="items",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    key = models.SlugField(verbose_name="Chave", max_length=40)
    type_of = models.PositiveIntegerField(
        verbose_name="Tipo",
        choices=Choice.get_choices_for("standard", "CONFIGURATION_ITEM_CHOICE"),
        default=CONFIGURATION_ITEM_CHOICE_TEXT,
        blank=True,
        null=True,
    )
    value = models.TextField(verbose_name="Valor", blank=True, null=True)

    class Meta:
        unique_together = (("configuration", "key"),)
        ordering = ("configuration", "key")

    def __str__(self):
        return "{app}.{key}: {value}".format(
            app=self.configuration, key=self.key, value=self.value
        )

    @property
    def get_name(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.name
        return None

    @property
    def get_max_value(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.max_value
        return None

    @property
    def get_min_value(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.min_value
        return None

    @property
    def get_paid(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.paid
        return None

    @property
    def get_gera_falta(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.gera_falta
        return None

    @property
    def get_payroll(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.payroll
        return None

    @property
    def get_vertical_progression(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.vertical_progression
        return None

    @property
    def get_premium_license(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.premium_license
        return None

    @property
    def get_type_by_possession(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.type_by_possession
        return None

    @property
    def get_all_tbp(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.all_tbp
        return None

    @property
    def get_mandatory_document(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.mandatory_document
        return None

    @property
    def get_exibir_folha_ponto(self):
        if hasattr(self, "justificationitem"):
            return self.justificationitem.exibir_folha_ponto
        return None


class JustificationItem(Item):
    name = models.CharField(verbose_name="Nome", max_length=120)
    max_value = models.IntegerField(
        verbose_name="Máximo em horas", blank=True, null=True
    )
    min_value = models.IntegerField(
        verbose_name="Mínimo em horas", blank=True, null=True
    )
    paid = models.IntegerField(
        default=3,
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        null=True,
        blank=True,
        verbose_name="Abonado?",
    )
    gera_falta = models.IntegerField(
        default=1,
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        verbose_name="Gera Falta",
    )
    payroll = models.BooleanField(
        verbose_name="Folha", default=False, blank=True, null=True
    )
    vertical_progression = models.BooleanField(
        verbose_name="Progressão Vertical", default=False, blank=True, null=True
    )
    premium_license = models.BooleanField(
        verbose_name="Licença Prêmio", default=False, blank=True, null=True
    )
    type_by_possession = models.TextField(
        verbose_name="Tipo de Servidor", blank=True, null=True
    )
    all_tbp = models.BooleanField(
        verbose_name="Todos Tipos de Servidor", default=False, blank=True, null=True
    )
    mandatory_document = models.IntegerField(
        default=2,
        choices=Choice.get_choices_for("rh", "SIM_NAO"),
        null=True,
        blank=True,
        verbose_name="Documento Obrigatório?",
    )
    exibir_folha_ponto = models.BooleanField(
        verbose_name="Exibir Folha ponto", default=True
    )

    class Meta:
        ordering = (
            "configuration",
            "key",
        )

    def __str__(self):
        return "{app}.{name}: {value}".format(
            app=self.configuration, name=self.name, value=self.value
        )

    def validate_all_tbp(self):
        choices = Choice.objects.filter(
            app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION"
        )
        text_tbp = ""
        if self.all_tbp:
            for choice in choices:
                if text_tbp == "":
                    text_tbp = choice.cvalue
                else:
                    text_tbp = f"{text_tbp},{choice.cvalue}"
            self.type_by_possession = text_tbp
        else:
            self.type_by_possession = self.type_by_possession.replace(" ", "")

    @classmethod
    def get_config_for(klass, config):
        try:
            value_list = klass.objects.filter(
                configuration__application=config
            ).values_list("value", "name")
            values = [(int(value[0]), value[1]) for value in value_list]
            return values
        except Exception as e:
            pass

    def save(self, *args, **kwags):
        self.validate_all_tbp()
        super(JustificationItem, self).save(*args, **kwags)


class ConfigPoint(models.Model):
    place = models.CharField(verbose_name="Local", max_length=150)
    prosecution = models.CharField(verbose_name="Promotoria", max_length=150)
    network = models.CharField(verbose_name="Rede", max_length=20)

    class Meta:
        ordering = ["place", "prosecution"]

    def __str__(self):
        return "{place}-{net}".format(place=self.place, net=self.network)

    def save(self, *args, **kwags):
        self.network = self.network.replace(" ", "")
        super(ConfigPoint, self).save(*args, **kwags)


class Configuration(models.Model):
    application = models.SlugField(verbose_name="Chave", max_length=60, unique=True)
    itens = models.ManyToManyField(Item, related_name="configs")

    class NotConfigured(Exception):
        pass

    @staticmethod
    def get_or_create(application):
        cfg, created = Configuration.objects.get_or_create(application=application)
        return cfg

    def get(self, key, default=None, type_of=3):
        item, created = self.items.get_or_create(
            key=key, defaults={"value": default, "type_of": type_of}
        )
        # TODO: FAZER CASTING DE ACORDO COM O type_of
        return item.value

    def set(self, key, value, type_of=3):
        k, created = self.items.update_or_create(
            key=key, defaults={"value": value, "type_of": type_of}
        )
        return k

    def __str__(self):
        return "%s" % self.application


class EmailTemplate(models.Model):
    code = models.CharField(verbose_name="Código", max_length=150, unique=True)
    subject = models.CharField(
        verbose_name="Assunto", max_length=150, null=True, blank=True
    )
    contents = models.TextField(verbose_name="Conteúdo", null=True, blank=True)
    description = models.TextField(verbose_name="Descrição", null=True, blank=True)

    def __str__(self):
        return f"{self.code} - {self.subject}"


class RunCodeManager:

    AUTO_REGISTRO = getattr(settings, "RUNCODE_AUTO_REGISTER", False)

    __classes = {}
    __loaded = False

    @classmethod
    def discovery_in(cls, apps, pkg=""):
        for app in apps:
            try:
                mod = (
                    importlib.import_module(".%s" % app, pkg)
                    if pkg
                    else importlib.import_module("%s" % app)
                )
                if hasattr(mod, "__all__"):
                    cls.discovery_in(
                        mod.__all__, app if not pkg else ("%s.%s" % (pkg, app))
                    )
            except ImportError:
                log.debug("IMPORT ERROR: %s" % app)
            except Exception as e:
                raise e

    @classmethod
    def discovery(cls):
        """
        Este metodo faz uma busca em todos os aplicativos instalados no ambiente em busca de modulos que tem o nome calcs.
        pode ser um modulo unico ou pode ser um pacote de modulos, neste caso é aconselhavel utilizar o __init__.py para indicar
        quais modulos serão carregados utilizando o __all__
        """
        log.debug(">>>>>>>> RunCodeManager DISCOVERY >>>>>>>>>>")
        if not cls.__loaded:
            cls.__loaded = True
            cls.discovery_in(settings.INSTALLED_APPS)

    @classmethod
    def persist(cls, uid, c):
        # from rh.gfp.models import Calculo
        created = False
        try:
            path = "%s.%s" % (c.__module__, c.__name__)
            ccode, created = ClassCode.objects.update_or_create(
                path=path,
                defaults={
                    "slug": uid,
                    "title": getattr(c, "title", getattr(c, "titulo", "SEM TÍTULO")),
                    "description": getattr(c, "descricao", "SEM DESCRIÇÃO"),
                    "name_object": c.__name__,
                    "typeof": c.typeof,
                },
            )
        except Exception as e:
            log.exception(e)
        return created

    @classmethod
    def register(cls, uid=""):
        def decorator(classcode):
            if classcode.__name__ not in list(cls.__classes.keys()):
                cls.__classes.update(
                    {"%s.%s" % (classcode.__module__, classcode.__name__): classcode}
                )
                classcode.UID = uid
                if cls.AUTO_REGISTRO:
                    created = cls.persist(uid, classcode)
                    log.info(
                        "ClassCode %s registred! >> %s <<"
                        % (uid, "CREATED" if created else "UPDATED")
                    )
            else:
                log.error("O classcode %s ja esta registrado." % classcode.title)
            return classcode

        return decorator

    @classmethod
    def factory(cls, path, *args, **kargs):
        try:
            c = RunCodeManager.get_classcode_from_path(path)(*args, **kargs)
        except Exception as e:
            log.info("Erro ao carregar calculo %s" % path)
            log.exception(e)
            return None
        else:
            return c

    @classmethod
    def get_from_path(cls, path):
        return cls.get_classcode_from_path(path)

    @classmethod
    def get_classcode_from_path(cls, path):
        return cls.__classes.get(path, None)

    @classmethod
    def get_choices(cls, typeof=None):
        obj = [("Command", "Comando")]
        for path in list(cls.__classes.keys()):
            ccode = cls.get_classcode_from_path(path)
            if ccode is not None and (typeof is None or ccode.typeof == typeof):
                obj.append(
                    (path, ccode.title if hasattr(ccode, "title") else ccode.titulo)
                )

        return tuple(obj)


class ClassCodeManager(models.Manager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class ClassCode(models.Model):

    class Meta:
        ordering = ("path",)

    objects = ClassCodeManager()
    slug = models.CharField(max_length=128, null=True, unique=True)
    path = models.CharField(max_length=128, null=True, unique=True)
    title = models.CharField(max_length=128, blank=True)
    description = models.CharField(max_length=128, null=True)
    name_object = models.CharField(max_length=128, choices=RunCodeManager.get_choices())
    typeof = models.CharField(
        max_length=20,
        choices=list(TYPEOFEXECUTION.items()),
        default="CALCULO",
        db_index=True,
        null=False,
    )

    def __str__(self):
        return self.path or ""

    @classmethod
    def clean(cls):
        for cc in cls.objects.all():
            if not cc.cls:
                cc.delete()

    @property
    def cls(self):
        if self.module and self.name_class:
            if hasattr(self.module, self.name_class):
                return getattr(self.module, self.name_class)
        return None

    @property
    def path_module(self):
        return ".".join(self.path.split(".")[0:-1]) if self.path else None

    @property
    def name_class(self):
        return self.path.split(".")[-1] if self.path else None

    @property
    def module(self):
        if self.path_module:
            try:
                return importlib.import_module(self.path_module)
            except ImportError as err:
                log.exception(err)
                return None
        return None

    def natural_key(self):
        return (self.slug,)


class Assinatura(AuditTimestampModel):
    """
    Modelo responsável por armazenar informações sobre Assinatura de um usuário.

    É um modelo abstrato, que deve ser herdado pelo modelo que deseja gravar as informações sobre assinatura.
    """

    assinado_por = models.ForeignKey(
        "rh.PessoaFisica",
        related_name="assinaturas_%(class)s",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    assinado_em = models.DateTimeField("Assinado em", null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

    @property
    def assinado_por_nome(self):
        return self.assinado_por.social_name if self.assinado_por else None

    def assinar(self, pessoa):
        self.assinado_por = pessoa
        self.assinado_em = datetime.now()
        self.save()


# METODOS UTILS - DEVERIA ESTAR EM UTILS
def get_hexdigest(algorithm, salt, raw_string):
    """
    Implementação extraída de django.contrib.auth
    Returns a string of the hexdigest of the given plaintext and salt
    using the given algorithm ('md5', 'sha1').
    """

    raw_string, salt = encoding.smart_str(raw_string), encoding.smart_str(salt)

    try:
        return hashlib.new(algorithm, salt + raw_string).hexdigest()
    except Exception:
        raise Exception(
            "Erro na geração do digest!"
        )  # ValueError("Erro na geração do digest!")


def get_hexdigest_from_file(algorithm, salt, full_path):
    """
    Este método solicita o hash do conteúdo do arquivo.
    """
    fin = open(full_path, "r")
    s = fin.read()
    fin.close()
    return get_hexdigest(algorithm, salt, s)


def dv_is_valid(numero):
    """
    Este método verifica se o número (ex:'35041.000387/2000-19') possui o dígito verificador correto.
    """
    numero = numero.split("-")
    if get_digito_verificador(numero[0]) == numero[1]:
        return True
    return False


def get_digito_verificador(numero):
    """
    Este método  realiza o gerênciamento das funções que geram os dígitos verificadores para o número (ex:'35041.000387/2000-19')
    de parâmetro.
    """
    primeiro_dv = get_primeiro_dv(numero)
    if primeiro_dv != -1:
        segundo_dv = get_segundo_dv(numero, primeiro_dv)
    else:
        return -1
    return str(primeiro_dv) + str(segundo_dv)


def get_primeiro_dv(numero):
    """
    Este método gera o primeiro dígito verificador para o número (ex:'35041.000387/2000') de parâmetro.
    """
    try:
        exp = re.compile(r"\.|/|-")
        numero = "%s" % (numero,)
        numero = exp.sub("", numero)
        numero_invertido = numero[::-1]
        peso = 2
        soma = 0
        modulo = 11
        if len(numero_invertido) == 15:
            for dig in numero_invertido:
                soma += peso * int(dig)
                peso += 1
        resto = soma % modulo
        dv = modulo - resto
        if dv == 11:
            return 1
        if dv == 10:
            return 1
        if dv == 0:
            return 1
        else:
            return dv
    except Exception as ecp:
        raise ecp
        return -1


def get_segundo_dv(numero, p_dv):
    """
    Este método gera o segundo dígito verificador para o número (ex:'35041.000387/2000-1') e o primeiro dígito verificador, p_dv
    informados por parâmetro.
    """
    try:
        exp = re.compile(r"\.|/|-")
        numero = "%s-%d" % (
            numero,
            p_dv,
        )
        numero = exp.sub("", numero)
        numero_invertido = numero[::-1]
        peso = 2
        soma = 0
        modulo = 11
        if len(numero_invertido) == 16:
            for dig in numero_invertido:
                soma += peso * int(dig)
                peso += 1
        resto = soma % modulo
        dv = modulo - resto
        if dv == 11:
            return 1
        if dv == 10:
            return 1
        if dv == 0:
            return 1
        else:
            return dv

    except Exception as ecp:
        raise ecp
        return -1


# numero = "35041.000387/2000"
# dv_is_valid(numero + '-' + get_digito_verificador(numero))
# ########################################################################

"""
    CHOICES SICAP TCE-TO
"""

"""
CHOICE UTILIZADO APENAS PARA SICAP-AP
"""
TIPO_MOVIMENTACAO = (
    (1, "NOMEAÇÃO/EFETIVO"),
    (3, "REVERSÃO"),
    (4, "REINTEGRAÇÃO"),
    (5, "READAPTÇÃO"),
    (7, "APROVEITAMENTO"),
    (8, "APOSENTADORIA"),
    (9, "PENSÃO"),
    (10, "NOMEAÇÃO/COMISSIONADO"),
    (11, "À DISPOSIÇÃO (REQUISITADO)"),
    (12, "CEDIDO P/ OUTRA ENTIDADE"),
    (13, "RECONDUÇÃO"),
    (16, "DESLIGAMENTO"),
    (17, "REVISÃO DE APOSENTADORIA"),
    (19, "REVISÃO DE PENSÃO"),
    (20, "LICENÇA"),  # ESTA OPÇÃO NÃO VEIO DO TIPOS DO SICAP PESSOAL
)

"""
CHOICE UTILIZADO NA PUBLICACAO
"""
TIPO_ATO_MOVIMENTACAO = (
    (1, "LEI"),
    (2, "DECRETO"),
    (3, "DECRETO LEGISLATIVO"),
    (4, "PORTARIA"),
    (5, "RESOLUÇÃO"),
    (6, "CIRCULAR"),
    (7, "DESPACHO"),
    (8, "PROCESSO"),
    (9, "REQUERIMENTO"),
    (10, "CONCESSÃO"),
    (11, "ATO"),
    (12, "APOSTILA"),
    (13, "OFÍCIO"),
    (14, "MEMORANDO"),
    (99, "OUTROS"),
    (98, "TERMO POSSE"),
    (97, "TERMO EXERCÍCIO"),
    (96, "TERMO LOTAÇÃO"),
)

"""
Sistema de PLANEJAMENTO
"""
TENDENCIA_CHOICES = (
    (0, "ALTA"),
    (1, "ESTÁVEL"),
    (2, "BAIXA"),
)

PROJETO_STATUS_CHOICES = (
    (0, "NÃO INICIADO"),
    (1, "ABERTO"),
    (2, "BLOQUEADO"),
    (3, "FECHADO"),
    (4, "FECHADO PELO CLIENTE"),
)

INDICADOR_TIPO_CHOICES = (
    (0, "PONTUAL"),
    (1, "CUMULATIVO"),
    (2, "AGUARDANDO DEFINIÇÃO"),
)

INDICADOR_PERIODO_CHOICES = (
    (0, "MENSAL"),
    (1, "BIMESTRAL"),
    (2, "TRIMESTRAL"),
    (3, "SEMESTRAL"),
    (4, "ANUAL"),
)

METODO_ANALISE_CHOICES = ((0, "MELHOR CASO"), (1, "PIOR CASO"))

auditlog.register(ConfigPoint)
auditlog.register(JustificationItem)
