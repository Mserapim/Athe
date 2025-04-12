# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0019_cargoquadro_military"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="declaracaoatividade",
            options={
                "ordering": ("-data_exercicio",),
                "verbose_name": "Declara\xe7\xe3o de Atividade",
            },
        ),
        migrations.AlterModelOptions(
            name="movimentacaosubstituicao",
            options={
                "ordering": ["-data_inicio"],
                "verbose_name": "Movimenta\xe7\xe3o de Substitui\xe7\xe3o",
            },
        ),
        migrations.AlterField(
            model_name="anotacaocomunicacao",
            name="tipo_comunicacao",
            field=models.IntegerField(
                default=4,
                verbose_name="Tipo Comunica\xe7\xe3o",
                choices=[
                    (3, "F\xc9RIAS"),
                    (1, "RECESSO"),
                    (2, "LICEN\xc7A"),
                    (4, "AUS\xcaNCIA DA COMARCA"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="anotacaohorarioespecial",
            name="dados_horario",
            field=models.ManyToManyField(
                to="rh.AnotHorEspDados", verbose_name="Dados Hor\xe1rio"
            ),
        ),
        migrations.AlterField(
            model_name="documento",
            name="dados_especificos",
            field=models.ManyToManyField(
                to="rh.DocsDadosEspecificos", verbose_name="Dados Espec\xedficos"
            ),
        ),
        migrations.AlterField(
            model_name="lotacao",
            name="grupo",
            field=models.ManyToManyField(to="rh.Lotacao"),
        ),
        migrations.AlterField(
            model_name="movimentacaodesligamento",
            name="movimentacao_posse",
            field=models.OneToOneField(
                related_name="desligamento",
                to="rh.MovimentacaoPosse",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="orgaogeral",
            name="endereco",
            field=models.ManyToManyField(to="rh.Endereco", verbose_name="Endere\xe7o"),
        ),
        migrations.AlterField(
            model_name="orgaogeral",
            name="telefone",
            field=models.ManyToManyField(to="rh.Telefone"),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="dado_bancario",
            field=models.ManyToManyField(
                related_name="dados_bancarios_pessoas",
                verbose_name="Dado Banc\xe1rio",
                to="rh.DadoBancario",
            ),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="endereco",
            field=models.ManyToManyField(to="rh.Endereco", verbose_name="Endere\xe7o"),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="telefone",
            field=models.ManyToManyField(to="rh.Telefone"),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="documento",
            field=models.ManyToManyField(to="rh.Documento"),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="email_pessoal",
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="pessoafisica",
            name="necessidades_especiais",
            field=models.ManyToManyField(
                related_name="pessoafisica", to="rh.NecessidadeEspecial"
            ),
        ),
        migrations.AlterField(
            model_name="publicacao",
            name="vehicle_page",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="curso",
            field=models.ManyToManyField(to="rh.Curso"),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="documento_digital",
            field=models.ManyToManyField(
                related_name="servidor",
                verbose_name="Documentos digitais",
                to="rh.DocumentoDigital",
            ),
        ),
        migrations.AlterField(
            model_name="servidor",
            name="user",
            field=models.OneToOneField(
                related_name="servidor",
                null=True,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Usu\xe1rio",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="unidadeadministrativa",
            name="email",
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="unidadeadministrativa",
            name="responsavel",
            field=models.OneToOneField(
                null=True,
                blank=True,
                to="rh.PessoaFisica",
                verbose_name="Respons\xe1vel",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
