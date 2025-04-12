# -*- coding: utf8 -*-
from app.settings import ORGAN_IDENTIFIER
import json as n_json
import os
import re
import requests
from functools import partial

from django import template
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseRedirect, QueryDict
from django.shortcuts import render

import static
from auth.sso.views import login_redirect
from auditoria.models import LineLog
from contrib import controller, extjs, helpers
from contrib.decorator import is_public, login_required, update_timeout_session
from contrib.utils import DateUtils, caller_name, get_json_engine, employee_from_user
from contrib.middleware import get_current_user
from .forms import LoginForm

from standard.models import Choice

json = get_json_engine()

log = helpers.getLogger(__name__)

AUDIT_ACCESS_PERFIL = "mpmt-perfil-auditoria"


class FirstAccessDriver(object):

    def __init__(self, request):
        self.request = request

    def check_first(self):
        raise Exception("Method abstract not implemented.")

    def validate(self):
        raise Exception("Method abstract not implemented.")


class DisableFirstAcesse(FirstAccessDriver):

    def check_first(self):
        return False


class ExtLogin(extjs.ExtWidget):

    @is_public()
    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write("new toolkit.widget.ExtLogin()")

    def _logout_sso(self):
        log.info("Realizando logout no SSO")
        tokens = self.request.session.get("oauth_token", None)

        log.debug(["tokens", tokens])

        if tokens:
            access_token = tokens.get("access_token", None)

            payload = {
                "token": access_token,
                "client_id": settings.OAUTH_CLIENT_ID,
                "client_secret": settings.OAUTH_CLIENT_SECRET,
            }
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            res = requests.post(
                settings.OAUTH_SERVER + settings.OAUTH_REVOKE_TOKEN_URL,
                data=payload,
                headers=headers,
                verify=False,
            )

            log.debug(["res", res])
        else:
            log.info("OAuth tokens not found in request")

        if "MPTO.SSO.Token" in self.request.COOKIES:
            self.response.set_cookie(
                "MPTO.SSO.Token",
                max_age=0,
                domain=settings.SSO_COOKIE_DOMAIN,
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
            )
        else:
            log.info("SSO Cookie not found")

        if "MPTO.visit_intranet" in self.request.COOKIES:
            self.response.set_cookie(
                "MPTO.visit_intranet",
                max_age=0,
                domain=settings.SSO_COOKIE_DOMAIN,
                expires="Thu, 01 Jan 1970 00:00:00 GMT",
            )
        else:
            log.info("SSO Cookie not found")

    def _logout_local(self):
        log.info("Realizando logout local")
        try:
            llog = LineLog()
            llog.level = 64
            llog.read_request(self.request)
            llog.status = 1
            llog.save()
        except Exception as e:
            self.log.exception(e)

        auth.logout(self.request)

    def logout(self, args=[]):
        if getattr(settings, "USE_SSO", False):
            self._logout_sso()

        self._logout_local()

    def redirect_cancel(self, args=[]):
        obj = {"url": settings.LDAP_AUTH["nologin"]}

        self.response.write(json.encode(obj))

    @is_public()
    def connect(self, args=[]):
        obj = {"success": False, "msg": "Nada foi feito até este momento."}

        user = self.request.POST.get("login", "")
        passwd = self.request.POST.get("passwd", "")
        theme = int(self.request.POST.get("theme", 1))

        o_user = auth.authenticate(username=user, password=passwd)

        llog = LineLog()
        llog.read_request(self.request)
        llog.level = 32

        if o_user:
            obj.update(success=True)
            auth.login(self.request, o_user)

            self.request.session["theme"] = theme

            llog.status = 1
        else:
            obj.update(msg="Nome de usuário ou senha inválida.")
            llog.status = 0

        llog.save()
        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def first_access(self, args=[]):
        obj = {
            "success": False,
            "msg": "Erro ao validar informações do servidor.\nEntre em contato com o RH (ramal 7692).",
        }

        llog = LineLog()
        llog.read_request(self.request)
        llog.level = 32

        cpf = self.request.POST.get("cpf", "")
        cpf = cpf.replace(".", "")
        cpf = cpf.replace("-", "")

        matricula = self.request.POST.get("matricula", "")
        nascimento = DateUtils.str_to_date(self.request.POST["nascimento"])

        llog.status = 0
        servidor = ExtLogin.valida_servidor(cpf, matricula, nascimento)
        if (
            servidor is not None
            and servidor.user is None
            and self.request.user.is_authenticated
        ):
            if ExtLogin.set_user_servidor(
                servidor, self.request.user
            ) and ExtLogin.set_permissao_servidor(servidor):
                llog.status = 1
                obj.update(success=True)
        elif servidor is None:
            obj.update(msg="Os dados do servidor não batem.")
        elif self.request.user.is_authenticated is False:
            obj.update(msg="A sua sessão expirou tente novamente.")
        elif servidor is not None and servidor.user is not None:
            obj.update(success=True)

        if llog.status == 1:
            obj.update(success=True)
            obj.update(msg="Configuração de primeiro acesso realizada com sucesso!")

        llog.save()
        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @staticmethod
    def valida_servidor(cpf, matricula, data_nascimento):
        """
        Este método verifica se o cpf, matrícula e data data de nascimento pertencem a um servidor.
        @param kargs - Variável keyworded .
        @return Servidor - Retorna o Servidor caso seja encontrado, de outra forma retorna None.
        """
        from contrib.utils import getLogger
        from rh.models import Servidor

        log = getLogger("ExtLogin:View:valida_servidor")

        try:
            servidor = Servidor.objects.get(
                pessoa_fisica__cpf=cpf,
                matricula=matricula,
                pessoa_fisica__data_nascimento=data_nascimento,
            )
        except Exception as e:
            log.info("%s", (cpf, matricula, data_nascimento))
            log.exception(e)
            servidor = None
        finally:
            return servidor

    @staticmethod
    def set_user_servidor(servidor, user):
        """
        Este método atribui User ao Servidor.
        @param Servidor - Servidor que receberá o User.
        @param User - User que será atribuído ao Servidor.
        @return True - em caso de sucesso. De outra forma False.
        """
        from contrib.utils import getLogger
        from rh.models import Servidor

        log = getLogger("ExtLogin:View:set_user_servidor")
        try:
            Servidor.objects.filter(user=user).update(user=None)
            servidor.user = user
            servidor.save()
        except Exception as e:
            log.exception(e)
            return False
        return True

    @staticmethod
    def set_permissao_servidor(servidor):
        """
        Este método aplica as permissões básicas ao Servidor/User. A permissão aplicada será ao grupo BASICO.
        @param Servidor - Servidor que receberá a permissão.
        @return True - em caso de sucesso. De outra forma False.
        """
        from contrib.utils import getLogger
        from engine.models import ControllerPermission
        from django.contrib.auth.models import Group

        log = getLogger("ExtLogin:View:set_permissao_servidor")
        rst = False

        try:
            cperm = ControllerPermission.objects.get(name="basico")
            group = Group.objects.get(name="Basico")
        except Group.DoesNotExist:
            log.warn("Não consegui encontrar o grupo de funcionalidades basico.")
        except ControllerPermission.DoesNotExist:
            log.warn(
                "Não consegui encontrar o grupo de permissões de controllers basico"
            )
        except Exception as e:
            log.exception(e)
        else:
            cperm.users.add(servidor.user)
            group.user_set.add(servidor.user)
            rst = True

        return rst

    @staticmethod
    def set_localizacao_servidor(servidor, localizacao):
        """
        Este método atribui a localização ao servidor.
        @param Servidor - Instância de Servidor.
        @param int - PK da lotação.
        @return True - em caso de sucesso. De outra forma False.
        """
        from rh.models import ServidorLocalizacao, Lotacao
        from contrib.utils import getLogger

        log = getLogger("ExtLogin:View:set_localizacao_servidor")
        try:
            servidor_localizacao = ServidorLocalizacao(
                servidor=servidor, localizacao=Lotacao.objects.get(pk=localizacao)
            )
            servidor_localizacao.save()
        except Exception as e:
            log.exception(e)
            return False
        return True

    @staticmethod
    def get_localizacao_servidor(servidor):
        """
        Este método atribui a localização ao servidor.
        @param Servidor - Instância de Servidor.
        @param int - PK da lotação.
        @return int - Quantidade de localizações para aquele servidor.
        Retornará "0" quando não houver dados cadastrados.
        """
        from rh.models import ServidorLocalizacao

        if servidor.tipo == "M":
            return 1
        return ServidorLocalizacao.objects.filter(servidor=servidor).count()


class Application(controller.DefaultController):

    collections = {
        "js": [
            ("/%(context)s/static/js/ext/adapter/ext/ext-base.js", "lib"),
            ("/%(context)s/static/js/ext/ext-all.js", "lib"),
            ("/%(context)s/static/js/ext/ext-lang-pt_BR.js", "lib"),
            ("/%(context)s/static/js/ckeditor/ckeditor.js", "lib"),
            ("/%(context)s/static/js/ckeditor/lang/pt-br.js", "lib"),
            ("/%(context)s/static/js/ckeditor/styles.js", "lib"),
            ("/%(context)s/static/js/ckeditor/config.js", "lib"),
            ("/%(context)s/static/js/codemirror/lib/codemirror.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/mode/overlay.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/hint/show-hint.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/hint/css-hint.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/hint/html-hint.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/hint/xml-hint.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/hint/javascript-hint.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/search/searchcursor.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/search/search.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/dialog/dialog.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/edit/matchbrackets.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/edit/closebrackets.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/comment/comment.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/brace-fold.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/comment-fold.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/foldcode.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/foldgutter.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/indent-fold.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/markdown-fold.js", "lib"),
            ("/%(context)s/static/js/codemirror/addon/fold/xml-fold.js", "lib"),
            ("/%(context)s/static/js/codemirror/keymap/sublime.js", "lib"),
            ("/%(context)s/static/js/codemirror/mode/javascript/javascript.js", "lib"),
            ("/%(context)s/static/js/codemirror/mode/xml/xml.js", "lib"),
            ("/%(context)s/static/js/codemirror/mode/htmlmixed/htmlmixed.js", "lib"),
            ("/%(context)s/static/js/codemirror/mode/python/python.js", "lib"),
            ("/%(context)s/static/js/codemirror/mode/django/django.js", "lib"),
            ("/%(context)s/static/js/core/core.js", "core"),
            ("/%(context)s/static/js/toolkit/util.js", "core"),
            ("/%(context)s/static/js/toolkit/base64.js", "core"),
            ("/%(context)s/static/js/toolkit/exception.js", "core"),
            ("/%(context)s/static/js/toolkit/widget.js", "core"),
            ("/%(context)s/static/js/core/RemoteObserver.js", "core"),
            ("/%(context)s/static/js/toolkit/application.js", "core"),
            ("/%(context)s/static/js/toolkit/feed.js", "core"),
            ("/%(context)s/static/js/toolkit/auth-widget.js", "core"),
            ("/%(context)s/static/js/toolkit/plugins.js", "core"),
            ("/%(context)s/static/js/toolkit/thread.js", "core"),
            ("/%(context)s/static/js/toolkit/iget.js", "core"),
            ("/%(context)s/static/js/toolkit/restful.js", "core"),
            ("/%(context)s/static/js/core/TilePagePanel.js", "core"),
            ("/%(context)s/static/js/core/Restful.js", "core"),
            ("/%(context)s/static/js/core/RestfulGrid.js", "core"),
            ("/%(context)s/static/js/core/GridActionWindow.js", "core"),
            ("/%(context)s/static/js/core/GridSelectWindow.js", "core"),
            ("/%(context)s/static/js/core/TreeActionWindow.js", "core"),
            ("/%(context)s/static/js/core/TreeMoveWindow.js", "core"),
            ("/%(context)s/static/js/core/TreeSelectWindow.js", "core"),
            ("/%(context)s/static/js/core/RestfulTree.js", "core"),
            ("/%(context)s/static/js/core/RestfulPanel.js", "core"),
            ("/%(context)s/static/js/core/RestfulWindow.js", "core"),
            ("/%(context)s/static/js/core/fields/ComboField.js", "core"),
            ("/%(context)s/static/js/core/fields/FoldedRestfulField.js", "core"),
            (
                "/%(context)s/static/js/core/fields/AutocompleteSelectionWindow.js",
                "core",
            ),
            ("/%(context)s/static/js/core/fields/AutocompleteField.js", "core"),
            ("/%(context)s/static/js/core/fields/RelatedSelectWindow.js", "core"),
            ("/%(context)s/static/js/core/fields/RelatedRestfulField.js", "core"),
            ("/%(context)s/static/js/core/fields/MultiSelectField.js", "core"),
            ("/%(context)s/static/js/core/fields/DisplayDatetimeField.js", "core"),
            ("/%(context)s/static/js/core/fields/DisplayDateField.js", "core"),
            ("/%(context)s/static/js/core/fields/CodeEditor.js", "core"),
            ("/%(context)s/static/js/core/fields/PhoneField.js", "core"),
            ("/%(context)s/static/js/core/fields/CpfField.js", "core"),
            ("/%(context)s/static/js/core/fields/CurrencyField.js", "core"),
            ("/%(context)s/static/js/core/fields/RestfulMultiChoiceField.js", "core"),
            ("/%(context)s/static/js/core/fields/FileUploadField.js", "core"),
            ("/%(context)s/static/js/core/fields/WebcamInputWindow.js", "core"),
            ("/%(context)s/static/js/core/fields/ImageFileUploadField.js", "core"),
            ("/%(context)s/static/standard/ChoiceRestful.js", "core"),
            ("/%(context)s/static/standard/ChoiceWindow.js", "core"),
            ("/%(context)s/static/standard/ChoiceGrid.js", "core"),
            ("/%(context)s/static/standard/ChoiceManage.js", "core"),
            ("/%(context)s/static/standard/fields/ChoiceField.js", "core"),
            ("/%(context)s/static/standard/fields/CheckBoxChoiceField.js", "core"),
            ("/%(context)s/static/js/core/GlobalMenu.js", "core"),
            ("/%(context)s/static/js/core/DebugInformation.js", "core"),
            ("/%(context)s/static/js/auth/LinkUserServidorWindow.js", "core"),
            ("/%(context)s/static/js/toolkit/fields/DateTimeField.js", "core"),
            ("/%(context)s/static/js/toolkit/fields/AutoCompleteField.js", "core"),
            ("/%(context)s/static/js/toolkit/fields/CKEditor.js", "core"),
            ("/%(context)s/static/js/stats/Colector.js", "core"),
        ],
        "dep_js": {},
        "css": [
            "/%(context)s/static/js/codemirror/lib/codemirror.css",
            "/%(context)s/static/js/codemirror/addon/fold/foldgutter.css",
            "/%(context)s/static/js/codemirror/theme/3024-day.css",
            "/%(context)s/static/css/chrome22.css",
            "/%(context)s/static/core.css",
            "/%(context)s/static/js/core/core.css",
            "/%(context)s/static/js/core/papper.css",
            "/%(context)s/static/ged.css",
        ],
    }

    @is_public()
    def heart_check(self, args=[]):
        self.response.write('{ "success": true, "message": "estou online" }')

    def dump_http(self, args=[]):
        if getattr(settings, "DEBUG", False):
            self.response["Content-Type"] = "text/plain"
            prefix = self.request.GET.get("name", None)

            for attr, value in sorted(self.request.META.items()):
                if not prefix or attr.startswith(prefix):
                    self.response.write("%-35s: %s\n" % (attr, value))
        else:
            self.response = HttpResponseNotFound()

    @staticmethod
    def clear_dependence_js(path):
        collection_js = Application.collections.get("js", [])
        dependencies_js = Application.collections.get("dep_js", {})

        # Verificando dependencias supridas com novo path
        for dep_path in list(dependencies_js.keys()):
            if path in dependencies_js[dep_path]:
                dependencies_js[dep_path].remove(path)
            if len(dependencies_js[dep_path]) == 0:
                collection_js.append(dep_path)
                dependencies_js.pop(dep_path)
                log.debug("CLEAR JS DEPENDENCE: %s" % dep_path)
                Application.clear_dependence_js(dep_path)

    @staticmethod
    def register_javascript(path, dependencies=[], scope=None):
        app = scope
        if not scope:
            app = caller_name(2)
            app = app.split(".")[0] if app else "default"

        collection_js = Application.collections.get("js", [])
        dependencies_js = Application.collections.get("dep_js", {})
        if path not in collection_js:
            # Armazenando path com dependencia para ser carregado depois
            for dep_js in dependencies:
                if dep_js not in collection_js and dep_js not in dependencies_js.get(
                    path, []
                ):
                    dependencies_js[path] = (
                        [
                            dep_js,
                        ]
                        if path not in dependencies_js
                        else (
                            dependencies_js[path]
                            + [
                                dep_js,
                            ]
                        )
                    )
                    log.debug(
                        "CREATE JS DEPENDENCE: %s > %s" % (path, dependencies_js[path])
                    )

            if path not in dependencies_js:
                collection_js.append((path, app))
                Application.clear_dependence_js((path, app))

    @staticmethod
    def register_stylesheet(path):
        css = Application.collections.get("css", [])
        if path not in css:
            css.append(path)

    @is_public()
    def css_icons(self, *args):
        from django import template
        from engine.models import Controller, Application

        icons = []

        for app in Application.objects.exclude(icon=None):
            icons.append({"name": app.icon.split(".")[0], "image": app.icon})

        for ctl in Controller.objects.exclude(icon=None):
            icons.append({"name": ctl.icon.split(".")[0], "image": ctl.icon})

        tpl = template.engines["django"].from_string(
            """
{% for icon in icons %}
    .icon-{{icon.name}} {background-image:url('/{{context}}/static/engine/images/icons/{{icon.image}}') !important}
    .tree-icon-{{icon.name}} .x-tree-node-icon {background-image:url('/{{context}}/static/engine/images/icons/{{icon.image}}') !important}
{% endfor %}"""
        )

        self.response["content-type"] = "text/css"
        self.response.write(tpl.render({"icons": icons, "context": settings.CONTEXT}))

    @classmethod
    def session_resource(klass, name):
        def wrapper(method):
            db = getattr(klass, "_session_resource_db", [])

            db.append({"name": name, "method": method})

            setattr(klass, "_session_resource_db", db)
            return method

        return wrapper

    def read_session_resources(self):
        db = getattr(self, "_session_resource_db", [])
        rst = {}

        for res in db:
            rst.update({res.get("name"): res.get("method")()})

        return rst

    @is_public()
    @update_timeout_session(False)
    def get_session_information(self, args=[]):
        import platform

        obj = {
            "node": platform.node(),
            "is_auth": self.is_auth(),
            "session_timeout": (settings.TIMEOUT_SESSION + 5) * 1000,
            "is_firstaccess": False,
        }

        if self.is_auth():
            obj.update(
                notifications=self.read_session_resources(),
                access_reports=(
                    get_current_user()
                    .controllerpermission_set.filter(name="mpmt-menu-aba-relatorios")
                    .exists()
                    or get_current_user().is_superuser
                ),
            )

        if obj.get("is_firstaccess"):
            obj.update(session_timeout=(120 * 1000))
            self.request.session.set_expiry(120)

        self.response["Content-Type"] = "text/javascript"
        if "cb" in self.request.GET:
            self.response.write(
                "%s(%s)" % (self.request.GET.get("cb"), json.encode(obj))
            )
        else:
            self.response.write(json.encode(obj))

    def un_autorized(self, args=[]):
        self.response.status_code = 403
        if args[0] == "TEXT":
            self.response.write("Acesso negado.")
        elif args[0] == "JSON":
            obj = {
                "exception": "toolkit.exception.JSONError",
                "exceptionMessage": "Acesso negado.",
            }
            self.response.write(json.encode(obj))
        elif args[0] == "BUFFER":
            self.response["content-type"] = "text/plain"
            self.response["content-disposition"] = (
                "attachment; filename=acesso_negado.txt"
            )
            self.response.write("Acesso negado.")

    @classmethod
    def read_cachesum(klass, name):
        import hashlib

        eng = hashlib.new("md5")
        with open("/app/root/static/build/%s.min.js" % name, "r") as fd:
            for chunk in iter(partial(fd.read, 8192), b""):
                eng.update(chunk)

        return eng.hexdigest()

    @classmethod
    def get_session_javascripts(klass):
        from default.management.commands.minify import Command

        defaults = {"context": getattr(settings, "CONTEXT", "")}
        obj = []

        if getattr(settings, "MINIFY_JS_BASEDIR", False) and getattr(
            settings, "MINIFY_JS_URL_BASEPATH", False
        ):
            cachedata = None

            try:
                log.info(
                    "js cache: %s",
                    os.path.join(getattr(settings, "MINIFY_JS_BASEDIR"), "cache.json"),
                )

                cachedata = n_json.load(
                    open(
                        os.path.join(
                            getattr(settings, "MINIFY_JS_BASEDIR"), "cache.json"
                        )
                    )
                )
            except Exception as e:
                log.exception(e)
                cachedata = {}

            for js_lib in [a for a in klass.js_libraries() if a != "remote"]:
                ccache = cachedata.get(js_lib, "undefined")

                obj.append(
                    "%s/%s.min.js?ccache=%s"
                    % (getattr(settings, "MINIFY_JS_URL_BASEPATH"), js_lib, ccache)
                )

            obj += [
                path % defaults
                for path, libname in Application.collections.get("js", [])
                if libname == "remote"
            ]
        else:
            obj = [
                path % defaults
                for path, libname in Application.collections.get("js", [])
            ]

        return obj

    @classmethod
    def js_libraries(klass):
        weights = {
            "lib": 0,
            "core": 1,
            "engine": 2,
            "standard": 3,
            "rh": 3,
            "raf": 100,
        }

        if not getattr(klass, "__cache_js_libraries", False):
            klass.__cache_js_libraries = sorted(
                {lib for path, lib in Application.collections.get("js", [])},
                key=lambda b: weights.get(b, 10),
            )

        return klass.__cache_js_libraries

    @classmethod
    def get_session_stylesheet(self):
        from default.management.commands.minify import Command

        defaults = {"context": getattr(settings, "CONTEXT", "")}
        obj = []

        if getattr(settings, "MINIFY_CSS_OUT", None) is not None:
            obj = [
                path % defaults
                for path in Application.collections.get("css", [])
                if Command.is_uglify(path) is False
            ]
            flag = False
            for jsfile in Application.collections.get("css", []):
                if Command.is_uglify(jsfile) is True:
                    flag = True
                    break

            if flag is True:
                obj.insert(0, getattr(settings, "MINIFY_CSS_OUT"))
        else:
            obj = [path % defaults for path in Application.collections.get("css", [])]

        return obj

    @is_public()
    def login(self, args=[]):
        if settings.USE_SSO:
            self.response = login_redirect(self.request)
        else:
            redirect = None
            if not self.is_auth():
                form = LoginForm()

                if self.request.method == "POST":
                    form = LoginForm(self.request.POST)

                    if form.is_valid():
                        user = form.cleaned_data["login"]
                        passwd = form.cleaned_data["passwd"]
                        theme = form.cleaned_data["theme"]

                        o_user = auth.authenticate(username=user, password=passwd)

                        llog = LineLog()
                        llog.read_request(self.request)
                        llog.level = 32

                        if o_user and o_user.pk and o_user.is_active:
                            if (
                                o_user.controllerpermission_set.filter(
                                    manager_permission=True
                                ).exists()
                                or o_user.is_superuser
                            ):
                                auth.login(self.request, o_user)
                                self.request.session["theme"] = theme
                                llog.status = 1
                                redirect = HttpResponseRedirect(
                                    "/%s/" % getattr(settings, "CONTEXT", "athenas")
                                )
                            else:
                                if settings.ATHENAS_ENV == "production":
                                    url = "https://athenas.mpmt.mp.br/suite-athenas/"
                                else:  # 'homolog' e 'dev'
                                    url = (
                                        "https://athenas-hom.mpmt.mp.br/suite-athenas/"
                                    )
                                redirect = HttpResponseRedirect(url)
                        else:
                            if o_user and not o_user.pk:
                                form.add_error(
                                    None,
                                    "Login não configurado, favor entrar contato com o DGP!",
                                )
                                llog.status = 0
                            else:
                                form.add_error(None, "Usuário ou senha incorretos")
                                llog.status = 0

                        llog.save()

                params = {
                    "form": form,
                    "js": self.get_session_javascripts(),
                    "DEBUG": getattr(settings, "DEBUG"),
                    "CONTEXT": getattr(settings, "CONTEXT"),
                    "APPLICATION_TITLE": getattr(settings, "APPLICATION_TITLE"),
                    "imgs_name_default": self.get_imgs_name_default(),
                }
            else:
                redirect = HttpResponseRedirect(
                    "/%s/" % getattr(settings, "CONTEXT", "athenas")
                )

            self.response = (
                redirect if redirect else render(self.request, "login.tpl", params)
            )

    @is_public()
    def index(self, args=[]):
        uri = self.request.build_absolute_uri("")
        # uris = uri.replace('http', 'https')

        if getattr(settings, "FORCE_SECURE", False) and not self.request.is_secure():
            self.response = HttpResponseRedirect(
                self.request.build_absolute_uri("").replace("http", "https")
            )
        elif not self.is_auth():
            if settings.USE_SSO:
                if "MPTO.visit_intranet" not in self.request.COOKIES:
                    self.response = HttpResponseRedirect(settings.URL_INTRANET)
                    self.response.set_cookie(
                        "MPTO.visit_intranet",
                        value=True,
                        max_age=36000,
                        domain=settings.SSO_COOKIE_DOMAIN,
                    )
                else:
                    self.response = login_redirect(self.request)
            else:
                self.response = HttpResponseRedirect(
                    "/%s/Application/login/" % getattr(settings, "CONTEXT", "athenas")
                )
        else:

            if settings.USE_SSO:
                if "MPTO.visit_intranet" not in self.request.COOKIES:
                    self.response = HttpResponseRedirect(settings.URL_INTRANET)
                    self.response.set_cookie(
                        "MPTO.visit_intranet",
                        value=True,
                        max_age=36000,
                        domain=settings.SSO_COOKIE_DOMAIN,
                    )

            if (
                re.match(
                    ".*(Opera|Presto).*", self.request.META.get("HTTP_USER_AGENT", "")
                )
                is not None
            ):
                self.register_stylesheet("/%(context)s/static/css/ext-opera-hack.css")

            params = {
                "DEBUG": settings.DEBUG,
                "CONTEXT": settings.CONTEXT,
                "APPLICATION_TITLE": settings.APPLICATION_TITLE,
                "force_secure": getattr(settings, "FORCE_SECURE", False),
                "js": self.get_session_javascripts(),
                "css": self.get_session_stylesheet(),
                "theme": int(
                    self.request.session.get("theme") or getattr(settings, "THEME", 1)
                ),
                "DEFAULT_THEME": getattr(settings, "THEME", 0),
                "imgs_name_default": self.get_imgs_name_default(),
            }

            self.response = render(self.request, "layout.html", params)

    def get_imgs_name_default(self):
        if settings.DEBUG:
            # favicon_name_default = 'favicon-debug.png'
            # logomarca_name_default = 'logomarca.png'
            sufix_img_name_default = (
                ""
                if settings.ORGAN_IDENTIFIER == "mpto"
                else f"-{settings.ORGAN_IDENTIFIER}"
            )
            favicon_name_default = f"favicon{sufix_img_name_default}.jpg"
            logomarca_name_default = f"logomarca{sufix_img_name_default}.png"
        else:
            sufix_img_name_default = (
                ""
                if settings.ORGAN_IDENTIFIER == "mpto"
                else f"-{settings.ORGAN_IDENTIFIER}"
            )
            favicon_name_default = f"favicon{sufix_img_name_default}.jpg"
            logomarca_name_default = f"logomarca{sufix_img_name_default}.png"

        return {
            "favicon_name_default": favicon_name_default,
            "logomarca_name_default": logomarca_name_default,
        }

    def is_auth(self, args=[]):
        return self.request.user.is_authenticated

    def static(self, args=[]):
        tf = static.__path__[0]

        for arg in args:
            tf = tf + "/" + arg

        buf = self.load_static_file(filename=tf)
        tpl = template.engines["django"].from_string(buf)

        self.response["Content-Type"] = "text/css"
        self.response.write(tpl.render({"context": settings.CONTEXT}))

    def get_session_timeout(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode((settings.TIMEOUT_SESSION + 5) * 1000))

    def can_access(self, leaf):
        return self.can_access_from_model(leaf) or self.can_access_from_explicity(leaf)

    def can_access_from_explicity(self, leaf):
        ctls = []
        for row in self.request.user.controllerpermission_set.all():
            if row.controllers.filter(pk=leaf.pk).exists():
                return True

        return False

    def can_access_from_model(self, leaf):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.controllerpermission_set.filter(
            name=AUDIT_ACCESS_PERFIL
        ):
            return True

        return False

    @login_required(type="JSON")
    def get_leaf_controller(self, args=[]):
        from engine.models import Controller

        obj = {"success": False, "message": "Nada foi feito ainda."}

        action = self.request.POST["action"] if "action" in self.request.POST else None
        uuid = self.request.POST["uuid"] if "uuid" in self.request.POST else None

        try:
            leaf = Controller.objects.get(uuid=uuid)
        except Controller.DoesNotExist:
            obj.update(
                message="""Não foi possivel atender a sua solicitação.
                        A funcionalidade não esta instalada ou apresentou algum defeito.""",
                success=False,
            )
        else:
            if action == "open":
                if self.can_access(leaf):
                    obj.update(controller=f"{leaf.controller}", success=True)
                else:
                    obj.update(
                        message="Este usuário não possui permissão para acessar a aplicação.",
                        success=False,
                    )
            else:
                obj.update(
                    message="Não foi possível identificar uma ação.", success=False
                )

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_leaf_menu(self, root, only_verify=False):
        from engine.models import Controller

        obj = []

        for leaf in Controller.objects.filter(application=root, active=True).order_by(
            "position"
        ):
            if self.can_access(leaf):
                obj.append(
                    {
                        "id": "%d" % (leaf.pk),
                        "text": leaf.title,
                        "cls": (
                            "tree-icon-%s larger-font" % leaf.icon.split(".")[0]
                            if not leaf.icon is None
                            else "folder"
                        ),
                        "leaf": True,
                        "href": "javascript:toolkit.Application.createFormFor('"
                        + leaf.controller
                        + "')",
                        "uuid": leaf.uuid,
                        "uuid_url": f"//{settings.RESOURCE_BASE_URL}/{settings.CONTEXT}/#/open/{leaf.uuid}",
                        "icon_file": str(leaf.icon_file_path()),
                    }
                )

            if only_verify and len(obj) > 0:
                break

        return obj

    def get_root_menu(self, node=None, only_verify=False):
        from engine.models import Application

        obj = []
        result = Application.objects.filter(
            father=None if node == 0 else node, active=True
        )

        group_permission_name = Choice.objects.get(
            app_label="engine", name="GFP_NOME_PERFIL_LIMITE_ACESSO"
        ).label
        feature_group_name = Choice.objects.get(
            app_label="engine", name="GFP_NOME_MENU_LIMITE_ACESSO"
        ).label

        user = User.objects.get(username=self.request.user.username)
        group_permission = user.groups.filter(
            name=group_permission_name
        )  # Gestor de Grupo de Usuário
        feature_group = user.controllerpermission_set.filter(
            name=feature_group_name
        )  # Permissões de Funcionalidades
        audit_permission = user.controllerpermission_set.filter(
            name=AUDIT_ACCESS_PERFIL
        )

        for row in result.order_by("title"):
            if (
                audit_permission
                or row.pk != 19
                or (
                    row.pk == 19
                    and group_permission.exists()
                    and feature_group.exists()
                )
            ):
                item = {
                    "id": str(row.pk),
                    "text": row.title,
                    "cls": (
                        "tree-icon-%s larger-font" % row.icon.split(".")[0]
                        if not row.icon is None
                        else "folder"
                    ),
                }

                if self.request.user.is_superuser:
                    obj.append(item)
                elif audit_permission:
                    obj.append(item)
                elif self.get_leaf_menu(row, only_verify=True) or self.get_root_menu(
                    node=row.pk, only_verify=True
                ):
                    obj.append(item)
                    if only_verify:
                        break

        return obj

    def store_node_cache_object(self, user_id, node_id, menu):
        import json as json_sp

        menu_cache_dir = os.path.join(
            getattr(settings, "CACHE_PATH", "undefined"), "menu", str(user_id)
        )

        if not os.path.exists(menu_cache_dir):
            os.makedirs(menu_cache_dir)

        menu_cache_path = os.path.join(menu_cache_dir, "%d.json" % node_id)
        with open(menu_cache_path, "wt") as fd:
            # fd.write(json.encode(menu))
            json_sp.dump(
                menu, fd, indent=(2 if getattr(settings, "DEBUG", False) else 0)
            )

    def read_node_cache_object(self, user_id, node_id):
        import json as json_sp

        if not self.request.user.is_superuser:
            menu_cache_path = os.path.join(
                getattr(settings, "CACHE_PATH", "undefined"),
                "menu",
                str(user_id),
                "%d.json" % node_id,
            )
            cache_data = None
            log.info('Menu cache path "%s"', menu_cache_path)

            if os.path.exists(menu_cache_path):
                try:
                    with open(menu_cache_path, "rt") as fd:
                        cache_data = json_sp.load(fd)
                except Exception as e:
                    log.exception(e)
                    cache_data = None

            return cache_data
        else:
            return None

    def get_menu(self, args=[]):
        from engine.models import Application

        node_id = int(self.request.POST.get("node") or 0)

        if len(args) > 0 and not node_id:
            node_id = int(args[0] or 0)

        created_cache = False
        obj = self.read_node_cache_object(self.request.user.id, node_id)
        if not obj:
            obj = self.get_root_menu(node_id)
            if node_id > 0:
                root = Application.objects.get(pk=node_id)
                for leaf in self.get_leaf_menu(root):
                    obj.append(leaf)
            created_cache = True
        else:
            log.info(
                "Read cache for %s and node_id %d", self.request.user.username, node_id
            )

        if created_cache:
            self.store_node_cache_object(self.request.user.id, node_id, obj)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def load_menu(self, args=[]):
        from engine.models import Application, Controller

        obj = []
        root = self.request.POST["node"] if "node" in self.request.POST else 0
        query = Application.objects.filter(father=root)
        for row in query:
            obj = obj + [
                {
                    "id": "%d" % (row.id),
                    "text": row.title,
                    "cls": "folde",
                }
            ]

        query = Controller.objects.filter(application=Application.objects.get(pk=root))
        for row in query:
            obj = obj + [
                {
                    "id": "%d" % (row.id),
                    "text": row.title,
                    "cls": "folde",
                    "leaf": True,
                    "href": "javascript:toolkit.Application.create_form_for('"
                    + row.controller
                    + "')",
                }
            ]

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(obj))


class TracTicket(extjs.ExtWidget):

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.widget.TracTicket()")

    @login_required(type="JSON")
    def get_milestone(self, args=[]):
        trac = WSTrac()
        milestone = trac.all_milestones()[-1]

        self.response["content-type"] = "text/plain"
        self.response.write(json.encode(milestone))

    @login_required(type="JSON")
    def get_version(self, args=[]):
        trac = WSTrac()
        version = trac.all_versions()[-1]

        self.response["content-type"] = "text/plain"
        self.response.write(json.encode(version))

    @login_required(type="JSON")
    def create_ticket(self, args=[]):
        obj = {"result": False, "exception": "", "message": ""}

        try:
            trac = WSTrac()
            result, ticket = trac.create_ticket(self.request.POST, self.request.user)
            if result:
                obj["result"] = True
                obj["protocol"] = ticket
            else:
                obj["exception"] = "WSTrac.EXCEPTION"
                obj["message"] = "Erro criando ticket"
        except Exception as e:
            obj["exception"] = str(type(e))
            obj["message"] = str(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class Feed(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.feed.Widget()")


class IGet(extjs.ExtWidget):

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.iget.Widget()")

    @login_required(type="JSON")
    @update_timeout_session(enable=False)
    def refresh(self, args=[]):
        obj = {}

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class UserActive(IGet):
    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.iget.UserActive()")

    @login_required(type="JSON")
    @update_timeout_session(enable=False)
    def refresh(self, args=[]):
        obj = {}
        info = []

        from auditoria.models import LineLog
        from django.db.models import Q, Count
        from datetime import datetime, timedelta

        now = datetime.now()

        delta = timedelta(seconds=(1 * 60))
        info.append(
            {
                "title": "Ultimo min.",
                "count": len(
                    LineLog.objects.filter(
                        Q(dt__range=(now - delta, now)) & ~Q(user=None)
                    )
                    .values("user")
                    .order_by("user")
                    .annotate(Count("user"))
                ),
            }
        )

        delta = timedelta(seconds=(10 * 60))
        info.append(
            {
                "title": "10 min. atrás",
                "count": len(
                    LineLog.objects.filter(
                        Q(dt__range=(now - delta, now)) & ~Q(user=None)
                    )
                    .values("user")
                    .order_by("user")
                    .annotate(Count("user"))
                ),
            }
        )

        delta = timedelta(seconds=(30 * 60))
        info.append(
            {
                "title": "30 min. atrás",
                "count": len(
                    LineLog.objects.filter(
                        Q(dt__range=(now - delta, now)) & ~Q(user=None)
                    )
                    .values("user")
                    .order_by("user")
                    .annotate(Count("user"))
                ),
            }
        )

        delta = timedelta(days=1)
        info.append(
            {
                "title": "1 dia atrás",
                "count": len(
                    LineLog.objects.filter(
                        Q(dt__range=(now - delta, now)) & ~Q(user=None)
                    )
                    .values("user")
                    .order_by("user")
                    .annotate(Count("user"))
                ),
            }
        )

        obj["info"] = info

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class ContactSearch(IGet):

    @login_required(type="JSON")
    def autocomplete(self, args=[]):
        from rh.models import Servidor, Lotacao
        from django.db.models import Q

        # TODO: Realizar tarefa relatada no ticket #184

        obj = {"result": []}

        model = None
        if "model" in self.request.POST:
            if self.request.POST["model"] == "Servidor":
                model = Servidor
            if self.request.POST["model"] == "Lotacao":
                model = Lotacao

        qs = [
            Q(**{cl["name"] + "__icontains": self.request.POST["query"]})
            for cl in model.to_search
            if cl["type"] == "text"
        ]

        q = None
        for qN in qs:
            q = Q(q | qN) if not q is None else qN

        if not model is None:
            for row in model.objects.filter(q):
                obj["result"].append({"pk": row.pk, "description": str(row)})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def search(self, args=[]):
        from rh.models import Servidor, Lotacao, ServidorLotacao

        obj = {"result": [], "totalRows": 0}

        if "type" in self.request.POST:
            if self.request.POST["type"] == "Servidor":
                s = Servidor.objects.get(pk=int(self.request.POST["pk"]))
                collection = s.pessoa_fisica.phone.filter(publico=True)

                obj["totalRows"] = collection.count()

                for fone in collection:
                    obj["result"].append(
                        {
                            "pk": fone.pk,
                            "contact": fone.numero,
                            "type": fone.get_tipo_telefone_display(),
                            "pessoa": str(s.pessoa_fisica),
                        }
                    )

            elif self.request.POST["type"] == "Lotacao":
                slts = Lotacao.objects.get(
                    pk=int(self.request.POST["pk"])
                ).employee_exercise

                for slt in slts:
                    s = slt.servidor
                    for fone in s.pessoa_fisica.phone.filter(publico=True):
                        obj["result"].append(
                            {
                                "pk": fone.pk,
                                "contact": fone.numero.replace("-", ""),
                                "type": fone.get_tipo_telefone_display(),
                                "pessoa": str(s.pessoa_fisica),
                            }
                        )

                l = Lotacao.objects.get(pk=int(self.request.POST["pk"]))
                for fone in l.phone.filter(publico=True):
                    obj["result"].append(
                        {
                            "pk": fone.pk,
                            "contact": fone.numero.replace("-", ""),
                            "type": fone.get_tipo_telefone_display(),
                            "pessoa": str(l),
                        }
                    )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.iget.ContactSearch()")


class UserInformation(IGet):

    @login_required(type="JSON")
    def update_donor(self, args=None):
        args = args or []

        result = {
            "success": False,
            "message": "Nothing done yet",
        }

        try:
            if self.request.method != "PUT":
                self.response.status_code = 405
                raise Exception("Verbo HTTP incorreto")

            params = QueryDict(self.request.body)
            employee = self.request.user.servidor
            is_donor = params.get("isDonor", "off") == "on"
            if is_donor != employee.pessoa_fisica.doador:
                employee.pessoa_fisica.doador = is_donor
                employee.pessoa_fisica.save()
        except Exception as e:
            log.exception(str(e))
            result.update({"message": str(e)})
        else:
            result.update(
                {
                    "success": True,
                    "message": "Operação realizada com sucesso!",
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.iget.UserInformation()")

    # _TODEL_ A funcionalidade "Atualização de telefones" foi implementada no novo Dashboard utilizando o código Restful existente do modelo Telefone.
    @login_required(type="JSON")
    def add_fone(self, args=[]):
        from rh.models import Telefone

        obj = {"success": False, "msg": "Nada foi feito ainda"}

        try:
            servidor = self.request.user.servidor

            tel = Telefone(
                tipo_telefone=self.request.POST["tipo_telefone"],
                numero=self.request.POST["numero"],
                publico=(
                    self.request.POST["publico"] == "on"
                    if "publico" in self.request.POST
                    else False
                ),
                person=servidor.pessoa_fisica.pessoa_ptr,
            )

            tel.save()

            obj["success"] = True
        except:
            pass

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def edit_fone(self, args=[]):
        from rh.models import Telefone

        obj = {"success": False, "msg": "Nada foi feito ainda"}

        try:
            servidor = self.request.user.servidor

            tel = servidor.pessoa_fisica.phone.get(pk=self.request.POST["pk"])
            tel.tipo_telefone = self.request.POST["tipo_telefone"]
            tel.publico = (
                self.request.POST["publico"] == "on"
                if "publico" in self.request.POST
                else False
            )
            tel.numero = self.request.POST["numero"]

            tel.save()

            obj["success"] = True
        except:
            pass

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def delete_fone(self, args=[]):
        from rh.models import Telefone

        obj = {"success": False, "msg": "Nada foi feito ainda"}

        try:
            servidor = self.request.user.servidor

            tel = servidor.pessoa_fisica.phone.get(pk=self.request.POST["pk"])
            tel.delete()

            obj["success"] = True
        except Exception as e:
            obj["msg"] = e

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def myfones(self, args=[]):
        obj = {"root": [], "totalRows": 0}

        servidor = self.request.user.servidor
        obj["totalRows"] = servidor.pessoa_fisica.phone.all().count()
        for fone in servidor.pessoa_fisica.phone.all():
            obj["root"].append(
                {
                    "pk": fone.pk,
                    "numero": fone.numero,
                    "tipo": fone.get_tipo_telefone_display(),
                    "tipo_telefone": fone.tipo_telefone,
                    "publico": fone.publico,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    @update_timeout_session(enable=False)
    def refresh(self, args=[]):
        from rh.models import MovimentacaoPosse

        default = {
            "message": "Nothing done yet",
            "success": False,
            "username": str(self.request.user),
            "nome": None,
            "mail": None,
            "matricula": None,
            "lotacao": None,
            "cargo": None,
            "funcao": None,
            "tsangue": None,
            "dorgao": None,
            "natural": None,
            "ecivil": None,
            "ramais": None,
            "dataReferenciaFerias": None,
            "foto": "/athenas/static/images/photo-placeholder-85x113.png",
        }
        result = default.copy()

        try:
            employee = employee_from_user(self.request.user)

            result["nome"] = employee.pessoa_fisica.nome
            result["mail"] = employee.user.email
            result["ecivil"] = employee.pessoa_fisica.get_estado_civil_display()
            result["natural"] = str(employee.pessoa_fisica.municipio_naturalidade)
            result["matricula"] = employee.matricula
            result["dorgao"] = employee.pessoa_fisica.doador and "SIM" or "NÃO"

            result["tsangue"] = "{0}{1}".format(
                employee.pessoa_fisica.get_sangue_display(),
                "-" if employee.pessoa_fisica.fator_rh == 1 else "+",
            )

            if employee.pessoa_fisica.foto:
                result["foto"] = employee.pessoa_fisica.foto.resizelink((85, 113))

            result["lotacao"] = [
                str(workplace) for workplace in employee.work_locations
            ]

            result["cargo"] = []
            for mp in MovimentacaoPosse.objects.filter(servidor=employee, ativo=True):
                if mp.quadro:
                    if (
                        mp.quadro.cargo.tipo_lei_cargo == "CM"
                        or mp.quadro.cargo.tipo_lei_cargo == "EF"
                    ):
                        result["cargo"].append(str(mp.quadro.cargo))
                    else:
                        result["funcao"] = str(mp.quadro.cargo)
                else:
                    result["cargo"].append(str(mp.description_possession))

            result["ramais"] = []
            for phone in employee.pessoa_fisica.phone.all():
                result["ramais"].append(phone.get_number_formated())

            result["dataReferenciaFerias"] = ""
            if employee.data_referencia_ferias:
                result["dataReferenciaFerias"] = (
                    employee.data_referencia_ferias.strftime("%d/%m")
                )

            result["message"] = "Operação realizada com sucesso"
            result["success"] = True
        except Exception as e:
            self.log.exception(e)
            result = default.copy()
            result.update(message=str(e))

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(result))


class ServerInformation(IGet):

    @login_required(type="JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.iget.ServerInformation()")

    def _format_bytes(self, num):
        uns = ("KB", "MB", "GB", "TB")
        un = 0

        while un < len(uns) and num > 1024.00:
            un += 1
            num = num / 1024.00

        return "{0} {1}".format(round(num, 2), uns[un])

    @login_required(type="JSON")
    @update_timeout_session(enable=False)
    def refresh(self, args=[]):
        import socket

        obj = {
            "hostname": "&nbsp;",
            "ip": "&nbsp;",
            "mem_phy": "&nbsp;",
            "mem_unused": "&nbsp;",
            "mem_cache": "&nbsp;",
            "mem_swap": "&nbsp;",
            "hostname": "&nbsp;",
        }

        obj["hostname"] = socket.gethostname()
        obj["ip"] = socket.gethostbyname(obj["hostname"])

        fd = open("/proc/meminfo")
        for line in fd.readlines():
            if line.find("MemTotal") == 0:
                p = line.split(":")
                obj["mem_phy"] = self._format_bytes(float(p[1].replace(" ", "")[0:-3]))
            if line.find("Cached") == 0:
                p = line.split(":")
                obj["mem_cache"] = self._format_bytes(
                    float(p[1].replace(" ", "")[0:-3])
                )
            if line.find("MemFree") == 0:
                p = line.split(":")
                obj["mem_unused"] = self._format_bytes(
                    float(p[1].replace(" ", "")[0:-3])
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
