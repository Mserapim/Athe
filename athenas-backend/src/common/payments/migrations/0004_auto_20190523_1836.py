# -*- coding: utf-8 -*-

from django.db import migrations, models, transaction


def forwards_data_migration(apps, schema_editor):
    Partnership = apps.get_model("payments.BankPartnership")
    TicketPay = apps.get_model("payments.TicketPay")

    with transaction.atomic():
        partner, created = Partnership.objects.get_or_create(
            identifier="EXTERNAL_PAYMENT",
            partnertship_code="319796",
            charge_code="3128940",
        )
        TicketPay.objects.all().update(partnership=partner)


def reverse_data_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0003_ticketpay_process_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="BankPartnership",
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
                    "identifier",
                    models.CharField(
                        default="INTERNAL_PAYMENT",
                        max_length=100,
                        verbose_name="Identificador de Tipo",
                    ),
                ),
                (
                    "charge_code",
                    models.CharField(
                        default="3179485",
                        max_length=7,
                        verbose_name="C\xc3\xb3digo de Cobran\xc3\xa7a",
                    ),
                ),
                (
                    "partnertship_code",
                    models.CharField(
                        default="319796",
                        max_length=6,
                        verbose_name="C\xc3\xb3digo de Conv\xc3\xaanio de Com. Eletr\xc3\xb4nico",
                    ),
                ),
                (
                    "callback_url",
                    models.CharField(
                        default="https://athenas.mpto.mp.br/athenas/",
                        max_length=256,
                        verbose_name="Url de Retorno",
                    ),
                ),
                (
                    "days_remaining",
                    models.CharField(
                        default="10",
                        max_length=3,
                        verbose_name="Dias para o vencimento",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tipo de Boleto",
                "verbose_name_plural": "Tipos de Boletos",
            },
        ),
        migrations.RemoveField(
            model_name="ticketpay",
            name="callback_url",
        ),
        migrations.RemoveField(
            model_name="ticketpay",
            name="company_code",
        ),
        migrations.AddField(
            model_name="ticketpay",
            name="partnership",
            field=models.ForeignKey(
                related_name="tickets",
                null=True,
                to="payments.BankPartnership",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
            preserve_default=False,
        ),
        migrations.RunPython(forwards_data_migration, reverse_data_migration),
    ]
