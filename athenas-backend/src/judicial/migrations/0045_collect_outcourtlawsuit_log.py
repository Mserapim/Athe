# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import sys, os

from django.db import migrations, models
from contrib.utils import getLogger

logger = getLogger("migrations")


def log(message, rollback=True, rollback_char="\b"):
    print(message, end="")

    if rollback:
        print(rollback_char * len(message), end="")

    sys.stdout.flush()


def up_collect(apps, schema_editor):
    from judicial.models import (
        OutCourtLawsuit,
        OutCourtLawsuitLog,
        AssessmentNoticeOffice,
        Denunciation,
        Ordinace,
        OrdinaceReformulated,
    )

    query = OutCourtLawsuit.objects.exclude(cache_number="--").order_by("pk")

    if "M_SIZE" in os.environ:
        query = query[: int(os.environ.get("M_SIZE", "200"))]

    total = query.count()
    pos = 0
    warn_count = 0
    err_count = 0

    log(" ", False)
    logger.info("--- BEGIN migrate 0042 ---")
    for lawsuit in query:
        pos += 1
        log(
            "analizando %d de %d (warn: %d, err: %d)"
            % (pos, total, warn_count, err_count)
        )

        type_lawsuit = 6
        deadline_days = 7
        last_signed_data = None

        for part in lawsuit.all_signed_documents.order_by("signed_at"):
            part = part.my_origin

            if isinstance(part, Denunciation):
                deadline_days = 30
                type_lawsuit = 1
            elif isinstance(part, AssessmentNoticeOffice):
                deadline_days = 30 if part.notice_office_type in (1, 2) else None
                if part.notice_office_type in (1, 2):
                    type_lawsuit = 1
                elif part.notice_office_type == 3:
                    type_lawsuit = 8
            elif isinstance(part, (Ordinace, OrdinaceReformulated)):
                deadline_days = ({2: 365, 3: 90, 4: 90, 7: 365}).get(
                    part.type_ordinace, None
                )
                type_lawsuit = part.type_ordinace
            else:
                try:
                    if deadline_days and last_signed_data:
                        deadline_days = (
                            deadline_days - (part.signed_at - last_signed_data).days
                        )
                    elif deadline_days:
                        deadline_days = (
                            deadline_days
                            - (part.signed_at - lawsuit.origin.created_at).days
                        )
                except Exception as e:
                    warn_count += 1
                    deadline_days = None
                    logger.warning(
                        "%s (%s) [%d] {%s}",
                        lawsuit.cache_number,
                        part.codename,
                        part.pk,
                        last_signed_data,
                    )
                    logger.exception(e)

            if deadline_days:
                deadline_days = 0 if deadline_days < 0 else deadline_days

            try:
                OutCourtLawsuitLog(
                    lawsuit=lawsuit,
                    type_lawsuit=type_lawsuit,
                    part=part,
                    location=part.create_location,
                    deadline_days=deadline_days,
                    initiator_at=(
                        part.signed_at if part.my_origin.is_initiator else None
                    ),
                ).save()
            except:
                err_count += 1
                logger.error(
                    "%s (%s) [%d] {%s}",
                    lawsuit.cache_number,
                    part.codename,
                    part.pk,
                    last_signed_data,
                )

            last_signed_data = part.signed_at

    logger.info("--- END migrate 0042 ---")
    log(
        "analizando %d de %d (warn: %d, err: %d)" % (pos, total, warn_count, err_count),
        rollback_char=" ",
    )
    log(" ", rollback_char=" ")


def down_collect(apps, schema_editor):
    OutCourtLawsuitLog = apps.get_model("judicial.OutCourtLawsuitLog")
    OutCourtLawsuitLog.objects.filter().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0044_auto_20180419_1511"),
    ]

    operations = [migrations.RunPython(up_collect, down_collect)]
