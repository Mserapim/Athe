import sys
from django.db import migrations, models
from judicial.models import (
    OutCourtLawsuit,
    MovementLog,
    Triage,
    TriagePart,
    OutCourtLawsuitLog,
)
from rh.models import OrgaoGeral
from dateutil.relativedelta import relativedelta


def _print(message):
    sys.stdout.write(message)
    sys.stdout.flush()


def fix_movement(lawsuit, triage, cartorio):
    next_part = (
        lawsuit.all_signed_documents.exclude(signed_at__lte=triage.signed_at)
        .order_by("signed_at")
        .first()
    )

    if next_part:
        try:
            obj, created = MovementLog.objects.get_or_create(
                out_court_lawsuit_id=lawsuit.pk,
                from_location_id=cartorio.pk,
                to_location_id=next_part.create_location.pk,
                defaults={
                    "sended_by_id": triage.effected_by.pk,
                    "sended_at": triage.effected_at,
                },
            )
        except Exception as e:
            print("ERRO ? ", lawsuit, flush=True)

        triage_part = triage.parts.filter(distributed_id=next_part.create_location.pk)
        if triage_part:
            triage_part.update(lawsuit_id=lawsuit.pk)

    else:
        triage_part = triage.parts.order_by("id").first()
        query = TriagePart.objects.filter(pk=triage_part.pk)
        if query:
            query.update(lawsuit_id=lawsuit.pk)


def up_fix_movement_log_of_triage(apps, schema):
    print("##############INICIO UPDATE fix MovementLog ################")

    query = Triage.objects.exclude(parts=None).filter(
        signed_at__isnull=False, parts__lawsuit_id=None
    )
    cartorio = OrgaoGeral.objects.get(pk=248)

    for triage in query.order_by("id"):
        if triage.parts.count() > 1:
            for lawsuit in triage.shared_with_lawsuit.all():
                fix_movement(lawsuit, triage, cartorio)
        elif triage.parts.count() == 1:
            fix_movement(triage.lawsuit, triage, cartorio)
        else:
            _print("#### ERRO na quantidade de triageparts")


def fix_main_tag_movement(apps, schema):
    print("##############INICIO UPDATE main_tag IN MovementLog ################")

    delta = relativedelta(seconds=5)
    for m in MovementLog.objects.filter(main_tag__isnull=True):
        dt_ini = m.sended_at - delta
        dt_fim = m.sended_at + delta
        parts = m.out_court_lawsuit.all_signed_documents.filter(
            signed_at__range=(dt_ini, dt_fim)
        )
        if parts:
            logs = OutCourtLawsuitLog.objects.filter(part=parts.first())
            if logs:
                log = logs.first()
                MovementLog.objects.filter(pk=m.pk).update(main_tag=log.main_tag)


def up_fix_log_main_matter(apps, schema):
    print("##############INICIO UPDATE main_matter IN MovementLog ################")

    query = Triage.objects.exclude(parts=None).filter(signed_at__isnull=False)

    for triage in query.order_by("id"):
        query_log = OutCourtLawsuitLog.objects.filter(lawsuit=triage.lawsuit).order_by(
            "id"
        )
        logs_ids = []
        for log in query_log:
            if not log.main_matter:
                logs_ids.append(log.pk)
            else:
                break

        OutCourtLawsuitLog.objects.filter(id__in=logs_ids).update(
            main_matter=triage.parts.first().matter
        )


def down_fix_movement_log_of_triage(apps, schema):
    pass


def down_fix_main_tag_movement(apps, schema):
    pass


def down_fix_log_main_matter(apps, schema):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0091_add_lawsuit_in_triagepart"),
    ]

    operations = [
        migrations.RunPython(
            up_fix_movement_log_of_triage, down_fix_movement_log_of_triage
        ),
        migrations.RunPython(fix_main_tag_movement, down_fix_main_tag_movement),
        migrations.RunPython(up_fix_log_main_matter, down_fix_log_main_matter),
    ]
