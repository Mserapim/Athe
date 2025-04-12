# -*- coding: utf-8 -*-
# Django settings for src project.
import logging
import os
import re
import socket

from contrib.config import config as config, config_file_content

from dj_database_url import parse as db_url
from django.core.management.utils import get_random_secret_key

from contrib.logging import GELFFormatter

from app.decouple_castings import dj_mongo_url

from contrib import dynaset
from datetime import timedelta


ORGAN_IDENTIFIER = config("ORGAN_IDENTIFIER", default="mpmt")

AUTO_PERMISSIONS_GROUPS = config("AUTO_PERMISSIONS_GROUPS", default=True)
AUTO_PERMISSIONS_FUNCS = config("AUTO_PERMISSIONS_FUNCS", default=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT_DIR = os.path.abspath(os.path.sep.join([BASE_DIR, ".."]))
VAR_DIR = config("VAR_DIR", default=os.path.join(PARENT_DIR, "var"))

SYSTEM_INFO_FILE = os.path.join(BASE_DIR, "sysinfo.json")

DEBUG = config("DEBUG", default=True, cast=lambda v: bool(int(v)))
DEBUG_TOOLBAR = config("DEBUG_TOOLBAR", default=False, cast=lambda v: bool(int(v)))

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default=[
        "web",
        "daphne",
        "athenas",
        "127.0.0.1",
        "localhost",
    ],
)

SERVICE_TOKEN_ALLOWED = config("SERVICE_TOKEN_ALLOWED", default="")

NOSQL_DATABASES = {
    "default": config(
        "NOSQL_DATABASE_DEFAULT",
        default="mongodb://athenas:1234@mongo:27017/auth",
        cast=dj_mongo_url,
    )
}

MSSQL_DATABASE = {
    "sispat": {
        "database": config("MSSQL_DATABASE_SISPAT", default=""),
        "user": config("MSSQL_DATABASE_SISPAT_USER", default=""),
        "password": config("MSSQL_DATABASE_SISPAT_PASSWORD", default=""),
        "host": config("MSSQL_DATABASE_SISPAT_HOST", default=""),
    }
}

DATABASES = {
    "default": config(
        "DATABASE_DEFAULT",
        default="postgres://postgres:123@db/athenas01",
        cast=db_url,
        use_secret=True,
    )
}

ENABLE_ARQUIMEDES = config("ENABLE_ARQUIMEDES", default=False)
CONFIG_DIR_TNS = config(
    "CONFIG_DIR_TNS", default="/app/oracle/client/21c/network/admin/"
)

try:
    import sys

    # import oracledb

    # sys.modules["cx_Oracle"] = oracledb
    # oracledb.init_oracle_client(config_dir=CONFIG_DIR_TNS)
    # # DATABASES.update({
    #     'sisdias': {
    #         'ENGINE': 'django.db.backends.oracle',
    #         'NAME': config('DATABASE_ORACLE_NAME', default='os14mp.sede.mpe:1521/mpmt'),
    #         'USER': config('DATABASE_SISDIAS_USER', default='', use_secret=True),
    #         'PASSWORD': config('DATABASE_SISDIAS_PASSWORD', default='', use_secret=True),
    #     },
    # })
    # DATABASES.update({
    #     'mdc4web': {
    #         'ENGINE': 'django.db.backends.oracle',
    #         'NAME': config('DATABASE_ORACLE_NAME', default='os14mp.sede.mpe:1521/mpmt'),
    #         'USER': config('DATABASE_FOLHAPONTO_USER', default='', use_secret=True),
    #         'PASSWORD': config('DATABASE_FOLHAPONTO_PASSWORD', default='', use_secret=True)
    #     },
    # })

except Exception as err:
    print(err)
    print(
        """
        WARNING
        cx_Oracle não encontrado.
        Acesso banco de dados do Arquimedes não está configurado.
    """
    )
else:
    ARQUIMEDES_DB_SCHEMA = config("ARQUIMEDES_DB_SCHEMA", default=None)
    ARQUIMEDES_URI = config("ARQUIMEDES_URI", default=None)
    arquimedes = False
    try:
        arquimedes = config("DATABASE_ARQUIMEDES", cast=eval)
    except Exception as err:
        print(err)
    if arquimedes:
        DATABASES.update(arquimedes=arquimedes)

# DATABASE_ROUTERS = ('app.database.NodeRoute',)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = config("TIME_ZONE", default="America/Cuiaba")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "pt-BR"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(BASE_DIR, "web", "static")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ""

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = "/media/"

# Make this unique, and don't share it with anybody.
SECRET_KEY = config("SECRET_KEY", default=get_random_secret_key())

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        # 'DEBUG': DEBUG,
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "web", "static"),
            os.path.join(BASE_DIR, "static", "html"),
        ],
    },
]

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "contrib.middleware.BadPatternRequestMethodData",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "auth.ws.middleware.WSAuthenticatorBackend",
    "auth.sso.middleware.OAuthMiddleware",
    # "auth.sso.middleware.SSOMiddleware",
    "auth.jwt.middleware.Backend",
    "contrib.middleware.ThreadLocals",
    "contrib.middleware.StartupLoader",
    "contrib.middleware.AppDistributedInformation",
    # 'auditlog.middleware.AuditlogMiddleware',
    "middleware.custom_auditlog_middleware.CustomAuditlogMiddleware",
)

# Configurando o django para autenticar no backend LDAP.
AUTHENTICATION_BACKENDS = config(
    "AUTHENTICATION_BACKENDS",
    default=[
        "auth.ws.base.WSAuthBackend",
        "auth.dummy.Backend",
        "auth.sso.backend.SSOAuthBackend",
    ],
)

AUTH_DUMMY_PASSWORD = config("AUTH_DUMMY_PASSWORD", default="a1b2c3d4")

SSO_PUBLIC_KEY = config("SSO_PUBLIC_KEY", default="")

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="user@mailserver.com")
SERVER_EMAIL = config("SERVER_EMAIL", default="user@servermail.com")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.servermail.com")
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="user@servermail.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="secret")
EMAIL_PORT = config("EMAIL_PORT", default=587)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True)

# Contexto
HTTP_PROTOCOL = config("HTTP_PROTOCOL", default="http")
CONTEXT = "athenas"
DOMAIN = config("DOMAIN", default="127.0.0.1")
ATHENAS = "%s://%s/%s" % (HTTP_PROTOCOL, DOMAIN, CONTEXT)
DOMAIN_INTERNAL = config("DOMAIN_INTERNAL", default="web:8000")
ATHENAS_INTERNAL = "%s://%s/%s" % (HTTP_PROTOCOL, DOMAIN_INTERNAL, CONTEXT)

# Configuração do Gestor de Usuários
# Opções first_last, initials_last, first_dot_last
USERNAME_TYPE = config("USERNAME_TYPE", default="first_last")
MAIL_NAME_TYPE = config("MAIL_NAME_TYPE", default="first_last")
DEFAULT_USER_PASSWORD = config("DEFAULT_USER_PASSWORD", default="@Secr3t@")

CHANGE_PASSWORD_TYPE = config("CHANGE_PASSWORD_TYPE", default=None)

# Configuracao do LDAP
LDAP_AUTH = {
    "uri": config("LDAP_URI", default="ldap://10.2.1.200:389"),
    "tls": config("LDAP_TLS", default=True),
    "dn": config("LDAP_DN", default="dc=homologacao,dc=sede,dc=mpe"),
    "basedn": config(
        "LDAP_BASEDN", default="OU=MPMT-Users,OU=AD,DC=homologacao,DC=sede,DC=mpe"
    ),
    "admin": {
        "user": config(
            "LDAP_ADMIN_USER_DN", default="cn=admin,dc=default", use_secret=True
        ),
        "passwd": config("LDAP_ADMIN_PASSWD", default="secr3t", use_secret=True),
    },
    "user_object": config("LDAP_USER_OBJECT", default="cn"),
    "nologin": config("LDAP_NOLOGIN", default="."),
    "db_user_autocreate": config("LDAP_DB_USER_AUTOCREATE", default=False),
    "domain_mail": config("LDAP_DOMAIN_MAIL", default="mpmt.mp.br"),
    "binddn_use_domain": config("BINDDN_USE_DOMAIN", default=False),
}

JASPER_CONFIG = {
    "username": config("JASPER_SERVER_USERNAME", default="user", use_secret=True),
    "password": config("JASPER_SERVER_PASSWORD", default="secret", use_secret=True),
    "context": config("JASPER_SERVER_CONTEXT", default="jasperserver"),
    "host": config("JASPER_SERVER_HOST", default="jreport"),
    "port": config("JASPER_SERVER_PORT", default=8080),
    "legarcy": config(
        "JASPER_SERVER_REST_LEGARCY", default=False, cast=lambda v: bool(int(v))
    ),
}

REPORT_DEFAULT_PATH = config("REPORT_DEFAULT_PATH", default=None)

JAVA_HOME = config("JAVA_HOME", default=None)
JAVA_OPTIONS = config("JAVA_OPTIONS", default=None)
JASPER_BUILDER = config("JASPER_BUILDER", default=None)
JASPER_HOME = config("JASPER_BUILDER_HOME", default=None)
JASPER_TMP = config("JASPER_BUILDER_TMP", default=None)
JASPER_DATASOURCE = config("JASPER_BUILDER_DATASOURCE", default=None)

ITOP_URL = config("ITOP_URL", default=None)
ITOP_VERSION = config("ITOP_VERSION", default=None)
ITOP_USER = config("ITOP_USER", default=None)
ITOP_PWD = config("ITOP_PWD", default=None)
ITOP_ORIGEM = config("ITOP_ORIGEM", default=None)

# ROOT_URLCONF = 'urls.fcgi'
# if os.environ.get('NGINX', False) is not False:
#     ROOT_URLCONF = 'urls.default'

ROOT_URLCONF = "urls.default"

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * (1024 * 1024)
UPLOAD_STORE_DIR = config("UPLOAD_STORE_DIR", default=os.path.join(VAR_DIR, "storage"))
EXTERNAL_UPLOAD_STORE_DIR = config(
    "EXTERNAL_UPLOAD_STORE_DIR", default=UPLOAD_STORE_DIR
)

FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.TemporaryFileUploadHandler",)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOG_LEVELS = {
    "NOTSET": logging.NOTSET,
    "WARNING": logging.WARNING,
    "CRITICAL": logging.CRITICAL,
    "DEBUG": logging.DEBUG,
    "ERROR": logging.ERROR,
    "FATAL": logging.FATAL,
    "INFO": logging.INFO,
}

"""
Valor em minutos, para ficar mais didático
"""
TIMEOUT_SESSION_IN_MINUTES = config("TIMEOUT_SESSION_IN_MINUTES", default=60.0)

"""
Valor em segundos
"""
TIMEOUT_SESSION = TIMEOUT_SESSION_IN_MINUTES * 60
SESSION_COOKIE_AGE = TIMEOUT_SESSION
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False)

LOG_FILENAME = os.path.join(VAR_DIR, "log", "athenas.log")
LOG_MAX_SIZE = (1024 * 1024) * 200
LOG_ROTATION = 9
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FORMAT_MESSAGE = (
    "%(asctime)s - %(name)s.%(funcName)s.(%(lineno)d) - %(levelname)s - %(message)s"
)
LOG_FORMAT_DATE = "%Y-%m-%d %H:%M:%S"
LOG_STREAM_NAME = config("LOG_STREAM_NAME", default="stram")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(message)s"},
        "verbose": {"format": "%s %s" % (socket.gethostname(), LOG_FORMAT_MESSAGE)},
        "colored": {
            "format": "%(hostname)s \033[1m\033[31m%(levelname)-7s\033[0m \033[33m\033[1m%(funcName)s in %(module)s (%(lineno)s) \033[0m \033[1m\033[36m%(message)s\033[0m"
        },
        "new": {
            "format": "\n".join(
                [
                    "\033[1;32m%(hostname)s\033[0m [\033[1;31m%(levelname)s\033[0m] \033[1;33m%(pathname)s (%(lineno)d)\033[0m",
                    " + \033[1m%(message)s\033[0m",
                    "",
                ]
            )
        },
        "gelf": {
            "()": GELFFormatter,
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_FILENAME,
            "formatter": config("LOG_FORMAT", default="colored"),
        },
        "file-ws": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(VAR_DIR, "log", "ws.log"),
            "formatter": config("LOG_FORMAT", default="colored"),
        },
        "graylog": {
            "level": LOG_LEVEL,
            "class": "contrib.logging.GELFUDPHandler",
            "host": config("GRAYLOG_HOST", default="localhost"),
            "port": config("GRAYLOG_PORT", default=12201, cast=int),
            "formatter": "gelf",
        },
        "graylog-older": {
            "level": LOG_LEVEL,
            "class": "contrib.logging.GELFUDPHandler",
            "host": config("GRAYLOG_HOST_OLDER", default="localhost"),
            "port": config("GRAYLOG_PORT_OLDER", default=12201, cast=int),
            "formatter": "gelf",
        },
        "db_log": {
            "level": "DEBUG",
            "class": "common.services.handlers.DBHandler",
            "model": "common.services.models.StatusLog",
            "expiry": 86400,
            "formatter": "colored",
        },
    },
    "loggers": {
        "base-athenas": {
            "handlers": config("LOG_BASE_HANDLE", default=["file"]),
            "level": "DEBUG",
            "propagate": True,
        },
        "websocket": {
            "handlers": config("LOG_BASE_HANDLE", default=["file-ws"]),
            "level": "DEBUG",
            "propagate": True,
        },
        "db": {
            "handlers": ["db_log", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}


APPLICATION_TITLE = config(
    "APPLICATION_TITLE", default="Ministério Público do Mato Grosso"
)

FORCE_SECURE = config("FORCE_SECURE", default=False)

SIGLAS_LOTACAO = config("SIGLAS_LOTACAO", default=None)

STARTUP_MODULES = ()

DATE_INPUT_FORMATS = ("%d/%m/%Y",)
DATETIME_INPUT_FORMATS = ("%d/%m/%Y %H:%M",)

AUTH_USER_MODEL = "auth.User"

# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

TO_CHECK_STATS = (
    {
        "key": "HTTP_USER_AGENT",
        "pattern": "^.*Firefox/3\.0\.([0-9]+|1[0-9]).*$",
        "msg": 'Navegador do host "%(REMOTE_ADDR)s" necessita de atualização do navegador.',
    },
)

CACHE_BASE = config("CACHE_BASE", default=os.path.join(VAR_DIR, "cache"))
CACHE_PATH = os.path.join(CACHE_BASE, "athenas")
LOCKS_DIR = os.path.join(CACHE_BASE, "locks")
RESTART_FILE = os.path.join(BASE_DIR, "restart.txt")

CACHE = {
    "dir": CACHE_PATH,
    "jreport": os.path.join(CACHE_BASE, "jreport"),
    "sicapap": os.path.join(CACHE_BASE, "sicapap"),
    "flowchart": os.path.join(CACHE_BASE, "flowchart"),
}

# CALCULO_AUTO_REGISTER = True
RUNCODE_AUTO_REGISTER = True

THEME = config("THEME", default=0)

SIGN_FONT = "/usr/share/fonts/truetype/droid/DroidSans.ttf"
SIGN_FONT_SIZE = 13

# Web environment
RESOURCE_BASE_URL = None
ATHENAS_PORT = config("ATHENAS_PORT", default=8000)

if DOMAIN and ATHENAS_PORT:
    RESOURCE_BASE_URL = "%(domain)s:%(port)d" % {"domain": DOMAIN, "port": ATHENAS_PORT}
else:
    RESOURCE_BASE_URL = DOMAIN

DOWNLOAD_IMAGES_URL = "//%s/media/images" % RESOURCE_BASE_URL
RESIZED_IMAGES_DIR = os.path.join(VAR_DIR, "www", "media", "images")

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = config("SESSION_CACHE_ALIAS", default="redis")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config(
            "REDIS_CACHE_LOCATION", default="redis://:secr3t@redis:6379/2"
        ),
        "OPTIONS": config(
            "REDIS_CACHE_OPTIONS",
            default={
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 30,
                    "retry_on_timeout": True,
                },
            },
        ),
        "KEY_PREFIX": config("REDIS_CACHE_PREFIX", default="cache"),
    },
    "redis": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config(
            "REDIS_CACHE_LOCATION", default="redis://:secr3t@redis:6379/1"
        ),
        "OPTIONS": config(
            "REDIS_CACHE_OPTIONS",
            default={
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 30,
                    "retry_on_timeout": True,
                },
            },
        ),
        "KEY_PREFIX": config("REDIS_CACHE_PREFIX", default="cache"),
    },
    "file": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": os.path.join(CACHE_BASE, "session"),
    },
    "memcache01": {
        "BACKEND": "django.core.cache.backends.memcached.PyMemcacheCache",
        "LOCATION": config("CACHE_MEMCACHED01_LOCATION", default=["memcache"]),
    },
}

RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY", default="")

MINIFY_JS_BASEDIR = config(
    "MINIFY_JS_BASEDIR", default=os.path.join(VAR_DIR, "www", "static", "build")
)
MINIFY_JS_URL_BASEPATH = config("MINIFY_JS_URL_BASEPATH", "/athenas/static/build")
MINIFY_JS_HTDOCS = config("MINIFY_JS_HTDOCS", default=os.path.join(VAR_DIR, "www"))

CONV_COBRANCA = config(
    "CONV_COBRANCA", default="undefined"
)  # Código de Cobrança do refTran
ID_CONV = config(
    "ID_CONV", default="undefined"
)  # Número do Comercio Eletronico: 318602 codConv

MINIFY_JS_RULES = [
    (re.compile(r"js/toolkit"), os.path.join(BASE_DIR, "static/js"), lambda a: a[1:]),
    (re.compile(r"js/crypto"), os.path.join(BASE_DIR, "static/js"), lambda a: a[1:]),
    (
        re.compile(r"js/(core|auth|stats)"),
        os.path.join(BASE_DIR, "static"),
        lambda a: a,
    ),
    (re.compile(r"standard"), os.path.join(BASE_DIR, "static"), lambda a: a),
    (
        re.compile(r"js/ext"),
        os.path.join(MINIFY_JS_HTDOCS, "ext-3.4.0"),
        lambda a: a[2:],
    ),
    (re.compile(r"js/ckeditor"), MINIFY_JS_HTDOCS, lambda a: a[1:]),
    (
        re.compile(r"js/codemirror"),
        os.path.join(MINIFY_JS_HTDOCS, "CodeMirror"),
        lambda a: a[2:],
    ),
]

INSTALLED_APPS_DJANGO = (
    "channels",
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.postgres",
    # 'django.contrib.admin',
    "django.contrib.humanize",
    # 'snowpenguin.django.recaptcha2',
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "drf_spectacular",
    # Health Check
    "health_check",  # required
    "health_check.db",  # stock Django health checkers
    # 'health_check.cache',
    "health_check.storage",
    "health_check.contrib.migrations",
    # 'health_check.contrib.celery',              # requires celery
    # 'health_check.contrib.celery_ping',         # requires celery
    # 'health_check.contrib.psutil',              # disk and memory utilization; requires psutil
    # 'health_check.contrib.redis',               # required Redis broker
    "colorfield",
)

INSTALLED_APPS_MODULES = (
    # CORE
    "auth.base",
    "auth.ws",
    "auth.jwt",
    "auth.mastiff",
    # 'monitor',
    "auditoria",
    "engine",
    "engine.mq",
    "engine.notification",
    "default",
    "standard",
    "standard.questionario",
    # NOTIFICACAO
    "common.util",
    # Mala direta
    "common.mailing",
    # Votações
    "common.poll",
    # Diário Oficial
    "common.official_journal",
    # SIATU
    "common.siatu",
    # iTop
    "common.itop",
    # Gestor de Dias Úteis
    "common.usefulday",
    # Questionários
    # 'common.questionnaire',
    "ged",
    # RH
    "rh",
    "rh.gfp",
    "rh.gfp.dirf",
    "rh.gfp.planoconta",
    "rh.gfp.configuration",
    "rh.ferias",
    "rh.afastamento",
    "rh.estagio",
    "rh.profile",
    "rh.ponto",
    "rh.socialsecurity",
    "rh.pensao",
    "rh.scmmp",
    "rh.cif",
    "rh.apd",
    "rh.registration",
    "rh.dayoff",
    "rh.employeeaccesscontrol",
    "rh.plantoes",
    "rh.pvf",
    "rh.pvf.absence",
    "rh.queryregistration",
    "rh.cadastralquality",
    "rh.gratifications_manager",
    "rh.sisdias",
    "rh.defin",
    "rh.modelreport",
    "rh.registerpoint",
    "rh.antiguidades",
    "rh.servidor",
    "rh.teletrabalho",
    "rh.folhaponto",
    # 'rh.ac',
    "edocs.protocolo",
    "edocs.protocolo.apiprotocol",
    "edocs.protocolo.requestform",
    "edocs.processo",
    "edocs.protocolo.channels",
    # WEB
    "web",
    "web.ouvidoria",
    "web.accountability",
    "web.media_indoor",
    # PLANEJAMENTO
    "planejamento.pe",
    "planejamento.contrato",
    # CESAF
    "cesaf.gecap",
    "cesaf.concurso",
    # CEAF
    "ceaf",
    # 'bi',
    # ADMINISTRATIVO
    "workflow",
    "adm.contabilidade",
    "adm.eproc",
    "adm.compras",
    "adm.cpl",
    "adm.mto",
    "adm.patrimonio",
    # JUDICIAL
    "judicial",
    "judicial.tac",
    "judicial.council",
    # RAF
    "raf",
    # ESOCIAL
    "esocial",
    #
    # Corregedoria-geral
    "corregedoria",
    "corregedoria.reportbuilder",
    "corregedoria.cirdir",
    "corregedoria.inspection",
    "corregedoria.prontuary",
    "corregedoria.cnmp",
    # common
    "common.payments",
    "common.distribution",
    "common.internal_security",
    "common.saci",
    "common.functional_id",
    "common.clinical",
    "common.document_access",
    "common.services",
    # Reports
    "reports",
    # Auditlog
    "auditlog",
    "health",
    "health.sst",
    # Nomeação
    "nomeacao",
    "nomeacao.cadastramento",
    # Anotação Pessoal
    "anotacao_pessoal",
    # Menu Permissões
    "menu_permissoes",
    # Diárias
    "diarias",
    # Painel de Controle
    "painel_controle",
    "auth.apiv2",
)

TEST_APPS = config("TEST_APPS", default=[])

APPS_TO_REMOVE = [
    "corregedoria",
    "corregedoria.reportbuilder",
    "corregedoria.cirdir",
    "corregedoria.inspection",
    "corregedoria.prontuary",
    "corregedoria.cnmp",
]
REMOVE_APPS = config("REMOVE_APPS", default=APPS_TO_REMOVE)

INSTALLED_APPS = (
    INSTALLED_APPS_DJANGO
    + tuple([app for app in INSTALLED_APPS_MODULES if app not in REMOVE_APPS])
    + tuple(TEST_APPS)
)

# Configuracao do Roteador
ROUTER = {
    "default": {
        "controller": "Application",
        "action": "index",
    },
    "exception": {
        "controller": "DefaultException",
        "action": "index",
    },
    "controllers": [
        # 'planejamento.pe.views',
        # 'adm.sispat.views',
    ]
    + dynaset.apps_controllers(INSTALLED_APPS),
}

ASGI_APPLICATION = "app.asgi.py3.application"

CHANNEL_LAYERS = config(
    "CHANNEL_LAYERS",
    default={
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": ["redis://:secr3t@redis:6379/0"]},
        },
    },
)

# Configuracao do OAuth2
USE_SSO = config("USE_SSO", default=False)

SSO_COOKIE_DOMAIN = config("SSO_COOKIE_DOMAIN", default=".tls.local")

OAUTH_SERVER = config("OAUTH_SERVER", default="https://a.tls.local:7443")

OAUTH_AUTHORIZATION_URL = config("OAUTH_AUTHORIZATION_URL", default="/o/authorize/")
OAUTH_TOKEN_URL = config("OAUTH_TOKEN_URL", default="/o/token/")
OAUTH_REVOKE_TOKEN_URL = config("OAUTH_REVOKE_TOKEN_URL", default="/o/revoke_token/")

OAUTH_REFRESH_TOKEN_URL = OAUTH_TOKEN_URL

OAUTH_CLIENT_ID = config("OAUTH_CLIENT_ID", default="client_id")
OAUTH_CLIENT_SECRET = config("OAUTH_CLIENT_SECRET", default="client_secret")

OAUTH_CALLBACK_URL = config(
    "OAUTH_CALLBACK_URL",
    default="https://b.tls.local:8443/athenas/oauth/login/callback/",
)
OAUTH_USER_SYNC_FREQUENCY = config("OAUTH_USER_SYNC_FREQUENCY", default=3600)
OAUTH_VERIFY_SSL = config("OAUTH_VERIFY_SSL", default=False)
OAUTH_RESOURCE_URL = config("OAUTH_RESOURCE_URL", default="/api/userinfo")

SSO_PUBLIC_KEY = config_file_content("SSO_PUBLIC_KEY")

HERMES_TOKEN = config(
    "HERMES_TOKEN", default="01dc6aef-eb78-4ddf-9882-ec7a2e34b78e", use_secret=True
)
HERMES_TOKEN_RELATORIOS = config("HERMES_TOKEN_RELATORIOS", default="", use_secret=True)
HERMES_TOKEN_EMAIL_PESSOAL = config(
    "HERMES_TOKEN_EMAIL_PESSOAL", default="", use_secret=True
)
HERMES_TOKEN_PROCESSAMENTOS = config(
    "HERMES_TOKEN_PROCESSAMENTOS", default="", use_secret=True
)
HERMES_URL = config(
    "HERMES_URL",
    default="https://teste.mpmt.mp.br/hermes-api/rest/solicitacao/solicitarEnvioEmail",
)
HERMES_URL_ANEXO = config(
    "HERMES_URL_ANEXO",
    default="https://teste.mpmt.mp.br/hermes-api/rest/solicitacao/solicitarEnvioEmailComAnexo",
)
HERMES_URL_NOTIFICACAO = config(
    "HERMES_URL_NOTIFICACAO",
    default="https://teste.mpmt.mp.br/hermes-api/rest/notificacao",
)
URL_INTRANET = config("URL_INTRANET", default="https://intranet.tls.local:8080/")

PLANTOES_API_URL = config(
    "PLANTOES_API_URL", default="https://teste.mpmt.mp.br/plantoes/api"
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = config(
    "SESSION_EXPIRE_AT_BROWSER_CLOSE", default=False
)

ESOCIAL_ENVIRONMENT = config("ESOCIAL_ENVIRONMENT", default=2)

AUDITLOG_INCLUDE_ALL_MODELS = False

SISDIAS_TOKEN = config("TOKEN_API_SISDIAS", default="", use_secret=True)
SISDIAS_API_URL = config("SISDIAS_API_URL", default="")

locals().update(dynaset.apps_settings(INSTALLED_APPS))

CROWD_SERVER_NAME = config("CROWD_SERVER_NAME", default="https://dev-crowd.mpmt.mp.br")
CROWD_SERVER_PORT = config("CROWD_SERVER_PORT", default=443)
CROWD_APP_NAME = config("CROWD_APP_NAME", default="")
CROWD_APP_PASSWD = config("CROWD_APP_PASSWD", default="", use_secret=True)
CROWD_SESSION_NAME = config("CROWD_SESSION_NAME", default="")
MASTIFF_URL_SERVER = config(
    "MASTIFF_URL_SERVER",
    default="https://teste.mpmt.mp.br/mastiff/seam/resource/rest/permissao/consultar",
)
ATHENAS_ENV = config("ATHENAS_ENV", default="dev")
REMOTE = config("REMOTE", default="127.0.0.1")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("auth.backend.CustomJWTAuthentication",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ATHENAS API",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "POSTPROCESSING_HOOKS": [],
    "SCHEMA_PATH_PREFIX": "/athenas/api/v2",
}

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

JWT_SECRET_KEY = config("JWT_SECRET_KEY", "secr3t", use_secret=True)
CLASS_AUTHENTICATION_JWT = ("auth.backend.CustomTokenJWTAuthentication",)

STATIC_ROOT = os.path.join(BASE_DIR, "app/var/www/static/")
STATIC_URL = "/athenas/static/"

TOKEN_API_NOMEACAO_RESIDENTES = config(
    "TOKEN_API_NOMEACAO_RESIDENTES", default="", use_secret=True
)

TOKEN_API_DAA_TRANSP_DIST = config(
    "TOKEN_API_DAA_TRANSP_DIST", default="", use_secret=True
)

TOKEN_API_PLANTOES = config("TOKEN_API_PLANTOES", default="", use_secret=True)

CROWD_USERNAME = config("CROWD_USERNAME", default="", use_secret=True)
CROWD_PASSWORD = config("CROWD_PASSWORD", default="", use_secret=True)
CROWD_TOKEN = config("CROWD_TOKEN", default="", use_secret=True)

if ATHENAS_ENV == "dev":
    AUTHENTICATION_CLASSES_REPORT = None
    PERMISSION_CLASSES_REPORT = "rest_framework.permissions.AllowAny"
else:
    AUTHENTICATION_CLASSES_REPORT = "auth.backend.CustomJWTAuthentication"
    PERMISSION_CLASSES_REPORT = "rest_framework.permissions.IsAuthenticated"

IPS_AUTH_DEV = config("IPS_AUTH_DEV", [])
