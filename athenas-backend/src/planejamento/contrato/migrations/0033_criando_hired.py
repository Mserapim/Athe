from django.db import migrations, models
from planejamento.contrato.models import Contrato
from rh.models import Pessoa


def migrating_hired_person(apps, schema_editor):
    from planejamento.contrato.models import Hired

    for c in Contrato.objects.all():
        hired = Hired(agreement=c, person=c.pessoa.last(), start_date=c.data_inicio)
        hired.save()


class Migration(migrations.Migration):

    dependencies = [("contrato", "0032_auto_20201117_1652")]

    operations = [
        migrations.CreateModel(
            name="Hired",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "agreement",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to="contrato.contrato",
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.CASCADE, to="rh.Pessoa", blank=True, null=True
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.RunPython(migrating_hired_person),
    ]
