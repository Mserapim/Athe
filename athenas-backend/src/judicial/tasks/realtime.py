# -*- coding: utf-8 -*-
import os
import json

from subprocess import call
from celery import Celery
from django.conf import settings
from django.db.models import Q
from contrib.utils import getLogger, employee_from_user
from datetime import datetime
from judicial.models import (
    PartLawsuit,
    OutCourtLawsuit,
    RequestCollaboration,
)
from django.contrib.auth.models import User
from default.websocket import RemoteEmmiter

log = getLogger("tasker")

app = Celery("report")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


def _lawsuit_from_user_and_part(user, part):
    employee = employee_from_user(user)
    workplaces_id = [l.pk for l in employee.work_locations.all()]

    lawsuit = None

    if not lawsuit:
        if (
            user.has_perm("judicial.outcourtlawsuitadmin")
            or part.lawsuit.location.pk in workplaces_id
        ):
            lawsuit = part.lawsuit

    if not lawsuit:
        query = part.shared_with_lawsuit.filter(location__id__in=workplaces_id)
        if query.exists():
            lawsuit = query.first()

    if not lawsuit:
        collabs = RequestCollaboration.objects.filter(
            lawsuit=part.lawsuit, canceled_by=None
        ).filter(
            Q(requestcollaborationperson__person=employee.pessoa_fisica)
            | Q(
                requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
            )
        )
        if collabs.exists():
            lawsuit = part.lawsuit

    if not lawsuit:
        if part.lawsuit.all_signed_documents.filter(
            diligences__responsible_delivering__officer_diligence=employee_from_user(
                user
            )
        ).exists():
            lawsuit = part.lawsuit

    if not lawsuit:
        raise Exception('O usuário "%s" não tem acesso ao documento.' % user.username)

    return lawsuit


@app.task
def create_cache_document(object_jwt, part_id, user_id):
    part = PartLawsuit.objects.get(pk=part_id)
    file_path = os.path.join(part.lawsuit.cache_dir, "%s" % (part.pk))
    file_lock = os.path.join(part.lawsuit.cache_dir, "%d.lock" % (part.pk))
    user = User.objects.get(id=user_id)

    lawsuit = _lawsuit_from_user_and_part(user, part)

    if not os.path.exists(part.lawsuit.cache_dir):
        os.makedirs(part.lawsuit.cache_dir)

    cmd = []
    cmd += settings.JUDICIAL_WKHTML_CMD
    cmd += settings.JUDICIAL_WKHTML_STATIC_PARAMS
    cmd += [
        "--custom-header",
        "Authorization",
        "JWT %s" % (object_jwt),
        "%s%s/?lawsuit=%d&part=%d&execution_organ=%d"
        % (
            settings.ATHENAS_INTERNAL,
            settings.JUDICIAL_URL_CACHE,
            lawsuit.pk,
            part.pk,
            part.lawsuit.location.pk,
        ),
        file_path,
    ]

    log.info("compiler command: %s", " ".join(cmd))
    call(cmd, shell=False)

    RemoteEmmiter.emmit_for_user(user, "judicial-load-cache-doc", part_id=part.pk)

    if os.path.exists(file_lock):
        os.remove(file_lock)


@app.task
def create_cache_lawsuit(object_jwt, lawsuit_id, user_id):
    lawsuit = OutCourtLawsuit.objects.get(pk=lawsuit_id)
    file_path = os.path.join(lawsuit.cache_dir, "full")
    file_lock = os.path.join(lawsuit.cache_dir, "full.lock")
    user = User.objects.get(id=user_id)

    if not os.path.exists(lawsuit.cache_dir):
        os.makedirs(lawsuit.cache_dir)

    cmd = []
    cmd += settings.JUDICIAL_WKHTML_CMD
    cmd += settings.JUDICIAL_WKHTML_STATIC_PARAMS
    cmd += [
        "--custom-header",
        "Authorization",
        "JWT %s" % (object_jwt),
        "%s%s/?lawsuit=%d&execution_organ=%d"
        % (
            settings.ATHENAS_INTERNAL,
            settings.JUDICIAL_URL_CACHE,
            lawsuit.pk,
            lawsuit.location.pk,
        ),
        file_path,
    ]

    log.info("compiler command: %s", " ".join(cmd))
    call(cmd, shell=False)

    RemoteEmmiter.emmit_for_user(
        user, "judicial-load-cache-lawsuit", url_cache=lawsuit.abs_url_cache
    )

    if os.path.exists(file_lock):
        os.remove(file_lock)
