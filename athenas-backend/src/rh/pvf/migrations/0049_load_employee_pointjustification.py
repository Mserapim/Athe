from django.db import migrations


def forward(apps, schema_editor):
    PointJustification = apps.get_model("pvf", "PointJustification")

    queryset = PointJustification.objects.filter(employee__isnull=True).exclude(
        request__isnull=True
    )

    for justification in queryset:
        justification.employee_id = justification.request.employee_id
        justification.save()


def backward(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("pvf", "0048_marktelework_saldo_devedor_anterior"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
