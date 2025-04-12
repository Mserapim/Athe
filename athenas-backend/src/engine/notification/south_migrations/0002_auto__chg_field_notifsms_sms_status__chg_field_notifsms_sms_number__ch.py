# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'NotifSMS.sms_status'
        db.alter_column(
            "eng_notification_sms",
            "sms_status",
            self.gf("django.db.models.fields.CharField")(default="", max_length=3),
        )

        # Changing field 'NotifSMS.sms_number'
        db.alter_column(
            "eng_notification_sms",
            "sms_number",
            self.gf("django.db.models.fields.CharField")(default="", max_length=12),
        )

        # Changing field 'Message.mid'
        db.alter_column(
            "eng_message",
            "mid",
            self.gf("django.db.models.fields.CharField")(
                default="", unique=True, max_length=30
            ),
        )

        # Changing field 'Message.header'
        db.alter_column(
            "eng_message",
            "header",
            self.gf("django.db.models.fields.CharField")(max_length=30),
        )

        # Changing field 'Message.default_params'
        db.alter_column(
            "eng_message",
            "default_params",
            self.gf("django.db.models.fields.CharField")(max_length=400),
        )

        # Changing field 'Message.type'
        db.alter_column(
            "eng_message",
            "type",
            self.gf("django.db.models.fields.CharField")(max_length=10),
        )

        # Changing field 'Message.message'
        db.alter_column(
            "eng_message", "message", self.gf("django.db.models.fields.TextField")()
        )

        # Changing field 'NotifEmail.sms_number'
        db.alter_column(
            "eng_notification_email",
            "sms_number",
            self.gf("django.db.models.fields.CharField")(default="", max_length=150),
        )
        # Adding index on 'Notification', fields ['sender_id']
        db.create_index("eng_notification", ["sender_id"])

        # Adding index on 'Notification', fields ['created_at']
        db.create_index("eng_notification", ["created_at"])

        # Adding index on 'Notification', fields ['target_id']
        db.create_index("eng_notification", ["target_id"])

        # Changing field 'Notification.params'
        db.alter_column(
            "eng_notification",
            "params",
            self.gf("django.db.models.fields.CharField")(default="", max_length=400),
        )

        # Changing field 'Notification.type'
        db.alter_column(
            "eng_notification",
            "type",
            self.gf("django.db.models.fields.CharField")(max_length=10),
        )

    def backwards(self, orm):
        # Removing index on 'Notification', fields ['target_id']
        db.delete_index("eng_notification", ["target_id"])

        # Removing index on 'Notification', fields ['created_at']
        db.delete_index("eng_notification", ["created_at"])

        # Removing index on 'Notification', fields ['sender_id']
        db.delete_index("eng_notification", ["sender_id"])

        # Changing field 'NotifSMS.sms_status'
        db.alter_column(
            "eng_notification_sms",
            "sms_status",
            self.gf("django.db.models.fields.CharField")(max_length=3, null=True),
        )

        # Changing field 'NotifSMS.sms_number'
        db.alter_column(
            "eng_notification_sms",
            "sms_number",
            self.gf("django.db.models.fields.CharField")(max_length=12, null=True),
        )

        # Changing field 'Message.mid'
        db.alter_column(
            "eng_message",
            "mid",
            self.gf("django.db.models.fields.CharField")(
                unique=True, max_length=30, null=True
            ),
        )

        # Changing field 'Message.header'
        db.alter_column(
            "eng_message",
            "header",
            self.gf("django.db.models.fields.CharField")(max_length=30, null=True),
        )

        # Changing field 'Message.default_params'
        db.alter_column(
            "eng_message",
            "default_params",
            self.gf("django.db.models.fields.CharField")(max_length=400, null=True),
        )

        # Changing field 'Message.type'
        db.alter_column(
            "eng_message",
            "type",
            self.gf("django.db.models.fields.CharField")(max_length=10, null=True),
        )

        # Changing field 'Message.message'
        db.alter_column(
            "eng_message",
            "message",
            self.gf("django.db.models.fields.TextField")(null=True),
        )

        # Changing field 'NotifEmail.sms_number'
        db.alter_column(
            "eng_notification_email",
            "sms_number",
            self.gf("django.db.models.fields.CharField")(max_length=150, null=True),
        )

        # Changing field 'Notification.params'
        db.alter_column(
            "eng_notification",
            "params",
            self.gf("django.db.models.fields.CharField")(max_length=400, null=True),
        )

        # Changing field 'Notification.type'
        db.alter_column(
            "eng_notification",
            "type",
            self.gf("django.db.models.fields.CharField")(max_length=10, null=True),
        )

    models = {
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
        "notification.message": {
            "Meta": {"object_name": "Message", "db_table": "'eng_message'"},
            "default_params": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'{}'", "max_length": "400", "blank": "True"},
            ),
            "header": (
                "django.db.models.fields.CharField",
                [],
                {"default": "''", "max_length": "30", "blank": "True"},
            ),
            "id": ("django.db.models.fields.AutoField", [], {"primary_key": "True"}),
            "message": ("django.db.models.fields.TextField", [], {"default": "''"}),
            "mid": (
                "django.db.models.fields.CharField",
                [],
                {"unique": "True", "max_length": "30", "blank": "True"},
            ),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'INFO'", "max_length": "10"},
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
                {"max_length": "150", "blank": "True"},
            ),
        },
        "notification.notification": {
            "Meta": {
                "ordering": "('-created_at',)",
                "object_name": "Notification",
                "db_table": "'eng_notification'",
            },
            "created_at": (
                "django.db.models.fields.DateTimeField",
                [],
                {"auto_now": "True", "db_index": "True", "blank": "True"},
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
            "params": ("django.db.models.fields.CharField", [], {"max_length": "400"}),
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
                {"db_index": "True", "null": "True", "blank": "True"},
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
            "target_id": (
                "django.db.models.fields.PositiveIntegerField",
                [],
                {"db_index": "True"},
            ),
            "type": (
                "django.db.models.fields.CharField",
                [],
                {"default": "'SYS'", "max_length": "10"},
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
                {"max_length": "12", "blank": "True"},
            ),
            "sms_status": (
                "django.db.models.fields.CharField",
                [],
                {"max_length": "3", "blank": "True"},
            ),
        },
    }

    complete_apps = ["notification"]
