# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "mid",
                    models.CharField(
                        help_text="",
                        unique=True,
                        max_length=30,
                        verbose_name="MID",
                        blank=True,
                    ),
                ),
                (
                    "header",
                    models.CharField(
                        default="",
                        help_text="",
                        max_length=30,
                        verbose_name="Header",
                        blank=True,
                    ),
                ),
                (
                    "message",
                    models.TextField(default="", help_text="", verbose_name="Message"),
                ),
                (
                    "type",
                    models.CharField(
                        default="INFO",
                        help_text="",
                        max_length=10,
                        verbose_name="Type of Message",
                        choices=[
                            ("INFO", "Information"),
                            ("WARNING", "Caution"),
                            ("ERROR", "Error"),
                        ],
                    ),
                ),
                (
                    "default_params",
                    models.CharField(
                        default="{}",
                        help_text="",
                        max_length=400,
                        verbose_name="Default Params",
                        blank=True,
                    ),
                ),
            ],
            options={
                "db_table": "eng_message",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotifEmail",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "sms_number",
                    models.CharField(
                        help_text="", max_length=150, verbose_name="Email", blank=True
                    ),
                ),
            ],
            options={
                "db_table": "eng_notification_email",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "sender_id",
                    models.PositiveIntegerField(db_index=True, null=True, blank=True),
                ),
                ("target_id", models.PositiveIntegerField(db_index=True)),
                (
                    "type",
                    models.CharField(
                        default="SYS",
                        max_length=10,
                        verbose_name="Type of Notification",
                        choices=[
                            ("SYS", "System"),
                            ("SMS", "SMS"),
                            ("EMAIL", "Email"),
                            ("ONTOP", "On top"),
                        ],
                    ),
                ),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Status of Notification",
                        choices=[
                            (8, "received"),
                            (1, "not send"),
                            (2, "send"),
                            (4, "send error"),
                            (16, "abandoned"),
                        ],
                    ),
                ),
                ("params", models.CharField(max_length=400, verbose_name="Params")),
                ("created_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "msg",
                    models.ForeignKey(
                        related_name="notifications",
                        verbose_name="Message",
                        to="notification.Message",
                        help_text="",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "sender_ct",
                    models.ForeignKey(
                        related_name="notifications_send",
                        blank=True,
                        to="contenttypes.ContentType",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "target_ct",
                    models.ForeignKey(
                        related_name="notifications_receive",
                        to="contenttypes.ContentType",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ("-created_at",),
                "db_table": "eng_notification",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotifSMS",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "sms_number",
                    models.CharField(
                        help_text="",
                        max_length=12,
                        verbose_name="SMS Number",
                        blank=True,
                    ),
                ),
                (
                    "sms_status",
                    models.CharField(
                        help_text="",
                        max_length=3,
                        verbose_name="SMS Status",
                        blank=True,
                    ),
                ),
                (
                    "notification",
                    models.ForeignKey(
                        related_name="sms_notifications",
                        to="notification.Notification",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "eng_notification_sms",
            },
            bases=(models.Model,),
        ),
    ]
