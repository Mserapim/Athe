# -*- coding: utf-8 -*-
from ctypes import ArgumentError
from django.core.management.base import BaseCommand
from django.conf import settings
from optparse import make_option
from contrib.utils import getLogger
from django.conf import settings

import ldap
import ldap.modlist
import hashlib
import base64


class Command(BaseCommand):
    help = "Comando usado para criar usuario no LDAP."

    option_list = BaseCommand.option_list + (
        make_option("--user", nargs=1, dest="user", help="Nome do novo usuario."),
        make_option(
            "--password=USER", dest="passwd", nargs=1, help="Senha do novo usuario."
        ),
    )

    def __init__(self, *args, **kargs):
        self.log = getLogger(self.__class__.__name__)
        BaseCommand.__init__(self, *args, **kargs)

    def _create_domain(self, ldap_connection):
        ldif = ldap.modlist.addModlist(
            {"objectClass": ["top", "domain"], "o": "mp", "dc": "mp"}
        )

        try:
            ldap_connection.add_s(settings.LDAP_AUTH["dn"], ldif)
        except ldap.LDAPError as e:
            self.log.exception(e)

    def _check_user_exist(self, ldap_connection, user):
        filter = "cn=" + user

        try:
            rid = ldap_connection.search(
                settings.LDAP_AUTH["basedn"], ldap.SCOPE_SUBTREE, filter, None
            )
            result = False

            while True:
                type, row = ldap_connection.result(rid, 0)
                if row == []:
                    break
                else:
                    result = True

            return result
        except ldap.LDAPError as e:
            return False

    def _check_schema_exist(self, ldap_connection, schema):
        filter = "ou=" + schema

        try:
            rid = ldap_connection.search(
                settings.LDAP_AUTH["dn"], ldap.SCOPE_SUBTREE, filter, None
            )
            result = False

            while True:
                type, row = ldap_connection.result(rid, 0)
                if row == []:
                    break
                else:
                    result = True

            return result
        except ldap.LDAPError as e:
            self.log.exception(e)
            return False

    def _create_schema(self, ldap_connection, schema):
        ldif = ldap.modlist.addModlist(
            {"objectClass": ["top", "organizationalUnit"], "ou": schema}
        )

        try:
            ldap_connection.add_s(settings.LDAP_AUTH["basedn"], ldif)
            return True
        except ldap.LDAPError as e:
            self.log.exception(e)
            return False

    def _create_user(self, ldap_connection, user, passwd):
        hash = hashlib.sha1()
        hash.update(passwd.encode())

        ldif = ldap.modlist.addModlist(
            {
                "objectClass": ["top", "person"],
                "cn": user,
                "sn": user,
                "userPassword": "{SHA}" + base64.encodestring(hash.digest()),
            }
        )

        try:
            ldap_connection.add_s(
                "cn=" + user + "," + settings.LDAP_AUTH["basedn"], ldif
            )
            return True
        except ldap.LDAPError as e:
            self.log.exception(e)
            return False

    def handle(self, *args, **options):
        if not options["user"]:
            raise ArgumentError("O nome do usuario deve ser informado.")
            return
        else:
            if not options["passwd"]:
                raise ArgumentError("A senha do usuario deve ser informado.")
                return
            else:
                try:
                    l = ldap.initialize(settings.LDAP_AUTH["uri"])
                    l.bind_s(
                        settings.LDAP_AUTH["admin"]["user"],
                        settings.LDAP_AUTH["admin"]["passwd"],
                    )

                    if self._check_user_exist(l, options["user"]):
                        self.log.info("O usuario ja existe no LDAP.")
                    else:
                        self.log.warn("O usuário não exite.")

                        part = settings.LDAP_AUTH["basedn"].split(",")
                        part = part[0].split("=")

                        self._create_domain(l)

                        if not self._check_schema_exist(l, part[1]):
                            self.log.info("A base de usuários nao exite e será criada.")
                            self._create_schema(l, part[1])

                        result = self._create_user(
                            l, options["user"], options["passwd"]
                        )

                        if result:
                            self.log.info("Usuário criado com exito.")
                        else:
                            self.log.info(
                                "Ocorreu um erro na criação do usuário cheque o retorno no log do LDAP."
                            )

                    l.unbind()
                except Exception as exception:
                    self.log.exception(exception)
