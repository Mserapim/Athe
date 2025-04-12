# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scmmp", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="processojudicial",
            options={
                "ordering": ("-id",),
                "permissions": (
                    ("scmmp_admin", "Administrador de Informa\xe7\xf5es SCMMP"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="membroprocesso",
            name="situacao",
            field=models.SmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Situa\xe7\xe3o",
                choices=[
                    (1, "Em Tr\xc3\xa2mite"),
                    (2, "Sobrestado"),
                    (3, "Julgado"),
                    (4, "Pendente de Recurso"),
                    (5, "Transitado em Julgado: procedente"),
                    (6, "Transitado em Julgado: improcedente"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="processojudicial",
            name="url",
            field=models.CharField(
                max_length=250, null=True, verbose_name="Link", blank=True
            ),
        ),
    ]
