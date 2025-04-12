from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0028_data_assinatura"),
    ]

    operations = [
        migrations.AddField(
            model_name="valorcontrato",
            name="objeto",
            field=models.TextField(blank=True, null=True, verbose_name="Objeto"),
        ),
        migrations.AddField(
            model_name="valorcontrato",
            name="permite_reajuste",
            field=models.BooleanField(verbose_name="Gera contrato?", default=False),
        ),
        migrations.AddField(
            model_name="valorcontrato",
            name="data_reajuste",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data do Reajuste"
            ),
        ),
        migrations.AddField(
            model_name="valorcontrato",
            name="valor_reajuste",
            field=models.DecimalField(
                verbose_name="Valor do Reajuste",
                max_digits=18,
                decimal_places=2,
                blank=True,
                null=True,
            ),
        ),
    ]
