# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes:

:Classes:
   :class:`WSSecurity`.

"""

from auth.ws import models
from django.contrib import auth
from contrib.extjs import ExtWidget
from contrib.decorator import is_public

from contrib.utils import get_json_engine

json = get_json_engine()


class WSSecurity(ExtWidget):
    """
    **Classe** para gerenciamento de permissões e acessos aos serviços do Athenas.

    :Métodos:
        :func:`authorize`,
        :func:`login`.
    """

    @is_public()
    def login(self, args=[]):
        """Método para autenticar usuarios junto ao athenas.

        :param args: Lista de parâmetros recebidos pela requisição cliente.
        :type args: Array

        :returns:  Object -- Objeto do tipo JSON contendo o status da autenticação.

        >>> print login({'app_key': '123', 'user_key': '456'})
        {
            'success': True,
            'message': 'Usuário autenticado',
            'user_name': 'athenas_user'
        }
        """

        # Recupera parametros para autenticacao
        user_key = self.request.POST.get("user_key") or None
        app_key = self.request.POST.get("app_key") or None

        # Inicializa conteúdo das respostas aos clientes
        obj = {
            "success": False,
            "message": "",
            "app_key": app_key,
            "user_key": user_key,
            "user_name": None,
        }

        # Usuario legítimo e autenticado
        user = auth.authenticate(username=app_key, password=user_key)
        if user is not None and user.is_active:

            # Loga cliente junto ao athenas
            auth.login(self.request, user)
            obj.update(success=True)
            obj.update(user_name=user.username)
            obj.update(message="Usuário autenticado:")

        # Usuario inválido
        else:
            obj.update(message="Nome de usuário ou senha inválido(s).")

        # Retorna resposta para o cliente em formato json
        self.response["Content-Type"] = "text/javascript"

        # Configura respostas para requisicoes cross domain
        if "callback" in self.request.POST:
            self.response.write(
                "%s(%s)" % (self.request.POST.get("callback"), json.encode(obj))
            )
        else:
            self.response.write(json.encode(obj))

    # Metodo para gerar user_key para usuarios
    @is_public()
    def authorize(self, args=[]):
        """Método para gerar chaves de autorização (user_key) para usuarios.

        :param args: Lista de parâmetros recebidos pela requisição.
        :type args: Array

        :returns:  Object -- Objeto do tipo JSON contendo o status da autorização.
        :raises: Application.DoesNotExist.

        >>> print authorize({'app_key': '123', 'username': 'athenas_user', 'password': 'passwd'})
        {
            'success': True,
            'message': 'Aplicativo autorizado',
            'user_key': '456'
        }
        """

        # Recupera parametros para autorizacao
        app_key = self.request.POST.get("app_key") or None

        # Inicializa conteúdo das respostas aos clientes
        obj = {
            "success": False,
            "message": "",
            "app_key": app_key,
            "user_key": None,
            "user_name": None,
        }

        # Busca token da aplicacao na base
        try:
            app = models.Application.objects.get(app_key=app_key)
        except models.Application.DoesNotExist:
            app = None

        # Verifica a existencia ou nao do token
        if app is not None:

            # Autentica usuário
            username = self.request.POST.get("username", "")
            password = self.request.POST.get("password", "")
            user = auth.authenticate(username=username, password=password)

            # Usuario legítimo e autenticado
            if user is not None and user.is_active:

                # Verifica se ja existe user_key para o usuario
                try:
                    permission = models.UserPermission.objects.get(user=user)

                # Gera user_key e a retorna para o cliente
                except models.UserPermission.DoesNotExist:
                    permission = models.UserPermission(user=user, application=app)
                    permission.save()

                # Retorna user_key para o cliente
                obj.update(success=True)
                obj.update(user_name=user.username)
                obj.update(user_key=permission.user_token)
                obj.update(message="Aplicativo autorizado:")

                auth.login(self.request, user)

            # Usuario inválido
            else:
                obj.update(message="Nome de usuário ou senha inválido(s).")

        # app_key nao encontrada na base
        else:
            obj.update(message="Acesso negado, aplicativo não autorizado:")

        # Retorna resposta para o cliente em formato json
        self.response["Content-Type"] = "text/javascript"

        # Configura respostas para requisicoes cross domain
        if "callback" in self.request.POST:
            self.response.write(
                "%s(%s)" % (self.request.POST.get("callback"), json.encode(obj))
            )
        else:
            self.response.write(json.encode(obj))

    @is_public()
    def is_authenticated(self, args=[]):
        # self.response.write(json.encode(self.request.user.is_authenticated))
        self.render(self.request.user.is_authenticated)
