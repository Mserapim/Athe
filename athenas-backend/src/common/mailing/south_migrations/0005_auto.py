# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing M2M table for field users on 'Profile'
        db.delete_table("mailing_profile_users")

        # Adding M2M table for field mailing_users on 'Profile'
        db.create_table(
            "mailing_profile_mailing_users",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("profile", models.ForeignKey(orm["mailing.profile"], null=False)),
                (
                    "mailinguser",
                    models.ForeignKey(orm["mailing.mailinguser"], null=False),
                ),
            ),
        )
        db.create_unique(
            "mailing_profile_mailing_users", ["profile_id", "mailinguser_id"]
        )

    def backwards(self, orm):
        # Adding M2M table for field users on 'Profile'
        db.create_table(
            "mailing_profile_users",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("profile", models.ForeignKey(orm["mailing.profile"], null=False)),
                (
                    "mailinguser",
                    models.ForeignKey(orm["mailing.mailinguser"], null=False),
                ),
            ),
        )
        db.create_unique("mailing_profile_users", ["profile_id", "mailinguser_id"])

        # Removing M2M table for field mailing_users on 'Profile'
        db.delete_table("mailing_profile_mailing_users")

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
        "mailing.address": {
            "Meta": {"object_name": "Address"},
            "city": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'addresses'", "to": "orm['mailing.City']"},
            ),
            "code": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "10", "null": "True", "db_index": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "locality": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "null": "True"},
            ),
            "neighborhood": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "null": "True"},
            ),
        },
        "mailing.city": {
            "Meta": {"object_name": "City", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "state": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'cities'", "to": "orm['mailing.State']"},
            ),
        },
        "mailing.common": {
            "Meta": {"object_name": "Common"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "name": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "null": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "150", "null": "True", "blank": "True"},
            ),
        },
        "mailing.company": {
            "Meta": {"object_name": "Company", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "mailing.contact": {
            "Meta": {"object_name": "Contact", "_ormbases": ["mailing.Common"]},
            "address": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'contact'",
                    "unique": "True",
                    "to": "orm['mailing.Address']",
                },
            ),
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "company": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'contacts'", "to": "orm['mailing.Company']"},
            ),
            "groups": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "blank": "True",
                    "related_name": "'contacts'",
                    "null": "True",
                    "symmetrical": "False",
                    "to": "orm['mailing.Group']",
                },
            ),
            "phone": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'contact'",
                    "unique": "True",
                    "null": "True",
                    "to": "orm['mailing.Phone']",
                },
            ),
            "position": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'contacts'", "to": "orm['mailing.Position']"},
            ),
            "profile": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'contacts'", "to": "orm['mailing.Profile']"},
            ),
            "treatment": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'contacts'", "to": "orm['mailing.Treatment']"},
            ),
        },
        "mailing.group": {
            "Meta": {"object_name": "Group", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "profile": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {"related_name": "'groups'", "to": "orm['mailing.Profile']"},
            ),
        },
        "mailing.mailinguser": {
            "Meta": {"object_name": "MailingUser"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "is_admin": (
                "django.db.models.fields.BooleanField",
                [],
                {"default": "False", "db_index": "True"},
            ),
            "user": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'mailing_user'",
                    "unique": "True",
                    "to": "orm['auth.User']",
                },
            ),
        },
        "mailing.phone": {
            "Meta": {"object_name": "Phone"},
            "fax": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mobile": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True", "blank": "True"},
            ),
            "normal": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True", "blank": "True"},
            ),
        },
        "mailing.position": {
            "Meta": {"object_name": "Position", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "mailing.profile": {
            "Meta": {"object_name": "Profile", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "mailing_users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "symmetrical": "False",
                    "related_name": "'profiles'",
                    "null": "True",
                    "to": "orm['mailing.MailingUser']",
                },
            ),
        },
        "mailing.state": {
            "Meta": {"object_name": "State", "_ormbases": ["mailing.Common"]},
            "UF": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "null": "True"},
            ),
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
        "mailing.treatment": {
            "Meta": {"object_name": "Treatment", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
        },
    }

    complete_apps = ["mailing"]
