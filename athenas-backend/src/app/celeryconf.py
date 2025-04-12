# -*- coding: utf-8 -*-
import importlib

import django
from contrib.config import config as _config
from decouple import config
from kombu import Exchange, Queue

django.setup()

broker_url = _config(
    "CELERY_BROKER_URL", default="amqp://admin:secr3t@rabbitmq/default"
)

broker_pool_limit = _config("BROKER_POOL_LIMIT", default=0)

result_backend = _config("CELERY_RESULT_BACKEND", default="mongodb://mongo/celery_0")

worker_pool_restarts = _config("CELERY_POOL_RESTARTS", default=True)

mongodb_backend_settings = _config(
    "CELERY_MONGODB_BACKEND_SETTINGS",
    default={"database": "celery_0", "taskmeta_collection": "celery_0_taskmeta"},
)

imports = [
    "contrib.reports",
    "edocs.protocolo.task.rh_reference",
    "edocs.protocolo.task.reports",
    "edocs.protocolo.task.dispatch",
    "edocs.protocolo.task.cache_build",
    "edocs.protocolo.task.flowchart",
    "rh.task.workplace",
    "rh.task.sicapap",
    "rh.task.cnmp_report",
    "rh.task.account_integration",
    "rh.task.hoursworkcontractworkload",
    "rh.task.afastamento.recess_batch",
    "rh.gfp.previdencia.task.igeprev",
    "common.poll.tasks",
    "common.saci.tasks",
    "judicial.tasks",
    "judicial.tasks.realtime",
    "ged.task",
    "raf.tasks",
    "rh.gfp.tasks",
    "rh.gfp.tasks_paycheckdifference",
    "rh.gfp.tasks_conference",
    "rh.gfp.tasks_gcpp",
    "rh.gfp.tasks_payment_vacation",
    "rh.gratifications_manager.tasks_cumulative_exercises",
    "rh.gratifications_manager.tasks_cumulative_exercises_permanent",
    "rh.gratifications_manager.tasks_gm",
    "rh.gratifications_manager.tasks_aux_coord",
    "rh.gratifications_manager.tasks_diligence",
    "rh.gratifications_manager.tasks_gratifications",
    "rh.gratifications_manager.tasks_member_gratifications",
    "rh.ferias.tasks",
    "adm.patrimonio.tasks",
    "esocial.tasks.qualification",
    "esocial.tasks.generation",
    # 'corregedoria.cirdir.tasks',
    "esocial.tasks.tasks",
    # 'corregedoria.cirdir.tasks',
    "corregedoria.reportbuilder.tasks",
    "rh.dayoff.tasks",
    "common.clinical.tasks",
    "web.media_indoor.tasks",
    "rh.pvf.tasks",
    "reports.tasks",
    "rh.queryregistration.tasks",
    "rh.defin.tasks_eventualprovider",
    "rh.gfp.dirf.tasks",
    "rh.ponto.tasks_falta",
    "nomeacao.cadastramento.tasks_sinc_form_nomeacao_residente",
    "rh.servidor.tasks_atualizar_infos",
    "rh.registerpoint.tasks_atualizar_campo_marcacao",
    "rh.folhaponto.tasks_importar_justificativas",
    "rh.folhaponto.tasks_importar_batidas",
    "rh.servidor.tasks_servidor_id_usuario_mastiff",
    "rh.teletrabalho.tasks",
]

django_conf = importlib.import_module("django.conf")
if getattr(django_conf.settings, "ENABLE_ARQUIMEDES", True):
    imports.append("rh.task.arquimedes")

accept_content = _config("CELERY_ACCEPT_CONTENT", default=["json"])

task_serializer = _config("CELERY_TASK_SERIALIZER", default="json")

enable_utc = _config("CELERY_ENABLE_UTC", default=False)

timezone = _config("TIME_ZONE", default="America/Cuiaba")

task_acks_late = _config("CELERY_ACKS_LATE", default=True)

worker_prefetch_multiplier = _config("CELERYD_PREFETCH_MULTIPLIER", default=1)

task_default_queue = _config("CELERY_DEFAULT_QUEUE", default="default")

worker_log_format = _config(
    "CELERYD_LOG_FORMAT",
    default="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
)

task_queues = (
    Queue(
        "realtime",
        Exchange("realtime"),
        routing_key="realtime",
        queue_arguments={"x-max-priority": 100},
    ),
    Queue(
        "reports",
        Exchange("reports"),
        routing_key="reports",
        queue_arguments={"x-max-priority": 100},
    ),
    Queue(
        "important",
        Exchange("important"),
        routing_key="important",
        queue_arguments={"x-max-priority": 50},
    ),
    Queue(
        "default",
        Exchange("default"),
        routing_key="default",
        queue_arguments={"x-max-priority": 1},
    ),
    Queue(
        "esocial-events",
        Exchange("esocial-events"),
        routing_key="esocial-events",
        queue_arguments={"x-max-priority": 1},
    ),
    # Queue('low-priority', Exchange('low-priority'), routing_key='low-priority', queue_arguments={'x-max-priority': 1}),
)

task_routes = {
    "contrib.reports.start_report": {"queue": "reports"},
    "judicial.tasks.realtime.create_cache_document": {"queue": "realtime"},
    "judicial.tasks.realtime.create_cache_lawsuit": {"queue": "realtime"},
}
