# -*- coding: utf-8 -*-
from django.db import models
from auditlog.registry import auditlog
from datetime import datetime, timedelta

from standard.models import AuditTimestampModel, Choice, JustificationItem


class MarkPoint(AuditTimestampModel):
    mark = models.TimeField(verbose_name="Marcação", blank=True, null=True)
    employee = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="register_point",
        on_delete=models.CASCADE,
    )
    day = models.DateField(verbose_name="Dia", blank=True, null=True)
    ip = models.CharField(verbose_name="IP", blank=True, null=True, max_length=15)
    marcacao = models.DateTimeField("Marcação de Ponto", blank=True, null=True)
    marcacao_valida = models.BooleanField("Marcação Válida", default=True)
    tabela_import = models.CharField(
        "Tabela de Importação", max_length=100, null=True, blank=True
    )
    codigo_import = models.CharField(
        "Código - Importação", max_length=100, null=True, blank=True
    )

    class Meta:
        ordering = ("-day", "-mark")

    @property
    def get_date(self):
        """
        Retorna a data e hora da batida de ponto, caso seja uma justificativa, retorna apenas a data da batida.
        Utiliza a data e a hora do campo 'marcacao' se o campo estiver preenchido. Caso contrário, utiliza os campos mark e day.
        """
        if self.marcacao:
            hora = self.marcacao.time().hour
            minuto = self.marcacao.time().minute
            segundo = self.marcacao.time().second
            if hora == 0 and minuto == 0 and segundo == 0:
                return self.marcacao.date().strftime("%d/%m/%Y")
            else:
                date = self.marcacao.date().strftime("%d/%m/%Y")
                time = self.marcacao.time().strftime("%H:%M:%S")
                return f"{date} {time}"
        else:
            date = self.day.strftime("%d/%m/%Y")
            time = self.mark.strftime("%H:%M:%S")
            return f"{date} {time}"

    @property
    def get_name(self):
        return self.employee.pessoa_fisica.nome

    @property
    def get_matricula(self):
        return self.employee.matricula

    @property
    def get_register(self):
        return self.employee.pessoa_fisica.cpf

    @property
    def get_workplace(self):
        lotacao = self.employee.lotacoes.filter(ativo=True).first()
        return f"{lotacao.nome}"


class FolhaPontoHistoricoNotificacoes(AuditTimestampModel):
    servidor = models.ForeignKey(
        "rh.Servidor",
        verbose_name="Servidor",
        related_name="folha_ponto_historico_notificacoes",
        on_delete=models.CASCADE,
    )
    referencia_ano = models.IntegerField(verbose_name="Referência ano")
    referencia_mes = models.IntegerField(verbose_name="Referência mês")

    db_table = "folhaponto_historico_notificacoes"


auditlog.register(MarkPoint)
