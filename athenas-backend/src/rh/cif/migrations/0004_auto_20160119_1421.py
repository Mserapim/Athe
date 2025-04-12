# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0003_auto_20151008_1000"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="controlinformationmember",
            options={
                "ordering": ("employee__servidor",),
                "permissions": (
                    ("cif_admin", "Administrador de Informa\xe7\xf5es Membros"),
                    ("cif_membro", "Membro usu\xe1rio"),
                    ("cif_auditoria", "Auditoria do Sistema"),
                ),
            },
        ),
        migrations.AddField(
            model_name="address",
            name="refperiod_address",
            field=models.ForeignKey(
                related_name="ref_address",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="debtsencumbrances",
            name="refperiod_debts",
            field=models.ForeignKey(
                related_name="ref_debts",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="property",
            name="refperiod_property",
            field=models.ForeignKey(
                related_name="ref_property",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="teaching",
            name="refperiod_teaching",
            field=models.ForeignKey(
                related_name="ref_teaching",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="controlinformationmember",
            name="referenceperiod",
            field=models.ForeignKey(
                related_name="controlinformation",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Per\xedodo de Refer\xeancia",
                to="cif.ReferencePeriod",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="end_date",
            field=models.DateField(
                null=True, verbose_name="Data Fim Exerc\xedcio", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="exercise",
            field=models.CharField(
                default="0", max_length=50, verbose_name="Per\xedodo de Exerc\xedcio"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="exercise_year",
            field=models.IntegerField(
                default=0, verbose_name="Per\xedodo de Exerc\xedcio"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="referenceperiod",
            name="start_date",
            field=models.DateField(
                null=True, verbose_name="Data In\xedcio Exerc\xedcio", blank=True
            ),
            preserve_default=True,
        ),
    ]
