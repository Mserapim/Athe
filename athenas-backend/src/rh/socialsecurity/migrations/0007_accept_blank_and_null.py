# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0006_change_fk_unique_to_one2one"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employmentbond",
            name="archive",
            field=models.CharField(
                max_length=256, null=True, verbose_name="Arquivo", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="employmentbond",
            name="deduction",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Dedu\xe7\xf5es", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="employmentbond",
            name="end_date",
            field=models.DateField(null=True, verbose_name="T\xe9rmino", blank=True),
        ),
        migrations.AlterField(
            model_name="employmentbond",
            name="liquid_days",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Tempo l\xedquido", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="employmentbond",
            name="possession",
            field=models.OneToOneField(
                null=True,
                blank=True,
                to="rh.MovimentacaoPosse",
                verbose_name="Movimenta\xe7\xe3o de Posse",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="contribution_prevision_date",
            field=models.DateField(
                null=True,
                verbose_name="Data da aposentadoria por contribui\xe7\xe3o",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="exercise_date",
            field=models.DateField(
                null=True, verbose_name="Primeiro emprego", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="integral_prevision_date",
            field=models.DateField(
                null=True, verbose_name="Data da aposentadoria integral", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="last_occupation",
            field=models.ForeignKey(
                related_name="retirementprevisions",
                verbose_name="\xc3\x9altima ocupa\xc3\xa7\xc3\xa3o",
                blank=True,
                to="rh.Quadro",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
