# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Application'
        db.create_table(
            "engine_application",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "icon",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=260, null=True, blank=True
                    ),
                ),
                (
                    "title",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "active",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
                (
                    "father",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["engine.Application"], null=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["Application"])

        # Adding model 'Controller'
        db.create_table(
            "engine_controller",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "icon",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=260, null=True, blank=True
                    ),
                ),
                (
                    "title",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "controller",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=50, null=True
                    ),
                ),
                (
                    "application",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["engine.Application"]
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["Controller"])

        # Adding model 'ControllerContentType'
        db.create_table(
            "engine_controllercontenttype",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "controller",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["engine.Controller"]
                    ),
                ),
                (
                    "content_type",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["contenttypes.ContentType"]
                    ),
                ),
                (
                    "priority",
                    self.gf("django.db.models.fields.SmallIntegerField")(default=0),
                ),
            ),
        )
        db.send_create_signal("engine", ["ControllerContentType"])

        # Adding unique constraint on 'ControllerContentType', fields ['controller', 'content_type']
        db.create_unique(
            "engine_controllercontenttype", ["controller_id", "content_type_id"]
        )

        # Adding model 'LDAPServer'
        db.create_table(
            "engine_ldapserver",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "address",
                    self.gf("django.db.models.fields.IPAddressField")(max_length=15),
                ),
                ("port", self.gf("django.db.models.fields.PositiveIntegerField")()),
                (
                    "dn",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "basedn",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "admin_user",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "admin_password",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                (
                    "user_object",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
                ("priority", self.gf("django.db.models.fields.PositiveIntegerField")()),
                ("tls", self.gf("django.db.models.fields.BooleanField")(default=False)),
                (
                    "falt",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
            ),
        )
        db.send_create_signal("engine", ["LDAPServer"])

        # Adding model 'LDAPServerFault'
        db.create_table(
            "engine_ldapserverfault",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "server",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["engine.LDAPServer"]
                    ),
                ),
                (
                    "moment",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now=True, blank=True
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["LDAPServerFault"])

        # Adding model 'ControllerPermission'
        db.create_table(
            "engine_controllerpermission",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=60, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["ControllerPermission"])

        # Adding M2M table for field users on 'ControllerPermission'
        db.create_table(
            "engine_controllerpermissioc29e",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                (
                    "controllerpermission",
                    models.ForeignKey(orm["engine.controllerpermission"], null=False),
                ),
                ("user", models.ForeignKey(orm["auth.user"], null=False)),
            ),
        )
        db.create_unique(
            "engine_controllerpermissioc29e", ["controllerpermission_id", "user_id"]
        )

        # Adding M2M table for field controllers on 'ControllerPermission'
        db.create_table(
            "engine_controllerpermissioe194",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                (
                    "controllerpermission",
                    models.ForeignKey(orm["engine.controllerpermission"], null=False),
                ),
                ("controller", models.ForeignKey(orm["engine.controller"], null=False)),
            ),
        )
        db.create_unique(
            "engine_controllerpermissioe194",
            ["controllerpermission_id", "controller_id"],
        )

    def backwards(self, orm):

        # Removing unique constraint on 'ControllerContentType', fields ['controller', 'content_type']
        db.delete_unique(
            "engine_controllercontenttype", ["controller_id", "content_type_id"]
        )

        # Deleting model 'Application'
        db.delete_table("engine_application")

        # Deleting model 'Controller'
        db.delete_table("engine_controller")

        # Deleting model 'ControllerContentType'
        db.delete_table("engine_controllercontenttype")

        # Deleting model 'LDAPServer'
        db.delete_table("engine_ldapserver")

        # Deleting model 'LDAPServerFault'
        db.delete_table("engine_ldapserverfault")

        # Deleting model 'ControllerPermission'
        db.delete_table("engine_controllerpermission")

        # Removing M2M table for field users on 'ControllerPermission'
        db.delete_table("engine_controllerpermissioc29e")

        # Removing M2M table for field controllers on 'ControllerPermission'
        db.delete_table("engine_controllerpermissioe194")

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
        "engine.application": {
            "Meta": {
                "ordering": "['-father__title', 'title']",
                "object_name": "Application",
            },
            "active": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
            "father": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['engine.Application']", "null": "True", "blank": "True"},
            ),
            "icon": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "260", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
        },
        "engine.controller": {
            "Meta": {
                "ordering": "('application', 'controller')",
                "object_name": "Controller",
            },
            "application": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['engine.Application']"},
            ),
            "controller": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
            "icon": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "260", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "title": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "50", "null": "True"},
            ),
        },
        "engine.controllercontenttype": {
            "Meta": {
                "unique_together": "(('controller', 'content_type'),)",
                "object_name": "ControllerContentType",
            },
            "content_type": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['contenttypes.ContentType']"},
            ),
            "controller": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['engine.Controller']"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "priority": (
                "django.db.models.fields.SmallIntegerField",
                [],
                {"default": "0"},
            ),
        },
        "engine.controllerpermission": {
            "Meta": {"object_name": "ControllerPermission"},
            "controllers": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['engine.Controller']",
                    "null": "True",
                    "blank": "True",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "to": "orm['auth.User']",
                    "null": "True",
                    "blank": "True",
                },
            ),
        },
        "engine.ldapserver": {
            "Meta": {"object_name": "LDAPServer"},
            "address": (
                "django.db.models.fields.IPAddressField",
                [],
                {"max_length": "15"},
            ),
            "admin_password": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "admin_user": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "basedn": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "dn": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
            "falt": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "port": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "priority": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "tls": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
            "user_object": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60", "null": "True"},
            ),
        },
        "engine.ldapserverfault": {
            "Meta": {"object_name": "LDAPServerFault"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "moment": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "blank": "True"},
            ),
            "server": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['engine.LDAPServer']"},
            ),
        },
    }

    complete_apps = ["engine"]
