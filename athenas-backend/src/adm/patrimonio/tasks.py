# -*- coding: utf-8 -*-
import os

from celery import Celery

from adm.patrimonio.models import Avaliacao, Notification
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from engine.mq.models import Task


app = Celery("patrimonio")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))

log = getLogger()


@app.task
def avaliation_analise(task, avaliation, *args, **kwargs):
    log.info("Task: %s", task)
    log.info("AvaliacaoID: %d", avaliation)

    task = Task.objects.get(uuid=task)
    obj = Avaliacao.objects.get(pk=avaliation)

    def feedback(message, pct=0.0, **params):
        task.progress_message = message % params
        task.progress = pct
        task.save()

    obj.feedback = feedback

    task.message = "Analizando a %s..." % str(obj)
    task.state = "progress"
    task.save()
    obj.analize()
    task.state = "ready"
    task.message = "Processo de analize de %s concluído." % str(obj)
    task.save()


@app.task
def avaliation_execute(task, avaliation, username="athenas", *args, **kwargs):
    log.info("Task: %s", task)
    log.info("AvaliacaoID: %d", avaliation)

    set_current_user(username)
    task = Task.objects.get(uuid=task)
    obj = Avaliacao.objects.get(pk=avaliation)

    def feedback(message, pct=0.0, **params):
        task.progress_message = message % params
        task.progress = pct
        task.save()

    obj.feedback = feedback

    task.message = "Executando a %s..." % str(obj)
    task.state = "progress"
    task.save()
    obj.analize(True)
    task.state = "ready"
    task.message = "Processo de execução de %s concluído." % str(obj)
    task.save()


@app.task
def avaliation_populate(task, avaliation, *args, **kwargs):
    log.info("Task: %s", task)
    log.info("AvaliacaoID: %d", avaliation)

    task = Task.objects.get(uuid=task)
    obj = Avaliacao.objects.get(pk=avaliation)

    def feedback(message, pct=0.0, **params):
        task.progress_message = message % params
        task.progress = pct
        task.save()

    obj.feedback = feedback

    task.message = "Populando a %s..." % str(obj)
    task.state = "progress"
    task.save()
    obj.populate()
    task.state = "ready"
    task.message = "Processo de população de %s concluído." % str(obj)
    task.save()


@app.task
def bulk_send(movements_pk, username):
    """Cria uma notificação para cada Movimento

    Argumentos:
        movements_pk: Uma lista de chaves-primárias de Movimento
        username: String contendo o nome do usuário corrente

    """
    set_current_user(username)
    Notification.bulk_send(movements_pk)


@app.task
def generate_term(report, params, output_format="PDF"):
    """Gera o Termo de Responsabilidade

    Argumentos:
        report: O caminho do relatório na árvore do Jasper Server
        params: Parâmetros para a geração do relatório
        output_format: Formato do arquivo de saída

    """
    return Notification.generate_term(report, params, output_format)


@app.task
def attach_and_dispatch(filename, notification_pk, username):
    """Cria o protocolo, anexa o termo de responsabilidade e despacha o protocolo

    Argumentos:
        filename: Caminho do arquivo de relatório gerado no método generate_term
        notification_pk: Chave-primária do modelo Notification
        username: String contendo o nome do usuário corrente

    OBS: O argumento 'filename' (poderia ser qualquer nome) é
    posicional e recebe o output da task à esquerda do pipe
    (ver primitiva chain do Celery).

    """
    set_current_user(username)
    Notification.attach_and_dispatch(filename, notification_pk)
