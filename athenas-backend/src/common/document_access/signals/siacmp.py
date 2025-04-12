# -*- encoding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from common.document_access.models import (
    AllowedListItem,
    AttendanceControl,
    ControlType,
    LegalPrerogative,
)
from common.saci.models import Attendance, Step
from common.saci.signals.custom import access_control_signal
from contrib.middleware import get_current_user
from contrib.utils import getLogger, person_from_user


log = getLogger()
log_prefix = "[document_access]"


def _classify_attendance(attendance, control_type, justification, legal_prerogative):
    log.info(
        f"{log_prefix} Classifying SIACMP Attendance: {attendance.protocol.codigo}"
    )

    attendance_control, obj_created = AttendanceControl.classify(
        document=attendance,
        control_type=control_type,
        legal_prerogative=legal_prerogative,
        justification=justification,
    )


def _reclassify_attendance(attendance, control_type, justification, legal_prerogative):
    log.info(
        f"{log_prefix} ReClassifying SIACMP Attendance: {attendance.protocol.codigo}"
    )

    control = attendance.attendance_control

    # Somente reclassifica se o nível de acesso fornecido for diferente do atual.
    if control.control_type != control_type:
        with transaction.atomic():
            control.reclassify(
                control_type=control_type,
                legal_prerogative=legal_prerogative,
                justification=justification,
            )


@receiver(access_control_signal, sender=Attendance)
def attendance_access_control(
    sender, attendance, control_type_id, justification, legal_prerogative_id, **kwargs
):
    try:
        control_type = ControlType.objects.get(id=control_type_id)
    except ControlType.DoesNotExist:
        raise Exception("O Nível de Acesso fornecido não existe.")

    try:
        legal_prerogative = LegalPrerogative.objects.get(id=legal_prerogative_id)
    except LegalPrerogative.DoesNotExist:
        raise Exception("A Hipótese Legal fornecida não existe.")

    # Se já tem controle de acesso, reclassifica. Senão, classifica.
    if hasattr(attendance, "attendance_control"):
        _reclassify_attendance(
            attendance=attendance,
            control_type=control_type,
            legal_prerogative=legal_prerogative,
            justification=justification,
        )
    else:
        _classify_attendance(
            attendance=attendance,
            control_type=control_type,
            legal_prerogative=legal_prerogative,
            justification=justification,
        )


@receiver(post_save, sender=Step)
def post_save_step(sender, instance, *args, **kwargs):
    if hasattr(instance.attendance, "attendance_control"):
        control = instance.attendance.attendance_control

        # Allowedlist é para classificações com grau de sigilo.
        if (
            control.control_type
            and control.control_type.is_secret
            and hasattr(instance.destination, "lotacao")
        ):
            person = instance.destination.lotacao.responsavel.pessoa_fisica
            log.info(f"{log_prefix} Granting access to: {person}")
            try:
                control.grant_person_access(person)
            except AllowedListItem.CurrentUserNotAllowed:
                raise Exception(
                    "Este documento possui controle de acesso e não pode ser encaminhado."
                )
