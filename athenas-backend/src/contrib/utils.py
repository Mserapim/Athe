# -*- coding: utf-8 -*-
""" Módulo que contém a definição de classes utilitárias.

    :Classes:
        :class:`Logging`,
        :class:`DateUtils`,
        :class:`DateRange`,
        :class:`EmptyDateRange`,
        :class:`MultipleDateRange`.
"""

# import fpconst
import re
import logging
import os
import zipfile
import socket
import codecs
import re
import ldap
import platform
import base64
import jwt

from functools import wraps
from django.db import transaction, connection, reset_queries
from django.db.models import Q, F
from django.contrib.auth.models import Permission
from logging.handlers import RotatingFileHandler
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.template.defaultfilters import slugify
from auth.base.models import PasswordChangeRequest
from fonema import phonetic
from itertools import islice, chain
from django.conf import settings
from django_filters import CharFilter, BaseInFilter, NumberFilter


def make_phonetic(value, sep=" "):
    by_pass = re.compile("^[0-9]")
    return sep.join(
        [(phonetic(p) if not by_pass.match(p) else p) for p in value.split(sep)]
    )


class LdapUser(object):

    def __init__(self, **kwargs):

        cfg = kwargs or getattr(settings, "LDAP_AUTH", {})

        self.__uri = cfg.get("uri")
        self.__secure = cfg.get("tls", False) or "ldaps://" in self.__uri
        self.__user_object = cfg.get("user_object")
        self.__basedn = cfg.get("basedn")
        self.__dn = cfg.get("dn")
        self.__adm = cfg.get("admin", {})

        self.__log = getLogger(__name__)

        # self.__ldap = self.__initialize(self.__cfg)

    def __initialize(self):

        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        ldap_con = ldap.initialize(self.__uri)

        self.__log.info("Initializing ldap connection")

        if self.__secure:
            ldap_con.set_option(ldap.OPT_REFERRALS, 0)
            # ldap_con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            ldap_con.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
            ldap_con.set_option(ldap.OPT_X_TLS_DEMAND, True)
            self.__log.info("Safe ldap connection")

        ldap_con.set_option(ldap.OPT_TIMEOUT, 30)

        return ldap_con

    def __bind(self):
        dn = "%s,%s" % (self.__adm.get("user", ""), self.__dn)
        pwd = self.__adm.get("passwd", "").encode("u8")
        con = self.__initialize()
        self.__log.info("Binding adm...")
        con.bind_s(dn, pwd)
        self.__log.info("Adm credentials binded")
        return con

    def __password_change_params(self, user, new_passwd):
        userdn = "%s=%s,%s" % (self.__user_object, user, self.__basedn)

        modify_passwd_op = []
        if ldap.get_option(ldap.OPT_PROTOCOL_VERSION) > 2:
            password_value = '"%s"' % new_passwd
            modify_passwd_op = [
                (ldap.MOD_REPLACE, "unicodePwd", [password_value.encode("utf-16-le")])
            ]
        else:
            password_value = str(new_passwd)
            modify_passwd_op = [
                (ldap.MOD_REPLACE, "userPassword", [password_value]),
                # (ldap.MOD_REPLACE, 'sambaLMPassword', [password_value]),
                # (ldap.MOD_REPLACE, 'sambaNTPassword', [password_value])
            ]

        return userdn, modify_passwd_op

    def __do_change_password(self, username, new_password):

        try:
            username = username.lower().replace(" ", "")

            if not new_password or len(new_password) < 6:
                raise Exception(
                    "A nova senha deve ter pelo menos 6 caracteres alfanuméricos"
                )
            if new_password == "123mudar":
                raise Exception("A nova senha deve ser diferente da senha padrão")

            if ldap.get_option(ldap.OPT_PROTOCOL_VERSION) > 2:
                new_password = new_password.encode("u8")

            con = self.__bind()
            userdn, passwd_chage_op = self.__password_change_params(
                username, new_password
            )

            con.modify_s(userdn, passwd_chage_op)
        except Exception as e:
            self.__log.exception(e)
            raise e

    def check_user(self, user, pwd=None):
        dn = "%s=%s,%s" % (self.__user_object, user, self.__basedn)
        con = self.__initialize()
        self.__log.info("Cheking user...")
        con.bind_s(dn, pwd.encode("u8"))
        self.__log.info("User checked.")

    def get_password_change_request(self, username, token):
        return PasswordChangeRequest.objects.filter(
            user__username=username, key=token, valid=True
        ).last()

    def change_password(self, username, current_password, new_password):

        try:
            if not isinstance(username, str) and not isinstance(current_password, str):
                raise Exception(
                    "Credenciais inválidas. Insira corretamente o usuário e senha atuais."
                )
            try:
                self.check_user(username, current_password)
            except Exception as e:
                self.__log.exception(e)
                raise Exception("Usuário ou senha atuais inválidos.")

        except Exception as e:
            self.__log.exception(e)
            raise e
        else:
            self.__do_change_password(username, new_password)

    def reset_password(self, username, authorization_token, new_password):
        try:
            change_req = self.get_password_change_request(username, authorization_token)

            if not change_req:
                raise Exception(
                    "É necessário um código de solicitação de recuperação de senha válido."
                )

        except Exception as e:
            self.__log.exception(e)
            raise e

        else:
            try:
                self.__do_change_password(username, new_password)

                with transaction.atomic():
                    change_req.valid = False
                    change_req.save()

            except Exception as ee:
                self.__log.exception(ee)
                raise ee


class Logging(object):
    """
    **Classe** para fornecer utilidades de log.
    """

    _instance = None

    class Singleton:
        """
        **Classe** para fornecer utilidades de log.

        :Métodos:
            :func:`get_logging`.
        """

        def __init__(self):
            self._logging = {}

        def get_logging(self, name="Generic"):
            """
            :param name: Nome
            :type name: String

            :returns: Logger
            """
            if name not in self._logging:
                self._logging[name] = logging.getLogger(name)

                handler = RotatingFileHandler(
                    filename=settings.LOG_FILENAME,
                    maxBytes=settings.LOG_MAX_SIZE,
                    backupCount=9,
                    mode="a",
                )

                fmt = logging.Formatter(
                    settings.LOG_FORMAT_MESSAGE, settings.LOG_FORMAT_DATE
                )

                handler.setFormatter(fmt)
                self._logging[name].setLevel(settings.LOG_LEVELS[settings.LOG_LEVEL])
                self._logging[name].addHandler(handler)

            return self._logging[name]

    def __init__(self):
        if Logging._instance is None:
            Logging._instance = Logging.Singleton()
        self.__dict__["_EventHandler_instance"] = Logging._instance

    def __getattr__(self, aAttr):
        return getattr(self._instance, aAttr)

    def __setattr__(self, aAttr, aValue):
        return setattr(self._instance, aAttr, aValue)


class Extra:

    __keys = (
        "hostname",
        "user",
        "remote_addr",
        "req_path",
        "req_method",
        "req_client_by_site",
        "stream_name",
    )

    @property
    def req(self):
        from contrib.middleware import current_request

        return current_request()

    def __iter__(self):
        for k in self.__keys:
            yield k

    def _hostname_value(self):
        return platform.node()

    def _stream_name_value(self):
        return "athenas.%s" % getattr(settings, "LOG_STREAM_NAME", "stream")

    def _real_remote_addr_value(self):
        return self.req.META.get("HTTP_X_REAL_IP", self.req.META.get("REMOTE_ADDR"))

    def _remote_addr_value(self):
        return self._real_remote_addr_value() if self.req else "127.0.0.1"

    def _req_path_value(self):
        return self.req.path if self.req else None

    def _req_client_by_site_value(self):
        return self.req.META.get("HTTP_X_SITE_CLIENT_IP", None) if self.req else None

    def _req_method_value(self):
        return self.req.method if self.req else "not-request"

    def _user_value(self):
        from contrib.middleware import get_current_user

        user = get_current_user()

        return user.username if user else "anonymous"

    def __getitem__(self, key, default=None):
        return getattr(self, "_%s_value" % key, lambda: default)()


class CustomAdapter(logging.LoggerAdapter):

    def warn(self, *args, **kwargs):
        self.warning(*args, **kwargs)


def getLogger(name="base-athenas"):
    logconf = getattr(settings, "LOGGING", {})
    loggers = logconf.get("loggers", {})

    name_parts = name.split(".")
    flag = False

    while name_parts and not flag:
        flag = ".".join(name_parts) in loggers
        name_parts = name_parts if flag else name_parts[:-1]

    logname = ".".join(name_parts) if name_parts else "base-athenas"

    logger = logging.getLogger(logname)

    return CustomAdapter(logger, Extra())
    # return logger


def _get_json_engine_from_json(_json):
    class JSonEngine:
        @classmethod
        def encode(self, obj):
            return _json.dumps(obj)

        @classmethod
        def decode(self, S):
            return _json.loads(S)

    return JSonEngine


def _get_json_engine_from_cjson(_json):
    class CJSonEngine:
        @classmethod
        def encode(self, obj):
            return _json.encode(obj)

        @classmethod
        def decode(self, S):
            return _json.decode(S)

    return CJSonEngine


def _get_json_engine_from_simplejson(_json):

    __jencoder__ = _json.JSONEncoder()
    __jdecoder__ = _json.JSONDecoder()

    class SimpleJSonEngine:
        @classmethod
        def encode(self, obj):
            return __jencoder__.encode(obj)

        @classmethod
        def decode(self, S):
            return __jdecoder__.decode(S)

    return SimpleJSonEngine


def get_json_engine():
    try:
        import json as _json

        return _get_json_engine_from_json(_json)
    except ImportError:
        try:
            import cjson as _json

            return _get_json_engine_from_cjson(_json)
        except ImportError:
            try:
                import simplejson as _json

                return _get_json_engine_from_simplejson(_json)
            except ImportError:
                raise Exception(
                    "Instale pelo menos um dos seguintes pacotes: python-cjson ou python python-simplejson"
                )


def dict2qs(pars):
    return "&".join(["%s=%s" % (k, v) for k, v in list(pars.items())])


class DateUtils:
    """
    **Classe** para fornecer utilidades padronizadas para Datas.

    :Métodos:
        :func:`time_to_str`,
        :func:`str_to_time`,
        :func:`datetime_to_str`,
        :func:`str_to_datetime`,
        :func:`date_to_str`,
        :func:`str_to_date`,
        :func:`default_time_format`,
        :func:`default_datetime_format`,
        :func:`default_date_format`,
        :func:`time_formats`,
        :func:`datetime_formats`,
        :func:`date_formats`,
        :func:`next_business_day`.
    """

    @staticmethod
    def time_to_str(value):
        """Converte um objeto que contém horário para string contendo apenas horário.

        :param value: Objeto que contém horário.
        :type value: Time ou Datetime

        :returns: String com horário.
        """
        format = DateUtils.default_time_format()
        return value.strftime(format)

    @staticmethod
    def str_to_time(value):
        """Converte uma string que contém apenas horário para objeto contendo horário.

        :param value: Horário no formato padrão.
        :type value: String

        :returns: Objeto que contém horário.
        """
        log = getLogger(__name__)

        for format in DateUtils.time_formats():
            try:
                dt = datetime.strptime(value, format)
            except Exception as e:
                log.exception(e)
            else:
                return dt
        raise Exception("Invalid time value.")

    @staticmethod
    def datetime_to_str(value):
        """Converte um objeto que contém data e horário para string.

        :param value: Data e Hora.
        :type value: Datetime

        :returns: String com data e horário.
        """
        format = DateUtils.default_datetime_format()
        return value.strftime(format)

    @staticmethod
    def str_to_datetime(value):
        """Converte uma string que contém data e horário para objeto datetime.

        :param value: Data e Horário no formato padrão.
        :type value: String

        :returns: Objeto que contém data e horário.
        """
        log = getLogger(__name__)

        for format in DateUtils.datetime_formats():
            try:
                dt = datetime.strptime(value, format)
            except Exception as e:
                log.exception(e)
            else:
                return dt
        raise Exception("Invalid datetime value.")

    @staticmethod
    def date_to_str(value, format_date=None):
        """Converte uma objeto que contém data para string contendo apenas data.

        :param value: Data.
        :param format_date: String ou None.
        :type value: Date ou Datetime

        :returns: String que contém data.
        """
        if not format_date:
            format_date = DateUtils.default_date_format()
        return value.strftime(format_date)

    @staticmethod
    def str_to_date(value, format=None):
        """Converte uma string que contém data para objeto contendo data.

        :param value: Data no formato padrão.
        :type value: String

        :returns: Objeto que contém data.
        """
        log = getLogger(__name__)
        formats = list(DateUtils.date_formats())
        if format:
            formats += [
                format,
            ]
        for format in formats:
            try:
                dt = datetime.strptime(value, format).date()
            except Exception as e:
                log.exception(e)
            else:
                return dt
        raise Exception("Formato da data é inválido.")

    @staticmethod
    def default_time_format(index=0):
        """Formato padrão de horário

        :param index: Índice da lista de formato padrão. (Opcional)
        :type index: Integer.

        :returns: O item de índice 'index' da lista de formato padrão.
        """
        return DateUtils.time_formats()[index]

    @staticmethod
    def default_datetime_format(index=0):
        """Formato padrão de data e horário

        :param index: Índice da lista de formato padrão. (Opcional)
        :type index: Integer.

        :returns: O item de índice 'index' da lista de formato padrão.
        """
        return DateUtils.datetime_formats()[index]

    @staticmethod
    def default_date_format(index=0):
        """Formato padrão de data

        :param index: Índice da lista de formato padrão. (Opcional)
        :type index: Integer.

        :returns: O item de índice 'index' da lista de formato padrão.
        """
        return DateUtils.date_formats()[index]

    @staticmethod
    def time_formats():
        """Formatos padrão de horário."""
        return getattr(settings, "TIME_INPUT_FORMATS", ["%H:%M"])

    @staticmethod
    def datetime_formats():
        """Formatos padrão de data e horário."""
        return getattr(settings, "DATETIME_INPUT_FORMATS", ["%d/%m/%Y %H:%M"])

    @staticmethod
    def date_formats():
        """Formatos padrão de data."""
        return getattr(settings, "DATE_INPUT_FORMATS", ["%d/%m/%Y"])

    @staticmethod
    def next_business_day(value):
        """Calcula o próximo dia útil.

        :param value: Data.
        :type value: Date ou Datetime

        :returns: Date ou Datetime do próximo dia útil.
        """

        bus = False
        days = 1
        while not bus:
            next = value + relativedelta(days=days)
            if not next.weekday() in (5, 6):
                bus = True
            days += 1
        return next

    @staticmethod
    def is_holiday(data):
        """Verifica se uma data é feriado nacional.

        :param data: Data a ser verificada.
        :type data: Date

        :returns: Boolean.
        """
        if not isinstance(data, date):
            raise Exception("Erro: Parâmetro deve ser do tipo Date")

        FERIADOS = {
            date(data.year, 1, 1): "Confraternização Universal",
            date(data.year, 3, 29): "Paixão de Cristo",
            date(data.year, 4, 21): "Tiradentes",
            date(data.year, 5, 1): "Dia Mundial do Trabalho",
            date(data.year, 9, 7): "Independência do Brasil",
            date(data.year, 10, 12): "Nossa Senhora Aparecida",
            date(data.year, 11, 2): "Finados",
            date(data.year, 11, 15): "Proclamação da República",
            date(data.year, 12, 25): "Natal",
        }

        return data in list(FERIADOS.keys())

    @staticmethod
    def ajusta_data_expediente(data, topo):
        """Ajusta uma data de acordo com o horário de expediente. Com arredondamento de uma data no horário de almoço para 12h ou 14h.

        :param data: Data a ser ajustada no horário de expediente.
        :type data: Datetime

        :param topo: True ajusta para 14h, False ajusta para 12h.
        :type topo: Boolean

        :returns: Data ajustada.
        """
        inicio_matutino = datetime(data.year, data.month, data.day, 9, 0, 0)
        fim_matutino = datetime(data.year, data.month, data.day, 12, 0, 0)
        inicio_vespertino = datetime(data.year, data.month, data.day, 14, 0, 0)
        fim_vespertino = datetime(data.year, data.month, data.day, 18, 0, 0)

        if data < inicio_matutino:
            return inicio_matutino
        if data > fim_matutino and data < inicio_vespertino:
            if topo is True:
                return inicio_vespertino
            else:
                return fim_matutino
        if data > fim_vespertino:
            return fim_vespertino

        return data

    @staticmethod
    def tempo_para_fim_expediente(data):
        """Calcula o tempo restante para o fim do expediente de um dia.

        :param data: Data e Hora.
        :type data: Datetime

        :returns: timedelta.
        """
        fim_expediente = datetime(data.year, data.month, data.day, 18, 0, 0)

        data = DateUtils.ajusta_data_expediente(data, True)

        if data.hour <= 12:
            # Turno Matutino
            return fim_expediente - relativedelta(hours=2) - data

        # Turno Vespertino
        return fim_expediente - data

    @staticmethod
    def tempo_de_expediente(data_inicial, data_final):
        """Calcula o tempo de expediente entre uma data inicial e uma data final.

        :param data_inicial: Data inicial.
        :type data_inicial: Datetime

        :param data_final: Data final.
        :type data_final: Datetime

        :returns: timedelta.
        """
        from contrib.daterange import NewDateRange

        if not isinstance(data_inicial, datetime) or not isinstance(
            data_final, datetime
        ):
            raise Exception("Os parâmetros devem ser datetime")
        if data_final < data_inicial:
            raise Exception("Erro: data final menor que data inicial")

        data_inicial = DateUtils.ajusta_data_expediente(data_inicial, True)
        data_final = DateUtils.ajusta_data_expediente(data_final, False)

        if data_inicial.date() == data_final.date():
            # Mesmo dia
            if data_inicial.weekday() in (5, 6) or DateUtils.is_holiday(
                data_inicial.date()
            ):
                # Final de semana ou feriado
                return timedelta()
            if data_inicial.hour <= 12 and data_final.hour >= 14:
                # Turnos diferentes
                return data_final - relativedelta(hours=2) - data_inicial
            else:
                # Mesmo turno
                return data_final - data_inicial

        # Dias diferentes
        date_range = NewDateRange(data_inicial, data_final)
        tempo_decorrido = timedelta()
        for dia in date_range.iter():
            if dia.weekday() in (5, 6):
                continue
            if DateUtils.is_holiday(dia):
                continue
            if dia == data_inicial.date():
                # Primeiro dia - conta até o fim do expediente
                tempo_decorrido = tempo_decorrido + DateUtils.tempo_para_fim_expediente(
                    data_inicial
                )
            elif dia == data_final.date():
                # Ultimo dia - conta tempo de expediente decorrido no dia
                tempo_decorrido = tempo_decorrido + (
                    timedelta(0, 8 * 3600)
                    - DateUtils.tempo_para_fim_expediente(data_final)
                )
            else:
                # Dias intermediarios - conta tempo total de expediente
                tempo_decorrido = tempo_decorrido + timedelta(0, 8 * 3600)

        return tempo_decorrido


class EmptyDateRange(object):
    """
    **Classe** para representar um intervalo vazio de datas.

    :Métodos:
        :func:`to_list`,
        :func:`in_range`,
        :func:`intersect`,
        :func:`union`.
    """

    start_date = None
    end_date = None

    def __init__(self):
        # self.log = getLogger(__name__)
        # self.log.info('INIT EmptyDateRange')

        self.start_date = None
        self.end_date = None

    def __str__(self):
        return "[ Empty (0 day) ]"

    def __eq__(self, other):
        return isinstance(other, EmptyDateRange)

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return (self > other) or (self == other)

    def __lt__(self, other):
        return not (self > other) and not (self == other)

    def __le__(self, other):
        return False

    def __add__(self, other):
        return self.union(other)

    def __sub__(self, other):
        return EmptyDateRange()

    @property
    def days(self):
        return 0

    @property
    def business_days(self):
        return 0

    @property
    def first(self):
        return None

    @property
    def last(self):
        return None

    def to_list(self):
        """:returns: Lista vazia de datas do DateRange."""
        return []

    def in_range(self, dt):
        """:returns: Booleano False."""
        return False

    def intersect(self, date_range):
        """Realiza interseção de outro DateRange com este DateRange vazio.

        :param date_range: DeteRange a realizar interseção.

        :returns: Instância de EmptyDateRange.
        """
        return EmptyDateRange()

    def union(self, other):
        """Realiza união de outro DateRange com este DateRange vazio.

        :param other: DateRange a realizar união.

        :returns: DateRange resultante da união.
        """
        from contrib.daterange import NewDateRange

        if isinstance(other, EmptyDateRange):
            return EmptyDateRange()
        return NewDateRange(other.start_date, other.end_date)

    def toordinals(self):
        return (0, 0)


def show_trace(out, stack, indent_size=0, indent_char="."):
    """
    stack = traceback.extract_stack()
    """
    indent = 0
    last_trace = stack[-1]

    for filename, lineno, module, unused in stack:
        complement = ""

        if last_trace[0] == filename and last_trace[1] == lineno:
            complement = " <-- (FIX THIS)"

        out(
            "%(step)03d | %(indent)s%(filename)s in line %(lineno)d %(complement)s"
            % {
                "indent": indent_char * (indent * indent_size),
                "filename": filename,
                "lineno": lineno,
                "step": indent,
                "complement": complement,
            }
        )

        indent += 1


def make_zipfile(output_filename, root_dir, include_root_dir=True):
    log = getLogger(__name__)

    if include_root_dir:
        relroot = os.path.abspath(os.path.join(root_dir, os.pardir))
    else:
        relroot = os.path.abspath(root_dir)

    log.debug("RELROOT: %s" % relroot)
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(root_dir):
            # add directory (needed for empty dirs)
            log.debug(
                "ROOT: %s ROOT_DIR: %s : %s"
                % (os.path.abspath(root), os.path.abspath(root_dir), include_root_dir)
            )
            if include_root_dir or os.path.abspath(root_dir) != os.path.abspath(root):
                zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                if os.path.isfile(filename):  # regular files only
                    arcname = os.path.join(os.path.relpath(root, relroot), file)
                    zip.write(filename, arcname)

    return os.path.abspath(output_filename)


class Locker(object):
    """
    Add two methods in class for the locks procedures
    1. create_lock
    2. remove_lock
    """

    @classmethod
    def start(cls):
        log = getLogger(__name__)
        if not os.path.exists(settings.LOCKS_DIR):
            os.makedirs(settings.LOCKS_DIR)
        start_file = os.path.join(
            settings.LOCKS_DIR, "%s.start" % slugify(socket.gethostname())
        )
        codecs.open(start_file, "w").write(datetime.today().strftime("%Y%m%d%H%M%S%f"))
        log.info("LOCK: CREATING START FILE %s" % start_file)
        return start_file

    @classmethod
    def starter_id(cls):
        if not os.path.exists(settings.LOCKS_DIR):
            return None
            # os.makedirs(settings.LOCKS_DIR)
        start_file = os.path.join(
            settings.LOCKS_DIR, "%s.start" % slugify(socket.gethostname())
        )
        return codecs.open(start_file, "r").read()

    @classmethod
    def get_host_from_id(cls, sid):
        locks_dir = getattr(settings, "LOCKS_DIR", None)
        for f in os.listdir(locks_dir):
            if (
                os.path.isfile(os.path.join(locks_dir, f))
                and f.endswith(".start")
                and codecs.open(os.path.join(locks_dir, f), "r").read() == sid
            ):
                return f.replace(".start", "")
        return None

    @classmethod
    def create_lock(cls, slug):
        log = getLogger(__name__)
        started_id = codecs.open(
            os.path.join(
                settings.LOCKS_DIR, "%s.start" % slugify(socket.gethostname())
            ),
            "r",
        ).read()
        lock_file_name = "%s.%s.alck" % (
            datetime.today().strftime("%Y%m%d%H%M%S%f"),
            slug,
        )
        codecs.open(os.path.join(settings.LOCKS_DIR, lock_file_name), "w").write(
            started_id
        )
        log.info("LOCK: CREATING LOCK FILE %s" % lock_file_name)
        return lock_file_name

    @classmethod
    def remove_lock(cls, lock_file_name):
        log = getLogger(__name__)
        file_path = os.path.join(settings.LOCKS_DIR, lock_file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            log.info("LOCK: REMOVING LOCK FILE %s" % lock_file_name)
        else:
            log.info("LOCK: LOCK FILE %s NOT EXIST" % lock_file_name)

    @classmethod
    def started_ids(cls):
        locks_dir = getattr(settings, "LOCKS_DIR", None)
        locks = {}
        for f in os.listdir(locks_dir):
            if os.path.isfile(os.path.join(locks_dir, f)) and f.endswith(".start"):
                locks[codecs.open(os.path.join(locks_dir, f), "r").read()] = f.replace(
                    ".start", ""
                )
        return locks

    @classmethod
    def locks(cls):
        log = getLogger(__name__)
        locks_dir = getattr(settings, "LOCKS_DIR", None)
        locks = {}
        if locks_dir:
            if os.path.exists(locks_dir):
                started_ids = cls.started_ids()
                locks_files = [
                    f
                    for f in os.listdir(locks_dir)
                    if os.path.isfile(os.path.join(locks_dir, f))
                    and f.endswith(".alck")
                ]
                for d in locks_files:
                    res = re.match(r"([0-9]*).([0-9a-zA-Z_]*).alck", d)
                    if res and res.groups():
                        start_dtime = datetime.strptime(
                            res.groups()[0], "%Y%m%d%H%M%S%f"
                        )
                        rd = relativedelta(datetime.today(), start_dtime)
                        lock_id = codecs.open(os.path.join(locks_dir, d), "r").read()
                        sid = started_ids.get(lock_id) or "__zombies__"
                        if sid not in locks:
                            locks[sid] = []
                        locks[sid].append(
                            {
                                "file": d,
                                "zombie": lock_id not in list(started_ids.keys()),
                                "duration": rd,
                                "duration_str": "%dd %02dh %02dm %02ds"
                                % (rd.days, rd.hours, rd.minutes, rd.seconds),
                                "id": lock_id,
                                "slug": res.groups()[1],
                            }
                        )
                    else:
                        log.info("LOCK: ERROR in name format of LOCK FILE %s" % d)
        else:
            log.warn("LOCK: not informed LOCKS DIR in settings")

        return locks


def dump_dict(dictionary):
    log = getLogger("")

    for attr, value in list(dictionary.items()):
        log.debug("%30s : %s", attr, str(value))


def person_from_user(user, only_active=True):
    if not user:
        return None
    elif only_active:
        if hasattr(user, "servidor"):
            return user.servidor.pessoa_fisica if user.servidor.ativo else None
        elif hasattr(user, "person"):
            return (
                user.person.pessoafisica
                if hasattr(user.person, "pessoafisica")
                else None
            )
        return getattr(user, "web_person", None)
    else:
        return user.servidor.pessoa_fisica


def natural_person_from_user(user, only_active=True):
    """Returns natural_person from the user's employee"""
    natural_person = None
    if not user:
        return natural_person
    user_employee = getattr(user, "servidor", None)
    if user_employee:
        if only_active:
            if user_employee.ativo:
                natural_person = user_employee.pessoa_fisica
        else:
            natural_person = user_employee.pessoa_fisica
    return natural_person


def employee_from_user(user, only_active=True):
    employee = None
    if not user:
        return employee
    elif only_active:
        if getattr(user, "servidor", None) and user.servidor.ativo:
            employee = user.servidor
    else:
        employee = getattr(user, "servidor", None)
    return employee


def user_from_person(person, only_active_employee=False):
    """Returns an User object from a Pessoa object."""

    user = None

    if person.is_servidor():
        if only_active_employee:
            employee_set = person.pessoafisica.servidor_set.filter(ativo=True)
        else:
            employee_set = person.pessoafisica.servidor_set.order_by(
                "-ativo"
            )  # Prioriza ativo

        employee = employee_set.filter(user__isnull=False).first()
        user = employee.user if employee else user

    return user


def caller_name(skip=1):
    """Get a name of a caller in the format module.class.method

    `skip` specifies how many levels of stack to skip while getting caller
    name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

    An empty string is returned if skipped levels exceed stack height
    """
    # stack = inspect.stack()
    # start = 0 + skip
    # if len(stack) < start + 1:
    #   return ''
    # parentframe = stack[start][0]
    #
    # name = []
    # module = inspect.getmodule(parentframe)
    # # `modname` can be None when frame is executed directly in console
    # # TODO(techtonik): consider using __main__
    # if module:
    #     name.append(module.__name__)
    # # detect classname
    # if 'self' in parentframe.f_locals:
    #     # I don't know any way to detect call from the object method
    #     # XXX: there seems to be no way to detect static method call - it will
    #     #      be just a function call
    #     name.append(parentframe.f_locals['self'].__class__.__name__)
    # codename = parentframe.f_code.co_name
    # if codename != '<module>':  # top level usually
    #     name.append( codename ) # function or a method
    #
    # ## Avoid circular refs and frame leaks
    # #  https://docs.python.org/2.7/library/inspect.html#the-interpreter-stack
    # del parentframe, stack
    #
    # return ".".join(name)
    return "deprecated"


def has_direct_perm(user, code_perm):
    if user.is_superuser:
        app_label, codename = code_perm.split(".")

        qs = Permission.objects.filter(Q(user=user) | Q(group__user=user))
        return qs.filter(content_type__app_label=app_label, codename=codename).exists()

    return user.has_perm(code_perm)


def int_to_roman(num):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def can_cast_to_int(value):
    """Checks whether the value can be converted to int"""
    if not isinstance(value, (str, bytes, int, float)):
        return False

    try:
        int(value)
        return True
    except ValueError:
        return False


##########################
# Database optimizations #
##########################


def dbreset():
    """Reset stats from performed database queries"""
    reset_queries()


def dbqueries():
    """Returns stats from performed queries on database"""
    return connection.queries


def dblen():
    """Returns the amount of performed queries from the last clean state of the queries"""
    return len(connection.queries)


def dbtime():
    """Returns the overall time (in ms) from the last clean state of the queries"""
    return sum([float(query["time"]) for query in connection.queries])


def dbstats(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        log = getLogger(func.__name__)
        reset_queries()
        response = func(*args, **kwargs)
        log.info(f"As queries executadas foram: {dbqueries()}")
        log.info(f"Custou {dblen()} queries que levaram {dbtime()} milisegundos")
        return response

    return func_wrapper


def comparar_querys(q_01, q_02, ignorar_campos=[]):
    if q_01.exists() is False or q_02.exists() is False:
        return False

    pk_q_01 = q_01[0]._meta.pk.name
    pk_q_02 = q_02[0]._meta.pk.name

    ignorar_campos_q_01 = set(ignorar_campos) | set([pk_q_01])
    ignorar_campos_q_02 = set(ignorar_campos) | set([pk_q_02])

    list_q_01 = [
        {k: v for k, v in d.items() if not k in ignorar_campos_q_01}
        for d in q_01.values()
    ]
    list_q_02 = [
        {k: v for k, v in d.items() if not k in ignorar_campos_q_02}
        for d in q_02.values()
    ]

    q_01_sorted = sorted(sorted(d.items()) for d in list_q_01)
    q_02_sorted = sorted(sorted(d.items()) for d in list_q_02)

    return q_01_sorted == q_02_sorted


def import_from_string(path_module):
    if path_module is None:
        return []
    parts = path_module.split(".")
    module_name = ".".join(parts[:-1])
    class_name = parts[-1]

    module = __import__(module_name, fromlist=[class_name])
    import_class = getattr(module, class_name)
    return [import_class]


def decode_base64(content):
    try:
        base64_data = base64.b64encode(content)
        return base64_data.decode("utf-8")
    except:
        return None


def criar_token_api(username, token_jwt=None, qtd_dias_exp=None):
    """
    Método responsável por criar um token a partir de um usuário para acessar as APIs (V2)
    """

    payload = {"username": username}

    if qtd_dias_exp:
        payload["exp"]: datetime.datetime.utcnow() + datetime.timedelta(
            days=qtd_dias_exp
        )

    if token_jwt is None:
        token_jwt = settings.JWT_SECRET_KEY

    token = jwt.encode(payload, token_jwt, algorithm="HS256")

    return token


class QuerySetChain(object):
    """
    Chains multiple subquerysets (possibly of different models) and behaves as
    one queryset.  Supports minimal methods needed for use with
    django.core.paginator.
    """

    def __init__(self, *subquerysets):
        self.querysets = subquerysets

    def count(self):
        """
        Performs a .count() for all subquerysets and returns the number of
        records as an integer.
        """
        return sum(qs.count() for qs in self.querysets)

    def _clone(self):
        "Returns a clone of this queryset chain"
        return self.__class__(*self.querysets)

    def _all(self):
        "Iterates records in all subquerysets"
        return chain(*self.querysets)

    def __getitem__(self, ndx):
        """
        Retrieves an item or slice from the chained set of results from all
        subquerysets.
        """
        if type(ndx) is slice:
            return list(islice(self._all(), ndx.start, ndx.stop, ndx.step or 1))
        else:
            return islice(self._all(), ndx, ndx + 1).next()


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def remover_caracteres_invalidos(texto):
    return "".join(char for char in texto if ord(char) >= 32 or char in "\t\n\r")


def filtrar_data(campo, antes, depois):
    filtro = {}
    if antes and depois:
        filtro.update({f"{campo}__range": [antes, depois]})
    elif antes:
        filtro.update({f"{campo}__lte": antes})
    elif depois:
        filtro.update({f"{campo}__gte": depois})
    return filtro


def get_label_value_de_queryset(queryset, label, value, sem_distinct=None):
    """
    Função que retorna uma lista de dicionários do tipo Queryset.

    :param queryset: Queryset para ser transformado
    :param str label: Campo para ser a label
    :param str value: Campo para ser o value
    :param bool or None no_distinct: Ignora o distinct padrão
    :rtype: list[dict]
    :return: [{label: "x", value: "y"}...]
    """

    queryset = (
        queryset.annotate(label=F(label), value=F(value))
        .values("label", "value")
        .order_by("label")
    )
    if sem_distinct:
        return queryset
    return queryset.distinct("label")


def get_object_or_none(model, **kwargs):
    """
    Função que tenta retornar um objeto do modelo; caso ele não exista, retorna None.

    :param class model: Classe do Model Django
    :param kwargs: Sequência contendo os campos do modelo
    """
    try:
        model_object = model.objects.get(**kwargs)
    except model.DoesNotExist:
        model_object = None
    return model_object


# Classes utilitárias da biblioteca django-filters
class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class CharInFilter(BaseInFilter, CharFilter):
    pass
