from django.db import migrations, models


def up_fix_officer_diligence_removed(apps, schema):
    OfficerDiligence = apps.get_model("judicial", "OfficerDiligence")
    query = OfficerDiligence.objects.all()

    for officer in query:
        if officer.status != 1:
            OfficerDiligence.objects.filter(pk=officer.pk).update(is_removed=True)


def down_fix_officer_diligence_removed(apps, schema):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0092_fix_movementlog_triage"),
    ]

    operations = [
        migrations.AddField(
            model_name="officerdiligence",
            name="is_removed",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            up_fix_officer_diligence_removed, down_fix_officer_diligence_removed
        ),
    ]
