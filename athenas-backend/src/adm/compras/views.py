# -*- coding: utf-8 -*-
import time
from datetime import date

from adm.compras.models import (
    NEAquisicao,
    NEAquisicaoRegistroPreco,
    NotaDotacao,
    ProcessoAquisicao,
    ProdutoProcesso,
)
from adm.contabilidade.models import NE, FonteRecurso, Produto
from adm.contabilidade.views import ContabFonteRecurso
from adm.cpl.models import ProdutoVencedor
from adm.cpl.views import CPLProdutoVencedor
from adm.eproc.models import Processo
from adm.eproc.views import CustonAutocomplete as EPAutocomplete
from adm.eproc.views import EPProcesso
from adm.mto.models import NaturezaDespesa
from adm.mto.views import MTONaturezaDespesa
from contrib import extjs
from contrib.utils import get_json_engine
from django import forms
from django.conf import settings
from django.db.models.query_utils import Q
from rh.models import Servidor
from standard.views import AutoCompleteField

json = get_json_engine()


class CustonAutocomplete(EPAutocomplete):

    def autocomplete(self, args=[]):
        obj = {}
        q = None
        qs = []
        model = None
        flag = False

        if "model" in self.request.POST:
            if self.request.POST["model"] == "Produto":
                model = Produto
                if "query" in self.request.POST:
                    qs.append(Q(descricao__icontains=self.request.POST["query"]))
                else:
                    qs.append(Q(pk=int(self.request.POST["pk"])))
            if self.request.POST["model"] == "FonteRecurso":
                model = FonteRecurso
                if "query" in self.request.POST:
                    qs.append(Q(numero__icontains=self.request.POST["query"]))
                    qs.append(Q(descricao__icontains=self.request.POST["query"]))
                else:
                    qs.append(Q(pk=int(self.request.POST["pk"])))
            if args[0] == "FonteRecurso":
                model = FonteRecurso
                if "query" in self.request.POST:
                    qs.append(Q(numero__icontains=self.request.POST["query"]))
                    qs.append(Q(descricao__icontains=self.request.POST["query"]))
                else:
                    qs.append(Q(pk=int(self.request.POST["pk"])))
            elif args[0] == "produtoprocesso":
                model = ProdutoProcesso
                if "query" in self.request.POST:
                    qs.append(Q(descricao__icontains=self.request.POST["query"]))
                    qs.append(
                        Q(produto__descricao__icontains=self.request.POST["query"])
                    )
                    qs.append(Q(subitem__numero__icontains=self.request.POST["query"]))
                    qs.append(
                        Q(subitem__descricao__icontains=self.request.POST["query"])
                    )
                    qs.append(
                        Q(
                            elemento_despesa__numero__icontains=self.request.POST[
                                "query"
                            ]
                        )
                    )
                    qs.append(
                        Q(
                            elemento_despesa__descricao__icontains=self.request.POST[
                                "query"
                            ]
                        )
                    )
                else:
                    qs.append(Q(pk=int(self.request.POST["pk"])))
            elif args[0] == "produtovencedor":
                model = ProdutoVencedor
                if "query" in self.request.POST:
                    qs.append(
                        Q(
                            participante__pessoa__nome__icontains=self.request.POST[
                                "query"
                            ]
                        )
                    )
                    qs.append(
                        Q(licitacao__numero__icontains=self.request.POST["query"])
                    )
                else:
                    qs.append(Q(pk=int(self.request.POST["pk"])))
            else:
                EPAutocomplete.autocomplete(self, args)
                flag = True

        if model:
            for qn in qs:
                q = qn if q is None else Q(q | qn)
            obj["result"] = [
                {"pk": row.pk, "description": str(row)}
                for row in model.objects.filter(q)
            ]

        if not flag:
            self.response["content-type"] = "text/javascript"
            self.response.write(json.encode(obj))


class COMPRASProcessoAquisicao(EPProcesso, CustonAutocomplete):

    def create(self, args=[]):
        obj = {"success": True, "message": ""}
        processo = ProcessoAquisicao(
            numero=self.request.POST["numero"],
            titulo=self.request.POST["titulo"],
            dt=date.fromtimestamp(
                time.mktime(
                    time.strptime(
                        self.request.POST["data"],
                        getattr(settings, "DATE_INPUT_FORMATS")[0],
                    )
                )
            ),
            interessado=Servidor.objects.get(pk=int(self.request.POST["interessado"])),
            descricao=self.request.POST["descricao"],
            orcamento=self.request.POST["orcamento"],
        )
        try:
            processo.save()
            obj.update(pk=processo.pk)
        except Exception as e:
            obj["message"] = "Não foi possível gravar as informações!"
            obj["success"] = False
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def add_item(self, args=[]):
        obj = {"success": True, "message": ""}
        produto_processo = ProdutoProcesso(
            produto=Produto.objects.get(pk=int(self.request.POST["produto"])),
            processo_aquisicao=ProcessoAquisicao.objects.get(
                pk=int(self.request.POST["processo_aquisicao"])
            ),
            quantidade=self.request.POST["quantidade"],
            valor_unitario_estimado=self.request.POST["valor_unitario_estimado"],
            descricao=self.request.POST["descricao"],
        )
        try:
            produto_processo.save()
        except Exception as e:
            obj["message"] = str(e)
            obj["success"] = False
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update_item(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            pp = ProdutoProcesso.objects.get(pk=int(self.request.POST["pk"]))
        except Exception as e:
            obj["message"] = (
                "Não consegui encontrar informações do Produto de Processo!"
            )
            obj["success"] = False
            self.log.exception(e)
        else:
            try:
                pp.produto = Produto.objects.get(pk=int(self.request.POST["produto"]))
                pp.processo_aquisicao = ProcessoAquisicao.objects.get(
                    pk=int(self.request.POST["processo_aquisicao"])
                )
                pp.quantidade = self.request.POST["quantidade"]
                pp.valor_unitario_estimado = self.request.POST[
                    "valor_unitario_estimado"
                ]
                pp.descricao = self.request.POST["descricao"]
                pp.save()
            except Exception as e:
                obj["message"] = "Não consegui gravar dados da edição!"
                obj["success"] = False
                self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def delete_items(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            ProdutoProcesso.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            ).delete()
        except Exception as e:
            obj["message"] = "Não consegui remover Produto Processo!"
            obj["success"] = False
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def set_nd(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            nds = NotaDotacao.objects.filter(pk__in=self.request.POST.getlist("nd"))
            items = self.request.POST.getlist("items")
            for item in ProdutoProcesso.objects.filter(pk__in=items):
                [item.nota_dotacao.add(nd) for nd in nds]
        except Exception as e:
            obj.update(message=str(e))
            obj.update(success=False)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def unset_nd(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            items = self.request.POST.getlist("items")
            for item in ProdutoProcesso.objects.filter(pk__in=items):
                item.nota_dotacao.clear()
        except Exception:
            obj.update(success=False)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_produto_from(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        produtos = ProdutoProcesso.objects.filter(
            processo_aquisicao=int(self.request.POST["processo_aquisicao"])
        )

        if "query" in self.request.POST:
            produtos = produtos.filter(
                Q(
                    Q(nota_dotacao__numero__icontains=self.request.POST["query"])
                    | Q(programa_trabalho__icontains=self.request.POST["query"])
                    | Q(fonte_recurso__icontains=self.request.POST["query"])
                    | Q(natureza_despesa__icontains=self.request.POST["query"])
                )
            )

        obj["totalRows"] = produtos.count()

        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        end = (
            start + int(self.request.POST["limit"])
            if "limit" in self.request.POST
            else 1000
        )

        if "sort" in self.request.POST:
            if self.request.POST["dir"] == "ASC":
                produtos = produtos.order_by("%s" % self.request.POST["sort"])
            else:
                produtos = produtos.filter(
                    processo_aquisicao=int(self.request.POST["processo"])
                )

        context = getattr(settings, "CONTEXT", "")
        try:
            for item in produtos[start:end]:
                info = {
                    "status": [
                        {
                            "icon": "/%s/static/adm/images/%s"
                            % (context, "ok.png" if item.is_ok() else "pendente.png"),
                            "title": (
                                "Tudo ok" if item.is_ok() else item.get_pendencias()
                            ),
                            "alt": "Tudo ok" if item.is_ok() else item.get_pendencias(),
                        }
                    ],
                    "produto_pk": item.produto.pk,
                    "produto": str(item.produto),
                    "qnt": "%d %s" % (int(item.quantidade), item.produto.unidade.sigla),
                    "valor_estimado": (
                        int(item.quantidade) * float(item.valor_unitario_estimado)
                    ),
                    "valor_estimado_unitario": float(item.valor_unitario_estimado),
                    "nd": "",
                    "pk": item.pk,
                    "descricao": item.descricao,
                }

                if item.nota_dotacao.count() > 0:
                    nds = ""
                    for nd in item.nota_dotacao.all():
                        nds += ", " if len(nds) > 0 else ""
                        nds += str(nd)
                    info.update(nd=nds)
                else:
                    info.update(nd="SEM ND")

                obj["result"].append(info)
        except Exception as e:
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get(self, args=[]):
        code = {"result": []}

        try:
            obj = Processo.objects.get(pk=int(self.request.POST["pk"]))

            code["result"].append({"pk": obj.pk, "id": obj.pk, "description": str(obj)})
        except Exception:
            pass

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.encode(code))


class COMPRASNotaDotacao(extjs.ExtCrud, CustonAutocomplete):
    class Form(forms.ModelForm):
        natureza_despesa = AutoCompleteField(
            model=NaturezaDespesa,
            controller=MTONaturezaDespesa,
            label="Nat. de Despesa",
        )
        fonte_recurso = AutoCompleteField(
            model=FonteRecurso, controller=ContabFonteRecurso, label="Fonte do Recurso"
        )

        class Meta:
            exclude = []
            model = NotaDotacao

    titles = {
        "PANEL": "Notas de Dotações",
        "LIST": "Gerenciador de Nota de Dotação",
        "NEW": "Novo(a) Nota de Dotação",
        "EDIT": "Editando um(a) Nota de Dotação",
        "DELETE": "Removendo um(a) Nota de Dotação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
            {
                "header": "Data",
                "sortable": True,
                "dataIndex": "data",
                "toSearch": False,
            },
            {
                "header": "Fonte de Recurso",
                "sortable": True,
                "dataIndex": "fonte_recurso",
                "toSearch": False,
            },
            {
                "header": "Natureza de Despesa",
                "sortable": True,
                "dataIndex": "natureza_despesa",
                "toSearch": False,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "toSearch": False,
            },
            {
                "header": "Programa de Trabalho",
                "sortable": True,
                "dataIndex": "programa_trabalho",
                "toSearch": False,
            },
            {
                "header": "Valor",
                "sortable": True,
                "dataIndex": "valor",
                "toSearch": False,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class COMPRASProdutoProcesso(extjs.ExtCrud):
    class Form(forms.ModelForm):
        model = ProdutoProcesso

    titles = {
        "PANEL": "Produto processo",
        "LIST": "Gerenciador de Produto processos",
        "NEW": "Novo(a) Produto processo",
        "EDIT": "Editando um(a) Produto processo",
        "DELETE": "Removendo um(a) Produto processo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class COMPRASNe(extjs.ExtCrud):
    class Form(forms.ModelForm):
        credor = AutoCompleteField(
            model=ProdutoVencedor, controller=CPLProdutoVencedor, label="Credor"
        )
        produto_processo = AutoCompleteField(
            model=ProdutoProcesso,
            controller=COMPRASProdutoProcesso,
            label="Produto processo",
        )

        class Meta:
            exclude = []
            model = NE

    titles = {
        "PANEL": "NE",
        "LIST": "Gerenciador de NEs",
        "NEW": "Novo(a) NE",
        "EDIT": "Editando um(a) NE",
        "DELETE": "Removendo um(a) NE",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class COMPRASNeAquisicao(COMPRASNe, CustonAutocomplete):
    class Form(forms.ModelForm):
        credor = AutoCompleteField(
            model=ProdutoVencedor, controller=CPLProdutoVencedor, label="Credor"
        )
        produto_processo = AutoCompleteField(
            model=ProdutoProcesso,
            controller=COMPRASProdutoProcesso,
            label="Produto processo",
        )

        class Meta:
            exclude = []
            model = NEAquisicao

    titles = {
        "PANEL": "Notas de Empenhos",
        "LIST": "Gerenciador de Nota de Empenho",
        "NEW": "Novo(a) Nota de Empenho",
        "EDIT": "Editando um(a) Nota de Empenho",
        "DELETE": "Removendo um(a) Nota de Empenho",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
            {
                "header": "Data",
                "sortable": True,
                "dataIndex": "data",
                "toSearch": False,
            },
            {
                "header": "Fonte de Recurso",
                "sortable": True,
                "dataIndex": "fonte_recurso",
                "toSearch": False,
            },
            {
                "header": "Natureza de Despesa",
                "sortable": True,
                "dataIndex": "natureza_despesa",
                "toSearch": False,
            },
            {
                "header": "Número",
                "sortable": True,
                "dataIndex": "numero",
                "toSearch": False,
            },
            {
                "header": "Programa de Trabalho",
                "sortable": True,
                "dataIndex": "programa_trabalho",
                "toSearch": False,
            },
            {
                "header": "Valor",
                "sortable": True,
                "dataIndex": "valor",
                "toSearch": False,
            },
        ]
        obj = self._apply_to_search_for_columns_grid(obj)
        self.response.write(json.encode(obj))


class COMPRASNeAquisicaoRegistroPreco(COMPRASNe, CustonAutocomplete):
    class Form(forms.ModelForm):
        credor = AutoCompleteField(
            model=ProdutoVencedor, controller=CPLProdutoVencedor, label="Credor"
        )
        produto_processo = AutoCompleteField(
            model=ProdutoProcesso,
            controller=COMPRASProdutoProcesso,
            label="Produto processo",
        )

        class Meta:
            exclude = []
            model = NEAquisicaoRegistroPreco

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "processo":
            obj = self.get_store_processo(args)
        elif args[0] == "vencedor":
            obj = self.get_store_vencedor(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_processo(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        processo = ProcessoAquisicao.objects.filter(excluido_por=None, orcamento=2)
        obj["totalRows"] = processo.count()
        start = int(self.request.POST["start"]) if "start" in self.request.POST else 0
        end = (
            start + int(self.request.POST["limit"])
            if "limit" in self.request.POST
            else 1000
        )

        if "sort" in self.request.POST:
            if self.request.POST["dir"] == "ASC":
                processo = processo.order_by("%s" % self.request.POST["sort"])
            else:
                processo = processo.order_by("-%s" % self.request.POST["sort"])
        processo = processo[start:end]

        for p in processo:
            obj["result"].append(
                {
                    "codigo": p.pk,
                    "numero": p.numero_cache,
                    "titulo": p.titulo,
                    "interessado": str(p.interessado.pessoa_fisica),
                }
            )
        return obj

    def get_store_vencedor(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            for produto_vencedor in ProdutoVencedor.objects.filter(
                licitacao=ProcessoAquisicao.objects.get(
                    pk=self.request.POST["processo"]
                )
                .licitacao.get()
                .pk
            ):
                produto_processo = produto_vencedor.produto_processo.all()
                obj["totalRows"] = produto_processo.count()
                start = (
                    int(self.request.POST["start"])
                    if "start" in self.request.POST
                    else 0
                )
                end = (
                    start + int(self.request.POST["limit"])
                    if "limit" in self.request.POST
                    else 1000
                )
                try:
                    translate = {"nome": "descricao"}
                    if (
                        "sort" in self.request.POST
                        and self.request.POST["sort"] in translate
                    ):
                        if self.request.POST["dir"] == "ASC":
                            produto_processo = produto_processo.order_by(
                                "%s" % translate.get(self.request.POST["sort"]), "pk"
                            )
                        else:
                            produto_processo = produto_processo.order_by(
                                "-%s" % translate.get(self.request.POST["sort"]), "pk"
                            )
                    else:
                        produto_processo = produto_processo.order_by("pk")
                    produto_processo = produto_processo[start:end]
                except Exception as e:
                    self.log.exception(e)
                for pp in produto_processo:
                    obj["result"].append(
                        {
                            "codigo": pp.pk,
                            "vencedor": str(produto_vencedor.participante.pessoa.nome),
                            "vencedor_cod": produto_vencedor.pk,
                            "produto": str(pp.produto.descricao),
                            "produto_cod": pp.pk,
                            "quantidade": "%d %s"
                            % (int(pp.quantidade), pp.produto.unidade.sigla),
                            "valor_unitario": (
                                str(pp.valor_unitario) if pp.valor_unitario else "0.00"
                            ),
                            "valor_total": str(pp.valor_total),
                            "usado": pp.get_quantidade_usada(),
                        }
                    )
        except Exception as e:
            self.log.exception(e)
        return obj


class COMPRASGemp(extjs.ExtWidget):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.adm.compras.Gemp()")

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "ne":
            obj = self.get_store_ne(args)
        elif args[0] == "subitem":
            obj = self.get_store_subitem(args)
        elif args[0] == "item":
            obj = self.get_store_item(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_ne(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            nes = NE.objects.all()
            obj["totalRows"] = nes.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )
            try:
                translate = {
                    "nome": "servidor__pessoa_fisica__nome",
                    "dt_realizacao": "data_realizacao",
                }
                if (
                    "sort" in self.request.POST
                    and self.request.POST["sort"] in translate
                ):
                    if self.request.POST["dir"] == "ASC":
                        nes = nes.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        nes = nes.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    nes = nes.order_by("-data")
                nes = nes[start:end]
            except Exception as e:
                self.log.exception(e)

            for ne in nes:
                status = {"icon": "", "title": "Status", "alt": "Status"}
                try:
                    controller = (
                        "COMPRASNeAquisicao"
                        if ne.neaquisicao
                        else "COMPRASNeAquisicaoRegistroPreco"
                    )
                except Exception:
                    controller = "COMPRASNeAquisicaoRegistroPreco"
                try:
                    quantidade = ne.neaquisicaoregistropreco.quantidade
                except Exception:
                    quantidade = ne.produto_processo.quantidade
                obj["result"].append(
                    {
                        "status": [status],
                        "codigo": ne.pk,
                        "numero": ne.numero,
                        "processo": ne.credor.licitacao.processo.numero_cache,
                        "licitacao": ne.credor.licitacao.numero,
                        "credor": str(ne.credor.participante.pessoa),
                        "credor_pk": ne.credor.pk,
                        "data": ne.data.strftime("%d/%m/%Y") if ne.data else "",
                        "modalidade": str(ne.get_modalidade_display()),
                        "modalidade_pk": str(ne.modalidade),
                        "valor": str(ne.valor),
                        "controller": controller,
                        "produto": str(ne.produto_processo.produto.descricao),
                        "quantidade": quantidade,
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_subitem(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            codigos = []
            pp_obj = ProdutoVencedor.objects.get(
                pk=self.request.POST["produto_vencedor"]
            ).produto_processo.all()
            obj["totalRows"] = pp_obj.count()
            for pp in pp_obj:
                if pp.produto.subitem.pk not in codigos:
                    codigos.append(pp.produto.subitem.pk)
                    obj["result"].append(
                        {
                            "codigo": pp.produto.subitem.pk,
                            "numero": str(pp.produto.subitem.numero),
                            "nome": str(pp.produto.subitem.descricao),
                            "elemento": str(pp.produto.subitem.elemento_despesa.numero),
                            "elemento_pk": pp.produto.subitem.elemento_despesa.pk,
                        }
                    )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_item(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            pp_obj = ProdutoProcesso.objects.filter(
                pk__in=ProdutoProcesso.objects.filter(
                    Q(produto__subitem__pk=self.request.POST["sub_item"])
                    & Q(vencedor_produto=self.request.POST["produto_vencedor"])
                )
                .values("pk")
                .distinct()
            )
            obj["totalRows"] = pp_obj.count()
            for pp in pp_obj:
                obj["result"].append(
                    {
                        "codigo": pp.pk,
                        "nome": str(pp.produto),
                        "unidade": str(pp.produto.unidade),
                        "descricao": str(pp.descricao),
                        "quantidade": "%d %s"
                        % (int(pp.quantidade), pp.produto.unidade.sigla),
                        "valor_unitario": str(pp.valor_unitario),
                        "valor_total": str(pp.valor_total),
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def update(self, args=[]):
        result = json.decode(self.request.POST["result"])
        if isinstance(result, dict):
            result = [result]
        try:
            for r in result:
                ProdutoProcesso.objects.filter(pk=int(r.get("codigo"))).update(
                    descricao=r.get("descricao")
                )
        except Exception as e:
            self.log.debug(e)
