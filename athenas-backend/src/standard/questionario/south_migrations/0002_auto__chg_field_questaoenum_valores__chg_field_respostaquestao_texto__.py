# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'QuestaoEnum.valores'
        db.alter_column(
            "qst_questaoenum",
            "valores",
            self.gf("django.db.models.fields.CharField")(max_length=100),
        )

        # Changing field 'RespostaQuestao.texto'
        db.alter_column(
            "qst_respostaquestao",
            "texto",
            self.gf("django.db.models.fields.TextField")(),
        )

        # Changing field 'QuestionarioChave.chave'
        db.alter_column(
            "qst_questionariochave",
            "chave",
            self.gf("django.db.models.fields.CharField")(default=None, max_length=100),
        )

        # Changing field 'Resposta.texto'
        db.alter_column(
            "qst_resposta", "texto", self.gf("django.db.models.fields.TextField")()
        )

        # Changing field 'Alternativa.texto'
        db.alter_column(
            "qst_alternativa",
            "texto",
            self.gf("django.db.models.fields.TextField")(default=""),
        )

        # Changing field 'Alternativa.valor'
        db.alter_column(
            "qst_alternativa",
            "valor",
            self.gf("django.db.models.fields.CharField")(default="", max_length=5),
        )

        # Changing field 'ReferenciaTextual.conteudo'
        db.alter_column(
            "qst_referenciatextual",
            "conteudo",
            self.gf("django.db.models.fields.TextField")(),
        )

        # Changing field 'ReferenciaTextual.label'
        db.alter_column(
            "qst_referenciatextual",
            "label",
            self.gf("django.db.models.fields.CharField")(default=None, max_length=100),
        )

        # Changing field 'Questionario.titulo'
        db.alter_column(
            "qst_questionario",
            "titulo",
            self.gf("django.db.models.fields.CharField")(default=None, max_length=50),
        )

        # Changing field 'Questionario.descricao'
        db.alter_column(
            "qst_questionario",
            "descricao",
            self.gf("django.db.models.fields.TextField")(),
        )

        # Changing field 'Elemento.label'
        db.alter_column(
            "qst_elemento",
            "label",
            self.gf("django.db.models.fields.CharField")(default=None, max_length=50),
        )

        # Changing field 'QuestionarioResposta.chave'
        db.alter_column(
            "qst_questionarioresposta",
            "chave",
            self.gf("django.db.models.fields.CharField")(default=None, max_length=64),
        )

        # Changing field 'Questao.enunciado'
        db.alter_column(
            "qst_questao",
            "enunciado",
            self.gf("django.db.models.fields.TextField")(default=None),
        )

    def backwards(self, orm):

        # Changing field 'QuestaoEnum.valores'
        db.alter_column(
            "qst_questaoenum",
            "valores",
            self.gf("django.db.models.fields.CharField")(max_length=100, null=True),
        )

        # Changing field 'RespostaQuestao.texto'
        db.alter_column(
            "qst_respostaquestao",
            "texto",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'QuestionarioChave.chave'
        db.alter_column(
            "qst_questionariochave",
            "chave",
            self.gf("django.db.models.fields.CharField")(max_length=100, null=True),
        )

        # Changing field 'Resposta.texto'
        db.alter_column(
            "qst_resposta",
            "texto",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'Alternativa.texto'
        db.alter_column(
            "qst_alternativa",
            "texto",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'Alternativa.valor'
        db.alter_column(
            "qst_alternativa",
            "valor",
            self.gf("django.db.models.fields.CharField")(max_length=5, null=True),
        )

        # Changing field 'ReferenciaTextual.conteudo'
        db.alter_column(
            "qst_referenciatextual",
            "conteudo",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'ReferenciaTextual.label'
        db.alter_column(
            "qst_referenciatextual",
            "label",
            self.gf("django.db.models.fields.CharField")(max_length=100, null=True),
        )

        # Changing field 'Questionario.titulo'
        db.alter_column(
            "qst_questionario",
            "titulo",
            self.gf("django.db.models.fields.CharField")(max_length=50, null=True),
        )

        # Changing field 'Questionario.descricao'
        db.alter_column(
            "qst_questionario",
            "descricao",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'Elemento.label'
        db.alter_column(
            "qst_elemento",
            "label",
            self.gf("django.db.models.fields.CharField")(max_length=50, null=True),
        )

        # Changing field 'QuestionarioResposta.chave'
        db.alter_column(
            "qst_questionarioresposta",
            "chave",
            self.gf("django.db.models.fields.CharField")(max_length=64, null=True),
        )

        # Changing field 'Questao.enunciado'
        db.alter_column(
            "qst_questao",
            "enunciado",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

    models = {
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
        "questionario.alternativa": {
            "Meta": {
                "ordering": "('ordem',)",
                "object_name": "Alternativa",
                "db_table": "'qst_alternativa'",
            },
            "grupo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "label": (
                "django.db.models.fields.CharField",
                [],
                {"default": "''", "max_length": "100", "null": "True"},
            ),
            "ordem": (
                "django.db.models.fields.PositiveSmallIntegerField",
                [],
                {"null": "True"},
            ),
            "questao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'alternativas'",
                    "null": "True",
                    "to": "orm['questionario.Questao']",
                },
            ),
            "texto": ("django.db.models.fields.TextField", [], {"blank": "True"}),
            "valor": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "5", "blank": "True"},
            ),
        },
        "questionario.elemento": {
            "Meta": {
                "ordering": "('ordem',)",
                "unique_together": "(['object_id', 'content_type'],)",
                "object_name": "Elemento",
                "db_table": "'qst_elemento'",
            },
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "elemento_pai": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'pai_elemento'",
                    "null": "True",
                    "to": "orm['questionario.Elemento']",
                },
            ),
            "grupo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "label": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
            "object_id": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "ordem": (
                "django.db.models.fields.PositiveSmallIntegerField",
                [],
                {"null": "True"},
            ),
            "questionario": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.Questionario']"},
            ),
        },
        "questionario.questao": {
            "Meta": {"object_name": "Questao", "db_table": "'qst_questao'"},
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "enunciado": ("django.db.models.fields.TextField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mista": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
        },
        "questionario.questaoaberta": {
            "Meta": {
                "object_name": "QuestaoAberta",
                "db_table": "'qst_questaoaberta'",
                "_ormbases": ["questionario.Questao"],
            },
            "questao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['questionario.Questao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "questionario.questaoenum": {
            "Meta": {
                "object_name": "QuestaoEnum",
                "db_table": "'qst_questaoenum'",
                "_ormbases": ["questionario.QuestaoMS"],
            },
            "questaoms_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['questionario.QuestaoMS']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "valores": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'1:1'", "max_length": "100"},
            ),
        },
        "questionario.questaoms": {
            "Meta": {
                "object_name": "QuestaoMS",
                "db_table": "'qst_questaoms'",
                "_ormbases": ["questionario.Questao"],
            },
            "questao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['questionario.Questao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "questionario.questionario": {
            "Meta": {
                "ordering": "['-ativo', 'titulo']",
                "object_name": "Questionario",
                "db_table": "'qst_questionario'",
            },
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "criado_em": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "data_fim": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_inicio": ("django.db.models.fields.DateField", [], {}),
            "descricao": ("django.db.models.fields.TextField", [], {"default": "''"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modificado_em": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "titulo": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
            "unico": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
        },
        "questionario.questionariochave": {
            "Meta": {
                "unique_together": "(('chave', 'questionario'),)",
                "object_name": "QuestionarioChave",
                "db_table": "'qst_questionariochave'",
            },
            "chave": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "questionario": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.Questionario']"},
            ),
        },
        "questionario.questionarioresposta": {
            "Meta": {
                "object_name": "QuestionarioResposta",
                "db_table": "'qst_questionarioresposta'",
            },
            "chave": ("django.db.models.fields.CharField", [], {"max_length": "64"}),
            "criado_em": (
                "django.db.models.fields.DateField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "questionario": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.Questionario']"},
            ),
        },
        "questionario.referenciatextual": {
            "Meta": {
                "ordering": "('label',)",
                "object_name": "ReferenciaTextual",
                "db_table": "'qst_referenciatextual'",
            },
            "conteudo": ("django.db.models.fields.TextField", [], {"default": "''"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "label": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
        },
        "questionario.resposta": {
            "Meta": {"object_name": "Resposta", "db_table": "'qst_resposta'"},
            "alternativa": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "to": "orm['questionario.Alternativa']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "peso": ("django.db.models.fields.IntegerField", [], {"default": "0"}),
            "questao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.Questao']"},
            ),
            "questionario_resposta": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.QuestionarioResposta']"},
            ),
            "texto": ("django.db.models.fields.TextField", [], {"default": "''"}),
        },
        "questionario.respostaquestao": {
            "Meta": {
                "unique_together": "(('questao', 'questionario_resposta'),)",
                "object_name": "RespostaQuestao",
                "db_table": "'qst_respostaquestao'",
            },
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "questao": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.Questao']"},
            ),
            "questionario_resposta": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['questionario.QuestionarioResposta']"},
            ),
            "texto": ("django.db.models.fields.TextField", [], {"default": "''"}),
        },
        "questionario.respostaquestaoaberta": {
            "Meta": {
                "object_name": "RespostaQuestaoAberta",
                "db_table": "'qst_resposta_questao_aberta'",
                "_ormbases": ["questionario.RespostaQuestao"],
            },
            "respostaquestao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['questionario.RespostaQuestao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "questionario.respostaquestaoms": {
            "Meta": {
                "object_name": "RespostaQuestaoMS",
                "db_table": "'qst_resposta_questao_ms'",
                "_ormbases": ["questionario.RespostaQuestao"],
            },
            "respostaquestao_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['questionario.RespostaQuestao']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
    }

    complete_apps = ["questionario"]
