# -*- coding: utf-8 -*-
from django.db import models
from standard.models import Choice
from contrib.middleware import get_current_user


class RegistrationQuery(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição", null=True, blank=True)
    sql = models.TextField(verbose_name="Consulta Sql")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-id",)

    def is_permission_cadastral_quality(self):
        """ " Checar se o usuário pertence ao grupo mpmt-perfil-qualidade-cadastral-admin,
        que o qual terá permissão para criar/editar/excluir consultas"""

        group_name = Choice.objects.filter(
            name="PERMISSION_CADASTRAL_QUALITY", app_label="cadastralquality"
        ).first()
        if group_name:
            user = get_current_user()
            return user.groups.filter(name=group_name).exists()
        else:
            return False

    def validate(self, not_validate=False):
        if not self.is_permission_cadastral_quality() and not not_validate:
            raise Exception(
                "Você não tem permissão para criar/alterar/excluir Cadastros."
            )
        return True

    def save(self, *args, **kwargs):
        self.validate(not_validate=kwargs.get("not_validate", False))
        if "not_validate" in kwargs:
            kwargs.pop("not_validate")
        super(RegistrationQuery, self).save(*args, **kwargs)

    def delete(self, *args, **kwags):
        self.validate()
        super(RegistrationQuery, self).delete(*args, **kwags)
