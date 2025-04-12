# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0030_auto_20160808_1526"),
        ("afastamento", "0002_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="baselicencaafastamento",
            options={
                "ordering": ["-data_inicio", "-estado"],
                "verbose_name": "BaseLicencaAfastamento",
            },
        ),
        migrations.AddField(
            model_name="baselicencaafastamento",
            name="designation_exercise",
            field=models.ManyToManyField(
                related_name="departures_exercise",
                null=True,
                to="rh.ServidorLotacao",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="afastamentocursoconcurso",
            name="cargo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="rh.Cargo",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="afastamentodeslocamento",
            name="localidade_destino",
            field=models.ForeignKey(
                related_name="deslocamento_destino",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Localidade",
            ),
        ),
        migrations.AlterField(
            model_name="afastamentodeslocamento",
            name="localidade_origem",
            field=models.ForeignKey(
                related_name="deslocamento_origem",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.Localidade",
            ),
        ),
        migrations.AlterField(
            model_name="afastamentomandatoeletivo",
            name="cargo_eletivo",
            field=models.IntegerField(
                default=1,
                choices=[
                    (1, "Prefeito/Vice"),
                    (2, "Vereador"),
                    (3, "Deputado Estadual"),
                    (4, "Deputado Federal"),
                    (5, "Governador/Vice"),
                    (6, "Senador/Presidente Rep\xfablica/Vice"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="afastamentooutroorgao",
            name="contribuicao",
            field=models.IntegerField(
                default=2,
                verbose_name="Op\xe7\xe3o de contribui\xe7\xe3o",
                choices=[(1, "Sim"), (2, "N\xe3o")],
            ),
        ),
        migrations.AlterField(
            model_name="afastamentooutroorgao",
            name="onus",
            field=models.IntegerField(
                default=1,
                verbose_name="\xd4nus",
                choices=[(1, "Origem"), (2, "Requisitante")],
            ),
        ),
        migrations.AlterField(
            model_name="afastamentotreinamento",
            name="curso",
            field=models.ForeignKey(
                related_name="afatreinamento_curso",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.Curso",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="afastamentotreinamento",
            name="instituicao",
            field=models.ManyToManyField(
                related_name="afastamentotreinamento",
                to="rh.UnidadeAdministrativa",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="motivo",
            field=models.IntegerField(
                default=2,
                blank=True,
                choices=[
                    (1, "F\xc9RIAS"),
                    (2, "LICEN\xc7A"),
                    (3, "RECESSO NATALINO"),
                    (4, "PLANT\xc3O"),
                    (5, "VIAGEM A TRABALHO"),
                    (6, "DESEMPENHO DE FUN\xc7\xc3O"),
                    (7, "DISPOSI\xc7\xc3O DE OUTRO \xd3RG\xc3O"),
                    (8, "REPRESENTA\xc7\xc3O DE CLASSE"),
                    (9, "ATUA\xc7\xc3O DE GRUPO DE TRABALHO"),
                    (10, "TR\xc2NSITO/PROMO\xc7\xc3O/REMO\xc7\xc3O"),
                    (12, "SUSPENS\xc3O"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="prorrogacao",
            field=models.ManyToManyField(
                related_name="afastamento",
                null=True,
                verbose_name="Prorroga\xe7\xe3o",
                to="rh.Prorrogacao",
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="baselicencasaudejuntamedica",
            name="documento",
            field=models.ManyToManyField(
                related_name="documentos_licencasaudejunta",
                verbose_name="Documenta\xe7\xe3o Complementar",
                to="ged.Arquivo",
                blank=True,
            ),
        ),
    ]
