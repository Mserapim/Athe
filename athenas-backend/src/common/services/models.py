import importlib
import logging

from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from standard.models import AuditTimestampModel, Choice, ClassCode
from django.contrib.auth.models import User

from contrib.utils import getLogger
from contrib.middleware import get_current_user

log = getLogger(__name__)


class ScheduledServices(AuditTimestampModel):
    name = models.CharField(verbose_name="Nome", null=True, blank=True, max_length=50)
    command = models.TextField(verbose_name="Comando", null=True, blank=True)
    description = models.TextField(verbose_name="Descrição", null=True, blank=True)
    classcode = models.ForeignKey(
        ClassCode,
        verbose_name="ClassCode",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    executado_em = models.DateTimeField(
        verbose_name="Executado em", null=True, blank=True
    )
    executado_por = models.ForeignKey(
        User,
        verbose_name="Executado por",
        blank=True,
        null=True,
        related_name="historico_servico",
        on_delete=models.PROTECT,
    )
    executado = models.BooleanField("Executado", default=False, blank=True)
    em_execucao = models.BooleanField("Em execução", default=False, blank=True)

    class Meta:
        verbose_name = "Serviços Agendados"
        ordering = ("name",)
        unique_together = ("classcode", "command")

    def __str__(self):
        return f"{self.name}"

    def is_permission_services(self):
        """Checar se o usuário pertence ao grupo mpmt-perfil-servicos-agendado-admin,
        que o qual terá permissão para criar/editar/excluir serviços"""

        group_name = Choice.objects.filter(
            name="PERMISSION_SERVICES", app_label="common"
        ).first()
        if group_name:
            user = get_current_user()
            return user.groups.filter(name=group_name).exists()
        else:
            return False

    def run_job(self):
        a = importlib.import_module(self.classcode.path_module)
        class_to_run = getattr(a, self.classcode.name_class)
        if self.command:
            func_to_run = getattr(class_to_run, self.command)
            return func_to_run(class_to_run())
        return class_to_run()

    def validate(self, not_validate=False):
        self.validate_blank()
        self.validate_permissions(not_validate)
        return True

    def validate_blank(self):
        if not self.name or not self.command or not self.description:
            raise Exception("Favor preencher os campos Nome, Comando e Descrição.")

    def validate_permissions(self, not_validate):
        if not self.is_permission_services() and not not_validate:
            raise Exception(
                "Você não tem permissão para criar/alterar/excluir Serviços."
            )

    def save(self, *args, **kwargs):
        self.validate(not_validate=kwargs.get("not_validate", False))
        super(ScheduledServices, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.validate()
        super(ScheduledServices, self).delete(*args, **kwargs)


LOG_LEVELS = (
    (logging.NOTSET, "NOTSET"),
    (logging.INFO, "INFO"),
    (logging.WARNING, "WARNING"),
    (logging.DEBUG, "DEGUB"),
    (logging.ERROR, "ERROR"),
    (logging.FATAL, "FATAL"),
)


class StatusLog(models.Model):
    logger_name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(
        choices=LOG_LEVELS, default=logging.ERROR, db_index=True
    )
    msg = models.TextField()
    path = models.TextField()
    trace = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    def __str__(self):
        return self.msg

    class Meta:
        ordering = ("create_datetime",)
        verbose_name_plural = verbose_name = "Logging"


class HistoricoServico(AuditTimestampModel):
    EXECUCAO = (
        (0, ""),
        (1, "Manual"),
        (2, "Automático"),
    )

    iniciado_em = models.DateTimeField(null=True, blank=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)
    ssid = models.CharField(max_length=400, verbose_name="SSID", null=True, blank=True)
    execucao = models.SmallIntegerField(
        default=0, choices=EXECUCAO, blank=True, null=True
    )
    sucesso = models.BooleanField("Status", default=False, blank=True)
    servico = models.ForeignKey(
        ScheduledServices,
        verbose_name="Serviço",
        related_name="historico_servico",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.servico.name}: {self.iniciado_em} - {self.finalizado_em}"

    @property
    def possui_mensagens(self):
        from engine.mq.models import TaskMessages

        if self.ssid and TaskMessages.objects.filter(tasker__uuid=self.ssid).exists():
            return True
        return False
