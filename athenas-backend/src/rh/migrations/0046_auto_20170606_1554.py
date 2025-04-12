# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0045_auto_20170529_1814"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pessoafisica",
            name="fator_rh",
            field=models.IntegerField(
                default=2, null=True, verbose_name="Fator RH", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="grau_instrucao",
            field=models.IntegerField(
                default=8,
                blank=True,
                verbose_name="Grau de Instru\xe7\xe3o",
                choices=[
                    (1, "ANALFABETO"),
                    (2, "ALFABETIZADO SEM CURSOS REGULARES"),
                    (3, "SERA EXCLUIDO 4"),
                    (4, "FUNDAMENTAL COMPLETO"),
                    (5, "M\xc9DIO INCOMPLETO"),
                    (6, "MEDIO COMPLETO OU EQUIVALENTE LEGAL"),
                    (7, "SUPERIOR INCOMPLETO"),
                    (8, "SUPERIOR COMPLETO OU EQUIVALENTE LEGAL"),
                    (9, "ESPECIALIZA\xc7\xc3O/P\xd3S"),
                    (10, "MESTRADO"),
                    (11, "DOUTORADO"),
                    (12, "SERA EXCLUIDO"),
                    (13, "SERA EXCLUIDO 1"),
                    (14, "SERA EXCLUIDO 2"),
                    (15, "At\xe9 o 5o ano incompleto do Ensino Fundamental"),
                    (16, "5o ano completo do Ensino Fundamental"),
                    (17, "Do 6o ao 9o ano do Ensino Fundamental incompleto"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="sangue",
            field=models.IntegerField(default=4, blank=True),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="sexual_orientation",
            field=models.PositiveSmallIntegerField(
                default=5,
                null=True,
                verbose_name="Orienta\xe7\xe3o Sexual",
                blank=True,
                choices=[
                    (1, "Heterossexual"),
                    (2, "Homossexual"),
                    (3, "Bissexual"),
                    (4, "Assexual"),
                    (5, "N\xe3o Informada"),
                ],
            ),
        ),
    ]
