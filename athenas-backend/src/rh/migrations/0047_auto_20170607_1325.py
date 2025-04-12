# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0046_auto_20170606_1554"),
    ]

    operations = [
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="main",
            field=models.BooleanField(default=False, verbose_name="Principal"),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="main",
            field=models.BooleanField(default=False, verbose_name="Principal"),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="fator_rh",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Fator RH",
                blank=True,
                choices=[(1, "-"), (2, "+")],
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
                    (15, "AT\xc9 O 5o ANO INCOMPLETO DO ENSINO FUNDAMENTAL"),
                    (16, "5o ANO COMPLETO DO ENSINO FUNDAMENTAL"),
                    (17, "DO 6o AO 9o ANO DO ENSINO FUNDAMENTAL INCOMPLETO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="sangue",
            field=models.IntegerField(
                default=4, blank=True, choices=[(1, "B"), (2, "AB"), (3, "O"), (4, "A")]
            ),
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
                    (1, "HETEROSSEXUAL"),
                    (2, "HOMOSSEXUAL"),
                    (3, "BISSEXUAL"),
                    (4, "ASSEXUAL"),
                    (5, "N\xc3O INFORMADA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="publication_state",
            field=models.SmallIntegerField(
                default=1,
                choices=[
                    (1, "Em Aberto"),
                    (2, "P\xfablica\xe7\xe3o Solicitada"),
                    (3, "P\xfablica\xe7\xe3o Realizada"),
                    (4, "P\xfablica\xe7\xe3o Cancelada"),
                    (5, "Publica\xe7\xe3o Solicitada ao Expediente"),
                ],
            ),
        ),
    ]
