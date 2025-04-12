# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        for a in orm.Avaliacao.objects.all():
            a.satisfacao = 6 - a.tipo_avaliacao.pk
            a.save()

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        "auth.group": {
            "Meta": {"object_name": "Group"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "80"},
            ),
            "permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "to": "orm['auth.Permission']",
                    "symmetrical": "False",
                    "blank": "True",
                },
            ),
        },
        "auth.permission": {
            "Meta": {
                "ordering": "(u'content_type__app_label', u'content_type__model', u'codename')",
                "unique_together": "((u'content_type', u'codename'),)",
                "object_name": "Permission",
            },
            "codename": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100"},
            ),
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
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
                {"max_length": "75", "blank": "True"},
            ),
            "first_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "blank": "True"},
            ),
            "groups": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {"to": "orm['auth.Group']", "symmetrical": "False", "blank": "True"},
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
                {"max_length": "30", "blank": "True"},
            ),
            "password": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "128"},
            ),
            "user_permissions": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "to": "orm['auth.Permission']",
                    "symmetrical": "False",
                    "blank": "True",
                },
            ),
            "username": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "30"},
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
                {"max_length": "100"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "model": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
            "name": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "titulo": ("django.db.models.fields.CharField", [], {"max_length": "200"}),
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
            "file": ("django.db.models.fields.CharField", [], {"max_length": "32"}),
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
                {"default": "'{}'", "max_length": "400", "blank": "True"},
            ),
            "header": (
                "django.db.models.fields.CharField",
                [],
                {"default": "''", "max_length": "30", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "message": ("django.db.models.fields.TextField", [], {"default": "''"}),
            "mid": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "30", "blank": "True"},
            ),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'INFO'", "max_length": "10"},
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
            "params": ("django.db.models.fields.CharField", [], {"max_length": "400"}),
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
                {"default": "'SYS'", "max_length": "10"},
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
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "conta": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
            "numero": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "3"},
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
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "codigo": ("django.db.models.fields.CharField", [], {"max_length": "12"}),
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
                {"default": "'S'", "max_length": "1"},
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
                {"default": "'EF'", "max_length": "2"},
            ),
            "unidade_administrativa": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.UnidadeAdministrativa']", "null": "True"},
            ),
        },
        "rh.carreira": {
            "Meta": {"object_name": "Carreira"},
            "codigo": ("django.db.models.fields.CharField", [], {"max_length": "10"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "rh.cbo": {
            "Meta": {"object_name": "Cbo"},
            "codigo": ("django.db.models.fields.CharField", [], {"max_length": "10"}),
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "250"},
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "rh.dadobancario": {
            "Meta": {"ordering": "['banco']", "object_name": "DadoBancario"},
            "agencia": ("django.db.models.fields.CharField", [], {"max_length": "15"}),
            "banco": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Banco']"},
            ),
            "conta_corrente_completa": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "tipo_conta": ("django.db.models.fields.IntegerField", [], {}),
        },
        "rh.docsdadosespecificos": {
            "Meta": {"object_name": "DocsDadosEspecificos"},
            "especificidade": ("django.db.models.fields.IntegerField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "valor": ("django.db.models.fields.CharField", [], {"max_length": "30"}),
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
            "numero": ("django.db.models.fields.CharField", [], {"max_length": "30"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "rh.especialidade": {
            "Meta": {"ordering": "['nome']", "object_name": "Especialidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "sigla": ("django.db.models.fields.CharField", [], {"max_length": "2"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "rh.incapacidade": {
            "Meta": {"object_name": "InCapacidade"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "rh.instancia": {
            "Meta": {"ordering": "['nome']", "object_name": "Instancia"},
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
                {"default": "'NOMEACAO'", "max_length": "30"},
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
            "cnpj": ("django.db.models.fields.CharField", [], {"max_length": "14"}),
            "pessoa_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['rh.Pessoa']", "unique": "True", "primary_key": "True"},
            ),
            "razao_social": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
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
                {"max_length": "4", "blank": "True"},
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
                {"default": "'SERVIDOR_QUADRO'", "max_length": "40"},
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
                {"default": "'NOT_FOUND'", "max_length": "40"},
            ),
            "situacao_servidor": (
                "django.db.models.fields.IntegerField",
                [],
                {"default": "19"},
            ),
            "tipo": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'S'", "max_length": "1", "blank": "True"},
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
            "numero": ("django.db.models.fields.CharField", [], {"max_length": "15"}),
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
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
                {"max_length": "1"},
            ),
            "instancia": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Instancia']", "null": "True", "blank": "True"},
            ),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
        "siatu.anexo": {
            "Meta": {"object_name": "Anexo"},
            "arquivo": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"related_name": "'+'", "unique": "True", "to": "orm['ged.Arquivo']"},
            ),
            "chamado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'anexos'", "to": "orm['siatu.Chamado']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
        },
        "siatu.atendente": {
            "Meta": {"ordering": "('usuario__username',)", "object_name": "Atendente"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "notificacao_receber_chamado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "usuario": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['auth.User']", "unique": "True"},
            ),
        },
        "siatu.atendentesservicos": {
            "Meta": {
                "ordering": "('atendente__usuario__username', 'servico__nome')",
                "unique_together": "(('servico', 'atendente'),)",
                "object_name": "AtendentesServicos",
                "db_table": "'siatu_atendentes_servicos'",
            },
            "atendente": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'relacaoAt_Serv'", "to": "orm['siatu.Atendente']"},
            ),
            "distribuicao_automatica": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "servico": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'relacaoAt_Serv'", "to": "orm['siatu.Servico']"},
            ),
        },
        "siatu.avaliacao": {
            "Meta": {"object_name": "Avaliacao"},
            "chamado": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['siatu.Chamado']", "unique": "True"},
            ),
            "esclarecimento": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"default": "0"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "motivo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "250", "null": "True"},
            ),
            "presteza": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"default": "0"},
            ),
            "replica": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True"},
            ),
            "satisfacao": ("django.db.models.fields.SmallIntegerField", [], {}),
            "tempo": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"default": "0"},
            ),
            "tipo_avaliacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['siatu.TipoAvaliacao']"},
            ),
        },
        "siatu.baseconhecimento": {
            "Meta": {
                "ordering": "('objeto__descricao',)",
                "object_name": "BaseConhecimento",
                "db_table": "'siatu_base_conhecimento'",
            },
            "arquivo": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'+'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['ged.Arquivo']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modelo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['siatu.Modelo']", "null": "True"},
            ),
            "objeto": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['siatu.Objeto']"},
            ),
            "problema": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "500"},
            ),
            "solucao": ("django.db.models.fields.TextField", [], {}),
        },
        "siatu.chamado": {
            "Meta": {"ordering": "('-pk',)", "object_name": "Chamado"},
            "ano": ("django.db.models.fields.SmallIntegerField", [], {}),
            "atendentes": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'chamados'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Atendente']",
                },
            ),
            "base_conhecimento": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'chamados'",
                    "null": "True",
                    "through": "orm['siatu.ItemBaseConhecimento']",
                    "to": "orm['siatu.BaseConhecimento']",
                },
            ),
            "cache_numero": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "db_index": "True"},
            ),
            "cancelado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "cfg_email_atendente": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['siatu.ConfigEmailAtendente']"},
            ),
            "cfg_email_solicitante": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['siatu.ConfigEmailSolicitante']"},
            ),
            "chamado_anterior": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'chamado_reincidente'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['siatu.Chamado']",
                },
            ),
            "data_fila_atendimento": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True"},
            ),
            "fila": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'chamados'",
                    "null": "True",
                    "to": "orm['siatu.FilaUnica']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "motivo_cancelado": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
            "motivo_urgencia": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
            "nao_institucional": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "numero": ("django.db.models.fields.SmallIntegerField", [], {}),
            "reincidencia": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['siatu.Reincidencia']", "unique": "True", "null": "True"},
            ),
            "relatorio": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "servico": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'chamados'", "to": "orm['siatu.Servico']"},
            ),
            "solicitacao": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['siatu.Solicitacao']", "unique": "True"},
            ),
            "status_atual": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'+'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['siatu.Status']",
                },
            ),
            "terceirizada": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'chamados'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Terceirizada']",
                },
            ),
            "terceiro_interno": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'chamados'",
                    "symmetrical": "False",
                    "to": "orm['siatu.TerceiroInterno']",
                },
            ),
            "urgente": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
        "siatu.configemailatendente": {
            "Meta": {"object_name": "ConfigEmailAtendente"},
            "apos_avaliacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "transferido_atendente": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
        },
        "siatu.configemailsolicitante": {
            "Meta": {"object_name": "ConfigEmailSolicitante"},
            "aguardando_avaliacao": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "garantia": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "terceirizada": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "transferido_atendente": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "viagem": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
        },
        "siatu.distribuicaoautomatica": {
            "Meta": {
                "object_name": "DistribuicaoAutomatica",
                "db_table": "'siatu_distribuicao_automatica'",
            },
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "servico": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'distribuicao_automatica'",
                    "unique": "True",
                    "to": "orm['siatu.Servico']",
                },
            ),
            "solicitantes": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'+'",
                    "symmetrical": "False",
                    "to": "orm['auth.User']",
                },
            ),
            "tipo_atendimento": (
                "django.db.models.fields.CommaSeparatedIntegerField",
                [],
                {"max_length": "15"},
            ),
        },
        "siatu.filaunica": {
            "Meta": {
                "unique_together": "(('servico', 'localidade'),)",
                "object_name": "FilaUnica",
                "db_table": "'siatu_fila_unica'",
            },
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "localidade": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50"},
            ),
            "servico": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'filas'", "to": "orm['siatu.Servico']"},
            ),
        },
        "siatu.gerente": {
            "Meta": {"ordering": "('usuario__username',)", "object_name": "Gerente"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "usuario": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {"to": "orm['auth.User']", "unique": "True"},
            ),
        },
        "siatu.itembaseconhecimento": {
            "Meta": {
                "ordering": "('base_conhecimento__objeto__descricao',)",
                "unique_together": "(('chamado', 'base_conhecimento'),)",
                "object_name": "ItemBaseConhecimento",
                "db_table": "'siatu_item_base_conhecimento'",
            },
            "base_conhecimento": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'itens_base_conhecimento'",
                    "to": "orm['siatu.BaseConhecimento']",
                },
            ),
            "chamado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'itens_base_conhecimento'",
                    "to": "orm['siatu.Chamado']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "info": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "siatu.modelo": {
            "Meta": {"ordering": "('descricao',)", "object_name": "Modelo"},
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "100"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "informatica": (
                "django.db.models.fields.NullBooleanField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "siatu.objeto": {
            "Meta": {"ordering": "('descricao',)", "object_name": "Objeto"},
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "100"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "informatica": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "modelos": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'objetos'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Modelo']",
                },
            ),
        },
        "siatu.reincidencia": {
            "Meta": {"object_name": "Reincidencia"},
            "confirm_atendente": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "motivo_gerente": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "opiniao_atendente": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "parecer": (
                "django.db.models.fields.NullBooleanField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "siatu.servico": {
            "Meta": {"ordering": "('nome',)", "object_name": "Servico"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "lista_atendentes": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'servicos_vinculados'",
                    "symmetrical": "False",
                    "through": "orm['siatu.AtendentesServicos']",
                    "to": "orm['siatu.Atendente']",
                },
            ),
            "lista_gerentes": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'servicos_vinculados'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Gerente']",
                },
            ),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "150"}),
            "servico_superior": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'subservicos'",
                    "null": "True",
                    "to": "orm['siatu.Servico']",
                },
            ),
        },
        "siatu.solicitacao": {
            "Meta": {"ordering": "('-pk',)", "object_name": "Solicitacao"},
            "chamado_anterior": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'+'", "null": "True", "to": "orm['siatu.Chamado']"},
            ),
            "descricao_problema": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "600"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "reincidencia": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "servico": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'solicitacoes'", "to": "orm['siatu.Servico']"},
            ),
            "solicitante": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'+'", "to": "orm['auth.User']"},
            ),
            "tipo": ("django.db.models.fields.SmallIntegerField", [], {"default": "0"}),
            "usuario": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'+'", "to": "orm['auth.User']"},
            ),
        },
        "siatu.status": {
            "Meta": {"ordering": "('data_inicio',)", "object_name": "Status"},
            "chamado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'historico_status'", "to": "orm['siatu.Chamado']"},
            ),
            "data_inicio": ("django.db.models.fields.DateTimeField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "motivo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "300", "null": "True"},
            ),
            "previsao_fim": ("django.db.models.fields.DateField", [], {"null": "True"}),
            "status": ("django.db.models.fields.SmallIntegerField", [], {}),
            "terceirizada": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'+'",
                    "null": "True",
                    "to": "orm['siatu.Terceirizada']",
                },
            ),
        },
        "siatu.terceirizada": {
            "Meta": {"ordering": "('nome',)", "object_name": "Terceirizada"},
            "cnpj": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "80"}),
        },
        "siatu.terceirointerno": {
            "Meta": {"ordering": "('nome',)", "object_name": "TerceiroInterno"},
            "cpf": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
            "endereco": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": ("django.db.models.fields.CharField", [], {"max_length": "80"}),
            "telefone": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
        },
        "siatu.tipoavaliacao": {
            "Meta": {"ordering": "('pk',)", "object_name": "TipoAvaliacao"},
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50"},
            ),
            "iconcls": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "necessita_motivo": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
        "siatu.transferencia": {
            "Meta": {"ordering": "('pk',)", "object_name": "Transferencia"},
            "aceito_por": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'+'", "null": "True", "to": "orm['auth.User']"},
            ),
            "atendente_anterior": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'transferencias_como_remetente'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Atendente']",
                },
            ),
            "atendente_posterior": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'transferencias_como_destinatario'",
                    "symmetrical": "False",
                    "to": "orm['siatu.Atendente']",
                },
            ),
            "cancelado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "chamado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'transferencias'", "to": "orm['siatu.Chamado']"},
            ),
            "data_aceite": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True"},
            ),
            "data_pedido": ("django.db.models.fields.DateTimeField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "motivo": ("django.db.models.fields.CharField", [], {"max_length": "300"}),
            "pedido_por": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'+'", "to": "orm['auth.User']"},
            ),
        },
    }

    complete_apps = ["siatu"]
    symmetrical = True
