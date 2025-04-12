from django.db import migrations, models
import django.db.models.deletion
from planejamento.contrato.models import CorporateStructure


def deleting_corporate_structure(apps, schema_editor):
    CorporateStructure.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0046_alter_enterprise_provider"),
    ]

    operations = [migrations.RunPython(deleting_corporate_structure)]
