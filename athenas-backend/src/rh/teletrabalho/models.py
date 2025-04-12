from standard.models import AuditTimestampModel
from django.db import models
from django.db.models import Q
from auditlog.registry import auditlog

from datetime import date, timedelta
from contrib.utils import getLogger

log = getLogger(__name__)


def str_data_inicio(data):
    data_split = data.split("/")
    return date(year=int(data_split[1]), month=int(data_split[0]), day=1)


def str_data_fim(data):
    data_split = data.split("/")

    if int(data_split[0]) == 12:
        data_inicio_proximo_mes = date(year=int(data_split[1]) + 1, month=1, day=1)

    else:
        data_inicio_proximo_mes = date(
            year=int(data_split[1]), month=int(data_split[0]) + 1, day=1
        )

    return data_inicio_proximo_mes - timedelta(1)


class ConfigPeriodoEnvioRelatoriosSemestrais(AuditTimestampModel):
    """Configuração do periodo de envio de relatorios semestrais de teletrabalho"""

    titulo = models.CharField(max_length=250, verbose_name="Título")
    data_inicio_periodo_envio = models.DateField(verbose_name="Data Início de Envio")
    data_fim_periodo_envio = models.DateField(
        verbose_name="Data Fim de Envio", null=True, blank=True
    )
    data_inicio_periodo_analisado = models.CharField(
        max_length=10, verbose_name="Data Início de periodo analisado"
    )
    data_fim_periodo_analisado = models.CharField(
        max_length=10,
        verbose_name="Data Fim de periodo analisado",
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = (
            "titulo",
            "data_inicio_periodo_envio",
            "data_inicio_periodo_analisado",
        )

    def __str__(self):
        return f"{self.titulo}"

    def validar_periodo_envio_inicio_fim(self):
        if (
            self.data_fim_periodo_envio
            and self.data_fim_periodo_envio < self.data_inicio_periodo_envio
        ):
            raise Exception(
                "A data final do período de envio não pode ser menor que a inicial."
            )

    def validar_periodo_analisado_inicio_fim(self):
        if str_data_fim(self.data_fim_periodo_analisado) and str_data_fim(
            self.data_fim_periodo_analisado
        ) < str_data_inicio(self.data_inicio_periodo_analisado):
            raise Exception(
                "A data final do período analisado não pode ser menor que a inicial."
            )

    def validar_periodo_envio_concomitante(self):
        q_periodos = ConfigPeriodoEnvioRelatoriosSemestrais.objects.filter(
            Q(data_fim_periodo_envio__gte=self.data_inicio_periodo_envio),
            Q(
                Q(data_fim_periodo_envio__isnull=True)
                | Q(data_fim_periodo_envio__lte=self.data_fim_periodo_envio)
            ),
        )

        if self.pk:
            q_periodos = q_periodos.exclude(pk=self.pk)

        if q_periodos.exists():
            raise Exception("Já existe um Período de envio na data informada.")

    def validar_registro_unico(self):
        q_periodos = ConfigPeriodoEnvioRelatoriosSemestrais.objects.filter(
            titulo=self.titulo,
            data_inicio_periodo_envio=self.data_inicio_periodo_envio,
            data_inicio_periodo_analisado=str_data_inicio(
                self.data_inicio_periodo_analisado
            ),
        )
        if self.pk:
            q_periodos = q_periodos.exclude(pk=self.pk)

        if q_periodos.exists():
            raise Exception(
                """Registro já existente, não pode existir registros com título,
                            data início de período de envio e data de início de analise de substituições iguais."""
            )

    def validar_envio_analise(self):
        if str_data_fim(self.data_fim_periodo_analisado) > self.data_fim_periodo_envio:
            raise Exception(
                """ O período de anlise não pode ser superior ao período de envio."""
            )

    def validacao(self):
        self.validar_periodo_envio_inicio_fim()
        self.validar_periodo_analisado_inicio_fim()
        self.validar_periodo_envio_concomitante()
        self.validar_envio_analise()
        self.validar_registro_unico()

    def save(self, *args, **kargs):
        self.validacao()
        return super().save(*args, **kargs)

    @property
    def data_inicio_periodo_analisado_completa(self):
        return str_data_inicio(self.data_inicio_periodo_analisado)

    @property
    def data_fim_periodo_analisado_completa(self):
        return str_data_fim(self.data_fim_periodo_analisado)


auditlog.register(ConfigPeriodoEnvioRelatoriosSemestrais)
