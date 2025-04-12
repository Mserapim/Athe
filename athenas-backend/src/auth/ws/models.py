# -*- coding: utf-8 -*-
"""
Módulo que contém a definição das classes:

:Classes:
   :class:`Application`,
   :class:`UserPermission`.

"""

import os, hashlib
from django.db import models


class ApplicationManager(models.Manager):

    def get_by_natural_key(self, app_key):
        return self.get(app_key=app_key)


class Application(models.Model):
    """**Classe** que modela Aplicativos autorizados a requisitar serviços ao athenas."""

    objects = ApplicationManager()

    #: Atibuto que identifica o título do aplicativo.
    title = models.CharField(unique=True, max_length=50)

    #: Atibuto que contém a chave do aplicativo.
    app_key = models.CharField(max_length=32)

    #: Atibuto que define o prazo de validade de acessos do aplicativo.
    valid_at = models.DateTimeField(null=True)

    def natural_key(self):
        return (self.app_key,)

    @property
    def is_valid(self):
        pass

    def _is_valid(self, moment):
        pass

    def save(self, *args, **kwargs):
        if self.title:
            self.app_key = hashlib.md5(self.title.encode("u8")).hexdigest()

        super(Application, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.title)


class UserPermissionManager(models.Manager):

    def get_by_natural_key(self, user_token):
        return self.get(user_token=user_token)


class UserPermission(models.Model):
    """
    **Classe** que modela Usuários e suas devidas permissões para requisitar serviços ao athenas.

    :Métodos:
        :func:`save`,
        :func:`_token_generator`.
    """

    objects = UserPermissionManager()

    #: Atibuto que identifica os usuários que possuem acesso ao athenas.
    user = models.ForeignKey(
        "auth.User", related_name="ws_permissions", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    #: Atibuto que identifica o aplicativo autorizado a requisitar serviços ao athenas.
    application = models.ForeignKey(
        Application, related_name="users", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)

    #: Atibuto que armazena o valor da chave de usuário.
    user_token = models.CharField(max_length=32, blank=True)

    #: Atibuto que define o status de um determinado usuário.
    active = models.BooleanField(default=True)

    def natural_key(self):
        return (self.user_token,)

    def _token_generator(self):
        """Método para gerar chaves MD5 para identificar usuários.

        :returns:  String -- Hash MD5 de 128 bits.
        """

        digest = hashlib.new("md5")
        digest.update(os.urandom(4096))
        return digest.hexdigest()

    def save(self, *args, **kargs):
        """Método para gerar chaves de usuários e persistir valores na base de dados."""

        if self.pk is None and not self.user_token:
            self.user_token = self._token_generator()
        super(UserPermission, self).save(*args, **kargs)
