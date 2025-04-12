# -*- coding: utf-8 -*-
import os
import django
import json

from subprocess import call, Popen, PIPE
from functools import partial
from celery import Celery, group
from django.conf import settings
from contrib.utils import getLogger
from contrib.middleware import set_current_user, get_current_user
from datetime import datetime
from judicial.models import (
    Attached,
    PartLawsuit,
    ExecutionOrgan,
    Pouch,
    PouchLawsuit,
    OutCourtLawsuit,
    Manifestation,
    DeliveryAttemptLegalSign,
    DeliveryAttempt,
    Recomendation,
    EventControl,
)
from rh.models import Localidade
from django.contrib.auth.models import User
from ged.models import Arquivo as GedFile

log = getLogger("tasker")

app = Celery("report")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))

# django.setup()


@app.task()
def migrate_sign_attempt(pk, user):
    set_current_user(user)

    attempt = DeliveryAttempt.objects.get(pk=pk)
    DeliveryAttempt.objects.filter(pk=attempt.pk).update(
        signed_by=get_current_user(), signed_at=datetime.now(), is_signed_by_system=True
    )

    attempt.refresh_from_db()
    DeliveryAttemptLegalSign.sign(attempt)

    DeliveryAttempt.objects.filter(pk=attempt.pk).update(
        cache_rendered=attempt.rendered
    )

    return None


@app.task()
def open_lawsuit_per_month(year, month):
    my_group = group(
        [
            open_lawsuit_execuiton_organ_per_month.s(organ.pk, year, month)
            for organ in ExecutionOrgan.objects.filter()
        ]
    )

    promise = my_group()
    for pk, total in [a for a in promise.get() if a[1]]:
        print("%d;%s;%d" % (pk, ExecutionOrgan.objects.get(pk=pk), total))


@app.task()
def open_lawsuit_execuiton_organ_per_month(organ, year, month):
    q = PartLawsuit.objects.filter(
        create_location__id=organ, signed_at__year=year, signed_at__month=month
    ).filter(
        type_part__in=(
            "denunciation",
            "assessmentnoticeoffice",
            "ordinace",
            "ordinacereformulated",
        )
    )

    return (organ, q.count())


@app.task()
def process_attached_document(pk):
    attached = Attached.objects.get(pk=pk)
    attached.process_renderer_pages()


@app.task()
def process_renderer_pages_of_protable_document_executor(
    filebase, dest, start_page, end_page
):
    cmd = [
        '"/usr/bin/convert"',
        "-background",
        "white",
        "-alpha",
        "remove",
        "-limit",
        "memory",
        "%s" % (getattr(settings, "JUDICIAL_CONVERT_LIMIT_MEMORY")),
        "-limit",
        "map",
        "%s" % (getattr(settings, "JUDICIAL_CONVERT_LIMIT_MAP")),
        '"-density"',
        '"%s"' % (getattr(settings, "JUDICIAL_CONVERT_DENSITY")),
        '"-quality"',
        '"%s"' % (getattr(settings, "JUDICIAL_CONVERT_QUALITY")),
        '"%s[%d-%d]"' % (filebase, start_page, end_page - 1),
        '"-resize"',
        '"794"',
        '"%s"' % dest,
    ]

    log.info(" ".join(cmd))
    pid_fd = Popen(" ".join(cmd), shell=True, stdout=PIPE, stderr=PIPE)
    pid_fd.wait()

    log.info("Return code %d", pid_fd.returncode)
    if pid_fd.returncode != 0:
        for chunk in iter(partial(pid_fd.stderr.read, 8192), b""):
            try:
                log.error(chunk)
            except Exception:
                log.error("Error processing %s", filebase)
    else:
        hash_content = os.path.basename(filebase)
        gedfile = GedFile.objects.get(file=hash_content)

        fix_rendered_documents(gedfile)
        fix_rendered_diligences(gedfile)


def fix_rendered_diligences(gedfile):
    query = Attached.objects.filter(file_descriptor=gedfile).exclude(
        attached_diligence__judicialdiligence__part__signed_by=None
    )

    if query.exists():
        for attached in query:
            set_current_user(attached.modified_by)
            _fix_rendered_document(attached.diligence.judicialdiligence.part)


def fix_rendered_documents(gedfile):
    query = Attached.objects.filter(file_descriptor=gedfile).exclude(
        attached_document__signed_by=None
    )

    if query.exists():
        for attached in query:
            set_current_user(attached.modified_by)
            _fix_rendered_document(attached.attached_document)


def _fix_rendered_document(document):
    log.info(
        "Atualizando cache do evento %(evento)d do procedimento %(procedimento)s",
        {
            "evento": EventControl.number_control_of(document.lawsuit, document),
            "procedimento": document.lawsuit.cache_number,
        },
    )

    document.create_cache_document(force=True)


@app.task()
def delivery_pouch(pouch_id, by_user_id):
    pouch = Pouch.objects.get(pk=pouch_id)

    tasks = group(
        [
            delivery_pouch_item.s(item.id, by_user_id)
            for item in pouch.items.filter(movement_part=None)
        ]
    )

    tasks.apply_async()


@app.task()
def delivery_pouch_item(pouch_item_id, by_user_id):
    set_current_user(User.objects.get(pk=by_user_id))
    PouchLawsuit.objects.get(pk=pouch_item_id).delivery()


@app.task()
def decrement_remaining_days(dry_run, location_id, to_date):
    try:
        # a data vem no formato iso, converte para formato compativel pra busca no queryset
        to_date = datetime.strptime(to_date, "%Y-%m-%dT%H:%M:%S").date()

        query_lawsuit = []
        query_manifestation = []
        query_recomendation = []
        location = Localidade.objects.get(pk=location_id)

        if to_date.isoweekday() in [6, 7]:

            query_lawsuit = OutCourtLawsuit.queryset_lawsuit_to_weekend_decrement_day(
                location=location, to_date=to_date
            )

            query_manifestation = (
                Manifestation.queryset_manifestation_to_weekend_decrement_day(
                    location=location, to_date=to_date
                )
            )

            query_recomendation = (
                Recomendation.queryset_recomendation_to_weekend_decrement_day(
                    location=location, to_date=to_date
                )
            )
        else:

            query_lawsuit = OutCourtLawsuit.queryset_lawsuit_to_decrement_day(
                location=location, to_date=to_date
            )

            query_manifestation = Manifestation.queryset_manifestation_to_decrement_day(
                location=location, to_date=to_date
            )

            query_recomendation = Recomendation.queryset_recomendation_to_decrement_day(
                location=location, to_date=to_date
            )

        log.info("Data: %s -> Modo simulado: %s" % (to_date, dry_run))
        log.info(
            "Cidade %s -> Qtd de procedimentos %s " % (location, query_lawsuit.count())
        )
        log.info(
            "Cidade %s -> Qtd de Manifestacoes %s "
            % (location, query_manifestation.count())
        )
        log.info(
            "Cidade %s -> Qtd de Recomendacoes %s "
            % (location, query_recomendation.count())
        )

    except Exception as e:
        log.info("Ocorreu um problema: %s " % e)
        raise e

    else:
        OutCourtLawsuit.decrement_remaining_days(
            query_set=query_lawsuit, dry_run=dry_run
        )
        Manifestation.decrement_remaining_days(
            query_set=query_manifestation, dry_run=dry_run
        )
        Recomendation.decrement_remaining_days(
            query_set=query_recomendation, dry_run=dry_run
        )
