# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ProsecutorAction.county'
        db.alter_column(
            "web_prosecutoraction",
            "county_id",
            self.gf("django.db.models.fields.related.ForeignKey")(to=orm["rh.Comarca"]),
        )

    def backwards(self, orm):

        # Changing field 'ProsecutorAction.county'
        db.alter_column(
            "web_prosecutoraction",
            "county_id",
            self.gf("django.db.models.fields.related.ForeignKey")(
                to=orm["web.CountyMarker"]
            ),
        )

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
                "ordering": "['codigo_cnpq', 'titulo']",
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
                {"max_length": "10", "null": "True"},
            ),
            "conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True"},
            ),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "dv_agencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True"},
            ),
            "dv_conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
                {"max_length": "20", "null": "True"},
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
                {"max_length": "6", "null": "True"},
            ),
            "tem_convenio": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"null": "True"},
            ),
        },
        "rh.capacidade": {
            "Meta": {"object_name": "Capacidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "250", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
        },
        "rh.circunscricao": {
            "Meta": {"object_name": "Circunscricao"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "tipo_conta": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.docsdadosespecificos": {
            "Meta": {"object_name": "DocsDadosEspecificos"},
            "especificidade": ("django.db.models.fields.IntegerField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.especialidade": {
            "Meta": {"ordering": "['nome']", "object_name": "Especialidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.incapacidade": {
            "Meta": {"object_name": "InCapacidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.instancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Instancia"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.microregiao": {
            "Meta": {"object_name": "MicroRegiao"},
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
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.molestia": {
            "Meta": {"object_name": "Molestia"},
            "data_laudo": ("django.db.models.fields.DateField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
                {"null": "True", "blank": "True"},
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
            "Meta": {"object_name": "Publicacao"},
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
            "especialidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Especialidade']", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
            "servidor_tipo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.TipoServidor']", "null": "True"},
            ),
            "situacao_funcional_cache": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'NOT_FOUND'", "max_length": "40", "null": "True"},
            ),
            "situacao_servidor": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "19"},
            ),
            "tipo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'S'", "max_length": "1", "null": "True", "blank": "True"},
            ),
            "tipo_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.TipoOrigem']", "null": "True", "blank": "True"},
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
            "data_alteracao": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now": "True", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
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
        "rh.tipoorigem": {
            "Meta": {"object_name": "TipoOrigem"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "rh.tiposervidor": {
            "Meta": {"ordering": "['nome']", "object_name": "TipoServidor"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
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
                {"max_length": "1", "null": "True"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
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
        "web.area": {
            "Meta": {"object_name": "Area"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "as_link": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_share": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "fullname": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "kind_of_content": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'area'", "max_length": "100", "null": "True"},
            ),
            "modules": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'sites'",
                    "null": "True",
                    "to": "orm['web.Module']",
                },
            ),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True", "db_index": "True"},
            ),
            "parent": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'children'", "null": "True", "to": "orm['web.Area']"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "256", "null": "True"},
            ),
        },
        "web.audio": {
            "Meta": {"object_name": "Audio", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'audios'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.choice": {
            "Meta": {"object_name": "Choice"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "choice": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "poll": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'choices'", "to": "orm['web.Poll']"},
            ),
            "votes": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "0", "db_index": "True"},
            ),
        },
        "web.comment": {
            "Meta": {"object_name": "Comment"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'comments'", "to": "orm['web.Content']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "person_email": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "person_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "text": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.common": {
            "Meta": {"object_name": "Common"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "null": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "150", "null": "True"},
            ),
        },
        "web.content": {
            "Meta": {
                "unique_together": "(('slug', 'create_date'),)",
                "object_name": "Content",
            },
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "areas": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'contents'",
                    "null": "True",
                    "through": "orm['web.ContentArea']",
                    "to": "orm['web.Area']",
                },
            ),
            "as_gallery": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "as_link": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "create_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "db_index": "True", "blank": "True"},
            ),
            "credits": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "has_comment": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_meta": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_tag": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "position": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "9999", "db_index": "True"},
            ),
            "publication_end": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "publication_start": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "published": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "published_date": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "db_index": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "views": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "0", "db_index": "True"},
            ),
        },
        "web.contentarea": {
            "Meta": {"object_name": "ContentArea"},
            "area": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'content_area'", "to": "orm['web.Area']"},
            ),
            "content": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'content_area'", "to": "orm['web.Content']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "original": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
        },
        "web.countymarker": {
            "Meta": {"object_name": "CountyMarker"},
            "county": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'county_marker'",
                    "unique": "True",
                    "to": "orm['rh.Comarca']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "marker": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'county_marker'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['web.MapMarker']",
                },
            ),
        },
        "web.file": {
            "Meta": {"object_name": "File", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'files'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.image": {
            "Meta": {"object_name": "Image", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'images'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.link": {
            "Meta": {"object_name": "Link", "_ormbases": ["web.Multimedia"]},
            "fullname": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "is_banner": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "kind": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "1", "db_index": "True"},
            ),
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "parent": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'children'", "null": "True", "to": "orm['web.Link']"},
            ),
        },
        "web.map": {
            "Meta": {"object_name": "Map", "_ormbases": ["web.Content"]},
            "center": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'centered_map'",
                    "unique": "True",
                    "to": "orm['web.MapMarker']",
                },
            ),
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "disable_default_ui": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "draggable": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "map_type_id": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "markers": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'maps'",
                    "null": "True",
                    "to": "orm['web.MapMarker']",
                },
            ),
            "max_zoom": ("django.db.models.fields.IntegerField", [], {"null": "True"}),
            "min_zoom": ("django.db.models.fields.IntegerField", [], {"null": "True"}),
            "zoom": ("django.db.models.fields.IntegerField", [], {"null": "True"}),
            "zoom_control": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
        "web.mapmarker": {
            "Meta": {"object_name": "MapMarker"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "latitute": ("django.db.models.fields.FloatField", [], {}),
            "longitude": ("django.db.models.fields.FloatField", [], {}),
        },
        "web.metakey": {
            "Meta": {"object_name": "MetaKey"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'metadata'",
                    "null": "True",
                    "to": "orm['web.Content']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "key": (
                "django.db.models.fields.CharField",
                [],
                {
                    "max_length": "128",
                    "unique": "True",
                    "null": "True",
                    "db_index": "True",
                },
            ),
        },
        "web.metavalue": {
            "Meta": {"object_name": "MetaValue"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "key": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'meta_values'", "to": "orm['web.MetaKey']"},
            ),
            "value": (
                "django.db.models.fields.CharField",
                [],
                {
                    "max_length": "384",
                    "unique": "True",
                    "null": "True",
                    "db_index": "True",
                },
            ),
        },
        "web.module": {
            "Meta": {"object_name": "Module", "_ormbases": ["web.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Common']", "unique": "True", "primary_key": "True"},
            ),
        },
        "web.multimedia": {
            "Meta": {"object_name": "Multimedia", "_ormbases": ["web.Content"]},
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "ged": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True"},
            ),
            "url_embed": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.poll": {
            "Meta": {"object_name": "Poll", "_ormbases": ["web.Content"]},
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "restricted": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "show_partial": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "users_who_voted": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'polls_voted'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "web.pollconditions": {
            "Meta": {"object_name": "PollConditions"},
            "description": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "expression": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "polls": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'conditions'",
                    "null": "True",
                    "to": "orm['web.Poll']",
                },
            ),
            "value": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "256", "null": "True"},
            ),
        },
        "web.post": {
            "Meta": {"object_name": "Post", "_ormbases": ["web.Content"]},
            "content_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Content']", "unique": "True", "primary_key": "True"},
            ),
            "has_audio": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_file": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_image": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_link": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "has_video": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "is_index": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "post": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'posts'", "null": "True", "to": "orm['web.Post']"},
            ),
            "shared": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "text": ("django.db.models.fields.TextField", [], {"null": "True"}),
        },
        "web.prosecutoraction": {
            "Meta": {"object_name": "ProsecutorAction", "_ormbases": ["web.Post"]},
            "county": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'prosecutor_actions'", "to": "orm['rh.Comarca']"},
            ),
            "decision_date": (
                "django.db.models.fields.DateField",
                [],
                {"db_index": "True"},
            ),
            "doc_number": (
                "django.db.models.fields.IntegerField",
                [],
                {"db_index": "True"},
            ),
            "filing": ("django.db.models.fields.TextField", [], {"null": "True"}),
            "post_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Post']", "unique": "True", "primary_key": "True"},
            ),
            "start_date": (
                "django.db.models.fields.DateField",
                [],
                {"db_index": "True"},
            ),
            "status": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'prosecutor_actions'",
                    "to": "orm['web.ProsecutorActionStatus']",
                },
            ),
        },
        "web.prosecutoractionstatus": {
            "Meta": {
                "object_name": "ProsecutorActionStatus",
                "_ormbases": ["web.Common"],
            },
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['web.Common']", "unique": "True", "primary_key": "True"},
            ),
        },
        "web.tag": {
            "Meta": {"object_name": "Tag"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "contents": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'tags'",
                    "null": "True",
                    "to": "orm['web.Content']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "384", "null": "True"},
            ),
        },
        "web.video": {
            "Meta": {"object_name": "Video", "_ormbases": ["web.Multimedia"]},
            "multimedia_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['web.Multimedia']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "posts": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'videos'",
                    "null": "True",
                    "to": "orm['web.Post']",
                },
            ),
        },
        "web.webgroup": {
            "Meta": {"object_name": "WebGroup"},
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True", "db_index": "True"},
            ),
            "area": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'groups'", "to": "orm['web.Area']"},
            ),
            "can_add": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_change": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_delete": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "can_publish": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128", "null": "True", "db_index": "True"},
            ),
            "users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'web_groups'",
                    "null": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
    }

    complete_apps = ["web"]
