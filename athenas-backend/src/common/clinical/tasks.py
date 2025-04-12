# -*- coding: utf-8 -*-
import os

from celery import Celery
from contrib.utils import getLogger
from common.clinical.models import Prescription
from ged.models import Arquivo as FileObject
from django.conf import settings
from auth.jwt.models import DisposableVoucher
from subprocess import call
from contrib.middleware import set_current_user
from edocs.protocolo.models import Protocolo, Attachment, TipoDocumento
from django.db import transaction

log = getLogger("tasker")

app = Celery("report")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def manufacture_prescription(prescription_id):
    prescription = Prescription.objects.get(pk=prescription_id, delivery_state=2)
    vouche = DisposableVoucher.objects.create(user=prescription.signed_by)

    set_current_user(prescription.signed_by)

    if not os.path.exists(prescription.cache_directory):
        os.makedirs(prescription.cache_directory)

    cmd = (
        settings.JUDICIAL_WKHTML_CMD
        + settings.JUDICIAL_WKHTML_STATIC_PARAMS
        + [
            "--custom-header",
            "Authorization",
            "JWT %s" % (vouche.jwt.decode()),
            "%s%s/%d"
            % (
                settings.ATHENAS_INTERNAL,
                "/ClinicalPrescription/printer",
                prescription.pk,
            ),
            prescription.cache_filepath,
        ]
    )

    log.info(" ".join(cmd))
    return_code = call(cmd, shell=False)

    if return_code == 0:
        with open(prescription.cache_filepath, "rb") as fd:
            fd.content_type = "application/pdf"
            prescription.file_description = FileObject.create_from_stream(
                fd, prescription.signed_by
            )

        prescription.file_description.filename = "receituario-%d-%05d.pdf" % (
            prescription.prescription_year,
            prescription.prescription_number,
        )
        prescription.file_description.save()

        prescription.delivery_state = 3
        prescription.save()

        os.unlink(prescription.cache_filepath)
    else:
        raise Exception("Ocorreram erros ao tentar gerar o pdf verifique os logs")


@app.task()
def delivery_prescription(prescription_id):
    prescription = Prescription.objects.get(pk=prescription_id, delivery_state=3)

    set_current_user(prescription.signed_by)

    with transaction.atomic():
        protocol = Protocolo.docketing(
            subject="Receituário %s" % prescription.cache_number,
            document_type=TipoDocumento.objects.get(pk=89),
            interested=prescription.doctor.person,
            home_court=prescription.doctor_workplace,
            external_number=prescription.cache_number,
            content="Segue anexo o receituário digital para ser impresso.",
        )

        protocol.sign_document()
        movement = protocol.movimentacoes.first()
        movement.attachments.add(
            Attachment(
                title="Receituário Médico", attach=prescription.file_description
            ),
            bulk=False,
        )
        movement.do_send(
            person_destination=[prescription.partner.pessoa_fisica.pk],
            confidential=True,
            advice="Segue anexo o receituário digital para ser impresso.",
            employee_origin=prescription.doctor_employee,
        )

        prescription.protocol = protocol
        prescription.delivery_state = 4
        prescription.save()
