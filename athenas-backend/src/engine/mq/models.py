# -*- coding: utf-8 -*-
import json
import uuid
import logging
import datetime

from django.db import models
from app.settings import HERMES_TOKEN
from common.util.send_email import EmailNotification
from contrib.documents import mascarar_cpf
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
from default.views import Application as app
from engine.mq.const import (
    SISTEMA_HERMES,
    STATUS_NOTIFICACAO,
    TEMPLATE_NOTIFICACAO_HERMES,
    TIPO_TASK_PROCESSAMENTO_ESOCIAL,
    TIPO_TASK_PROCESSAMENTO_RELATORIO,
    TIPO_TOKEN_HERMES,
)
from rh.servidor.mastiff_utils import MastiffGraphql
from standard.models import Choice, EmailTemplate
from ged.models import Arquivo as FileGED
from dateutil.relativedelta import relativedelta
from common.services.models import ScheduledServices, HistoricoServico

from decimal import *

log = logging.getLogger()

# TASKS STATES
# initializing
# progress
# ready
# failed


class Task(models.Model):
    owner = models.ForeignKey(
        "auth.user", related_name="my_tasks_in_mq", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    description = models.CharField(
        max_length=255, verbose_name="Description", default=""
    )
    uuid = models.CharField(max_length=36, db_index=True)
    state = models.CharField(max_length=15, default="initializing")
    message = models.TextField()
    data = models.TextField()
    params = models.TextField(default="{}")
    progress = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    progress_message = models.CharField(max_length=100, null=True)

    started_task = models.DateTimeField(
        verbose_name="Started", auto_now_add=True, db_index=True
    )
    finished_task = models.DateTimeField(
        verbose_name="Finished", null=True, db_index=True
    )
    visualized = models.BooleanField(
        verbose_name="Visualized", default=False, blank=True
    )
    notificar_hermes = models.BooleanField(
        verbose_name="Notificar hermes", default=False, blank=True
    )
    tipo_processamento = models.IntegerField(
        choices=Choice.get_choices_for("engine", "TIPO_PROCESSAMENTO_TASK"),
        verbose_name="Tipo de processamento",
        null=True,
        blank=True,
    )
    servico = models.ForeignKey(
        ScheduledServices,
        verbose_name="Serviço",
        related_name="task",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    # total = models.PositiveIntegerField(default=0, blank=True)
    # count = models.PositiveIntegerField(default=0, blank=True)
    # increment = models.PositiveSmallIntegerField(default=1, blank=True)
    # starter_id = models.CharField(max_length=20, verbose_name='Starter ID', null=True)

    class Meta:
        ordering = ("-pk",)

    @property
    def finished(self):
        return (self.state.startswith("mf-") and True) or False

    @property
    def executed(self):
        return self.finished or self.state in ["ready", "failed"]

    def increment_progress(self, inc):
        self.__class__.objects.filter(pk=self.pk).update(
            progress=models.F("progress") + inc
        )

    def finish_execution(self, status="SUCCESS", msg="", pct_msg="", set_process=True):
        self.finished_task = datetime.datetime.now()
        self.state = "failed" if status in ["ERROR", "failed"] else "ready"
        if set_process and self.progress is not None:
            self.progress = 100
        uptime = relativedelta(self.finished_task, self.started_task)
        self.info(
            "Processado em - %dh %smin %ss"
            % (uptime.hours, uptime.minutes, uptime.seconds)
        )
        if msg:
            self.message = msg
        if pct_msg:
            self.progress_message = pct_msg

        self.save()

    def mark_finished(self, state=None, msg=""):
        if not self.finished:
            if msg:
                self.message = msg
            self.state = "-".join(["mf", self.state if not state else state])
            self.visualized = True
            self.save()
        else:
            raise Exception("A tarefa %s já esta marcada como finalizada." % self.uuid)

    def info(self, msg="", type_of=1, file_ged=None, pct=0, msg_pct="", pct_progress=0):
        log.debug("TASK SAVE...")
        if pct != 0 or pct_progress != 0:
            if pct_progress != 0:
                if self.progress is None:
                    self.progress = Decimal(pct_progress)
                else:
                    self.progress = self.progress + Decimal(pct_progress)
            else:
                if pct != 0:
                    self.progress = pct
            if not msg_pct:
                msg_pct = "Processando %.1f%%" % self.progress
            self.progress_message = msg_pct
            self.save()
        if msg:
            self.messages.create(message=msg[0:400], type_of=type_of, file_ged=file_ged)

    def add_message(self, msg=""):
        self.messages.create(message=msg[0:400])

    def add_file(self, afile, msg=""):
        if not msg:
            msg = "Arquivo gerado: %s" % afile.filename
        self.info(msg, type_of=4, file_ged=afile)

    def save(self, *args, **kwags):
        if not self.pk:
            self.owner = get_current_user()
            self.uuid = str(uuid.uuid4())

        if self.servico and self.uuid:
            historico = (
                HistoricoServico.objects.filter(servico=self.servico)
                .order_by("-iniciado_em")
                .first()
            )
            if historico:
                HistoricoServico.objects.filter(pk=historico.pk).update(ssid=self.uuid)

        super(Task, self).save(*args, **kwags)
        self.notificar_email_hermes()

    def get_template(self):
        try:
            cod_template = TEMPLATE_NOTIFICACAO_HERMES.get(self.tipo_processamento)
            return EmailTemplate.objects.get(code=cod_template)
        except:
            log.error(
                f"Não foi possível encontrar o Modelo de Email: NOTIFICACAO_HERMES!"
            )
            return None

    def get_conteudo_template(self, template):
        conteudo = ""
        if self.tipo_processamento == TIPO_TASK_PROCESSAMENTO_RELATORIO:
            conteudo = template.contents.replace("%link%", self.message).replace(
                "%nome_relatorio%", self.description
            )
        elif self.tipo_processamento == TIPO_TASK_PROCESSAMENTO_ESOCIAL:
            tp_processamento = Choice.objects.filter(
                name="TIPO_PROCESSAMENTO_TASK", value=TIPO_TASK_PROCESSAMENTO_ESOCIAL
            ).first()
            conteudo = (
                template.contents.replace("%descricao%", self.description)
                .replace("%mensagem%", self.message)
                .replace(
                    "%tipo_processamento%",
                    tp_processamento.label if tp_processamento else "",
                )
            )
        return conteudo

    def notificar_email_hermes(self):
        if self.notificar_hermes and self.state in STATUS_NOTIFICACAO.get(
            self.tipo_processamento, ["ready"]
        ):
            servidor = employee_from_user(get_current_user())
            pessoa_fisica = servidor.pessoa_fisica
            destinatarios = [
                {
                    "email": pessoa_fisica.email,
                    "nome": pessoa_fisica.nome,
                    "idUsuario": servidor.id_usuario_mastiff,
                }
            ]
            template = self.get_template()
            if template:
                conteudo = self.get_conteudo_template(template)
                assunto = template.subject
                token = TIPO_TOKEN_HERMES.get(self.tipo_processamento, HERMES_TOKEN)
                sistema = SISTEMA_HERMES.get(self.tipo_processamento, "ATHENAS")
                EmailNotification().send_email_default(
                    destinatarios,
                    assunto,
                    conteudo,
                    hermes_token=token,
                    sistema=sistema,
                )

    @classmethod
    def start(klass, method, description="", **kwargs):
        from engine.mq.utils import get_servico

        log.debug("STARTING...")
        task = klass()
        params = kwargs.copy()
        servico = get_servico()

        if "data_model" in params:
            params.pop("data_model")
        task.params = json.dumps(params)
        task.description = description
        task.servico = servico
        task.save()

        kwargs.update(
            task=task.uuid,
            hook="https://athenas.py27/athenas/MQTaskRestful/hook/%s/" % task.uuid,
        )

        # method.apply_async(kwargs=kwargs, queue='reports')
        queue = None
        if "queue" in kwargs:
            queue = kwargs["queue"]
            kwargs.pop("queue")
        method.apply_async(kwargs=kwargs, queue=queue)
        return task

    def __str__(self):
        return "<engine.mq.Task uuid:%s>" % self.uuid

    @staticmethod
    @app.session_resource("tasker")
    def to_session_resource():
        query = Task.objects.filter(
            owner=get_current_user(), state__in=("ready", "failed")
        )

        return query.count()


class TaskMessages(models.Model):
    """ """

    class Meta:
        ordering = ("id",)

    tasker = models.ForeignKey(
        Task, verbose_name="Task", related_name="messages", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    message = models.CharField(
        max_length=400,
        verbose_name="Message",
    )
    type_of = models.PositiveSmallIntegerField(
        verbose_name="Type",
        default=1,
        choices=Choice.get_choices_for("engine", "TASK_MESSAGE_TYPE"),
        db_index=True,
    )
    file_ged = models.ForeignKey(
        FileGED,
        verbose_name="Arquivo",
        related_name="mq_tasks_messages",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
