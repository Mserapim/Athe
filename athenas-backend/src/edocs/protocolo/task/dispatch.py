# -*- coding: utf-8 -*-
import os

from celery import Celery
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo, Envelop

app = Celery("reports")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))

log = getLogger(__name__)


@app.task(max_retries=3, rate_limit="2/s")
def async_send_to_person(user_id, movement_id, opts):
    raise Exception("Foi descontinuado em favor do uso de envelopes")


@app.task(max_retries=3, rate_limit="2/s")
def async_send_to_location(user_id, movement_id, opts):
    raise Exception("Foi descontinuado em favor do uso de envelopes")


@app.task(max_retries=3)
def async_protocol_cache_build(protocol_id):
    protocol = Protocolo.objects.get(pk=protocol_id)
    cached = protocol.appends_of_document


@app.task(max_retries=3, rate_limit="4/s")
def async_dispatch_envelop(envelop_id):
    envelop = Envelop.objects.get(pk=envelop_id)
    envelop.dispatch()
