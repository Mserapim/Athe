from django.db import migrations
from contrib.middleware import set_current_user
from rh.models import Servidor, ServidorLotacao


def forward(*args, **kwargs):
    set_current_user("athenas")

    servidor_q = (
        Servidor.objects.filter(
            ativo=False,
            servidor_lotacao__ativo=True,
        )
        .order_by("type_by_possession")
        .distinct()
    )

    for servidor in servidor_q:
        data_desligamento = servidor.data_desligamento
        if data_desligamento:
            ServidorLotacao.objects.filter(
                servidor=servidor,
                ativo=True,
            ).update(ativo=False, data_vigencia_fim=data_desligamento)
        else:
            ServidorLotacao.objects.filter(
                servidor=servidor,
                ativo=True,
            ).update(ativo=False, data_vigencia_fim=servidor.created_at)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0331_atualizar_lotacoes_designacoes_inconsistentes"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
