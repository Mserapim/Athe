# -*- coding: utf-8 -*-

import json
import os
from logging import getLogger

import requests
from celery import Celery
from django.conf import settings

from rh.models import Servidor

log = getLogger(__name__)

app = Celery("account-integration")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task()
def account_integration_proxy(employee_id, encoded_data):
    employee = Servidor.objects.get(pk=employee_id)

    try:
        log.info(
            'Enviando informações do servidor "%s" para o "account-integration".',
            employee,
        )
        req = requests.post(
            getattr(settings, "ACCOUNT_INTEGRATION_ENDPOINT", "undefined"),
            headers={
                "Authorization": getattr(
                    settings, "ACCOUNT_INTEGRATION_TOKEN", "undefined"
                ),
                "Content-Type": "application/json",
            },
            json=json.loads(encoded_data),
        )

        log.info("Status code: %s", req.status_code)
        log.info("Data: %s", req.text)

        if req.status_code == 200:
            log.info(
                'Dados processados do servidor "%s" no "account-integration" com sucesso.',
                employee,
            )
        else:
            res = json.loads(req.text)
            log.debug(req.text)
            log.debug(res)
            log.error("Messagem: %s", res.get("message", "undefined"))
    except Exception as e:
        log.info(
            "End Point: %s",
            getattr(settings, "ACCOUNT_INTEGRATION_ENDPOINT", "undefined"),
        )
        log.info(getattr(settings, "ACCOUNT_INTEGRATION_TOKEN", "undefined"))
        log.exception(e)
