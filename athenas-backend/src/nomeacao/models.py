from django.db import models

from standard.models import AuditTimestampModel, Choice
from rh.models import Localidade

from nomeacao.const import (
    TIPO_COR,
    TEM_DEFICIENCIA,
    TIPO_SEXO,
    TIPO_COTA,
    TIPO_ESCOLARIDADE,
)


class PessoaFisicaConvidado(AuditTimestampModel):
    """
    Modelo para armazenar dados importados do formulário de pessoas que são convidadas à nomeação.
    """

    nome_completo = models.CharField("Nome Completo", max_length=255)
    nome_social = models.CharField("Nome Social", max_length=100, null=True, blank=True)
    dt_nascimento = models.DateField("Data de Nascimento", null=True, blank=True)
    cor = models.SmallIntegerField(choices=TIPO_COR, null=True, blank=True)
    deficiencia = models.SmallIntegerField(
        "Deficiência?", choices=TEM_DEFICIENCIA, null=True, blank=True
    )
    tel_cel = models.CharField("Telefone Celular", max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    sexo = models.CharField(
        "Sexo", max_length=1, choices=TIPO_SEXO, null=True, blank=True
    )
    orientacao_sexual = models.PositiveSmallIntegerField(
        "Orientação Sexual",
        choices=Choice.get_choices_for("rh", "SEXUAL_ORIENTATION"),
        null=True,
        blank=True,
    )
    identidade_genero = models.CharField(
        "Identidade de Gênero", max_length=100, null=True, blank=True
    )
    cota = models.CharField(
        "Cota", max_length=2, choices=TIPO_COTA, null=True, blank=True
    )
    sangue_tipo = models.CharField(
        "Tipo Sanguíneo",
        choices=Choice.get_choices_for("rh", "BLOOD"),
        max_length=15,
        null=True,
        blank=True,
    )
    sangue_fator_rh = models.IntegerField(
        "Fator RH",
        choices=Choice.get_choices_for("rh", "FACTOR_RH"),
        null=True,
        blank=True,
    )
    sangue_doador = models.BooleanField("Doador de Sangue", null=True, blank=True)
    filiacao_mae = models.CharField(
        "Filiação - Mãe", max_length=250, null=True, blank=True
    )
    filiacao_pai = models.CharField(
        "Filiação - Pai", max_length=250, null=True, blank=True
    )

    class Meta:
        verbose_name = "Pessoa Física - Convidado à Nomeação"
        verbose_name_plural = "Pessoas Físicas - Convidados à Nomeação"
        ordering = ("nome_completo",)

    def __str__(self):
        return str(self.nome_completo)


class DocumentoConvidado(AuditTimestampModel):
    """
    Modelo para armazenar dados dos documentos pessoais do convidado à nomeação
    """

    convidado = models.OneToOneField(
        PessoaFisicaConvidado,
        verbose_name="Documentação Convidado",
        related_name="documentacao",
        on_delete=models.PROTECT,
    )
    rg = models.CharField("RG", max_length=20, null=True, blank=True)
    rg_numero = models.CharField("RG - Número", max_length=20, null=True, blank=True)
    rg_orgao = models.CharField("RG - Orgão", max_length=255, null=True, blank=True)
    rg_uf = models.CharField("RG - UF", max_length=2, null=True, blank=True)
    rg_data = models.DateField("RG - Data", null=True, blank=True)
    cnh_numero = models.CharField("CNH - Número", max_length=30, null=True, blank=True)
    cnh_uf = models.CharField("CNH - UF", max_length=2, null=True, blank=True)
    cnh_categoria = models.CharField(
        "CNH - Categoria", max_length=10, null=True, blank=True
    )
    cnh_data_exp = models.CharField(
        "CNH - Data Expiração", max_length=15, null=True, blank=True
    )
    cnh_data_val = models.CharField(
        "CNH - Data Validade", max_length=15, null=True, blank=True
    )
    cpf = models.CharField("CPF", max_length=20, null=True, blank=True)
    tit_eleit_numero = models.CharField(
        "Título Eleitoral - Número", max_length=15, null=True, blank=True
    )
    tit_eleit_zona = models.CharField(
        "Título Eleitoral - Zona", max_length=3, null=True, blank=True
    )
    tit_eleit_secao = models.CharField(
        "Título Eleitoral - Seção", max_length=4, null=True, blank=True
    )
    tit_eleit_municipio = models.CharField(
        "Título Eleitoral - Município", max_length=255, null=True, blank=True
    )
    tit_eleit_municipio_id = models.IntegerField(
        "Título Eleitoral - Município ID", null=True, blank=True
    )

    class Meta:
        verbose_name = "Documentação da Pessoa Física - Convidado à Nomeação"
        verbose_name_plural = "Documentação das Pessoas Físicas - Convidados à Nomeação"
        ordering = ("convidado__nome_completo",)

    def __str__(self):
        return f"{self.convidado} - {self.cpf}"

    @property
    def cpf_sem_mascara(self):
        return self.cpf.replace("-", "").replace(".", "")


class EscolaridadeConvidado(AuditTimestampModel):
    """
    Modelo para armazenar dados de escolaridade do convidado à nomeação
    """

    convidado = models.OneToOneField(
        PessoaFisicaConvidado,
        verbose_name="Escolaridade Convidado",
        related_name="escolaridade",
        on_delete=models.PROTECT,
    )
    escolaridade = models.SmallIntegerField(
        choices=TIPO_ESCOLARIDADE, null=True, blank=True
    )
    coeficiente_graduacao = models.CharField(
        "Coeficiente Graduação", max_length=10, null=True, blank=True
    )
    nome_instituicao_graduacao = models.CharField(
        "Nome Instituição Graduação", max_length=255, null=True, blank=True
    )
    data_conclusao_graduacao = models.DateField(
        "Data de Conclusão da Graduação", null=True, blank=True
    )
    nome_instituicao_pos_graduacao = models.CharField(
        "Nome Instituição Pós Graduação", max_length=255, null=True, blank=True
    )

    class Meta:
        verbose_name = "Escolaridade da Pessoa Física - Convidado à Nomeação"
        verbose_name_plural = "Escolaridade das Pessoas Físicas - Convidados à Nomeação"
        ordering = ("convidado__nome_completo",)

    def __str__(self):
        return f"{self.convidado} - {self.get_escolaridade_display()}"


class EnderecoConvidado(AuditTimestampModel):
    """
    Modelo para armazenar dados de endereço do convidado à nomeação
    """

    convidado = models.OneToOneField(
        PessoaFisicaConvidado,
        verbose_name="Endereço Convidado",
        related_name="endereco",
        on_delete=models.PROTECT,
    )
    tipo_endereco = models.CharField(
        "Tipo Endereço", max_length=20, null=True, blank=True
    )
    tipo_logradouro = models.CharField(
        "Tipo Logradouro", max_length=20, null=True, blank=True
    )
    logradouro = models.CharField("Logradouro", max_length=255, null=True, blank=True)
    numero = models.CharField("Número", max_length=20, null=True, blank=True)
    compl = models.CharField("Complemento", max_length=100, null=True, blank=True)
    bairro = models.CharField("Bairro", max_length=100, null=True, blank=True)
    cep = models.CharField("CEP", max_length=20, null=True, blank=True)
    municipio = models.ForeignKey(
        Localidade,
        verbose_name="Município",
        related_name="endereco_nomeacao",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Endereço da Pessoa Física - Convidado à Nomeação"
        verbose_name_plural = "Endereço das Pessoas Físicas - Convidados à Nomeação"
        ordering = ("convidado__nome_completo",)

    def __str__(self):
        return f"{self.convidado} - {self.tipo_endereco}"


class DadoBancarioConvidado(AuditTimestampModel):
    """
    Modelo para armazenar dados bancários do convidado à nomeação
    """

    convidado = models.OneToOneField(
        PessoaFisicaConvidado,
        verbose_name="Dados Bancários Convidado",
        related_name="dados_bancarios",
        on_delete=models.PROTECT,
    )
    banco = models.CharField("Banco", max_length=50, null=True, blank=True)
    tipo_conta = models.CharField("Tipo de Conta", max_length=50, null=True, blank=True)
    numero_agencia = models.CharField(
        "Agência - Número", max_length=50, null=True, blank=True
    )
    numero_conta = models.CharField(
        "Conta - Número", max_length=50, null=True, blank=True
    )

    class Meta:
        verbose_name = "Dados Bancários da Pessoa Física - Convidado à Nomeação"
        verbose_name_plural = (
            "Dados Bancários das Pessoas Físicas - Convidados à Nomeação"
        )
        ordering = ("convidado__nome_completo",)

    def __str__(self):
        return f"{self.convidado} - banco: {self.banco} - ag: {self.numero_agencia} - conta: {self.numero_conta}"
