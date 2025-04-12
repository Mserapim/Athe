from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0029_valorcontrato_novoscampos"),
    ]

    operations = [
        migrations.AddField(
            model_name="minutesolicitation",
            name="sei_number",
            field=models.TextField(blank=True, null=True, verbose_name="Número SEI"),
        ),
    ]
