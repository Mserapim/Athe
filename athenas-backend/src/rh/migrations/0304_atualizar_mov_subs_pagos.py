from django.db import migrations, models

from rh.models import MovimentacaoSubstituicao


def forward(*args, **kwargs):
    for mov in MovimentacaoSubstituicao.objects.filter(paid_out=False):
        if (
            mov.substitutions_consolidated.exists()
            and mov.substitutions_consolidated.first().gcpp
            and mov.substitutions_consolidated.first().gcpp.status == "pago"
        ):
            MovimentacaoSubstituicao.objects.filter(pk=mov.pk).update(paid_out=True)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0303_merge_20240426_1111"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
