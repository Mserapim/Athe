# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'LineLog'
        db.create_table(
            "auditoria_linelog",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "user",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["auth.User"], null=True, blank=True
                    ),
                ),
                (
                    "dt",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
                ("level", self.gf("django.db.models.fields.IntegerField")(null=True)),
                (
                    "controller",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, null=True
                    ),
                ),
                (
                    "action",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=200, null=True
                    ),
                ),
                ("status", self.gf("django.db.models.fields.IntegerField")(null=True)),
                (
                    "json_description",
                    self.gf("django.db.models.fields.TextField")(null=True),
                ),
                (
                    "host_address",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=100, null=True
                    ),
                ),
                (
                    "host_name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=250, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("auditoria", ["LineLog"])

    def backwards(self, orm):

        # Deleting model 'LineLog'
        db.delete_table("auditoria_linelog")

    models = {
        "auditoria.linelog": {
            "Meta": {"ordering": "('-dt',)", "object_name": "LineLog"},
            "action": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
            "controller": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200", "null": "True"},
            ),
            "dt": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "host_address": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
            "host_name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "250", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "json_description": (
                "django.db.models.fields.TextField",
                [],
                {"null": "True"},
            ),
            "level": ("django.db.models.fields.IntegerField", [], {"null": "True"}),
            "status": ("django.db.models.fields.IntegerField", [], {"null": "True"}),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['auth.User']", "null": "True", "blank": "True"},
            ),
        },
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
    }

    complete_apps = ["auditoria"]
