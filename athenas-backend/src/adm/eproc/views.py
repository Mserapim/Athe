# -*- coding: utf-8 -*-
import time
from datetime import date

from adm.contabilidade.models import Produto
from adm.eproc.models import Pagina, Processo
from contrib.extjs import ExtWidget
from contrib.utils import get_json_engine
from django.db.models import Q
from rh.models import Servidor

json = get_json_engine()


class CustonAutocomplete(ExtWidget):

    def autocomplete(self, args=[]):
        obj = {"result": []}

        model = None
        q = None
        qs = []

        if "model" in self.request.POST:
            if self.request.POST["model"] == "Servidor":
                model = Servidor
                qs.append(Q(matricula__icontains=self.request.POST["query"]))
                qs.append(Q(pessoa_fisica__nome__icontains=self.request.POST["query"]))
                qs.append(Q(pessoa_fisica__cpf__icontains=self.request.POST["query"]))
            if self.request.POST["model"] == "Produto":
                model = Produto
                qs.append(Q(descricao__icontains=self.request.POST["query"]))

            for qn in qs:
                q = qn if q is None else Q(q | qn)
            obj["result"] = [
                {"pk": row.pk, "description": str(row)}
                for row in model.objects.filter(q)
            ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class EPProcesso(CustonAutocomplete):

    def create(self, args=[]):
        obj = {"success": True, "message": ""}
        processo = Processo(
            numero=self.request.POST["numero"],
            titulo=self.request.POST["titulo"],
            dt=date.fromtimestamp(
                time.mktime(time.strptime(self.request.POST["data"], "%Y-%m-%d"))
            ),
            interessado=Servidor.objects.get(pk=int(self.request.POST["interessado"])),
            descricao=self.request.POST["descricao"],
        )
        try:
            processo.save()
        except Exception as e:
            obj["message"] = "Não foi possível gravar as informações!"
            obj["success"] = False
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": True, "message": ""}

        try:
            processo = Processo.objects.get(pk=int(self.request.POST["processo"]))
        except Exception as e:
            obj["message"] = "Não consegui encontrar informações do Processo!"
            obj["success"] = False
            self.log.exception(e)
        else:
            try:
                processo.descricao = self.request.POST["descricao"]
                processo.save()
            except Exception as e:
                obj["message"] = "Não consegui gravar dados da edição!"
                obj["success"] = False
                self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            Processo.objects.filter(pk=int(self.request.POST["processo"])).update(
                excluido_por=self.request.user
            )
        except Exception as e:
            obj["message"] = "Não consegui remover Processo!"
            obj["success"] = False
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class EPGerenciador(CustonAutocomplete):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.adm.eproc.Gerenciador()")

    def remove(self, args=[]):
        obj = {}

        try:
            Processo.objects.filter(
                pk__in=self.request.POST.getlist("processos")
            ).update(excluido_por=self.request.user)
        except Exception:
            obj.update(success=False)
            obj.update(msg="Ocorreu um erro removendo os processos selecionados.")
        else:
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        processo = Processo.objects.filter(excluido_por=None)

        if "query" in self.request.POST:
            processo = processo.filter(
                Q(
                    Q(numero__icontains=self.request.POST["query"])
                    | Q(titulo__icontains=self.request.POST["query"])
                    | Q(
                        interessado__pessoa_fisica__nome__icontains=self.request.POST[
                            "query"
                        ]
                    )
                )
            )

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
                    "status": p.get_type_information(),
                    "numero": p.numero_cache,
                    "ano": p.dt.year,
                    "titulo": p.titulo,
                    "interessado": str(p.interessado.pessoa_fisica),
                    "controller": p.get_controller(),
                    "values": {
                        "pk": p.pk,
                        "numero": p.numero,
                        "data": p.dt.strftime("%d/%m/%Y"),
                        "titulo": p.titulo,
                        "interessado": p.interessado.pk,
                        "descricao": p.descricao,
                        "orcamento": (
                            p.processoaquisicao.orcamento
                            if hasattr(p, "processoaquisicao")
                            else None
                        ),
                    },
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_from(self, args=[]):
        obj = {}

        # TODO: Listar as páginas do processo), 'pk'

        obj = {"totalRows": 0, "result": []}
        try:
            if "query" in self.request.POST:
                pagina = Pagina.objects.filter(
                    Q(processo=int(self.request.POST["processo"]))
                    & Q(
                        Q(numero__icontains=self.request.POST["query"])
                        | Q(processo__numero__icontains=self.request.POST["query"])
                        | Q(processo__titulo__icontains=self.request.POST["query"])
                        | Q(
                            processo__interessado__pessoa_fisica__nome__icontains=self.request.POST[
                                "query"
                            ]
                        )
                    )
                )
            else:
                pagina = Pagina.objects.filter(
                    processo=int(self.request.POST["processo"])
                )
            obj["totalRows"] = pagina.count()
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
                        pagina = pagina.order_by("%s" % self.request.POST["sort"])
                    else:
                        pagina = pagina.order_by("-%s" % self.request.POST["sort"])
                pagina = pagina[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in pagina:
                obj["result"].append(
                    {
                        "numero": og.numero,
                        "processo": og.processo,
                    }
                )
        except Exception as e:
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
