# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from django.contrib.auth import backends
from django.contrib.auth import models
from django.contrib.auth.models import User
from django.db import connections
from auth.backend import LDAPBalancer
from django.conf import settings

import os
import random


class Backend(backends.ModelBackend):
    """
    Backend para autenticação Web com LDAP.
    """

    def __init__(self):
        super(Backend, self).__init__()
        self.log = getLogger("auth.ldap.oracle.%s" % Backend.__name__)

    def authenticate(self, request, username=None, password=None):
        """
        Sobrescreve o metodo de autenciação do MOdelBackend fazendo autênticar no LDAP.
        :param username Nome do usuários.
        :param password Senha do usuários.
        :return Retorna uma entidade User caso tenha conseguido autênticar.
        """
        try:
            bl = LDAPBalancer()
            host = bl.next()

            cfg = bl.get_configuration(host)
        except Exception as e:
            self.log.exception(e)
            cfg = settings.LDAP_AUTH

        uri = cfg["uri"]

        self.log.info("Usando o servidor %s" % uri)

        if username and password:
            username = username.lower().replace(" ", "")

            try:
                cur = connections["default"].cursor()
            except Exception as e:
                self.log.exception(e)
                return None
            else:
                host = uri.split(":")[1].replace("//", "")
                port = int(uri.split(":")[2].replace("/", ""))

                self.log.debug((host, port))

                result = cur.execute(
                    "SELECT django_auth('%s', '%s', '%s', %d, '%s', '%s') as is_auth FROM DUAL"
                    % (
                        username,
                        password,
                        host,
                        port,
                        cfg.get("user_object"),
                        cfg.get("basedn"),
                    )
                )

                row = result.fetchone()

                if row[0] == "0":
                    return None
                else:
                    self.log.info("Usuários autenticado com sucesso no LDAP!!!")

                    try:
                        user = models.User.objects.get(username=username)
                    except models.User.DoesNotExist:
                        if cfg["db_user_autocreate"]:
                            user = models.User.objects.create_user(
                                username, username + "@" + cfg["domain_mail"]
                            )
                            user.set_password(os.urandom(12))
                            user.save()
                            self.log.info("Usuário criado no banco de dados!!!")
                        else:
                            user = None

                    return user if user.is_active else None

    def get_user(self, user_id):
        """
        Metodo responsável por retorna um usuário de acordo com seu user_id.
        :param user_id Identificador do usuário.
        :return Caso consegui encontrar o usuário retorna, caso contrario retorna None.
        """
        try:
            user = models.User.objects.get(pk=user_id)
            # self.log.info("Usuario com id %s encontrado." % user_id)
            return user
        except User.DoesNotExist:
            self.log.critical("Usuário não existe na base de dados.")
            return None
