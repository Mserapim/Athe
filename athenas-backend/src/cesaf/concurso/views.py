# -.- coding: utf8 -.-

# TODO: Realizar alteração para listar as incrições por concurso, atualmente todas estão sendo listadas.

from django.db import transaction
from django.db.models import Q
from contrib.controller import DefaultController
from contrib import extjs
from cesaf.concurso.models import (
    Inscricao,
    Concurso as ConcursoModel,
    SelecaoEstagio,
    Vaga,
)
from cesaf.concurso.forms import ParecerForm
from edocs.protocolo.models import Referencia, Protocolo, Movimentacao
from rh.models import Localidade, PessoaFisica, Servidor, Lotacao
from web.services.lib import IProtocolo
from web.services.forms import RecursoForm
from contrib.decorator import login_required
from auditoria.models import LineLog

import datetime

from contrib.utils import get_json_engine

json = get_json_engine()


class CONCURSOGerenciador(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.cesaf.concurso.Gerenciador()")

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "concurso":
            obj = self.get_store_concurso()
        if args[0] == "inscricao":
            obj = self.get_store_inscricao()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_concurso(self):
        obj = {"totalRows": 0, "result": []}
        try:
            concurso = ConcursoModel.objects.all()
            obj["totalRows"] = concurso.count()
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
                        concurso = concurso.order_by("%s" % self.request.POST["sort"])
                    else:
                        concurso = concurso.order_by("-%s" % self.request.POST["sort"])
                concurso = concurso[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in concurso:
                pars = None
                for v in Vaga.objects.filter(concurso=og):
                    pars = pars | Q(vaga__id=v.id) if pars else Q(vaga__id=v.id)
                inscricao = Inscricao.objects.filter(pars)
                obj["result"].append(
                    {
                        "codigo": og.pk,
                        "nome": str(og.nome),
                        "dt_inicio": og.dt_inicio.strftime("%d/%m/%Y"),
                        "promovido_por": "CESAF",
                        "descricao": str(og.descricao),
                        "inscritos": inscricao.count(),
                        "homologados": inscricao.filter(~Q(homologado=None)).count(),
                        "slug": "SLUG",
                    }
                )
        except Exception as e:
            self.log.exception(e)
        self.log.debug(obj)
        return obj

    def get_store_inscricao(self):
        obj = {"totalRows": 0, "result": []}
        try:
            pars = None
            for v in Vaga.objects.filter(concurso__id=self.request.POST["concurso"]):
                pars = pars | Q(vaga__id=v.id) if pars else Q(vaga__id=v.id)

            if "com_recurso" in self.request.POST:
                pars = pars & Q(recurso=True)
            inscricao = Inscricao.objects.filter(pars)

            obj["totalRows"] = len(inscricao)
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
                    "codigo": "pk",
                    "pessoa_nome": "protocolo__interessado__nome",
                    "vaga_area": "vaga__area",
                    "vaga_local": "vaga__local__nome",
                    "curso": "curso",
                    # "faculdade": "faculdade",
                    # "disponibilidade": "disponibilidade",
                    "protocolo": "protocolo__codigo",
                    "data_criacao": "protocolo__data_criacao",
                }
                if "sort" in self.request.POST and translate.get(
                    self.request.POST["sort"]
                ):
                    if self.request.POST["dir"] == "ASC":
                        inscricao = inscricao.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        inscricao = inscricao.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                inscricao = inscricao[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in inscricao:
                try:
                    cpf = PessoaFisica.objects.get(pk=og.protocolo.interessado.pk).cpf
                except Exception:
                    cpf = ""
                try:
                    selecao_estagio = SelecaoEstagio.objects.get(inscricao=og)
                except Exception:
                    selecao_estagio = None
                try:
                    disponibilidade = (
                        selecao_estagio.disponibilidade == 1
                        and "MATUTINO"
                        or "VESPERTINO"
                    )
                except Exception:
                    disponibilidade = ""
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
                            }
                        ],
                        "codigo": og.pk,
                        "protocolo": og.protocolo.codigo,
                        "vaga_area": str(og.vaga.area),
                        "vaga_local": str(og.vaga.local.nome),
                        "vaga_quantidade": og.vaga.quantidade,
                        "curso": selecao_estagio is not None
                        and selecao_estagio.curso
                        or "",
                        "faculdade": selecao_estagio is not None
                        and selecao_estagio.faculdade
                        or "",
                        "matricula": selecao_estagio is not None
                        and selecao_estagio.matricula
                        or "",
                        "ano_periodo": selecao_estagio is not None
                        and selecao_estagio.ano_periodo
                        or "",
                        "ano_conclusao": selecao_estagio is not None
                        and selecao_estagio.ano_conclusao.year
                        or "",
                        "disponibilidade": disponibilidade,
                        "pessoa_nome": str(og.protocolo.interessado.nome),
                        "pessoa_cpf": cpf,
                        "data_criacao": og.protocolo.data_criacao.strftime(
                            "%d/%m/%y %H:%M:%S"
                        ),
                        "homologado": og.homologado is not None
                        and og.homologado.strftime("%d/%m/%y %H:%M:%S")
                        or "",
                    }
                )
        except Exception as e:
            self.log.exception(e)
        return obj

    @login_required(type="JSON")
    def deferir_recurso(self, args=[]):
        res = {
            "success": False,
            "msg": "A requisição deve ser feita via POST",
            "data": None,
        }

        try:
            with transaction.atomic():
                log = LineLog(request=self.request, level=131, status=0)
                self.response["content-type"] = "text/javascript"
                if self.request.POST:
                    form = ParecerForm(self.request.POST)
                    if form.is_valid():
                        data = form.cleaned_data
                        tipo = (
                            "Deferimento"
                            if data["tipo"].lower() == "deferir"
                            else "Indeferimento"
                        )

                        p = Protocolo.objects.get(codigo=data["recurso"])
                        p.deferido = (
                            True if data["tipo"].lower() == "deferir" else False
                        )
                        p.data_finalizado = datetime.datetime.now()
                        p.save()
                        servidor = Servidor.objects.get(user=self.request.user)
                        lotacao = Lotacao.objects.get(sigla="CESAF")
                        Movimentacao(
                            protocolo=p,
                            lotacao_origem=lotacao,
                            servidor_origem=servidor,
                            data_encaminhamento=datetime.datetime.now(),
                            parecer=data["parecer"],
                            passo=p.movimentacoes.all().count(),
                            destinatario=p.interessado,
                        ).save()

                        Inscricao.objects.get(
                            protocolo__codigo=data["inscricao"]
                        ).check_recursos()

                        log.status = 1
                        res["success"] = True
                        res["msg"] = "%s realizado com sucesso." % tipo
                    else:
                        res["msg"] = "Dados do formulário são inválidos"
                log.save()
        except Exception as err:
            res["msg"] = "Não foi possível realizar o %s." % tipo
            res["data"] = str(err)
        self.response.write(json.encode(res))

    def recurso_por_inscricao(self, args=[]):
        if args:
            recursos = Protocolo.objects.filter(
                referencias__protocolo__codigo=args[0], data_finalizado=None
            ).values("codigo", "assunto", "resumo")
            self.response["content-type"] = "text/javascript"
            self.response.write(
                json.encode(
                    {"totalRows": recursos.count(), "result": eval(str(recursos))}
                )
            )

    @login_required(type="JSON")
    def homologar(self, args=[]):
        from datetime import datetime

        obj = {"success": True, "message": "", "failure": 0}
        for pkinsc in self.request.POST.getlist("inscricao"):
            log = LineLog(request=self.request, level=130, status=0)
            try:
                insc = Inscricao.objects.get(pk=int(pkinsc))
                insc.homologado = datetime.now()
                insc.save()
                log.status = 1
                # TODO: IMPLEMENTAR FINALIZAÇÃO DE PROTOCOLO
            except Exception as e:
                self.log.exception(e)
                obj["success"] = False
                obj["failure"] = 1
                obj["message"] = str(e)
            log.save()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class Concurso(DefaultController):

    def vagas(self, args=[]):
        if args:
            try:
                _vagas = ConcursoModel.objects.get(slug=args[0]).vagas.values(
                    "id", "area", "local"
                )
                for item in _vagas:
                    item["local"] = str(Localidade.objects.get(id=item["local"]))
                return self.render(
                    data={
                        "error": False,
                        "msg": "Lista de vagas.",
                        "data": list(_vagas),
                    }
                )
            except Exception as e:
                return self.render(data={"error": True, "msg": str(e), "data": None})
        return self.render(
            data={
                "error": True,
                "msg": "É necessário informar qual concurso.",
                "data": None,
            }
        )

    def verificar_inscricao(self, args=[]):
        if args:
            inscricao = Inscricao.objects.filter(
                protocolo__interessado__pessoafisica__cpf=args[0]
            )
            if inscricao.count() == 0:
                return self.render(
                    data={
                        "error": True,
                        "msg": "Não foi encontrada inscrição relacionada ao usuário",
                        "data": None,
                    }
                )
            else:
                inscricao = inscricao[0]
                data = {
                    "evento": inscricao.vaga.concurso.nome,
                    "inscricao": inscricao.protocolo.codigo,
                    "data": inscricao.protocolo.data_criacao,
                    "area": inscricao.vaga.area,
                    "local": str(inscricao.vaga.local),
                    "candidato": inscricao.protocolo.interessado.nome,
                    "cpf": inscricao.protocolo.interessado.pessoafisica.cpf,
                }
                return self.render(
                    data={
                        "error": False,
                        "msg": "Existe uma inscrição relacionada a este candidato.",
                        "data": data,
                    }
                )
        return self.render(
            data={
                "error": True,
                "msg": "É necessário informar o número de CPF do candidato",
                "data": None,
            }
        )

    def recurso(self, args=[]):
        data = {
            "error": True,
            "msg": "A requisição deve ser feita via POST.",
            "data": None,
        }
        try:
            with transaction.atomic():
                if self.request.POST:
                    form = RecursoForm(self.request.REQUEST)
                    data.update(
                        {
                            "msg": "Os dados enviados não foram validados. Verifique se estes estão corretos."
                        }
                    )
                    if form.is_valid():
                        d = form.cleaned_data
                        inscricao = Inscricao.objects.filter(
                            protocolo__codigo=d["inscricao"]
                        )
                        data.update(
                            {
                                "msg": "Não foi encontrada a inscrição referente ao número: %s"
                                % d["inscricao"]
                            }
                        )
                        if inscricao.exists():
                            mov = inscricao.protocolo.movimentacoes.all().latest("pk")
                            ref = Referencia(
                                protocolo=inscricao.protocolo, movimentacao=mov
                            )
                            ref.save()

                            d["sigla_lotacao"] = "CESAF"
                            recurso = IProtocolo.do(d, inscricao.protocolo)
                            if not recurso["error"]:
                                recurso = recurso["data"]
                                recurso.referencias.add(ref)
                                inscricao.recurso = True
                                inscricao.save()

                                data = {
                                    "concurso": inscricao.vaga.concurso.nome,
                                    "inscricao": inscricao.protocolo.codigo,
                                    "data_inscricao": inscricao.protocolo.data_criacao,
                                    "area_inscricao": inscricao.vaga.area,
                                    "local_vaga": str(inscricao.vaga.local),
                                    "candidato": inscricao.protocolo.interessado.nome,
                                    "cpf": inscricao.protocolo.interessado.pessoafisica.cpf,
                                    "recurso": recurso.codigo,
                                    "data": recurso.data_criacao,
                                    "assunto": recurso.assunto,
                                    "resumo": recurso.resumo,
                                }
                                data.update(
                                    {
                                        "error": False,
                                        "msg": "Protocolo do recurso gerado com sucesso.",
                                    }
                                )
                            else:
                                raise Exception(recurso)
        except Exception as err:
            self.log.exception(err)
            data.update({"msg": "Falha no processo, contate a TI."})
        return self.render(data=data)
