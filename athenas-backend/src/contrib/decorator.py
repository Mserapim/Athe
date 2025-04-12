# -*- coding: utf-8 -*-
import cProfile
from datetime import datetime
import decimal
import os
import pickle
import threading
from functools import lru_cache, wraps

from django.conf import settings
from django.db import models
from django.template.defaultfilters import addslashes
from pathlib import Path

from contrib.helpers import err, err2html, err2text
from contrib.pattern import Singleton
from contrib.utils import get_json_engine, getLogger

log = getLogger("decorator")


def ilru_cache(*cache_args, **cache_kwargs):
    def cache_decorator(func):
        @wraps(func)
        def cache_factory(self, *args, **kwargs):
            # log.debug('Creating ilru_cache for instance {%s} and method {%s}' % (self, func.__name__))
            instance_cache = lru_cache(*cache_args, **cache_kwargs)(func)
            instance_cache = instance_cache.__get__(self, self.__class__)
            setattr(self, func.__name__, instance_cache)
            return instance_cache(*args, **kwargs)

        return cache_factory

    return cache_decorator


def norm(value):
    cast = {
        decimal.Decimal: lambda x: float(x or 0),
        int: lambda x: int(float(x or 0)),
        models.BooleanField: lambda x: int(x or 0) == 1,
    }
    fn = cast.get(value.__class__, lambda x: x)
    return fn(value)


class profile:

    def __init__(self, filename, time=False):
        self.filename = filename
        self.time = time

    def __call__(self, method):
        def wrapper(*args, **kargs):
            retval = None
            if getattr(method, "profiled", False) is False:
                prof = cProfile.Profile()
                method.profiled = True
                retval = prof.runcall(method, *args, **kargs)
                method.profiled = False
                filename = self.filename
                if self.time:
                    p = Path(self.filename)
                    tms = datetime.timestamp(datetime.now())
                    p.parent.mkdir(exist_ok=True)
                    filename = f"{p.parent.absolute()}/{p.stem}.{tms}{p.suffix}"
                prof.dump_stats(filename)
            else:
                retval = method(*args, **kargs)
            return retval

        return wrapper


def validate(form_class, method="POST", response_type="default"):
    def decorator(_def):
        def new_def(*args, **kw):
            req = args[0].request
            form, message = None, None

            if req.method == method:
                form = form_class(req.POST)
                if not form.is_valid():
                    message = "Corrija o(s) seguinte(s) erros:"
                    content_type = dict(
                        json="text/javascript",
                        html="text/html",
                        text="text/plain",
                        default="text/javascript",
                    )
                    format_error = dict(json=err, html=err2html, text=err2text)
                    data = format_error.get(response_type.lower(), err)(message, form)
                    args[0].response["Content-Type"] = content_type[
                        response_type.lower()
                    ]
                    return args[0].render(data)
                else:
                    data = form.cleaned_data
                    for k, v in list(data.items()):
                        if isinstance(v, str):
                            data[k] = addslashes(v)
                    req.data = data
                    req.form = form
            return _def(*args, **kw)

        return new_def

    return decorator


def update_timeout_session(enable=True):
    def decorator(fc):
        fc.__update_timeout_session__ = enable
        return fc

    return decorator


class FilterException(Exception):
    pass


class FilterType:
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"


class FilterInformation:
    field_real = None
    field_virtal = None
    handle = None
    type = None

    def __init__(self, **kargs):
        if "field_real" in kargs:
            self.field_real = kargs["field_real"]
        else:
            raise FilterException("O nome do campo real não foi informado.")

        if "field_virtual" in kargs:
            self.field_virtual = kargs["field_virtual"]
        else:
            raise FilterException("O nome do campo virtual não existe.")

        if "type" in kargs:
            self.type = kargs["type"]
        else:
            self.type = FilterType.TEXT

        if "handle" in kargs:
            self.handle = kargs["handle"]
        else:
            self.handle = None


class LoginRequiredType:
    """ """

    JSON = "JSON"
    PLAIN = "TEXT"
    XML = "XML"
    HTML = "HTML"


def filter(confs):
    def decorator(_class_):
        for conf in confs:
            if not getattr(_class_, "filterInformation", False):
                _class_.filterInformation = []
            _class_.filterInformation.append(conf)
        return _class_

    return decorator


def install_view(menu, title, install=True):
    ptitle = title
    pmenu = menu
    pinstall = install

    def decorator(cls):
        class InstallMeta:
            controller = cls.__name__
            title = ptitle
            node_menu = pmenu
            install = pinstall

        cls.InstallMeta = InstallMeta

        return cls

    return decorator


def install_model(menu, title, create=None, install=None):
    def decorator(cls):
        class InstallModel:
            node_menu = menu
            title_view = title

        if create:
            InstallModel.create_view = True
        if install:
            InstallModel.install_view = True
        cls.InstallModel = InstallModel
        return cls

    return decorator


def login_required(type=None):
    """
    [DEPRECATED]
    Decorador para configurar metodos e funções para checagem de login
    """

    def decorator(function):
        function.have_login = True
        function.have_login_type = type
        return function

    return decorator


def is_public():
    def decorator(method):
        method._is_public = True
        return method

    return decorator


def tab(tabsconf):
    def decorator(cls):
        if "tabs_conf" not in dir(cls):
            cls.tabs_conf = []

        used = set()
        fields = []

        for field in cls.Form.Meta.model._meta.get_fields():
            if not field.auto_created or field.concrete:
                fields.append(field.name)

        fields = set(fields)
        # FIXME: Remover os campos que não são editaveis.
        for tabc in tabsconf:
            used = used.union(set(tabc["field"]))
            cls.tabs_conf.append(tabc)

        exclude = set([])
        if "exclude" in dir(cls.Form.Meta):
            if isinstance(cls.Form.Meta.exclude, tuple) or isinstance(
                cls.Form.Meta.exclude, list
            ):
                exclude = cls.Form.Meta.exclude
            else:
                exclude = [cls.Form.Meta.exclude]

        exclude = set(exclude)
        fields = fields - exclude
        rest = (fields - used) - set(["id"])

        if len(rest) > 0:
            cls.tabs_conf.append({"title": "Outros", "field": tuple(rest)})

        return cls

    return decorator


def to_search(fields):
    """
    Decorador de models, informa quais são os campos passiveis de busca, assim como o tipo adotado de busca

    fields = [
        {
            'name': 'pessoafisica__nome',
            'type': 'text|number|date|date_time|choices|boolean'
        }
    ]
    """

    def decorator(cls):
        ts = []

        for field in fields:
            ts.append(field)

        cls.to_search = ts
        return cls

    return decorator


def start_daemon(name="NoNameDef"):
    def decorator(thread):
        dm = DaemonManage.get_instance()

        if issubclass(thread, threading.Thread):
            try:
                t = thread(name=name, group=None)

                if dm.register(t):
                    t.setDaemon(True)
                    t.start()
                else:
                    del t

            except Exception as e:
                log.exception(e)
        else:
            log.info("Só posso usar o auto start com objetos do tipo thread.")

        dm.save()
        return thread

    return decorator


class DaemonManage(Singleton):

    def __init__(self, *args, **kargs):
        self.table = {}

        if (
            getattr(settings, "DAEMONMANAGE_TYPE", False)
            == getattr(settings, "DAEMONMANAGE_TYPE_PROCESS", True)
            and self.exist_dump()
        ):
            self.table = self.load()

    def clear(self):
        try:
            os.ulink(getattr(settings, "DAEMONMANAGE_DUMP_FILENAME", "/tmp/dump"))
        except Exception:
            pass

    def register(self, thread):
        lock = threading.Lock()
        lock.acquire()

        ppid = os.getppid()

        if ppid not in self.table:
            self.table[ppid] = {}

        if not thread.getName() in self.table[ppid]:
            self.table[ppid] = {thread.getName(): thread.ident}
            lock.release()
            return True
        else:
            lock.release()
            return False

    def exist_dump(self):
        return os.path.exists(
            getattr(settings, "DAEMONMANAGE_DUMP_FILENAME", "/tmp/dump")
        )

    def save(self):
        lock = threading.Lock()
        lock.acquire()

        try:
            fd = open(getattr(settings, "DAEMONMANAGE_DUMP_FILENAME", "/tmp/dump"), "w")
            pickle.dump(self.table, fd, pickle.HIGHEST_PROTOCOL)
            fd.close()
        except Exception:
            pass
        finally:
            lock.release()

    def load(self):
        lock = threading.Lock()
        lock.acquire()

        try:
            fd = open(getattr(settings, "DAEMONMANAGE_DUMP_FILENAME", "/tmp/dump"), "r")
            obj = pickle.load(fd)
            fd.close()

            return obj
        except Exception as e:
            log.exception(e)
            return None
        finally:
            lock.release()


def add_methods(methods):
    """
    Adiciona um método à classe decorada
    Params:
    @cls -> classe a ser decorada, passada automaticamente pelo python
    @funcs -> dicionario com os nome e funcoes a serem mapeadas na classe decorada
        Ex.: Decorando a classe A para adicionar dois métodos(notify e notify_all) mapeados respectivamente
             para os métodos notify e notify da classe Notification
                @add_methods({'notify':Notification.notify, 'notify_all': Notification.notify_all})
                class A:
                    pass
            Nesse
    """

    def decorator(cls):
        if not (methods and isinstance(methods, dict)):
            return cls
        for k in list(methods.keys()):
            setattr(cls, k, methods[k])
        return cls

    return decorator


def help_for():
    """ """
    json = get_json_engine()
    #    log.debug("Decorator [Help For]")

    @login_required(type="JSON")
    def get_help_info(self, args=[]):
        log.debug("GHI: %s" % self.__class__.__name__)
        tag = "default"
        obj = {"success": True, "total": len(self.get_help_items(tag)), "items": []}
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def get_help_item(self, args=[]):
        tag = "default"
        items = self.get_help_items(tag)
        idx = int(self.request.POST["index"]) if "index" in self.request.POST else 0
        obj = {
            "success": False,
        }
        if 0 < idx <= len(items):
            obj["success"] = True
            obj["item"] = items[idx - 1]
        self.response.write(json.encode(obj))

    def get_help_items(self, tag="default"):
        log.debug("GHII %s" % self.__class__.__name__)
        if self.items:
            return self.items[tag] if tag in self.items else self.items["default"]
        else:
            return []

    def decorator(cls):
        # log.debug("Decorando %s com help for" % cls.__class__.__name__)
        if not hasattr(cls, "get_help_info"):
            setattr(cls, "get_help_info", get_help_info)
        if not hasattr(cls, "get_help_items"):
            setattr(cls, "get_help_items", get_help_items)
        if not hasattr(cls, "get_help_item"):
            setattr(cls, "get_help_item", get_help_item)
        return cls

    return decorator


def cache_return(function):
    """
    Faz um cache do retorno de um método e caso seja chamado várias vezes numa mesma sessão
    retornará o valor cacheado e não precisara executar o método novamente
    O decorador vai criar uma variavel com o nome _cache_(nome_do_metodo) no objeto que contém o método
    """

    def decorator(obj):
        cache_name = "_cache_%s" % function.__name__
        if not hasattr(obj, cache_name):
            setattr(obj, cache_name, function(obj))
        return getattr(obj, cache_name)

    return decorator


def auditable(*args, **kargs):
    """
    Audita o model decorado, adicionando a possibilidade de verificar quais campos foram alterados após o objeto ter sido carregado.
    Os nomes dos campos a serem auditados podem ser passados como parametros, caso não passe nenhum nome, o TODOS os fields serão auditados
    Pode-se utilizar o parametro @exclude com uma lista de nomes de fields a serem excluidos da auditoria
    EX.:
    @auditable('campo1', 'campo2')
    """

    def equals(self, other):
        for key in self.audit_fields:
            try:
                if float(getattr(self, key, None)) != float(getattr(other, key, None)):
                    # log.debug("NOT EQUALS: %s - %s/%s" % (key, getattr(self, key, None), getattr(other, key, None)))
                    return False
            except Exception:
                if getattr(self, key, None) != getattr(other, key, None):
                    # log.debug("NOT EQUALS: %s - %s/%s" % (key, getattr(self, key, None), getattr(other, key, None)))
                    return False
        return True

    def differences(self, other):
        diffs = []
        for key in self.audit_fields:
            try:
                if float(getattr(self, key, None)) != float(getattr(other, key, None)):
                    # log.debug("NOT EQUALS: %s - %s/%s" % (key, getattr(self, key, None), getattr(other, key, None)))
                    diffs.append(key)
            except Exception:
                if getattr(self, key, None) != getattr(other, key, None):
                    # log.debug("NOT EQUALS: %s - %s/%s" % (key, getattr(self, key, None), getattr(other, key, None)))
                    diffs.append(key)
        return diffs

    # def __setattr__(self, name, value):
    #     new_value = float(value) if isinstance(value, decimal.Decimal) else value
    #     if name in self.audit_fields and hasattr(self, name):
    #         old_value = float(getattr(self, name)) if isinstance(getattr(self, name), decimal.Decimal) else getattr(self, name)
    #         if name not in self.old_fields:
    #             if new_value!= old_value: self.old_fields[name]= old_value
    #         elif name in self.old_fields:
    #             if new_value== self.old_fields[name]: self.old_fields.pop(name)
    #     object.__setattr__(self, name, new_value)
    @property
    def diff(self):
        d1 = self._initial_fields
        d2 = self.__dict__

        diffs = {
            k: (norm(v), norm(d2[k]))
            for k, v in list(d1.items())
            if norm(v) != norm(d2[k])
        }

        return diffs

    @property
    def is_dirty(self):
        return (self.old_fields and True) or False

    @property
    def changed(self):
        return (self.old_fields and True) or False

    def init_class(self, *args, **kargs):
        # setattr(self, 'old_fields', {})
        self._init(*args, **kargs)
        self._initial_fields = {
            k: self.__dict__[k] for k in self.__dict__ if k in self.audit_fields
        }

    def decorator(cls):
        cls.exclude = kargs.get("exclude", [])
        if not args:
            cls.audit_fields = [
                f.name for f in cls._meta.fields if f.name not in cls.exclude
            ]
        else:
            cls.audit_fields = [f for f in args if f not in cls.exclude]

        cls._init = cls.__init__
        cls.__init__ = init_class
        cls.old_fields = diff
        cls.diff = diff
        cls.is_dirty = is_dirty
        cls.changed = changed
        # cls.__setattr__ = __setattr__
        cls._equals = equals
        cls._differences = differences
        return cls

    return decorator


def deprecated(func):
    def decorator(obj, *args, **kwargs):
        from contrib.utils import getLogger, show_trace
        import traceback

        log = getLogger(__name__)

        log.warn(
            "--- BEGIN DEPRECATED METHOD %s.%s ---",
            obj.__class__.__name__,
            func.__name__,
        )
        show_trace(
            log.warn, traceback.extract_stack()[:-1], indent_size=1, indent_char=" "
        )
        log.warn(
            "--- END DEPRECATED METHOD %s.%s ---", obj.__class__.__name__, func.__name__
        )

        return func(obj, *args, **kwargs)

    return decorator


def mixin(base, overwrite=False, ignore=[], register=False):
    def _decorator_mixin(klass):
        for name, attr in list(base.__dict__.items()):
            if name not in ignore and (not getattr(klass, name, None) or overwrite):
                setattr(klass, name, attr)
        if register:
            base.register(klass)
        return klass

    return _decorator_mixin
