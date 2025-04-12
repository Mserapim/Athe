# -.- coding: utf-8 -.-
from django.contrib.auth.models import User
from django.utils import encoding
from django.db import models
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from django.conf import settings
from django.db.models import Q, F

import hashlib
import decimal
import re
import importlib

log = getLogger(__name__)


TYPEOFEXECUTION = {
    "CALCULO": "Cálculos para FOPAG",
    "LOADER": "Carregadores de arquivos",
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
        decimal.Decimal: lambda x: round(float(x or 0), 10),
        int: lambda x: int(float(x or 0)),
        float: lambda x: round(x or 0, 10),
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

        diffs = {
            k: (norm(v), norm(d2[k]))
            for k, v in list(d1.items())
            if (k in self.audit_fields and norm(v) != norm(d2[k]))
        }

        return diffs

    @property
    def old_fields(self):
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
                if key not in exclude and float(getattr(self, key, None)) != float(
                    getattr(other, key, None)
                ):
                    return False
            except Exception:
                if key not in exclude and getattr(self, key, None) != getattr(
                    other, key, None
                ):
                    return False
        return True

    def _differences(self, other, exclude=[], only=[]):
        diffs = []
        only = only if only else self.audit_fields
        audit_fields = set(self.audit_fields).intersection(only) - set(exclude)
        for key in audit_fields:
            try:
                if float(getattr(self, key, None)) != float(getattr(other, key, None)):
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
        fields = self.AUDITABLE.get("fields", [f.name for f in self._meta.fields])
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


class ChoiceManager(models.Manager):

    def get_by_natural_key(self, app_label, name, value):
        return self.get(app_label=app_label, name=name, value=value)


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
        return item.value

    def set(self, key, value, type_of=3):
        k, created = self.items.update_or_create(
            key=key, defaults={"value": value, "type_of": type_of}
        )
        return k

    def __str__(self):
        return "%s" % self.application


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
        obj = []
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
            except ImportError:
                return None
        return None

    def natural_key(self):
        return (self.slug,)


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
        exp = re.compile("\.|/|-")
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
        exp = re.compile("\.|/|-")
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
