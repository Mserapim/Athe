# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TicketPay",
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
                ("name", models.CharField(max_length=60, verbose_name="Nome")),
                ("cpf_cnpj", models.CharField(max_length=14, verbose_name="CPF/Cnpj")),
                ("city", models.CharField(max_length=18, verbose_name="Cidade")),
                ("state", models.CharField(max_length=2, verbose_name="UF")),
                ("zip_code", models.CharField(max_length=8, verbose_name="CEP")),
                (
                    "message_store",
                    models.CharField(max_length=1082, verbose_name="Mensagem"),
                ),
                (
                    "address",
                    models.CharField(max_length=60, verbose_name="Endere\xc3\xa7o"),
                ),
                (
                    "value",
                    models.DecimalField(
                        verbose_name="Valor", max_digits=15, decimal_places=2
                    ),
                ),
                (
                    "company_code",
                    models.CharField(
                        default="319796",
                        max_length=6,
                        verbose_name="C\xc3\xb3digo de Conv\xc3\xaanio",
                    ),
                ),
                ("control", models.CharField(max_length=10, verbose_name="Controle")),
                (
                    "ticket_number",
                    models.CharField(
                        max_length=17, verbose_name="N\xc3\xbamero do Boleto"
                    ),
                ),
                (
                    "expiration_date",
                    models.DateField(verbose_name="Data de Vencimento"),
                ),
                (
                    "callback_url",
                    models.CharField(
                        default="/portal/servicos/boleto/",
                        max_length=60,
                        verbose_name="URL de Retorno",
                    ),
                ),
                (
                    "person_type",
                    models.CharField(
                        default="1", max_length=1, verbose_name="Tipo de Pessoa"
                    ),
                ),
                (
                    "payment_type",
                    models.CharField(
                        default="2", max_length=2, verbose_name="Tipo de Pagamento"
                    ),
                ),
                (
                    "document_type",
                    models.CharField(
                        default="DS", max_length=2, verbose_name="Tipo de Duplicata"
                    ),
                ),
            ],
            options={
                "verbose_name": "Boleto",
                "verbose_name_plural": "Boletos",
            },
        ),
    ]
