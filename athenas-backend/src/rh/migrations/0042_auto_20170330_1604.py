# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0041_auto_20170327_1632"),
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
                    (95, "DECLARA\xc7\xc3O DE ENTRADA EM ATIVIDADE"),
                    (96, "TERMO LOTA\xc7\xc3O"),
                    (97, "TERMO EXERC\xcdCIO"),
                    (98, "TERMO POSSE"),
                    (99, "OUTROS"),
                    (100, "DOCUMENTO DIGITAL"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="tipo",
            field=models.IntegerField(
                null=True,
                verbose_name="Tipo",
                choices=[
                    (1, "C\xd4NJUGE"),
                    (2, "COMPANHEIRO(A)"),
                    (3, "FILHO(A) N\xc3O EMANCIPADO MENOR DE 21 ANOS"),
                    (4, "FILHO INV\xc1LIDO(A)"),
                    (5, "PAI(M\xc3E) COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (
                        6,
                        "IRM\xc3O N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                    ),
                    (7, "IRM\xc3O INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (
                        8,
                        "ENTEADO N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                    ),
                    (9, "ENTEADO INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (
                        10,
                        "MENOR TUTELADO N\xc3O EMANCIPADO MENOR DE 21 ANOS COM DEPEND\xcaNCIA ECON\xd4MICA",
                    ),
                    (11, "MENOR TUTELADO INV\xc1LIDO COM DEPEND\xcaNCIA ECON\xd4MICA"),
                    (12, "OUTROS"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="orgaogeral",
            name="codigo_igeprev",
            field=models.IntegerField(
                unique=True, verbose_name="C\xf3digo igeprev", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="renda_familiar",
            field=models.DecimalField(
                null=True,
                verbose_name="Renda Familiar",
                max_digits=12,
                decimal_places=2,
                blank=True,
            ),
        ),
    ]
