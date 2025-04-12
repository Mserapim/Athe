from django.db import migrations
from contrib.middleware import set_current_user
from django.db.models import F
from rh.models import MetaTeletrabalho


def forward(*args, **kwargs):
    set_current_user("athenas")
    metas = MetaTeletrabalho.objects.filter(
        mov_teletrabalho__data_fim__lt=F("data_fim")
    )
    for meta in metas:
        dt_fim_teletrabalho = meta.mov_teletrabalho.data_fim
        MetaTeletrabalho.objects.filter(pk=meta.pk).update(data_fim=dt_fim_teletrabalho)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0327_povoar_possui_saldo_devedor"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
