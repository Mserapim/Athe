# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_correct_base_previdencia(apps, schema_editor):
    FolhaEvento = apps.get_model("gfp", "FolhaEvento")
    qq = FolhaEvento.objects.exclude(correct_contribution_base=0)
    upsd = FolhaEvento.objects.filter(correct_contribution_base__lt=0).update(
        correct_base_previdencia=models.F("correct_contribution_base")
    )
    upsp = qq.filter(evento__tipo="D").update(
        correct_contribution_base=models.F("correct_contribution_base") * -1
    )

    print("BASE_PREVIDENCIAS UPDATEDS: T(%s) D(%s)" % (upsp, upsd))


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0011_auto_20190130_1128"),
        ("gfp", "0058_estruturatabelasalarial_salary_unit"),
    ]

    operations = [
        migrations.AddField(
            model_name="folhaevento",
            name="correct_base_previdencia",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="folhamodelo",
            name="types_of_employee",
            field=models.ManyToManyField(
                related_name="models_payroll", to="standard.Choice"
            ),
        ),
        migrations.AddField(
            model_name="remunerationperiod",
            name="base_gratification",
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name="remunerationperiod",
            name="base_value",
            field=models.DecimalField(default=0, max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name="estruturatabelasalarial",
            name="salary_unit",
            field=models.PositiveSmallIntegerField(
                default=5,
                blank=True,
                verbose_name="Unidade de sal\xc3\xa1rio fixo",
                choices=[
                    (1, "Por Hora"),
                    (2, "Por Dia"),
                    (3, "Por Semana"),
                    (4, "Por Quinzena"),
                    (5, "Por M\xeas"),
                    (6, "Por Tarefa"),
                    (7, "N\xe3o aplic\xe1vel"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="para_indicativo",
            field=models.CharField(
                default=None,
                max_length=1,
                null=True,
                verbose_name="Para os",
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                    ("A", "JOVEM CIDAD\xc3O - APRENDIZ"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="folhamodelo",
            name="somente_ativo",
            field=models.BooleanField(
                default=False, verbose_name="Somente para ativos na folha"
            ),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                blank=True,
                null=True,
                verbose_name="Portal Transpar\xeancia",
                choices=[
                    (1, "REMUNERA\xc7\xc3O: Subs\xeddio"),
                    (3, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o de Representa\xe7\xe3o"),
                    (4, "REMUNERA\xc7\xc3O: VPI"),
                    (5, "REMUNERA\xc7\xc3O: Adicional de F\xe9rias"),
                    (6, "REMUNERA\xc7\xc3O: Abono Perman\xeancia"),
                    (7, "REMUNERA\xc7\xc3O: Gratifica\xe7\xe3o Natilina"),
                    (8, "RECIS\xd3RIA: F\xe9rias Vencidas"),
                    (9, "RECIS\xd3RIA: Adicional de F\xe9rias"),
                    (10, "RECIS\xd3RIA: Gratifica\xe7\xe3o Natalina"),
                    (11, "EFEITOS NEGATIVOS: Redutor de Teto"),
                    (12, "DEDU\xc7\xd4ES: IRRF"),
                    (13, "DEDU\xc7\xd4ES: IRRF - 13\xba Sal\xe1rio"),
                    (14, "DEDU\xc7\xd4ES: Previd\xeancia Social"),
                    (15, "DEDU\xc7\xd4ES: Previd\xeancia - 13\xba Sal\xe1rio"),
                    (16, "INDENIZAT\xd3RIAS: Aux. Alimenta\xe7\xe3o"),
                    (17, "INDENIZAT\xd3RIAS: Aux. Creche"),
                    (18, "INDENIZAT\xd3RIAS: Aux. Moradia"),
                    (19, "INDENIZAT\xd3RIAS: Aux. Transparte"),
                    (20, "INDENIZAT\xd3RIAS: Diferen\xe7a URV"),
                    (21, "INDENIZAT\xd3RIAS: Diferen\xe7a PAE"),
                    (22, "INDENIZAT\xd3RIAS: Abono de Perman\xeancia"),
                    (23, "INDENIZAT\xd3RIAS: Previd\xeancia Social"),
                    (24, "INDENIZAT\xd3RIAS: IRRF"),
                    (25, "Remunera\xe7\xe3o do Cargo Efetivo"),
                    (26, "Outras Verbas Remunerat\xf3rias, Legais ou Judiciais"),
                    (27, "Fun\xe7\xe3o de Confian\xe7a"),
                    (28, "Vencimento"),
                    (29, "Gratifica\xe7\xe3o"),
                    (30, "Gratifica\xe7\xe3o Natalina"),
                    (31, "F\xe9rias Constitucionais"),
                    (32, "Abono Perman\xeancia"),
                    (33, "Contribui\xe7\xe3o Previdenci\xe1ria"),
                    (34, "Imposto de Renda"),
                    (35, "Reten\xe7\xe3o por Teto Constitucional"),
                    (36, "OUTROS REDUTORES/DESCONTOS"),
                    (37, "VERBAS INDENIZAT\xd3RIAS"),
                    (38, "OUTRAS REMUNERA\xc7\xd5ES RETROATIVAS/TEMPOR\xc1RIAS"),
                    (39, "VERBAS EXERCICIOS ANTERIORES"),
                    (40, "OUTRAS REMUNERA\xc7\xd5ES TEMPOR\xc1RIAS"),
                ],
            ),
        ),
        migrations.RunPython(update_correct_base_previdencia, _null_function),
    ]
