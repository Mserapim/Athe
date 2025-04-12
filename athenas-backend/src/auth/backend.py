# -*- coding: utf-8 -*-
import base64
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import exceptions
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from engine.models import LDAPServer
from contrib.utils import getLogger
from contrib.helpers import DynaObject
from django.contrib.auth import backends
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from auth.sso.crowd import CrowdServer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
from auditlog.middleware import AuditlogMiddleware

import os
import ldap
import random
import jwt


log = getLogger(__name__)


class Balancer(object):

    def __init__(self):
        self.log = getLogger(self.__class__.__name__)

    def next(self):
        """
        Metodo responsável por selecionar um novo servidor.
        :return Retorna um modelo de host
        """

    def set_falt(self, host):
        """
        Metodo responsável por definir um host como em falta.
        :param host Host para ser setado como em falta.
        """

    def get_configuration(self, host):
        """
        Metodo responsável por transformar um host em uma configuração.
        :param host Host para ser utilizado na configuração
        """


class LDAPBalancer(Balancer):

    def next(self):
        ldaps = LDAPServer.objects.filter(falt=False)
        result = None

        sum = 0
        for l in ldaps:
            sum += l.priority

        random.seed(hash(os.urandom(5)))
        rnd = random.randint(0, sum)

        for l in ldaps:
            rnd -= l.priority
            if rnd <= 0:
                result = l
                break

        if result:
            return result
        else:
            return ldaps[-1]

    def set_fault(self, host):
        host.falt = True
        host.save()

    def get_configuration(self, host):
        return {
            "uri": str(host),
            "dn": host.dn,
            "basedn": host.basedn,
            "admin": {"user": host.admin_user, "passwd": host.admin_password},
            "user_object": host.user_object,
            "nologin": ".",
            "db_user_autocreate": False,
            "domain_mail": "mp.to.gov.br",
        }


class LDAPBackend(backends.ModelBackend):
    """
    Backend para autenticação Web com LDAP.
    """

    def __init__(self):
        super(LDAPBackend, self).__init__()
        self.log = getLogger(LDAPBackend.__name__)

    def authenticate(self, request, username=None, password=None):
        """
        Sobrescreve o metodo de autenciação do MOdelBackend fazendo autênticar no LDAP.
        :param username Nome do usuários.
        :param password Senha do usuários.
        :return Retorna uma entidade User caso tenha conseguido autênticar.
        """
        host = None

        try:
            try:
                bl = LDAPBalancer()
                host = bl.next()

                cfg = bl.get_configuration(host)
            except Exception as e:
                self.log.exception(e)
                cfg = getattr(settings, "LDAP_AUTH", {})
                host = DynaObject()
                host.tls = cfg["tls"]
                host.save = lambda: None

            uri = cfg["uri"]

            self.log.info("Usando o servidor ({0}).".format(uri))

            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            ldap_con = ldap.initialize(uri)
            if host.tls:
                ldap_con.set_option(ldap.OPT_REFERRALS, 0)
                ldap_con.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
                ldap_con.set_option(ldap.OPT_X_TLS, ldap.OPT_X_TLS_DEMAND)
                ldap_con.set_option(ldap.OPT_X_TLS_DEMAND, True)

            ldap_con.set_option(ldap.OPT_TIMEOUT, 30)
            if username and password:
                username = username.lower().replace(" ", "")
                ldap_bind = "%s=%s,%s" % (cfg["user_object"], username, cfg["basedn"])

                if cfg["binddn_use_domain"]:
                    ldap_bind = f"{username}@{cfg['domain_mail']}"

                self.log.info("dn: %s" % ldap_bind)
                ldap_con.bind_s(ldap_bind, password.encode("utf-8"))
                self.log.info("Usuário autenticado com sucesso!!!")
                try:
                    user = models.User.objects.get(username=username)
                except models.User.DoesNotExist:
                    if cfg["db_user_autocreate"]:
                        user = models.User.objects.create_user(
                            username=username, email=username + "@" + cfg["domain_mail"]
                        )
                        user.is_staff = True
                        user.set_password(os.urandom(12))
                        user.save()
                        self.log.info("Usuário criado no banco de dados!!!")
                    else:
                        user = User()
                return user
        except ldap.INVALID_CREDENTIALS as e:
            self.log.debug("LDAP Bind: %s", ldap_bind)
            self.log.exception(e)
            return None
        except ldap.SERVER_DOWN as e:
            self.log.exception(e)
            if host:
                host.falt = True
                host.save()
            return None
        except Exception as exc:
            LDAPBackend.status = str(exc)
            self.log.exception(exc)
            self.log.debug(ldap)
            return None

    def get_user(self, user_id):
        """
        Metodo responsável por retorna um usuário de acordo com seu user_id.
        :param user_id Identificador do usuário.
        :return Caso consegui encontrar o usuário retorna, caso contrario retorna None.
        """
        try:
            user = models.User.objects.get(pk=user_id)
            # self.log.info("LDAPBackend: Usuario com id {0} encontrado.".format(user_id))
            return user
        except User.DoesNotExist:
            self.log.critical("LDAPBackend: Usuário não existe na base de dados.")
            return None


class CustomJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        """
        Autentica uma solicitação de usuário por token Crowd e username

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário autenticado
        """
        if settings.ATHENAS_ENV == "dev":
            return self.autenticacao_dev(request)
        return self.autenticacao_crowd(request)

    def autenticacao_crowd(self, request):
        """
        Autentica uma solicitação de usuário por token Crowd

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário autenticado
        """
        token = self.get_token(request)
        if token is None:
            return None
        remote = self.get_remote(request)
        validado_token = self.get_validated_token(token, remote)
        usuario = self.get_user(validado_token), None
        # self.add_usuario_auditoria(request,usuario)
        return usuario

    def autenticacao_dev(self, request):
        """
        Autentica uma solicitação de usuário por token Crowd ou username

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário autenticado
        """
        usuario = request.headers.get("username", None)
        if usuario:
            validado_token = {"user": {"name": usuario}}
            usuario = self.get_user(validado_token), None
            # self.add_usuario_auditoria(request,usuario)
            return usuario
        else:
            return self.autenticacao_crowd(request)

    def get_validated_token(self, raw_token, remote):
        """
        Valida se o token crowd é válido
        """
        result = None
        crowd = CrowdServer(
            settings.CROWD_SERVER_NAME,
            settings.CROWD_APP_NAME,
            settings.CROWD_APP_PASSWD,
        )
        if settings.ATHENAS_ENV in ["dev"]:
            ips = settings.IPS_AUTH_DEV
            for ip in ips:
                try:
                    result = crowd.validate_session(raw_token, ip)
                    if result:
                        break
                except:
                    pass
        else:
            result = crowd.validate_session(raw_token, remote)
        return result

    def get_token(self, request):
        return request.COOKIES.get(settings.CROWD_SESSION_NAME, None)

    # def add_usuario_auditoria(self,request,usuario):
    #     """
    #     Adiciona o usuário autenticado na auditoria de logs AuditlogMiddleware

    #     - param request: Uma instância da solicitação HTTP.
    #     - param user: usuário autenticado.
    #     """
    #     if usuario:
    #         request.user = usuario[0]
    #         AuditlogMiddleware().process_request(request)

    def get_remote(self, request):
        remote = None
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            remote = forwarded.split(",")[0].strip()
        else:
            remote = request.META.get("REMOTE_ADDR")

        return remote

    def get_user(self, validated_token):
        """
        Tenta localizar e retornar um usuário usando o token validado fornecido.
        """
        user = None
        if validated_token:
            try:
                username = validated_token["user"]["name"]
                user = User.objects.get(username=username)
            except self.user_model.DoesNotExist:
                raise AuthenticationFailed(
                    ("Usuário não encontrado"), code="user_not_found"
                )
            if not user.is_active:
                raise AuthenticationFailed(("Usuário inativo"), code="user_inactive")
        else:
            raise AuthenticationFailed(
                ("O token é inválido ou expirado."), code="token_invalid"
            )

        return user


class CustomTokenJWTAuthentication(JWTAuthentication):
    """
    classe específica para autenticação por token JWT
    """

    def authenticate(self, request):
        """
        Autentica uma solicitação de usuário por token Bearer

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário autenticado
        """
        token = self.get_token(request)
        if token is None:
            return None
        validated_token = self.get_validated_token(token)

        return self.get_user(validated_token, request=request), None

    def get_token(self, request):
        data = request.headers.get("authorization", "")
        token = str.replace(str(data), "Bearer ", "")
        return token

    def get_validated_token(self, raw_token):
        """
        Valida se o token jwt é válido
        """
        try:
            result = jwt.decode(
                raw_token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
            )
        except:
            raise AuthenticationFailed(
                "Token inválido ou expirado.", code="token_invalid"
            )
        if result:
            return result
        return False

    def get_user(self, validated_token, request=None):
        """
        Tenta localizar e retornar um usuário usando o token validado fornecido.
        """
        user = None
        if validated_token:
            try:
                if validated_token.get("cpf", False):
                    user = User.objects.filter(
                        servidor__pessoa_fisica__cpf=request.data.get("cpf")
                    ).last()
                else:
                    user = User.objects.get(username=validated_token.get("username"))
            except self.user_model.DoesNotExist:
                raise AuthenticationFailed(
                    ("Usuário não encontrado"), code="user_not_found"
                )
            if not user.is_active:
                raise AuthenticationFailed(("Usuário inativo"), code="user_inactive")
        else:
            raise AuthenticationFailed(
                ("Token inválido ou expirado."), code="token_invalid"
            )

        return user


class MultiAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Autentica uma solicitação de usuário por token Bearer ou Crowd

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário autenticado
        """
        token = request.headers.get("authorization", "")
        if token.startswith("Bearer "):
            return CustomTokenJWTAuthentication().authenticate(request)
        else:
            return CustomJWTAuthentication().authenticate(request)


class ExternalJWTAuthentication(BaseAuthentication):

    @staticmethod
    def create_access_token(data: dict, expires_delta_minutes: int = None):
        """
        Cria um JSON Web Token (JWT) codificado com os dados e tempo de expiração especificados.

        - param data: Um dicionário contendo os dados a serem codificados no JWT.
        - param expires_delta_minutes: Um timedelta especificando o tempo de expiração para o JWT.
            Se não for fornecido, o tempo de expiração padrão é usado.
        - return: Uma string representando o JWT codificado.
        """
        access_token_payload = {}
        access_token_payload.update(data)
        if expires_delta_minutes:
            expire = datetime.utcnow() + timedelta(minutes=expires_delta_minutes)
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        access_token_payload.update({"exp": expire})
        token = jwt.encode(
            access_token_payload, settings.JWT_SECRET_KEY, algorithm="HS256"
        )
        return str(token)

    @staticmethod
    def decode_token(token: str):
        """
        Decodifica o token JWT fornecido e retorna o usuário associado.

        - param token: O token JWT para decodificar.
        - return: A instância do usuário associada ao token.
        - raises rest_framework.exceptions.AuthenticationFailed: Se o token for inválido ou não conter um usuário.
        """
        try:
            access_token = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=["HS256"]
            )
            user_id = access_token.get("user")
            user = User.objects.get(pk=user_id)
            if not user:
                raise exceptions.AuthenticationFailed(
                    _("Invalid token: Non valid user or password.")
                )

            return user
        except (InvalidToken, TokenError):
            raise exceptions.AuthenticationFailed(_("Invalid token."))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

    @staticmethod
    def authenticate_credentials(username: str, password: str):
        """
        Verifica se o nome de usuário e a senha fornecidos são autênticos no sistema.

        - param username: O nome de usuário do usuário.
        - param password: A senha do usuário.
        - return: Retorna uma tupla com o objeto do usuário e booleano (created).
        - raises rest_framework.exceptions.AuthenticationFailed: Se o usuário não estiver autenticado.
        """
        user = authenticate(username=username, password=password)
        if not user:
            raise exceptions.AuthenticationFailed(_("Invalid username or password"))

        return user, True

    @staticmethod
    def authenticate_login(request, type_authenticate: str):
        """
        Esta função verifica se a solicitação contém um header válido.
        O token é decodificado para obter um usuário e uma senha, que são então passados
        para a função `authenticate_credentials` para validar as credenciais.
        Se as credenciais forem válidas, a função retorna uma tupla (user, created).
        Se a solicitação não contiver um cabeçalho de autorização válido ou as credenciais forem
        inválidas, ela gera uma exceção `AuthenticationFailed` com um código de status 401 (Não autorizado).

        - param request: Uma instância da solicitação HTTP.
        - param type_authenticate: String para o tipo de autenticação usado no header.
        - raises rest_framework.exceptions.AuthenticationFailed: Se a solicitação não contiver um  header
            válido ou as credenciais forem inválidas.
        - return: Tupla com as chaves primárias dos modelos de usuário e .
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise exceptions.AuthenticationFailed(_("Missing authorization header."))

        auth_header_parts = auth_header.split()

        if (
            len(auth_header_parts) != 2
            or auth_header_parts[0].lower() != type_authenticate
        ):
            raise exceptions.AuthenticationFailed(_("Invalid authorization header."))

        try:
            auth_header_decode = base64.b64decode(auth_header_parts[1]).decode()
            user, password = auth_header_decode.split(":")
            if not User.objects.filter(username=user).exists():
                raise Exception
            ExternalJWTAuthentication.authenticate_credentials(user, password)
        except Exception:
            raise exceptions.AuthenticationFailed(_("Invalid credentials."))

        return ExternalJWTAuthentication.authenticate_credentials(
            username=user, password=password
        )

    @staticmethod
    def authenticate(request):
        """
        Autentica uma solicitação de usuário decodificando o token.

        Esta função recebe um token como entrada, decodifica-o usando a função `decode_token`
        e retorna o token decodificado.

        - param request: Uma instância da solicitação HTTP.
        - return: O usuário decodificado
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise exceptions.AuthenticationFailed(_("Missing authorization token."))

        try:
            auth_header_parts = auth_header.split()
            if len(auth_header_parts) != 2 or auth_header_parts[0].lower() != "bearer":
                raise exceptions.AuthenticationFailed(
                    _("Invalid authorization header.")
                )

            token = auth_header_parts[1]
            user = ExternalJWTAuthentication.decode_token(token)
            return user, True
        except Exception as error:
            raise exceptions.AuthenticationFailed(_("Invalid token: {}").format(error))
