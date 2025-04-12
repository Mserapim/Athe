# -*- coding: utf-8 -*-

import ast
import datetime

from django import forms
from django.db import transaction

from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.apd.api.periodicevaluationperformance import ApdPeriodicEvaluationPerformance
from rh.apd.models import Evaluation, PeriodicEvaluationPerformance
from rh.models import Servidor
from standard.questionario.models import (
    Elemento,
    Questao,
    QuestionarioResposta,
    ReferenciaTextual,
    Resposta,
)

# from standard.questionario.views import *

log = getLogger(__name__)


class ApdEvaluation(ApdPeriodicEvaluationPerformance):
    """Classe representativa da Avaliação de APD, via herança do modelo PeriodicEvaluationPerformance."""

    _model = PeriodicEvaluationPerformance

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.evaluation.Manage")')

    class Form(forms.ModelForm):
        """Class Form necessário para que se possa herdar o app Questionário, utilizando o formulário construido por ele."""

        class Meta:
            """Necessário essa implementação porque o modelo PeriodicEvaluationPerformance herda a classe QMontarQuestionario.

            A classe QMontarQuestionario faz o processo de construção do formulário para exibir o questionário de avaliação.
            """

            exclude = []
            model = PeriodicEvaluationPerformance

    def get_query(self):
        """Get query."""
        query = super(ApdEvaluation, self).get_query()
        if self.request.user.has_perm("apd.apd_boss"):
            user = self.request.user.servidor
            query = query.filter(
                status=1, employee__servidor__in=user.subordinados.all()
            )
        else:
            query = self._model.objects.none()
        return query

    def get_list_questionnaire(self, args=[]):
        """Sobrescrita do metodo da classe QMontarQuestionario que busca um querstionário existente para montar na tela."""
        rst = {"count": 0, "collection": []}
        try:
            #  FAZER VERIFICACOES PARA PERMITIR EXIBICAO DO FORMULARIO
            apd = PeriodicEvaluationPerformance.objects.get(pk=args[1])
            apd.validate_modified()
            if apd._released():
                raise Exception("Essa estapa ainda não está liberada para avaliação!")
            if apd.evaluation_apd.exists():
                raise Exception("Avaliação já realizada para esse período!")
            else:
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)

        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def list_questionnaire_change(self, pk, servidor_pk=None):
        """Sobrescrita do metodo da classe QMontarQuestionario que busca um querstionário
        existente para montar na tela em caso de alteração de dados."""
        rst = {"collection": []}
        try:
            apd = PeriodicEvaluationPerformance.objects.get(pk=int(servidor_pk))
            if int(self.request.POST.get("tipo")) == 1:
                # se for avaliacao pelo chefe
                if not apd.action_state_evaluation(1):
                    raise Exception(PeriodicEvaluationPerformance.BlockEvaluation())

                evaluation = Evaluation.objects.get(
                    subordinate=apd,
                    start_period_evaluation=apd.start_date,
                    end_period_evaluation=apd.end_date,
                )
                qr = QuestionarioResposta.objects.get(
                    pk=evaluation.questionnaire_response_id
                )
            else:
                # se for manifestacao pelo servidor
                if not apd.action_state_evaluation(2):
                    raise Exception(PeriodicEvaluationPerformance.BlockManifestation())
                manifestation = Evaluation.objects.get(
                    subordinate=apd,
                    start_period_evaluation=apd.start_date,
                    end_period_evaluation=apd.end_date,
                )
                qr = QuestionarioResposta.objects.get(
                    pk=manifestation.questionario_resposta_id
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
                            "chave": apd.gera_chave(),
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
                            "chave": apd.gera_chave(),
                            "tipo": el.elemento.tipo,
                        }
                    )
        except Evaluation.DoesNotExist:
            rst.update(message="Nenhuma Avaliação Encontrada!")
        except Exception as e:
            self.log.error(e)
        else:
            rst.update(success=True)
            return rst

    def get_questionnaire_change(self, args=[]):
        """Sobrescrita do metodo da classe QMontarQuestionario que chama o metodo list_questionnaire_change."""
        rst = {"count": 0, "collection": []}
        try:
            # log.info(self.request.POST.get('tipo'))
            apd = PeriodicEvaluationPerformance.objects.get(pk=args[1])
            apd.validate_modified()
            if not apd.action_state_evaluation(int(self.request.POST.get("tipo"))):
                raise Exception("Não é possível alterar essa evaliação!")

            if not apd.evaluation_apd.exists():
                raise Exception("Nenhuma avaliação encontrada para esse período!")
            else:
                rst = None if len(args) == 0 else self.list_questionnaire_change(*args)
                rst.update(success=True)
        except Exception as e:
            self.log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_evaluation(self, args=[]):
        """Salva uma avaliação com os dados do formulário preenchido."""
        rst = {"message": "Nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                employee = apd.employee.servidor
                if not ast.literal_eval(self.request.POST.get("manual") or "False"):
                    boss = self.request.user.servidor
                    questionnaire_response = QuestionarioResposta.objects.get(
                        pk=self.request.POST.get("questionnaire_response")
                    )
                    evaluation = Evaluation(
                        questionnaire_response=questionnaire_response,
                        subordinate=apd,
                        boss=boss,
                        start_period_evaluation=apd.start_date,
                        end_period_evaluation=apd.end_date,
                        days_suspended_evaluation=apd.days_suspended,
                    )
                else:
                    try:
                        boss = Servidor.objects.get(
                            pk=self.request.POST.get("evaluator")
                        )
                        questionnaire_response = QuestionarioResposta.objects.get(
                            pk=self.request.POST.get("pk_questionnaire_response")
                        )
                    except Exception:
                        rst.update(message="Avaliador ou questionário não existe.")
                    text_justification_repetition = self.request.POST.get(
                        "text_justification_repetition"
                    )
                    evaluation = Evaluation(
                        questionnaire_response=questionnaire_response,
                        subordinate=apd,
                        boss=boss,
                        start_period_evaluation=apd.start_date,
                        end_period_evaluation=apd.end_date,
                        days_suspended_evaluation=apd.days_suspended,
                        text_justification_repetition=text_justification_repetition,
                        repetition_flag=True,
                    )
                evaluation.save()
                Notification.notify(
                    "apd-evaluation-boss",
                    employee,
                    types=("SYS",),
                    **{
                        "from": boss,
                        "start": DateUtils.date_to_str(apd.start_date),
                        "end": DateUtils.date_to_str(apd.end_date),
                    }
                )
        except Exception as e:
            rst.update(
                message="Ocorreu um erro ao salvar avaliação! ("
                + "{}".format(e.args[0])
                + ")"
            )
            try:
                QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("questionnaire_response")
                ).delete()
            except Exception as e:
                self.log.error(e)
        else:
            rst.update(success=True, message="Avaliação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_change_evaluation(self, args=[]):
        """Salva uma alteração de avaliação com os dados do formulário preenchido."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                employee = apd.employee.servidor
                boss = self.request.user.servidor
                # ACAO ALTERAR UMA AVALIACAO
                if apd.action_state_evaluation(1):
                    boss = self.request.user.servidor
                    Evaluation.objects.get(
                        subordinate=apd,
                        start_period_evaluation=apd.start_date,
                        end_period_evaluation=apd.end_date,
                    ).save()
                    Notification.notify(
                        "apd-evaluation-alter-boss",
                        employee,
                        types=("SYS",),
                        **{
                            "from": boss,
                            "start": DateUtils.date_to_str(apd.start_date),
                            "end": DateUtils.date_to_str(apd.end_date),
                        }
                    )
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
        else:
            rst.update(success=True, message="Alteração salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_list_external_questionnaire(self, args=[]):
        rst = {"count": 0, "collection": []}
        try:
            apd = PeriodicEvaluationPerformance.objects.get(pk=args[1])
            # qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            # evaluations = Evaluation.objects.filter(avaliado=args[1])

            if Evaluation.objects.filter(
                start_period_evaluation=apd.start_date,
                end_period_evaluation=apd.end_date,
                subordinate__employee=apd.employee,
            ).exists():
                rst.update(
                    collection=[],
                    message="Já existe uma avaliação realizada para esse período!",
                    success=False,
                )
            else:
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_external_evaluation(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            self.log.info(self.request.POST)
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                questionnaire_response = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionnaire_response")
                )
                evaluation = Evaluation(
                    questionnaire_response=questionnaire_response,
                    subordinate=apd,
                    boss=Servidor.objects.get(user__username="athenas"),
                    start_period_evaluation=apd.start_date,
                    end_period_evaluation=apd.end_date,
                    days_suspended_evaluation=apd.days_suspended,
                    external_evaluator=self.request.POST.get("external_evaluator"),
                    external_registration=self.request.POST.get(
                        "external_registration"
                    ),
                    external_jobposition=self.request.POST.get("external_jobposition"),
                    external_workplace=self.request.POST.get("external_workplace"),
                    date_external_evaluation=(
                        DateUtils.str_to_date(
                            self.request.POST.get("date_external_evaluation")
                        )
                        if self.request.POST.get("date_external_evaluation") != ""
                        else datetime.now()
                    ),
                )
                evaluation.save()
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionnaire_response")
            ).delete()
        else:
            rst.update(success=True, message="Avaliação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def opinion_reconsideration_evaluation(self, args=[]):
        """DECISÃO DO PEDIDO DE RECONSIDERAÇÃO DE AVALIAÇÃO."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            log.info(self.request.POST)
            apd = self._model.objects.get(pk=int(self.request.POST.get("pk")))
            apd.validate_modified()
            evaluation = apd.get_evaluation()

            if not apd.exists_evaluation():
                raise Exception("Nenhuma avaliação encontrada!")

            if evaluation.reconsideration_flag:
                if not evaluation.validate_order_opinion_reconsideration():
                    raise Exception(
                        "O prazo para realizar o parecer quanto ao pedido de reconsideração da avaliação está expirado!"
                    )

                Evaluation.objects.filter(pk=evaluation.pk).update(
                    opinion_request_reconsideration=self.request.POST.get("message"),
                    date_opinion_request_reconsideration=datetime.datetime.now(),
                )

                rst.update(success=True, message="Procedimento realizado com sucesso.")

                Notification.notify(
                    "apd-opinion-reconsideration",
                    apd.employee.servidor,
                    types=("SYS",),
                    **{
                        "from": str(apd.employee.servidor),
                        "start": DateUtils.date_to_str(apd.start_date),
                        "end": DateUtils.date_to_str(apd.end_date),
                        "deadline": apd.configuration.deadline_reconsideration,
                    }
                )

            else:
                rst.update(
                    success=False,
                    message="Não existe um pedido de reconsideração para esta avaliação!",
                )

        except PeriodicEvaluationPerformance.DoesNotExist:
            rst.update(message="Nada não encontrado!")
        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
