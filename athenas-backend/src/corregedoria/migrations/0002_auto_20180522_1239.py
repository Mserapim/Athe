# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import standard.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("raf", "0025_auto_20180519_0246"),
        ("corregedoria", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConfigLinkInspectionRAF",
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
                    "inspection_table",
                    models.IntegerField(
                        verbose_name="Tabela de Inspection",
                        choices=[
                            (1, "Atendimento ao P\xfablico"),
                            (2, "Processos Judiciais Recebidos"),
                            (3, "Processos Judiciais Devolvidos"),
                            (4, "Processos Eleitorais Recebidos"),
                            (5, "Processos Eleitorais Devolvidos"),
                        ],
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
                (
                    "raf_item",
                    models.ForeignKey(
                        related_name="+",
                        blank=True,
                        to="raf.Item",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "raf_subitem",
                    models.ForeignKey(
                        related_name="+", to="raf.SubItem", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={
                "ordering": ["inspection_table"],
                "verbose_name": "V\xednculo para aferi\xe7\xe3o de dados do RAF em Inspection",
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
        migrations.AlterField(
            model_name="configproductivity",
            name="score_table",
            field=models.IntegerField(
                verbose_name="Tabela de C\xe1lculo",
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
            model_name="configscoretable",
            name="score_table",
            field=models.IntegerField(
                verbose_name="Tabela de C\xe1lculo",
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
    ]
