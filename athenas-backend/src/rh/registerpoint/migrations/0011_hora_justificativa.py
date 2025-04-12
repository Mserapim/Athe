from django.db import migrations
from django.conf import settings

from rh.registerpoint.utils.ponto import carga_horaria_diaria


def forward(apps, schema_editor):
    from datetime import timedelta

    PointJustification = apps.get_model("pvf", "PointJustification")
    CargaHoraria = apps.get_model("rh", "CargaHoraria")
    JustificationItem = apps.get_model("standard", "JustificationItem")

    justificativas = (
        PointJustification.objects.filter(number_hours="00:00", start_date__year=2025)
        .exclude(employee__tipo="M")
        .select_related("employee")
    )

    total = justificativas.count()
    print(f"Processando {total} registros...")

    updates = []

    for justificativa in justificativas:
        servidor_id = justificativa.employee_id
        dia = justificativa.start_date

        jornadas_trabalho = CargaHoraria.objects.filter(
            servidor_id=servidor_id,
            data_inicio__lte=dia,
            jornada_trabalho__isnull=False,
        ).order_by("-data_inicio")

        if not jornadas_trabalho.exists():
            continue

        try:
            ch_dia = carga_horaria_diaria(jornadas_trabalho, dia)
        except Exception as e:
            continue

        motivo = JustificationItem.objects.filter(id=justificativa.reason_type).first()
        if not motivo:
            continue

        max_value = motivo.max_value

        if max_value is not None:
            novo_valor = min(max_value, ch_dia)
        else:
            novo_valor = ch_dia

        horas = novo_valor // 60
        minutos = novo_valor % 60
        novo_number_hours = f"{horas:02}:{minutos:02}"

        updates.append((justificativa.id, novo_number_hours))

    for justificativa_id, novo_number_hours in updates:
        PointJustification.objects.filter(id=justificativa_id).update(
            number_hours=novo_number_hours
        )

    print(f"✅ Atualização concluída para {len(updates)} registros.")


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("registerpoint", "0010_auto_20240911_1000"),
    ]

    operations = [migrations.RunPython(forward, backward)]
