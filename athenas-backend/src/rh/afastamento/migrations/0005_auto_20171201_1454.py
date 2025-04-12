# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0004_auto_20170427_1354"),
    ]

    operations = [
        migrations.CreateModel(
            name="BancoDeHoras",
            fields=[
                (
                    "baselicencaafastamento_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="afastamento.BaseLicencaAfastamento",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "db_table": "afastamento_bancodehoras",
                "verbose_name": "Folga Compensa\xe7\xe3o",
            },
            bases=("afastamento.baselicencaafastamento",),
        ),
        migrations.AlterField(
            model_name="baselicencaafastamento",
            name="tipo",
            field=models.IntegerField(
                default=1,
                blank=True,
                db_index=True,
                choices=[
                    (1, "BaseLicencaAfastamento"),
                    (2, "Afastamento"),
                    (3, "Licenca"),
                    (4, "Ausencia"),
                    (5, "FeriasAfastamento"),
                    (6, "Viagem"),
                    (7, "Recesso"),
                    (8, "LicencaSaude"),
                    (9, "LicencaSaude3Dias"),
                    (10, "LicencaSaudeJuntaMedica"),
                    (11, "LicencaDoencaPessoaFamilia"),
                    (12, "LicencaMaternidade"),
                    (13, "LicencaAdocao"),
                    (14, "LicencaAfastamentoConjuge"),
                    (15, "LicencaServicoMilitar"),
                    (16, "LicencaAtividadePolitica"),
                    (17, "LicencaCapacitacao"),
                    (18, "LicencaInteresseParticular"),
                    (19, "LicencaMandatoClassista"),
                    (20, "AfastamentoOutroOrgao"),
                    (21, "AfastamentoMandatoEletivo"),
                    (22, "AfastamentoEstudar"),
                    (23, "AfastamentoMissao"),
                    (24, "AfastamentoEleitoral"),
                    (25, "AfastamentoServirJuri"),
                    (26, "AfastamentoTreinamento"),
                    (27, "AfastamentoDeslocamento"),
                    (28, "AfastamentoCompeticao"),
                    (29, "AfastamentoCursoConcurso"),
                    (30, "AfastamentoPrisao"),
                    (31, "AusenciaDoacaoSangue"),
                    (32, "AusenciaEleitor"),
                    (33, "AusenciaCasamento"),
                    (34, "AusenciaNascimento"),
                    (35, "AusenciaFalecimento"),
                    (36, "AusenciaConclusao"),
                    (37, "LicencaSaude30Dias"),
                    (38, "FolgaEleitoral"),
                    (39, "AtuacaoGrupoTrabalho"),
                    (40, "DesempenhoFuncao"),
                    (41, "Plantao"),
                    (42, "FolgaCompensacao"),
                    (43, "FolgaAniversario"),
                    (44, "AfastamentoSuspensao"),
                    (45, "AfastamentoComparecimentoJuizo"),
                    (46, "BancoDeHoras"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="licencasaude",
            name="acidente_transito",
            field=models.IntegerField(
                default=True,
                null=True,
                blank=True,
                choices=[(1, "ATROPELAMENTO"), (2, "COLIS\xc3O")],
            ),
        ),
    ]
