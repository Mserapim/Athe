from django.db import migrations, models
import django.db.models.deletion
from standard.models import Choice


def adding_months(apps, schema_editor):
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=1, label="Janeiro"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=2, label="Fevereiro"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=3, label="Março"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=4, label="Abril"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=5, label="Maio"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=6, label="Junho"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=7, label="Julho"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=8, label="Agosto"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=9, label="Setembro"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=10, label="Outubro"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=11, label="Novembro"
    )
    Choice.objects.create(
        app_label="contrato", name="MES_REAJUSTE", cvalue=12, label="Dezembro"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("contrato", "0040_updating_agreement_fields"),
    ]
    operations = [
        migrations.RunPython(adding_months),
        migrations.AlterField(
            model_name="contrato",
            name="reference_month",
            field=models.IntegerField(choices=[(1, "Pipoca")], blank=True, null=True),
        ),
    ]
