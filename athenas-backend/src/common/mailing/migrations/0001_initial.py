# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Address",
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
                ("locality", models.CharField(max_length=150)),
                ("neighborhood", models.CharField(max_length=100)),
                ("code", models.CharField(max_length=10, db_index=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Common",
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
                ("name", models.CharField(max_length=150)),
                ("slug", models.SlugField(max_length=150, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="City",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="Contact",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "address",
                    models.OneToOneField(
                        related_name="contact",
                        to="mailing.Address",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "company",
                    models.ForeignKey(
                        related_name="contacts",
                        to="mailing.Company",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="MailingUser",
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
                    "permission",
                    models.CharField(
                        default="basic",
                        max_length=12,
                        db_index=True,
                        choices=[
                            ("basic", "B\xc3\xa1sico"),
                            ("reviser", "Revisor"),
                            ("admin", "Administrador"),
                        ],
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        related_name="mailing_user",
                        to=settings.AUTH_USER_MODEL,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Phone",
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
                ("fax", models.CharField(max_length=15, blank=True)),
                ("normal", models.CharField(max_length=15, blank=True)),
                ("mobile", models.CharField(max_length=15, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Position",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "users",
                    models.ManyToManyField(
                        related_name="profiles", to="mailing.MailingUser"
                    ),
                ),
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="State",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("uf", models.CharField(max_length=2, blank=True)),
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.CreateModel(
            name="Treatment",
            fields=[
                (
                    "common_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="mailing.Common",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("mailing.common",),
        ),
        migrations.AddField(
            model_name="group",
            name="profile",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="groups", to="mailing.Profile", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contact",
            name="groups",
            field=models.ManyToManyField(
                related_name="contacts", to="mailing.Group", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contact",
            name="phone",
            field=models.OneToOneField(
                related_name="contact",
                null=True,
                to="mailing.Phone",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contact",
            name="position",
            field=models.ForeignKey(
                related_name="contacts", to="mailing.Position", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contact",
            name="profile",
            field=models.ForeignKey(
                related_name="contacts", to="mailing.Profile", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="contact",
            name="treatment",
            field=models.ForeignKey(
                related_name="contacts",
                to="mailing.Treatment",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="city",
            name="state",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="cities", to="mailing.State", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="address",
            name="city",
            # Parametro "on_delete" adicionado. (Django 2)
            field=models.ForeignKey(
                related_name="addresses", to="mailing.City", on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
