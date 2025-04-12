# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0048_tipodocumento"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(
                verbose_name="Tipo Documento",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (18, "DECIS\xc3O"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                    (101, "PORTARIA DE INSTAURA\xc7\xc3O"),
                ],
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
                    (18, "N\xc3O INFORMADO"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(
                verbose_name="Tipo de Publica\xe7\xe3o",
                choices=[
                    (1, "ATO"),
                    (2, "DECRETO"),
                    (3, "PORTARIA"),
                    (4, "OF\xcdCIO"),
                    (5, "DESPACHO"),
                    (6, "TERMO"),
                    (7, "MEMORANDO"),
                    (8, "REQUERIMENTO"),
                    (9, "CONCESS\xc3O"),
                    (10, "ACORDO COOPERA\xc7\xc3O T\xc9CNICA"),
                    (11, "LEI"),
                    (12, "APOSTILA"),
                    (14, "DECRETO LEGISLATIVO"),
                    (15, "RESOLU\xc7\xc3O"),
                    (16, "CIRCULAR"),
                    (17, "PROCESSO"),
                    (18, "DECIS\xc3O"),
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                    (101, "PORTARIA DE INSTAURA\xc7\xc3O"),
                ],
            ),
        ),
    ]
