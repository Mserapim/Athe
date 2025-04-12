# -*- coding: utf-8 -*-

import datetime

from django import forms
from django.db import transaction

from contrib.daterange import NewDateRange
from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.estagio.api.estagioprobatorioservidor import GepEstagioProbatorioServidor
from rh.estagio.models import (
    Elemento,
    EstagioAvaliacao,
    EstagioProbatorioServidor,
    ManifestacaoEstagio,
    QuestionarioResposta,
)
from rh.models import Servidor
from standard.questionario.models import Questao, ReferenciaTextual, Resposta

# from standard.questionario.views import *

log = getLogger(__name__)


class GepEstagioProbatorioAvaliador(GepEstagioProbatorioServidor):

    _model = EstagioProbatorioServidor

    full_text_index = (
        "posse_servidor__servidor__matricula__icontains",
        "posse_servidor__servidor__pessoa_fisica__nome__icontains",
    )

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = EstagioProbatorioServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.avaliador.Manage")')

    def get_query(self):
        query = super(GepEstagioProbatorioAvaliador, self).get_query()

        if self.request.user.has_perm("estagio.estagio_avaliador"):
            user = self.request.user.servidor
            query = query.filter(
                status=1, posse_servidor__servidor__in=user.subordinados.all()
            )

        return query

    def get_resposta_avaliacao(self, args=[]):
        rst = {"count": 0, "collection": []}
        try:
            rst = None if len(args) == 0 else self.get_data_resposta(*args)
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_list_questionario(self, args=[]):
        rst = {"count": 0, "collection": []}
        try:
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
            qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            avaliacoes = EstagioAvaliacao.objects.filter(avaliado=args[1])
            # verifica se ja foi finalizada todas as etapas
            if (
                not avaliacoes.count()
                >= estagio_servidor.current_stage
                == qtde_periodos
            ):
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)
            else:
                rst.update(
                    message=str(EstagioAvaliacao.EstagioFinalizado()),
                    success=False,
                )
            # verifica se a etapa já está liberada
            if not estagio_servidor.is_released:
                rst.update(
                    collection=[],
                    message=str(EstagioAvaliacao.AvaliacaoNaoLiberada()),
                    success=False,
                )
            # caso os dados de gestor estagio não tenham sido atualizados ainda impede a avaliacao com a mesma etapa
            aval_list = []
            for aval in avaliacoes:
                aval_list.append(aval.periodo_avaliado)
            if estagio_servidor.current_stage in aval_list:
                rst.update(
                    collection=[],
                    message=str(EstagioAvaliacao.AvaliacaoRealizada()),
                    success=False,
                )
            # verifica se o estagio esta bloqueado
            if estagio_servidor.bloqueada:
                rst.update(
                    collection=[],
                    message=str(EstagioAvaliacao.AvaliacaoBloqueada()),
                    success=False,
                )
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_list_questionario_externo(self, args=[]):
        rst = {"count": 0, "collection": []}
        try:
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
            qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            avaliacoes = EstagioAvaliacao.objects.filter(avaliado=args[1])
            # verifica se ja foi finalizada todas as etapas
            if (
                not avaliacoes.count()
                >= estagio_servidor.current_stage
                == qtde_periodos
            ):
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)
            else:
                rst.update(
                    message=str(EstagioAvaliacao.EstagioFinalizado()),
                    success=False,
                )

            # caso os dados de gestor estagio não tenham sido atualizados ainda impede a avaliacao com a mesma etapa
            aval_list = []
            for aval in avaliacoes:
                aval_list.append(aval.periodo_avaliado)
            if estagio_servidor.current_stage in aval_list:
                rst.update(
                    collection=[],
                    message=str(EstagioAvaliacao.AvaliacaoRealizada()),
                    success=False,
                )
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def list_questionario_alteracao(self, pk, servidor_pk=None):
        rst = {"collection": []}
        try:
            eps = EstagioProbatorioServidor.objects.get(pk=int(servidor_pk))
            if int(self.request.POST.get("tipo")) == 1:
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
                    rst["collection"].append(
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
                        }
                    )
                elif isinstance(el.elemento, ReferenciaTextual):
                    rst["collection"].append(
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
        except Exception as e:
            self.log.info(e)
        else:
            rst.update(success=True)
            return rst

    def get_questionario_alteracao(self, args=[]):
        try:
            rst = None if len(args) == 0 else self.list_questionario_alteracao(*args)
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_avaliacao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                servidor_avaliado = gestor_estagio_avaliado.posse_servidor.servidor
                gestor_estagio_avaliador = self.request.user.servidor
                questionario_resposta = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionario_resposta")
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
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionario_resposta")
            ).delete()
        else:
            rst.update(success=True, message="Avaliação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_avaliacao_estagio_externo(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            self.log.info(self.request.POST)
            # gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(pk=self.request.POST.get('pk_gestor_estagio'))
            with transaction.atomic():
                gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                questionario_resposta = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionario_resposta")
                )
                dias_interrompidos = NewDateRange(
                    gestor_estagio_avaliado.next_evaluation(),
                    gestor_estagio_avaliado.proxima_avaliacao,
                )

                estagio_avaliacao = EstagioAvaliacao(
                    questionario_resposta=questionario_resposta,
                    avaliado=gestor_estagio_avaliado,
                    avaliador=Servidor.objects.get(user__username="athenas"),
                    periodo_avaliado=gestor_estagio_avaliado.current_stage,
                    data_inicio_etapa=gestor_estagio_avaliado.ultima_avaliacao
                    or gestor_estagio_avaliado._inicio_estagio,
                    dias_interrompidos=(
                        0 if dias_interrompidos.days == 1 else dias_interrompidos.days
                    ),
                    data_fim_etapa=gestor_estagio_avaliado.proxima_avaliacao,
                    avaliador_externo=self.request.POST.get("avaliador_externo"),
                    cargo_externo=self.request.POST.get("cargo_externo"),
                    lotacao_externo=self.request.POST.get("lotacao_externo"),
                    matricula_externo=self.request.POST.get("matricula_externo"),
                    data_avaliacao_externa=(
                        DateUtils.str_to_date(
                            self.request.POST.get("data_avaliacao_externa")
                        )
                        if self.request.POST.get("data_avaliacao_externa") != ""
                        else datetime.now()
                    ),
                )

                estagio_avaliacao.save()

        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionario_resposta")
            ).delete()
        else:
            rst.update(success=True, message="Avaliação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_alteracao_avaliacao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                gestor_estagio_avaliado = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                # ACAO ALTERAR UMA AVALIACAO
                if gestor_estagio_avaliado._acao_estado_avalicao(1):
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
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
        else:
            rst.update(success=True, message="Alteração salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
