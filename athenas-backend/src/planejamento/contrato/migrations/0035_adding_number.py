from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0034_criando_ride"),
    ]

    operations = [
        migrations.AddField(
            model_name="ride",
            name="number",
            field=models.CharField(
                max_length=100, verbose_name="Número da Carona", blank=True, null=True
            ),
        ),
    ]
