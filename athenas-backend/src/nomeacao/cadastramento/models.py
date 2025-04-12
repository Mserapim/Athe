from django.db import models

from standard.models import AuditTimestampModel, Choice
from nomeacao.models import PessoaFisicaConvidado
from ged.models import Arquivo
from rh.models import MovimentacaoPosse

from nomeacao.const import TIPO_DOCUMENTO_ANEXO


class ConviteNomeacao(AuditTimestampModel):
    """
    Modelo para armazenar dados sobre o convite à nomeação
    """

    convidado = models.ForeignKey(
        PessoaFisicaConvidado,
        verbose_name="Convite Nomeação",
        related_name="convite_nomeacao",
        on_delete=models.PROTECT,
    )
    tipo_nomeacao = models.IntegerField(
        "Tipo de Nomeação",
        choices=Choice.get_choices_for("nomeacao", "TIPO_NOMEACAO"),
        null=True,
    )
    classificado = models.SmallIntegerField("Classificado?", null=True, blank=True)
    status_convocacao = models.CharField(
        "Status da Convocação", max_length=150, null=True, blank=True
    )
    data_convocacao = models.DateTimeField("Data da Convocação", null=True, blank=True)
    data_email_convocacao = models.DateTimeField(
        "Data do Email de Convocação", null=True, blank=True
    )
    data_desistencia = models.DateTimeField(
        "Data da Desistência", null=True, blank=True
    )
    data_resposta = models.DateTimeField("Data da Resposta", null=True, blank=True)
    data_possivel_expericao = models.DateTimeField(
        "Data da Possível Expiração", null=True, blank=True
    )
    data_expiracao = models.DateTimeField("Data da Expiração", null=True, blank=True)
    sinc_form = models.BooleanField("Sincronizar Formulário", default=True)
    provimento = models.ForeignKey(
        MovimentacaoPosse,
        verbose_name="Provimento",
        related_name="convite_Nomeação",
        on_delete=models.SET_NULL,
        null=True,
    )

    class Meta:
        verbose_name = "Convite de Nomeação"
        verbose_name_plural = "Convites de Nomeação"
        ordering = ("convidado__nome_completo",)

    def __str__(self):
        return f"{self.convidado} - {self.status_convocacao}"


class AnexoConvite(AuditTimestampModel):
    """
    Modelo para armazenar os anexos relacionados à nomeação
    """

    convite = models.ForeignKey(
        ConviteNomeacao,
        verbose_name="Anexo do Convite",
        related_name="anexos",
        on_delete=models.PROTECT,
    )
    tipo_documento = models.SmallIntegerField(
        choices=TIPO_DOCUMENTO_ANEXO, null=True, blank=True
    )
    tipo_documento_descr = models.CharField(
        "Tipo Documento - Descrição", max_length=255, null=True, blank=True
    )
    arquivo_nome = models.CharField(
        "Nome do Arquivo", max_length=100, null=True, blank=True
    )
    arquivo_nome_original = models.CharField(
        "Nome Original do Arquivo", max_length=255, null=True, blank=True
    )
    api_relative_path = models.CharField(
        "Relative Path da API", max_length=255, null=True, blank=True
    )
    api_diretorio = models.CharField(
        "Diretório da API", max_length=255, null=True, blank=True
    )
    arquivo = models.ForeignKey(
        Arquivo,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="anexos_convite_nomeacao",
    )

    class Meta:
        verbose_name = "Anexo do Convite à Nomeação"
        verbose_name_plural = "Anexos do Convite à Nomeação"
        ordering = ("convite__convidado__nome_completo",)

    def __str__(self):
        return f"{self.convite.convidado} - {self.arquivo_nome}"

    @property
    def api_arquivo_path(self):
        from nomeacao.cadastramento.sinc_form_nomeacao_residente import (
            SincFormNomeacaoResidentes,
        )

        return SincFormNomeacaoResidentes().buscar_anexo_url(self.api_relative_path)
