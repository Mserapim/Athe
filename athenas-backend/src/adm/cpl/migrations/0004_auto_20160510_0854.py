# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cpl", "0003_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="participante",
            name="pessoa",
            field=models.OneToOneField(
                to="rh.Pessoa", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="publicacaolicitacao",
            name="veiculo_publicacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                verbose_name="Ve\xedculo Publica\xe7\xe3o",
                choices=[
                    (1, "DOE ACRE"),
                    (2, "DOE AMAPA"),
                    (3, "DOE AMAZONAS"),
                    (4, "DOE RORAIMA"),
                    (5, "DOE RONDONIA"),
                    (6, "DOE PARA"),
                    (7, "DOE TOCANTINS"),
                    (8, "DOE CEARA"),
                    (9, "DOE RIO GRANDE DO NORTE"),
                    (10, "DOE PERNAMBUCO"),
                    (11, "DOE PARAIBA"),
                    (12, "DOE SERGIPE"),
                    (13, "DOE BAHIA"),
                    (14, "DOE MARANHAO"),
                    (15, "DOE PIAUI"),
                    (16, "DOE MINAS GERAIS"),
                    (17, "DOE SAO PAULO"),
                    (18, "DOE ESPIRITO SANTO"),
                    (19, "DOE RIO DE JANEIRO"),
                    (21, "DOE PARANA"),
                    (22, "DOE SANTA CATARINA"),
                    (23, "DOE RIO GRANDE DO SUL"),
                    (24, "DOE MATO GROSSO DO SUL"),
                    (25, "DOE GOIAS"),
                    (26, "DOE DISTRITO FEDERAL"),
                    (27, "DOE MATO GROSSO"),
                    (28, "DIARIO JUSTICA"),
                    (29, "DIARIO JUSTICA ELEITORAL"),
                    (30, "DIARIO OFICIAL DA UNIAO"),
                    (31, "DIARIO OFICIAL DO MUNICIPIO DE PALMAS TO"),
                    (32, "REGISTRO CIVIL DAS PESSOAS NATURAIS"),
                    (33, "PLACAR"),
                    (34, "DI\xc1RIO ELETR\xd4NICO DO MPE"),
                ],
            ),
        ),
    ]
