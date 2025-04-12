# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.db.models import Q

from contrib import extjs
from contrib.decorator import login_required
from contrib.utils import get_json_engine
from rh.gfp.models import Evento, FolhaEvento
from rh.models import PessoaFisica, Publicacao, Servidor
from rh.pensao.models import (
    Pensao,
    PensaoAlimenticia,
    PensaoAlimenticiaEvento,
    PensaoFolhaEvento,
    PensaoMorte,
    PensaoMorteEvento,
)
from rh.views import RHPessoaFisica, RHPublicacao, RHServidor
from standard.views import AutoCompleteField

json = get_json_engine()


class PENSAOPensao(extjs.ExtCrud):

    class Form(forms.ModelForm):
        servidor = AutoCompleteField(model=Servidor, label="Servidor")
        pensionista = AutoCompleteField(model=PessoaFisica, label="Pensionista")
        publicacao = AutoCompleteField(model=Publicacao, label="Publicação")

        class Meta:
            exclude = []
            model = Pensao

    titles = {
        "PANEL": "Pensão",
        "LIST": "Gerenciador de Pensão",
        "NEW": "Novo(a) Pensão",
        "EDIT": "Editando um(a) Pensão",
        "DELETE": "Removendo um(a) Pensão",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 220,
            },
            {
                "header": "Pensionista",
                "sortable": True,
                "dataIndex": "pensionista",
                "toSearch": False,
                "width": 220,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "toSearch": False,
                "width": 150,
            },
            {
                "header": "Dedutível IRRF",
                "sortable": True,
                "dataIndex": "dedutivel_irrf",
                "toSearch": False,
                "width": 100,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PENSAOPensaoAlimenticia(PENSAOPensao):

    class Form(forms.ModelForm):
        servidor = AutoCompleteField(model=Servidor, label="Servidor")
        pensionista = AutoCompleteField(model=PessoaFisica, label="Beneficiário")
        publicacao = AutoCompleteField(
            model=Publicacao, label="Publicação", required=False
        )
        evento_pensao = AutoCompleteField(
            model=Evento, label="Evento pagador", required=True
        )

        class Meta:
            model = PensaoAlimenticia
            exclude = ["evento"]

    titles = {
        "PANEL": "Pensão Alimentícia",
        "LIST": "Gerenciador de Pensão Alimentícia",
        "NEW": "Novo(a) Pensão Alimentícia",
        "EDIT": "Editando um(a) Pensão Alimentícia",
        "DELETE": "Removendo um(a) Pensão Alimentícia",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Pensionista",
                "sortable": True,
                "dataIndex": "pensionista",
                "toSearch": False,
                "width": 200,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Dedutível IRRF",
                "sortable": True,
                "dataIndex": "dedutivel_irrf",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Evento",
                "sortable": True,
                "dataIndex": "evento",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Data início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Data fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "toSearch": False,
                "width": 80,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PENSAOPensaoAlimenticiaEvento(extjs.ExtCrud):

    class Form(forms.ModelForm):
        pensao_alimenticia = AutoCompleteField(
            model=PensaoAlimenticia, label="Pensão Alimentícia"
        )
        evento = AutoCompleteField(model=Evento, label="Evento")

        class Meta:
            model = PensaoAlimenticiaEvento
            exclude = ["tipo", "valor"]

    titles = {
        "PANEL": "Evento de Pensão Alimentícia",
        "LIST": "Gerenciador de Evento de Pensão Alimentícia",
        "NEW": "Novo(a) Evento de Pensão Alimentícia",
        "EDIT": "Editando um(a) Evento de Pensão Alimentícia",
        "DELETE": "Removendo um(a) Evento de Pensão Alimentícia",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Pensão Alimenticia",
                "sortable": True,
                "dataIndex": "pensao_alimenticia",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Evento",
                "sortable": True,
                "dataIndex": "evento",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Pct",
                "sortable": True,
                "dataIndex": "pct",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Valor fixo",
                "sortable": True,
                "dataIndex": "valor_fixo",
                "toSearch": False,
                "width": 80,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PENSAOPensaoMorte(PENSAOPensao):

    class Form(forms.ModelForm):
        servidor = AutoCompleteField(
            model=Servidor, controller=RHServidor, label="Servidor"
        )
        pensionista = AutoCompleteField(
            model=PessoaFisica, controller=RHPessoaFisica, label="Pensionista"
        )
        publicacao = AutoCompleteField(
            model=Publicacao,
            controller=RHPublicacao,
            label="Publicação",
            required=False,
        )

        class Meta:
            model = PensaoMorte
            exclude = ["evento"]

    titles = {
        "PANEL": "Pensão por Morte",
        "LIST": "Gerenciador Pensão por Morte",
        "NEW": "Novo(a) Pensão Pensão por Morte",
        "EDIT": "Editando um(a) Pensão Pensão por Morte",
        "DELETE": "Removendo um(a) Pensão Pensão por Morte",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Servidor",
                "sortable": True,
                "dataIndex": "servidor",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Pensionista",
                "sortable": True,
                "dataIndex": "pensionista",
                "toSearch": False,
                "width": 200,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Dedutível IRRF",
                "sortable": True,
                "dataIndex": "dedutivel_irrf",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Evento",
                "sortable": True,
                "dataIndex": "evento",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Percentagem",
                "sortable": True,
                "dataIndex": "percentagem",
                "toSearch": False,
                "width": 100,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PENSAOPensaoMorteEvento(extjs.ExtCrud):

    class Form(forms.ModelForm):
        pensao_morte = AutoCompleteField(model=PensaoMorte, label="Pensão por Morte")
        evento = AutoCompleteField(model=Evento, label="Evento")

        class Meta:
            model = PensaoMorteEvento
            exclude = ["tipo", "valor"]

    titles = {
        "PANEL": "Evento de Pensão por Morte",
        "LIST": "Gerenciador de Evento de Pensão por Morte",
        "NEW": "Novo(a) Evento de Pensão por Morte",
        "EDIT": "Editando um(a) Evento de Pensão por Morte",
        "DELETE": "Removendo um(a) Evento de Pensão por Morte",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Pensão por Morte",
                "sortable": True,
                "dataIndex": "pensao_morte",
                "toSearch": True,
                "width": 200,
            },
            {
                "header": "Evento",
                "sortable": True,
                "dataIndex": "evento",
                "toSearch": False,
                "width": 100,
            },
            {
                "header": "Pct",
                "sortable": True,
                "dataIndex": "pct",
                "toSearch": False,
                "width": 80,
            },
            {
                "header": "Valor fixo",
                "sortable": True,
                "dataIndex": "valor_fixo",
                "toSearch": False,
                "width": 80,
            },
        ]

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PENSAOGerenciadorPensao(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.rh.pensao.Gerenciador()")

    def store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "servidor":
            obj = self.get_store_servidor(args)
        if args[0] == "pensao":
            obj = self.get_store_pensao(args)
        if args[0] == "evento":
            obj = self.get_store_evento(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_servidor(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            servidores = Servidor.objects.filter(~Q(pensao_pagador=None)).distinct()
            obj["totalRows"] = servidores.count()
            start = int(self.request.POST.get("start", 0))
            end = start + int(self.request.POST.get("limit", 50))

            for s in servidores[start:end]:
                obj["result"].append(
                    {
                        "status": {
                            "icon": "/%s/static/rh/images/%s.png"
                            % (
                                getattr(settings, "CONTEXT", "athenas"),
                                "ativo" if s.ativo else "inativo",
                            ),
                            "alt": "Servidor ativo" if s.ativo else "Servidor inativo",
                            "title": (
                                "Servidor ativo" if s.ativo else "Servidor inativo"
                            ),
                        },
                        "codigo": s.pk,
                        "descricao": s,
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_pensao(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            pensoes = Pensao.objects.filter(
                Q(servidor=self.request.POST.get("servidor", 0))
                & ~Q(pk=self.request.POST.get("pensao", None))
            )
            obj["totalRows"] = pensoes.count()
            start = int(self.request.POST.get("start", 0))
            end = start + int(self.request.POST.get("limit", 50))

            for pen in pensoes[start:end]:
                try:
                    tipo = "pensaoalimenticia" if pen.pensaoalimenticia else ""
                except Exception:
                    tipo = "pensaomorte" if pen.pensaomorte else ""
                status = {
                    "icon": "/%s/static/rh/images/%s.png"
                    % (getattr(settings, "CONTEXT", "athenas"), tipo),
                    "title": (
                        "Pensão Alimentícia"
                        if tipo == "pensaoalimenticia"
                        else "Pensão por Morte"
                    ),
                    "alt": (
                        "Pensão Alimentícia"
                        if tipo == "pensaoalimenticia"
                        else "Pensão por Morte"
                    ),
                }
                obj["result"].append(
                    {
                        "status": [status],
                        "codigo": pen.pk,
                        "descricao": pen.pensionista,
                        "pensionista": pen.pensionista.pk,
                        "publicacao": pen.publicacao if pen.publicacao else "",
                        "dedutivel_irrf": "Sim" if pen.dedutivel_irrf else "Não",
                        "tipo": tipo,
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_evento(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        pensao = Pensao.objects.get(pk=int(self.request.POST.get("pensao", 0)))
        pensao = (
            pensao.pensaomorte
            if hasattr(pensao, "pensaomorte")
            else pensao.pensaoalimenticia
        )
        eventos_pensao = pensao.eventos.all()

        obj["totalRows"] = eventos_pensao.count()
        start = int(self.request.POST.get("start", 0))
        end = start + int(self.request.POST.get("limit", 50))

        for ep in eventos_pensao[start:end]:
            obj.get("result").append(
                {
                    "codigo": ep.pk,
                    "descricao": ep.evento,
                    "valor": {"tipo": ep.tipo, "valor": float(ep.valor or 0.00)},
                }
            )

        return obj

    @login_required(type="JSON")
    def associa_evento_debito(self, args=[]):
        obj = {
            "success": False,
            "message": "Nada foi feito ainda.",
            "messages": [],
            "evento_error": [],
        }

        try:
            pensao = PensaoMorte.objects.get(pk=self.request.POST.get("pensao"))
        except PensaoMorte.DoesNotExist:
            obj.update(
                message="Não consegui encontrar a pensão por morte para este benficiário."
            )
        else:
            query = FolhaEvento.objects.filter(
                pk__in=self.request.POST.getlist("folha_eventos")
            )
            for fe in query:
                try:
                    pfe = PensaoFolhaEvento(
                        pensao=pensao, folha_evento=fe, valor=fe.valor
                    )

                    pfe.save()
                    obj.update(success=True)
                except Exception as e:
                    self.log.exception(e)
                    obj.get("messages").append(e)
                    obj.get("evento_error").append(pfe.evento.numero)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def remover(self, args=[]):
        obj = {"success": True, "message": ""}
        try:
            if self.request.POST.get("model", "") == "servidor":
                for s in self.request.POST.getlist("selected"):
                    Servidor.objects.get(pk=int(s)).pensao_pagador.filter().delete()
            elif self.request.POST.get("model", "") == "pensao":
                for p in self.request.POST.getlist("selected"):
                    Pensao.objects.filter(pk=int(p)).delete()
            else:
                pensao = Pensao.objects.get(pk=self.request.POST.get("pensao"))
                if self.request.POST.get("tipo", "") == "pensaoalimenticia":
                    pensao.pensaoalimenticia.eventos.filter(
                        pk__in=self.request.POST.getlist("evento")
                    ).delete()
                else:
                    pensao.pensaomorte.eventos.filter(
                        pk__in=self.request.POST.getlist("evento")
                    ).delete()
        except Exception as e:
            obj["message"] = "Não consegui remover o Evento!"
            obj["success"] = False
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required(type="JSON")
    def copiar(self, args=[]):
        obj = {"success": True, "message": ""}
        self.log.debug("COPIAR")
        try:
            self.log.debug(self.request.POST)
            if "pensao" in self.request.POST and "evento" in self.request.POST:
                pensoes = self.request.POST.getlist("pensao")
                for pensao in pensoes:
                    pen = Pensao.objects.get(pk=pensao)
                    eventos = self.request.POST.getlist("evento")
                    for evento in eventos:
                        try:
                            self.log.debug("------------------pensao de PA")
                            if pen.pensaoalimenticia:
                                pevento = PensaoAlimenticiaEvento.objects.get(
                                    pk=int(evento)
                                )
                                novo_evento = PensaoAlimenticiaEvento(
                                    pensao_alimenticia=pevento.pensao_alimenticia,
                                    evento=pevento.evento,
                                    pct=pevento.pct,
                                    valor_fixo=pevento.valor_fixo,
                                )
                                novo_evento.save()
                                pen.pensaoalimenticia.pensaoalimenticiaevento_palimenticia.add(
                                    novo_evento
                                )
                        except Exception as e:
                            self.log.exception(e)
                            self.log.debug("----------------pensao de DV")
                            pevento = PensaoMorteEvento.objects.get(pk=int(evento))
                            novo_evento = PensaoAlimenticiaEvento(
                                pensao_alimenticia=pevento.pensao_alimenticia,
                                evento=pevento.evento,
                                pct=pevento.pct,
                                valor_fixo=pevento.valor_fixo,
                            )
                            novo_evento.save()
                            pen.pensaomorteevento.pensaomorteevento_pensaomorte.add(
                                novo_evento
                            )
        #                    for a in protocolo.anexos.all():
        #                        if not str(a.pk) in anexos: protocolo.anexos.remove(a)
        except Exception as e:
            obj["message"] = "Não consegui copiar o Evento!"
            obj["success"] = False
            self.log.exception(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
