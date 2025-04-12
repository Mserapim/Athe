from django.db import migrations, models


def update_unitary_measure(apps, schema_editor):
    # Mozart 25 de março de 2020 13:41
    MinuteItem = apps.get_model("contrato.MinuteItem")
    MinuteItem.objects.filter(unit_measure=None).update(unit_measure=61)


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0025_adequando_campos_contrato"),
    ]

    operations = [
        migrations.RunPython(update_unitary_measure),
    ]
