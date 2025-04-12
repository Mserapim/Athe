# -.- coding: utf-8 -.-
from datetime import datetime

from adm.mto.models import ElementoDespesaSubItem
from contrib.decorator import to_search
from contrib.utils import getLogger
from django.db import models

log = getLogger(__name__)


class PPARevisao(models.Model):
    data_vigencia = models.DateField(null=True)
    ano_inicio = models.SmallIntegerField()
    ano_fim = models.SmallIntegerField()
    ano_revisao = models.SmallIntegerField(null=True)
    publicacao = models.ForeignKey(
        "rh.Publicacao",
        related_name="revisoes_ppa",
        null=True,
        on_delete=models.CASCADE,
    )
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return "REVISÃO %d (%d até %d)" % (
            int(self.ano_revisao or 0),
            int(self.ano_inicio or 0),
            int(self.ano_fim or 0),
        )

    def save(self, *args, **kwags):
        if (
            self.__class__.objects.filter(data_vigencia__lt=self.data_vigencia).exists()
            and self.ativo
        ):
            self.__class__.objects.filter(data_vigencia__lt=self.data_vigencia).filter(
                ativo=True
            ).update(ativo=False)

        super(PPARevisao, self).save(*args, **kwags)


class PPAPrograma(models.Model):
    revisao = models.ForeignKey(
        PPARevisao, related_name="programas", on_delete=models.CASCADE
    )
    codigo = models.CharField(max_length=10, null=False)
    parent = models.ForeignKey(
        "self",
        related_name="sub_programas",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(max_length=60)

    def save(self, *args, **kargs):
        models.Model.save(self, *args, **kargs)
        for acao in self.acoes.all():
            acao.save()


@to_search(
    [
        {"name": "cache_codigo", "type": "text"},
        {"name": "titulo", "type": "text"},
    ]
)
class PPAAcao(models.Model):
    codigo = models.CharField(max_length=10, null=False)
    funcao = models.CharField(max_length=10, null=False, verbose_name="Função")
    subfuncao = models.CharField(max_length=10, null=False, verbose_name="Subfunção")
    programa = models.ForeignKey(
        PPAPrograma, related_name="acoes", null=True, on_delete=models.CASCADE
    )
    titulo = models.CharField(max_length=120)
    fonte_exclusiva = models.ForeignKey(
        "contabilidade.FonteRecurso",
        related_name="acoes_vinculadas",
        null=True,
        on_delete=models.CASCADE,
    )
    cache_codigo = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return "%s/%s - %s" % (
            self.cache_codigo,
            self.programa.revisao.ano_revisao,
            self.titulo,
        )

    def save(self, *args, **kargs):
        self.cache_codigo = "%(funcao)02d.%(subfuncao)03d.%(programa)s.%(acao)s" % {
            "programa": self.programa.codigo,
            "acao": self.codigo,
            "funcao": int(self.funcao or 0),
            "subfuncao": int(self.subfuncao or 0),
        }

        models.Model.save(self, *args, **kargs)

    @property
    def revision_year(self):
        if self.programa and self.programa.revisao.ano_revisao:
            return self.programa.revisao.ano_revisao
        return None

    def checa_conjunto_fonte(self, fonte):
        """
        Checa se a ação pode ser utilizada em conjunto com a fonte. No caso das ações com fonte exclusivas.
        """
        if self.fonte_exclusiva.exists():
            return fonte in self.fonte_exclusiva.all()
        else:
            return True

    # def get_process_for_current_year(self, solicitation):
    #     from adm.diarias.models import Solicitacao as Solicitation


#
#     if not isinstance(solicitation, Solicitation):
#         raise Exception('Forneça uma instância válida de solicitação de diária.')
#
#     return self.process.filter(
#         ano_referencia=datetime.today().year,
#         tipo=1,
#         active=True,
#         for_debt_recognition=bool(solicitation.reconhecido_divida)
#     ).get()


class GrupoContabil(models.Model):
    numero = models.IntegerField(unique=True)
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.numero, self.descricao)


class Unidade(models.Model):
    sigla = models.CharField(max_length=6)
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return "{0} - {1}".format(self.sigla, self.descricao)


@to_search(
    [
        {"name": "descricao", "type": "text"},
        {"name": "grupo_contabil__numero", "type": "number"},
        {"name": "grupo_contabil__descricao", "type": "text"},
        {"name": "elemento_despesa_subitem__numero", "type": "number"},
        {"name": "elemento_despesa_subitem__descricao", "type": "text"},
    ]
)
class Categoria(models.Model):
    class Meta:
        unique_together = ["elemento_despesa_subitem", "grupo_contabil"]

    elemento_despesa_subitem = models.ForeignKey(
        "mto.ElementoDespesaSubItem", on_delete=models.CASCADE
    )
    grupo_contabil = models.ForeignKey("GrupoContabil", on_delete=models.CASCADE)
    descricao = models.CharField(max_length=150)

    def __str__(self):
        return str(self.descricao)


@to_search(
    [
        {"name": "unidade__sigla", "type": "text"},
        {"name": "unidade__descricao", "type": "text"},
        {"name": "descricao", "type": "text"},
    ]
)
class Produto(models.Model):
    subitem = models.ForeignKey(
        ElementoDespesaSubItem,
        related_name="produto",
        null=True,
        on_delete=models.CASCADE,
    )
    unidade = models.ForeignKey("Unidade", on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    quantidade = models.IntegerField()
    fracao = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        return str(self.descricao)


@to_search(
    [
        {"name": "numero", "type": "text"},
        {"name": "descricao", "type": "text"},
    ]
)
class FonteRecurso(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=150)
    convenio = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.numero, self.descricao)


@to_search([{"name": "numero", "type": "text"}])
class NE(models.Model):
    """NE = NotaEmpenho"""

    # credor = models.ForeignKey('cpl.ProdutoVencedor', null = True, on_delete=models.CASCADE)
    # produto_processo = models.ForeignKey('compras.ProdutoProcesso', on_delete=models.CASCADE)
    numero = models.CharField(max_length=50, unique=True)
    data = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    data_nota = models.DateField(null=True, blank=True)
    modalidade = models.IntegerField(
        choices=((1, "ORDINÁRIO"), (3, "ESTIMATIVA"), (5, "GLOBAL"))
    )
    valor = models.DecimalField(max_digits=16, decimal_places=2, blank=True)

    class Meta:
        ordering = ("-id", "numero")
        # unique_together = ('credor', 'produto_processo')

    def __str__(self):
        return self.numero

    # def save(self, force_insert=False, force_update=False):
    #     log = getLogger("NE:Model")
    #     try:
    #         if not self.valor: raise Exception('O valor deve ser informado!')
    #         super(NE, self).save(force_insert, force_update)
    #     except Exception, e:
    #         log.exception(e)
    #         raise e

    # def get_calculo_valor(self):
    #     return 0


class BudgetaryIndicator(models.Model):
    """Indicador Orçamentário: Ação, Objeto e Fonte."""

    action = models.ForeignKey(
        PPAAcao, related_name="budgetary_indicators", on_delete=models.CASCADE
    )
    object_name = models.CharField(max_length=128, verbose_name="Objeto")
    source = models.ForeignKey(
        FonteRecurso, related_name="budgetary_indicators", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=64, verbose_name="I.O.")
    year = models.CharField(max_length=4, verbose_name="Ano", null=True, blank=True)

    class Meta:
        verbose_name = "Indicador Orçamentário"
        unique_together = ("name", "object_name", "action", "source")

    def __str__(self):
        return "%s" % self.name
