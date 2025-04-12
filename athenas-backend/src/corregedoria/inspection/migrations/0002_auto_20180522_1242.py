# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        # ('cif', '0015_auto_20170926_1522'),
        # ('rh', '0063_auto_20180522_1242'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("inspection", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Accumulations",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "accumulation",
                    models.ForeignKey(
                        related_name="+",
                        to="rh.ServidorLotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lista de substitui\xe7\xf5es do membro inspecionado no per\xedodo da inspe\xe7\xe3o.",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Address",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "address",
                    models.ForeignKey(
                        related_name="+", to="cif.AddressCif", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lista de endere\xe7os do membro inspecionado no per\xedodo da inspe\xe7\xe3o.",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="DeadlineRecommendation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("deadline", models.DateField(null=True, blank=True)),
                ("extension", models.BooleanField(default=False)),
                ("response", models.TextField(null=True, blank=True)),
                ("decision", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Recomenda\xe7\xf5es gerais na inspe\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="GeneralObservations",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("observation", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Observa\xe7\xf5es gerais na inspe\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="HarmedCalculation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("harmedcalculation", models.NullBooleanField(default=False)),
                ("justification", models.TextField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Informa\xe7\xe3o sobre PREJU\xcdZO para c\xe1lculo da Nota Final",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Recommendations",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("recommendation", models.TextField(null=True, blank=True)),
                ("waiting_response", models.BooleanField(default=False)),
                ("deadline", models.DateField(null=True, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["waiting_response", "-deadline"],
                "verbose_name": "Recomenda\xe7\xf5es gerais na inspe\xe7\xe3o",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Replacements",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lista de substitui\xe7\xf5es do membro inspecionado no per\xedodo da inspe\xe7\xe3o.",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="Teaching",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Lista de doc\xeancias do membro inspecionado no per\xedodo da inspe\xe7\xe3o.",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="analysisperformanceinaudiences",
            name="observation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="attachments",
            name="area",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="\xc1REA",
                blank=True,
                choices=[
                    (1, "Regularidade dos Servi\xe7os"),
                    (2, "Estrutura"),
                    (3, "Desempenho Funcional"),
                    (4, "Observa\xe7\xf5es Gerais"),
                    (5, "Recomenda\xe7\xf5es"),
                    (6, "Anexos"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="attachments",
            name="attachment_type",
            field=models.SmallIntegerField(
                default=1,
                null=True,
                verbose_name="TIPO DE ANEXO",
                blank=True,
                choices=[
                    (1, "Editais"),
                    (2, "Portaria de Delega\xe7\xe3o"),
                    (3, "Certid\xf5es"),
                    (4, "Ata"),
                    (5, "Pe\xe7as"),
                    (6, "Audi\xeancias"),
                    (7, "Tabelas Extrajudiciais"),
                    (8, "Impugna\xe7\xf5es"),
                    (9, "Cumprimento de Senten\xe7as"),
                    (10, "Relat\xf3rios e-Proc"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="courtlawsuitcontrol",
            name="apps",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="courtlawsuitcontrol",
            name="others",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="executionorganmanagement",
            name="observation",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="inspection",
            name="holder_employee",
            field=models.ForeignKey(
                related_name="+",
                blank=True,
                to="rh.Servidor",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="outcourtlawsuitcontrol",
            name="apps",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="outcourtlawsuitcontrol",
            name="others",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="outcourtlawsuitcount",
            name="number_of_public_audiences_in_the_last_year",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="outcourtlawsuitcount",
            name="number_of_tac_administrative_dishonesty",
            field=models.SmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="publicattendance",
            name="apps",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="publicattendance",
            name="others",
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="qualitativeanalysisofthepartscivilcourtlawsuit",
            name="no_parts_to_analyze",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="qualitativeanalysisofthepartscriminalcourtlawsuit",
            name="no_parts_to_analyze",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="qualitativeanalysisofthepartselectoral",
            name="no_parts_to_analyze",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AddField(
            model_name="qualitativeanalysisofthepartsoutcourtlawsuit",
            name="no_parts_to_analyze",
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="attachments",
            name="inspection",
            field=models.ForeignKey(
                related_name="attachments",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="inspection",
            name="accumulates",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="attendance",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="daily_attendance",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="replacements",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="residence",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="teaching",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="inspection",
            name="titular_employee",
            field=models.BooleanField(default=False),
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
                ],
            ),
        ),
        migrations.AlterField(
            model_name="promptnesscourtlawsuit",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="promptnessoutcourtlawsuit",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="promptnessuppermanagement",
            name="score_table",
            field=models.IntegerField(
                default=2,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="registeredpublicattendancenumber",
            name="score_table",
            field=models.IntegerField(
                default=1,
                null=True,
                verbose_name="Tabela de C\xe1lculo",
                blank=True,
                choices=[
                    (1, "N\xe3o se aplica"),
                    (2, "Presteza  - Feitos Judiciais"),
                    (3, "Presteza  - Feitos Extrajudiciais"),
                    (4, "Presteza  - Atendimento tempestivo \xe0s determina\xe7\xf5es"),
                    (5, "Produtividade - Fator I - Pe\xe7as Iniciais"),
                    (6, "Produtividade - Fator I - Procedimentos Administrativos"),
                    (7, "Produtividade - Fator II - Pe\xe7as Judiciais"),
                    (8, "Produtividade - Fator II - Procedimentos Administrativos"),
                    (9, "Produtividade - Fator III"),
                    (10, "Produtividade - Fator IV - Audi\xeancias Judiciais"),
                    (
                        11,
                        "Produtividade - Fator IV - Aud. P\xfablicas ou Administrativas",
                    ),
                    (12, "Produtividade - Fator IV - J\xfaris"),
                    (13, "Atendimento ao P\xfablico"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="teaching",
            name="inspection",
            field=models.ForeignKey(
                related_name="teachings",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="teaching",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="teaching",
            name="teaching",
            field=models.ForeignKey(
                related_name="+", to="cif.Teaching", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="replacements",
            name="inspection",
            field=models.ForeignKey(
                related_name="replacement",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="replacements",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="replacements",
            name="replacement",
            field=models.ForeignKey(
                related_name="+",
                to="rh.MovimentacaoSubstituicao",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="recommendations",
            name="inspection",
            field=models.ForeignKey(
                related_name="recommendations",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="recommendations",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="harmedcalculation",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="harmedcalculation",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="generalobservations",
            name="inspection",
            field=models.OneToOneField(
                to="inspection.Inspection", on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="generalobservations",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="deadlinerecommendation",
            name="recommendation",
            field=models.ForeignKey(
                related_name="deadlines",
                to="inspection.Recommendations",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="address",
            name="inspection",
            field=models.ForeignKey(
                related_name="addresses",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="address",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="accumulations",
            name="inspection",
            field=models.ForeignKey(
                related_name="accumulation",
                to="inspection.Inspection",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="accumulations",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
