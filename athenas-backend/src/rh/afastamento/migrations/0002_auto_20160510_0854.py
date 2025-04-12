# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="afastamentotreinamento",
            name="instituicao",
            field=models.ManyToManyField(
                related_name="afastamentotreinamento", to="rh.UnidadeAdministrativa"
            ),
        ),
        migrations.AlterField(
            model_name="ausenciafalecimento",
            name="pessoa",
            field=models.OneToOneField(
                related_name="ausenciafalecimento",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Pessoa",
                to="rh.PessoaFisica",
            ),
        ),
        migrations.AlterField(
            model_name="ausencianascimento",
            name="crianca",
            field=models.OneToOneField(
                related_name="ausencianascimento",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Filho(a)",
                to="rh.PessoaFisica",
            ),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="prorrogacao",
            field=models.ManyToManyField(
                related_name="afastamento",
                verbose_name="Prorroga\xe7\xe3o",
                to="rh.Prorrogacao",
            ),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="remunerado",
            field=models.BooleanField(default=True, verbose_name="Remunerado"),
        ),
        migrations.AlterField(
            model_name="baselicencasaudejuntamedica",
            name="documento",
            field=models.ManyToManyField(
                related_name="documentos_licencasaudejunta",
                verbose_name="Documenta\xe7\xe3o Complementar",
                to="ged.Arquivo",
            ),
        ),
    ]
