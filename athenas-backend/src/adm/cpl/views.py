# -*- coding: utf-8 -*-
import os.path
import time
from datetime import date, datetime

from adm.compras.models import NEAquisicao, ProcessoAquisicao, ProdutoProcesso
from adm.contabilidade.models import Produto
from adm.cpl.models import Licitacao, Participante, ProdutoVencedor, PublicacaoLicitacao
from adm.eproc.models import Processo
from contrib import extjs
from contrib.decorator import login_required
from contrib.utils import DateUtils, get_json_engine
from django import forms
from django.conf import settings
from django.db.models import Q
from ged.forms import FileUploadField
from ged.models import Arquivo
from rh.models import Pessoa
from standard.views import AutoCompleteField

json = get_json_engine()


class CustomAutocomplete(extjs.ExtCrud):

    def autocomplete(self, args=[]):
        qs = []
        model = None
        obj = {}

        """"""
        if len(args) > 0:
            if args[0] == "Pessoa":
                model = Pessoa
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(nome__icontains=self.request.POST.get("query", "")))
            elif args[0] == "Licitacao":
                model = Licitacao
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(numero__icontains=self.request.POST.get("query", "")))
            elif args[0] == "Participante":
                model = Participante
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(pessoa__nome__icontains=self.request.POST.get("query", ""))
                    )
            elif args[0] == "Vencedor":
                model = ProdutoVencedor
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(
                            participante__pessoa__nome__icontains=self.request.POST.get(
                                "query", ""
                            )
                        )
                    )
            elif args[0] == "Produto":
                model = Produto
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(
                        Q(descricao__icontains=self.request.POST.get("query", ""))
                    )
            elif args[0] == "Contrato":
                model = Produto
                if "pk" in self.request.POST:
                    qs.append(Q(pk=int(self.request.POST.get("pk", 0))))
                else:
                    qs.append(Q(numero__icontains=self.request.POST.get("query", "")))
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


class CPLGerenciador(extjs.ExtWidget):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.adm.cpl.Gerenciador()")

    def get_store(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        if args[0] == "licitacao":
            obj = self.get_store_licitacao(args)
        elif args[0] == "processo":
            obj = self.get_store_processo(args)
        elif args[0] == "participante":
            obj = self.get_store_participante(args)
        elif args[0] == "produto":
            obj = self.get_store_produto(args)
        elif args[0] == "vencedorproduto":
            obj = self.get_store_vencedor_produto(args)
        elif args[0] == "documento":
            obj = self.get_store_documento(args)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_store_site(self, args=[]):
        obj = {
            "modalidade": "",
            "registro_preco": False,
            "finalizado": False,
            "items": [],
            "count": 0,
        }
        try:
            finalizado = "finalizado" in self.request.POST
            registro_preco = "registro_preco" in self.request.POST
            modalidade = self.request.POST["modalidade"]
            q = Q(arquivado=False)
            if finalizado:
                q = Q(q & Q(finalizado=finalizado))
            if registro_preco:
                q = Q(q & Q(registro_preco=registro_preco))
            if "modalidade" in self.request.POST:
                if modalidade != "0":
                    if modalidade == "1":
                        obj["modalidade"] = "CONCORRÊNCIA"
                    elif modalidade == "2":
                        obj["modalidade"] = "CONVITE"
                    elif modalidade == "3":
                        obj["modalidade"] = "PREGÃO ELETRÔNICO"
                    elif modalidade == "4":
                        obj["modalidade"] = "PREGÃO PRESENCIAL"
                    elif modalidade == "5":
                        obj["modalidade"] = "TOMADA DE PREÇO"

                    if q is not None:
                        q = Q(q & Q(modalidade=modalidade))
                    else:
                        q = Q(modalidade=modalidade)

                else:
                    obj["modalidade"] = "TODAS"

            if "numero" in self.request.POST:
                if q is not None:
                    q = Q(q & Q(numero=self.request.POST["numero"]))
                else:
                    q = Q(numero=self.request.POST["numero"])

            if q is not None:
                licitacoes = Licitacao.objects.filter(q)
            else:
                licitacoes = Licitacao.objects.all()

            obj["count"] = licitacoes.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )
            licitacoes = licitacoes.order_by("-data_realizacao")
            licitacoes = licitacoes[start:end]
            obj["registro_preco"] = registro_preco
            obj["finalizado"] = finalizado
            for og in licitacoes:
                files = []
                for p in og.publicacaolicitacao_set.all():
                    filename = "{0}/{1}".format(
                        settings.UPLOAD_STORE_DIR, p.arquivo.file if p.arquivo else ""
                    )
                    files.append(
                        {
                            "permalink": p.arquivo.permalink() if p.arquivo else "",
                            "titulo": p.arquivo.filename if p.arquivo else "",
                            "mimetype": "application/pdf".replace("/", "-"),
                            "tipo": "{0} {1}".format(
                                p.get_tipo_display(),
                                p.get_natureza_display() if p.natureza else "",
                            ),
                            "data_pub": p.data_expedicao.strftime("%d/%m/%Y"),
                            "size": os.path.getsize(filename),
                        }
                    )
                obj["items"].append(
                    {
                        "pk": og.pk,
                        "numero": "%s/%s" % (og.numero, og.data_cadastro.year),
                        "data_cadastro": (
                            og.data_cadastro.strftime("%d/%m/%Y")
                            if og.data_cadastro
                            else ""
                        ),
                        "mes_realizacao": (
                            og.data_realizacao.strftime("%m")
                            if og.data_realizacao
                            else ""
                        ),
                        "data_realizacao": (
                            og.data_realizacao.strftime("%d/%m/%Y")
                            if og.data_realizacao
                            else ""
                        ),
                        "modalidade": og.get_modalidade_display(),
                        "objeto": str(og.processo.titulo),
                        "dias_pendentes": (og.data_realizacao - datetime.now()).days,
                        "files": files,
                    }
                )
        except Exception as e:
            self.log.exception(e)

        self.render(data=obj)

    def get_licitacao_information(self, args=[]):
        obj = {
            "pk": None,
            "numero": "",
            "objeto": "",
            "ocorreu": False,
            "data_realizacao": "",
        }
        try:
            licitacao = Licitacao.objects.get(pk=int(self.request.POST["pk"]))
            files = []
            for p in licitacao.publicacaolicitacao_set.all():
                filename = "{0}/{1}".format(
                    settings.UPLOAD_STORE_DIR, p.arquivo.file if p.arquivo else ""
                )
                files.append(
                    {
                        "permalink": p.arquivo.permalink() if p.arquivo else "",
                        "titulo": p.arquivo.filename if p.arquivo else "",
                        "mimetype": "application/pdf".replace("/", "-"),
                        "tipo": "{0} {1}".format(
                            p.get_tipo_display(),
                            p.get_natureza_display() if p.natureza else "",
                        ),
                        "data_pub": p.data_expedicao.strftime("%d/%m/%Y"),
                        "size": os.path.getsize(filename),
                    }
                )
            produtos = []
            for pp in ProdutoProcesso.objects.filter(
                Q(processo_aquisicao=licitacao.processo)
            ):
                produtos.append(
                    {
                        "quantidade": "%d %s"
                        % (int(pp.quantidade), pp.produto.unidade.sigla),
                        "unidade": pp.produto.unidade.descricao,
                        "titulo": str(pp.produto.descricao),
                    }
                )

            vencedores = []
            for p in licitacao.participante_set.all():
                produtos_vencedor = []
                for produto_processo in p.produtovencedor_set.get(
                    licitacao=licitacao
                ).produto_processo.all():
                    produtos_vencedor.append(
                        {
                            "quantidade": "%d %s"
                            % (int(pp.quantidade), pp.produto.unidade.sigla),
                            "unidade": produto_processo.produto.unidade.descricao,
                            "titulo": str(produto_processo.produto.descricao),
                        }
                    )
                vencedores.append(
                    {"pessoa": str(p.pessoa.nome), "produtos": produtos_vencedor}
                )
            obj = {
                "pk": licitacao.pk,
                "numero": "%s/%s" % (licitacao.numero, licitacao.data_cadastro.year),
                "data_cadastro": (
                    licitacao.data_cadastro.strftime("%d/%m/%Y")
                    if licitacao.data_cadastro
                    else ""
                ),
                "mes_realizacao": (
                    licitacao.data_realizacao.strftime("%m")
                    if licitacao.data_realizacao
                    else ""
                ),
                "data_realizacao": (
                    licitacao.data_realizacao.strftime("%d/%m/%Y")
                    if licitacao.data_realizacao
                    else ""
                ),
                "modalidade": licitacao.get_modalidade_display(),
                "objeto": str(licitacao.processo.titulo),
                "dias_pendentes": (licitacao.data_realizacao - datetime.now()).days,
                "files": files,
                "produtos": produtos,
                "vencedores": vencedores,
            }
        except Exception as e:
            self.log.exception(e)

        self.render(data=obj)

    def get_store_processo(self, args=[]):
        obj = {"totalRows": 0, "result": []}

        try:
            processos = Processo.objects.filter(excluido_por=None)
            obj["totalRows"] = processos.count()
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
                        processos = processos.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        processos = processos.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    processos = processos.order_by("-dt")
                processos = processos[start:end]
            except Exception as e:
                self.log.exception(e)

            for processo in processos:
                """
                Estados:
                    1- Aguardando licitação
                    2- Aguardando documentos(aviso e edital)
                    3- Aguardando participantes(participantes da licitação)
                    4- Aguardando vencedores(Aguardando ligação de produtos do processo ao participante)
                """
                try:
                    licitacao = Licitacao.objects.get(processo=processo)
                    li_codigo = licitacao.pk if licitacao.pk is not None else ""
                    li_numero = (
                        licitacao.numero if licitacao.numero is not None else "Pendente"
                    )
                    li_modalidade = (
                        licitacao.get_modalidade_display()
                        if licitacao.modalidade is not None
                        else ""
                    )
                    li_modalidade_pk = (
                        licitacao.modalidade if licitacao.modalidade is not None else ""
                    )
                    li_data_realizacao = (
                        licitacao.data_realizacao.strftime("%d/%m/%Y")
                        if licitacao.data_realizacao is not None
                        else None
                    )
                    dias_pendentes = (
                        (licitacao.data_realizacao.day - datetime.now().day)
                        if licitacao.data_realizacao is not None
                        else ""
                    )
                    li_registro_preco = (
                        licitacao.registro_preco is True and "Sim" or "Não"
                    )
                    li_arquivado = licitacao.arquivado
                    li_contrato = licitacao.contrato
                except Exception as e:
                    self.log.exception(e)
                    dias_pendentes = None
                    licitacao = None
                    li_codigo = ""
                    li_numero = "Pendente"
                    li_modalidade = ""
                    li_modalidade_pk = ""
                    li_data_realizacao = ""
                    li_registro_preco = ""
                    li_contrato = False
                    li_arquivado = False
                status = {
                    "icon": "static/engine/images/icons/athenas-0024.png",
                    "title": "Aguardando Licitação",
                    "alt": "Aguardando Licitação",
                }
                if licitacao is not None:
                    if licitacao.tem_pendencia():
                        status = {
                            "icon": "static/engine/images/icons/athenas-0099.png",
                            "title": "Aguardando Documentos",
                            "alt": "Aguardando Documentos",
                        }
                    elif Participante.objects.filter(licitacao=licitacao).count() == 0:
                        status = {
                            "icon": "static/engine/images/icons/athenas-0830.png",
                            "title": "Aguardando Participantes",
                            "alt": "Aguardando Participantes",
                        }
                    else:
                        try:
                            p_produtos = ProdutoProcesso.objects.filter(
                                Q(
                                    Q(processo_aquisicao=licitacao.processo)
                                    & Q(vencedor_produto=None)
                                )
                            )
                        except Exception:
                            p_produtos = []

                        if len(p_produtos):
                            status = {
                                "icon": "static/engine/images/icons/athenas-0106.png",
                                "title": "Aguardando Vencedores para produtos",
                                "alt": "Aguardando Vencedores para produtos",
                            }

                if dias_pendentes is None:
                    texto_data = "Prazo não definido!"
                    icon_data = "static/engine/images/icons/athenas-0023.png"
                elif dias_pendentes > 0:
                    texto_data = "Faltam {0} dia(s)".format(dias_pendentes)
                    icon_data = "static/engine/images/icons/athenas-0023.png"
                elif dias_pendentes == 0:
                    texto_data = "Realizando hoje!"
                    icon_data = "static/engine/images/icons/athenas-0415.png"
                else:
                    texto_data = "Realizada!"
                    icon_data = "static/engine/images/icons/athenas-0022.png"

                obj["result"].append(
                    {
                        "status": [
                            status,
                            {"icon": icon_data, "title": texto_data, "alt": texto_data},
                            {
                                "icon": (
                                    "static/images/archive.png"
                                    if li_arquivado is True
                                    else ""
                                ),
                                "title": "Arquivado" if li_arquivado is True else "",
                                "alt": "Arquivado" if li_arquivado is True else "",
                            },
                        ],
                        "codigo": processo.pk,
                        "numero": processo.numero_cache,
                        "dt": (
                            processo.dt.strftime("%d/%m/%Y")
                            if processo.dt is not None
                            else ""
                        ),
                        "titulo": str(processo.titulo),
                        "interessado": str(processo.interessado),
                        "orcamento": processo.processoaquisicao.get_orcamento_display(),
                        "li_codigo": li_codigo,
                        "li_numero": li_numero,
                        "li_modalidade": li_modalidade,
                        "li_modalidade_pk": li_modalidade_pk,
                        "li_data_realizacao": li_data_realizacao,
                        "li_registro_preco": li_registro_preco,
                        "li_arquivado": "Sim" if li_arquivado is True else "Não",
                        "li_contrato": "Sim" if li_contrato is True else "Não",
                    }
                )
        except Exception as e:
            self.log.exception(e)

        return obj

    def get_store_licitacao(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            licitacoes = Licitacao.objects.all()
            obj["totalRows"] = licitacoes.count()
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
                        licitacoes = licitacoes.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        licitacoes = licitacoes.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    licitacoes = licitacoes.order_by("-data_realizacao")
                licitacoes = licitacoes[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in licitacoes:
                obj["result"].append(
                    {
                        "status": [
                            {
                                "icon": (
                                    "static/cesaf/images/homologar.png"
                                    if og.arquivado is not None
                                    else "static/cesaf/images/homologar-disabled.png"
                                ),
                                "title": (
                                    "Arquivado"
                                    if og.arquivado is not None
                                    else "Não arquivado"
                                ),
                                "alt": (
                                    "Arquivado"
                                    if og.arquivado is not None
                                    else "Não arquivado"
                                ),
                            }
                        ],
                        "codigo": og.pk,
                        "processo": str(og.processo),
                        "modalidade": og.modalidade,
                        "registro_preco": og.registro_preco,
                        "numero": og.numero,
                        "data_realizacao": (
                            og.data_realizacao.strftime("%d/%m/%Y")
                            if og.data_realizacao is not None
                            else ""
                        ),
                    }
                )
        except Exception as e:
            self.log.exception(e)

        return obj

    def get_store_participante(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            if self.request.POST["licitacao"]:
                participantes = Participante.objects.filter(
                    licitacao=Licitacao.objects.get(
                        pk=int(self.request.POST["licitacao"])
                    )
                )
            else:
                participantes = Participante.objects.all()
            obj["totalRows"] = participantes.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )
            try:
                translate = {"nome": "pessoa__nome"}
                if (
                    "sort" in self.request.POST
                    and self.request.POST["sort"] in translate
                ):
                    if self.request.POST["dir"] == "ASC":
                        participantes = participantes.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        participantes = participantes.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                participantes = participantes[start:end]
            except Exception as e:
                self.log.exception(e)

            for p in participantes:
                vencedor = p.is_vencedor(int(self.request.POST["licitacao"]))
                obj["result"].append(
                    {
                        "status": [
                            {
                                "icon": (
                                    "static/cesaf/images/certificado.png"
                                    if vencedor
                                    else "static/cesaf/images/certificado-disabled.png"
                                ),
                                "title": (
                                    "Vencedor"
                                    if vencedor
                                    else "Ainda não foi contemplado"
                                ),
                                "alt": (
                                    "Vencedor"
                                    if vencedor
                                    else "Ainda não foi contemplado"
                                ),
                            }
                        ],
                        "codigo": p.pk,
                        "nome": str(p.pessoa.nome),
                    }
                )
        except Exception as e:
            obj = {
                "totalRows": 1,
                "result": [{"status": "", "codigo": "1", "nome": "erro"}],
            }
            self.log.exception(e)
        return obj

    def get_store_produto(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            try:
                produto_processo = ProdutoProcesso.objects.filter(
                    Q(
                        Q(
                            processo_aquisicao=Licitacao.objects.get(
                                pk=int(self.request.POST["licitacao"])
                            ).processo
                        )
                        & Q(vencedor_produto=None)
                    )
                )
            except Exception as e:
                self.log.exception(e)
                produto_processo = []
            obj["totalRows"] = produto_processo.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
            )
            end = (
                start + int(self.request.POST["limit"])
                if "limit" in self.request.POST
                else 1000
            )
            try:
                translate = {"nome": "produto__descricao"}
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
                    produto_processo = produto_processo.order_by("produto__descricao")
                produto_processo = produto_processo[start:end]
            except Exception as e:
                self.log.exception(e)

            for pp in produto_processo:
                obj["result"].append(
                    {
                        "codigo": pp.pk,
                        "nome": str(pp.produto.descricao),
                        "quantidade": "%d %s"
                        % (int(pp.quantidade), pp.produto.unidade.sigla),
                        "valor_total": str(pp.valor_total),
                        "valor_unitario": (
                            str(pp.valor_unitario) if pp.valor_unitario else "0.00"
                        ),
                        "valor_unitario_estimado": (
                            str(pp.valor_unitario_estimado)
                            if pp.valor_unitario_estimado
                            else "0.00"
                        ),
                        "valor_unitario_aditivo": (
                            str(pp.valor_unitario_aditivo)
                            if pp.valor_unitario_aditivo
                            else "0.00"
                        ),
                        "valor_unitario_lance": (
                            str(pp.valor_unitario_lance)
                            if pp.valor_unitario_lance
                            else "0.00"
                        ),
                    }
                )
        except Exception as e:
            self.log.exception(e)

        return obj

    def get_store_vencedor_produto(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            try:
                produto_processo = ProdutoVencedor.objects.get(
                    Q(participante__pk=int(self.request.POST["vencedor"]))
                    & Q(licitacao__pk=int(self.request.POST["licitacao"]))
                ).produto_processo.all()
            except Exception:
                self.log.warning("Não há produtos para este vencedor.")
                return obj

            obj["totalRows"] = produto_processo.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
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
                        "nome": str(pp.produto.descricao),
                        "quantidade": "%d %s"
                        % (int(pp.quantidade), pp.produto.unidade.sigla),
                        "valor_total": str(pp.valor_total),
                        "valor_unitario": (
                            str(pp.valor_unitario) if pp.valor_unitario else "0.00"
                        ),
                    }
                )
        except Exception as e:
            self.log.exception(e)

        return obj

    def get_store_documento(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        try:
            try:
                documento = PublicacaoLicitacao.objects.filter(
                    licitacao__pk=int(self.request.POST["licitacao"])
                )
            except Exception as e:
                self.log.exception(e)
                documento = []
            obj["totalRows"] = documento.count()
            start = (
                int(self.request.POST["start"]) if "start" in self.request.POST else 0
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
                        documento = documento.order_by(
                            "%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                    else:
                        documento = documento.order_by(
                            "-%s" % translate.get(self.request.POST["sort"]), "pk"
                        )
                else:
                    documento = documento.order_by("tipo")
                documento = documento[start:end]
            except Exception as e:
                self.log.exception(e)

            for og in documento:
                if og.tipo == 1:
                    tipo_nome = "ata_registro"
                if og.tipo == 2:
                    tipo_nome = "aviso"
                if og.tipo == 3:
                    tipo_nome = "edital"
                if og.tipo == 4:
                    tipo_nome = "esclarecimento"
                if og.tipo == 5:
                    tipo_nome = "impugnacao"
                if og.tipo == 6:
                    tipo_nome = "homologacao"

                obj["result"].append(
                    {
                        "codigo": og.pk,
                        "data_expedicao": (
                            og.data_expedicao.strftime("%d/%m/%Y")
                            if og.data_expedicao is not None
                            else ""
                        ),
                        "tipo": og.get_tipo_display(),
                        "natureza": (
                            og.get_natureza_display() if og.natureza is not None else ""
                        ),
                        "veiculo_publicacao": (
                            og.get_veiculo_publicacao_display()
                            if og.veiculo_publicacao is not None
                            else ""
                        ),
                        "numero_publicacao": (
                            og.numero_publicacao
                            if og.numero_publicacao is not None
                            else ""
                        ),
                        "data_publicacao": (
                            og.data_publicacao.strftime("%d/%m/%Y")
                            if og.data_publicacao is not None
                            else ""
                        ),
                        "tipo_nome": tipo_nome,
                        "veiculo_publicacao_id": (
                            og.veiculo_publicacao
                            if og.veiculo_publicacao is not None
                            else ""
                        ),
                        "arquivo": (
                            [str(og.arquivo), og.arquivo.pk]
                            if og.arquivo is not None
                            else ""
                        ),
                        "objeto": og.objeto if og.objeto is not None else "",
                        "natureza_id": og.natureza if og.natureza is not None else "",
                    }
                )
        except Exception as e:
            self.log.exception(e)

        return obj

    @login_required(type="JSON")
    def arquivar(self, args=[]):
        obj = {"success": True, "message": "", "failure": 0}
        try:
            Licitacao.objects.filter(
                pk__in=self.request.POST.getlist("licitacao")
            ).update(arquivado=self.request.POST["tipo"] == "true" and True or False)
        except Exception as e:
            obj["success"] = False
            obj["failure"] = 1
            obj["message"] = str(e)
            self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def set_homologada(self, licitacao):
        if PublicacaoLicitacao.objects.filter(Q(licitacao=licitacao) & Q(tipo=6)):
            Licitacao.objects.all().update(homologada=True)
        else:
            Licitacao.objects.all().update(homologada=False)

    def create(self, args=[]):
        obj = {"success": True, "message": ""}
        if self.request.POST["model"] == "documento":
            try:
                try:
                    publicacao_licitacao = PublicacaoLicitacao.objects.get(
                        pk=int(self.request.POST["documento"])
                    )
                except Exception:
                    publicacao_licitacao = None

                try:
                    veiculo_publicacao = (
                        self.request.POST["veiculo_publicacao"]
                        if self.request.POST["veiculo_publicacao"] != ""
                        else None
                    )
                except Exception:
                    veiculo_publicacao = None

                try:
                    numero_publicacao = (
                        self.request.POST["numero_publicacao"]
                        if self.request.POST["numero_publicacao"] != ""
                        else None
                    )
                except Exception:
                    numero_publicacao = None

                try:
                    data_publicacao = (
                        date.fromtimestamp(
                            time.mktime(
                                time.strptime(
                                    self.request.POST["data_publicacao"],
                                    getattr(settings, "DATE_INPUT_FORMATS")[0],
                                )
                            )
                        )
                        if self.request.POST["data_publicacao"] != ""
                        else None
                    )
                except Exception:
                    data_publicacao = None

                try:
                    natureza = (
                        self.request.POST["natureza"]
                        if self.request.POST["natureza"] != ""
                        else None
                    )
                except Exception:
                    natureza = None

                tipo = self.request.POST["tipo"]
                interno = tipo == 3 and True or False
                licitacao = Licitacao.objects.get(
                    pk=int(self.request.POST["licitacao"])
                )
                arquivo = self.request.POST["arquivo"]
                arquivo = (
                    Arquivo.objects.get(pk=int(self.request.POST["arquivo"]))
                    if arquivo != ""
                    else None
                )
                objeto = (
                    self.request.POST["objeto"]
                    if "objeto" in self.request.POST
                    else None
                )
                interno = interno
                ano = None
                data_expedicao = (
                    date.fromtimestamp(
                        time.mktime(
                            time.strptime(
                                self.request.POST["data_expedicao"],
                                getattr(settings, "DATE_INPUT_FORMATS")[0],
                            )
                        )
                    )
                    if self.request.POST["data_expedicao"] != ""
                    else datetime.now().date()
                )
                tipo = (
                    self.request.POST["tipo"] if "tipo" in self.request.POST else None
                )
                natureza = natureza

                if publicacao_licitacao is None:
                    publicacao_licitacao = PublicacaoLicitacao(
                        licitacao=licitacao,
                        arquivo=arquivo,
                        objeto=objeto,
                        interno=interno,
                        ano=ano,
                        veiculo_publicacao=veiculo_publicacao,
                        numero_publicacao=numero_publicacao,
                        data_publicacao=data_publicacao,
                        data_expedicao=data_expedicao,
                        tipo=tipo,
                        natureza=natureza,
                    )
                else:
                    publicacao_licitacao.licitacao = licitacao
                    publicacao_licitacao.arquivo = arquivo
                    publicacao_licitacao.objeto = objeto
                    publicacao_licitacao.interno = interno
                    publicacao_licitacao.ano = ano
                    publicacao_licitacao.veiculo_publicacao = veiculo_publicacao
                    publicacao_licitacao.numero_publicacao = numero_publicacao
                    publicacao_licitacao.data_publicacao = data_publicacao
                    publicacao_licitacao.data_expedicao = data_expedicao
                    publicacao_licitacao.tipo = tipo
                    publicacao_licitacao.natureza = natureza
                publicacao_licitacao.save()
                if "data_realizacao" in self.request.POST:
                    if self.request.POST["data_realizacao"] != "":
                        Licitacao.objects.filter(pk=licitacao.pk).update(
                            data_realizacao=DateUtils.str_to_date(
                                self.request.POST["data_realizacao"]
                            )
                        )
            except Exception as e:
                obj["message"] = "Não foi possível gravar as informações!"
                obj["success"] = False
                self.log.exception(e)
        if self.request.POST["model"] == "licitacao":
            if self.request.POST["licitacao"] != "":
                licitacao = Licitacao.objects.get(
                    pk=int(self.request.POST["licitacao"])
                )
                licitacao.modalidade = self.request.POST["modalidade"]
                licitacao.numero = self.request.POST["numero"]
                licitacao.processo = ProcessoAquisicao.objects.get(
                    pk=int(self.request.POST["processo"])
                )
                licitacao.registro_preco = (
                    True if "registro_preco" in self.request.POST else False
                )
                licitacao.contrato = True if "contrato" in self.request.POST else False
            else:
                licitacao = Licitacao(
                    modalidade=self.request.POST["modalidade"],
                    numero=self.request.POST["numero"],
                    processo=ProcessoAquisicao.objects.get(
                        pk=int(self.request.POST["processo"])
                    ),
                    registro_preco=(
                        True if "registro_preco" in self.request.POST else False
                    ),
                    contrato=True if "contrato" in self.request.POST else False,
                )
            try:
                licitacao.save()
            except Exception as e:
                obj["message"] = "Não foi possível gravar as informações!"
                obj["success"] = False
                self.log.exception(e)

        if self.request.POST["model"] == "participante":
            obj = {"success": True, "message": "", "produto": []}
            try:
                participante = Participante.objects.get(
                    Q(pessoa=int(self.request.POST["pessoa"]))
                )
            except Exception:
                participante = Participante(
                    pessoa=Pessoa.objects.get(pk=int(self.request.POST["pessoa"]))
                )
                try:
                    participante.save()
                except Exception as e:
                    obj["message"] = "Não foi possível gravar as informações!"
                    obj["success"] = False
                    self.log.exception(e)
            try:
                participante.licitacao.add(
                    Licitacao.objects.get(pk=int(self.request.POST["licitacao"]))
                )
            except Exception as e:
                obj["message"] = "Não foi possível gravar as informações!"
                obj["success"] = False
                self.log.exception(e)

        if self.request.POST["model"] == "produto":
            obj = {"success": True, "message": "", "produto": []}
            for pp in self.request.POST.getlist("itens"):
                try:
                    try:
                        produto_vencedor = ProdutoVencedor.objects.get(
                            Q(participante__pk=int(self.request.POST["vencedor"]))
                            & Q(licitacao__pk=int(self.request.POST["licitacao"]))
                        )
                    except Exception:
                        produto_vencedor = ProdutoVencedor(
                            participante=Participante.objects.get(
                                pk=int(self.request.POST["vencedor"])
                            ),
                            licitacao=Licitacao.objects.get(
                                pk=int(self.request.POST["licitacao"])
                            ),
                        )
                        produto_vencedor.save()
                    produto_vencedor.produto_processo.add(
                        ProdutoProcesso.objects.get(pk=int(pp))
                    )
                    self.create_ne_aquisicao(
                        produto_vencedor,
                        Licitacao.objects.get(
                            pk=int(self.request.POST["licitacao"])
                        ).processo.orcamento,
                        ProdutoProcesso.objects.get(pk=int(pp)),
                    )
                except Exception as e:
                    self.log.exception(e)
                    obj["message"] = "Não consegui adicionar o Produto!"
                    obj["produto"] = ["Não consegui adicionar o Produto!", pp]
                    obj["success"] = False

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @classmethod
    def create_ne_aquisicao(cls, produto_vencedor, tipo, produto_processo):
        if tipo == 1:
            try:
                ne = NEAquisicao.objects.get(
                    credor=produto_vencedor, produto_processo=produto_processo
                )
            except Exception:
                ne = NEAquisicao(
                    credor=produto_vencedor,
                    modalidade=1,
                    produto_processo=produto_processo,
                )
            ne.save()

    @classmethod
    def remove_ne_aquisicao(cls, produto_vencedor, tipo, produto_processo):
        if tipo == 1:
            try:
                NEAquisicao.objects.filter(
                    credor=produto_vencedor, produto_processo=produto_processo
                ).delete()
            except Exception as e:
                cls.log.exception(e)

    def add(self, args=[]):
        obj = {"success": True, "message": "", "produto": []}
        if self.request.POST["model"] == "participante":
            try:
                participante = Participante.objects.get(
                    Q(pessoa=int(self.request.POST["pessoa"]))
                    & Q(licitacao=int(self.request.POST["licitacao"]))
                )
            except Exception:
                participante = Participante(
                    pessoa=Pessoa.objects.get(pk=int(self.request.POST["pessoa"]))
                )

                try:
                    participante.save()
                except Exception as e:
                    obj["message"] = "Não foi possível gravar as informações!"
                    obj["success"] = False
                    self.log.exception(e)

            try:
                participante.licitacao.add(
                    Licitacao.objects.get(pk=int(self.request.POST["licitacao"]))
                )
            except Exception as e:
                obj["message"] = "Não foi possível gravar as informações!"
                obj["success"] = False
                self.log.exception(e)

        if self.request.POST["model"] == "produto":
            for pp in self.request.POST.getlist("itens"):
                try:
                    try:
                        produto_vencedor = ProdutoVencedor.objects.get(
                            Q(participante__pk=int(self.request.POST["vencedor"]))
                            & Q(licitacao__pk=int(self.request.POST["licitacao"]))
                        )
                    except Exception:
                        produto_vencedor = ProdutoVencedor(
                            participante=Participante.objects.get(
                                pk=int(self.request.POST["vencedor"])
                            ),
                            licitacao=Licitacao.objects.get(
                                pk=int(self.request.POST["licitacao"])
                            ),
                        )
                        produto_vencedor.save()
                    produto_vencedor.produto_processo.add(
                        ProdutoProcesso.objects.get(pk=int(pp))
                    )
                    self.create_ne_aquisicao(
                        produto_vencedor,
                        Licitacao.objects.get(
                            pk=int(self.request.POST["licitacao"])
                        ).processo.orcamento,
                        ProdutoProcesso.objects.get(pk=int(pp)),
                    )
                except Exception as e:
                    self.log.exception(e)
                    obj["message"] = "Não consegui adicionar o Produto!"
                    obj["produto"] = ["Não consegui adicionar o Produto!", pp]
                    obj["success"] = False
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {"success": True, "message": ""}
        if self.request.POST["model"] == "documento":
            try:
                PublicacaoLicitacao.objects.filter(
                    pk__in=self.request.POST.getlist("itens")
                ).delete()
                self.set_homologada(self.request.POST["licitacao"])
            except Exception as e:
                obj["message"] = "Não consegui remover Documento!"
                obj["success"] = False
                self.log.exception(e)
        if self.request.POST["model"] == "participante":
            try:
                for p in Participante.objects.filter(
                    pk__in=self.request.POST.getlist("itens")
                ):
                    p.licitacao.remove(
                        Licitacao.objects.get(pk=int(self.request.POST["licitacao"]))
                    )
            except Exception as e:
                obj["message"] = "Não consegui remover Participante!"
                obj["success"] = False
                self.log.exception(e)
        if self.request.POST["model"] == "produto":
            try:
                produto_vencedor = ProdutoVencedor.objects.get(
                    Q(participante__pk=int(self.request.POST["vencedor"]))
                    & Q(licitacao__pk=int(self.request.POST["licitacao"]))
                )
                for produto_processo in self.request.POST.getlist("itens"):
                    produto_vencedor.produto_processo.remove(
                        ProdutoProcesso.objects.get(pk=int(produto_processo))
                    )
                    self.remove_ne_aquisicao(
                        produto_vencedor,
                        Licitacao.objects.get(
                            pk=int(self.request.POST["licitacao"])
                        ).processo.orcamento,
                        produto_processo,
                    )
            except Exception as e:
                obj["message"] = "Não consegui adicionar o Produto!"
                obj["success"] = False
                self.log.exception(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        result = json.decode(self.request.POST["result"])
        if isinstance(result, dict):
            result = [result]
        try:
            for r in result:
                ProdutoProcesso.objects.filter(pk=int(r.get("codigo"))).update(
                    valor_unitario_lance=str(r.get("valor_unitario_lance")).replace(
                        ",", "."
                    ),
                    valor_unitario=str(r.get("valor_unitario_lance")).replace(",", "."),
                    valor_unitario_aditivo=str(r.get("valor_unitario_aditivo")).replace(
                        ",", "."
                    ),
                )
        except Exception as e:
            self.log.debug(e)


class CPLLicitacao(extjs.ExtCrud):
    class InstallMeta:
        controller = "CPLLicitacao"
        title = "Licitação"
        node_menu = "cpl"
        install = True

    class Form(forms.ModelForm):
        processo = AutoCompleteField(
            model=ProcessoAquisicao,
            controller="adm.compras.COMPRASProcessoAquisicao",
            label="Processo",
        )

        class Meta:
            exclude = []
            model = Licitacao
            exclude = ["arquivado", "finalizado", "data_cadastro", "homologada"]

    titles = {
        "PANEL": "Licitação",
        "LIST": "Gerenciador de Licitação",
        "NEW": "Novo(a) Licitação",
        "EDIT": "Editando um(a) Licitação",
        "DELETE": "Removendo um(a) Licitação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class CPLPublicacaoLicitacao(extjs.ExtCrud):
    class InstallMeta:
        controller = "CPLPublicacaoLicitacao"
        title = "Publicação de Licitação"
        node_menu = "cpl"
        install = True

    class Form(forms.ModelForm):
        licitacao = AutoCompleteField(
            model=Licitacao, controller=CPLLicitacao, label="Licitação"
        )
        arquivo = FileUploadField(label="Arquivo", required=False)

        class Meta:
            exclude = []
            model = PublicacaoLicitacao

    titles = {
        "PANEL": "Publicação de Licitação",
        "LIST": "Gerenciador de Publicação de Licitação",
        "NEW": "Novo(a) Publicação de Licitação",
        "EDIT": "Editando um(a) Publicação de Licitação",
        "DELETE": "Removendo um(a) Publicação de Licitação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class CPLParticipante(CustomAutocomplete):
    class InstallMeta:
        controller = "CPLParticipante"
        title = "Participante"
        node_menu = "cpl"
        install = True

    class Form(forms.ModelForm):
        pessoa = AutoCompleteField(model=Pessoa, label="Pessoa")

        class Meta:
            exclude = []
            model = Participante

    titles = {
        "PANEL": "Participante",
        "LIST": "Gerenciador de Participante",
        "NEW": "Novo(a) Participante",
        "EDIT": "Editando um(a) Participante",
        "DELETE": "Removendo um(a) Participante",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class CPLProdutoVencedor(CustomAutocomplete):
    class InstallMeta:
        controller = "CPLProdutoVencedor"
        title = "Produto Vencedor"
        node_menu = "cpl"
        install = True

    class Form(forms.ModelForm):
        participante = AutoCompleteField(
            model=Participante, father="CPLProdutoVencedor", label="Participante"
        )
        licitacao = AutoCompleteField(
            model=Licitacao, father="CPLProdutoVencedor", label="Licitação"
        )

        class Meta:
            exclude = []
            model = ProdutoVencedor

    titles = {
        "PANEL": "Vencedor de Licitação",
        "LIST": "Gerenciador de Vencedor de Licitação",
        "NEW": "Novo(a) Vencedor de Licitação",
        "EDIT": "Editando um(a) Vencedor de Licitação",
        "DELETE": "Removendo um(a) Vencedor de Licitação",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }
