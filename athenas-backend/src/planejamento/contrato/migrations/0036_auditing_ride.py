from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from standard.models import Choice


def adding_engaged(apps, schema_editor):
    # Adicionar 7=engaged -> Contratado
    Choice.objects.create(
        app_label="contrato",
        name="MINUTE_SOLICITATION_SITUATION",
        cvalue=7,
        label="Contratado",
    )
    # Adicionar 7=Contratar
    Choice.objects.create(
        app_label="contrato",
        name="MINUTE_SOLICITATION_ACTION",
        cvalue=7,
        label="Contratar",
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contrato", "0035_adding_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="ride",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ride",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                default=845,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="ride",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="ride",
            name="modified_by",
            field=models.ForeignKey(
                blank=True,
                default=845,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(adding_engaged),
    ]
