# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0005_auto_20180613_1721"),
    ]

    operations = [
        migrations.AddField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="basis_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="convincily_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="proof_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="redaction_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="report_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="basis_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="convincily_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="proof_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="redaction_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="report_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartselectoral",
            name="basis_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartselectoral",
            name="convincily_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartselectoral",
            name="proof_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartselectoral",
            name="redaction_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartselectoral",
            name="report_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="basis_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="convincily_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="proof_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="redaction_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="report_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="basis_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="convincily_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="proof_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="redaction_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AddField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="report_score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="processesforanalysisperformanceinaudiences",
            name="audience_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="Tipo de Audi\xeancia",
                blank=True,
                choices=[
                    (1, "N\xe3o informado"),
                    (2, "Concilia\xe7\xe3o"),
                    (3, "Instru\xe7\xe3o"),
                    (4, "Julgamento"),
                    (5, "Instru\xe7\xe3o e Julgamento"),
                    (6, "Preliminar"),
                    (7, "Interrogat\xf3rio"),
                    (8, "Inquiri\xe7\xe3o"),
                    (9, "Diploma\xe7\xe3o"),
                    (10, "Justifica\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="basis",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="convincily",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="proof",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="redaction",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="report",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscivilcourtlawsuit",
            name="score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="basis",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="convincily",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="proof",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="redaction",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="report",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartscriminalcourtlawsuit",
            name="score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="basis",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="convincily",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="proof",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="redaction",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="report",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartselectoral",
            name="score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="basis",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="convincily",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="proof",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="redaction",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="report",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsoutcourtlawsuit",
            name="score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="basis",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="convincily",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="proof",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="redaction",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="report",
            field=models.CharField(max_length=2000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="procforqualanalysisofthepartsprocuratorate",
            name="score",
            field=models.DecimalField(
                default=0, null=True, max_digits=4, decimal_places=2, blank=True
            ),
        ),
    ]
