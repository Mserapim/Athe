from django.db import migrations, models
from standard.models import Choice


def adding_motives(apps, schema_editor):
    Choice.objects.create(
        app_label="contrato", name="MOTIVO_ESTRUTURA", cvalue=1, label="Empresa pública"
    )
    Choice.objects.create(
        app_label="contrato",
        name="MOTIVO_ESTRUTURA",
        cvalue=2,
        label="Sem quadro societário",
    )
    Choice.objects.create(
        app_label="contrato", name="MOTIVO_ESTRUTURA", cvalue=3, label="Não se aplica"
    )
    Choice.objects.create(
        app_label="contrato",
        name="MOTIVO_ESTRUTURA",
        cvalue=4,
        label="Informação Indisponível",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0047_deleting_enterprise_structure"),
    ]

    operations = [
        migrations.RunPython(adding_motives),
        migrations.AddField(
            model_name="enterprise",
            name="apply",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="enterprise",
            name="motive",
            field=models.SmallIntegerField(
                choices=[
                    (1, "Empresa pública"),
                    (2, "Sem quadro societário"),
                    (3, "Não se aplica"),
                    (4, "Informação Indisponível"),
                ],
                default=4,
            ),
        ),
    ]
