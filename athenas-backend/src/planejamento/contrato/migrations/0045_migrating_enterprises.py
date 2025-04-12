from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

from rh.models import Pessoa, PessoaJuridica
from planejamento.contrato.models import Enterprise, Minute, MinuteSolicitation


def adding_all_enterprises(apps, schema_editor):
    for pj in PessoaJuridica.objects.filter():
        enterprise_counter = Enterprise.objects.filter(person=pj).count()
        if enterprise_counter == 0:
            Enterprise.objects.create(person=pj)

    for m in Minute.objects.filter():
        enterprise_counter = Enterprise.objects.filter(person=m.provider).count()
        if enterprise_counter == 1:
            m.enterprise_provider = Enterprise.objects.get(person=m.provider)
            m.save()


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0044_fixing_enterprise"),
    ]

    if settings.ORGAN_IDENTIFIER == "mpto":
        operations = [migrations.RunPython(adding_all_enterprises)]
