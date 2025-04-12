# -.- coding: utf-8 -.-
from standard.models import PROJETO_STATUS_CHOICES
from standard.models import TENDENCIA_CHOICES
from standard.models import INDICADOR_TIPO_CHOICES
from standard.models import INDICADOR_PERIODO_CHOICES
from standard.models import METODO_ANALISE_CHOICES
from rh.models import Servidor
from django.db import models
import datetime
from contrib.decorator import filter, FilterInformation, FilterType, to_search


class InstallApplication:
    prefixo_controller = "PE"
    title_application = "PE"
    install_application = False
    create_views = False
    menu = [
        "Planejamento Estratégico",
        "pe",
        0,
        ["Cadastro", "cadastro_pe", 0],
        ["Parâmetros", "parametros_pe", 0],
    ]


@to_search(
    [
        {"name": "descricao", "type": "text"},
    ]
)
class Planejamento(models.Model):
    """
    Cadastro do Planejamento Estratégico
    """

    descricao = models.CharField(max_length=200, verbose_name="Descrição", unique=True)
    data_inicio = models.DateField(
        verbose_name="Data para Início", null=True, blank=True
    )
    data_termino = models.DateField(
        verbose_name="Data para Término", null=True, blank=True
    )
    metodo_analise = models.IntegerField(
        choices=METODO_ANALISE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Método para Análise",
    )
    limite_alta = models.IntegerField(verbose_name="Limite inferior para ALTA")
    limite_baixa = models.IntegerField(verbose_name="Limite superior para BAIXA")
    objetivo = models.ManyToManyField("Objetivo", verbose_name="Objetivo")

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.descricao


@to_search(
    [
        {"name": "planejamento__descricao", "type": "text"},
        {"name": "descricao", "type": "text"},
    ]
)
class Objetivo(models.Model):
    """
    Cadastro dos objetivos de um Planejamento Estratégico.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome", unique=True)
    descricao = models.CharField(max_length=4000, verbose_name="Descrição", unique=True)
    projeto = models.ManyToManyField("Projeto", verbose_name="Projeto")
    indicador = models.ManyToManyField("Indicador", verbose_name="Indicador")

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.nome


@to_search(
    [
        {"name": "objetivo__descricao", "type": "text"},
        {"name": "servidor__nome", "type": "text"},
        {"name": "tendencia", "type": "text"},
    ]
)
class Analise(models.Model):
    """
    Cadastro dos análises de um objetivo específico.
    """

    objetivo = models.ForeignKey(
        Objetivo,
        related_name="fkey_objetivo_avaliacao",
        verbose_name="Objetivo",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    responsavel = models.ForeignKey(
        Servidor,
        related_name="fkey_servidor_analise",
        verbose_name="Responsável",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data = models.DateField(null=True, blank=True, verbose_name="Data de Referência")
    tendencia = models.IntegerField(
        choices=TENDENCIA_CHOICES, null=True, blank=True, verbose_name="Tendência"
    )
    analise = models.CharField(
        max_length=4000, verbose_name="Análise", null=True, blank=True
    )
    recomendacoes = models.CharField(
        max_length=4000, verbose_name="Recomendações", null=True, blank=True
    )

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.analise


@to_search(
    [
        {"name": "nome", "type": "text"},
    ]
)
class Periodo(models.Model):
    """
    Cadastro dos periodos para metas e coletas de dados dos indicadores.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome", unique=True)
    dias = models.IntegerField(null=False, blank=False, verbose_name="Dias")

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.nome


@to_search(
    [
        {"name": "objetivo__descricao", "type": "text"},
        {"name": "descricao", "type": "text"},
        {"name": "nome", "type": "text"},
    ]
)
class Indicador(models.Model):
    """
    Cadastro dos indicadores de um Objetivo.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome", unique=True)
    descricao = models.CharField(max_length=4000, verbose_name="Descrição")
    tipo = models.IntegerField(
        choices=INDICADOR_TIPO_CHOICES, null=True, blank=True, verbose_name="Tipo"
    )
    periodo = models.ForeignKey(
        Periodo,
        related_name="fkey_periodo_indicador",
        verbose_name="Período",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    peso = models.IntegerField(null=True, blank=True, verbose_name="Peso")
    indicadormeta = models.ManyToManyField(
        "IndicadorMeta", verbose_name="Indicador Meta"
    )

    class InstallModel:
        node_menu = "cadastro_pe"

    def save(self, force_insert=False, force_update=False):
        if self.peso is None:
            self.peso = 1
        super(Indicador, self).save(force_insert, force_update)

    def __str__(self):
        return self.nome


@to_search(
    [
        {"name": "indicador__descricao", "type": "text"},
    ]
)
class IndicadorValor(models.Model):
    """
    Cadastro dos valores aferidos de um indicador para uma data específica.
    """

    indicador = models.ForeignKey(
        Indicador,
        related_name="fkey_indicador_indicadorvalor",
        verbose_name="Indicador",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data = models.DateField(null=True, blank=True, verbose_name="Data")
    valor = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valor")

    class InstallModel:
        node_menu = "cadastro_pe"


class IndicadorMeta(models.Model):
    """
    Cadastro da meta de um indicador para uma data específica.
    """

    data = models.DateField(null=True, blank=True, verbose_name="Data")
    valor = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valor")

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.data.strftime("%d/%m/%Y")


@to_search(
    [
        {"name": "indicador__nome", "type": "text"},
        {"name": "servidor__nome", "type": "text"},
        {"name": "tendencia", "type": "text"},
    ]
)
class AnaliseIndicador(models.Model):
    """
    Cadastro dos análises de um indicador específico.
    """

    indicador = models.ForeignKey(
        Indicador,
        related_name="fkey_analiseindicador_avaliacao",
        verbose_name="Indicador",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    responsavel = models.ForeignKey(
        Servidor,
        related_name="fkey_servidor_analiseindicador",
        verbose_name="Responsável",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data = models.DateField(null=True, blank=True, verbose_name="Data de Referência")
    tendencia = models.IntegerField(
        choices=TENDENCIA_CHOICES, null=True, blank=True, verbose_name="Tendência"
    )
    analise = models.CharField(
        max_length=4000, verbose_name="Análise", null=True, blank=True
    )
    recomendacoes = models.CharField(
        max_length=4000, verbose_name="Recomendações", null=True, blank=True
    )

    class InstallModel:
        node_menu = "cadastro_pe"


@to_search(
    [
        {"name": "objetivo__descricao", "type": "text"},
        {"name": "nome", "type": "text"},
        {"name": "descricao", "type": "text"},
        {"name": "servidor__nome", "type": "text"},
    ]
)
class Projeto(models.Model):
    """
    Cadastro dos projetos de um Objetivo.
    """

    nome = models.CharField(max_length=200, verbose_name="Nome", unique=True)
    descricao = models.CharField(
        max_length=4000, verbose_name="Descrição", null=True, blank=True
    )
    responsavel = models.ForeignKey(
        Servidor,
        related_name="fkey_servidor_projeto",
        verbose_name="Responsável",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data_inicio = models.DateField(
        verbose_name="Data para Início", null=True, blank=True
    )
    data_termino = models.DateField(
        verbose_name="Data para Término", null=True, blank=True
    )
    status = models.IntegerField(
        choices=PROJETO_STATUS_CHOICES, null=True, blank=True, verbose_name="Status"
    )
    andamento = models.IntegerField(null=True, blank=True, verbose_name="Andamento")

    class InstallModel:
        node_menu = "cadastro_pe"

    def __str__(self):
        return self.nome


@filter(
    (
        FilterInformation(
            field_real="projeto", field_virtual="projeto__nome", type=FilterType.TEXT
        ),
    )
)
@to_search(
    [
        {"name": "projeto__nome", "type": "text"},
    ]
)
class AndamentoProjeto(models.Model):
    """
    Cadastro dos valores aferidos de do andamento do projeto.
    """

    projeto = models.ForeignKey(
        Projeto,
        related_name="fkey_projeto_andamentoprojeto",
        verbose_name="Projeto",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)
    data = models.DateField(null=True, blank=True, verbose_name="Data")
    concluido = models.CharField(max_length=50, verbose_name="Concluído")

    class InstallModel:
        node_menu = "cadastro_pe"
