# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Planejamento'
        db.create_table(
            "pe_planejamento",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "descricao",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, unique=True, null=True
                    ),
                ),
                (
                    "data_inicio",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "data_termino",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "metodo_analise",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                ("limite_alta", self.gf("django.db.models.fields.IntegerField")()),
                ("limite_baixa", self.gf("django.db.models.fields.IntegerField")()),
            ),
        )
        db.send_create_signal("pe", ["Planejamento"])

        # Adding M2M table for field objetivo on 'Planejamento'
        db.create_table(
            "pe_planejamento_objetivo",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("planejamento", models.ForeignKey(orm["pe.planejamento"], null=False)),
                ("objetivo", models.ForeignKey(orm["pe.objetivo"], null=False)),
            ),
        )
        db.create_unique("pe_planejamento_objetivo", ["planejamento_id", "objetivo_id"])

        # Adding model 'Objetivo'
        db.create_table(
            "pe_objetivo",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "nome",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, unique=True, null=True
                    ),
                ),
                (
                    "descricao",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, unique=True, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["Objetivo"])

        # Adding M2M table for field projeto on 'Objetivo'
        db.create_table(
            "pe_objetivo_projeto",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("objetivo", models.ForeignKey(orm["pe.objetivo"], null=False)),
                ("projeto", models.ForeignKey(orm["pe.projeto"], null=False)),
            ),
        )
        db.create_unique("pe_objetivo_projeto", ["objetivo_id", "projeto_id"])

        # Adding M2M table for field indicador on 'Objetivo'
        db.create_table(
            "pe_objetivo_indicador",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("objetivo", models.ForeignKey(orm["pe.objetivo"], null=False)),
                ("indicador", models.ForeignKey(orm["pe.indicador"], null=False)),
            ),
        )
        db.create_unique("pe_objetivo_indicador", ["objetivo_id", "indicador_id"])

        # Adding model 'Analise'
        db.create_table(
            "pe_analise",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "objetivo",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="fkey_objetivo_avaliacao", to=orm["pe.Objetivo"]
                    ),
                ),
                (
                    "responsavel",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="fkey_servidor_analise",
                        null=True,
                        to=orm["rh.Servidor"],
                    ),
                ),
                (
                    "data",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "tendencia",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "analise",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True, blank=True
                    ),
                ),
                (
                    "recomendacoes",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["Analise"])

        # Adding model 'Periodo'
        db.create_table(
            "pe_periodo",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "nome",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, unique=True, null=True
                    ),
                ),
                ("dias", self.gf("django.db.models.fields.IntegerField")()),
            ),
        )
        db.send_create_signal("pe", ["Periodo"])

        # Adding model 'Indicador'
        db.create_table(
            "pe_indicador",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "nome",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, unique=True, null=True
                    ),
                ),
                (
                    "descricao",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True
                    ),
                ),
                (
                    "tipo",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "periodo",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="fkey_periodo_indicador", to=orm["pe.Periodo"]
                    ),
                ),
                (
                    "peso",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["Indicador"])

        # Adding M2M table for field indicadormeta on 'Indicador'
        db.create_table(
            "pe_indicador_indicadormeta",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("indicador", models.ForeignKey(orm["pe.indicador"], null=False)),
                (
                    "indicadormeta",
                    models.ForeignKey(orm["pe.indicadormeta"], null=False),
                ),
            ),
        )
        db.create_unique(
            "pe_indicador_indicadormeta", ["indicador_id", "indicadormeta_id"]
        )

        # Adding model 'IndicadorValor'
        db.create_table(
            "pe_indicadorvalor",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "indicador",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="fkey_indicador_indicadorvalor",
                        to=orm["pe.Indicador"],
                    ),
                ),
                (
                    "data",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "valor",
                    self.gf("django.db.models.fields.DecimalField")(
                        max_digits=10, decimal_places=4
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["IndicadorValor"])

        # Adding model 'IndicadorMeta'
        db.create_table(
            "pe_indicadormeta",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "data",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "valor",
                    self.gf("django.db.models.fields.DecimalField")(
                        max_digits=10, decimal_places=4
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["IndicadorMeta"])

        # Adding model 'AnaliseIndicador'
        db.create_table(
            "pe_analiseindicador",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "indicador",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="fkey_analiseindicador_avaliacao",
                        to=orm["pe.Indicador"],
                    ),
                ),
                (
                    "responsavel",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="fkey_servidor_analiseindicador",
                        null=True,
                        to=orm["rh.Servidor"],
                    ),
                ),
                (
                    "data",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "tendencia",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "analise",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True, blank=True
                    ),
                ),
                (
                    "recomendacoes",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["AnaliseIndicador"])

        # Adding model 'Projeto'
        db.create_table(
            "pe_projeto",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "nome",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, unique=True, null=True
                    ),
                ),
                (
                    "descricao",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2000, null=True, blank=True
                    ),
                ),
                (
                    "responsavel",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="fkey_servidor_projeto",
                        null=True,
                        to=orm["rh.Servidor"],
                    ),
                ),
                (
                    "data_inicio",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "data_termino",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "status",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "andamento",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["Projeto"])

        # Adding model 'AndamentoProjeto'
        db.create_table(
            "pe_andamentoprojeto",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "projeto",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="fkey_projeto_andamentoprojeto",
                        to=orm["pe.Projeto"],
                    ),
                ),
                (
                    "data",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "concluido",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("pe", ["AndamentoProjeto"])

    def backwards(self, orm):

        # Deleting model 'Planejamento'
        db.delete_table("pe_planejamento")

        # Removing M2M table for field objetivo on 'Planejamento'
        db.delete_table("pe_planejamento_objetivo")

        # Deleting model 'Objetivo'
        db.delete_table("pe_objetivo")

        # Removing M2M table for field projeto on 'Objetivo'
        db.delete_table("pe_objetivo_projeto")

        # Removing M2M table for field indicador on 'Objetivo'
        db.delete_table("pe_objetivo_indicador")

        # Deleting model 'Analise'
        db.delete_table("pe_analise")

        # Deleting model 'Periodo'
        db.delete_table("pe_periodo")

        # Deleting model 'Indicador'
        db.delete_table("pe_indicador")

        # Removing M2M table for field indicadormeta on 'Indicador'
        db.delete_table("pe_indicador_indicadormeta")

        # Deleting model 'IndicadorValor'
        db.delete_table("pe_indicadorvalor")

        # Deleting model 'IndicadorMeta'
        db.delete_table("pe_indicadormeta")

        # Deleting model 'AnaliseIndicador'
        db.delete_table("pe_analiseindicador")

        # Deleting model 'Projeto'
        db.delete_table("pe_projeto")

        # Deleting model 'AndamentoProjeto'
        db.delete_table("pe_andamentoprojeto")

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
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
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
            "Meta": {"object_name": "Notification", "db_table": "'eng_notification'"},
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
        "pe.analise": {
            "Meta": {"object_name": "Analise"},
            "analise": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "data": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "objetivo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'fkey_objetivo_avaliacao'",
                    "to": "orm['pe.Objetivo']",
                },
            ),
            "recomendacoes": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'fkey_servidor_analise'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "tendencia": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "pe.analiseindicador": {
            "Meta": {"object_name": "AnaliseIndicador"},
            "analise": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "data": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicador": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'fkey_analiseindicador_avaliacao'",
                    "to": "orm['pe.Indicador']",
                },
            ),
            "recomendacoes": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'fkey_servidor_analiseindicador'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "tendencia": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "pe.andamentoprojeto": {
            "Meta": {"object_name": "AndamentoProjeto"},
            "concluido": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "data": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "projeto": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'fkey_projeto_andamentoprojeto'",
                    "to": "orm['pe.Projeto']",
                },
            ),
        },
        "pe.indicador": {
            "Meta": {"object_name": "Indicador"},
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicadormeta": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['pe.IndicadorMeta']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "unique": "True", "null": "True"},
            ),
            "periodo": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'fkey_periodo_indicador'", "to": "orm['pe.Periodo']"},
            ),
            "peso": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "tipo": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
        },
        "pe.indicadormeta": {
            "Meta": {"object_name": "IndicadorMeta"},
            "data": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "valor": (
                "django.db.models.fields.DecimalField",
                [],
                {"max_digits": "10", "decimal_places": "4"},
            ),
        },
        "pe.indicadorvalor": {
            "Meta": {"object_name": "IndicadorValor"},
            "data": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicador": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'fkey_indicador_indicadorvalor'",
                    "to": "orm['pe.Indicador']",
                },
            ),
            "valor": (
                "django.db.models.fields.DecimalField",
                [],
                {"max_digits": "10", "decimal_places": "4"},
            ),
        },
        "pe.objetivo": {
            "Meta": {"object_name": "Objetivo"},
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "unique": "True", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "indicador": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['pe.Indicador']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "unique": "True", "null": "True"},
            ),
            "projeto": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['pe.Projeto']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "pe.periodo": {
            "Meta": {"object_name": "Periodo"},
            "dias": ("django.db.models.fields.IntegerField", [], {}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "unique": "True", "null": "True"},
            ),
        },
        "pe.planejamento": {
            "Meta": {"object_name": "Planejamento"},
            "data_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_termino": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "unique": "True", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "limite_alta": ("django.db.models.fields.IntegerField", [], {}),
            "limite_baixa": ("django.db.models.fields.IntegerField", [], {}),
            "metodo_analise": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "objetivo": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['pe.Objetivo']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "pe.projeto": {
            "Meta": {"object_name": "Projeto"},
            "andamento": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_inicio": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "data_termino": (
                "django.db.models.fields.DateField",
                [],
                {"null": "True", "blank": "True"},
            ),
            "descricao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2000", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "nome": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "unique": "True", "null": "True"},
            ),
            "responsavel": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "blank": "True",
                    "related_name": "'fkey_servidor_projeto'",
                    "null": "True",
                    "to": "orm['rh.Servidor']",
                },
            ),
            "status": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True", "blank": "True"},
            ),
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
                {"max_length": "3", "null": "True"},
            ),
            "numero_convenio": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "20", "null": "True", "blank": "True"},
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
        "rh.orgaogeral": {
            "Meta": {"ordering": "['nome']", "object_name": "OrgaoGeral"},
            "abreviacao": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True", "blank": "True"},
            ),
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "descricao": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True", "blank": "True"},
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
                    "symmetrical": "False",
                    "to": "orm['rh.DadoBancario']",
                    "null": "True",
                    "blank": "True",
                },
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
            "municipio_naturalidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.Localidade']", "null": "True", "blank": "True"},
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
        "rh.servidor": {
            "Meta": {
                "ordering": "('pessoa_fisica__nome', 'pessoa_fisica__cpf', 'matricula')",
                "object_name": "Servidor",
            },
            "ativo": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
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
            "grau_instrucao": (
                "django.db.models.fields.IntegerField",
                [],
                {"null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "incapacidade": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['rh.InCapacidade']", "null": "True", "blank": "True"},
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
        "rh.telefone": {
            "Meta": {"object_name": "Telefone"},
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

    complete_apps = ["pe"]
