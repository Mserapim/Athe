# encoding: utf-8
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'AreaConhecimento'
        db.create_table(
            "gecap_areaconhecimento",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "titulo",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, null=True
                    ),
                ),
                (
                    "codigo_cnpq",
                    self.gf("django.db.models.fields.SmallIntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "cache_codigo_cnpq",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=20, null=True, blank=True
                    ),
                ),
                (
                    "sub_area_de",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="sub_areas",
                        null=True,
                        to=orm["gecap.AreaConhecimento"],
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["AreaConhecimento"])

        # Adding model 'Capacitacao'
        db.create_table(
            "gecap_capacitacao",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "nome",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "dt_inicio",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "dt_fim",
                    self.gf("django.db.models.fields.DateField")(null=True, blank=True),
                ),
                (
                    "carga_horaria",
                    self.gf("django.db.models.fields.IntegerField")(
                        null=True, blank=True
                    ),
                ),
                ("promovido_por", self.gf("django.db.models.fields.IntegerField")()),
                (
                    "cidade_evento",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="capacitacoes", to=orm["rh.Localidade"]
                    ),
                ),
                (
                    "data_cadastro",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
                (
                    "ementa",
                    self.gf("django.db.models.fields.TextField")(null=True, blank=True),
                ),
                (
                    "publicar",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
                (
                    "descricao",
                    self.gf("django.db.models.fields.TextField")(null=True, blank=True),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Capacitacao"])

        # Adding M2M table for field promotores on 'Capacitacao'
        db.create_table(
            "gecap_capacitacao_promotores",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                (
                    "capacitacao",
                    models.ForeignKey(orm["gecap.capacitacao"], null=False),
                ),
                ("orgaogeral", models.ForeignKey(orm["rh.orgaogeral"], null=False)),
            ),
        )
        db.create_unique(
            "gecap_capacitacao_promotores", ["capacitacao_id", "orgaogeral_id"]
        )

        # Adding M2M table for field area_conhecimento on 'Capacitacao'
        db.create_table(
            "gecap_capacitacao_area_con77c4",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                (
                    "capacitacao",
                    models.ForeignKey(orm["gecap.capacitacao"], null=False),
                ),
                (
                    "areaconhecimento",
                    models.ForeignKey(orm["gecap.areaconhecimento"], null=False),
                ),
            ),
        )
        db.create_unique(
            "gecap_capacitacao_area_con77c4", ["capacitacao_id", "areaconhecimento_id"]
        )

        # Adding model 'Evento'
        db.create_table(
            "gecap_evento",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Evento"])

        # Adding model 'Seminario'
        db.create_table(
            "gecap_seminario",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Seminario"])

        # Adding model 'Oficina'
        db.create_table(
            "gecap_oficina",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Oficina"])

        # Adding model 'Feira'
        db.create_table(
            "gecap_feira",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Feira"])

        # Adding model 'Reuniao'
        db.create_table(
            "gecap_reuniao",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Reuniao"])

        # Adding model 'Congresso'
        db.create_table(
            "gecap_congresso",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Congresso"])

        # Adding model 'Curso'
        db.create_table(
            "gecap_curso",
            (
                (
                    "capacitacao_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["gecap.Capacitacao"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Curso"])

        # Adding model 'Inscricao'
        db.create_table(
            "gecap_inscricao",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "servidor",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="inscricoes", to=orm["rh.Servidor"]
                    ),
                ),
                (
                    "capacitacao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="inscricoes", to=orm["gecap.Capacitacao"]
                    ),
                ),
                (
                    "certificado",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["ged.Arquivo"], null=True, blank=True
                    ),
                ),
                (
                    "homologado",
                    self.gf("django.db.models.fields.DateTimeField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "data_cadastro",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Inscricao"])

        # Adding unique constraint on 'Inscricao', fields ['capacitacao', 'servidor']
        db.create_unique("gecap_inscricao", ["capacitacao_id", "servidor_id"])

        # Adding model 'Investimento'
        db.create_table(
            "gecap_investimento",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "inscricao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="investimentos",
                        null=True,
                        to=orm["gecap.Inscricao"],
                    ),
                ),
                (
                    "capacitacao",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="investimentos",
                        null=True,
                        to=orm["gecap.Capacitacao"],
                    ),
                ),
                (
                    "descricao",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "valor",
                    self.gf("django.db.models.fields.DecimalField")(
                        max_digits=18, decimal_places=2
                    ),
                ),
                (
                    "previsao",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
            ),
        )
        db.send_create_signal("gecap", ["Investimento"])

    def backwards(self, orm):

        # Removing unique constraint on 'Inscricao', fields ['capacitacao', 'servidor']
        db.delete_unique("gecap_inscricao", ["capacitacao_id", "servidor_id"])

        # Deleting model 'AreaConhecimento'
        db.delete_table("gecap_areaconhecimento")

        # Deleting model 'Capacitacao'
        db.delete_table("gecap_capacitacao")

        # Removing M2M table for field promotores on 'Capacitacao'
        db.delete_table("gecap_capacitacao_promotores")

        # Removing M2M table for field area_conhecimento on 'Capacitacao'
        db.delete_table("gecap_capacitacao_area_con77c4")

        # Deleting model 'Evento'
        db.delete_table("gecap_evento")

        # Deleting model 'Seminario'
        db.delete_table("gecap_seminario")

        # Deleting model 'Oficina'
        db.delete_table("gecap_oficina")

        # Deleting model 'Feira'
        db.delete_table("gecap_feira")

        # Deleting model 'Reuniao'
        db.delete_table("gecap_reuniao")

        # Deleting model 'Congresso'
        db.delete_table("gecap_congresso")

        # Deleting model 'Curso'
        db.delete_table("gecap_curso")

        # Deleting model 'Inscricao'
        db.delete_table("gecap_inscricao")

        # Deleting model 'Investimento'
        db.delete_table("gecap_investimento")

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

    complete_apps = ["gecap"]
