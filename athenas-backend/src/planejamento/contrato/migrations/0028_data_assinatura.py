from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0027__unit_measure_obrigatorio"),
    ]

    operations = [
        migrations.AddField(
            model_name="valorcontrato",
            name="data_assinatura",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data da Assinatura"
            ),
        ),
    ]
