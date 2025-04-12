# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("afastamento", "0003_auto_20160818_0946"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("rh", "0030_auto_20160808_1526"),
    ]

    operations = [
        migrations.CreateModel(
            name="TableJobPositionSubstitute",
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
                (
                    "substituted_number",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Substituted number"
                    ),
                ),
                (
                    "substituted_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="Substituted name"
                    ),
                ),
                (
                    "substitute_number",
                    models.CharField(
                        max_length=20, null=True, verbose_name="Substitute number"
                    ),
                ),
                (
                    "substitute_name",
                    models.CharField(
                        max_length=100, null=True, verbose_name="Substitute name"
                    ),
                ),
                (
                    "position_number",
                    models.IntegerField(null=True, verbose_name="Position number"),
                ),
            ],
            options={
                "db_table": "VW_JOB_POSITION_SUBSTITUTE",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="EmployeeWorkplaceHistory",
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
                ("pk_history", models.IntegerField()),
                (
                    "designacao",
                    models.BooleanField(
                        default=False, verbose_name="Designa\xe7\xe3o de exerc\xedcio"
                    ),
                ),
                (
                    "provisorio",
                    models.BooleanField(
                        default=False, verbose_name="Lota\xe7\xe3o Provis\xf3ria"
                    ),
                ),
                (
                    "data_vigencia",
                    models.DateField(
                        null=True, verbose_name="Data Vig\xeancia", blank=True
                    ),
                ),
                (
                    "data_vigencia_inicio",
                    models.DateField(
                        null=True, verbose_name="Data Vig\xeancia In\xedcio"
                    ),
                ),
                (
                    "data_vigencia_fim",
                    models.DateField(
                        null=True, verbose_name="Data Vig\xeancia Fim", blank=True
                    ),
                ),
                ("data_cadastro", models.DateField(auto_now_add=True)),
                ("data_alteracao", models.DateField(auto_now=True, null=True)),
                (
                    "full_exercise",
                    models.BooleanField(
                        default=False, verbose_name="Exerc\xedcio pleno"
                    ),
                ),
                (
                    "responsible",
                    models.BooleanField(default=False, verbose_name="Respons\xe1vel"),
                ),
                ("from_substitution", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(default=True)),
                ("owner", models.BooleanField(default=False)),
                (
                    "anotacao_geral_lotacao",
                    models.ForeignKey(
                        blank=True,
                        to="rh.AnotacaoGeral",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "changed_by_departure",
                    models.ForeignKey(
                        related_name="history_employee_workplace_changed",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="afastamento.BaseLicencaAfastamento",
                        null=True,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.CreateModel(
            name="WorkplaceExerciseHistory",
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
                ("date", models.DateTimeField(auto_now_add=True)),
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
                    "employee_workplace",
                    models.ForeignKey(
                        related_name="exercise_history",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="rh.EmployeeWorkplaceHistory",
                        null=True,
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
                (
                    "workplace",
                    models.ForeignKey(
                        related_name="exercise_history",
                        to="rh.Lotacao",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["date"],
                "verbose_name": "Hist\xf3rico de lota\xe7\xf5es e seus exerc\xedcios",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.RemoveField(
            model_name="servidorlotacao",
            name="situation",
        ),
        migrations.AddField(
            model_name="inativacaocargomembro",
            name="designation",
            field=models.ForeignKey(
                related_name="inactivation_jobposition",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="inativacaocargomembro",
            name="possession",
            field=models.ForeignKey(
                related_name="inativacaocargo",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Posse",
                blank=True,
                to="rh.MovimentacaoPosse",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicaomembro",
            name="automatic_substitute",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicaomembro",
            name="designation_substitute",
            field=models.ForeignKey(
                related_name="membersubstitution_substitute",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="movimentacaosubstituicaomembro",
            name="designation_substituted",
            field=models.ForeignKey(
                related_name="membersubstitution_substituted",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="pessoa",
            name="slug",
            field=models.SlugField(default="", max_length=100, verbose_name="Slug"),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="changed_by_departure",
            field=models.ForeignKey(
                related_name="employee_workplace_changed",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="afastamento.BaseLicencaAfastamento",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="child_of",
            field=models.ForeignKey(
                related_name="father_of",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Derivada de",
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="created_by_departure",
            field=models.ForeignKey(
                related_name="employee_workplace_created",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="afastamento.BaseLicencaAfastamento",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="owner",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="servidorlotacao",
            name="responsible",
            field=models.BooleanField(default=False, verbose_name="Respons\xe1vel"),
        ),
        migrations.AlterField(
            model_name="anotacaoevento",
            name="nome_evento",
            field=models.CharField(
                default="", max_length=100, verbose_name="Nome Evento"
            ),
        ),
        migrations.AlterField(
            model_name="anotacaoplantao",
            name="periodo",
            field=models.CharField(
                default="1",
                max_length=10,
                verbose_name="Per\xedodo",
                choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
            ),
        ),
        migrations.AlterField(
            model_name="anotacaorecesso",
            name="periodo",
            field=models.CharField(
                default="1",
                max_length=10,
                verbose_name="Per\xedodo",
                choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
            ),
        ),
        migrations.AlterField(
            model_name="anotacaotempodobro",
            name="periodo",
            field=models.CharField(
                default="",
                max_length=10,
                verbose_name="Per\xedodo",
                choices=[("1", "PRIMEIRO"), ("2", "SEGUNDO")],
            ),
        ),
        migrations.AlterField(
            model_name="banco",
            name="numero",
            field=models.CharField(
                default="", unique=True, max_length=3, verbose_name="N\xfamero"
            ),
        ),
        migrations.AlterField(
            model_name="cargo",
            name="codigo",
            field=models.CharField(default="", max_length=12, verbose_name="C\xf3digo"),
        ),
        migrations.AlterField(
            model_name="carreira",
            name="codigo",
            field=models.CharField(default="", max_length=10, verbose_name="C\xf3digo"),
        ),
        migrations.AlterField(
            model_name="cbo",
            name="codigo",
            field=models.CharField(default="", max_length=10, verbose_name="C\xf3digo"),
        ),
        migrations.AlterField(
            model_name="cbo",
            name="descricao",
            field=models.CharField(
                default="", max_length=250, verbose_name="Descri\xe7\xe3o"
            ),
        ),
        migrations.AlterField(
            model_name="dadobancario",
            name="agencia",
            field=models.CharField(
                default="", max_length=15, verbose_name="Ag\xeancia com DV"
            ),
        ),
        migrations.AlterField(
            model_name="dadobancario",
            name="conta_corrente_completa",
            field=models.CharField(
                default="", max_length=15, verbose_name="Conta Corrente com DV"
            ),
        ),
        migrations.AlterField(
            model_name="docsdadosespecificos",
            name="valor",
            field=models.CharField(default="", max_length=30, verbose_name="Valor"),
        ),
        migrations.AlterField(
            model_name="documento",
            name="numero",
            field=models.CharField(default="", max_length=30, verbose_name="N\xfamero"),
        ),
        migrations.AlterField(
            model_name="estado",
            name="sigla",
            field=models.CharField(default="", max_length=2),
        ),
        migrations.AlterField(
            model_name="inativacaocargomembro",
            name="cargo_arquimedes",
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name="inativacaocargomembro",
            name="publicacao_alteracao",
            field=models.ForeignKey(
                related_name="inativacao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Documento Revoga\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="movimentacaosubstituicaomembro",
            name="cargo_arquimedes",
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name="pessoa",
            name="nome",
            field=models.CharField(default="", max_length=100, verbose_name="Nome"),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="designacao",
            field=models.BooleanField(
                default=False, verbose_name="Designa\xe7\xe3o de exerc\xedcio"
            ),
        ),
        migrations.AlterField(
            model_name="telefone",
            name="numero",
            field=models.CharField(default="", max_length=15, verbose_name="N\xfamero"),
        ),
        migrations.AlterField(
            model_name="tiposervidor",
            name="indicativo",
            field=models.CharField(
                default="S",
                max_length=1,
                choices=[
                    ("I", "INDEFINIDO"),
                    ("E", "ESTAGI\xc1RIO"),
                    ("M", "MEMBRO DO MINIST\xc9RIO P\xdaBLICO"),
                    ("P", "MILITAR"),
                    ("S", "SERVIDOR"),
                    ("T", "TERCEIRIZADO"),
                    ("V", "VOLUNT\xc1RIO"),
                ],
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="child_of",
            field=models.ForeignKey(
                related_name="history_father_of",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Derivada de",
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="created_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="created_by_departure",
            field=models.ForeignKey(
                related_name="history_employee_workplace_created",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="afastamento.BaseLicencaAfastamento",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="employee_workplace",
            field=models.ForeignKey(
                related_name="history_servidor_lotacao",
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="lotacao",
            field=models.ForeignKey(
                related_name="history_servidores_lotacao",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Lota\xe7\xe3o/Designa\xe7\xe3o",
                to="rh.Lotacao",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="modified_by",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="movimentacao_posse",
            field=models.ForeignKey(
                related_name="history_lotacoes",
                on_delete=django.db.models.deletion.PROTECT,
                to="rh.MovimentacaoPosse",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="publicacao",
            field=models.ForeignKey(
                blank=True, to="rh.Publicacao", null=True, on_delete=models.CASCADE
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="employeeworkplacehistory",
            name="servidor",
            field=models.ForeignKey(
                related_name="history_servidor_lotacao",
                verbose_name="Servidor",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
