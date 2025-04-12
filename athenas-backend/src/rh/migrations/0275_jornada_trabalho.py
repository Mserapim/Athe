from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0274_merge_20231003_1508"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargahoraria",
            name="jornada_trabalho",
            field=models.ForeignKey(
                "HoursWorkContract",
                null=True,
                blank=True,
                verbose_name="Jornada de Trabalho",
                on_delete=models.SET_NULL,
            ),
        ),
    ]
