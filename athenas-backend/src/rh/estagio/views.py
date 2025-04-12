# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms
from django.db import models as models_d
from django.db.models import Q

from contrib import extjs
from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, get_json_engine, getLogger
from engine.models import ControllerPermission
from engine.notification.models import Notification
from rh.estagio.models import (
    ApreciacaoComissao,
    ComissaoAvaliadora,
    Conceito,
    Configuracao,
    DecisaoChefeOrgao,
    EstagioAvaliacao,
    EstagioComissaoServidor,
    EstagioProbatorioServidor,
    FatorAvaliacao,
    IntegrantesComissao,
    ManifestacaoEstagio,
    QuesitoAvaliacao,
)
from rh.models import Publicacao, Servidor
from rh.views import RHPublicacao
from standard.questionario.models import (
    Elemento,
    Questao,
    Questionario,
    QuestionarioResposta,
    ReferenciaTextual,
    Resposta,
)
from standard.questionario.views import QMontarQuestionario, QQuestionario
from standard.views import AutoCompleteField

json = get_json_engine()
log = getLogger(__name__)


class GEPComissaoAvaliadora(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = ComissaoAvaliadora

    def json(self, args=[]):
        self.response.write("new toolkit.gep.ConfiguradorComissao()")
        self.response["content-type"] = "text/javascript"

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            self.log.info(self.request.POST)
            R = self.request.REQUEST
            start = int(R.get("start", 0))
            end = int(R.get("limit", 50)) + start

            query = ComissaoAvaliadora.objects.all()

            for comissao in query[start:end]:
                obj["collection"].append(
                    {
                        "pk": comissao.id,
                        "comissao_anterior": (
                            "%s" % comissao.comissao_anterior
                            if comissao.comissao_anterior
                            else "Não informada"
                        ),
                        "publicacao": "%s" % comissao.publicacao,
                        "data_inicio": (
                            DateUtils.date_to_str(comissao.data_inicio)
                            if comissao.data_inicio
                            else ""
                        ),
                        "data_fim": (
                            DateUtils.date_to_str(comissao.data_fim)
                            if comissao.data_fim
                            else "Não informada"
                        ),
                    }
                )
        except Exception as e:
            self.log.info(e)
        else:
            obj.update(count=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            comissao = ComissaoAvaliadora.objects.get(
                pk=int(self.request.POST["pk_comissao"])
            )
            obj.update(
                {
                    "collection": {
                        "pk": comissao.pk,
                        "comissao_anterior": comissao.comissao_anterior_id,
                        "publicacao": comissao.publicacao_id,
                        "data_inicio": (
                            DateUtils.date_to_str(comissao.data_inicio)
                            if comissao.data_inicio
                            else ""
                        ),
                        "data_fim": (
                            DateUtils.date_to_str(comissao.data_fim)
                            if comissao.data_fim
                            else ""
                        ),
                    },
                    "success": True,
                }
            )
        except Exception as e:
            obj.update(
                {
                    "message": "Não consegui encontrar a comissão desejada.",
                    "success": False,
                }
            )
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def create(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        try:
            self.log.info(self.request.POST)
            publicacao = Publicacao.objects.get(pk=int(self.request.POST["publicacao"]))
            comissao_anterior = (
                ComissaoAvaliadora.objects.get(
                    pk=int(self.request.POST["comissao_anterior"])
                )
                if self.request.POST["comissao_anterior"]
                else None
            )
            comissao = ComissaoAvaliadora(
                comissao_anterior=comissao_anterior,
                publicacao=publicacao,
                data_inicio=DateUtils.str_to_date(self.request.POST["data_inicio"]),
                data_fim=(
                    DateUtils.str_to_date(self.request.POST["data_fim"])
                    if self.request.POST["data_fim"]
                    else None
                ),
            )
            comissao.save()

        except Exception as e:
            # transaction.rollback()
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            obj.update(success=False)
            self.log.info(e)
        else:
            # transaction.commit()
            obj.update(success=True)
            obj.update(message="Comissão salva com sucesso!")
            self.log.info("Comissão salva com sucesso")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        try:
            comissao = ComissaoAvaliadora.objects.get(
                pk=int(self.request.REQUEST.get("pk_comissao"))
            )
            publicacao = (
                Publicacao.objects.get(pk=int(self.request.REQUEST.get("publicacao")))
                if self.request.REQUEST.get("publicacao")
                else None
            )
            comissao_anterior = (
                ComissaoAvaliadora.objects.get(
                    pk=int(self.request.REQUEST.get("comissao_anterior"))
                )
                if self.request.REQUEST.get("comissao_anterior")
                else None
            )

            comissao.comissao_anterior = comissao_anterior
            comissao.publicacao = publicacao
            comissao.data_inicio = (
                DateUtils.str_to_date(self.request.REQUEST.get("data_inicio"))
                if self.request.REQUEST.get("data_inicio")
                else None
            )
            comissao.data_fim = (
                DateUtils.str_to_date(self.request.REQUEST.get("data_fim"))
                if self.request.REQUEST.get("data_fim")
                else None
            )
            comissao.save()

            obj.update(message="Comissão alterada com sucesso!")
            obj.update(success=True)

        except Exception as e:
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            obj.update(success=False)
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}

        try:
            comissoes = ComissaoAvaliadora.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for comissao in comissoes:
                comissao.delete()
        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_integrantes(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.GET)
        try:
            comissao = IntegrantesComissao.objects.filter(
                comissao_id=self.request.GET.get("pk_comissao")
            )
            for integrante in comissao:
                obj["collection"].append(
                    {
                        "pk": integrante.pk,
                        "pk_comissao": integrante.comissao_id.pk,
                        "pk_integrante": integrante.servidor_id.pk,
                        "nome_integrante": "%s"
                        % integrante.servidor_id.pessoa_fisica.nome,
                        "funcao": "%s" % integrante.get_display(),
                        "tipo_integrante": integrante.tipo_participante,
                        "impedimento": "Sim" if integrante.impedimento else "Não",
                    }
                )

        except Exception as e:
            self.log.info(e)
        # obj.update(count = query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_list_integrantes(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.POST)
        try:
            integrante_comissao = IntegrantesComissao.objects.get(
                servidor_id=self.request.POST.get("pk_integrante"),
                comissao_id=self.request.POST.get("pk_comissao"),
                tipo_participante=self.request.POST.get("tipo_integrante"),
            )
            obj.update(
                {
                    "collection": {
                        "pk_comissao": integrante_comissao.comissao_id.pk,
                        "integrante": integrante_comissao.servidor_id.pk,
                        "tipo_integrante": integrante_comissao.tipo_participante,
                        "impedimento": "2" if integrante_comissao.impedimento else "1",
                    },
                    "success": True,
                }
            )
        except Exception as e:
            obj.update(
                {
                    "message": "Não consegui encontrar o integrante desejado.",
                    "success": False,
                }
            )
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create_integrante(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        try:
            self.log.info(self.request.POST)
            comissao = ComissaoAvaliadora.objects.get(
                pk=int(self.request.POST["pk_comissao"])
            )
            servidor = Servidor.objects.get(pk=int(self.request.POST["integrante"]))
            ordem = (
                int(
                    IntegrantesComissao.objects.filter(comissao_id=comissao)
                    .aggregate(ultima_posicao=models_d.Max("ordem"))
                    .get("ultima_posicao")
                    or 0
                )
                + 1
            )
            integrante_comissao = IntegrantesComissao.objects.create(
                comissao_id=comissao,
                servidor_id=servidor,
                tipo_participante=self.request.POST["tipo_integrante"],
                ordem=ordem,
                impedimento=(
                    True
                    if self.request.POST["impedimento"]
                    and int(self.request.POST["impedimento"]) == 2
                    else False
                ),
            )
            integrante_comissao.save()

        except Exception as e:
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            obj.update(success=False)
            self.log.info(e)
        else:
            obj.update(success=True)
            obj.update(message="Integrante adicionado sucesso!")
            self.log.info("Integrante adicionado com sucesso!")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update_integrantes(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)
        try:
            integrante_comissao = IntegrantesComissao.objects.get(
                pk=int(self.request.POST.get("pk_comissao_servidor"))
            )

            servidor = Servidor.objects.get(pk=int(self.request.POST.get("integrante")))
            comissao = ComissaoAvaliadora.objects.get(
                pk=int(self.request.POST.get("pk_comissao"))
            )

            integrante_comissao.comissao_id = comissao
            integrante_comissao.servidor_id = servidor
            integrante_comissao.tipo_participante = self.request.POST.get(
                "tipo_integrante"
            )
            integrante_comissao.impedimento = (
                True
                if self.request.POST["impedimento"]
                and int(self.request.POST["impedimento"]) == 2
                else False
            )
            integrante_comissao.save()

            obj.update(success=True)

        except Exception as e:
            obj.update(success=False)
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove_integrante(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.POST)
        try:
            integrante = IntegrantesComissao.objects.get(
                servidor_id=self.request.POST.get("pk_integrante"),
                comissao_id=self.request.POST.get("pk_comissao"),
                tipo_participante=self.request.POST.get("tipo_participante"),
            )
            integrante.delete()

        except Exception as e:
            obj.update(success=False)
            obj.update(message="Não consegui remover os dados.")
            self.log.info(e)
        else:
            self.log.info("Integrante removido com sucesso!")
            obj.update(message="Removido com sucesso!")
            obj.update(success=True)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def move_integrante(self, args=[]):
        obj = self._move_up() if args[0] == "up" else self._move_down()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def _move_up(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        query = IntegrantesComissao.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = IntegrantesComissao.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception as e:
                self.log.error(e)
                obj.update(message="Não consegui encontrar o participante.")
            else:
                q.reorder()
                for cs in query.order_by("ordem"):
                    cs.move_up()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj

    def _move_down(self):
        obj = {"success": False, "message": "Nada foi feito ainda."}
        query = IntegrantesComissao.objects.filter(
            pk__in=self.request.REQUEST.getlist("pk")
        )
        if query.exists() is True:
            try:
                q = IntegrantesComissao.objects.get(
                    pk=query.values("pk").distinct().latest("pk").get("pk")
                )
            except Exception:
                obj.update(message="Não consegui encontrar o participante")
            else:
                q.reorder()
                for cs in query.order_by("-ordem"):
                    cs.move_down()
                obj.update(success=True)
        else:
            obj.update(
                message="Não foi selecionado nenhum item ou os itens já foram removidos."
            )

        return obj


class GEPConceito(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Conceito

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 70,
            },
            {
                "header": "Descrição",
                "sortable": True,
                "dataIndex": "descricao",
                "key": "titulo",
                "width": 500,
            },
            {
                "header": "Valor Inicial",
                "sortable": True,
                "dataIndex": "valor_inicial",
                "key": "data_inicio",
                "width": 80,
            },
            {
                "header": "Valor Final",
                "sortable": True,
                "dataIndex": "valor_final",
                "key": "data_fim",
                "width": 80,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Conceito",
        "LIST": "Configurador de Conceitos",
        "NEW": "Novo Conceito",
        "EDIT": "Editando Conceito",
        "DELETE": "Removendo Conceito",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GEPConfiguracao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = Configuracao

        configuracao_anterior = AutoCompleteField(
            model=Configuracao,
            controller="GEPConfiguracao",
            label="Configuração Anterior",
            required=False,
        )
        questionario = AutoCompleteField(
            model=Questionario, controller=QQuestionario, label="Questionário"
        )
        questionario_manifestacao_servidor = AutoCompleteField(
            model=Questionario,
            controller=QQuestionario,
            label="Questionário Manifestação do Servidor",
        )
        publicacao = AutoCompleteField(
            model=Publicacao, controller=RHPublicacao, label="Publicação"
        )

    def get_columns_grid(self, args=[]):
        obj = [
            {
                "header": "Chave",
                "sortable": True,
                "dataIndex": "id",
                "key": "id",
                "width": 40,
            },
            {
                "header": "Questionário",
                "sortable": True,
                "dataIndex": "questionario",
                "key": "questionario",
                "width": 230,
            },
            {
                "header": "Publicação",
                "sortable": True,
                "dataIndex": "publicacao",
                "key": "publicacao",
                "width": 150,
            },
            {
                "header": "Qtd. Avaliações",
                "sortable": True,
                "dataIndex": "qtde_avaliacoes",
                "key": "qtde_avaliacoes",
                "width": 100,
            },
            {
                "header": "Meses entre Avaliações",
                "sortable": True,
                "dataIndex": "qtde_meses_entre_avaliacao",
                "key": "qtde_meses_entre_avaliacao",
                "width": 150,
            },
            {
                "header": "Porc. para aprovação",
                "sortable": True,
                "dataIndex": "porc_aprovacao",
                "key": "porc_aprovacao",
                "width": 150,
            },
            {
                "header": "Data Início",
                "sortable": True,
                "dataIndex": "data_inicio",
                "key": "data_inicio",
                "width": 100,
            },
            {
                "header": "Data Fim",
                "sortable": True,
                "dataIndex": "data_fim",
                "key": "data_fim",
                "width": 100,
            },
        ]
        self.response.write(json.encode(obj))

    titles = {
        "PANEL": "Configuração",
        "LIST": "Configuração de Estágio",
        "NEW": "Nova Configuração",
        "EDIT": "Editando Configuração",
        "DELETE": "Removendo Configuração",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class GEPGestorEstagio(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = EstagioProbatorioServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.GestorEstagio()")

    def apply_filter(self, query):
        qs = []
        self.log.debug(self.request.POST)
        if "keyword" in self.request.POST:
            self.log.debug("FILTER: %s" % self.request.POST["keyword"])
            qs.append(
                Q(
                    posse_servidor__servidor__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    posse_servidor__servidor__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )

        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        query = query.filter(q) if q else query
        if (
            "tipo" in self.request.POST
            and self.request.POST.get("tipo") == "finalizado"
        ):
            query = query.filter(Q(status=2))
        elif (
            "tipo" in self.request.POST and self.request.POST.get("tipo") == "andamento"
        ):
            query = query.filter(Q(status=1, bloqueada=False))
        elif (
            "tipo" in self.request.POST and self.request.POST.get("tipo") == "bloqueado"
        ):
            query = query.filter(Q(bloqueada=True, status=1))
        elif (
            "tipo" in self.request.POST
            and self.request.POST.get("tipo") == "aguardando_comissao"
        ):
            query = query.filter(Q(status=3, bloqueada=True)).order_by("-fim_estagio")
        elif (
            "tipo" in self.request.POST
            and self.request.POST.get("tipo") == "order_name"
        ):
            query = query.filter(Q(status=1)).order_by("posse_servidor__servidor")
        elif (
            "tipo" in self.request.POST
            and self.request.POST.get("tipo") == "estabilizacao"
        ):
            query = query.filter(Q(status=3, bloqueada=True)).order_by("-fim_estagio")
        elif "tipo" in self.request.POST and self.request.POST.get("tipo") == "todos":
            query = query.all()
        else:
            query = query.filter(Q(status=1, bloqueada=False))

        return query

    def list(self, args=[]):
        try:
            query = EstagioProbatorioServidor.objects.all()
            query = self.apply_filter(query)
            if (
                "tipo" in self.request.POST
                and self.request.POST.get("tipo") == "aguardando_finalizacao"
            ):
                obj = self.aguardando_finalizacao(query)
            else:
                obj = self.list_normal(query)

        except Exception as e:
            self.log.error(e)

        obj.update(totalRows=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def aguardando_finalizacao(self, query):
        obj = {"collection": [], "totalRows": 0}
        # R = self.request.REQUEST
        # start = int(R.get('start', 0))
        # end = int(R.get('limit', 50)) + start
        for ge in query:
            states = ge.get_state_icons()
            if ge.get_wait_finish():
                obj["collection"].append(
                    {
                        "pk": ge.id,
                        "posse_servidor": "%s" % ge.posse_servidor,
                        "posse_servidor_pk": ge.posse_servidor.pk,
                        "servidor_pk": ge.posse_servidor.servidor.pk,
                        "nome_servidor": "%d : %s"
                        % (ge._servidor_estagio_matricula, ge._servidor_estagio_nome),
                        "cargo": ge.posse_servidor.quadro.cargo.codigo,
                        "cargo_id": ge.posse_servidor.quadro.cargo_id,
                        "etapa_atual": ge.current_stage,
                        "periodo_anterior": ge.avaliacoes_realizadas,
                        "media": round(ge.media, 2) if ge.media else "---",
                        "data_exercicio": DateUtils.date_to_str(ge._inicio_estagio),
                        "ultima_avaliacao": (
                            DateUtils.date_to_str(ge.ultima_avaliacao)
                            if ge.ultima_avaliacao
                            else "---"
                        ),
                        "proxima_avaliacao": (
                            DateUtils.date_to_str(ge.proxima_avaliacao)
                            if ge.proxima_avaliacao
                            else "---"
                        ),
                        "fim_estagio": (
                            DateUtils.date_to_str(ge.fim_estagio)
                            if ge.fim_estagio
                            else ""
                        ),
                        "prazos": "%s dia(s)" % ge.dias,
                        "bloqueada": ge.bloqueada,
                        "estado": ge.get_situacao(),
                        "questionario": "%s" % ge.configuracao.questionario,
                        "questionario_pk": ge.configuracao.questionario.id,
                        "questionario_manifestacao_pk": ge.configuracao.questionario_manifestacao_servidor_id,
                        "status": [
                            {
                                "iconCls": st["iconCls"],
                                "alt": st["alt"],
                                "title": st["alt"],
                            }
                            for st in states
                        ],
                    }
                )
        return obj

    def list_normal(self, query):
        obj = {"collection": [], "totalRows": 0}
        R = self.request.REQUEST
        start = int(R.get("start", 0))
        end = int(R.get("limit", 50)) + start
        for ge in query[start:end]:

            # states = ge.get_state_icons()
            # qs = ge.manifestacao_servidor.all()
            # questionario_manifestacao_pk = qs[0].questionario_resposta_id if qs.exists() else None
            obj["collection"].append(
                {
                    "pk": ge.id,
                    "posse_servidor": "%s" % ge.posse_servidor,
                    "posse_servidor_pk": ge.posse_servidor.pk,
                    "servidor_pk": ge.posse_servidor.servidor.pk,
                    "nome_servidor": "%d : %s"
                    % (ge._servidor_estagio_matricula, ge._servidor_estagio_nome),
                    "cargo": ge.posse_servidor.quadro.cargo.codigo,
                    "cargo_id": ge.posse_servidor.quadro.cargo_id,
                    "etapa_atual": ge.current_stage,
                    "periodo_anterior": ge.avaliacoes_realizadas,
                    "media": round(ge.media, 2) if ge.media else "---",
                    "data_exercicio": DateUtils.date_to_str(ge._inicio_estagio),
                    "ultima_avaliacao": (
                        DateUtils.date_to_str(ge.ultima_avaliacao)
                        if ge.ultima_avaliacao
                        else "---"
                    ),
                    "proxima_avaliacao": (
                        DateUtils.date_to_str(ge.proxima_avaliacao)
                        if ge.proxima_avaliacao
                        else "---"
                    ),
                    "fim_estagio": (
                        DateUtils.date_to_str(ge.fim_estagio) if ge.fim_estagio else ""
                    ),
                    "prazos": "%s dia(s)" % ge.dias,
                    "bloqueada": ge.bloqueada,
                    "estado": ge.get_situacao(),
                    "questionario": "%s" % ge.configuracao.questionario,
                    "questionario_pk": ge.configuracao.questionario.id,
                    "questionario_manifestacao_pk": ge.configuracao.questionario_manifestacao_servidor_id,
                    # 'status': [
                    #     {
                    #         'iconCls': st['iconCls'],
                    #         'alt': st['alt'],
                    #         'title': st['alt']
                    #     } for st in states
                    # ],
                }
            )
        return obj

    def get_information(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        try:
            serv = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["servidor"]
            )

            obj["collection"].append(
                {
                    "pk": serv.pk,
                    "nome_servidor": "%s" % (serv._servidor_estagio_nome),
                    "posse_servidor": "%s" % serv.posse_servidor,
                    "lotacao": "%s" % serv.posse_servidor.servidor.workplace_current,
                    "cargo": "%s - %s "
                    % (
                        serv.posse_servidor.quadro.cargo.nome,
                        serv.posse_servidor.quadro.especialidade,
                    ),
                    "chefe_atual": "%s" % serv.posse_servidor.servidor.chefe_imediato,
                    "periodo_estagio": serv.get_periodo_estagio(),
                }
            )
        except Exception as e:
            self.log.error(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def bloquear_etapa(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        try:
            estagio_servidor = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk"]
            )
            estagio_servidor.bloqueia_etapa()
            obj["message"] = "%sª Etapa de %s bloqueada com sucesso." % (
                estagio_servidor.current_stage,
                estagio_servidor._servidor_estagio_nome,
            )
            obj["success"] = True

        except Exception as e:
            self.log.info(e)
            obj["message"] = "Ocorreu um erro ao bloquear a etapa"
            obj["success"] = False

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def desbloquear_etapa(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        try:
            estagio_servidor = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk"]
            )
            if estagio_servidor.bloqueada is False:
                obj["message"] = "Esta etapa não está bloqueada."
            else:
                estagio_servidor.desbloqueia_etapa()
                obj["message"] = "%sª Etapa de %s desbloqueada com sucesso." % (
                    estagio_servidor.current_stage,
                    estagio_servidor._servidor_estagio_nome,
                )
            obj["success"] = True

        except Exception as e:
            self.log.info(e)
            obj["message"] = "Ocorreu um erro ao bloquear a etapa"
            obj["success"] = False

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def finalizar_etapa(self, args=[]):
        obj = {"collection": [], "totalRows": 0, "success": False}
        try:
            self.log.info(self.request.POST)
            estagio_servidor = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk"]
            )

            if (
                estagio_servidor._acao_estado_avalicao(3)
                and estagio_servidor.get_wait_finish()
            ):  # 3 = ACAO FINALIZAR ETAPA
                avaliacao = EstagioAvaliacao.objects.get(
                    avaliado=estagio_servidor.pk,
                    periodo_avaliado=estagio_servidor.current_stage,
                )
                estagio_servidor.atualiza_etapas()
                avaliacao.etapa_finalizada_por()
                obj["message"] = "%sª Etapa de %s atualizada com sucesso." % (
                    estagio_servidor.avaliacoes_realizadas,
                    estagio_servidor._servidor_estagio_nome,
                )
                obj["success"] = True
                self.log.info(
                    "%sª Etapa de: %s atualizada com sucesso."
                    % (
                        estagio_servidor.avaliacoes_realizadas,
                        estagio_servidor._servidor_estagio_nome,
                    )
                )
                # transaction.commit()
            else:
                raise Exception(str(EstagioProbatorioServidor.FinalizacaoEmDisputa()))
                # transaction.rollback()
        except EstagioProbatorioServidor.DoesNotExist as e:
            # transaction.rollback()
            self.log.info(e)
            obj["message"] = "Servidor não encontrado."
            # transaction.rollback()
        except EstagioAvaliacao.DoesNotExist as e:
            # transaction.rollback()
            self.log.info(e)
            obj["message"] = (
                "Não foi realizada nenhuma avaliacão de: %s para esta etapa."
                % estagio_servidor._servidor_estagio_nome
            )
            # transaction.rollback()
        except Exception as e:
            # transaction.rollback()
            obj["message"] = str(e)
            self.log.info(e)
            # transaction.rollback()
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def montar_comissao(self, args=[]):
        obj = {
            "collection": [],
            "totalRows": 0,
            "message": "Nada aconteceu ainda.",
            "success": False,
        }
        self.log.info(self.request.POST)
        try:
            data = datetime.now()
            eps = EstagioProbatorioServidor.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            )
            for estagio_servidor in eps:
                if (
                    estagio_servidor.liberado_para_formar_comissao()
                    and not estagio_servidor.comissao_estagio.exists()
                ):
                    comissao_avaliadora = ComissaoAvaliadora.objects.get(
                        Q(
                            Q(data_inicio__lte=data, data_fim__isnull=True)
                            | Q(data_inicio__lte=data, data_fim__gte=data)
                        )
                    )
                    chefe_imediato = (
                        estagio_servidor.posse_servidor.servidor.chefe_imediato
                    )
                    ecs = EstagioComissaoServidor(
                        estagio_prob_servidor=estagio_servidor
                    )
                    ecs.save()
                    suplentes = IntegrantesComissao.objects.filter(
                        comissao_id=comissao_avaliadora.id, tipo_participante__in=[4]
                    )
                    integ = IntegrantesComissao.objects.filter(
                        pk__in=ecs.integrante_comissao_avaliadora.values("id")
                    )
                    for integrante in IntegrantesComissao.objects.filter(
                        comissao_id=comissao_avaliadora.id,
                        tipo_participante__in=[1, 2, 3],
                    ):
                        if chefe_imediato == integrante.servidor_id:
                            ecs.integrante_comissao_avaliadora.add(
                                suplentes.filter().exclude(pk__in=integ.values("id"))[
                                    0
                                ],
                                bulk=False,
                            )
                        elif (
                            estagio_servidor.posse_servidor.servidor
                            == integrante.servidor_id
                        ):
                            ecs.integrante_comissao_avaliadora.add(
                                suplentes.filter().exclude(pk__in=integ.values("id"))[
                                    0
                                ],
                                bulk=False,
                            )
                        elif integrante.impedimento:
                            ecs.integrante_comissao_avaliadora.add(
                                suplentes.filter().exclude(pk__in=integ.values("id"))[
                                    0
                                ],
                                bulk=False,
                            )
                        else:
                            ecs.integrante_comissao_avaliadora.add(integrante)
                    ecs.save()
                else:
                    self.log.info(
                        "Estágio do(a) Servidor(a): %s não estáliberado para formar comissao"
                        % estagio_servidor._servidor_estagio
                    )
                    # raise Exception('Estágio de %s disponivel para formar comissão.'% eps._servidor_estagio))
                    # obj['message'] = 'Estágio de %s disponivel para formar comissão.' % eps._servidor_estagio
        except Exception as e:
            self.log.info(e)
            obj["message"] = "Estágio não disponivel para formar comissão."
        else:
            obj["message"] = "Rotina concluida."
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def finalizar_processo(self, args=[]):
        obj = {
            "collection": [],
            "totalRows": 0,
            "message": "Nada aconteceu ainda.",
            "success": False,
        }
        self.log.info(self.request.POST)
        try:
            eps = EstagioProbatorioServidor.objects.filter(
                pk__in=self.request.POST.getlist("pks")
            )
            for estagio_servidor in eps:
                if estagio_servidor.valida_ciencia_decisao_estagio():
                    estagio_servidor.status = 2
                    estagio_servidor.save()
                else:
                    self.log.info(
                        "O estágio de %s não possui decisão ainda do chefe do orgão."
                        % estagio_servidor
                    )
        except Exception as e:
            self.log.info(e)
            obj["message"] = "Estágio não disponivel para formar comissão."
        else:
            obj["message"] = "Rotina realizada com sucesso."
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_reports(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            self.log.info(self.request.POST)
            eps = EstagioProbatorioServidor.objects.get(
                posse_servidor__servidor__pk=self.request.POST["servidor"]
            )
            obj["collection"].append(
                {
                    "pk_servidor": self.request.POST["servidor"],
                    "etapa": self.request.POST["etapa"],
                    "questionario_avaliacao": eps.configuracao.questionario_id,
                    "questionario_manifestacao": eps.configuracao.questionario_manifestacao_servidor_id,
                    "cargo": eps.posse_servidor.quadro.cargo_id,
                }
            )
            obj["success"] = True
        except Exception as e:
            self.log.info(e)
            obj["message"] = "Ocorreu um erro ao buscar os dados."
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPAvaliacaoEstagio(QMontarQuestionario):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = EstagioProbatorioServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.GestorEstagioAdmin()")

    def get_medias(self, args=[]):
        obj = {"collection": []}
        try:
            estagio_servidor = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk"]
            )
            avaliacoes = []
            media_comissao = None
            for avaliado in estagio_servidor.avaliacoes.order_by("periodo_avaliado"):
                media_geral = 0
                flag_count = 0
                fator_list = []
                media_comissao = avaliado.media_comissao
                for fator in estagio_servidor.configuracao.fator_avaliacao.all():
                    soma = 0
                    conceito = None
                    for quesito in fator.quesito_avaliacao.all():
                        for elem in quesito.elemento.all():
                            for (
                                resp
                            ) in avaliado.questionario_resposta.resposta_set.all():
                                if elem.elemento.id == resp.questao_id:
                                    soma += resp.peso
                        media = float(soma) / float(quesito.count_elementos)
                        media_geral += media
                        flag_count += 1
                        for conc in avaliado.avaliado.configuracao.conceitos.all():
                            if (
                                media >= conc.valor_inicial
                                and media <= conc.valor_final
                            ):
                                conceito = conc.descricao
                        # media_fator = (float(soma) / float(quesito.count_elementos))
                        fator_list.append(
                            {
                                "conceito": conceito,
                                "descricao": fator.descricao,
                                "media": "%0.2f"
                                % (float(soma) / float(quesito.count_elementos)),
                            }
                        )

                media_etapa = media_geral / flag_count
                avaliacoes.append(
                    {
                        "avaliador": "%s " % avaliado.avaliador,
                        "periodo_avaliado": avaliado.periodo_avaliado,
                        "data": DateUtils.date_to_str(avaliado.criado_em),
                        "fator": fator_list,
                        "media_etapa": round(media_etapa, 2),
                        "media_comissao": (
                            "Média informada pela comissão: %s" % media_comissao
                            if media_comissao
                            else ""
                        ),
                    }
                )
            obj["collection"].append(
                {
                    "pk": estagio_servidor.pk,
                    "servidor": "%s" % estagio_servidor._servidor_estagio_nome,
                    "cargo": "%s - %s "
                    % (
                        estagio_servidor.posse_servidor.quadro.cargo.nome,
                        estagio_servidor.posse_servidor.quadro.especialidade,
                    ),
                    "matricula": estagio_servidor._servidor_estagio_matricula,
                    "lotacao": "%s"
                    % estagio_servidor.posse_servidor.servidor.workplace_current,
                    "inicio_estagio": DateUtils.date_to_str(
                        estagio_servidor._inicio_estagio
                    ),
                    "fim_estagio": (
                        DateUtils.date_to_str(estagio_servidor.fim_estagio)
                        if estagio_servidor.fim_estagio
                        else DateUtils.date_to_str(estagio_servidor.get_fim_estagio())
                    ),
                    "fator_avaliacao": avaliacoes or [],
                }
            )

        except Exception as e:
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def apply_filter(self, query):
        qs = []
        self.log.debug(self.request.POST)
        if "keyword" in self.request.POST:
            self.log.debug("FILTER: %s" % self.request.POST["keyword"])
            qs.append(
                Q(
                    posse_servidor__servidor__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    posse_servidor__servidor__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )

        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        query = query.filter(q) if q else query
        if (
            "tipo" in self.request.POST
            and self.request.POST.get("tipo") == "finalizado"
        ):
            query = query.filter(Q(status=2))
        elif (
            "tipo" in self.request.POST and self.request.POST.get("tipo") == "andamento"
        ):
            query = query.filter(Q(status=1))
        elif "tipo" in self.request.POST and self.request.POST.get("tipo") == "todos":
            query = query.all()
        else:
            query = query.filter(Q(status=1))
        return query

    def list(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        R = self.request.REQUEST
        start = int(R.get("start", 0))
        end = int(R.get("limit", 50)) + start
        try:
            self.log.info(self.request.user.servidor)
            chefe = self.request.user.servidor
            query = EstagioProbatorioServidor.objects.filter(
                posse_servidor__servidor__in=chefe.subordinados.all()
            )
            query = self.apply_filter(query)
            for estagio_servidor in query[start:end]:
                # states = estagio_servidor.get_state_icons()
                obj["collection"].append(
                    {
                        "pk": estagio_servidor.id,
                        "posse_servidor": "%s" % estagio_servidor.posse_servidor,
                        "posse_servidor_pk": estagio_servidor.posse_servidor.pk,
                        "servidor_pk": estagio_servidor.posse_servidor.servidor.pk,
                        "nome_servidor": "%d : %s"
                        % (
                            estagio_servidor._servidor_estagio_matricula,
                            estagio_servidor._servidor_estagio_nome,
                        ),
                        "data_exercicio": DateUtils.date_to_str(
                            estagio_servidor._inicio_estagio
                        ),
                        "cargo": estagio_servidor.posse_servidor.quadro.cargo.codigo,
                        "cargo_id": estagio_servidor.posse_servidor.quadro.cargo_id,
                        "etapa_atual": estagio_servidor.current_stage,
                        "media": (
                            round(estagio_servidor.media, 2)
                            if estagio_servidor.media
                            else "---"
                        ),
                        "ultima_avaliacao": (
                            DateUtils.date_to_str(estagio_servidor.ultima_avaliacao)
                            if estagio_servidor.ultima_avaliacao
                            else "---"
                        ),
                        "proxima_avaliacao": (
                            DateUtils.date_to_str(estagio_servidor.proxima_avaliacao)
                            if estagio_servidor.proxima_avaliacao
                            else "---"
                        ),
                        "questionario": "%s"
                        % estagio_servidor.configuracao.questionario,
                        "questionario_pk": estagio_servidor.configuracao.questionario.id,
                        "questionario_manifestacao_pk": estagio_servidor.configuracao.questionario_manifestacao_servidor_id,
                        "prazos": "%s dia(s)" % estagio_servidor.dias,
                        "bloqueada": estagio_servidor.bloqueada,
                        "periodo_anterior": estagio_servidor.avaliacoes_realizadas,
                        "estado": estagio_servidor.get_situacao(),
                        # 'status': [
                        #     {
                        #         'iconCls': st['iconCls'],
                        #         'alt': st['alt'],
                        #         'title': st['alt']
                        #     } for st in states
                        # ],
                    }
                )
        except Exception as e:
            self.log.error(e)

        obj.update(totalRows=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_list_questionario(self, args=[]):
        # metodo que sobrescreve o list_questionario, exibe o formulario de questionario, do  app questionario
        obj = {"collection": [], "totalRows": 0}
        self.log.info(args)
        try:
            periodo = self.request.POST["periodo"]
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
            qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            avaliacoes = EstagioAvaliacao.objects.filter(avaliado=args[1])

            # verifica se ja foi finalizada todas as etapas
            if not avaliacoes.count() >= qtde_periodos or periodo == qtde_periodos:
                obj = None if len(args) == 0 else self.list_questionario(*args)
            else:
                obj["message"] = str(EstagioAvaliacao.EstagioFinalizado())
                obj["success"] = False

            # verifica se a etapa já está liberada
            if not estagio_servidor.is_released:
                obj["collection"] = []
                obj["message"] = str(EstagioAvaliacao.AvaliacaoNaoLiberada())
                obj["success"] = False
            # caso os dados de gestor estagio não tenham sido atualizados ainda impede a avaliacao com a mesma etapa
            aval_list = []
            for aval in avaliacoes:
                aval_list.append(aval.periodo_avaliado)
            if estagio_servidor.current_stage in aval_list:
                obj["collection"] = []
                obj["message"] = str(EstagioAvaliacao.AvaliacaoRealizada())
                obj["success"] = False

            # verifica se o estagio esta bloqueado
            if estagio_servidor.bloqueada is True:
                obj["collection"] = []
                obj["message"] = str(EstagioAvaliacao.AvaliacaoBloqueada())
                obj["success"] = False

        except EstagioAvaliacao.DoesNotExist as e:
            self.log.info(e)
            obj["message"] = "Nenhuma Avaliação encontrada."
        except Exception as e:
            self.log.error(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_resposta_avaliacao(self, args=[]):
        obj = {"count": 0, "collection": []}
        try:
            self.log.info(args)
            obj = None if len(args) == 0 else self.get_data_resposta(*args)
        except Exception as e:
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def save_avaliacao_estagio(self, args=[]):
        obj = {"collection": [], "success": False, "totalRows": 0}
        self.log.info(self.request.POST)
        # pk_qr = self.request.POST['pk_questionario_resposta']
        try:
            gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk_gestor_estagio"]
            )
            servidor_avaliado = gestor_estagio_avaliado.posse_servidor.servidor
            gestor_estagio_avaliador = self.request.user.servidor
            questionario_resposta = QuestionarioResposta.objects.get(
                pk=self.request.POST["pk_questionario_resposta"]
            )
            periodo_avaliado = gestor_estagio_avaliado.current_stage
            dias_interrompidos = NewDateRange(
                gestor_estagio_avaliado.next_evaluation(),
                gestor_estagio_avaliado.proxima_avaliacao,
            )

            estagio_avaliacao = EstagioAvaliacao(
                questionario_resposta=questionario_resposta,
                avaliado=gestor_estagio_avaliado,
                avaliador=gestor_estagio_avaliador,
                periodo_avaliado=periodo_avaliado,
                data_inicio_etapa=gestor_estagio_avaliado.ultima_avaliacao
                or gestor_estagio_avaliado._inicio_estagio,
                dias_interrompidos=(
                    0 if dias_interrompidos.days == 1 else dias_interrompidos.days
                ),
                data_fim_etapa=gestor_estagio_avaliado.proxima_avaliacao,
            )
            estagio_avaliacao.save()

            Notification.notify(
                "gep-avaliacao-chefe",
                servidor_avaliado,
                types=("SYS",),
                **{
                    "from": str(gestor_estagio_avaliador),
                    "period": str(periodo_avaliado),
                }
            )

        except Exception as e:
            # transaction.rollback()
            log.debug(e)
            QuestionarioResposta.objects.get(
                pk=self.request.POST["pk_questionario_resposta"]
            ).delete()
            obj.update(message="Ocorreu um erro ao salvar avaliação!")
        else:
            # transaction.commit()
            self.log.info("Avaliação salva com sucesso")
            obj.update(message="Avaliação salva com sucesso!")
            obj.update(success=True)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def save_alteracao_avaliacao_estagio(self, args=[]):
        obj = {"collection": [], "success": False, "totalRows": 0}
        self.log.info(self.request.POST)
        try:
            gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk_gestor_estagio"]
            )

            if gestor_estagio_avaliado._acao_estado_avalicao(
                1
            ):  # ACAO ALTERAR UMA AVALIACAO
                gestor_estagio_avaliador = self.request.user.servidor
                EstagioAvaliacao.objects.get(
                    avaliado=gestor_estagio_avaliado,
                    periodo_avaliado=gestor_estagio_avaliado.current_stage,
                ).save()
                Notification.notify(
                    "gep-alteracao-chefe",
                    gestor_estagio_avaliado.posse_servidor.servidor,
                    types=("SYS",),
                    **{
                        "from": str(gestor_estagio_avaliador),
                        "period": str(gestor_estagio_avaliado.current_stage),
                    }
                )
            else:
                raise Exception(str(EstagioProbatorioServidor.AvalicaoBloqueada()))
                # transaction.rollback()
        except Exception as e:
            # transaction.rollback()
            self.log.info(e)
            obj["message"] = str(e)
            # transaction.rollback()
        else:
            self.log.info("Avaliacao alterada com sucesso.")
            obj.update(message="Dados alterados com sucesso!")
            obj.update(success=True)
            # transaction.commit()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def alterar_avaliacao(self, args=[]):
        obj = {"collection": [], "totalRows": 0}
        self.log.info(self.request.POST)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_questionario_alteracao(self, pk, servidor_pk=None):
        obj = {"collection": []}
        try:
            self.log.info(self.request.POST)

            eps = EstagioProbatorioServidor.objects.get(pk=int(servidor_pk))
            if int(self.request.POST["tipo"]) == 1:
                # se for avaliacao pelo chefe
                if not eps._acao_estado_avalicao(1):
                    raise Exception(str(EstagioProbatorioServidor.AvalicaoBloqueada()))

                avaliacao = EstagioAvaliacao.objects.get(
                    avaliado=eps, periodo_avaliado=int(eps.current_stage)
                )
                qr = QuestionarioResposta.objects.get(
                    pk=avaliacao.questionario_resposta_id
                )
            else:
                # se for manifestacao pelo servidor
                if not eps._acao_estado_avalicao(2):
                    raise Exception(
                        str(EstagioProbatorioServidor.ManifestacaoBloqueada())
                    )
                manifestacao = ManifestacaoEstagio.objects.get(
                    servidor=eps,
                    estagio_avaliacao__periodo_avaliado=int(eps.current_stage),
                )
                qr = QuestionarioResposta.objects.get(
                    pk=manifestacao.questionario_resposta_id
                )

            elementos = Elemento.objects.filter(questionario=qr.questionario_id)

            for el in elementos:
                alt_list = []
                if isinstance(el.elemento, Questao):
                    questao = Questao.objects.get(pk=el.elemento.id)
                    for alt in questao.alternativas.all():
                        r = Resposta.objects.filter(
                            questao__pk=el.elemento.id,
                            alternativa__pk=alt.id,
                            questionario_resposta__pk=qr.id,
                        )
                        alt_list.append(
                            {
                                "id": alt.id,
                                "label": alt.label,
                                "texto": alt.texto.replace("<br>", ""),
                                "valor": alt.valor,
                                "grupo": alt.grupo,
                                "id_resposta": r[0].id if r.count() else None,
                            }
                        )
                    texto_resposta = Resposta.objects.filter(
                        questao__pk=el.elemento.id, questionario_resposta__id=qr.id
                    )
                    obj["collection"].append(
                        {
                            "id": el.elemento.id,
                            "id_questionario": el.questionario_id,
                            "id_questionario_resposta": qr.id,
                            "enunciado": el.elemento.enunciado,
                            "tipo": el.elemento.tipo,
                            "mista": el.elemento.mista or None,
                            "label": el.label,
                            "chave": eps.gera_chave(),
                            "alternativas": alt_list or None,
                            "texto_resposta": (
                                texto_resposta[0].texto
                                if texto_resposta.count()
                                else None
                            ),
                            # 'texto_resposta': texto_resposta.texto[0] if texto_resposta != '' else None
                        }
                    )

                elif isinstance(el.elemento, ReferenciaTextual):
                    obj["collection"].append(
                        {
                            "id": el.elemento.id,
                            "id_questionario": el.questionario_id,
                            "id_questionario_resposta": qr.id,
                            "label": el.elemento.label,
                            "label_ele": el.label,
                            "conteudo": el.elemento.conteudo,
                            "chave": eps.gera_chave(),
                            "tipo": el.elemento.tipo,
                        }
                    )
        except EstagioAvaliacao.DoesNotExist as e:
            self.log.info(e)
            obj["message"] = "Nenhuma Avaliação encontrada."
        except ManifestacaoEstagio.DoesNotExist as e:
            self.log.info(e)
            obj["message"] = "Manifestação indisponível."
        except Exception as e:
            self.log.error(e)
            obj["success"] = False
            obj["message"] = str(e)
            # obj['message'] = 'Ocorreu um erro ao exibir o questionário'
        return obj

    def get_questionario_alteracao(self, args=[]):
        obj = None if len(args) == 0 else self.list_questionario_alteracao(*args)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def notifica_divergencia(self, args=[]):
        obj = {"collection": [], "message": "Nada aconteceu ainda", "success": False}
        self.log.info(self.request.POST)
        try:
            eps = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["estagioprob_id"]
            )
            estag_aval = EstagioAvaliacao.objects.get(
                periodo_avaliado=eps.current_stage, avaliado=eps
            )
            estag_aval.notifica_chefe_nao_concordancia(
                eps, self.request.POST["mensagem"]
            )
        except Exception as e:
            self.log.info(e)
            obj["message"] = "Não consegui realizar a notificaçao!"
        else:
            obj["message"] = "Notificação realizada com sucesso!"
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def nota_comissao(self, args=[]):
        obj = {"collection": [], "message": "Nada aconteceu ainda", "success": False}
        try:
            eps = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["estagioprob_id"]
            )
            estag_aval = EstagioAvaliacao.objects.get(
                periodo_avaliado=eps.current_stage, avaliado=eps
            )
            estag_aval.media_comissao = self.request.POST["nota"]
            estag_aval.observacao_comissao = self.request.POST["observacao"]
            estag_aval.save()
        except EstagioAvaliacao.DoesNotExist as e:
            obj["message"] = "Avaliação referente a esta etapa não foi econtrada!"
            self.log.info(e)
        except Exception as e:
            self.log.info(e)
            obj["message"] = "Não consegui lançar a nota!"
        else:
            obj["message"] = "Nota lançada com sucesso!"
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPConfiguradorAvaliacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = FatorAvaliacao

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.ConfiguradorAvaliacao()")


class GEPFatorAvaliacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = FatorAvaliacao

    def get_list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            pk_fator = self.request.POST["pk_fator_avaliacao"]
            fator_avaliacao = FatorAvaliacao.objects.get(pk=pk_fator)
            configuracao = Configuracao.objects.get(pk=fator_avaliacao.configuracao_id)
            self.log.info(configuracao)
        except Exception as e:
            obj.update(
                {
                    "message": "Não consegui encontrar o Fator desejado.",
                    "success": False,
                }
            )
            self.log.info(e)
        else:
            obj.update(
                {
                    "collection": {
                        "pk": fator_avaliacao.pk,
                        "descricao": str(fator_avaliacao.descricao),
                        "configuracao": fator_avaliacao.configuracao.pk,
                        "pk_questionario": fator_avaliacao.configuracao.questionario_id,
                    },
                    "success": True,
                }
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            self.log.info(self.request.POST)
            R = self.request.REQUEST
            start = int(R.get("start", 0))
            end = int(R.get("limit", 50)) + start

            query = FatorAvaliacao.objects.all()

            for fator in query[start:end]:
                obj["collection"].append(
                    {
                        "pk": fator.id,
                        "descricao": fator.descricao,
                        "configuracao": "%s" % fator.configuracao,
                        "pk_questionario": fator.configuracao.questionario_id,
                    }
                )
        except Exception as e:
            self.log.info(e)

        obj.update(count=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def create(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        try:
            self.log.info(self.request.POST)
            descricao = self.request.POST["descricao"]
            configuracao_pk = self.request.POST["configuracao"]
            configuracao = Configuracao.objects.get(pk=configuracao_pk)

            fatoravaliacao = FatorAvaliacao(
                descricao=descricao, configuracao=configuracao
            )
            fatoravaliacao.save()

            obj.update(success=True)
            obj.update(message="Salvo com sucesso!")
        except Exception as e:
            # transaction.rollback()
            obj.update(message="Ocorreu um erro ao salvar os dados!")
            obj.update(success=False)
            self.log.info(e)
        else:
            # transaction.commit()
            self.log.info("Salvo com sucesso")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update(self, args=[]):
        obj = {"collection": [], "count": 0, "message": "Nada aconteceu ainda"}
        self.log.info(self.request.POST)
        try:

            conf = Configuracao.objects.get(pk=self.request.REQUEST.get("configuracao"))
            fat_avaliacao = FatorAvaliacao.objects.get(
                pk=self.request.REQUEST.get("pk")
            )

            fat_avaliacao.descricao = self.request.REQUEST.get("descricao")
            fat_avaliacao.configuracao = conf

            fat_avaliacao.save()
            obj.update(success=True)
        except Exception as e:
            obj.update(success=False)
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {}

        try:
            fator_avaliacao = FatorAvaliacao.objects.filter(
                pk__in=self.request.POST.getlist("pk")
            )
            for fator in fator_avaliacao:
                fator.delete()
        except Exception as e:
            self.log.error(e)
            obj.update({"success": False, "message": "{}".format(e.args[0])})
        else:
            obj.update({"success": True})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPQuesitosAvaliacao(extjs.ExtCrud):
    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = QuesitoAvaliacao

    def list_elemento(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            # self.log.info(self.request.GET.get('questionario'))
            query = Elemento.objects.filter(
                questionario=self.request.GET.get("pk_questionario")
            )
            for eleme in query:
                # if eleme.elemento.tipo !='Ref. Textual':
                obj["collection"].append(
                    {
                        "pk_element": eleme.elemento.id,  # pk da referencia textual ou questao
                        "pk": eleme.id,
                        "enunciado": eleme.elemento.label,
                        "tipo": eleme.elemento.tipo,
                    }
                )
        except Exception as e:
            self.log.info(e)

        obj.update(count=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_quesitos(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            self.log.info(self.request.GET)
            fator = FatorAvaliacao.objects.get(pk=self.request.GET.get("pk_fator"))
            quesito_avaliacao = QuesitoAvaliacao.objects.filter(fator_avaliacao=fator)
            for quesitos in quesito_avaliacao.all():
                for elementos in quesitos.elemento.all():
                    obj["collection"].append(
                        {
                            "pk_quesito": quesitos.id,
                            "pk_element": elementos.elemento.id,  # pk da referencia textual ou questao
                            "pk": elementos.id,
                            "enunciado": elementos.elemento.label,
                            "tipo": elementos.elemento.tipo,
                        }
                    )

        except Exception as e:
            self.log.info(e)
        # obj.update(count = query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def create(self, args=[]):
        obj = {"collection": [], "count": 0}

        try:

            pk_fator_avaliacao = self.request.POST["pk_fator_avaliacao"]
            fator = FatorAvaliacao.objects.get(pk=pk_fator_avaliacao)

        except Exception as e:
            self.log.info(e)
            obj.update(message="Não consegui encontrar o fator de avaliação")
        else:
            try:
                quesito_avaliacao, created = QuesitoAvaliacao.objects.get_or_create(
                    fator_avaliacao=fator
                )
            except Exception as e:
                obj.update(message="Erro ao salvar os dados.")
                self.log.info(e)
            else:
                obj.update(success=True)
                # quesito_avaliacao.elemento.clear()
                try:
                    for elem in self.request.POST.getlist("pks_elemento"):
                        elementos = Elemento.objects.get(pk=elem)
                        if not elementos.elemento.tipo == "Ref. Textual":
                            quesito_avaliacao.elemento.add(
                                Elemento.objects.get(pk=elem)
                            )

                except Exception as e:
                    self.log.info(e)
                    obj.update(warning=True)
                    obj.update(message="Não consegui salvar os dados.")
                else:
                    self.log.info("Salvo com sucesso!")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def remove(self, args=[]):
        obj = {"collection": [], "count": 0}

        self.log.info(self.request.POST)
        try:
            # pk_elementos = self.request.POST.getlist('pk_element')
            pk_quesito = self.request.POST.get("pk_quesito")

            quesito_avaliacao = QuesitoAvaliacao.objects.get(pk=pk_quesito)
            elementos = Elemento.objects.filter(
                pk__in=self.request.POST.getlist("pk_element")
            )

            for elem in elementos:
                quesito_avaliacao.elemento.remove(elem)

            obj.update(success=True)
            obj.update(message="Removido com sucesso!")
        except Exception as e:
            obj.update(success=False)
            obj.update(message="Não consegui remover os dados.")
            self.log.info(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPManifestacaoServidor(GEPAvaliacaoEstagio):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.Servidor()")

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            # R = self.request.REQUEST
            # start = int(R.get('start', 0))
            # end = int(R.get('limit', 50)) + start
            servidor = self.request.user.servidor
            pk_posse = None
            for posse_ativa in servidor.posses_ativas.filter(
                quadro__cargo__tipo_lei_cargo="EF"
            ):
                pk_posse = posse_ativa.pk

            query = EstagioProbatorioServidor.objects.get(posse_servidor__pk=pk_posse)
            for avaliacao in query.avaliacoes.all():
                qs = avaliacao.manifestacao_servidor.all()
                # states = avaliacao.get_status()
                questionario_manifestacao_pk = (
                    qs[0].questionario_resposta_id if qs.exists() else None
                )
                obj["collection"].append(
                    {
                        "pk": query.pk,
                        "pk_avaliacao": avaliacao.pk,
                        "servidor_pk": avaliacao.avaliado.posse_servidor.servidor.pk,
                        "cargo_id": avaliacao.avaliado.posse_servidor.quadro.cargo_id,
                        "questionario_pk": query.configuracao.questionario.id,
                        "questionario_manifestacao_servidor_pk": query.configuracao.questionario_manifestacao_servidor_id,
                        "questionario_manifestacao_pk": questionario_manifestacao_pk,
                        "questionario_manifestacao": "%s"
                        % query.configuracao.questionario_manifestacao_servidor,
                        "periodo_avaliado": avaliacao.periodo_avaliado,
                        "periodo_anterior": query.avaliacoes_realizadas,
                        "data_avaliacao": DateUtils.date_to_str(avaliacao.criado_em),
                        "avaliador": "%s" % avaliacao.avaliador,
                        "servidor": "%d : %s"
                        % (
                            avaliacao.avaliado._servidor_estagio_matricula,
                            avaliacao.avaliado._servidor_estagio_nome,
                        ),
                        "status": avaliacao.get_status(),
                        "situacao": avaliacao.get_situacao(),
                        # 'status': [
                        #     {
                        #         'iconCls': st['iconCls'],
                        #         'alt': st['alt'],
                        #         'title': st['alt']
                        #     } for st in states
                        # ],
                    }
                )
            obj.update(count=query.avaliacoes.count())
        except Exception as e:
            self.log.info(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def get_list_questionario(self, args=[]):
        # metodo que sobrescreve o list_questionario do app questionario
        obj = {"collection": [], "totalRows": 0}
        self.log.info(args)
        try:
            periodo = self.request.POST["periodo"]
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
            # periodo = estagio_servidor.current_stage
            qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            avaliacoes = EstagioAvaliacao.objects.filter(avaliado=args[1])
            manif = ManifestacaoEstagio.objects.filter(servidor=args[1])
            aval = EstagioAvaliacao.objects.get(
                avaliado=args[1], periodo_avaliado=periodo
            )
            # #verifica se já foi concluido todas as etapas de avaliacao
            if (
                manif.count() <= qtde_periodos
                and avaliacoes.count() <= qtde_periodos
                and int(periodo) <= qtde_periodos
                and aval.status is True
            ):
                obj = None if len(args) == 0 else self.list_questionario(*args)
            else:
                obj["message"] = str(EstagioAvaliacao.EstagioFinalizado())
                obj["success"] = False

            # verifica se já existe manifestacao para a etapa selecionada
            manifestacoes = ManifestacaoEstagio.objects.filter(servidor=args[1])
            for manifestacao in manifestacoes:
                if manifestacao.estagio_avaliacao.periodo_avaliado == int(periodo):
                    obj["collection"] = []
                    obj["message"] = str(ManifestacaoEstagio.ManifestacaoRealizada())
                    obj["success"] = False

        except Exception as e:
            self.log.error(e)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def ciencia_decisao_estagio(self, args=[]):
        obj = {
            "collection": [],
            "count": 0,
            "success": False,
            "message": "Nada aconteceu ainda.",
        }
        self.log.info(self.request.POST)
        try:
            eps = EstagioProbatorioServidor.objects.get(pk=self.request.POST["pk"])
            eps._ciencia_decisao()
        except Exception as e:
            self.log.info(e)
            obj["message"] = str(e)
        else:
            obj["success"] = True
            obj["message"] = "Ciência realizada com sucesso."

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def save_manifestacao_estagio(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.POST)

        try:
            estagio_avaliacao = EstagioAvaliacao.objects.get(
                pk=self.request.POST["pk_avaliacao_estagio"]
            )
            gestor_estagio = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk_gestor_estagio"]
            )
            questionario_resposta = QuestionarioResposta.objects.get(
                pk=self.request.POST["pk_questionario_resposta"]
            )

            manifestacao_estagio = ManifestacaoEstagio(
                servidor=gestor_estagio,
                estagio_avaliacao=estagio_avaliacao,
                questionario_resposta=questionario_resposta,
            )
            manifestacao_estagio.save()
            gestor_permission = ControllerPermission.objects.get(name="estagio-gestor")
            Notification.notify_all(
                "gep-manifestacao-estagio",
                [
                    user.servidor
                    for user in gestor_permission.users.all()
                    if user.servidor
                ],
                types=("SYS",),
                **{
                    "from": str(gestor_estagio.posse_servidor.servidor),
                    "period": str(estagio_avaliacao.periodo_avaliado),
                }
            )

        except ControllerPermission.DoesNotExist as e:
            # transaction.commit()
            self.log.info(e)
            obj["message"] = (
                "Houve um erro na notificação do processo! Informe a DTI sobre o ocorrido."
            )
            obj["success"] = True
        except Exception as e:
            # transaction.rollback()
            self.log.info(e)
            QuestionarioResposta.objects.get(
                pk=self.request.POST["pk_questionario_resposta"]
            ).delete()
            obj.update(message="Ocorreu um erro ao salvar a manifestação!")
            obj["success"] = False
        else:
            # transaction.commit()
            obj.update(message="Manifestação Salva com sucesso!")
            obj.update(success=True)

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    # @transaction.commit_manually
    def save_alteracao_manifestacao_estagio(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.info(self.request.POST)
        try:
            gestor_estagio = EstagioProbatorioServidor.objects.get(
                pk=self.request.POST["pk_gestor_estagio"]
            )
            estagio_avaliacao = EstagioAvaliacao.objects.get(
                pk=self.request.POST["pk_avaliacao_estagio"]
            )
            questionario_resposta = QuestionarioResposta.objects.get(
                pk=self.request.POST["pk_questionario_resposta"]
            )

            if gestor_estagio._acao_estado_avalicao(
                2
            ):  # 2 = ACAO ALTERAR UMA MANIFESTACAO
                ManifestacaoEstagio.objects.get(
                    servidor=gestor_estagio,
                    estagio_avaliacao=estagio_avaliacao,
                    questionario_resposta=questionario_resposta,
                ).save()
                gestor_permission = ControllerPermission.objects.get(
                    name="estagio-gestor"
                )
                Notification.notify_all(
                    "gep-manifestacao-estagio",
                    [
                        user.servidor.all()[0]
                        for user in gestor_permission.users.all()
                        if user.servidor.count()
                    ],
                    types=("SYS",),
                    **{
                        "from": str(gestor_estagio.posse_servidor.servidor),
                        "period": str(estagio_avaliacao.periodo_avaliado),
                    }
                )
            else:
                raise Exception(str(EstagioProbatorioServidor.ManifestacaoBloqueada()))
                # transaction.rollback()
        except ControllerPermission.DoesNotExist as e:
            # transaction.commit()
            self.log.info(e)
            obj["message"] = (
                "Houve um erro na notificação do processo! Informe a DTI sobre o ocorrido."
            )
            obj["success"] = True
        except Exception as e:
            self.log.info(e)
            obj["message"] = str(e)
            obj["success"] = False
            # transaction.rollback()
        else:
            self.log.info("Manifestacao alterada com sucesso.")
            obj.update(message="Dados alterados com sucesso!")
            obj.update(success=True)
            # transaction.commit()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPApreciacaoComissao(extjs.ExtCrud):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.ApreciacaoEstagioComissao()")

    def apply_filter(self, query):
        qs = []
        self.log.debug(self.request.POST)
        if "keyword" in self.request.POST:
            self.log.debug("FILTER: %s" % self.request.POST["keyword"])
            qs.append(
                Q(
                    estagio_prob_servidor__posse_servidor__servidor__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    estagio_prob_servidor__posse_servidor__servidor__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )

        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        query = query.filter(q) if q else query
        return query

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        # R = self.request.REQUEST
        # start = int(R.get('start', 0))
        # end = int(R.get('limit', 50)) + start
        servidor = self.request.user.servidor

        query = EstagioComissaoServidor.objects.filter(
            integrante_comissao_avaliadora__servidor_id=servidor
        )

        query = self.apply_filter(query)
        for ecs in query:
            if not ecs.is_liberado_para_decisao():
                # states = ecs.get_status()
                obj["collection"].append(
                    {
                        "pk": ecs.id,
                        "pk_estagio_servidor": ecs.estagio_prob_servidor_id,
                        "pk_questionario_manifestacao": ecs.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor_id,
                        "pk_questionario": ecs.estagio_prob_servidor.configuracao.questionario.id,
                        "pk_comissao": ecs.integrante_comissao_avaliadora.values(
                            "comissao_id_id"
                        )[0].get("comissao_id_id"),
                        "pk_servidor": ecs.estagio_prob_servidor.posse_servidor.servidor_id,
                        "pk_cargo": ecs.estagio_prob_servidor.posse_servidor.quadro.cargo_id,
                        "nome_servidor": "%s "
                        % ecs.estagio_prob_servidor.posse_servidor.servidor,
                        # 'cargo': '%s' % ecs.estagio_prob_servidor.posse_servidor.quadro.cargo,
                        # 'cargo': '%s' % ecs.estagio_prob_servidor.posse_servidor.quadro.cargo,
                        "cargo": ecs.estagio_prob_servidor.posse_servidor.quadro.cargo.codigo,
                        "ultima_avaliacao": (
                            "%s "
                            % DateUtils.date_to_str(
                                ecs.estagio_prob_servidor.ultima_avaliacao
                            )
                            if ecs.estagio_prob_servidor.ultima_avaliacao
                            else ""
                        ),
                        "data_exercicio": "%s "
                        % DateUtils.date_to_str(
                            ecs.estagio_prob_servidor._inicio_estagio
                        ),
                        "fim_estagio": "%s"
                        % DateUtils.date_to_str(
                            ecs.estagio_prob_servidor.get_fim_estagio()
                        ),
                        "media": round(ecs.estagio_prob_servidor.media, 2),
                        # 'status': [
                        #     {
                        #         'iconCls': st['iconCls'],
                        #         'alt': st['alt'],
                        #         'title': st['alt']
                        #     } for st in states
                        # ],
                    }
                )
        obj.update(count=query.count())
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_apreciacoes(self, args=[]):
        obj = {"collection": [], "count": 0}
        self.log.debug(self.request.POST)
        R = self.request.REQUEST
        start = int(R.get("start", 0))
        end = int(R.get("limit", 50)) + start

        query = ApreciacaoComissao.objects.filter(
            # comissao_servidor=self.request.POST['pk_comissao'],
            comissao_servidor__estagio_prob_servidor__pk=self.request.POST[
                "pk_estagio_servidor"
            ]
        )
        for apreciacao in query[start:end]:
            obj["collection"].append(
                {
                    "pk": apreciacao.id,
                    "integrante_comissao": apreciacao.integrante_avaliador.servidor_id.pessoa_fisica.nome,
                    "decisao": "%s" % apreciacao.get_decisao(),
                    "data": DateUtils.date_to_str(apreciacao.created_at),
                }
            )

        obj["count"] = query.count()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def decisao_comissao(self, args=[]):
        obj = {
            "collection": [],
            "count": 0,
            "success": False,
            "message": "Nada aconteceu ainda",
        }
        self.log.debug(self.request.POST)
        try:
            avaliador = self.request.user.servidor
            estagio_comissao = EstagioComissaoServidor.objects.get(
                pk=self.request.POST["pk"]
            )
            ec = estagio_comissao.integrante_comissao_avaliadora.values(
                "comissao_id_id"
            )[0].get("comissao_id_id")
            integrante_comissao = IntegrantesComissao.objects.get(
                servidor_id=avaliador, comissao_id=ec
            )

            apreciacao_comissao = ApreciacaoComissao(
                comissao_servidor=estagio_comissao,
                integrante_avaliador=integrante_comissao,
                decisao=int(self.request.POST["decisao"]),
            )
            apreciacao_comissao.save()

        except Exception as e:
            self.log.info(e)
            # obj['message'] = 'Ocorreu um erro ao salvar os dados!'
            obj["message"] = str(e)
        else:
            obj["message"] = "Apreciação salva com sucesso!"
            obj["success"] = True

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPDecisaoChefeOrgao(extjs.ExtCrud):
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gep.ApreciacaoGestorOrgao()")

    def permission_list(self, args=[]):
        servidor = self.request.user.servidor
        return servidor.user.has_perm("estagio.can_valid_stage_prob")

    def apply_filter(self, query):
        qs = []
        self.log.debug(self.request.POST)
        if "keyword" in self.request.POST:
            self.log.debug("FILTER: %s" % self.request.POST["keyword"])
            qs.append(
                Q(
                    estagio_prob_servidor__posse_servidor__servidor__matricula__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )
            qs.append(
                Q(
                    estagio_prob_servidor__posse_servidor__servidor__pessoa_fisica__nome__icontains=self.request.POST[
                        "keyword"
                    ]
                )
            )

        q = None
        for qN in qs:
            q = qN if q is None else Q(q | qN)

        query = query.filter(q) if q else query
        return query

    def list(self, args=[]):
        obj = {"collection": [], "count": 0}
        try:
            # R = self.request.REQUEST
            # start = int(R.get('start', 0))
            # end = int(R.get('limit', 50)) + start
            query = EstagioComissaoServidor.objects.filter()
            query = self.apply_filter(query)
            for ecs in query:
                if (
                    ecs.is_liberado_para_decisao()
                    and not ecs.is_julgado()
                    and self.permission_list()
                ):
                    states = ecs.get_status_gestor_orgao()
                    obj["collection"].append(
                        {
                            "pk": ecs.id,
                            "pk_estagio_servidor": ecs.estagio_prob_servidor_id,
                            "pk_questionario_manifestacao": ecs.estagio_prob_servidor.configuracao.questionario_manifestacao_servidor_id,
                            "pk_questionario": ecs.estagio_prob_servidor.configuracao.questionario.id,
                            "pk_comissao": ecs.integrante_comissao_avaliadora.values(
                                "comissao_id_id"
                            )[0].get("comissao_id_id"),
                            "pk_servidor": ecs.estagio_prob_servidor.posse_servidor.servidor_id,
                            "pk_cargo": ecs.estagio_prob_servidor.posse_servidor.quadro.cargo_id,
                            "nome_servidor": "%s "
                            % ecs.estagio_prob_servidor.posse_servidor.servidor,
                            # 'cargo': '%s' % ecs.estagio_prob_servidor.posse_servidor.quadro.cargo,
                            # 'cargo': '%s' % ecs.estagio_prob_servidor.posse_servidor.quadro.cargo,
                            "cargo": ecs.estagio_prob_servidor.posse_servidor.quadro.cargo.codigo,
                            "ultima_avaliacao": (
                                DateUtils.date_to_str(
                                    ecs.estagio_prob_servidor.ultima_avaliacao
                                )
                                if ecs.estagio_prob_servidor.ultima_avaliacao
                                else None
                            ),
                            "data_exercicio": DateUtils.date_to_str(
                                ecs.estagio_prob_servidor._inicio_estagio
                            )
                            or None,
                            "fim_estagio": "%s"
                            % DateUtils.date_to_str(
                                ecs.estagio_prob_servidor.get_fim_estagio()
                            )
                            or None,
                            "media": round(ecs.estagio_prob_servidor.media, 2),
                            "status": [
                                {
                                    "iconCls": st["iconCls"],
                                    "alt": st["alt"],
                                    "title": st["alt"],
                                }
                                for st in states
                            ],
                        }
                    )
            obj.update(count=query.count())
        except Exception as e:
            self.log.info(e)
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def decisao_gestor_orgao(self, args=[]):
        obj = {
            "collection": [],
            "count": 0,
            "message": "Nada aconteceu ainda.",
            "success": False,
        }
        self.log.info(self.request.POST)
        try:
            ecs = EstagioComissaoServidor.objects.get(
                pk=self.request.POST["pk_comissao_servidor"]
            )
            cdo = DecisaoChefeOrgao(
                estagio_comissao_servidor=ecs,
                decisao=self.request.POST["decisao"],
                fundamentacao=self.request.POST["fundamentacao"],
            )
            cdo.save()
        except EstagioComissaoServidor.DoesNotExist:
            obj["message"] = "Não foi encontrada comissão para este servidor."
        except Exception as e:
            self.log.info(e)
            obj["message"] = str(e)
        else:
            obj["success"] = True
            obj["message"] = "Dados salvo com sucesso."

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class GEPPrintAvaliacao(extjs.ExtReportBuild):
    class Form(forms.Form):
        servidor = forms.CharField()
        cargo = forms.CharField()

    log = getLogger(__name__)
    report_src = "/to/mpe/rh/estagio_probatorio/notas/rh_ep_main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/estagio_probatorio/notas/",
        }
    ]

    def get_generated_filename(self):
        report_servidor = (
            "Relatorio_Estagio_Probatorio_%s.pdf"
            % Servidor.objects.get(
                pk=int(self.request.GET["servidor"])
            ).pessoa_fisica.nome
        )
        report_servidor = report_servidor.encode("utf-8")
        return report_servidor
        # return 'avaliacao_estagio_probatorio_%s.pdf' % Servidor.objects.get(pk = int(self.request.GET["servidor"])).pessoa_fisica.nome


class GEPPrintAvaliacaoChefe(extjs.ExtReportBuild):

    class Form(forms.Form):
        servidor = forms.CharField()
        cargo = forms.CharField()
        etapa = forms.CharField()
        questionario_avaliacao = forms.CharField()
        questionario_manifestacao = forms.CharField()

    log = getLogger(__name__)
    report_src = "/to/mpe/rh/estagio_probatorio/avaliacao/rh_ep_main"
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/estagio_probatorio/avaliacao/",
        }
    ]

    def get_generated_filename(self):
        report_servidor = (
            "Avaliacao_Estagio_Probatorio_%s.pdf"
            % Servidor.objects.get(
                pk=int(self.request.GET["servidor"])
            ).pessoa_fisica.nome
        )
        report_servidor = report_servidor.encode("utf-8")
        return report_servidor


class GEPPrintDecisaoEstagio(extjs.ExtReportBuild):

    class Form(forms.Form):
        servidor = forms.CharField()
        cargo = forms.CharField()

    log = getLogger(__name__)
    report_src = (
        "/to/mpe/rh/estagio_probatorio/especial/avaliacao/rh_ep_especial_avaliacao_main"
    )
    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/rh/estagio_probatorio/especial/avaliacao/",
        }
    ]

    def get_generated_filename(self):
        report_servidor = (
            "Decisao_Estagio_Probatorio_%s.pdf"
            % Servidor.objects.get(
                pk=int(self.request.GET["servidor"])
            ).pessoa_fisica.nome
        )
        report_servidor = report_servidor.encode("utf-8")
        return report_servidor
