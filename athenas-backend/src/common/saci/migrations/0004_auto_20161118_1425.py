# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("saci", "0003_auto_20160816_1617"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="step",
            options={"ordering": ["-created_at"], "verbose_name": "Passo"},
        ),
        migrations.AlterField(
            model_name="attendance",
            name="department",
            field=models.ForeignKey(
                related_name="in_attendance_department",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="departamento",
                to="rh.OrgaoGeral",
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="destination",
            field=models.ForeignKey(
                related_name="in_attendance_destination",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="destina\xe7\xe3o",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="person",
            field=models.ForeignKey(
                related_name="in_attendance",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="pessoa",
                to="rh.Pessoa",
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="protocol",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="protocolo.Protocolo",
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="represented",
            field=models.ForeignKey(
                related_name="in_attendance_represented",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="representado",
                blank=True,
                to="rh.Pessoa",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="signed_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="typology",
            field=models.ForeignKey(
                related_name="in_attendance",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Tipologia",
                to="saci.Typology",
            ),
        ),
        migrations.AlterField(
            model_name="attendancelegalsign",
            name="attendance",
            field=models.ForeignKey(
                related_name="legal_signs",
                on_delete=django.db.models.deletion.PROTECT,
                to="saci.Attendance",
            ),
        ),
        migrations.AlterField(
            model_name="step",
            name="attendance",
            field=models.ForeignKey(
                related_name="steps",
                on_delete=django.db.models.deletion.PROTECT,
                to="saci.Attendance",
            ),
        ),
        migrations.AlterField(
            model_name="step",
            name="destination",
            field=models.ForeignKey(
                related_name="step_destination",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Destino",
                to="rh.OrgaoGeral",
            ),
        ),
        migrations.AlterField(
            model_name="step",
            name="origin",
            field=models.ForeignKey(
                related_name="step_origin",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Origem",
                to="rh.OrgaoGeral",
            ),
        ),
    ]
