# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TaskSession'
        db.create_table(
            "eng_tasksession",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                ("sid", self.gf("django.db.models.fields.CharField")(max_length=32)),
                (
                    "description",
                    self.gf("django.db.models.fields.CharField")(max_length=255),
                ),
                (
                    "params_cache",
                    self.gf("django.db.models.fields.CharField")(
                        default="{}", max_length=400
                    ),
                ),
                (
                    "user",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        to=orm["auth.User"]
                    ),
                ),
                (
                    "started_task",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now_add=True, blank=True
                    ),
                ),
                (
                    "finished_task",
                    self.gf("django.db.models.fields.DateTimeField")(null=True),
                ),
                (
                    "visualized",
                    self.gf("django.db.models.fields.BooleanField")(default=False),
                ),
                (
                    "status",
                    self.gf("django.db.models.fields.CharField")(
                        default="RUNNING", max_length=16
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["TaskSession"])

        # Adding model 'TaskMessages'
        db.create_table(
            "eng_taskmessages",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "session",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="messages", to=orm["engine.TaskSession"]
                    ),
                ),
                (
                    "message",
                    self.gf("django.db.models.fields.CharField")(max_length=400),
                ),
                (
                    "type_of",
                    self.gf("django.db.models.fields.PositiveSmallIntegerField")(
                        default=1
                    ),
                ),
            ),
        )
        db.send_create_signal("engine", ["TaskMessages"])

        # Changing field 'ControllerPermission.name'
        db.alter_column(
            "engine_controllerpermission",
            "name",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

        # Changing field 'Application.title'
        db.alter_column(
            "engine_application",
            "title",
            self.gf("django.db.models.fields.CharField")(default="", max_length=50),
        )

        # Changing field 'Controller.controller'
        db.alter_column(
            "engine_controller",
            "controller",
            self.gf("django.db.models.fields.CharField")(default="", max_length=50),
        )

        # Changing field 'Controller.title'
        db.alter_column(
            "engine_controller",
            "title",
            self.gf("django.db.models.fields.CharField")(default="", max_length=50),
        )

        # Changing field 'Evento.resource'
        db.alter_column(
            "engine_evento",
            "resource",
            self.gf("django.db.models.fields.CharField")(default="", max_length=200),
        )

        # Changing field 'Evento.title'
        db.alter_column(
            "engine_evento",
            "title",
            self.gf("django.db.models.fields.CharField")(default="", max_length=100),
        )

        # Changing field 'Evento.interface'
        db.alter_column(
            "engine_evento",
            "interface",
            self.gf("django.db.models.fields.CharField")(default="", max_length=200),
        )

        # Changing field 'LDAPServer.dn'
        db.alter_column(
            "engine_ldapserver",
            "dn",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

        # Changing field 'LDAPServer.admin_user'
        db.alter_column(
            "engine_ldapserver",
            "admin_user",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

        # Changing field 'LDAPServer.user_object'
        db.alter_column(
            "engine_ldapserver",
            "user_object",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

        # Changing field 'LDAPServer.basedn'
        db.alter_column(
            "engine_ldapserver",
            "basedn",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

        # Changing field 'LDAPServer.admin_password'
        db.alter_column(
            "engine_ldapserver",
            "admin_password",
            self.gf("django.db.models.fields.CharField")(default="", max_length=60),
        )

    def backwards(self, orm):
        # Deleting model 'TaskSession'
        db.delete_table("eng_tasksession")

        # Deleting model 'TaskMessages'
        db.delete_table("eng_taskmessages")

        # Changing field 'ControllerPermission.name'
        db.alter_column(
            "engine_controllerpermission",
            "name",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

        # Changing field 'Application.title'
        db.alter_column(
            "engine_application",
            "title",
            self.gf("django.db.models.fields.CharField")(max_length=50, null=True),
        )

        # Changing field 'Controller.controller'
        db.alter_column(
            "engine_controller",
            "controller",
            self.gf("django.db.models.fields.CharField")(max_length=50, null=True),
        )

        # Changing field 'Controller.title'
        db.alter_column(
            "engine_controller",
            "title",
            self.gf("django.db.models.fields.CharField")(max_length=50, null=True),
        )

        # Changing field 'Evento.resource'
        db.alter_column(
            "engine_evento",
            "resource",
            self.gf("django.db.models.fields.CharField")(max_length=200, null=True),
        )

        # Changing field 'Evento.title'
        db.alter_column(
            "engine_evento",
            "title",
            self.gf("django.db.models.fields.CharField")(max_length=100, null=True),
        )

        # Changing field 'Evento.interface'
        db.alter_column(
            "engine_evento",
            "interface",
            self.gf("django.db.models.fields.CharField")(max_length=200, null=True),
        )

        # Changing field 'LDAPServer.dn'
        db.alter_column(
            "engine_ldapserver",
            "dn",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

        # Changing field 'LDAPServer.admin_user'
        db.alter_column(
            "engine_ldapserver",
            "admin_user",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

        # Changing field 'LDAPServer.user_object'
        db.alter_column(
            "engine_ldapserver",
            "user_object",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

        # Changing field 'LDAPServer.basedn'
        db.alter_column(
            "engine_ldapserver",
            "basedn",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

        # Changing field 'LDAPServer.admin_password'
        db.alter_column(
            "engine_ldapserver",
            "admin_password",
            self.gf("django.db.models.fields.CharField")(max_length=60, null=True),
        )

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
        "engine.application": {
            "Meta": {
                "ordering": "['-father__title', 'title']",
                "unique_together": "(('title', 'father'),)",
                "object_name": "Application",
            },
            "active": ("django.db.models.fields.BooleanField", [], {}),
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
            "title": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
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
                {"max_length": "50"},
            ),
            "icon": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "260", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "title": ("django.db.models.fields.CharField", [], {"max_length": "50"}),
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
            "Meta": {"ordering": "('name',)", "object_name": "ControllerPermission"},
            "controllers": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'controller_permissions'",
                    "blank": "True",
                    "to": "orm['engine.Controller']",
                },
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": ("django.db.models.fields.CharField", [], {"max_length": "60"}),
            "users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {"to": "orm['auth.User']", "symmetrical": "False", "blank": "True"},
            ),
        },
        "engine.evento": {
            "Meta": {"object_name": "Evento"},
            "end_date": ("django.db.models.fields.DateTimeField", [], {"null": "True"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "interface": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200"},
            ),
            "resource": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "200"},
            ),
            "start_date": ("django.db.models.fields.DateTimeField", [], {}),
            "title": ("django.db.models.fields.CharField", [], {"max_length": "100"}),
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
                {"max_length": "60"},
            ),
            "admin_user": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60"},
            ),
            "basedn": ("django.db.models.fields.CharField", [], {"max_length": "60"}),
            "dn": ("django.db.models.fields.CharField", [], {"max_length": "60"}),
            "falt": ("django.db.models.fields.BooleanField", [], {"default": "False"}),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "port": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "priority": ("django.db.models.fields.PositiveIntegerField", [], {}),
            "tls": ("django.db.models.fields.BooleanField", [], {}),
            "user_object": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "60"},
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
        "engine.taskmessages": {
            "Meta": {
                "ordering": "('id',)",
                "object_name": "TaskMessages",
                "db_table": "'eng_taskmessages'",
            },
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "message": ("django.db.models.fields.CharField", [], {"max_length": "400"}),
            "session": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'messages'", "to": "orm['engine.TaskSession']"},
            ),
            "type_of": (
                "django.db.models.fields.PositiveSmallIntegerField",
                [],
                {"default": "1"},
            ),
        },
        "engine.tasksession": {
            "Meta": {
                "ordering": "('started_task',)",
                "object_name": "TaskSession",
                "db_table": "'eng_tasksession'",
            },
            "description": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "255"},
            ),
            "finished_task": (
                "django.db.models.fields.DateTimeField",
                [],
                {"null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "params_cache": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'{}'", "max_length": "400"},
            ),
            "sid": ("django.db.models.fields.CharField", [], {"max_length": "32"}),
            "started_task": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now_add": "True", "blank": "True"},
            ),
            "status": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'RUNNING'", "max_length": "16"},
            ),
            "user": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"to": "orm['auth.User']"},
            ),
            "visualized": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False"},
            ),
        },
    }

    complete_apps = ["engine"]
