from django.db import migrations
from contrib.middleware import set_current_user
from rh.models import MovimentacaoTeletrabalho
from rh.pvf.models import SendingTelework, MarkTelework


def forward(*args, **kwargs):
    set_current_user("athenas")

    movimentacoes = MovimentacaoTeletrabalho.objects.all()

    for movimentacao in movimentacoes:
        # Pegar o último SendingTelework da Movimentacao
        ultimo_envio = (
            SendingTelework.objects.filter(
                work_plan=movimentacao,
                status=4,  # Efetivado
                cancelado_solicitacao=False,
            )
            .order_by("-id")
            .first()
        )

        if not ultimo_envio:
            continue

        # Verificar MarkTelework relacionado ao ultimo envio
        has_saldo_devedor = MarkTelework.objects.filter(
            request=ultimo_envio, saldo_devedor__gt=0
        ).exists()

        # Atualizar possui_saldo_devedor
        MovimentacaoTeletrabalho.objects.filter(pk=movimentacao.pk).update(
            possui_saldo_devedor=has_saldo_devedor
        )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0326_auto_20241211_1713"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
