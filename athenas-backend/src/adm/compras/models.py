# -*- coding: utf-8 -*-
from adm.contabilidade.models import NE
from adm.eproc.models import Processo
from contrib.decorator import to_search
from contrib.utils import getLogger
from django.conf import settings
from django.db import models
from django.db.models import Q


class NotaDotacao(models.Model):
    numero = models.CharField(max_length=50, unique=True)
    programa_trabalho = models.CharField(max_length=50)
    # Parametro "on_delete" adicionado. (Django 2)
    fonte_recurso = models.ForeignKey(
        "contabilidade.FonteRecurso", null=True, blank=True, on_delete=models.CASCADE
    )
    natureza_despesa = models.ForeignKey(
        "mto.NaturezaDespesa", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    valor = models.DecimalField(max_digits=16, decimal_places=2)
    data = models.DateTimeField(null=True, blank=True)

    def valor_alocado(self):
        total = 0

        for pp in self.produtos.all():
            total += float(pp.quantidade) * float(pp.valor_unitario_estimado)

        return total

    def total(self):
        return float(self.valor) - self.valor_alocado()

    def pendencia_valor_produtos_nd(self):
        """
        Este método verifica se a soma dos valores de todos os produtos do processo é igual ao valor da nota de dotação.
        @return boolean - True: quando hover pendência. False: quando não houver pendência.
        """
        return (
            False
            if ProdutoProcesso.get_soma_produto(
                ProdutoProcesso.objects.filter(nota_dotacao=self)
            )
            == self.valor
            else True
        )

    def __str__(self):
        return self.numero


@Processo.register_type(
    type_="processoaquisicao",
    controller="toolkit.adm.compras.ProcessoAquisicao",
    icon="static/adm/images/processo_aquisicao.png",
)
class ProcessoAquisicao(Processo):
    orcamento = models.IntegerField(
        choices=((1, "NOTA DE DOTAÇÃO"), (2, "IDENTIFICAÇÃO ORÇAMENTÁRIA"))
    )

    def get_type_information(self):
        pendencia, message = self.pendencias()
        return [
            {
                "icon": "/%s/static/adm/images/%s"
                % (
                    getattr(settings, "CONTEXT", ""),
                    "ok.png" if not pendencia else "pendente.png",
                ),
                "alt": message,
                "title": message,
            }
        ]

    def is_ok(self):
        return False not in [p.is_ok() for p in self.produtos.all()]

    def pendencias(self):
        if self.produtos.count() == 0:
            return True, "Nenhum produto associado ao processo."
        else:
            count = 0
            for p in self.produtos.all():
                if not p.is_ok():
                    count += 1

            if count > 0:
                return True, (
                    "Tem um produto com pendência."
                    if count == 1
                    else "Temos %d produtos com pendências." % count
                )
            else:
                return False, "Sem pendências."


@to_search(
    [
        {"name": "descricao", "type": "text"},
        {"name": "produto__descricao", "type": "text"},
    ]
)
class ProdutoProcesso(models.Model):
    class Meta:
        unique_together = ["produto", "processo_aquisicao"]

    # Parametro "on_delete" adicionado. (Django 2)
    produto = models.ForeignKey(
        "contabilidade.Produto", related_name="processos", on_delete=models.CASCADE
    )
    nota_dotacao = models.ManyToManyField("NotaDotacao", related_name="produtos")
    # Parametro "on_delete" adicionado. (Django 2)
    processo_aquisicao = models.ForeignKey(
        "ProcessoAquisicao", related_name="produtos", on_delete=models.CASCADE
    )
    quantidade = models.IntegerField()
    valor_unitario_estimado = models.DecimalField(max_digits=16, decimal_places=2)
    valor_unitario_lance = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    valor_unitario_aditivo = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    valor_unitario = models.DecimalField(max_digits=16, decimal_places=2)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return "%s" % (self.produto.descricao)

    def save(self, force_insert=False, force_update=False):
        # if self.processo_aquisicao.licitacao.count() >  0:
        #   raise Exception('Não posso modificar um processo de aquisição que já esteja em licitação')
        self.valor_unitario = self.valor_unitario_estimado
        super(ProdutoProcesso, self).save(force_insert, force_update)

    # TODO: CONSTRUIR UMA PROPRIEDADE
    def _valor_total(self):
        return self.quantidade * self.valor_unitario

    def is_ok(self):
        if self.processo_aquisicao.orcamento == 2:
            return True

        if self.nota_dotacao.count() > 0:
            nd_total = 0.0
            pd_total = 0.0
            to_sum = {}

            for nd in self.nota_dotacao.all():
                nd_total += float(nd.valor)
                for produto in nd.produtos.all():
                    to_sum[produto.pk] = float(produto.quantidade) * float(
                        produto.valor_unitario_estimado
                    )

            for key in list(to_sum.keys()):
                pd_total += to_sum.get(key, 0.0)

            return nd_total == pd_total
        else:
            return False

    def get_pendencias(self):
        pends = []
        if not (self.nota_dotacao.count() > 0):
            pends.append("Produto sem Nota de dotacão. ")
        else:
            nd_total = 0.0
            pd_total = 0.0
            to_sum = {}

            for nd in self.nota_dotacao.all():
                nd_total += float(nd.valor)
                for produto in nd.produtos.all():
                    to_sum[produto.pk] = float(produto.quantidade) * float(
                        produto.valor_unitario_estimado
                    )

            for key in list(to_sum.keys()):
                pd_total += to_sum.get(key, 0.0)

            total = nd_total - pd_total

            if total > 0:
                pends.append(
                    "Está sobrando capital na Nota de dotação, (R$ %0.2f). " % total
                )
            elif total < 0:
                pends.append(
                    "Está faltando capital na Nota de dotação, (R$ %0.2f). "
                    % (total * -1)
                )

        out = ""
        for pend in pends:
            out += pend
        return out

    @classmethod
    def get_soma_produto(items):
        """
        Realiza o cálculo do valor de cada produto no processo.
        Valor do Produto: quantidade * valor estimado = vProdn
        vTotalProd = vProd1 + vProd2 + ... vProdn
        """
        total = 0
        for pp in ProdutoProcesso.objects.filter(pk__in=items):
            total += pp.produto.quantidade * pp.valor_unitario_estimado
        return total

    def pendencia_produto_nd(processo_pk):
        """
        Este método verifica se existe algum produto adicionado ao processo.
        E também se todos os campos de cada produto estão preenchidos.
        @return boolean - True: quando hover pendência. False: quando não houver pendência.
        """
        produto_processo = ProdutoProcesso.objects.filter(
            processo_aquisicao=processo_pk
        )
        if produto_processo:
            for pp in produto_processo:
                if (
                    pp.produto is None
                    or pp.nota_dotacao is None
                    or pp.processo_aquisicao is None
                    or pp.quantidade is None
                    or pp.valor_unitario_estimado is None
                ):
                    return True
        else:
            return True
        return False

    @classmethod
    def pendencia_valor_produtos_nd(processo_pk):
        """
        Este método verifica se a soma dos valores de todos os produtos do processo é igual ao valor da nota de dotação.
        @return boolean - True: quando hover pendência. False: quando não houver pendência.
        """
        if (
            ProdutoProcesso.get_soma_produto(
                ProdutoProcesso.objects.filter(processo_aquisicao=processo_pk)
            )
            == ProdutoProcesso.objects.filter(processo_aquisicao=processo_pk)[
                0
            ].nota_dotacao.valor
        ):
            return False
        return True

    valor_total = property(_valor_total)

    def get_quantidade_usada(self):
        from adm.cpl.models import ProdutoVencedor

        quantidade = 0
        try:
            for ne in NEAquisicaoRegistroPreco.objects.filter(
                Q(
                    credor__in=ProdutoVencedor.objects.filter(
                        Q(licitacao=self.processo_aquisicao.licitacao.get().pk)
                        & Q(produto_processo=self.pk)
                    )
                )
                & Q(produto_processo=self.pk)
            ):
                quantidade += ne.quantidade
        except Exception:
            pass
        try:
            quantidade = NEAquisicao.objects.get(
                Q(
                    credor__in=ProdutoVencedor.objects.filter(
                        Q(licitacao=self.processo_aquisicao.licitacao.get().pk)
                        & Q(produto_processo=self.pk)
                    )
                )
                & Q(produto_processo=self.pk)
            ).produto_processo.quantidade
        except Exception:
            pass
        return quantidade


class NEAquisicao(NE):
    def save(self, force_insert=False, force_update=False):
        log = getLogger("NEAquisicao:Model")
        try:
            self.valor = self.get_calculo_valor()
            super(NEAquisicao, self).save(force_insert, force_update)
        except Exception as e:
            log.exception(e)

    def get_calculo_valor(self):
        return self.credor.get_calculo_valor_ne()


class NEAquisicaoRegistroPreco(NE):
    quantidade = models.IntegerField(default=0)

    class Meta:
        db_table = "compras_neaquisicaorp"

    def save(self, force_insert=False, force_update=False):
        log = getLogger("NEAquisicaoRegistroPreco:Model")
        try:
            if (
                self.produto_processo.quantidade
                - (self.produto_processo.get_quantidade_usada() + self.quantidade)
            ) >= 0:
                self.valor = self.get_calculo_valor()
                super(NEAquisicaoRegistroPreco, self).save(force_insert, force_update)
            else:
                raise Exception("Todos produtos já foram empenhados!")
        except Exception as e:
            log.exception(e)
            raise e

    def get_calculo_valor(self):
        return self.quantidade * self.produto_processo.valor_unitario
