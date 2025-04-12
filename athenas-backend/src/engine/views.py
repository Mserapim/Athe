# -*- coding: utf-8 -*-
from auditoria.models import LineLog
from django import forms
from django.contrib.auth.models import Permission, User, Group
from django.forms.models import ModelChoiceField
from django.conf import *
from standard.views import AutoCompleteField
from contrib import extjs
from engine import models
from contrib.decorator import install_view, tab, login_required
from contrib.utils import employee_from_user

try:
    from smbpasswd import lmhash, nthash
except:
    pass

from time import time
from engine import forms as engineforms

from contrib.utils import get_json_engine

json = get_json_engine()


class ENGControllerContentType(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.ControllerContentType

    titles = {
        "PANEL": "Funcionalidades e Entidades",
        "LIST": "Funcionalidades e Entidades",
        "NEW": "Novo Funcionalidades e Entidades",
        "EDIT": "Editando uma Funcionalidades e Entidades",
        "DELETE": "Deletando uma Funcionalidades e Entidades",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@install_view(menu="sub2", title="Grupos", install=True)
class AUTHGroup(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Group

    titles = {
        "PANEL": "Grupos",
        "LIST": "Gerenciador de Grupos",
        "NEW": "Novo Grupo",
        "EDIT": "Editando um Grupo",
        "DELETE": "Deletando um Grupo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "name",
                "key": "name",
                "width": 240,
            },
        ]

        obj = self._apply_to_search_for_columns_grid(obj)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class AUTHPermission(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Permission

    titles = {
        "PANEL": "Permissões",
        "LIST": "Gerenciador de Permissões",
        "NEW": "Nova",
        "EDIT": "Editando",
        "DELETE": "Deletando",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Identificação",
            "field": ["username", "password", "first_name", "last_name", "email"],
        },
        {"title": "Configuração", "field": ["is_staff", "is_active", "is_superuser"]},
        {"title": "Grupos", "field": ["groups"]},
        {"title": "Permissões", "field": ["user_permissions"]},
    ]
)
class AUTHUser(extjs.ExtCrud):

    class Form(forms.ModelForm):
        password = forms.CharField(label="Senha", widget=forms.PasswordInput)

        class Meta:
            exclude = []
            model = User
            exclude = ("date_joined", "last_login")

    titles = {
        "PANEL": "Usuários",
        "LIST": "Gerenciador de Usuários",
        "NEW": "Novo Usuário",
        "EDIT": "Editando um Usuários",
        "DELETE": "Deletando um Usuários",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def has_servidor(self, args=[]):
        obj = {"result": True}

        if self.request.user.is_staff:
            employee = employee_from_user(self.request.user, only_active=False)
            if not employee or not employee.ativo and not employee.aposentado:
                obj.update(result=False)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def need_change_password(self, args=[]):
        obj = {"result": False}

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Usuário",
                "sortable": True,
                "dataIndex": "username",
                "key": "username",
                "width": 200,
            },
            {
                "header": "Primeiro Nome",
                "sortable": True,
                "dataIndex": "first_name",
                "key": "first_name",
                "width": 180,
            },
            {
                "header": "Último Nome",
                "sortable": True,
                "dataIndex": "last_name",
                "key": "last_name",
                "width": 240,
            },
            {
                "header": "Membro da Equipe",
                "sortable": True,
                "dataIndex": "is_staff",
                "key": "is_staff",
                "width": 130,
            },
            {
                "header": "Status de Superusuário",
                "sortable": True,
                "dataIndex": "is_superuser",
                "key": "is_superuser",
                "width": 170,
            },
            {
                "header": "Endereço de E-mail",
                "sortable": True,
                "dataIndex": "email",
                "key": "email",
                "width": 240,
            },
            {
                "header": "Data de Registro",
                "sortable": True,
                "dataIndex": "date_joined",
                "key": "date_joined",
                "width": 130,
            },
            {
                "header": "Grupos",
                "sortable": True,
                "dataIndex": "groups",
                "key": "groups",
                "width": 180,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "is_active",
                "key": "is_active",
                "width": 70,
            },
            {
                "header": "Último Login",
                "sortable": True,
                "dataIndex": "last_login",
                "key": "last_login",
                "width": 130,
            },
            {
                "header": "Permissões do Usuário",
                "sortable": True,
                "dataIndex": "user_permissions",
                "key": "user_permissions",
                "width": 240,
            },
        ]

        obj = self._apply_to_search_for_columns_grid(obj)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@install_view(menu="sub1", title="Grupo de funcionalidades", install=True)
class ENGApplication(extjs.ExtCrud):

    class Form(forms.ModelForm):
        icon = engineforms.IconField(required=False, label="Icone")
        father = AutoCompleteField(
            model=models.Application, required=False, label="Aplicativo"
        )

        class Meta:
            exclude = []
            model = models.Application

    titles = {
        "PANEL": "Grupo de Funcionalidades",
        "LIST": "Grupos de Funcionalidades",
        "NEW": "Novo grupo de funcionalidade",
        "EDIT": "Editando um grupo de funcionalidade",
        "DELETE": "Deletando um grupo de funcionalidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Ativo",
                "sortable": True,
                "dataIndex": "active",
                "key": "active",
                "width": 70,
            },
            {
                "header": "Grupo de Funcionalidade",
                "sortable": True,
                "dataIndex": "father",
                "key": "father",
                "width": 240,
            },
            {
                "header": "Título",
                "sortable": True,
                "dataIndex": "title",
                "key": "title",
                "width": 240,
            },
        ]

        obj = self._apply_to_search_for_columns_grid(obj)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


@install_view(menu="sub1", title="Funcionalidades", install=True)
class ENGController(extjs.ExtCrud):

    class Form(forms.ModelForm):
        icon = engineforms.IconField(required=False, label="Icone")
        application = AutoCompleteField(model=models.Application, label="Aplicativo")

        class Meta:
            exclude = []
            model = models.Controller

    titles = {
        "PANEL": "Cadastro de funcionalidade",
        "LIST": "Gerenciador de Funcionalidades",
        "NEW": "Nova funcionalidade",
        "EDIT": "Editando uma funcionalidade",
        "DELETE": "Deletando uma funcionalidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Grupo de Funcionalidade",
                "sortable": True,
                "dataIndex": "application",
                "key": "application",
                "width": 320,
            },
            {
                "header": "Controlador",
                "sortable": True,
                "dataIndex": "controller",
                "key": "controller",
                "width": 240,
            },
            {
                "header": "Título",
                "sortable": True,
                "dataIndex": "title",
                "key": "title",
                "width": 240,
            },
        ]

        obj = self._apply_to_search_for_columns_grid(obj)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class ENGControllerPermission(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = models.ControllerPermission

    titles = {
        "PANEL": "Permissão para Funcionaliades",
        "LIST": "Permissão para Funcionaliades",
        "NEW": "Nova permissão de funcionalidade",
        "EDIT": "Editando uma permissão de funcionalidade",
        "DELETE": "Deletando uma permissão de funcionalidade",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Nome",
                "sortable": True,
                "dataIndex": "name",
                "key": "name",
                "width": 240,
            },
        ]
        self.response.write(json.encode(obj))


try:
    import ldap
except:

    class AUTHProfile(extjs.ExtWidget):
        @login_required(type="JSON")
        def json(self, args=[]):
            if not self.request.user is None:
                self.response.write(
                    "new toolkit.widget.auth.Profile({0})".format(self.request.user.pk)
                )
            else:
                self.response.write("new toolkit.widget.Exception('test')")

        @login_required(type="JSON")
        def get_user_information(self, args=[]):
            obj = {}

            user = self.request.user

            obj["first_name"] = user.first_name
            obj["last_name"] = user.last_name
            obj["email"] = user.email

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))

        @login_required(type="JSON")
        def change_user_information(self, args=[]):
            result = {"status": False, "message": ""}

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(result))

        @login_required(type="JSON")
        def change_password(self, args=[]):
            obj = {"result": False}

            self.response.write(json.encode(obj))

else:
    from auth.backend import *

    class AUTHProfile(extjs.ExtWidget):

        @login_required(type="JSON")
        def json(self, args=[]):
            if not self.request.user is None:
                self.response.write(
                    "new toolkit.widget.auth.Profile({0})".format(self.request.user.pk)
                )
            else:
                self.response.write("new toolkit.widget.Exception('test')")

        @login_required(type="JSON")
        def update_ldap(self, uri, filter, password, new_password):
            ldap_con = ldap.initialize(uri)
            ldap_con.set_option(ldap.OPT_TIMEOUT, 30)

            try:
                ldap_con.bind_s(filter, password.encode("utf-8"))

                new_password = new_password.encode("utf-8")
                digest = hashlib.new("md5", new_password).digest()

                utime = int((str(time())).split(".")[0])
                mods = [
                    (
                        ldap.MOD_REPLACE,
                        "userPassword",
                        "{MD5}%s" % base64.b64encode(digest),
                    ),
                    (ldap.MOD_REPLACE, "sambaLMPassword", lmhash(new_password)),
                    (
                        ldap.MOD_REPLACE,
                        "sambaNTPassword",
                        nthash(new_password.decode("utf-8")),
                    ),
                    (ldap.MOD_REPLACE, "sambaPwdLastSet", str(utime)),
                    (ldap.MOD_REPLACE, "shadowLastChange", str(utime / (60 * 60 * 24))),
                ]

                try:
                    ldap_con.modify_s(filter, mods)
                    return True, "Senha alterada com exito."
                except:
                    return False, "Não foi possível modificar a senha."
            except ldap.INVALID_CREDENTIALS:
                return False, "Pedido de mudança de senha negado."
            except Exception as e:
                self.log.exception(e)
                return False, "Ocorreu um erro modificando a senha."

        @login_required(type="JSON")
        def get_user_information(self, args=[]):
            obj = {}

            user = self.request.user

            obj["first_name"] = user.first_name
            obj["last_name"] = user.last_name
            obj["email"] = user.email

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))

        @login_required(type="JSON")
        def change_user_information(self, args=[]):
            result = {"status": False, "message": ""}

            linelog = LineLog()
            linelog.read_request(self.request)
            linelog.status = 1
            linelog.level = 5

            try:
                bl = LDAPBalancer()
                host = bl.next()

                log.info("LDAP: %s", host)

                cfg = bl.get_configuration(host)
            except Exception as e:
                cfg = settings.LDAP_AUTH

            try:
                user = self.request.user

                cn = "{0}={1},{2}".format(
                    cfg["user_object"], user.username, cfg["basedn"]
                )

                result["message"] = cn

                l = ldap.initialize(cfg["uri"])

                try:
                    l.bind_s(cn, self.request.POST["credencial"])
                    user.first_name = self.request.POST["first_name"]
                    user.last_name = self.request.POST["last_name"]
                    user.email = self.request.POST["email"]

                    user.save()

                    mods = [
                        (
                            ldap.MOD_REPLACE,
                            "displayName",
                            "{0} {1}".format(str(user.first_name), str(user.last_name)),
                        ),
                        (
                            ldap.MOD_REPLACE,
                            "gecos",
                            "{0} {1}".format(str(user.first_name), str(user.last_name)),
                        ),
                    ]

                    self.log.debug(mods)

                    try:
                        l.modify_s(cn, mods)
                        result["message"] = "Dados alterados com exito."
                        result["status"] = True
                    except TypeError as e:
                        self.log.exception(e)
                        linelog.status = 0
                        result["message"] = (
                            "Não foi possível modificar os dados.\n\nDescrição:\n{0}".format(
                                "test"
                            )
                        )
                    except Exception as e:
                        linelog.status = 0
                        self.log.exception(e)
                        result["message"] = (
                            "Não foi possível modificar os dados.\n\nDescrição:\n{0}".format(
                                type(e)
                            )
                        )
                except ldap.SERVER_DOWN as e:
                    linelog.status = 0
                    result["message"] = "Erro conectando com servidor LDAP."
                except ldap.INVALID_CREDENTIALS:
                    linelog.status = 0
                    result["message"] = "Senha inválida, autorização negada."
                except Exception as e:
                    self.log.exception(e)
                    linelog.status = 0
                    result["message"] = "Erro autênticando."

            except Exception as e:
                linelog.status = 0
                result["message"] = "Erro adequeirindo informações.\n{0}\n{1}".format(
                    str(e), cfg["uri"]
                )

            linelog.json_description["message"] = result["message"]
            linelog.save()

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(result))

        @login_required(type="JSON")
        def change_password(self, args=[]):
            obj = {"result": False}

            POST = self.request.POST
            linelog = LineLog()
            linelog.read_request(self.request)
            linelog.status = 1
            linelog.level = 3

            user = User.objects.get(pk=int(POST["user_id"]))
            if not user is None:
                self.log.debug("Usuario encontrado")

                try:
                    bl = LDAPBalancer()
                    host = bl.next()

                    cfg = bl.get_configuration(host)
                except:
                    linelog.status = 0
                    obj["message"] = "Senha antiga não confere"
                    cfg = settings.LDAP_AUTH

                filter = "{0}={1},{2}".format(
                    cfg["user_object"], user.username, cfg["basedn"]
                )

                self.log.debug(cfg["uri"])
                l_user, obj["message"] = self.update_ldap(
                    cfg["uri"], filter, POST["senha_antiga"], POST["senha_nova"]
                )

                obj["result"] = l_user
                if not l_user:
                    linelog.status = 0
            else:
                linelog.status = 0
                obj["message"] = "Usuario nao encontrado"

            if (
                "senha_antiga" in self.request.POST
                or "senha_nova" in self.request.POST
                or "senha_confirma" in self.request.POST
            ):
                linelog.json_description["post"]["senha_antiga"] = "***"
                linelog.json_description["post"]["senha_nova"] = "***"
                linelog.json_description["post"]["senha_confirma"] = "***"
            if (
                "senha_antiga" in self.request.GET
                or "senha_nova" in self.request.GET
                or "senha_confirma" in self.request.GET
            ):
                linelog.json_description["get"]["senha_antiga"] = "***"
                linelog.json_description["get"]["senha_nova"] = "***"
                linelog.json_description["get"]["senha_confirma"] = "***"

            linelog.json_description["message"] = obj["message"]
            linelog.save()

            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))
