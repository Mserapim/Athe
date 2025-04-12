from django.db import migrations, models

from rh.models import MovimentacaoSubstituicao, ConfigPeriodoCumulativoSubstituicao


def forward(*args, **kwargs):
    periodo = ConfigPeriodoCumulativoSubstituicao.objects.order_by(
        "data_inicio_periodo", "data_fim_periodo"
    ).first()
    pagos_ids = []
    for mov in MovimentacaoSubstituicao.objects.filter():
        if mov.substitutions_consolidated.exists():
            if mov.substitutions_consolidated.first().gcpp:
                if mov.substitutions_consolidated.first().gcpp.status == "pago":
                    pagos_ids.append(mov.pk)

    MovimentacaoSubstituicao.objects.filter(pk__in=pagos_ids).update(
        periodo_cumul_subs=periodo
    )


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0300_movimentacaosubstituicao_periodo_cumul_subs"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
