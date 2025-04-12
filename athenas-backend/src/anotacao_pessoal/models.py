from django.db import models
from django.db.models.query import QuerySet

from standard.models import AuditTimestampModel, Choice
from rh.gfp.models import Servidor
from rh.models import Publicacao


class AnotacaoPessoalManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(exibir=True)

    def get_queryset_all(self):
        return super().get_queryset()


class AnotacaoPessoal(AuditTimestampModel):
    """
    Modelo responsável por armazenar dados de Anotações Pessoais
    """

    servidor = models.ForeignKey(
        Servidor, related_name="anotacao_pessoal", on_delete=models.PROTECT
    )
    texto = models.TextField("Texto Anotação", null=True, blank=True)
    publicacao = models.ForeignKey(
        Publicacao,
        related_name="anotacao_pessoal",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    tipo = models.IntegerField(
        "Tipo de Anotação",
        choices=Choice.get_choices_for("rh", "TIPO_ANOTACAO"),
        null=True,
        blank=True,
    )
    documento_numero = models.CharField(
        "Número Documento", max_length=20, null=True, blank=True
    )
    documento_ano = models.IntegerField("Ano Documento", null=True, blank=True)
    documento_tipo = models.IntegerField(
        "Tipo de Documento",
        choices=Choice.get_choices_for("rh", "TIPO_DOCUMENTO"),
        null=True,
        blank=True,
    )
    documento_data = models.DateField("Data do Documento", null=True, blank=True)
    data_efeito_inicio = models.DateField("Data Efeito Início", null=True, blank=True)
    data_efeito_fim = models.DateField("Data Efeito Fim", null=True, blank=True)
    gedoc_numero = models.TextField(
        "Número GEDOC", max_length=50, null=True, blank=True
    )
    login_resp_import = models.TextField(
        "Login Responsável - SIAP Importação", max_length=100, null=True, blank=True
    )
    nome_resp_import = models.TextField(
        "Nome Responsável - SIAP Importação", max_length=100, null=True, blank=True
    )
    data_ultima_alteracao_import = models.DateTimeField(
        "Data Última Alteração - SIAP Importação", null=True, blank=True
    )
    status_import = models.SmallIntegerField(
        "Status - SIAP Importação", null=True, blank=True
    )
    codigo_siap_import = models.CharField(
        "Código - SIAP Importação", max_length=100, null=True, blank=True
    )
    exibir = models.BooleanField("Exibir", default=True)

    objects = AnotacaoPessoalManager()

    class Meta:
        verbose_name = "Anotação Pessoal"
        ordering = ("-documento_data",)

    def __str__(self):
        num_doc = (
            f" - Número Documento: {self.documento_numero}"
            if self.documento_numero
            else ""
        )
        return f"{self.servidor} - {self.get_tipo_display()}{num_doc}"

    @property
    def login_responsavel(self):
        return (
            self.login_resp_import
            if self.login_resp_import
            else self.created_by.username
        )

    @property
    def modified_at(self):
        return (
            self.data_ultima_alteracao
            if self.data_ultima_alteracao
            else self.modified_at
        )

    @property
    def tipo_label(self):
        if self.tipo:
            return self.get_tipo_display()
        return None

    @property
    def documento_tipo_label(self):
        if self.documento_tipo:
            return self.get_documento_tipo_display()
        return None

    @property
    def publicacao_label(self):
        if self.publicacao:
            return str(self.publicacao)
        return None

    @property
    def data_publicacao(self):
        if self.publicacao:
            return self.publicacao.data_publicacao
        return None

    @property
    def data_expedicao_publicacao(self):
        if self.publicacao:
            return self.publicacao.data_expedicao
        return None
