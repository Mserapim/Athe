# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0058_auto_20171108_1703"),
    ]

    operations = [
        migrations.AddField(
            model_name="lotacao",
            name="code_cnmp",
            field=models.CharField(max_length=4, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="dependente",
            name="grau_parentesco",
            field=models.IntegerField(
                verbose_name="Tipo de Parentesco",
                choices=[
                    (1, "C\xd4NJUGE"),
                    (2, "COMPANHEIRO"),
                    (3, "FILHO(A)"),
                    (4, "PAI/M\xc3E"),
                    (5, "IRM\xc3O"),
                    (6, "ENTEADO"),
                    (7, "MENOR TUTELADO"),
                    (8, "EX-C\xd4NJUGE"),
                    (9, "NETOS"),
                    (10, "OUTROS"),
                    (11, "OUTROS - DEPEND\xcaNCIA ECON\xd4MICA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaosubstituicao",
            name="designation_substituted",
            field=models.ForeignKey(
                related_name="substitution_substituted",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="relationship",
            name="app",
            field=models.IntegerField(
                default=1, verbose_name="Aplicativo", choices=[(1, "DIARIAS")]
            ),
        ),
        migrations.AlterField(
            model_name="servidorvinculo",
            name="vinculo",
            field=models.IntegerField(
                verbose_name="Tipo de V\xednculo",
                choices=[
                    (1, "C\xd4NJUGE"),
                    (2, "COMPANHEIRO"),
                    (3, "FILHO(A)"),
                    (4, "PAI/M\xc3E"),
                    (5, "IRM\xc3O"),
                    (6, "ENTEADO"),
                    (7, "MENOR TUTELADO"),
                    (8, "EX-C\xd4NJUGE"),
                    (9, "NETOS"),
                    (10, "OUTROS"),
                    (11, "OUTROS - DEPEND\xcaNCIA ECON\xd4MICA"),
                ],
            ),
        ),
    ]
