# -*- coding: utf-8 -*-

from django.db import models


from rh.models import Servidor
from standard.models import AuditTimestampModel


class ProcessoJudicial(AuditTimestampModel):
    """PROCESSO JUDICIAL."""

    class Meta:
        ordering = ("-id",)
        permissions = (("scmmp_admin", "Administrador de Informações SCMMP"),)

    numero_cnj = models.CharField(max_length=25, verbose_name="Número CNJ", unique=True)
    numero_local = models.CharField(
        max_length=25, verbose_name="Número Local", null=False, blank=False
    )
    orgao_julgador = models.CharField(
        max_length=250, verbose_name="Órgão Julgador", null=False, blank=False
    )
    nome_acao = models.CharField(
        max_length=250, verbose_name="Nome da Ação", null=False, blank=False
    )
    url = models.CharField(max_length=250, verbose_name="Link", null=True, blank=True)
    tipo_processo_judicial = models.SmallIntegerField(
        verbose_name="Tipo",
        choices=((1, "CIVIL"), (2, "CRIMINAL")),
        null=False,
        blank=False,
    )
    resumo = models.TextField(default="", null=True, blank=True, verbose_name="Resumo")
    observacao = models.TextField(
        default="", null=True, blank=True, verbose_name="Observação"
    )

    def __str__(self):
        return "Nº %s" % (self.numero_local)


class MembroProcesso(AuditTimestampModel):
    """MEMBRO PROCESSO."""

    class Meta:
        pass

    processo_judicial = models.ForeignKey(
        ProcessoJudicial,
        related_name="membro_processo",
        verbose_name="Processo Judicial",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    membro = models.ForeignKey(
        Servidor,
        related_name="membro_processo",
        verbose_name="Membro",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    situacao = models.SmallIntegerField(
        verbose_name="Situação",
        choices=(
            (1, "Em Trâmite"),
            (2, "Sobrestado"),
            (3, "Julgado"),
            (4, "Pendente de Recurso"),
            (5, "Transitado em Julgado: procedente"),
            (6, "Transitado em Julgado: improcedente"),
        ),
        null=True,
        blank=True,
    )
    data_situacao = models.DateField(null=True, blank=True, verbose_name="Data")

    # >>>>>>>>>>>> LEMBRAR <<<<<<<<<<<<<<<<<<<
    # CASO O PROCESSO ESTEJA NA SITUACAO 'TRANSITADO EM JULGADO PROCEDENTE, DEVE SER POSSIBILITADO O CADASTRO DA SANÇÃO'

    def __str__(self):
        return "Nº %s - %s " % (self.processo_judicial, self.membro)

    @property
    def icons(self):
        lista = []
        lista.append(self.icon_status)

        return lista

    @property
    def icon_status(self):
        return (
            {
                "iconCls": "icon-scmmp icon-scmmp-decisao",
                "title": "Sanção Judicial cadastrada",
            }
            if self.sancaojudicial.exists()
            else {"iconCls": "icon-scmmp icon-scmmp-blank", "title": ""}
        )


class FaseRecursal(AuditTimestampModel):
    """FASE RECURSAL."""

    class Meta:
        pass

    processo_judicial = models.ForeignKey(
        ProcessoJudicial,
        related_name="fase_recursal",
        verbose_name="Processo Judicial",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    numero_local = models.CharField(
        max_length=25, verbose_name="Número Local", null=False, blank=False
    )
    orgao_julgador = models.CharField(
        max_length=250, verbose_name="Órgão Julgador", null=False, blank=False
    )
    nome_acao = models.CharField(
        max_length=250, verbose_name="Nome da Ação", null=False, blank=False
    )
    url = models.CharField(max_length=250, verbose_name="Link", null=True, blank=True)

    def __str__(self):
        return "Nº %s - Nº %s " % (self.processo_judicial, self.numero_local)


class SancaoJudicial(AuditTimestampModel):
    """SANÇÃO JUDICIAL."""

    class Meta:
        pass

    processo_judicial = models.ForeignKey(
        ProcessoJudicial,
        related_name="processo",
        verbose_name="Processo Judicial",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    membro_processo = models.ForeignKey(
        MembroProcesso,
        related_name="sancaojudicial",
        verbose_name="Membro",
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    resumo = models.TextField(
        default="", null=False, blank=False, verbose_name="Resumo"
    )
    data_imposicao = models.DateField(
        null=False, blank=False, verbose_name="Data da Imposição"
    )
    cumprimento = models.SmallIntegerField(
        verbose_name="Houve Cumprimento?",
        choices=((1, "SIM"), (2, "NÃO")),
        null=True,
        blank=True,
    )
    data_cumprimento = models.DateField(
        null=True, blank=True, verbose_name="Data do Cumprimento"
    )
    ext_punibilidade = models.SmallIntegerField(
        verbose_name="Houve Extinção da Punibilidade?",
        choices=((1, "SIM"), (2, "NÃO")),
        null=False,
        blank=False,
    )
    reabilitacao = models.SmallIntegerField(
        verbose_name="Reabilitação?",
        choices=((1, "SIM"), (2, "NÃO")),
        null=False,
        blank=False,
    )
    data_reabilitacao = models.DateField(
        null=True, blank=True, verbose_name="Data da Reabilitação"
    )

    def __str__(self):
        return "%s - %s " % (self.processo_judicial, self.membro_processo)
