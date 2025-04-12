# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Common'
        db.create_table(
            "mailing_common",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "name",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=150, null=True
                    ),
                ),
                (
                    "slug",
                    self.gf("django.db.models.fields.SlugField")(
                        max_length=150, unique=True, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Common"])

        # Adding model 'Profile'
        db.create_table(
            "mailing_profile",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Profile"])

        # Adding model 'Group'
        db.create_table(
            "mailing_group",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
                (
                    "profile",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="groups", to=orm["mailing.Profile"]
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Group"])

        # Adding model 'Treatment'
        db.create_table(
            "mailing_treatment",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Treatment"])

        # Adding model 'Company'
        db.create_table(
            "mailing_company",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Company"])

        # Adding model 'Position'
        db.create_table(
            "mailing_position",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Position"])

        # Adding model 'State'
        db.create_table(
            "mailing_state",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
                (
                    "UF",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=2, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["State"])

        # Adding model 'City'
        db.create_table(
            "mailing_city",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
                (
                    "state",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="cities", to=orm["mailing.State"]
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["City"])

        # Adding model 'Address'
        db.create_table(
            "mailing_address",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "locality",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=150, null=True
                    ),
                ),
                (
                    "neighborhood",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=100, null=True
                    ),
                ),
                (
                    "code",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=10, null=True, db_index=True
                    ),
                ),
                (
                    "city",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="addresses", to=orm["mailing.City"]
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Address"])

        # Adding model 'Phone'
        db.create_table(
            "mailing_phone",
            (
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "fax",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=15, null=True
                    ),
                ),
                (
                    "normal",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=15, null=True
                    ),
                ),
                (
                    "mobile",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=15, null=True
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Phone"])

        # Adding model 'Contact'
        db.create_table(
            "mailing_contact",
            (
                (
                    "common_ptr",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        to=orm["mailing.Common"], unique=True, primary_key=True
                    ),
                ),
                (
                    "profile",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="contacts", to=orm["mailing.Profile"]
                    ),
                ),
                (
                    "treatment",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="contacts", to=orm["mailing.Treatment"]
                    ),
                ),
                (
                    "company",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="contacts", to=orm["mailing.Company"]
                    ),
                ),
                (
                    "position",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="contacts", to=orm["mailing.Position"]
                    ),
                ),
                (
                    "address",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        related_name="contact", unique=True, to=orm["mailing.Address"]
                    ),
                ),
                (
                    "phone",
                    self.gf("django.db.models.fields.related.OneToOneField")(
                        related_name="contact", unique=True, to=orm["mailing.Phone"]
                    ),
                ),
            ),
        )
        db.send_create_signal("mailing", ["Contact"])

        # Adding M2M table for field groups on 'Contact'
        db.create_table(
            "mailing_contact_groups",
            (
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", primary_key=True, auto_created=True
                    ),
                ),
                ("contact", models.ForeignKey(orm["mailing.contact"], null=False)),
                ("group", models.ForeignKey(orm["mailing.group"], null=False)),
            ),
        )
        db.create_unique("mailing_contact_groups", ["contact_id", "group_id"])

    def backwards(self, orm):
        # Deleting model 'Common'
        db.delete_table("mailing_common")

        # Deleting model 'Profile'
        db.delete_table("mailing_profile")

        # Deleting model 'Group'
        db.delete_table("mailing_group")

        # Deleting model 'Treatment'
        db.delete_table("mailing_treatment")

        # Deleting model 'Company'
        db.delete_table("mailing_company")

        # Deleting model 'Position'
        db.delete_table("mailing_position")

        # Deleting model 'State'
        db.delete_table("mailing_state")

        # Deleting model 'City'
        db.delete_table("mailing_city")

        # Deleting model 'Address'
        db.delete_table("mailing_address")

        # Deleting model 'Phone'
        db.delete_table("mailing_phone")

        # Deleting model 'Contact'
        db.delete_table("mailing_contact")

        # Removing M2M table for field groups on 'Contact'
        db.delete_table("mailing_contact_groups")

    models = {
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
                {"max_length": "150", "unique": "True", "null": "True"},
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
                    "null": "True",
                    "to": "orm['mailing.Group']",
                },
            ),
            "phone": (
                "django.db.models.fields.related.OneToOneField",
                [],
                {
                    "related_name": "'contact'",
                    "unique": "True",
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
        "mailing.phone": {
            "Meta": {"object_name": "Phone"},
            "fax": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "mobile": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
            ),
            "normal": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "15", "null": "True"},
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
