# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Phone.mobile'
        db.alter_column(
            "mailing_phone",
            "mobile",
            self.gf("django.db.models.fields.CharField")(default="", max_length=15),
        )

        # Changing field 'Phone.fax'
        db.alter_column(
            "mailing_phone",
            "fax",
            self.gf("django.db.models.fields.CharField")(default="", max_length=15),
        )

        # Changing field 'Phone.normal'
        db.alter_column(
            "mailing_phone",
            "normal",
            self.gf("django.db.models.fields.CharField")(default="", max_length=15),
        )

        # Changing field 'Address.code'
        db.alter_column(
            "mailing_address",
            "code",
            self.gf("django.db.models.fields.CharField")(default="", max_length=10),
        )

        # Changing field 'Address.neighborhood'
        db.alter_column(
            "mailing_address",
            "neighborhood",
            self.gf("django.db.models.fields.CharField")(default="", max_length=100),
        )

        # Changing field 'Address.locality'
        db.alter_column(
            "mailing_address",
            "locality",
            self.gf("django.db.models.fields.CharField")(default="", max_length=150),
        )
        # Deleting field 'State.UF'
        db.delete_column("mailing_state", "UF")

        # Adding field 'State.uf'
        db.add_column(
            "mailing_state",
            "uf",
            self.gf("django.db.models.fields.CharField")(
                default="", max_length=2, blank=True
            ),
            keep_default=False,
        )

        # Changing field 'MailingUser.permission'
        db.alter_column(
            "mailing_mailinguser",
            "permission",
            self.gf("django.db.models.fields.CharField")(max_length=12),
        )

        # Changing field 'Common.slug'
        db.alter_column(
            "mailing_common",
            "slug",
            self.gf("django.db.models.fields.SlugField")(default="", max_length=150),
        )

        # Changing field 'Common.name'
        db.alter_column(
            "mailing_common",
            "name",
            self.gf("django.db.models.fields.CharField")(default="", max_length=150),
        )

    def backwards(self, orm):

        # Changing field 'Phone.mobile'
        db.alter_column(
            "mailing_phone",
            "mobile",
            self.gf("django.db.models.fields.CharField")(max_length=15, null=True),
        )

        # Changing field 'Phone.fax'
        db.alter_column(
            "mailing_phone",
            "fax",
            self.gf("django.db.models.fields.CharField")(max_length=15, null=True),
        )

        # Changing field 'Phone.normal'
        db.alter_column(
            "mailing_phone",
            "normal",
            self.gf("django.db.models.fields.CharField")(max_length=15, null=True),
        )

        # Changing field 'Address.code'
        db.alter_column(
            "mailing_address",
            "code",
            self.gf("django.db.models.fields.CharField")(max_length=10, null=True),
        )

        # Changing field 'Address.neighborhood'
        db.alter_column(
            "mailing_address",
            "neighborhood",
            self.gf("django.db.models.fields.CharField")(max_length=100, null=True),
        )

        # Changing field 'Address.locality'
        db.alter_column(
            "mailing_address",
            "locality",
            self.gf("django.db.models.fields.CharField")(max_length=150, null=True),
        )
        # Adding field 'State.UF'
        db.add_column(
            "mailing_state",
            "UF",
            self.gf("django.db.models.fields.CharField")(max_length=2, null=True),
            keep_default=False,
        )

        # Deleting field 'State.uf'
        db.delete_column("mailing_state", "uf")

        # Changing field 'MailingUser.permission'
        db.alter_column(
            "mailing_mailinguser",
            "permission",
            self.gf("django.db.models.fields.CharField")(max_length=12, null=True),
        )

        # Changing field 'Common.slug'
        db.alter_column(
            "mailing_common",
            "slug",
            self.gf("django.db.models.fields.SlugField")(max_length=150, null=True),
        )

        # Changing field 'Common.name'
        db.alter_column(
            "mailing_common",
            "name",
            self.gf("django.db.models.fields.CharField")(max_length=150, null=True),
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
                {"db_index": "True", "max_length": "10", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "locality": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "blank": "True"},
            ),
            "neighborhood": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "100", "blank": "True"},
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
                {"max_length": "150", "blank": "True"},
            ),
            "slug": (
                "django.db.models.fields.SlugField",
                [],
                {"max_length": "150", "blank": "True"},
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
                    "symmetrical": "False",
                    "related_name": "'contacts'",
                    "blank": "True",
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
            "permission": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'basic'", "max_length": "12", "db_index": "True"},
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
                {"max_length": "15", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mobile": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "blank": "True"},
            ),
            "normal": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "blank": "True"},
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
            "users": (
                "django.db.models.fields.related.ManyToManyField",
                [],
                {
                    "related_name": "'profiles'",
                    "symmetrical": "False",
                    "to": "orm['mailing.MailingUser']",
                },
            ),
        },
        "mailing.state": {
            "Meta": {"object_name": "State", "_ormbases": ["mailing.Common"]},
            "common_ptr": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "to": "orm['mailing.Common']",
                    "unique": "True",
                    "primary_key": "True",
                },
            ),
            "uf": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "2", "blank": "True"},
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
