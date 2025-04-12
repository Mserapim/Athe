# -.- coding: utf8 -.-
from contrib.helpers import Resize
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes import models as contenttypes
from django.db import models
from django.db.models import signals
from django.template.defaultfilters import slugify
from django import template
from contrib.utils import getLogger, DateUtils, get_json_engine, Locker
from contrib import decorator
from django.conf import settings
from contrib.middleware import get_current_user
from dateutil.relativedelta import relativedelta
from ged.models import Arquivo as FileGED
from standard.models import AuditableMixins
from multiprocessing import Pool
from auditlog.registry import auditlog

import datetime
import random
import hashlib
import os
import re
import uuid

json = get_json_engine()

log = getLogger(__name__)


TASK_STATUS = {
    "RUNNING": "Executando",
    "STOPED": "Interrompida pelo usuário",
    "SUCCESS": "Finalizada com sucesso",
    "ERROR": "Erro na execução",
    "ABORTED": "Abortado",
}

TASK_MESSAGE_TYPE = {1: "INFO", 2: "WARN", 3: "ERROR", 4: "FILE"}

decorator.to_search(
    [
        {"name": "name", "type": "text"},
        {"name": "codename", "type": "text"},
        {"name": "content_type__app_label", "type": "text"},
        {"name": "content_type__name", "type": "text"},
    ]
)(Permission)


# class Choice(models.Model):
#     class Meta:
#         unique_together = (('name', 'module'), )

#     uuid = models.CharField(max_length=32, verbose_name='UUID', unique=True, db_index=True)
#     is_int = models.BooleanField(verbose_name='Is int?', default=False)
#     name = models.CharField(max_length=128, verbose_name='Name')
#     module = models.CharField(max_length=128, verbose_name='Module', null=True)
#     value = models.CharField(max_length=64, verbose_name='Value')
#     description = models.CharField(max_length=256, verbose_name='Description')


User._meta.permissions = (("can_manage_username", "Pode gerenciar nome de usuários"),)


class Evento(models.Model):
    title = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    resource = models.CharField(max_length=200)
    interface = models.CharField(max_length=200)

    def __str__(self):
        return "%s de %s até %s" % (
            self.title,
            DateUtils.datetime_to_str(self.start_date),
            (
                DateUtils.datetime_to_str(self.end_date)
                if self.end_date is not None
                else "indefinido"
            ),
        )


class ApplicationManager(models.Manager):
    """
    Gerenciador de aplicativos.
    """

    def get_by_natural_key(self, uuid, *args):
        return self.get(uuid=uuid)

    def get_queryset(self):
        return super(ApplicationManager, self).get_queryset().order_by("layer", "title")


@decorator.to_search(
    [
        {"name": "title", "type": "text"},
        {"name": "father__title", "type": "text"},
        {"name": "active", "type": "boolean", "true": "ativo", "false": "inativo"},
    ]
)
class Application(models.Model, AuditableMixins):
    class Meta:
        ordering = ["layer", "title"]
        unique_together = (("title", "father"),)

    AUDITABLE = {"fields": ["icon", "title", "active", "father", "uuid"]}

    icon = models.CharField(max_length=260, null=True, blank=True)
    title = models.CharField(max_length=50, verbose_name="Título")
    active = models.BooleanField(verbose_name="Ativo", default=True)
    father = models.ForeignKey(
        "Application",
        blank=True,
        null=True,
        verbose_name="Grupo de Funcionalidade",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    uuid = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="UUID",
        db_index=True,
        unique=True,
    )
    layer = models.PositiveSmallIntegerField(default=1, blank=True)
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="created_app",
        on_delete=models.CASCADE,
    )
    modified_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="modified_app",
        on_delete=models.CASCADE,
    )

    objects = ApplicationManager()

    def __str__(self):
        if self.father:
            return "%s -> %s" % (self.father, self.title)
        else:
            return self.title

    @property
    def is_active(self):
        return (
            self.active
            if self.father is None or self.active is False
            else self.father.is_active
        )

    def natural_key(self):
        return (self.uuid,)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = get_current_user() or self.get_default_user()
        self.modified_by = get_current_user() or self.get_default_user()
        if self == self.father:
            raise Exception("Um aplicativo não pode referenciar a si mesmo.")

        if self.father is None:
            self.title = self.title.upper()

        if not self.uuid:
            self.uuid = uuid.uuid4().hex

        self.layer = self._get_layer()

        super(Application, self).save(*args, **kwargs)

    def _get_layer(self):
        count = 1
        obj = self
        while obj.father:
            count += 1
            obj = obj.father
        return count


class ControllerManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, uuid, *args):
        return self.get(uuid=uuid)


@decorator.to_search(
    [
        {"name": "title", "type": "text"},
        {"name": "controller", "type": "text"},
        {"name": "application__title", "type": "text"},
    ]
)
class Controller(models.Model, AuditableMixins):
    class Meta:
        ordering = (
            "application",
            "controller",
        )

    AUDITABLE = {
        "fields": [
            "icon",
            "title",
            "active",
            "application",
            "uuid",
            "controller",
            "module",
        ]
    }

    icon = models.CharField(max_length=260, null=True, blank=True)
    title = models.CharField(max_length=50, verbose_name="Título")
    controller = models.CharField(max_length=50, verbose_name="Controlador")
    application = models.ForeignKey(
        Application, verbose_name="Grupo de Funcionalidade", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    active = models.BooleanField(default=True, verbose_name="Ativo")
    module = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        choices=[(app, app) for app in settings.INSTALLED_APPS],
        verbose_name="Modulo",
    )
    uuid = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name="UUID",
        db_index=True,
        unique=True,
    )
    icon_file = models.ForeignKey(
        FileGED, verbose_name="Ícone", null=True, blank=True, on_delete=models.CASCADE
    )
    position = models.IntegerField(
        "Ordem", default=9999, db_index=True, blank=True, null=True
    )
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="created_controller",
        on_delete=models.CASCADE,
    )
    modified_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="modified_controller",
        on_delete=models.CASCADE,
    )

    objects = ControllerManager()

    def __str__(self):
        return "%s -> %s" % (self.application, self.title)

    @property
    def is_active(self):
        return self.active and self.application.is_active

    def natural_key(self):
        return (self.uuid,)

    def icon_file_path(self):
        icon_file_path = ""
        if self.icon_file:
            path = self.icon_file.absolute_path
            mimetype = self.icon_file.mimetype

            if os.path.exists(path) and mimetype in ["image/jpeg", "image/png"]:
                resizer = Resize(path)
                resizer.do({"width": 104})
                icon_file_path = resizer.permalink()

        return icon_file_path

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_by = get_current_user() or self.get_default_user()
        self.modified_by = get_current_user() or self.get_default_user()
        if not self.uuid:
            self.uuid = uuid.uuid4().hex
        super(Controller, self).save(*args, **kwargs)


class ControllerContentTypeManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, controller_id, content_type_id, *args):
        return self.get(controller_id=controller_id, content_type_id=content_type_id)


class ControllerContentType(models.Model):
    controller = models.ForeignKey(
        Controller, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    content_type = models.ForeignKey(
        contenttypes.ContentType, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    priority = models.SmallIntegerField(
        choices=(
            (0, "Baixa"),
            (1, "Alta"),
        ),
        default=0,
    )

    class Meta:
        unique_together = ("controller", "content_type")

    def natural_key(self):
        return (self.controller_id, self.content_type_id)


def __post_save_controller_signal__(sender, **kargs):
    # TODO: verificar qual o problema, pois não executa a inserção quando este method estiver ativo
    p_controller = kargs["instance"]

    buf = """
{% for module in modules %}
from {{ module }} import *
{% endfor %}
ctr = {{ controller }}(None, None)
"""

    tpl = template.engines["django"].from_string(buf)
    buf = tpl.render(
        {
            "modules": settings.ROUTER["controllers"],
            "controller": p_controller.controller,
        }
    )

    try:
        ctr = None
        exec(buf)

        m = ctr.Form.Meta.model
        p_name = m.__name__.lower()
        p_app_label = m._meta.app_label

        query = contenttypes.ContentType.objects.filter(
            app_label=p_app_label, model=p_name
        )

        p_ctype = query[0]

        query = ControllerContentType.objects.filter(
            controller=p_controller, content_type=p_ctype
        )

        if len(query) == 0:
            ts = ControllerContentType(controller=p_controller, content_type=p_ctype)

            ts.save()
        else:
            log.debug("O Controller '{0}' já esta relacionado".format(p_controller))
    except Exception as exception:
        log.debug(buf)
        log.exception(exception)


# signals.post_save.connect(__post_save_controller_signal__, sender=Controller)


class LDAPServer(models.Model):
    WEIGHT_CHOICES = (
        (0, "Muito baixa"),
        (2, "Baixa"),
        (5, "Moderada"),
        (7, "Moderada a alta"),
        (9, "Alta"),
    )
    address = models.CharField(verbose_name="Endereço", max_length=15)
    port = models.PositiveIntegerField(verbose_name="Porta")
    dn = models.CharField(max_length=60)
    basedn = models.CharField(max_length=60)
    admin_user = models.CharField(max_length=60)
    admin_password = models.CharField(max_length=60)
    user_object = models.CharField(max_length=60)
    priority = models.PositiveIntegerField(
        choices=WEIGHT_CHOICES, verbose_name="Prioridade"
    )
    tls = models.BooleanField(verbose_name="Com TLS", default=False)
    falt = models.BooleanField(default=False, verbose_name="Em falta")

    def __str__(self):
        if self.tls:
            return "ldaps://{0}:{1}/".format(self.address, self.port)
        else:
            return "ldap://{0}:{1}/".format(self.address, self.port)


class LDAPServerFault(models.Model):
    server = models.ForeignKey(
        LDAPServer, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    moment = models.DateTimeField(auto_now=True)


class ControllerPermissionManager(models.Manager):
    """
    Gerenciador de funcionalidades.
    """

    def get_by_natural_key(self, name, *args):
        return self.get(name=name)


@decorator.to_search(
    [{"name": "name", "type": "text"}, {"name": "users__username", "type": "text"}]
)
class ControllerPermission(models.Model):
    name = models.CharField(max_length=60, verbose_name="Nome")
    users = models.ManyToManyField(User, blank=True, verbose_name="Usuários")
    controllers = models.ManyToManyField(
        Controller,
        blank=True,
        verbose_name="Funcionalidades",
        related_name="controller_permissions",
    )
    is_default = models.BooleanField(
        verbose_name="Permissões de funcionalidade padrão", default=False, blank=False
    )
    manager_permission = models.BooleanField(
        verbose_name="Grupo de funcionalidade gestor", default=False, blank=False
    )
    # groups = models.ManyToManyField(Group, blank= True, verbose_name= u'Grupos')
    objects = ControllerPermissionManager()

    class Meta:
        ordering = ("name",)

    def natural_key(self):
        return (self.name,)

    def __str__(self):
        return self.name

    def save(self, *args, **kargs):
        self.name = self.name.replace("_", "-")
        self.name = slugify(self.name)

        models.Model.save(self, *args, **kargs)


class GroupPermission(Group):
    is_default = models.BooleanField(
        verbose_name="Grupo de permissões padrão", default=False, blank=False
    )
    manager_permission = models.BooleanField(
        verbose_name="Grupo de permissões gestor", default=False, blank=False
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class NullTaskSession(object):
    """ """

    def __init__(self, *args, **kwargs):
        super(NullTaskSession, self).__init__(*args, **kwargs)
        self.__params = {}

    def __getitem__(self, key):
        return self.__params.get(key, None)

    def __setitem__(self, key, value):
        self.__params[key] = value

    def __contains__(self, key):
        return False

    @property
    def params(self):
        return self.__params

    def update(self, **kargs):
        pass

    def save(self, *args, **kargs):
        pass

    def message(self, msg, type_of=1, file_ged=None):
        pass

    def get(self, key):
        return self.__params.get(key, None)

    def set(self, key, value):
        self.__params[key] = value

    def send_message(self, msg, type_of=1):
        pass

    def add_file(self, afile, msg=""):
        pass

    @staticmethod
    def start_execution(msg=None):
        task = NullTaskSession()
        return task

    def finish_execution(self, status="SUCCESS", msg=""):
        pass

    @staticmethod
    def update_zombie_tasks():
        pass


class TaskSession(models.Model):
    """ """

    class Meta:
        ordering = ("started_task",)
        db_table = "eng_tasksession"

    sid = models.CharField(max_length=32, verbose_name="SID", db_index=True)
    description = models.CharField(max_length=255, verbose_name="Description")
    params_cache = models.CharField(
        max_length=400, verbose_name="Params", default="{}", null=False
    )
    user = models.ForeignKey(
        User, verbose_name="Users", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    started_task = models.DateTimeField(
        verbose_name="Started", auto_now_add=True, db_index=True
    )
    finished_task = models.DateTimeField(
        verbose_name="Finished", null=True, blank=True, db_index=True
    )
    visualized = models.BooleanField(
        verbose_name="Visualized", default=False, blank=True
    )
    status = models.CharField(
        max_length=16,
        verbose_name="Status",
        default="RUNNING",
        choices=list(TASK_STATUS.items()),
        db_index=True,
    )
    starter_id = models.CharField(max_length=20, verbose_name="Starter ID", null=True)

    def __getitem__(self, key):
        return self.params.get(str(key), None)

    def __setitem__(self, key, value):
        self.update(**{str(key): value})

    def __contains__(self, key):
        return key in self.params

    @property
    def params(self):
        if not hasattr(self, "_params"):
            self._params = json.decode(self.params_cache or "{}")
        return self._params

    def update(self, **kargs):
        self.params.update(**kargs)
        self.save()

    def save(self, *args, **kargs):
        new = self.pk is None
        if new:
            random.seed(os.urandom(10))
            magic = random.randint(0, 999999999)
            h = hashlib.new("md5")
            h.update(str(magic).encode())

            self.sid = h.hexdigest()
            self.params["sid"] = self.sid
            self.user = get_current_user()
            self.started_task = datetime.datetime.now()
            self.starter_id = Locker.starter_id()
        elif self.visualized and not self.finished_task:
            self.finish_execution(status="ERROR")

        if hasattr(self, "_params"):
            self.params_cache = json.encode(self._params)

        super(TaskSession, self).save(*args, **kargs)

        if new:
            self.send_message("Iniciando execução da tarefa")

    def info(self, msg, type_of=1, file_ged=None):
        self.message(msg, type_of=type_of, file_ged=file_ged)

    def message(self, msg, type_of=1, file_ged=None):
        log.debug("SEND MESSAGE: %s" % msg)
        self.messages.create(message=msg, type_of=type_of, file_ged=file_ged)

    def get(self, key):
        return self[key]

    def set(self, key, value):
        self[key] = value

    def send_message(self, msg, type_of=1):
        self.message(msg, type_of)

    def add_file(self, afile, msg=""):
        if not msg:
            msg = "Arquivo gerado: %s" % afile.filename
        self.message(msg, type_of=4, file_ged=afile)

    @staticmethod
    def start_execution(msg=None):
        task = TaskSession()
        task.description = msg or "Execução de tarefa"
        task.save()
        return task

    def finish_execution(self, status="SUCCESS", msg=""):
        self.finished_task = datetime.datetime.now()
        self.status = status
        uptime = relativedelta(self.finished_task, self.started_task)
        self.send_message(
            "%s - %dh %smin %ss"
            % (self.get_status_display(), uptime.hours, uptime.minutes, uptime.seconds)
        )
        if msg:
            self["pctText"] = msg

        self.save()

    @staticmethod
    def update_zombie_tasks():
        for task in TaskSession.objects.filter(finished_task=None).exclude(
            starter_id__in=list(Locker.started_ids().keys())
        ):
            task.info("Tarefa abortada no servidor!", 3)
            task.finish_execution("ERROR")


class TaskMessages(models.Model):
    """ """

    class Meta:
        ordering = ("id",)
        db_table = "eng_taskmessages"

    session = models.ForeignKey(
        TaskSession,
        verbose_name="Session",
        related_name="messages",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    message = models.CharField(
        max_length=400,
        verbose_name="Message",
    )
    type_of = models.PositiveSmallIntegerField(
        verbose_name="Type",
        default=1,
        choices=list(TASK_MESSAGE_TYPE.items()),
        db_index=True,
    )
    file_ged = models.ForeignKey(
        FileGED,
        verbose_name="Arquivo",
        related_name="tasks_messages",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)


decorator.to_search(
    [
        {"name": "username", "type": "text"},
        {"name": "servidor__matricula", "type": "text"},
        {"name": "servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "first_name", "type": "text"},
        {"name": "last_name", "type": "text"},
        {"name": "email", "type": "text"},
        {"name": "is_active", "type": "boolean", "true": "ativo", "false": "inativo"},
        {"name": "is_superuser", "type": "boolean", "true": "root", "false": None},
    ]
)(User)

decorator.to_search(
    [
        {"name": "name", "type": "text"},
    ]
)(Group)


# ----------- Signals ------------------------------------------------------------
def clear_cache(key, **kargs):
    key = "<>" if not key else key
    for entry in [
        name for name in os.listdir(settings.CACHE["dir"]) if re.match(key, name)
    ]:
        os.unlink(os.path.join(settings.CACHE["dir"], entry))


def clear_cache_by_users(pkset):
    for pk in pkset:
        clear_cache_by_user(pk)


def clear_cache_by_user(pk):
    menu_cache_dir = os.path.join(getattr(settings, "CACHE_PATH", ""), "menu", str(pk))

    log.debug("menu_cache_dir: %s", menu_cache_dir)
    if os.path.exists(menu_cache_dir):
        for filename in [
            e for e in os.listdir(menu_cache_dir) if re.match("^\d+\.json$", e)
        ]:
            log.debug("removendo %s", os.path.join(menu_cache_dir, filename))
            os.unlink(os.path.join(menu_cache_dir, filename))
    else:
        log.debug("sem cache de menu para o usuário com id %s", str(pk))


def clear_cache_by_applications(pkset):
    for pk in pkset:
        clear_cache_by_application(pk)


def clear_cache_by_application(pk):
    menu_cache_dir = os.path.join(getattr(settings, "CACHE_PATH", ""), "menu")

    log.debug("menu_cache_dir: %s", menu_cache_dir)
    if os.path.exists(menu_cache_dir):
        for dirname in os.listdir(menu_cache_dir):
            try:
                os.unlink(os.path.join(menu_cache_dir, dirname, "%s.json" % str(pk)))
            except:
                log.debug(
                    "not exists %s",
                    os.path.join(menu_cache_dir, dirname, "%s.json" % str(pk)),
                )
            else:
                log.debug(
                    "removed %s",
                    os.path.join(menu_cache_dir, dirname, "%s.json" % str(pk)),
                )
    else:
        log.debug("sem cache de menu para o usuário com id %d", pk)


def expire_menu_cache(
    sender, instance=None, action=None, model=None, pk_set=[], **kargs
):
    """
    Esse signal expira uma cache de menu quando algum evento que modifica as permissões
    do usuário é disparado
    """
    key = "<>"
    fn1 = lambda x: [str(user.id) for user in x.users.all()]
    fn2 = lambda x: [str(u) for u in x]
    fn3 = lambda x, q: [str(obj.pk) for obj in q]

    log.info("** BING ***")
    log.info([instance.__class__.__name__, model.__name__, action])

    try:
        if isinstance(instance, User):
            log.info("USER")

        if (
            instance.__class__.__name__ == "ControllerPermission"
            and action in ("pre_remove", "pre_clear", "post_add")
            and model is User
        ):
            ids = (
                fn1(instance) if action in ("pre_clear", "pre_remove") else fn2(pk_set)
            )
            log.info("Clear cache for user_ids %s", ids)
            clear_cache_by_users(ids)
        if (
            instance.__class__.__name__ == "ControllerPermission"
            and action in ("pre_remove", "pre_clear", "post_add")
            and model is Controller
        ):
            ids = fn3(pk_set, Application.objects.filter(controller__pk__in=pk_set))
            log.info("Clear cache for application ids %s", ids)
            clear_cache_by_applications(ids)
        elif (
            instance.__class__.__name__ == "Group"
            and action in ("post_remove", "pre_clear", "post_add")
            and model.__name__ == "Permission"
        ):
            ids = ["%s" % user.id for user in instance.user_set.all()]
            log.info("Clear cache for user_ids %s", ids)
            clear_cache_by_users(ids)
        elif (
            instance.__class__.__name__ == "User"
            and action in ("post_remove", "pre_clear", "post_add")
            and model.__name__ in ["Group", "Permission", "ControllerPermission"]
        ):
            log.info("Clear cache for user_id %s", instance.pk)
            clear_cache_by_user(instance.pk)
    except Exception as e:
        log.exception(e)


# signals.m2m_changed.connect(expire_menu_cache)
signals.m2m_changed.connect(
    expire_menu_cache, sender=ControllerPermission.users.through
)
signals.m2m_changed.connect(
    expire_menu_cache, sender=ControllerPermission.controllers.through
)
signals.m2m_changed.connect(expire_menu_cache, sender=User.groups.through)
signals.m2m_changed.connect(expire_menu_cache, sender=Group.permissions.through)

# --------------------- EXCEPTIONS ------------------------------------------------


class UserHasNotPermission(Exception):
    def __init__(self, perm):
        Exception.__init__(
            self,
            "Você não tem a permissão (%s) necessária para executar essa ação. Caso necessite, solicite ao Depto. de TI - Área de Programação"
            % perm,
        )


auditlog.register(Application)
auditlog.register(Controller)
auditlog.register(ControllerPermission)
auditlog.register(GroupPermission)
