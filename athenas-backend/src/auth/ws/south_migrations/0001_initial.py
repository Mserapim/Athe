# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Application'
        db.create_table(
            "ws_application",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "title",
                    self.gf("django.db.models.fields.CharField")(
                        unique=True, max_length=50
                    ),
                ),
                (
                    "app_key",
                    self.gf("django.db.models.fields.CharField")(max_length=32),
                ),
                (
                    "valid_at",
                    self.gf("django.db.models.fields.DateTimeField")(null=True),
                ),
            ),
        )
        db.send_create_signal("ws", ["Application"])

        # Adding model 'UserPermission'
        db.create_table(
            "ws_userpermission",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "user",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="ws_permissions", to=orm["auth.User"]
                    ),
                ),
                (
                    "application",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="users", to=orm["ws.Application"]
                    ),
                ),
                (
                    "user_token",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=32, blank=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(default=True),
                ),
            ),
        )
        db.send_create_signal("ws", ["UserPermission"])

    def backwards(self, orm):
        # Deleting model 'Application'
        db.delete_table("ws_application")

        # Deleting model 'UserPermission'
        db.delete_table("ws_userpermission")

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
                {
                    "symmetrical": "False",
                    "related_name": "u'user_set'",
                    "blank": "True",
                    "to": "orm['auth.Group']",
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
                    "symmetrical": "False",
                    "related_name": "u'user_set'",
                    "blank": "True",
                    "to": "orm['auth.Permission']",
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
        "ws.application": {
            "Meta": {"object_name": "Application"},
            "app_key": ("django.db.models.fields.CharField", [], {"max_length": "32"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "50"},
            ),
            "valid_at": ("django.db.models.fields.DateTimeField", [], {"null": "True"}),
        },
        "ws.userpermission": {
            "Meta": {"object_name": "UserPermission"},
            "active": ("django.db.models.fields.BooleanField", [], {"default": "True"}),
            "application": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'users'", "to": "orm['ws.Application']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'ws_permissions'", "to": "orm['auth.User']"},
            ),
            "user_token": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "32", "blank": "True"},
            ),
        },
    }

    complete_apps = ["ws"]
