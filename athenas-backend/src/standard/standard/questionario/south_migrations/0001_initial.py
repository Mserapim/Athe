# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Questao'
        db.create_table(
            "qst_questao",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                ("enunciado", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "mista",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
                (
                    "content_type",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["contenttypes.ContentType"]
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["Questao"])

        # Adding model 'Alternativa'
        db.create_table(
            "qst_alternativa",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "label",
                    self.gf("django.db.models.fields.CharField")(
                        default="", max_length=100, null=True
                    ),
                ),
                (
                    "texto",
                    self.gf("django.db.models.fields.TextField")(null=True, blank=True),
                ),
                (
                    "valor",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=5, null=True, blank=True
                    ),
                ),
                (
                    "grupo",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True, blank=True
                    ),
                ),
                (
                    "ordem",
                    self.gf("django.db.models.fields.PositiveSmallIntegerField")(
                        null=True
                    ),
                ),
                (
                    "questao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="alternativas",
                        null=True,
                        to=orm["questionario.Questao"],
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["Alternativa"])

        # Adding model 'QuestaoAberta'
        db.create_table(
            "qst_questaoaberta",
            (
                (
                    "questao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["questionario.Questao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["QuestaoAberta"])

        # Adding model 'QuestaoMS'
        db.create_table(
            "qst_questaoms",
            (
                (
                    "questao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["questionario.Questao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["QuestaoMS"])

        # Adding model 'QuestaoEnum'
        db.create_table(
            "qst_questaoenum",
            (
                (
                    "questaoms_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["questionario.QuestaoMS"], unique=True, primary_key=True
                    ),
                ),
                (
                    "valores",
                    self.gf("django.db.models.fields.CharField")(
                        default="1:1", max_length=100, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["QuestaoEnum"])

        # Adding model 'Questionario'
        db.create_table(
            "qst_questionario",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "titulo",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                ("descricao", self.gf("django.db.models.fields.TextField")(null=True)),
                ("data_inicio", self.gf("django.db.models.fields.DateField")()),
                (
                    "data_fim",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "criado_em",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
                (
                    "modificado_em",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now=True, blank=True
                    ),
                ),
                (
                    "ativo",
                    self.gf("django.db.models.fields.BooleanField")(default=True),
                ),
                (
                    "unico",
                    self.gf("django.db.models.fields.BooleanField")(default=True),
                ),
            ),
        )
        db.send_create_signal("questionario", ["Questionario"])

        # Adding model 'QuestionarioChave'
        db.create_table(
            "qst_questionariochave",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "chave",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=100, null=True
                    ),
                ),
                (
                    "questionario",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Questionario"]
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["QuestionarioChave"])

        # Adding unique constraint on 'QuestionarioChave', fields ['chave', 'questionario']
        db.create_unique("qst_questionariochave", ["chave", "questionario_id"])

        # Adding model 'ReferenciaTextual'
        db.create_table(
            "qst_referenciatextual",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "label",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=100, null=True
                    ),
                ),
                ("conteudo", self.gf("django.db.models.fields.TextField")(null=True)),
            ),
        )
        db.send_create_signal("questionario", ["ReferenciaTextual"])

        # Adding model 'Elemento'
        db.create_table(
            "qst_elemento",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "questionario",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Questionario"]
                    ),
                ),
                (
                    "content_type",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["contenttypes.ContentType"]
                    ),
                ),
                (
                    "object_id",
                    self.gf("django.db.models.fields.PositiveIntegerField")(),
                ),
                (
                    "ordem",
                    self.gf("django.db.models.fields.PositiveSmallIntegerField")(
                        null=True
                    ),
                ),
                (
                    "label",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "grupo",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "elemento_pai",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="pai_elemento",
                        null=True,
                        to=orm["questionario.Elemento"],
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["Elemento"])

        # Adding unique constraint on 'Elemento', fields ['object_id', 'content_type']
        db.create_unique("qst_elemento", ["object_id", "content_type_id"])

        # Adding model 'QuestionarioResposta'
        db.create_table(
            "qst_questionarioresposta",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "chave",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=64, null=True
                    ),
                ),
                (
                    "questionario",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Questionario"]
                    ),
                ),
                (
                    "criado_em",
                    self.gf("django.db.models.fields.DateField")(
                        auto_now_add=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["QuestionarioResposta"])

        # Adding model 'RespostaQuestao'
        db.create_table(
            "qst_respostaquestao",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "questao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Questao"]
                    ),
                ),
                (
                    "questionario_resposta",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.QuestionarioResposta"]
                    ),
                ),
                ("texto", self.gf("django.db.models.fields.TextField")(null=True)),
                (
                    "content_type",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["contenttypes.ContentType"]
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["RespostaQuestao"])

        # Adding unique constraint on 'RespostaQuestao', fields ['questao', 'questionario_resposta']
        db.create_unique(
            "qst_respostaquestao", ["questao_id", "questionario_resposta_id"]
        )

        # Adding model 'RespostaQuestaoMS'
        db.create_table(
            "qst_resposta_questao_ms",
            (
                (
                    "respostaquestao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["questionario.RespostaQuestao"],
                        unique=True,
                        primary_key=True,
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["RespostaQuestaoMS"])

        # Adding model 'RespostaQuestaoAberta'
        db.create_table(
            "qst_resposta_questao_aberta",
            (
                (
                    "respostaquestao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["questionario.RespostaQuestao"],
                        unique=True,
                        primary_key=True,
                    ),
                ),
            ),
        )
        db.send_create_signal("questionario", ["RespostaQuestaoAberta"])

        # Adding model 'Resposta'
        db.create_table(
            "qst_resposta",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "questao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Questao"]
                    ),
                ),
                (
                    "questionario_resposta",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.QuestionarioResposta"]
                    ),
                ),
                (
                    "alternativa",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["questionario.Alternativa"], null=True, blank=True
                    ),
                ),
                ("texto", self.gf("django.db.models.fields.TextField")(null=True)),
                ("peso", self.gf("django.db.models.fields.IntegerField")(default=1)),
            ),
        )
        db.send_create_signal("questionario", ["Resposta"])

    def backwards(self, orm):
        # Removing unique constraint on 'RespostaQuestao', fields ['questao', 'questionario_resposta']
        db.delete_unique(
            "qst_respostaquestao", ["questao_id", "questionario_resposta_id"]
        )

        # Removing unique constraint on 'Elemento', fields ['object_id', 'content_type']
        db.delete_unique("qst_elemento", ["object_id", "content_type_id"])

        # Removing unique constraint on 'QuestionarioChave', fields ['chave', 'questionario']
        db.delete_unique("qst_questionariochave", ["chave", "questionario_id"])

        # Deleting model 'Questao'
        db.delete_table("qst_questao")

        # Deleting model 'Alternativa'
        db.delete_table("qst_alternativa")

        # Deleting model 'QuestaoAberta'
        db.delete_table("qst_questaoaberta")

        # Deleting model 'QuestaoMS'
        db.delete_table("qst_questaoms")

        # Deleting model 'QuestaoEnum'
        db.delete_table("qst_questaoenum")

        # Deleting model 'Questionario'
        db.delete_table("qst_questionario")

        # Deleting model 'QuestionarioChave'
        db.delete_table("qst_questionariochave")

        # Deleting model 'ReferenciaTextual'
        db.delete_table("qst_referenciatextual")

        # Deleting model 'Elemento'
        db.delete_table("qst_elemento")

        # Deleting model 'QuestionarioResposta'
        db.delete_table("qst_questionarioresposta")

        # Deleting model 'RespostaQuestao'
        db.delete_table("qst_respostaquestao")

        # Deleting model 'RespostaQuestaoMS'
        db.delete_table("qst_resposta_questao_ms")

        # Deleting model 'RespostaQuestaoAberta'
        db.delete_table("qst_resposta_questao_aberta")

        # Deleting model 'Resposta'
        db.delete_table("qst_resposta")

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
            "texto": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "valor": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "5", "null": "True", "blank": "True"},
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
            "label": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
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
            "enunciado": ("django.db.models.fields.TextField", [], {"null": "True"}),
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
                {"default": "'1:1'", "max_length": "100", "null": "True"},
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
            "descricao": ("django.db.models.fields.TextField", [], {"null": "True"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "modificado_em": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "titulo": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "unico": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
        },
        "questionario.questionariochave": {
            "Meta": {
                "unique_together": "(('chave', 'questionario'),)",
                "object_name": "QuestionarioChave",
                "db_table": "'qst_questionariochave'",
            },
            "chave": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
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
            "chave": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "64", "null": "True"},
            ),
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
            "conteudo": ("django.db.models.fields.TextField", [], {"null": "True"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "label": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
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
            "peso": ("django.db.models.fields.IntegerField", [], {"default": "1"}),
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
            "texto": ("django.db.models.fields.TextField", [], {"null": "True"}),
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
            "texto": ("django.db.models.fields.TextField", [], {"null": "True"}),
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
