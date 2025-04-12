#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime
from threading import Thread

from django import forms
from django.db.models import Sum
from django.db.models.query_utils import Q

from auditoria.models import LineLog
from contrib import extjs
from contrib.decorator import add_methods, tab
from contrib.utils import get_json_engine
from engine.notification.models import Notification
from cesaf.gecap.models import (
    AreaConhecimento,
    Capacitacao,
    Congresso,
    Curso,
    Evento,
    Feira,
    Inscricao,
    Investimento,
    Oficina,
    Reuniao,
    Seminario,
)
from ged.models import Arquivo
from rh.models import Localidade, Servidor
from rh.views import RHLocalidade
from standard.views import AutoCompleteField

json = get_json_engine()


class CustomAutocomplete(extjs.ExtCrud):

    def autocomplete(self, args=[]):

        qs = []
        model = None
        obj = {}

        """"""
        if len(args) > 0:
            if self.request.POST["model"] == "Servidor":
                model = Servidor
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            pessoa_fisica__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(
                            pessoa_fisica__cpf__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
                    qs.append(
                        Q(matricula__icontains=self.request.POST.get("query", ""))
                    )
        """"""

        if model is not None and len(qs) > 0:
            q = None
            for qn in qs:
                q = qn if q is None else Q(q | qn)
            obj.update(
                result=[
                    {"pk": r.pk, "description": str(r)} for r in model.objects.filter(q)
                ]
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GCAPGerenciador(extjs.ExtWidget):

    def get_public_capacitacao(self, args=[]):
        obj = {}

        caps = Capacitacao.objects.filter(publicar=True).exclude(
            inscricao_fim__lt=datetime.now()
        )
        caps = caps.order_by("inscricao_fim", "inscricao_inicio")

        obj.update(count=caps.count())

        now = datetime.now()

        result = [
            {
                "pk": cap.pk,
                "dti": cap.dt_inicio.strftime("%d/%m/%Y"),
                "dtf": cap.dt_fim.strftime("%d/%m/%Y"),
                "idti": cap.inscricao_inicio.strftime("%d/%m/%Y %H:%M"),
                "idtf": cap.inscricao_fim.strftime("%d/%m/%Y %H:%M"),
                "carga_horaria": cap.carga_horaria,
                "titulo": cap.nome,
                "descricao": cap.descricao,
                "aberta": (cap.inscricao_inicio <= now and cap.inscricao_fim >= now),
                "dias_fim_inscricao": (cap.inscricao_fim - datetime.now()).days,
            }
            for cap in caps
        ]

        obj.update(result=result)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.cesaf.gecap.Gerenciador()")

    def request_certificate(self, args=[]):
        obj = {}

        cap = Capacitacao.objects.get(pk=int(self.request.POST["capacitacao"]))
        servidores = [i.servidor for i in cap.inscricoes.filter(certificado=None)]

        obj.update(notificados=len(servidores))

        t = Thread(
            target=Notification.notify_all,
            kwargs={
                "msg": "GECAP_COBRA_CERTIFICADO",
                "targets": servidores,
                "types": ["SYS"],
                "capacitacao": str(cap),
            },
        )
        t.daemon = True
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "capacitacao":
            obj = self.get_store_capacitacao(args)
        if args[0] == "inscricao":
            obj = self.get_store_inscricao(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_inscricao(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            inscricoes = Inscricao.objects.filter(
                capacitacao=Capacitacao.objects.get(
                    pk=int(self.request.POST["capacitacao"])
                )
            )

            if "query" in self.request.POST:
                inscricoes = inscricoes.filter(
                    Q(
                        servidor__pessoa_fisica__nome__icontains=self.request.POST[
                            "query"
                        ]
                    )
                    | Q(
                        servidor__pessoa_fisica__cpf__icontains=self.request.POST[
                            "query"
                        ]
                    )
                    | Q(servidor__matricula__icontains=self.request.POST["query"])
                )

            obj["totalRows"] = inscricoes.count()
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
                    "dt_cadastro": "data_cadastro",
                }

                if (
                    "sort" in self.request.POST
                    and self.request.POST["sort"] in translate
                ):
                    if self.request.POST["dir"] == "ASC":
                        inscricoes = inscricoes.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        inscricoes = inscricoes.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    inscricoes = inscricoes.order_by("-data_cadastro")
                inscricoes = inscricoes[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in inscricoes:
                inv = og.investimentos.aggregate(total=Sum("valor")).get("total")
                inv = inv if inv is not None else 0

                obj["result"].append(
                    {
                        "status": [
                            {
                                "icon": (
                                    "static/cesaf/images/homologar.png"
                                    if og.homologado is not None
                                    else "static/cesaf/images/homologar-disabled.png"
                                ),
                                "title": (
                                    "Homologado"
                                    if og.homologado is not None
                                    else "Não homologado"
                                ),
                                "alt": (
                                    "Homologado"
                                    if og.homologado is not None
                                    else "Não homologado"
                                ),
                            },
                            {
                                "icon": (
                                    "static/cesaf/images/certificado.png"
                                    if og.certificado is not None
                                    else "static/cesaf/images/certificado-disabled.png"
                                ),
                                "title": (
                                    "Certificado entrege"
                                    if og.certificado is not None
                                    else "Certificado não foi entregue"
                                ),
                                "alt": (
                                    "Certificado entrege"
                                    if og.certificado is not None
                                    else "Certificado não foi entregue"
                                ),
                            },
                        ],
                        "codigo": og.pk,
                        "servidor": og.servidor.pk,
                        "certificado": (
                            og.certificado.pk if og.certificado is not None else None
                        ),
                        "nome": og.servidor.pessoa_fisica.nome,
                        "capacitacao": (
                            og.capacitacao.nome if og.capacitacao is not None else ""
                        ),
                        "homologado": (
                            og.homologado.strftime("%d/%m/%Y")
                            if og.homologado is not None
                            else ""
                        ),
                        "dt_cadastro": (
                            og.data_cadastro.strftime("%d/%m/%Y %H:%M")
                            if og.data_cadastro is not None
                            else ""
                        ),
                        "investimento": str(inv),
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    def get_store_capacitacao(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            capacitacoes = None

            if "query" in self.request.POST:
                try:
                    capacitacoes = Capacitacao.objects.filter(
                        nome__icontains=self.request.POST["query"]
                    )
                except Exception as e:
                    self.log.exception(e)
            if capacitacoes is None:
                capacitacoes = Capacitacao.objects.all()

            obj["totalRows"] = capacitacoes.count()
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
                    "codigo": "protocolo__codigo",
                    "nome": "nome",
                    "dt_inicio": "dt_inicio",
                    "dt_fim": "dt_fim",
                }

                if (
                    "sort" in self.request.POST
                    and self.request.POST["sort"] in translate
                ):
                    if self.request.POST["dir"] == "ASC":
                        capacitacoes = capacitacoes.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        capacitacoes = capacitacoes.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    capacitacoes = capacitacoes.order_by("-data_cadastro")
                capacitacoes = capacitacoes[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in capacitacoes:
                inv_g = (
                    og.investimentos.filter(inscricao=None)
                    .aggregate(total=Sum("valor"))
                    .get("total")
                )
                inv_i = (
                    og.investimentos.filter(
                        ~Q(inscricao=None), ~Q(inscricao__homologado=None)
                    )
                    .aggregate(total=Sum("valor"))
                    .get("total")
                )

                inv_g = inv_g if inv_g is not None else 0
                inv_i = inv_i if inv_i is not None else 0

                inv = inv_g + inv_i

                valor = {
                    "codigo": og.pk,
                    "nome": og.nome,
                    "dt_inicio": (
                        og.dt_inicio.strftime("%d/%m/%Y")
                        if og.dt_inicio is not None
                        else ""
                    ),
                    "dt_fim": (
                        og.dt_fim.strftime("%d/%m/%Y") if og.dt_fim is not None else ""
                    ),
                    "carga_horaria": (
                        "%d h" % og.carga_horaria
                        if og.carga_horaria is not None
                        else "0 h"
                    ),
                    "investimento": str(inv),
                    "cidade": str(og.cidade_evento),
                }

                #   for attr in ['congresso', 'curso', 'evento', 'seminario', 'reuniao', 'feira', 'oficina']:
                #   	if hasattr(og, attr):
                #           valor.update(
                #               status = {
                #                   'icon':'static/cesaf/images/%s.png' % attr,
                #                   'title':attr.capitalize(),
                #                   'alt':attr.capitalize()
                #               }
                #           )
                #           valor.update(tipo = attr)
                #
                #   Talvez a sequencia de ifs abaixo fique melhor, fazendo como descrito acima.

                if hasattr(og, "congresso"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/congresso.png",
                            "title": "Congresso",
                            "alt": "Congresso",
                        }
                    )
                    valor.update(tipo="congresso")

                elif hasattr(og, "curso"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/curso.png",
                            "title": "Curso",
                            "alt": "Curso",
                        }
                    )
                    valor.update(tipo="curso")

                elif hasattr(og, "evento"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/evento.png",
                            "title": "Evento",
                            "alt": "Evento",
                        }
                    )
                    valor.update(tipo="evento")
                elif hasattr(og, "seminario"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/seminario.png",
                            "title": "Seminario",
                            "alt": "Seminario",
                        }
                    )
                    valor.update(tipo="seminario")
                elif hasattr(og, "reuniao"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/reuniao.png",
                            "title": "Reunião",
                            "alt": "Reunião",
                        }
                    )
                    valor.update(tipo="reuniao")
                elif hasattr(og, "feira"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/feira.png",
                            "title": "Feira",
                            "alt": "Feira",
                        }
                    )
                    valor.update(tipo="feira")
                elif hasattr(og, "oficina"):
                    valor.update(
                        status={
                            "icon": "static/cesaf/images/oficina.png",
                            "title": "Oficina",
                            "alt": "Oficina",
                        }
                    )
                    valor.update(tipo="oficina")

                obj["result"].append(valor)
        except Exception as e:
            self.log.exception(e)
        return obj


class GCAPAreaConhecimento(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = AreaConhecimento

    titles = {
        "PANEL": "Área de Conhecimento",
        "LIST": "Gerenciador de Área de Conhecimento",
        "NEW": "Novo(a) Área de Conhecimento",
        "EDIT": "Editando um(a) Área de Conhecimento",
        "DELETE": "Removendo um(a) Área de Conhecimento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@tab(
    [
        {
            "title": "Informações",
            "field": [
                "nome",
                "dt_inicio",
                "dt_fim",
                "carga_horaria",
                "cidade_evento",
                "ementa",
            ],
        },
        {"title": "Promotores", "field": ["promovido_por", "promotores"]},
        {"title": "Áreas do Conhecimento", "field": ["area_conhecimento"]},
        {"title": "Site", "field": ["publicar", "descricao"]},
    ]
)
class GCAPCapacitacao(extjs.ExtCrud):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Capacitacao
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Capacitação",
        "LIST": "Gerenciador de Capacitação",
        "NEW": "Novo(a) Capacitação",
        "EDIT": "Editando um(a) Capacitação",
        "DELETE": "Removendo um(a) Capacitação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPFeira(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Feira
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Feira",
        "LIST": "Gerenciador de Feiras",
        "NEW": "Novo(a) Feira",
        "EDIT": "Editando um(a) Feira",
        "DELETE": "Removendo um(a) Feira",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPReuniao(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Reuniao
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Reuniao",
        "LIST": "Gerenciador de Reuniaos",
        "NEW": "Novo(a) Reuniao",
        "EDIT": "Editando um(a) Reuniao",
        "DELETE": "Removendo um(a) Reuniao",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPOficina(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Oficina
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Oficina",
        "LIST": "Gerenciador de Oficinas",
        "NEW": "Novo(a) Oficina",
        "EDIT": "Editando um(a) Oficina",
        "DELETE": "Removendo um(a) Oficina",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPSeminario(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Seminario
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Seminário",
        "LIST": "Gerenciador de Seminário",
        "NEW": "Novo(a) Seminário",
        "EDIT": "Editando um(a) Seminário",
        "DELETE": "Removendo um(a) Seminário",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPCongresso(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Congresso
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Congresso",
        "LIST": "Gerenciador de Congresso",
        "NEW": "Novo(a) Congresso",
        "EDIT": "Editando um(a) Congresso",
        "DELETE": "Removendo um(a) Congresso",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPCurso(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Curso
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Curso",
        "LIST": "Gerenciador de Curso",
        "NEW": "Novo(a) Curso",
        "EDIT": "Editando um(a) Curso",
        "DELETE": "Removendo um(a) Curso",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GCAPEvento(GCAPCapacitacao):

    class Form(forms.ModelForm):
        cidade_evento = AutoCompleteField(
            model=Localidade, controller=RHLocalidade, label="Local"
        )

        class Meta:
            model = Evento
            exclude = ["capacitacao_ptr", "data_cadastro"]

    titles = {
        "PANEL": "Evento",
        "LIST": "Gerenciador de Evento",
        "NEW": "Novo(a) Evento",
        "EDIT": "Editando um(a) Evento",
        "DELETE": "Removendo um(a) Evento",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


@add_methods({"notify": Notification.notify})
class GCAPInscricao(CustomAutocomplete, extjs.ExtWidget):

    def homologar(self, args=[]):
        obj = {"count": 0, "success": 0, "failure": 0, "faileds": [], "inscricoes": []}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2058

        for pkinsc in self.request.POST.getlist("inscricao"):
            obj["count"] += 1

            try:
                insc = Inscricao.objects.get(pk=int(pkinsc))
                insc.homologado = datetime.now()
                insc.save()
                obj["success"] += 1

                self.notify(
                    "GECAP_HOMOLOGADO",
                    target=insc.servidor,
                    types=["SYS"],
                    capacitacao=str(insc.capacitacao),
                    cidade_evento=str(insc.capacitacao.cidade_evento),
                    data_inicio=insc.capacitacao.dt_inicio.strftime("%d/%m/%Y"),
                    data_fim=insc.capacitacao.dt_fim.strftime("%d/%m/%Y"),
                )
            except Exception as e:
                self.log.exception(e)
                obj["failure"] += 1
                obj["faileds"].append(pkinsc)

        if obj.get("success") > 0 and obj.get("failure") == 0:
            linelog.status = 1
        elif obj.get("success") > 0 and obj.get("failure") > 0:
            linelog.status = 2
        else:
            linelog.status = 0

        linelog.json_description["status_homologacao"] = {
            "success": obj.get("success", 0),
            "failure": obj.get("failure", 0),
        }

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def delete(self, args=[]):
        obj = {"count": 0, "success": 0, "failure": 0, "faileds": []}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2054

        for pkinsc in self.request.POST.getlist("inscricao"):
            obj["count"] += 1

            try:
                Inscricao.objects.get(pk=int(pkinsc)).delete()
                obj["success"] += 1
                linelog.status = 1
            except Inscricao.DoesNotExist:
                linelog.status = 0
                obj["failure"] += 1
                obj["faileds"].append(pkinsc)

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def add(self, args=[]):
        obj = {"success": False, "msg": "Nada ainda foi feito."}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2052

        try:
            i = Inscricao(
                capacitacao=Capacitacao.objects.get(
                    pk=int(self.request.POST["capacitacao"])
                ),
                servidor=Servidor.objects.get(pk=int(self.request.POST["servidor"])),
            )

            if self.request.POST["certificado"]:
                linelog.level = 2059
                i.certificado = Arquivo.objects.get(
                    pk=int(self.request.POST["certificado"])
                )

            i.save()
            obj.update(pk=i.pk)
            obj.update(success=True)
            obj.update(msg="Dados gravados com sucesso.")
            linelog.status = 1
        except Exception as e:
            linelog.status = 0
            obj.update(msg="Ocorreu um erro gravando os dados da inscrição.")
            self.log.exception(e)

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False, "msg": "Nada ainda foi feito."}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2053

        try:
            i = Inscricao.objects.get(pk=self.request.POST["pk"])

            if self.request.POST["certificado"] and i.certificado is None:
                linelog.level = 2059
                i.certificado = Arquivo.objects.get(
                    pk=int(self.request.POST["certificado"])
                )

            i.save()
            obj.update(pk=i.pk)
            obj.update(success=True)
            obj.update(msg="Dados gravados com sucesso.")
            linelog.status = 1
        except Exception as e:
            linelog.status = 0
            obj.update(msg="Ocorreu um erro gravando os dados da inscrição.")
            obj.update(e=str(e))

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GCAPInvestimento(extjs.ExtWidget):

    def copy(self, args=[]):
        obj = {"count": 0, "success": 0, "failure": 0, "msg": ""}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2060

        try:
            _from = Investimento.objects.filter(
                inscricao=Inscricao.objects.get(pk=int(self.request.POST["from"]))
            )
            _to = Inscricao.objects.get(pk=int(self.request.POST["to"]))
        except Exception as e:
            obj["msg"] = (
                "Não foi possivel identificar a origem ou o destino da copia de investimentos."
            )
            self.log.exception(e)
        else:
            for i in _from:
                obj["count"] += 1
                try:
                    i.pk = None
                    i.inscricao = _to
                    i.save()
                except Exception:
                    obj["failure"] += 1
                else:
                    obj["success"] += 1

        if obj.get("success") > 0 and obj.get("failure") == 0:
            linelog.status = 1
        elif obj.get("success") > 0 and obj.get("failure") > 0:
            linelog.status = 2
        else:
            linelog.status = 0

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list(self, args=[]):
        obj = {"result": []}

        if "inscricao" in self.request.POST and self.request.POST["inscricao"] != "":
            query = Investimento.objects.filter(
                capacitacao=Capacitacao.objects.get(
                    pk=int(self.request.POST["capacitacao"])
                ),
                inscricao=Inscricao.objects.get(pk=int(self.request.POST["inscricao"])),
            )
        else:
            query = Investimento.objects.filter(
                capacitacao=Capacitacao.objects.get(
                    pk=int(self.request.POST["capacitacao"])
                )
            )

        item = 0
        for inv in query:
            item += 1
            obj["result"].append(
                {
                    "status": [
                        {
                            "icon": (
                                "static/cesaf/images/individual.png"
                                if inv.inscricao is not None
                                else "static/cesaf/images/grupo.png"
                            ),
                            "alt": (
                                "Individual" if inv.inscricao is not None else "Grupo"
                            ),
                            "title": (
                                "Individual" if inv.inscricao is not None else "Grupo"
                            ),
                        }
                    ],
                    "pk": inv.pk,
                    "item": item,
                    "description": inv.descricao,
                    "description_ex": (
                        inv.descricao
                        if inv.inscricao is None
                        else "%s, %s"
                        % (inv.inscricao.servidor.pessoa_fisica, inv.descricao)
                    ),
                    "valor": str(inv.valor),
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def add(self, args=[]):
        obj = {"success": False}

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2049

        try:
            i = Investimento(
                capacitacao=Capacitacao.objects.get(
                    pk=int(self.request.POST["capacitacao"])
                ),
                descricao=self.request.POST["descricao"],
                valor=self.request.POST["valor"],
            )

            if (
                "inscricao" in self.request.POST
                and self.request.POST["inscricao"] != ""
            ):
                linelog.level = 2055
                i.inscricao = Inscricao.objects.get(
                    pk=int(self.request.POST["inscricao"])
                )

            i.save()
            obj.update(success=True)
            linelog.status = 1
        except Exception as e:
            linelog.status = 0
            obj.update(msg=str(e))
            self.log.exception(e)

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def delete(self, args=[]):
        obj = {"success": False}

        pks = self.request.POST.getlist("pk")

        linelog = LineLog()
        linelog.read_request(self.request)
        linelog.level = 2051

        try:
            investimentos = Investimento.objects.filter(pk__in=pks)
            result = [investimento.inscricao is None for investimento in investimentos]

            linelog.level = 2051 if True not in result else 2057

            investimentos.delete()
            obj.update(success=True)
            linelog.status = 1
        except Exception:
            linelog.status = 0
            pass

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"success": False}

        linelog = LineLog()
        linelog.read_request(self.request)

        try:
            i = Investimento.objects.get(pk=int(self.request.POST["pk"]))
            i.descricao = self.request.POST["descricao"]
            i.valor = self.request.POST["valor"]

            linelog.level = 2050 if i.inscricao is None else 2056

            i.save()
            obj.update(success=True)
            linelog.status = 1
        except Exception as e:
            linelog.status = 0
            obj.update(msg=str(e))

        linelog.save()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
