# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def create_convenants(apps, schema_editor):
    Banco = apps.get_model("rh", "Banco")
    BankingConvenant = apps.get_model("gfp", "BankingConvenant")

    createds = 0
    for b in Banco.objects.filter(tem_convenio__in=[1, 2]).exclude(
        numero_convenio__isnull=True
    ):
        try:
            ups, created = BankingConvenant.objects.get_or_create(
                convenant=b.numero_convenio,
                bank=b,
                defaults={
                    "identification": "CONVÊNIO %s - %s"
                    % (b.sigla if b.sigla else str(b), b.numero_convenio),
                    "counter": b.sequencial_arquivo,
                    "type_convenant": b.tem_convenio,
                    "agency_cod": b.agencia,
                    "agency_cod_dv": b.dv_agencia,
                    "account_cod": b.conta,
                    "account_cod_dv": b.dv_conta,
                },
            )
            if created:
                createds += 1
        except Exception as e:
            pass
    if createds:
        print("")
        print(">>ATENCAO<<")
        print(
            ">> Necessita configurar os convenios bancarios migrados (FOLHA PAGAMENTO >> Parametros >> Convênios Bancarios)"
        )
        print(
            ">> Identificador: Colocar um texto que identifique o convenio. EX.: BB FEBRABAN 240"
        )
        print(">> Ativo?: Se o convênio não for mais utilizado desmarcar esse campo")
        print(
            ">> Caso não seja configurado os arquivos de crédito não poderão ser gerados"
        )
        print("")


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0005_auto_20170406_1512"),
        ("gfp", "0045_evento_consignment_manager"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankingConvenant",
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
                    "identification",
                    models.CharField(
                        default="",
                        max_length=64,
                        verbose_name="Identificador",
                        db_index=True,
                    ),
                ),
                (
                    "convenant",
                    models.CharField(
                        max_length=64, verbose_name="Conv\xeanio", db_index=True
                    ),
                ),
                (
                    "counter",
                    models.PositiveIntegerField(
                        default=1, verbose_name="Contador", blank=True
                    ),
                ),
                ("active", models.BooleanField(default=True, verbose_name="Ativo?")),
                (
                    "type_convenant",
                    models.PositiveSmallIntegerField(
                        default=2,
                        verbose_name="Tipo Con\xeanio",
                        choices=[
                            (1, "Exclusivo para clientes do banco"),
                            (2, "Servidores de outros bancos via TED/DOC"),
                        ],
                    ),
                ),
                (
                    "agency_cod",
                    models.CharField(max_length=4, verbose_name="Ag\xeancia"),
                ),
                (
                    "agency_cod_dv",
                    models.CharField(max_length=2, verbose_name="Ag\xeancia/DV"),
                ),
                ("account_cod", models.CharField(max_length=20, verbose_name="Conta")),
                (
                    "account_cod_dv",
                    models.CharField(max_length=1, verbose_name="Conta/DV"),
                ),
                (
                    "bank",
                    models.ForeignKey(
                        verbose_name="Banco", to="rh.Banco", on_delete=models.CASCADE
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                (
                    "generator",
                    models.ForeignKey(
                        related_name="banking_conventants",
                        on_delete=django.db.models.deletion.SET_NULL,
                        verbose_name="Gerador",
                        blank=True,
                        to="standard.ClassCode",
                        null=True,
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_convenants, _null_function),
    ]
