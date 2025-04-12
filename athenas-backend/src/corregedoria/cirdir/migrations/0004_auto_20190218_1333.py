# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cirdir", "0003_auto_20190212_1739"),
    ]

    operations = [
        migrations.CreateModel(
            name="History",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("criteria", models.SmallIntegerField(null=True, blank=True)),
                ("action", models.TextField(null=True, blank=True)),
            ],
            options={
                "verbose_name": "Hist\xf3rio de a\xe7\xf5es do SRDIR",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="address",
            name="validate_reside_outside",
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_address",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_address_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_debits",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_debits_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_health",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_health_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_property",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_property_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_teaching_1st_semestry",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_teaching_1st_semestry_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_teaching_2nd_semestry",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="controlinformation",
            name="pendency_teaching_2nd_semestry_msg",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="address",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="addresses",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AlterField(
            model_name="debits",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="debitss",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AlterField(
            model_name="health",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="healths",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AlterField(
            model_name="property",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="properties",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AlterField(
            model_name="teaching",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="teachings",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AddField(
            model_name="history",
            name="controlinformation",
            field=models.ForeignKey(
                related_name="historics",
                on_delete=django.db.models.deletion.PROTECT,
                to="cirdir.ControlInformation",
            ),
        ),
        migrations.AddField(
            model_name="history",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="history",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
