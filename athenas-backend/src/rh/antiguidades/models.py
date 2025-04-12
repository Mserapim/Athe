from standard.models import AuditTimestampModel
from contrib.utils import getLogger
from rh.models import Servidor
from rh.antiguidades.const import ORIGEM, TIPO_CARGO
from django.db import models

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from validate_docbr import CPF as CPFValidateDocBr


log = getLogger(__name__)


class ListaAntiguidadeMembros(AuditTimestampModel):
    """
    Modelo representando a lista de antiguidade de membros.

    Esta classe contém informações sobre a antiguidade dos membros: ordem de antiguidade, início na carreira,
    tempos de afastamento, total na instância, efetivo exercício e total de carreira.
    Além disso, acessa informações relacionadas ao servidor: matrícula, nome,data de início na instância
    e posição no concurso.
    """

    servidor = models.OneToOneField(
        Servidor,
        on_delete=models.PROTECT,
        verbose_name="Servidor",
        related_name="antiguidade",
    )
    ordem_antiguidade = models.PositiveIntegerField(
        verbose_name="Ordem de Antiguidade", null=True
    )
    data_inicio_carreira = models.DateField(
        verbose_name="Início na Carreira", null=True
    )
    data_inicio_instancia = models.DateField(
        verbose_name="Data Início na Instância", null=True
    )
    tempo_afastamento = models.IntegerField(
        verbose_name="Tempo de Afastamento", null=True
    )
    tempo_total_instancia = models.IntegerField(
        verbose_name="Tempo Total na Instância", null=True
    )
    tempo_efetivo_exercicio = models.IntegerField(
        verbose_name="Tempo de Efetivo Exercício", null=True
    )
    tempo_total_carreira = models.IntegerField(
        verbose_name="Tempo Total de Carreira", null=True
    )
    origem = models.CharField(max_length=10, choices=ORIGEM, null=True, blank=True)
    tipo_cargo = models.IntegerField(
        verbose_name="Cargo", choices=TIPO_CARGO, null=True
    )

    class Meta:
        ordering = [
            "tipo_cargo",
            "ordem_antiguidade",
        ]

    @property
    def matricula(self):
        return self.servidor.matricula

    @property
    def cpf(self):
        cpf_klass = CPFValidateDocBr()
        return cpf_klass.mask(self.servidor.pessoa_fisica.cpf)

    @property
    def nome_social(self):
        return self.servidor.pessoa_fisica.social_name

    @property
    def nome(self):
        return self.servidor.pessoa_fisica.nome

    @property
    def posicao_concurso(self):
        return self.servidor.posicao_concurso

    def formatar_duracao(self, data):

        if data:
            hoje = datetime.today().date() + timedelta(
                days=1
            )  # Incrementando 1 dia corretamente
            diferenca = relativedelta(hoje, data)
            return f"{diferenca.years}a {diferenca.months}m {diferenca.days}d"
        return None

    @property
    def tempo_afastamento_formatado(self):
        return f"{self.tempo_afastamento}d"

    @property
    def total_instancia_formatado(self):
        return self.formatar_duracao(
            self.data_inicio_instancia
            if self.data_inicio_instancia and self.tipo_cargo != 3
            else self.data_inicio_carreira
        )

    @property
    def efetivo_exercicio_formatado(self):
        return self.formatar_duracao(
            self.data_inicio_carreira + timedelta(days=self.tempo_afastamento)
        )

    @property
    def total_carreira_formatado(self):
        return self.formatar_duracao(self.data_inicio_carreira)

    def __str__(self):
        return f"{self.servidor.pessoa_fisica.nome} - posição antiguidade: {self.ordem_antiguidade}"
