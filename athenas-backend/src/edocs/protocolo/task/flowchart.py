# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import os
import time

from celery import Celery
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.template import loader

from contrib.utils import getLogger, DateUtils
from edocs.protocolo.flowchart import ProtocolFlowchart, supported_output_formats
from edocs.protocolo.models import Protocolo as Protocol
from engine.mq.models import Task


log = getLogger()

app = Celery("flowchart")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def generate(task, hook, protocol, output_format):
    error_tag = '<span style="font-weight: bold; color: red">ERRO</span>:'
    try:
        try:
            task_obj = Task.objects.get(uuid=task)
        except Task.DoesNotExist:
            task_obj = None
            msg = f"Não foi possível recuperar a task de uuid {task}."
            raise ObjectDoesNotExist(msg)

        cache_dir = getattr(settings, "CACHE", {}).get("flowchart", None)
        if not cache_dir:
            raise ImproperlyConfigured(
                f"{error_tag} Não foi possível recuperar o caminho do "
                'diretório de cache para "flowchart".'
            )

        if not output_format or not isinstance(output_format, str):
            raise Exception(
                f"{error_tag} O formato de saída fornecido é inválido. "
                f"Formatos válidos: {supported_output_formats}."
            )

        if not protocol:
            raise Exception(f"{error_tag} Forneça um id de protocolo válido.")

        try:
            protocol_obj = Protocol.objects.select_related(
                "interessado",
                "orgao_geral_origem",
                "servidor_origem__pessoa_fisica",
                "tipo_documento",
            ).get(pk=protocol)
        except Protocol.DoesNotExist:
            raise ObjectDoesNotExist(
                f"{error_tag} Não foi possível encontrar "
                f"o protocolo de id {protocol}."
            )

        filename = f"{protocol_obj.codigo}_{task}.{output_format.lower()}"
        abs_path = os.path.join(cache_dir, filename)

        flowchart = ProtocolFlowchart(protocol=protocol_obj, detailed=True)
        flowchart.render()
        flowchart.save_to_file(abs_path)

        rendered = loader.get_template("protocolo/flowchart/message.html").render(
            {"task": task, "output_format": output_format, "code": protocol_obj.codigo}
        )

        task_obj.message = rendered
        task_obj.data = filename
        task_obj.state = "ready"
        task_obj.save()

        time.sleep(0.5)
    except Exception as e:
        log.exception(str(e))
        if task_obj:
            task_obj.state = "failed"
            task_obj.message = str(e)
            task_obj.save()
        else:
            raise e
