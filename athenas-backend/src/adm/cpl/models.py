# -.- coding: utf-8 -.-
from contrib.decorator import to_search
from django.db import models
from django.db.models import Q
from standard.models import Choice


class PublicacaoLicitacao(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    licitacao = models.ForeignKey(
        "Licitacao", verbose_name="Licitação", on_delete=models.CASCADE
    )
    # Parametro "on_delete" adicionado. (Django 2)
    arquivo = models.ForeignKey(
        "ged.Arquivo", null=True, blank=True, on_delete=models.CASCADE
    )
    objeto = models.TextField(null=True, blank=True)
    interno = models.BooleanField(null=False, default=False)
    ano = models.CharField(verbose_name="Ano", max_length=4, blank=True)
    veiculo_publicacao = models.IntegerField(
        verbose_name="Veículo Publicação",
        null=True,
        blank=True,
        choices=Choice.get_choices_for("rh", "VEICULO_PUBLICACAO"),
    )
    numero_publicacao = models.CharField(
        max_length=22, null=True, blank=True, verbose_name="Número Publicação"
    )
    data_publicacao = models.DateField(
        verbose_name="Data da Publicação", null=True, blank=True
    )
    data_expedicao = models.DateField(blank=True, verbose_name="Data de expedição")
    tipo = models.IntegerField(
        choices=(
            (1, "ATA DE REGISTRO DE PREÇOS"),
            (2, "AVISO"),
            (3, "EDITAL"),
            (4, "ESCLARECIMENTO"),
            (5, "IMPUGNAÇÃO"),
            (6, "HOMOLOGAÇÃO"),
        )
    )
    natureza = models.IntegerField(
        choices=((1, "ADIADO"), (2, "PRORROGADO"), (3, "REMARCADO")),
        null=True,
        blank=True,
    )

    def save(self, force_insert=False, force_update=False):
        self.ano = self.data_expedicao.year
        super(PublicacaoLicitacao, self).save(force_insert, force_update)


class Participante(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    licitacao = models.ManyToManyField(
        "Licitacao", symmetrical=False, verbose_name="Licitação"
    )
    pessoa = models.OneToOneField("rh.Pessoa", on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.pessoa.nome

    def is_vencedor(self, licitacao):
        try:
            if self.produtovencedor_set.get(licitacao=licitacao).produto_processo.all():
                return True
        except Exception:
            pass
        return False


class Licitacao(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    processo = models.ForeignKey(
        "compras.ProcessoAquisicao", related_name="licitacao", on_delete=models.CASCADE
    )
    modalidade = models.IntegerField(
        choices=(
            (1, "CONCORRÊNCIA"),
            (2, "CARTA CONVITE"),
            (3, "PREGÃO ELETRÔNICO"),
            (4, "PREGÃO PRESENCIAL"),
            (5, "TOMADA DE PREÇO"),
        )
    )
    registro_preco = models.BooleanField(
        default=False, verbose_name="Registro de preço"
    )
    numero = models.CharField(max_length=100, verbose_name="Número")
    data_realizacao = models.DateTimeField(
        verbose_name="Data de realização", null=True, blank=True
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    arquivado = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    contrato = models.BooleanField(default=False)
    homologada = models.BooleanField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False):
        if Licitacao.objects.filter(processo=self.processo) and self.pk is None:
            raise Exception("Este Processo já possui uma Licitação associada a ele.")
        if not self.processo.is_ok():
            raise Exception(
                "Ainda existem pendências para que o processo possa torna-se uma licitação."
            )
        super(Licitacao, self).save(force_insert, force_update)

    def tem_pendencia(self):
        """
        Este método verifica se há pendências relacionadas à licitação.
        Retorna True, caso exista. De outra forma retorna False.
        """
        publicacao_licitacao = PublicacaoLicitacao.objects.filter(
            Q(Q(licitacao=self) & Q(tipo__in=[2, 3]))
        )
        if publicacao_licitacao.count() >= 2:
            return False
        return True


@to_search(
    [
        {"name": "participante__pessoa__nome", "type": "text"},
        {"name": "licitacao__numero", "type": "text"},
    ]
)
class ProdutoVencedor(models.Model):
    # Parametro "on_delete" adicionado. (Django 2)
    participante = models.ForeignKey("Participante", on_delete=models.CASCADE)
    # Parametro "on_delete" adicionado. (Django 2)
    licitacao = models.ForeignKey(
        "Licitacao", related_name="produtovencedor", on_delete=models.CASCADE
    )
    produto_processo = models.ManyToManyField(
        "compras.ProdutoProcesso", symmetrical=False, related_name="vencedor_produto"
    )

    class Meta:
        unique_together = ("participante", "licitacao")

    def __str__(self):
        return "%s" % self.participante.pessoa.nome

    def get_calculo_valor_ne(self):
        total = 0
        for pp in self.produto_processo.all():
            total += pp.valor_total
        return total

    def get_produto_quantidade(self):
        return 0
