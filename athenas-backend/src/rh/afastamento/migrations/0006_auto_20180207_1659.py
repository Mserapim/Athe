# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0005_auto_20171201_1454"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ausenciafalecimento",
            name="vinculo",
            field=models.IntegerField(
                default=10,
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
        migrations.AlterField(
            model_name="ausencianascimento",
            name="crianca",
            field=models.ForeignKey(
                related_name="ausencianascimento",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Filho(a)",
                blank=True,
                to="rh.PessoaFisica",
                null=True,
            ),
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
                    (46, "AfastamentoDisponibilidade"),
                    (47, "BancoDeHoras"),
                ],
            ),
        ),
    ]
