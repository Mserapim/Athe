from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0030_campo_sei"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="minutesolicitation",
            name="sei_number",
        ),
    ]
