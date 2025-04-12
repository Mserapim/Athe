# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Capacitacao.inscricao_inicio'
        db.add_column(
            "gecap_capacitacao",
            "inscricao_inicio",
            self.gf("django.db.models.fields.DateTimeField")(null=True, blank=True),
            keep_default=False,
        )

        # Adding field 'Capacitacao.inscricao_fim'
        db.add_column(
            "gecap_capacitacao",
            "inscricao_fim",
            self.gf("django.db.models.fields.DateTimeField")(null=True, blank=True),
            keep_default=False,
        )

    def backwards(self, orm):
        # Deleting field 'Capacitacao.inscricao_inicio'
        db.delete_column("gecap_capacitacao", "inscricao_inicio")

        # Deleting field 'Capacitacao.inscricao_fim'
        db.delete_column("gecap_capacitacao", "inscricao_fim")

    models = {
        "auth.group": {
            "Meta": {"object_name": "Group"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "unique": "True", "null": "True"},
            ),
            "permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Permission']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "auth.permission": {
            "Meta": {
                "ordering": "('content_type__app_label', 'content_type__model', 'codename')",
                "unique_together": "(('content_type', 'codename'),)",
                "object_name": "Permission",
            },
            "codename": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
        },
        "auth.user": {
            "Meta": {"object_name": "User"},
            "date_joined": (
                "django.db.models.fields.DateTimeField",
                [],
                {"default": "datetime.datetime.now"},
            ),
            "email": (
                "django.db.models.fields.EmailField",
                [],
                {"max_length": "75", "null": "True", "blank": "True"},
            ),
            "first_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True", "blank": "True"},
            ),
            "groups": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Group']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "is_active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "is_staff": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "is_superuser": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "last_login": (
                "django.db.models.fields.DateTimeField",
                [],
                {"default": "datetime.datetime.now"},
            ),
            "last_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True", "blank": "True"},
            ),
            "password": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True"},
            ),
            "user_permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.Permission']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "username": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "unique": "True", "null": "True"},
            ),
        },
        "contenttypes.contenttype": {
            "Meta": {
                "ordering": "('name',)",
                "unique_together": "(('app_label', 'model'),)",
                "object_name": "ContentType",
                "db_table": "'django_content_type'",
            },
            "app_label": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "model": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "gecap.areaconhecimento": {
            "Meta": {
                "ordering": "['titulo', 'codigo_cnpq']",
                "object_name": "AreaConhecimento",
            },
            "cache_codigo_cnpq": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "codigo_cnpq": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "sub_area_de": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'sub_areas'",
                    "null": "True",
                    "to": "orm['gecap.AreaConhecimento']",
                },
            ),
            "titulo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
        },
        "gecap.capacitacao": {
            "Meta": {"object_name": "Capacitacao"},
            "area_conhecimento": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'capacitacoes'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['gecap.AreaConhecimento']",
                },
            ),
            "carga_horaria": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "cidade_evento": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'capacitacoes'", "to": "orm['rh.Localidade']"},
            ),
            "data_cadastro": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "dt_fim": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "dt_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "ementa": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "inscricao_fim": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "inscricao_inicio": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "promotores": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'capacitacoes'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['rh.OrgaoGeral']",
                },
            ),
            "promovido_por": ("django.db.models.fields.IntegerField", [], {}),
            "publicar": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
        "gecap.congresso": {
            "Meta": {"object_name": "Congresso", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.curso": {
            "Meta": {"object_name": "Curso", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.evento": {
            "Meta": {"object_name": "Evento", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.feira": {
            "Meta": {"object_name": "Feira", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.inscricao": {
            "Meta": {
                "unique_together": "(('capacitacao', 'servidor'),)",
                "object_name": "Inscricao",
            },
            "capacitacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'inscricoes'", "to": "orm['gecap.Capacitacao']"},
            ),
            "certificado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "data_cadastro": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "homologado": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "servidor": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'inscricoes'", "to": "orm['rh.Servidor']"},
            ),
        },
        "gecap.investimento": {
            "Meta": {"object_name": "Investimento"},
            "capacitacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'investimentos'",
                    "null": "True",
                    "to": "orm['gecap.Capacitacao']",
                },
            ),
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "inscricao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'investimentos'",
                    "null": "True",
                    "to": "orm['gecap.Inscricao']",
                },
            ),
            "previsao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "valor": (
                "django.db.models.fields.DecimalField",
                [],
                {"max_digits": "18", "decimal_places": "2"},
            ),
        },
        "gecap.oficina": {
            "Meta": {"object_name": "Oficina", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.reuniao": {
            "Meta": {"object_name": "Reuniao", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "gecap.seminario": {
            "Meta": {"object_name": "Seminario", "_ormbases": ["gecap.Capacitacao"]},
            "capacitacao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['gecap.Capacitacao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "ged.arquivo": {
            "Meta": {
                "unique_together": "(('file', 'user'),)",
                "object_name": "Arquivo",
            },
            "acesso": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "copia_de": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "created": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "file": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "32", "null": "True"},
            ),
            "filename": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "260", "null": "True", "blank": "True"},
            ),
            "group": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Lotacao']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mimetype": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['auth.User']"},
            ),
        },
        "notification.message": {
            "Meta": {"object_name": "Message", "db_table": "'eng_message'"},
            "default_params": (
                "django.db.models.fields.CharField",
                [],
                {
                    "default": "'{}'",
                    "max_length": "400",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "header": (
                "django.db.models.fields.CharField",
                [],
                {"default": "''", "max_length": "30", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "message": (
                "django.db.models.fields.TextField",
                [],
                {"default": "''", "null": "True"},
            ),
            "mid": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "unique": "True", "null": "True", "blank": "True"},
            ),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'INFO'", "max_length": "10", "null": "True"},
            ),
        },
        "notification.notification": {
            "Meta": {
                "ordering": "('-created_at',)",
                "object_name": "Notification",
                "db_table": "'eng_notification'",
            },
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "msg": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'notifications'",
                    "to": "orm['notification.Message']",
                },
            ),
            "params": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "400", "null": "True"},
            ),
            "sender_ct": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'notifications_send'",
                    "null": "True",
                    "to": "orm['contenttypes.ContentType']",
                },
            ),
            "sender_id": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "status": (
                "django.db.models.fields.PositiveSmallIntegerField",
                [],
                {"default": "2"},
            ),
            "target_ct": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'notifications_receive'",
                    "to": "orm['contenttypes.ContentType']",
                },
            ),
            "target_id": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'SYS'", "max_length": "10", "null": "True"},
            ),
        },
        "rh.anotacaogeral": {
            "Meta": {
                "ordering": "('-id',)",
                "object_name": "AnotacaoGeral",
                "db_table": "'rh_anotgeral'",
            },
            "ativa": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_documento": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now_add": "True", "null": "True", "blank": "True"},
            ),
            "data_portaria_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indireto": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "movimento_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "u'anotacoes'",
                    "null": "True",
                    "to": "orm['rh.MovimentacaoPessoal']",
                },
            ),
            "numero_documento": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "numero_processo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "publicacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Publicacao']", "null": "True", "blank": "True"},
            ),
            "resumo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "null": "True", "blank": "True"},
            ),
            "servidor": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'anotacoes'", "to": "orm['rh.Servidor']"},
            ),
            "texto": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "tipo_documento": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.banco": {
            "Meta": {"ordering": "['nome']", "object_name": "Banco"},
            "agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "dv_agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True", "blank": "True"},
            ),
            "dv_conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "unique": "True", "null": "True"},
            ),
            "numero_convenio": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "pessoajuridica": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'como_banco'",
                    "null": "True",
                    "to": "orm['rh.PessoaJuridica']",
                },
            ),
            "principal": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "sequencial_arquivo": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "0"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
            "tem_convenio": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"null": "True"},
            ),
        },
        "rh.capacidade": {
            "Meta": {"object_name": "Capacidade"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.cargo": {
            "Meta": {"ordering": "['nome']", "object_name": "Cargo"},
            "acumulavel": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "cargo_arquimedes": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "0"},
            ),
            "carreira": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Carreira']", "null": "True", "blank": "True"},
            ),
            "cbo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Cbo']"},
            ),
            "chefia": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "designa_exercicio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "entrancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Entrancia']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicativo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'S'", "max_length": "1", "null": "True"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "lotacao_responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'cargo_responsavel'",
                    "null": "True",
                    "to": "orm['rh.Lotacao']",
                },
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "poder": ("django.db.models.fields.IntegerField", [], {"default": "5"}),
            "professor": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "substituivel": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "tipo_lei_cargo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'EF'", "max_length": "2", "null": "True"},
            ),
            "unidade_administrativa": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.UnidadeAdministrativa']", "null": "True"},
            ),
        },
        "rh.carreira": {
            "Meta": {"object_name": "Carreira"},
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "data_fim": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.cbo": {
            "Meta": {"object_name": "Cbo"},
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "250", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "rh.circunscricao": {
            "Meta": {"object_name": "Circunscricao"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.comarca": {
            "Meta": {"object_name": "Comarca"},
            "circunscricao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Circunscricao']", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "grupo_comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.GrupoComarca']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "validacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
        },
        "rh.curso": {
            "Meta": {"object_name": "Curso"},
            "area_conhecimento": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['gecap.AreaConhecimento']", "null": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "1", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.dadobancario": {
            "Meta": {"ordering": "['banco']", "object_name": "DadoBancario"},
            "agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "banco": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Banco']"},
            ),
            "conta_corrente_completa": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "tipo_conta": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.docsdadosespecificos": {
            "Meta": {"object_name": "DocsDadosEspecificos"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "especificidade": ("django.db.models.fields.IntegerField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "valor": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True"},
            ),
        },
        "rh.documento": {
            "Meta": {"object_name": "Documento"},
            "arquivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "dados_especificos": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.DocsDadosEspecificos']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "data_expedicao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_validade": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "estado_expedicao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "null": "True"},
            ),
            "tipo_documento": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.documentodigital": {
            "Meta": {"object_name": "DocumentoDigital"},
            "arquivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "rh.endereco": {
            "Meta": {"object_name": "Endereco"},
            "bairro": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "cep": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True"},
            ),
            "complemento": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "logradouro": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "municipio": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']", "null": "True"},
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "tipo_endereco": ("django.db.models.fields.IntegerField", [], {}),
            "tipo_logradouro": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.entrancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Entrancia"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.especialidade": {
            "Meta": {"ordering": "['nome']", "object_name": "Especialidade"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True"},
            ),
        },
        "rh.estado": {
            "Meta": {"ordering": "['nome']", "object_name": "Estado"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "ibge": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "pais": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Pais']"},
            ),
            "siafi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True"},
            ),
            "tse": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
        },
        "rh.grupocomarca": {
            "Meta": {"object_name": "GrupoComarca"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.incapacidade": {
            "Meta": {"object_name": "InCapacidade"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.instancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Instancia"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.localidade": {
            "Meta": {"object_name": "Localidade"},
            "cep": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "9", "null": "True", "blank": "True"},
            ),
            "comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Comarca']", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "distancia_capital": (
                "django.db.models.fields.DecimalField",
                [],
                {
                    "null": "True",
                    "max_digits": "6",
                    "decimal_places": "2",
                    "blank": "True",
                },
            ),
            "estado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']"},
            ),
            "ibge": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicador_municipio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "microregiao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.MicroRegiao']", "null": "True", "blank": "True"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "sede_termo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "siafi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
            "valor_vale_transporte": (
                "django.db.models.fields.DecimalField",
                [],
                {
                    "null": "True",
                    "max_digits": "6",
                    "decimal_places": "2",
                    "blank": "True",
                },
            ),
        },
        "rh.lotacao": {
            "Meta": {
                "ordering": "['nome']",
                "object_name": "Lotacao",
                "_ormbases": ["rh.OrgaoGeral"],
            },
            "acesso_protocolo_geral": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "administrativo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "andar": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True", "blank": "True"},
            ),
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True", "blank": "True"},
            ),
            "comarca": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Comarca']", "null": "True", "blank": "True"},
            ),
            "designacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "entrancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Entrancia']", "null": "True", "blank": "True"},
            ),
            "executivo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "grupo": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Lotacao']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "grupo_lotacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "localidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']"},
            ),
            "organograma": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "orgaogeral_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.OrgaoGeral']", "unique": "True", "primary_key": "True"},
            ),
            "ouvidoria": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "pai": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'lotacoes_subordinadas'",
                    "null": "True",
                    "to": "orm['rh.Lotacao']",
                },
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'responsavel_por'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "sala": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "6", "null": "True", "blank": "True"},
            ),
        },
        "rh.mesoregiao": {
            "Meta": {"object_name": "MesoRegiao"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.microregiao": {
            "Meta": {"object_name": "MicroRegiao"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "meso_regiao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.MesoRegiao']"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.molestia": {
            "Meta": {"object_name": "Molestia"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_laudo": ("django.db.models.fields.DateField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "publicacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Publicacao']", "null": "True", "blank": "True"},
            ),
        },
        "rh.movimentacaopessoal": {
            "Meta": {
                "object_name": "MovimentacaoPessoal",
                "db_table": "'rh_movpessoal'",
            },
            "anota": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "anotacao_geral": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['rh.AnotacaoGeral']",
                    "null": "True",
                    "on_delete": "models.SET_NULL",
                    "blank": "True",
                },
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "publicacao_alteracao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'movimentacao'",
                    "null": "True",
                    "to": "orm['rh.Publicacao']",
                },
            ),
            "publicacao_movimentacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['rh.Publicacao']",
                    "null": "True",
                    "on_delete": "models.PROTECT",
                    "blank": "True",
                },
            ),
            "servidor": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['rh.Servidor']",
                    "on_delete": "models.PROTECT",
                    "blank": "True",
                },
            ),
            "texto": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "rh.movimentacaoposse": {
            "Meta": {
                "object_name": "MovimentacaoPosse",
                "db_table": "'rh_movposse'",
                "_ormbases": ["rh.MovimentacaoPessoal"],
            },
            "anotacao_geral_exercicio": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'anotgeral_exercicio'",
                    "null": "True",
                    "on_delete": "models.SET_NULL",
                    "to": "orm['rh.AnotacaoGeral']",
                },
            ),
            "anotacao_geral_nomeacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'anotgeral_nomeacao'",
                    "null": "True",
                    "on_delete": "models.SET_NULL",
                    "to": "orm['rh.AnotacaoGeral']",
                },
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "data_desligamento": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_exercicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_posse": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "movimentacaopessoal_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['rh.MovimentacaoPessoal']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "quadro": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Quadro']", "null": "True", "blank": "True"},
            ),
            "tipo_movcarreira": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'NOMEACAO'", "max_length": "30", "null": "True"},
            ),
        },
        "rh.necessidadeespecial": {
            "Meta": {"object_name": "NecessidadeEspecial"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.orgaogeral": {
            "Meta": {"ordering": "['nome']", "object_name": "OrgaoGeral"},
            "abreviacao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True", "blank": "True"},
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "codigo_igeprev": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "endereco": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Endereco']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "esfera_governamental": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "habilita_protocolo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "order_nome": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
            "poder": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "publica_doc": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "sigla": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "8", "null": "True", "blank": "True"},
            ),
            "telefone": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Telefone']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "rh.pais": {
            "Meta": {"ordering": "['nome']", "object_name": "Pais"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "ddi": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nacionalidade": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "nome_completo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.pessoa": {
            "Meta": {"ordering": "('nome',)", "object_name": "Pessoa"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "dado_bancario": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'dados_bancarios_pessoas'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['rh.DadoBancario']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "endereco": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Endereco']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "telefone": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Telefone']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "rh.pessoafisica": {
            "Meta": {
                "ordering": "('nome', 'cpf')",
                "object_name": "PessoaFisica",
                "_ormbases": ["rh.Pessoa"],
            },
            "cpf": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "14", "null": "True", "blank": "True"},
            ),
            "data_cadastro": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "null": "True", "blank": "True"},
            ),
            "data_nascimento": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_obito": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "doador": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "documento": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Documento']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "email_pessoal": (
                "django.db.models.fields.EmailField",
                [],
                {"max_length": "75", "null": "True", "blank": "True"},
            ),
            "estado_civil": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "1"},
            ),
            "fator_rh": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "2", "null": "True", "blank": "True"},
            ),
            "foto": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "municipio_naturalidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']", "null": "True", "blank": "True"},
            ),
            "necessidade_especial": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "necessidades_especiais": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'pessoafisica'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['rh.NecessidadeEspecial']",
                },
            ),
            "nome_conjuge": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "nome_mae": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "nome_pai": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "80", "null": "True", "blank": "True"},
            ),
            "pessoa_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.Pessoa']", "unique": "True", "primary_key": "True"},
            ),
            "raca_cor": ("django.db.models.fields.IntegerField", [], {"default": "6"}),
            "rg": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "rg_data_expedicao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "rg_orgao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "rg_uf": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Estado']", "null": "True", "blank": "True"},
            ),
            "sangue": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "4", "blank": "True"},
            ),
            "sexo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "1", "null": "True", "blank": "True"},
            ),
        },
        "rh.pessoajuridica": {
            "Meta": {
                "ordering": "('nome', 'cnpj')",
                "object_name": "PessoaJuridica",
                "_ormbases": ["rh.Pessoa"],
            },
            "cnpj": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "14", "null": "True"},
            ),
            "pessoa_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.Pessoa']", "unique": "True", "primary_key": "True"},
            ),
            "razao_social": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255", "null": "True"},
            ),
        },
        "rh.publicacao": {
            "Meta": {
                "ordering": "['-data_expedicao', 'origem', 'numero']",
                "object_name": "Publicacao",
            },
            "ano": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "4", "null": "True", "blank": "True"},
            ),
            "arquivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "cache_unicode": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_expedicao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True"},
            ),
            "data_publicacao": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_vigencia": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "interessado_nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True", "blank": "True"},
            ),
            "interno": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "lei_autorizativa": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
            ),
            "numero_publicacao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "22", "null": "True", "blank": "True"},
            ),
            "observacao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True", "blank": "True"},
            ),
            "origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.OrgaoGeral']", "null": "True", "blank": "True"},
            ),
            "tipo": ("django.db.models.fields.IntegerField", [], {}),
            "veiculo_publicacao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "rh.quadro": {
            "Meta": {
                "ordering": "('cargo', 'especialidade')",
                "unique_together": "(('cargo', 'especialidade'),)",
                "object_name": "Quadro",
            },
            "cargo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Cargo']"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "especialidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Especialidade']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "rh.servidor": {
            "Meta": {
                "ordering": "('pessoa_fisica__nome', 'pessoa_fisica__cpf', 'matricula')",
                "object_name": "Servidor",
            },
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
            "capacidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Capacidade']", "null": "True", "blank": "True"},
            ),
            "categoria_cache": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'SERVIDOR_QUADRO'", "max_length": "40", "null": "True"},
            ),
            "chefe_imediato": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'subordinados'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "classificacao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "curso": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['rh.Curso']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "data_referencia_ferias": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_registro": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now_add": "True", "null": "True", "blank": "True"},
            ),
            "documento_digital": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'servidor'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['rh.DocumentoDigital']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "incapacidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.InCapacidade']", "null": "True", "blank": "True"},
            ),
            "lotacoes": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "to": "orm['rh.Lotacao']",
                    "null": "True",
                    "through": "orm['rh.ServidorLotacao']",
                    "symmetrical": "False",
                },
            ),
            "matricula": (
                "django.db.models.fields.IntegerField",
                [],
                {"unique": "True"},
            ),
            "matricula_origem": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "molestia": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['rh.Molestia']",
                    "unique": "True",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "numero_cartao_ponto": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "pessoa_fisica": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.PessoaFisica']"},
            ),
            "situacao_funcional_cache": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'NOT_FOUND'", "max_length": "40", "null": "True"},
            ),
            "tipo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'S'", "max_length": "1", "null": "True", "blank": "True"},
            ),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'servidor'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
            "vpi": (
                "django.db.models.fields.DecimalField",
                [],
                {
                    "default": "0",
                    "max_digits": "18",
                    "decimal_places": "2",
                    "blank": "True",
                },
            ),
        },
        "rh.servidorlotacao": {
            "Meta": {"object_name": "ServidorLotacao"},
            "anotacao_geral_lotacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.AnotacaoGeral']", "null": "True", "blank": "True"},
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "data_cadastro": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "data_vigencia": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True"},
            ),
            "data_vigencia_fim": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_vigencia_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True"},
            ),
            "designacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "lotacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'servidores_lotacao'",
                    "null": "True",
                    "to": "orm['rh.Lotacao']",
                },
            ),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "movimentacao_posse": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'lotacoes'",
                    "null": "True",
                    "on_delete": "models.SET_NULL",
                    "to": "orm['rh.MovimentacaoPosse']",
                },
            ),
            "provisorio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "publicacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Publicacao']", "null": "True", "blank": "True"},
            ),
            "servidor": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'servidor_lotacao'", "to": "orm['rh.Servidor']"},
            ),
        },
        "rh.telefone": {
            "Meta": {"object_name": "Telefone"},
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "created_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modified_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "modified_by": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "blank": "True",
                    "on_delete": "models.PROTECT",
                    "to": "orm['auth.User']",
                },
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "publico": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "tipo_telefone": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.unidadeadministrativa": {
            "Meta": {
                "ordering": "['nome']",
                "object_name": "UnidadeAdministrativa",
                "_ormbases": ["rh.OrgaoGeral"],
            },
            "email": (
                "django.db.models.fields.EmailField",
                [],
                {"max_length": "75", "null": "True", "blank": "True"},
            ),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True", "blank": "True"},
            ),
            "orgaogeral_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.OrgaoGeral']", "unique": "True", "primary_key": "True"},
            ),
            "pessoa_juridica": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['rh.PessoaJuridica']",
                    "unique": "True",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "previdencia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'como_previdencia_de_unidade_administrativa'",
                    "null": "True",
                    "to": "orm['rh.PessoaJuridica']",
                },
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['rh.PessoaFisica']",
                    "unique": "True",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
    }

    complete_apps = ["gecap"]
