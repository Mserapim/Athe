# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0026_auto_20160725_1256"),
    ]

    operations = [
        migrations.CreateModel(
            name="FaseRecursal",
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
                    "numero_local",
                    models.CharField(max_length=25, verbose_name="N\xfamero Local"),
                ),
                (
                    "orgao_julgador",
                    models.CharField(
                        max_length=250, verbose_name="\xd3rg\xe3o Julgador"
                    ),
                ),
                (
                    "nome_acao",
                    models.CharField(max_length=250, verbose_name="Nome da A\xe7\xe3o"),
                ),
                (
                    "url",
                    models.CharField(
                        max_length=250, null=True, verbose_name="Link", blank=True
                    ),
                ),
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
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="MembroProcesso",
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
                    "situacao",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Houve Cumprimento?",
                        choices=[
                            (1, "Em Tr\xc3\xa2mite"),
                            (2, "Sobrestado"),
                            (3, "Julgado"),
                            (4, "Pendente de Recurso"),
                            (5, "Transitado em Julgado: procedente"),
                            (6, "Transitado em Julgado: improcedente"),
                        ],
                    ),
                ),
                (
                    "data_situacao",
                    models.DateField(null=True, verbose_name="Data", blank=True),
                ),
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
                    "membro",
                    models.ForeignKey(
                        related_name="membro_processo",
                        verbose_name="Membro",
                        to="rh.Servidor",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
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
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="ProcessoJudicial",
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
                    "numero_cnj",
                    models.CharField(
                        unique=True, max_length=25, verbose_name="N\xfamero CNJ"
                    ),
                ),
                (
                    "numero_local",
                    models.CharField(max_length=25, verbose_name="N\xfamero Local"),
                ),
                (
                    "orgao_julgador",
                    models.CharField(
                        max_length=250, verbose_name="\xd3rg\xe3o Julgador"
                    ),
                ),
                (
                    "nome_acao",
                    models.CharField(max_length=250, verbose_name="Nome da A\xe7\xe3o"),
                ),
                ("url", models.CharField(max_length=250, verbose_name="Link")),
                (
                    "tipo_processo_judicial",
                    models.SmallIntegerField(
                        verbose_name="Tipo", choices=[(1, "CIVIL"), (2, "CRIMINAL")]
                    ),
                ),
                (
                    "resumo",
                    models.TextField(
                        default="", null=True, verbose_name="Resumo", blank=True
                    ),
                ),
                (
                    "observacao",
                    models.TextField(
                        default="",
                        null=True,
                        verbose_name="Observa\xe7\xe3o",
                        blank=True,
                    ),
                ),
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
                "ordering": ("employee__servidor",),
                "permissions": (
                    ("scmmp_admin", "Administrador de Informa\xe7\xf5es SCMMP"),
                ),
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="SancaoJudicial",
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
                ("resumo", models.TextField(default="", verbose_name="Resumo")),
                (
                    "data_imposicao",
                    models.DateField(verbose_name="Data da Imposi\xe7\xe3o"),
                ),
                (
                    "cumprimento",
                    models.SmallIntegerField(
                        blank=True,
                        null=True,
                        verbose_name="Houve Cumprimento?",
                        choices=[(1, "SIM"), (2, "N\xc3\x83O")],
                    ),
                ),
                (
                    "data_cumprimento",
                    models.DateField(
                        null=True, verbose_name="Data do Cumprimento", blank=True
                    ),
                ),
                (
                    "ext_punibilidade",
                    models.SmallIntegerField(
                        verbose_name="Houve Extin\xe7\xe3o da Punibilidade?",
                        choices=[(1, "SIM"), (2, "N\xc3\x83O")],
                    ),
                ),
                (
                    "reabilitacao",
                    models.SmallIntegerField(
                        verbose_name="Reabilita\xe7\xe3o?",
                        choices=[(1, "SIM"), (2, "N\xc3\x83O")],
                    ),
                ),
                (
                    "data_reabilitacao",
                    models.DateField(
                        null=True, verbose_name="Data da Reabilita\xe7\xe3o", blank=True
                    ),
                ),
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
                    "membro_processo",
                    models.ForeignKey(
                        related_name="sancaojudicial",
                        verbose_name="Membro",
                        to="scmmp.MembroProcesso",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "modified_by",
                    models.ForeignKey(
                        related_name="+",
                        on_delete=django.db.models.deletion.PROTECT,
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "processo_judicial",
                    models.ForeignKey(
                        related_name="processo",
                        verbose_name="Processo Judicial",
                        to="scmmp.ProcessoJudicial",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AddField(
            model_name="membroprocesso",
            name="processo_judicial",
            field=models.ForeignKey(
                related_name="membro_processo",
                verbose_name="Processo Judicial",
                to="scmmp.ProcessoJudicial",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="faserecursal",
            name="processo_judicial",
            field=models.ForeignKey(
                related_name="fase_recursal",
                verbose_name="Processo Judicial",
                to="scmmp.ProcessoJudicial",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
