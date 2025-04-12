from django.db import migrations, models

from rh.models import MetaTeletrabalho


def forward(*args, **kwargs):
    MetaTeletrabalho.objects.filter(periodicity__isnull=True).update(periodicity=3)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0287_auto_20231108_1116"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
