# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0065_auto_20180820_2002"),
    ]

    operations = [
        migrations.AddField(
            model_name="trainee",
            name="educational_institution",
            field=models.ForeignKey(
                related_name="trainee_educational_institution",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Institui\xe7\xe3o Educacional",
                blank=True,
                to="rh.PessoaJuridica",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="trainee",
            name="employee_supervisor",
            field=models.ForeignKey(
                related_name="trainee_supervisor",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Supervisor",
                blank=True,
                to="rh.Servidor",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="trainee",
            name="insurance_number",
            field=models.CharField(
                max_length=50, null=True, verbose_name="N\xfamero de seguro", blank=True
            ),
        ),
        migrations.AddField(
            model_name="trainee",
            name="integration_agent",
            field=models.ForeignKey(
                related_name="trainee_educational_integration_agent",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Agente de Integra\xe7\xe3o",
                blank=True,
                to="rh.PessoaJuridica",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="trainee",
            name="level",
            field=models.IntegerField(default=1, verbose_name="N\xedvel"),
        ),
        migrations.AddField(
            model_name="trainee",
            name="nature",
            field=models.IntegerField(default=1, verbose_name="Natureza"),
        ),
        migrations.AddField(
            model_name="trainee",
            name="occupation_area",
            field=models.CharField(
                max_length=50,
                null=True,
                verbose_name="\xc1rea de ocupa\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name="trainee",
            name="value",
            field=models.DecimalField(
                null=True,
                verbose_name="Valor",
                max_digits=14,
                decimal_places=2,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="lotacao",
            name="id_itop",
            field=models.SmallIntegerField(unique=True, null=True, blank=True),
        ),
    ]
