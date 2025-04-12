# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0037_cargo_remunerated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="anotacaogeral",
            name="tipo_documento",
            field=models.IntegerField(verbose_name="Tipo Documento"),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Inst\xe2ncia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Entr\xe2ncia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="poder",
            field=models.IntegerField(default=5),
        ),
        migrations.AlterField(
            model_name="dadobancario",
            name="tipo_conta",
            field=models.IntegerField(verbose_name="Tipo de Conta"),
        ),
        migrations.AlterField(
            model_name="declaracaoatividade",
            name="turno",
            field=models.IntegerField(default=4),
        ),
        migrations.AlterField(
            model_name="dependencia",
            name="tipo",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="improvementandgraduatecnmp",
            name="nivel",
            field=models.IntegerField(verbose_name="N\xedvel"),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="sexual_orientation",
            field=models.PositiveSmallIntegerField(
                default=5, null=True, verbose_name="Orienta\xe7\xe3o Sexual", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="publication_state",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="tipo",
            field=models.IntegerField(verbose_name="Tipo de Publica\xe7\xe3o"),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="veiculo_publicacao",
            field=models.IntegerField(
                null=True, verbose_name="Ve\xedculo Publica\xe7\xe3o", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="publishedworkscnmp",
            name="work_type",
            field=models.IntegerField(verbose_name="Tipo"),
        ),
    ]
