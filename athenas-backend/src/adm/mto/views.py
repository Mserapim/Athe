# -.- coding: utf-8 -.-
from adm.mto.models import (
    CategoriaEconomica,
    ElementoDespesa,
    ElementoDespesaSubItem,
    GrupoDespesa,
    ModalidadeAplicacao,
    NaturezaDespesa,
)
from contrib import extjs
from contrib.utils import get_json_engine
from django import forms
from standard.views import AutoCompleteField

json = get_json_engine()


class MTOGrupoDespesa(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTOGrupoDespesa"
        title = "Grupo de Despesa"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = GrupoDespesa

    titles = {
        "PANEL": "Grupos de Despesas",
        "LIST": "Gerenciador de Grupo de Despesa",
        "NEW": "Novo(a) Grupo de Despesa",
        "EDIT": "Editando um(a) Grupo de Despesa",
        "DELETE": "Removendo um(a) Grupo de Despesa",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class MTOModalidadeAplicacao(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTOModalidadeAplicacao"
        title = "Modalidade de Aplicação"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = ModalidadeAplicacao

    titles = {
        "PANEL": "Modalidades de Aplicações",
        "LIST": "Gerenciador de Modalidade de Aplicação",
        "NEW": "Novo(a) Modalidade de Aplicação",
        "EDIT": "Editando um(a) Modalidade de Aplicação",
        "DELETE": "Removendo um(a) Modalidade de Aplicação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class MTOCategoriaEconomica(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTOCategoriaEconomica"
        title = "Categoria Econômica"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = CategoriaEconomica

    titles = {
        "PANEL": "Categorias Econômicas",
        "LIST": "Gerenciador de Categoria Econômica",
        "NEW": "Novo(a) Categoria Econômica",
        "EDIT": "Editando um(a) Categoria Econômica",
        "DELETE": "Removendo um(a) Categoria Econômica",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class MTOElementoDespesa(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTOElementoDespesa"
        title = "Elemento de Despesa"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = ElementoDespesa

    titles = {
        "PANEL": "Elementos de Despesas",
        "LIST": "Gerenciador de Elemento de Despesa",
        "NEW": "Novo(a) Elemento de Despesa",
        "EDIT": "Editando um(a) Elemento de Despesa",
        "DELETE": "Removendo um(a) Elemento de Despesa",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class MTOElementoDespesaCuston(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.adm.mto.Gerenciador()")

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "elemento_despesa":
            obj = self.get_store_elemento_despesa()
        if args[0] == "elemento_despesa_subitem":
            obj = self.get_store_elemento_despesa_subitem()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_elemento_despesa(self):
        obj = {"totalRows": 0, "result": []}
        try:
            eld = ElementoDespesa.objects.all()
            obj["totalRows"] = eld.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )

            try:
                if "sort" in self.request.POST:
                    if self.request.POST["dir"] == "ASC":
                        eld = eld.order_by("%s" % self.request.POST["sort"])
                    else:
                        eld = eld.order_by("-%s" % self.request.POST["sort"])
                eld = eld[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in eld:
                obj["result"].append(
                    {
                        "codigo": og.pk,
                        "numero": og.numero,
                        "descricao": str(og.descricao),
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_elemento_despesa_subitem(self):
        obj = {"totalRows": 0, "result": []}
        try:
            eld = ElementoDespesaSubItem.objects.all()
            obj["totalRows"] = eld.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )

            try:
                if "sort" in self.request.POST:
                    if self.request.POST["dir"] == "ASC":
                        eld = eld.order_by("%s" % self.request.POST["sort"])
                    else:
                        eld = eld.order_by("-%s" % self.request.POST["sort"])
                eld = eld[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in eld:
                obj["result"].append(
                    {
                        "codigo": og.pk,
                        "numero": og.numero,
                        "descricao": str(og.descricao),
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj


class MTOElementoDespesaSubItem(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTOElementoDespesaSubItem"
        title = "SubItem do Elemento de Despesa"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        elemento_despesa = AutoCompleteField(
            model=ElementoDespesa,
            # father="MTOElementoDespesa",
            controller=MTOElementoDespesa,
            label="Elemento de Despesa",
        )

        class Meta:
            exclude = []
            model = ElementoDespesaSubItem

    titles = {
        "PANEL": "SubItems dos Elementos de Despesas",
        "LIST": "Gerenciador de SubItem do Elemento de Despesa",
        "NEW": "Novo(a) SubItem do Elemento de Despesa",
        "EDIT": "Editando um(a) SubItem do Elemento de Despesa",
        "DELETE": "Removendo um(a) SubItem do Elemento de Despesa",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def delete(self, args=[]):
        obj = {"count": 0, "success": 0, "failure": 0, "faileds": []}

        for pkinsc in self.request.POST.getlist("subitem"):
            obj["count"] += 1

            try:
                ElementoDespesaSubItem.objects.get(pk=int(pkinsc)).delete()
                obj["success"] += 1
            except Exception:
                obj["failure"] += 1
                obj["faileds"].append(pkinsc)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class MTONaturezaDespesa(extjs.ExtCrud):
    class InstallMeta:
        controller = "MTONaturezaDespesa"
        title = "Natureza Despesa"
        node_menu = "mto"
        install = True

    class Form(forms.ModelForm):
        grupo_despesa = AutoCompleteField(
            model=GrupoDespesa,
            father="MTONaturezaDespesa",
            controller=MTOGrupoDespesa,
            label="Grupo de Despesa",
        )
        modalidade_aplicacao = AutoCompleteField(
            model=ModalidadeAplicacao,
            father="MTONaturezaDespesa",
            controller=MTOModalidadeAplicacao,
            label="Modalidade de Aplicação",
        )
        categoria_economica = AutoCompleteField(
            model=CategoriaEconomica,
            father="MTONaturezaDespesa",
            controller=MTOCategoriaEconomica,
            label="Categoria Econômica",
        )
        elemento_despesa = AutoCompleteField(
            model=ElementoDespesa,
            father="MTONaturezaDespesa",
            controller=MTOElementoDespesa,
            label="Elemento Despesa",
        )

        class Meta:
            exclude = []
            model = NaturezaDespesa

    titles = {
        "PANEL": "Natureza Despesa",
        "LIST": "Gerenciador de Natureza Despesa",
        "NEW": "Novo(a) Natureza Despesa",
        "EDIT": "Editando um(a) Natureza Despesa",
        "DELETE": "Removendo um(a) Natureza Despesa",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


#    def get_columns_grid(self,args=[]):
#        obj = [
#            {"header": "Chave", "sortable": True, "dataIndex": "id", "toSearch": False},
#            {"header": "Categoria Econômica", "sortable": True, "dataIndex": "categoria_economica", "toSearch": True},
#            {"header": "Elemento Despesa", "sortable": True, "dataIndex": "elemento_despesa", "toSearch": True},
#            {"header": "Grupo Despesa", "sortable": True, "dataIndex": "grupo_despesa", "toSearch": True},
#            {"header": "Modalidade Aplicação", "sortable": True, "dataIndex": "modalidade_aplicacao", "toSearch": True}
#        ]
#        obj = self._apply_to_search_for_columns_grid(obj)
#        self.response.write(json.encode(obj))

#    def autocomplete(self, args=[]):
#        obj = {"result": []}
#        if args[0] == 'GrupoDespesa':
#            for row in GrupoDespesa.objects.filter(
#                Q(numero__icontains = self.request.POST["query"]) |
#                Q(descricao__icontains = self.request.POST['query'])
#            ):
#                obj["result"].append({
#                    "id": row.pk,
#                    "description": str(row)
#                })
#        if args[0] == 'ModalidadeAplicacao':
#            for row in ModalidadeAplicacao.objects.filter(
#                Q(numero__icontains = self.request.POST["query"]) |
#                Q(descricao__icontains = self.request.POST['query'])
#            ):
#                obj["result"].append({
#                    "id": row.pk,
#                    "description": str(row)
#                })
#        if args[0] == 'CategoriaEconomica':
#            for row in CategoriaEconomica.objects.filter(
#                Q(numero__icontains = self.request.POST["query"]) |
#                Q(descricao__icontains = self.request.POST['query'])
#            ):
#                obj["result"].append({
#                    "id": row.pk,
#                    "description": str(row)
#                })
#        if args[0] == 'ElementoDespesa':
#            for row in ElementoDespesa.objects.filter(
#                Q(numero__icontains = self.request.POST["query"]) |
#                Q(descricao__icontains = self.request.POST['query'])
#            ):
#                obj["result"].append({
#                    "id": row.pk,
#                    "description": str(row)
#                })
#        if args[0] == 'ElementoDespesaSubItem':
#            for row in ElementoDespesaSubItem.objects.filter(
#                Q(numero__icontains = self.request.POST["query"]) |
#                Q(descricao__icontains = self.request.POST['query'])
#            ):
#                obj["result"].append({
#                    "id": row.pk,
#                    "description": str(row)
#                })
#
#        self.response['content-type'] = "text/javascript"
#        self.response.write(json.encode(obj))
