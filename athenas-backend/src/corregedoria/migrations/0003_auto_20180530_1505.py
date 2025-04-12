# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corregedoria", "0002_auto_20180522_1239"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configlinkinspectionraf",
            name="inspection_table",
            field=models.IntegerField(
                verbose_name="Tabela de Inspection",
                choices=[
                    (1, "Atendimento ao P\xfablico"),
                    (2, "Processos Judiciais Recebidos"),
                    (3, "Processos Judiciais Devolvidos"),
                    (4, "Processos Eleitorais Recebidos"),
                    (5, "Processos Eleitorais Devolvidos"),
                    (6, "Recomenda\xe7\xf5es Extrajudiciais"),
                    (7, "Termos de Ajustamento de Conduta"),
                    (8, "Audi\xeancias P\xfablicas"),
                    (9, "Procedimentos Extrajudiciais Instaurados"),
                    (10, "Procedimentos Extrajudiciais Arquivados"),
                    (11, "A\xe7\xf5es Civis Publicas e Medidas Ajuizadas"),
                    (12, "A\xe7\xf5es Civis P\xfablicas - Improbidade Administrativa"),
                ],
            ),
        ),
    ]
