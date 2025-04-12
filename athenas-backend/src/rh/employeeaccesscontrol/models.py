import os

import ldap
import ldap.modlist
from django.conf import settings
from django.contrib.auth.models import User

from contrib.middleware import getLogger
from rh.models import Servidor
from engine.models import ControllerPermission
from auditlog.registry import auditlog


log = getLogger(__name__)


class EACEmployee(Servidor):
    """Classe proxy utilizada para criar métodos relacionados ao gerenciamento de servidores
    no active directory"""

    class Meta:
        proxy = True

    def save(self, *args, **kargs):
        try:
            username = args[0]["username"]
            is_staff = args[0]["is_staff"]
            is_active = args[0]["is_active"]
            is_superuser = args[0]["is_superuser"]
            employee_id = args[0]["employee_id"]

            employee = Servidor.objects.get(pk=employee_id)
            user_exists = self.check_user_exists(username)

            if not user_exists and employee.user:
                user = employee.user
                user.username = username
            elif not user_exists and not employee.user:
                user = User.objects.create(username=username)
                employee.user = user
                if (
                    settings.ORGAN_IDENTIFIER == "mpmt"
                    and ControllerPermission.objects.filter(
                        name="portal-vida-funcional"
                    ).exists()
                ):
                    portal_vida_funcional = ControllerPermission.objects.get(
                        name="portal-vida-funcional"
                    )
                    user.controllerpermission_set.add(portal_vida_funcional)
            elif user_exists and employee.user and username == employee.user.username:
                user = employee.user
            else:
                raise Exception("O nome de usuário já existe.")

            user.is_staff = is_staff
            user.is_active = is_active
            user.is_superuser = is_superuser

            user.save()
            employee.save()

        except Exception as err:
            log.exception(err)
            raise err

    def check_user_exists(self, username):
        if User.objects.filter(username=username).exists():
            return True
        else:
            return False

    def __normalize_name(self, name):
        """Este método realiza a normalização do nome do servidor

        Args:
            name (str): Nome do servidor

        Returns:
            list: Lista com os nomes do servidor
        """

        return name.lower().split()

    def __first_last(self, name):
        """Este método retorna uma string com o primeiro e último nome do servidor

        Args:
            name (str): Nome do Servidor

        Returns:
            str: Primeiro e Último nome do servidor concatenado
        """

        first_name = self.__normalize_name(name)[0]
        last_name = self.__normalize_name(name)[-1]

        return f"{first_name}{last_name}"

    def __initials_last(self, name):
        """Este método retorna uma string com as iniciais do nome e último nome do servidor

        Args:
            name (str): Nome do Servidor

        Returns:
            str: Iniciais e Último nome do servidor concatenado
        """

        invalid_names = [
            "da",
            "de",
            "di",
            "do",
            "du",
            "das",
            "des",
            "dis",
            "dos",
            "dus",
            "e",
        ]

        name_initials = "".join(
            [n[0] for n in self.__normalize_name(name)[:-1] if n not in invalid_names]
        )
        # name_initials = name_lower_splitted[0][0] if not exist else name_lower_splitted[0][0:2]
        last_name = self.__normalize_name(name)[-1]

        return f"{name_initials}{last_name}"

    def __first_dot_last(self, name):
        """Este método retorna uma string com o primeiro e último nome do servidor separados por ponto

        Args:
            name (str): Nome do Servidor

        Returns:
            str: Primeiro e Último nome do servidor separado por ponto e concatenado
        """
        first_name = self.__normalize_name(name)[0]
        last_name = self.__normalize_name(name)[-1]

        return f"{first_name}.{last_name}"

    def __create_mail_name(self, name, mail_name_type=""):
        """Este método retonar o usuário de email baseado na configuração

        Args:
            name (str): Nome do servidor
            mail_name_type (str, optional): Configuração do tipo de usuário de email. Defaults to ''.

        Returns:
            str: nome do usuário de email
        """

        if mail_name_type == "first_dot_last":
            mail_name = self.__first_dot_last(name)
        else:
            mail_name = self.__first_last(name)

        return mail_name

    def __create_username(self, name, username_type=""):
        """Este método retonar o usuário baseado na configuração

        Args:
            name (str): Nome do servidor
            username_type (str, optional): Configuração do tipo do nome usuário. Defaults to ''.

        Returns:
            str: nome do usuário
        """

        if username_type == "initials_last":
            username = self.__initials_last(name)
        else:
            username = self.__first_last(name)

        return username

    def __extract_dn(self, dn):
        """Método responsável por converter o dn em string separado por ponto

        Args:
            dn (str): DN do LDAP

        Returns:
            str: String com os argumentos do DN separados por ponto
        """

        return ".".join([e.split("=")[-1] for e in dn.split(",")])

    def __bind(self):
        """Realiza a conexão com o serviço de Ldap

        Returns:
            ldap.ldapobject.SimpleLDAPObject: Objeto de conexão do ldap
        """

        conn = ldap.initialize(settings.LDAP_AUTH["uri"], bytes_mode=False)
        conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
        conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        conn.bind_s(
            settings.LDAP_AUTH["admin"]["user"], settings.LDAP_AUTH["admin"]["passwd"]
        )

        return conn

    def __check_user_exist(self, conn, user_object):
        """Responsável por verificar se um usuário existe no serviço de Ldap

        Args:
            conn (ldap.ldapobject.SimpleLDAPObject): Objeto de conexão do ldap
            user_object (str): CN ou UID definido do servidor

        Returns:
            bool: True se for encontrado e False se não for encontrado
        """

        filter = f"{settings.LDAP_AUTH['user_object']}={user_object}"

        try:
            rid = conn.search(
                settings.LDAP_AUTH["basedn"], ldap.SCOPE_SUBTREE, filter, None
            )
            result = False

            while True:
                type, row = conn.result(rid, 0)
                if row == []:
                    break
                else:
                    result = True

        except ldap.LDAPError as e:
            result = False

        return result

    def __check_auth(self, user_object, pwd=None):
        conn = ldap.initialize(settings.LDAP_AUTH["uri"], bytes_mode=False)
        conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 10.0)
        conn.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        conn.bind_s(
            settings.LDAP_AUTH["admin"]["user"], settings.LDAP_AUTH["admin"]["passwd"]
        )
        filter = f"{settings.LDAP_AUTH['user_object']}={user_object}"
        basedn = settings.LDAP_AUTH["basedn"]
        userdn = self.__search_userdn(conn, basedn, filter)
        log.info("Cheking user...")
        conn.bind_s(userdn, pwd)
        log.info("User checked.")

    def __create_ldap_user(
        self,
        conn,
        user_object,
        givenName,
        sn,
        sAMAccountName,
        userPrincipalName,
        mail,
        password,
    ):
        """[summary]

        Args:
            conn (ldap.ldapobject.SimpleLDAPObject): Objeto de conexão do ldap
            user_object (str): CN ou UID definido do servidor
            givenName (str): Primeiro nome do servidor
            sn (str): Sobrenome do Servidor
            sAMAccountName (str): [description]
            userPrincipalName (str): Usuário Principal
            mail ([type]): Email do servidor
            password (str): Senha padrão

        Returns:
            bool: True se for criado e False se não for criado

        """

        ldif = ldap.modlist.addModlist(
            {
                "objectClass": [
                    l.encode()
                    for l in ["top", "person", "organizationalPerson", "user"]
                ],
                "cn": user_object.encode(),
                "givenName": givenName.encode(),
                "sn": sn.encode(),
                "sAMAccountName": sAMAccountName.encode(),
                "mail": mail.encode(),
                "userPrincipalName": userPrincipalName.encode(),
                "userPassword": [password.encode("utf-16-le")],
            }
        )

        result = False
        try:
            dn = f"{settings.LDAP_AUTH['user_object']}={user_object},{settings.LDAP_AUTH['basedn']}"
            conn.add_s(dn, ldif)
            result = True

        except (ldap.LDAPError, Exception) as e:
            log.exception(e)
            conn.unbind()

        return result

    def __password_params(self, new_passwd):
        """Realiza a configuração da senha que será modificada

        Args:
            new_passwd ([type]): [description]

        Returns:
            list: Retorna uma lista com os argumentos usados na alteração da senha.
        """

        modify_passwd_op = []
        modify_passwd_op = [(ldap.MOD_REPLACE, "userPassword", [new_passwd.encode()])]

        return modify_passwd_op

    def __search_userdn(self, conn, basedn, filter=""):
        """Localiza o dn do usuário

        Args:
            conn (ldap.ldapobject.SimpleLDAPObject): Objeto de conexão do ldap
            basedn (str): Nome do domínio base
            filter (str, optional): Conteúdo do filtro que será utilizado para consultar no ldap. Defaults to ''.

        Returns:
            str: Nome de domínio do usuário
        """
        results = conn.search_s(basedn, ldap.SCOPE_SUBTREE, filter, None)

        userdn = ""
        if results:
            for dn, _ in results:
                userdn = dn

        return userdn

    def __change_password(self, user_object, new_password):
        """Método responsável por alterar a senha do servidor no serviço de ldap

        Args:
            user_object (str): CN ou UID definido do servidor
            new_password (str): Nova senha do servidor

        Raises:
            Exception: Servidor não encontrado no serviço de LDAP
            Exception: Erro no processamento do reset de senha
        """

        try:
            if not new_password or len(new_password) < 8:
                raise Exception(
                    "A nova senha deve ter pelo menos 8 caracteres alfanuméricos"
                )

            conn = self.__bind()

            filter = f"{settings.LDAP_AUTH['user_object']}={user_object}"

            basedn = settings.LDAP_AUTH["basedn"]
            userdn = self.__search_userdn(conn, basedn, filter)

            if userdn:
                passwd_change_op = self.__password_params(new_password)

                conn.modify_s(userdn, passwd_change_op)
            else:
                raise Exception(
                    "Não foi possível encontrar o servidor informado. A senha não foi modificada."
                )

        except Exception as e:
            log.exception(e)
            raise e

    def create_user_by_admin(self):
        """Realiza a criação do usuário no Athenas caso não exista

        Raises:
            Exception: Erro no processamento da criação do usuário
            Exception: Problema ao criar o username ou usuário de email
        """

        username_type = getattr(settings, "USERNAME_TYPE", "")
        mail_name_type = getattr(settings, "MAIL_NAME_TYPE", "")

        username = self.__create_username(self.pessoa_fisica.nome, username_type)
        mail_name = self.__create_mail_name(self.pessoa_fisica.nome, mail_name_type)

        if username and mail_name:
            email = mail_name + "@" + settings.LDAP_AUTH["domain_mail"]

            try:
                user = User.objects.create_user(username=username, email=email)
                user.set_password(os.urandom(12))
                user.is_active = True
                user.is_staff = True
                user.save()

                self.user = user
                self.save()

            except Exception as e:
                log.exception(e)
                raise e
        else:
            raise Exception("Ocorreu um erro ao criar o usuário.")

    def create_user_ldap(self):
        """Este método é responsavel por criar um usuário no serviço de ldap

        Raises:
            Exception: Usuário já existe
            Exception: Erro durante o processamento na criação do usuário
            Exception: Erro Genérico
        """

        DN = settings.LDAP_AUTH["dn"]

        try:
            conn = self.__bind()
            if settings.LDAP_AUTH["user_object"] == "uid":
                user_object = self.user.username

            elif settings.LDAP_AUTH["user_object"] == "cn":
                user_object = self.pessoa_fisica.nome.upper()

            givenName = self.pessoa_fisica.nome.upper().split()[0]
            sn = " ".join(self.pessoa_fisica.nome.upper().split()[1:])
            sAMAccountName = self.user.username
            userPrincipalName = self.user.username + f"@{self.__extract_dn(DN)}"
            mail = self.user.email
            password = settings.DEFAULT_USER_PASSWORD

            if self.__check_user_exist(conn, user_object):
                raise Exception("O usuário já existe no LDAP")

            else:
                result = self.__create_ldap_user(
                    conn,
                    user_object,
                    givenName,
                    sn,
                    sAMAccountName,
                    userPrincipalName,
                    mail,
                    password,
                )

                if result:
                    log.info("Usuário criado com exito.")
                else:
                    raise Exception("Ocorreu um erro na criação do usuário.")

            conn.unbind()

        except Exception as e:
            log.exception(e)
            raise e

    def reset_user_password(self):
        """Este método é reponsavel por resetar a senha do servidor no serviço de LDAP

        Raises:
            Exception: Erro ao alterar a senha do usuário

        Returns:
            bool: True caso tenha sucesso na alteração de senha
        """
        new_password = settings.DEFAULT_USER_PASSWORD

        if settings.LDAP_AUTH["user_object"] == "uid":
            user_object = self.user.username

        elif settings.LDAP_AUTH["user_object"] == "cn":
            user_object = self.pessoa_fisica.nome.upper()

        try:
            self.__change_password(user_object, new_password)
        except Exception as e:
            log.exception(e)
            raise e

        return True

    def change_password(self, current_password, new_password):
        """Este método é reponsavel por resetar a senha do servidor no serviço de LDAP

        Raises:
            Exception: Erro ao alterar a senha do usuário

        Returns:
            bool: True caso tenha sucesso na alteração de senha
        """

        try:
            if settings.LDAP_AUTH["user_object"] == "uid":
                user_object = self.user.username

            elif settings.LDAP_AUTH["user_object"] == "cn":
                user_object = self.pessoa_fisica.nome.upper()

            try:
                self.__check_auth(user_object, current_password)
            except Exception as e:
                log.exception(e)
                raise Exception("Usuário ou senha atuais inválidos.")

        except Exception as e:
            log.exception(e)
            raise e
        else:
            self.__change_password(user_object, new_password)


auditlog.register(EACEmployee)
