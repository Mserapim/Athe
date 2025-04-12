# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Message'
        db.create_table(
            "eng_message",
            (
                (
                    "mid",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=30, unique=True, null=True, blank=True
                    ),
                ),
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "header",
                    self.gf("django.db.models.fields.CharField")(
                        default="", max_length=30, null=True, blank=True
                    ),
                ),
                (
                    "default_params",
                    self.gf("django.db.models.fields.CharField")(
                        default="{}", max_length=400, null=True, blank=True
                    ),
                ),
                (
                    "type",
                    self.gf("django.db.models.fields.CharField")(
                        default="HOMOLOGACAO", max_length=10, null=True
                    ),
                ),
                ("message", self.gf("django.db.models.fields.TextField")(null=True)),
            ),
        )
        db.send_create_signal("notification", ["Message"])

        # Adding model 'Notification'
        db.create_table(
            "eng_notification",
            (
                (
                    "status",
                    self.gf("django.db.models.fields.PositiveSmallIntegerField")(
                        default=2
                    ),
                ),
                (
                    "sender_id",
                    self.gf("django.db.models.fields.PositiveIntegerField")(
                        null=True, blank=True
                    ),
                ),
                (
                    "created_at",
                    self.gf("django.db.models.fields.DateTimeField")(
                        auto_now=True, blank=True
                    ),
                ),
                (
                    "target_id",
                    self.gf("django.db.models.fields.PositiveIntegerField")(),
                ),
                (
                    "params",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=400, null=True
                    ),
                ),
                (
                    "sender_ct",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        blank=True,
                        related_name="notifications_send",
                        null=True,
                        to=orm["contenttypes.ContentType"],
                    ),
                ),
                (
                    "msg",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="notifications", to=orm["notification.Message"]
                    ),
                ),
                (
                    "type",
                    self.gf("django.db.models.fields.CharField")(
                        default="SYS", max_length=10, null=True
                    ),
                ),
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
                (
                    "target_ct",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="notifications_receive",
                        to=orm["contenttypes.ContentType"],
                    ),
                ),
            ),
        )
        db.send_create_signal("notification", ["Notification"])

        # Adding model 'NotifSMS'
        db.create_table(
            "eng_notification_sms",
            (
                (
                    "notification",
                    self.gf("django.db.models.fields.related.ForeignKey")(
                        related_name="sms_notifications",
                        to=orm["notification.Notification"],
                    ),
                ),
                (
                    "sms_status",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=3, null=True, blank=True
                    ),
                ),
                (
                    "sms_number",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=12, null=True, blank=True
                    ),
                ),
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
            ),
        )
        db.send_create_signal("notification", ["NotifSMS"])

        # Adding model 'NotifEmail'
        db.create_table(
            "eng_notification_email",
            (
                (
                    "sms_number",
                    self.gf("django.db.models.fields.CharField")(
                        max_length=150, null=True, blank=True
                    ),
                ),
                ("id", self.gf("django.db.models.fields.AutoField")(primary_key=True)),
            ),
        )
        db.send_create_signal("notification", ["NotifEmail"])

    def backwards(self, orm):

        # Deleting model 'Message'
        db.delete_table("eng_message")

        # Deleting model 'Notification'
        db.delete_table("eng_notification")

        # Deleting model 'NotifSMS'
        db.delete_table("eng_notification_sms")

        # Deleting model 'NotifEmail'
        db.delete_table("eng_notification_email")

    models = {
        "contenttypes.contenttype": {
            "Meta": {
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
            "message": ("django.db.models.fields.TextField", [], {"null": "True"}),
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
        "notification.notifemail": {
            "Meta": {
                "object_name": "NotifEmail",
                "db_table": "'eng_notification_email'",
            },
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "sms_number": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "150", "null": "True", "blank": "True"},
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
        "notification.notifsms": {
            "Meta": {"object_name": "NotifSMS", "db_table": "'eng_notification_sms'"},
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "notification": (
                "django.db.models.fields.related.ForeignKey",
                [],
                {
                    "related_name": "'sms_notifications'",
                    "to": "orm['notification.Notification']",
                },
            ),
            "sms_number": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "12", "null": "True", "blank": "True"},
            ),
            "sms_status": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "null": "True", "blank": "True"},
            ),
        },
    }

    complete_apps = ["notification"]
