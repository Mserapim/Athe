# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Manifestacao'
        db.create_table(
            "ouvidoria_manifestacao",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "mora_no_municipio_referido",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=1, null=True
                    ),
                ),
                (
                    "protocolo",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        related_name="manifestacao",
                        unique=True,
                        to=orm["protocolo.Protocolo"],
                    ),
                ),
            ),
        )
        db.send_create_signal("ouvidoria", ["Manifestacao"])

    def backwards(self, orm):

        # Deleting model 'Manifestacao'
        db.delete_table("ouvidoria_manifestacao")

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
            "message": ("django.db.models.fields.TextField", [], {"null": "True"}),
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
        "ouvidoria.manifestacao": {
            "Meta": {"object_name": "Manifestacao"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mora_no_municipio_referido": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "1", "null": "True"},
            ),
            "protocolo": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'manifestacao'",
                    "unique": "True",
                    "to": "orm['protocolo.Protocolo']",
                },
            ),
        },
        "protocolo.anexo": {
            "Meta": {"object_name": "Anexo"},
            "arquivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
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
        "protocolo.movimentacao": {
            "Meta": {
                "ordering": "['data_encaminhamento']",
                "object_name": "Movimentacao",
            },
            "anexos": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'movimentacao'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['protocolo.Anexo']",
                },
            ),
            "data_encaminhamento": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_recebimento": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "deferido": (
                "django.db.models.fields.NullBooleanField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "destinatario": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'mov_destinatario'",
                    "null": "True",
                    "to": "orm['rh.Pessoa']",
                },
            ),
            "encaminhado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "lotacao_criacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'mov_lotacao_criacao'",
                    "null": "True",
                    "to": "orm['rh.OrgaoGeral']",
                },
            ),
            "lotacao_destino": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'mov_lotacao_destino'",
                    "null": "True",
                    "to": "orm['rh.OrgaoGeral']",
                },
            ),
            "lotacao_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'mov_lotacao_origem'", "to": "orm['rh.OrgaoGeral']"},
            ),
            "parecer": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "passo": ("django.db.models.fields.IntegerField", [], {}),
            "protocolo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'movimentacoes'", "to": "orm['protocolo.Protocolo']"},
            ),
            "servidor_destino": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'mov_servidor_destino'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "servidor_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'mov_servidor_origem'", "to": "orm['rh.Servidor']"},
            ),
            "urgente": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
        "protocolo.protocolo": {
            "Meta": {"object_name": "Protocolo"},
            "assunto": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255", "null": "True"},
            ),
            "chancela": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "30", "unique": "True", "null": "True", "blank": "True"},
            ),
            "codigo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "unique": "True", "null": "True"},
            ),
            "data_criacao": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "deferido": (
                "django.db.models.fields.NullBooleanField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "encaminhado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "excluido": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "finalizado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "grupo": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
            "habilitado": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "interessado": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'prot_interessado'", "to": "orm['rh.Pessoa']"},
            ),
            "lotacao_criacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'prot_lotacao_criacao'",
                    "null": "True",
                    "to": "orm['rh.OrgaoGeral']",
                },
            ),
            "midia": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "orgao_geral_destino": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'prot_orgao_destino'",
                    "null": "True",
                    "to": "orm['rh.OrgaoGeral']",
                },
            ),
            "orgao_geral_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'prot_orgao_origem'", "to": "orm['rh.OrgaoGeral']"},
            ),
            "protocolo_externo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "referencias": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'prot_referencias'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['protocolo.Referencia']",
                },
            ),
            "resumo": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "serial": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "blank": "True"},
            ),
            "servidor_origem": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'prot_servidor_origem'", "to": "orm['rh.Servidor']"},
            ),
            "sigiloso": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "tipo_documento": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'prot_tipo_documento'",
                    "to": "orm['protocolo.TipoDocumento']",
                },
            ),
        },
        "protocolo.referencia": {
            "Meta": {"object_name": "Referencia"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "movimentacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['protocolo.Movimentacao']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "protocolo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['protocolo.Protocolo']", "null": "True", "blank": "True"},
            ),
        },
        "protocolo.tipodocumento": {
            "Meta": {"object_name": "TipoDocumento"},
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
                {"null": "True", "blank": "True"},
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
                {"to": "orm['rh.Servidor']"},
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
                {"null": "True", "blank": "True"},
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
                {"null": "True", "blank": "True"},
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
                "ordering": "('-id',)",
                "object_name": "MovimentacaoPessoal",
                "db_table": "'rh_movpessoal'",
            },
            "anotacao_geral": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'anotgeral'",
                    "null": "True",
                    "to": "orm['rh.AnotacaoGeral']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "publicacao_movimentacao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Publicacao']", "null": "True", "blank": "True"},
            ),
            "quad_ano": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "8", "null": "True", "blank": "True"},
            ),
            "servidor": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Servidor']"},
            ),
            "texto": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "texto_cache": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
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
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "poder": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
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
                {"max_length": "12", "null": "True", "blank": "True"},
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
                {"max_length": "100", "null": "True", "blank": "True"},
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
            "estado_civil": ("django.db.models.fields.IntegerField", [], {}),
            "fator_rh": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "foto": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['ged.Arquivo']", "null": "True", "blank": "True"},
            ),
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True"},
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
            "raca_cor": ("django.db.models.fields.IntegerField", [], {}),
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
            "Meta": {
                "unique_together": "(('tipo', 'numero', 'ano', 'veiculo_publicacao', 'numero_publicacao'),)",
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
            "tipo": ("django.db.models.fields.IntegerField", [], {}),
            "veiculo_publicacao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
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
                    "to": "orm['ged.Arquivo']",
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
                {"to": "orm['rh.TipoServidor']"},
            ),
            "situacao_servidor": ("django.db.models.fields.IntegerField", [], {}),
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
                    "null": "True",
                    "max_digits": "18",
                    "decimal_places": "12",
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
    }

    complete_apps = ["ouvidoria"]
