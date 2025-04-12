# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0028_auto_20161114_1118"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contracheque",
            name="employee_pays_pension",
            field=models.PositiveIntegerField(
                default=0,
                verbose_name="Pens\xe3o",
                choices=[
                    (0, "N\xc3O PAGA"),
                    (1, "PENS\xc3O ALIMENT\xcdCIA"),
                    (2, "PENS\xc3O POR MORTE"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="employee_source",
            field=models.PositiveIntegerField(
                default=1,
                verbose_name="Tipo de servidor",
                choices=[
                    (1, "SERVIDOR DA CASA"),
                    (2, "SERVIDOR CEDIDO"),
                    (3, "SERVIDOR REQUISITADO"),
                    (4, "ESTAGI\xc1RIO"),
                    (5, "SEM V\xcdNCULO"),
                    (6, "PENSIONISTA - ALIMENT\xcdCIA"),
                    (7, "PARTILHA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="status",
            field=models.PositiveIntegerField(
                default=1,
                blank=True,
                verbose_name="Status",
                choices=[
                    (1, "PRODU\xc7\xc3O"),
                    (2, "ENVIADO"),
                    (3, "PAGAMENTO EFETUADO"),
                    (4, "PAGAMENTO RECUSADO"),
                    (5, "CANCELADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="folha",
            name="status",
            field=models.SmallIntegerField(
                default=1,
                blank=True,
                verbose_name="Status",
                choices=[
                    (1, "EM PRODU\xc7\xc3O"),
                    (2, "EM ANALISE"),
                    (3, "FECHADO"),
                    (4, "PROCESSADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="folha",
            name="unicode_cache",
            field=models.CharField(db_index=True, max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Status",
                choices=[
                    (1, "Carregado com sucesso"),
                    (2, "N\xe3o carregado - matr\xedcula n\xe3o encontrada"),
                    (3, "N\xe3o carregado - servidor exonerado"),
                    (4, "N\xe3o carregado - servidor afastado"),
                    (5, "N\xe3o carregado - evento inexistente"),
                    (6, "Erro - lan\xe7amento inexistente no contracheque"),
                    (9, "N\xe3o carregado - erro desconhecido"),
                ],
            ),
        ),
        migrations.AlterUniqueTogether(
            name="folhamensagem",
            unique_together=set([("folha", "paycheck", "entry")]),
        ),
    ]
