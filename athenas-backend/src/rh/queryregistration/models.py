# -*- coding: utf-8 -*-
from django.db import models
from rh.models import Employee, Servidor
from standard.models import Choice
from contrib.middleware import get_current_user
from auditlog.registry import auditlog
from standard.models import AuditTimestampModel


class Consultation(AuditTimestampModel):
    title = models.CharField(max_length=300, verbose_name="Título do Relatório")
    sql = models.TextField(verbose_name="Consulta SQL")
    log_sql = models.TextField(verbose_name="SQL Executado", blank=True, null=True)
    download = models.BooleanField(verbose_name="Download", default=False)
    data = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-id",)

    def is_permission_consultation(self):
        """ " Checar se o usuário pertence ao grupo mpmt-perfil-cadastro-consultas-admin,
        que o qual terá permissão para criar/editar/excluir consultas"""

        group_name = Choice.objects.filter(
            name="PERMISSION_CONSULTATION", app_label="queryregistration"
        ).first()
        if group_name:
            user = get_current_user()
            return user.groups.filter(name=group_name).exists()
        else:
            return False

    def validate(self, not_validate=False):
        if not self.is_permission_consultation() and not not_validate:
            raise Exception(
                "Você não tem permissão para criar/alterar/excluir Consultas."
            )
        return True

    def save(self, *args, **kwargs):
        self.validate(not_validate=kwargs.get("not_validate", False))
        if "not_validate" in kwargs:
            kwargs.pop("not_validate")
        super(Consultation, self).save(*args, **kwargs)

    def delete(self, *args, **kwags):
        self.validate()
        super(Consultation, self).delete(*args, **kwags)

    @classmethod
    def save_log_sql(cls, pk, sql):
        consultation = cls.objects.get(pk=pk)
        consultation.log_sql = sql.decode("utf-8")
        consultation.save(not_validate=True)


class TagField(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name="Nome")
    description = models.CharField(
        max_length=250, verbose_name="Descrição", blank=True, null=True
    )
    key_tag = models.CharField(unique=True, max_length=50, verbose_name="Chave da Tag")
    type_tag = models.CharField(max_length=150, verbose_name="Tipo Campo")
    type_rest = models.CharField(
        max_length=250, verbose_name="Restful do Campo", blank=True, null=True
    )
    choice_id = models.CharField(
        max_length=250, verbose_name="Choice id", blank=True, null=True
    )
    value = models.CharField(max_length=50, verbose_name="Valor do campo")
    length = models.IntegerField(verbose_name="Tamanho do campo", blank=True, null=True)
    controller = models.CharField(
        max_length=50, verbose_name="Controller", blank=True, null=True
    )
    model = models.CharField(
        max_length=50, verbose_name="Modelo", blank=True, null=True
    )
    colums = models.IntegerField(verbose_name="Colunas", blank=True, null=True)
    many = models.BooleanField(verbose_name="Campo muitos", default=False)
    sql_in = models.BooleanField(verbose_name="Sql in", default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("-id",)

    def get_cache_value(self, employee, consultation, field_name):
        cache = CacheTag.objects.filter(
            tag=self, employee=employee, report=consultation, field_name=field_name
        ).last()
        return cache.value if cache else None

    def is_permission_tagfield(self):
        """ " Checar se o usuário pertence ao grupo mpmt-perfil-cadastro-consultas-admin,
        que o qual terá permissão para criar/editar/excluir Tags"""

        group_name = Choice.objects.filter(
            name="PERMISSION_CONSULTATION", app_label="queryregistration"
        ).first()
        if group_name:
            user = get_current_user()
            return user.groups.filter(name=group_name).exists()
        else:
            return False

    def validate_permission(self):
        if not self.is_permission_tagfield():
            raise Exception("Você não tem permissão para criar/alterar/excluir Tags.")

        return True

    def validate_field(self):
        if not self.name or not self.value or not self.type_tag:
            raise Exception("Preencha todos os campos obrigatórios.")

        return True

    def validate(self):
        self.validate_field()
        self.validate_permission()

    def save(self, *args, **kwargs):
        self.validate()
        self.key_tag = self.name.replace(" ", "_")
        super(TagField, self).save(*args, **kwargs)

    def delete(self, *args, **kwags):
        self.validate_permission()
        super(TagField, self).delete(*args, **kwags)


class CacheTag(models.Model):
    field_name = models.CharField(verbose_name="Nome do Campo", max_length=128)
    report = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    tag = models.ForeignKey(TagField, on_delete=models.CASCADE)
    employee = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    value = models.CharField(verbose_name="Valor", max_length=500)


auditlog.register(Consultation)
