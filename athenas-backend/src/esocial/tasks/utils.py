# -*- coding: utf-8 -*-
import os

from celery import Celery
from contrib.utils import getLogger

app = Celery("esocial")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


log = getLogger(__name__)


def task_conflict(task_search=[]):
    """Este método verifica se existe alguma task, task_search, rodando no momento.

    Args:
        task_search (list) - lista de tasks que devem ser checadas
    """
    active_queues = app.control.inspect().active() or ()
    for queue in active_queues:
        for running_task in active_queues[queue]:
            if running_task["name"] in task_search:
                return True
    return False


def _task_conflict_with_all(prefer_user=False):
    """Este método verifica se existe alguma task, task_search, rodando no momento.
    Utilizará todas as tarefas definidas task_search.

    Args:
        prefer_user (bool) - encontrar tarefas com usuário preferencialmente.
    """
    task_search = [
        "esocial.tasks.generation.create_events_task",
        "esocial.tasks.generation.generate_events_ti_task",
        "esocial.tasks.generation.generate_events_ti_registration_task",
        "esocial.tasks.generation.generate_events_registration_task",
        "esocial.tasks.generation.generate_event_registration",
        "esocial.tasks.generation.generate_events_payroll_task",
        "esocial.tasks.generation.generate_events_payroll_task_list",
        "esocial.tasks.generation.generate_events_payroll_process_task",
        "esocial.tasks.generation.generate_events_payroll_process_task_list",
        "esocial.tasks.generation.generate_delete_events_payroll_task",
        "esocial.tasks.generation.generate_close_events_payroll_task",
        "esocial.tasks.generation.generate_reopen_events_payroll_task",
        "esocial.tasks.generation.create_batches_task",
        "esocial.tasks.generation.clear_restricted_production_task",
        "esocial.tasks.generation.delete_events_not_sent_task",
        "esocial.tasks.generation.consult_batches_task",
        "esocial.tasks.generation.send_batches_task",
        "esocial.tasks.generation.generate_delete_events_task",
        "esocial.tasks.generation.analysis_task",
        "esocial.tasks.generation.analysis_all_period_task",
        "esocial.tasks.tasks.process_batches",
        "esocial.tasks.tasks.consult_batch",
        "esocial.tasks.tasks.send_batches",
    ]
    found = {}
    active_queues = app.control.inspect().active() or ()
    for queue in active_queues:
        for running_task in active_queues[queue]:
            if running_task["name"] in task_search:
                found = running_task
                if not prefer_user:
                    return found
                elif prefer_user and found.get("kwargs", {}).get("user", None):
                    return found
    return found


def task_conflict_with_all():
    """Este método verifica se existe alguma task, task_search, rodando no momento.
    Utilizará todas as tarefas definidas task_search.

    Args:
        task_search (list) - lista de tasks que devem ser checadas
    """
    return (_task_conflict_with_all() and True) or False
