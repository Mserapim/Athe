from __future__ import unicode_literals

import os

from django.conf import settings
from django.core.management import call_command
from django.db import migrations
from standard.models import Choice
from rh.pvf.models import PointJustification, PortalRequest
from rh.pvf.const import STS_CANCELED_APPLICANT, STS_CANCELED_DGP, STS_REJECTED

FIXTURES = ("fixtures/choices.json",)


def forward(*args, **kwargs):
    """
    Cancela PointJustfication de solicitações com status status Indeferido, Cancelado DGP ou Cancelado Solicitante no VDF.
    """

    print("Running forward...")
    request_type = Choice.objects.get(
        app_label="pvf", name="REQUEST_TYPE", label="Folha Ponto"
    )
    pvf_requests = PortalRequest.objects.filter(
        request_type=request_type.value,
        status__in=[STS_REJECTED, STS_CANCELED_DGP, STS_CANCELED_APPLICANT],
    )

    for pvf_request in pvf_requests:
        point_justifications = PointJustification.objects.filter(
            request=pvf_request, cancelado=False
        )
        point_justifications.update(cancelado=True)


def backward(*args, **kwargs):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [
        ("pvf", "0033_pvfsolicitacaocreditofolga"),
    ]

    operations = [migrations.RunPython(forward, backward)]
