# -*- coding: utf-8 -*-

# from standard.questionario.views import
import datetime

from django import forms
from django.db import transaction

from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.apd.api.periodicevaluationperformance import ApdPeriodicEvaluationPerformance
from rh.apd.models import (
    Evaluation,
    Manifestation,
    PeriodicEvaluationPerformance,
    Resource,
)
from standard.questionario.models import (
    Elemento,
    Questao,
    QuestionarioResposta,
    ReferenciaTextual,
    Resposta,
)

log = getLogger(__name__)


class ApdManifestation(ApdPeriodicEvaluationPerformance):
    """Classe representativa da Manifestação da Apd, hedando o modelo PeriodicEvaluationPerformance."""

    class Form(forms.ModelForm):
        """Class Form necessário para que se possa herdar o app Questionário, utilizando o formulário construido por ele."""

        class Meta:
            """Necessário essa implementação porque o modelo PeriodicEvaluationPerformance herda a classe QMontarQuestionario.

            A classe QMontarQuestionario faz o processo de construção do formulário para exibir o questionário de manifestação.
            """

            exclude = []
            model = PeriodicEvaluationPerformance

    def json(self, args=[]):
        """JSON."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("apd.manifestation.Manage")')

    def get_query(self):
        """GET QUERY."""
        query = super(ApdManifestation, self).get_query()
        if self.request.user.has_perm("apd.apd_subordinate"):
            user = self.request.user.servidor
            query = query.filter(employee__servidor=user)
        return query

    def resource_evaluation(self, args=[]):
        """SOLICITAR RECURSO DE AVALIAÇÃO."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            apd = self._model.objects.get(pk=int(self.request.POST.get("pk")))
            evaluation = apd.get_evaluation()

            apd.validate_modified()

            if not evaluation.validate_order_resource():
                raise Exception("O prazo para solicitar recurso está expirado!")
            if not apd.exists_evaluation():
                raise Exception("Nenhuma avaliação encontrada!")
            if not apd.exists_manifestation():
                raise Exception("Nenhuma manifestação encontrada!")

            if not evaluation.exists_resource():
                res = Resource(
                    evaluation=evaluation, text=self.request.POST.get("message")
                )
                res.save()
                # cif.notification_member(self.request.POST.get('message'))
                rst.update(success=True, message="Procedimento realizado com sucesso.")
                apd.notify_membercommission()
                apd.notify_boss_resource()
            else:
                rst.update(
                    success=False, message="Já foi solicitado recurso dessa avaliação!"
                )

        except PeriodicEvaluationPerformance.DoesNotExist:
            rst.update(message="Nada não encontrado!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def science_resource_decision(self, args=[]):
        """REALIZAR CIÊNCIA DA DECISÃO DE RECURSO."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            apd = self._model.objects.get(pk=int(self.request.POST.get("pk")))
            evaluation = apd.get_evaluation()
            resource = Resource.objects.get(evaluation=evaluation)
            if not resource.decision_resource.exists():
                raise Exception("Aguarde a decisão do recurso!")

            if resource.date_science_decision:
                raise Exception(
                    "A ciência já foi realizada para essa decisão de recurso!"
                )

            resource.date_science_decision = datetime.datetime.now()
            resource.save()
            rst.update(success=True, message="Procedimento realizado com sucesso.")

        except Resource.DoesNotExist:
            rst.update(
                message="Não foi possível encontrar nenhum recurso para essa avaliação!"
            )
        except PeriodicEvaluationPerformance.DoesNotExist:
            rst.update(message="Não foi possível encontrar uma APD!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def science_evaluation(self, args=[]):
        """REALIZAR CIÊNCIA DA DECISÃO DE RECURSO."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            apd = self._model.objects.get(pk=int(self.request.POST.get("pk")))

            if not apd.evaluation_apd.exists() or not apd.manifestation_apd.exists():
                raise Exception(
                    "É necessário que exista uma Avaliação e uma Manifestação!"
                )

            if apd.date_science_evaluation:
                raise Exception("A ciência já foi realizada para essa avaliação!")

            apd.date_science_evaluation = datetime.datetime.now()
            apd.save()

            rst.update(success=True, message="Procedimento realizado com sucesso.")

        except Resource.DoesNotExist:
            rst.update(
                message="Não foi possível encontrar nenhum recurso para essa avaliação!"
            )
        except PeriodicEvaluationPerformance.DoesNotExist:
            rst.update(message="Não foi possível encontrar uma APD!")
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def reconsideration_evaluation(self, args=[]):
        """SOLICITAR RECONSIDERAÇÃO DE AVALIAÇÃO."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            # log.info(self.request.POST)
            apd = self._model.objects.get(pk=int(self.request.POST.get("pk")))
            apd.validate_modified()
            evaluation = apd.get_evaluation()

            if not evaluation.validate_order_reconsideration():
                raise Exception("O prazo para solicitar reconsideração está expirado!")
            if not apd.exists_evaluation():
                raise Exception("Nenhuma avaliação encontrada!")

            if not evaluation.reconsideration_flag:
                Evaluation.objects.filter(pk=evaluation.pk).update(
                    text_reconsideration=self.request.POST.get("message"),
                    reconsideration_flag=True,
                    date_reconsideration=datetime.datetime.now(),
                )

                rst.update(success=True, message="Procedimento realizado com sucesso.")
                Notification.notify(
                    "apd-reconsideration",
                    apd.employee.servidor.chefe_imediato,
                    types=("SYS",),
                    **{
                        "from": str(apd.employee.servidor),
                        "start": DateUtils.date_to_str(apd.start_date),
                        "end": DateUtils.date_to_str(apd.end_date),
                        "deadline": str(apd.configuration.deadline_reconsideration),
                    }
                )

            else:
                rst.update(
                    success=False,
                    message="Já existe um pedido de reconsideração para esta avaliação!",
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

    def get_list_questionnaire(self, args=[]):
        """RETORNA O QUESTIONARIO ESTRUTURADO PARA A MANIFESTAÇÃO DA APD."""
        rst = {"count": 0, "collection": []}
        try:
            #  FAZER VERIFICACOES PARA PERMITIR EXIBICAO DO FORMULARIO
            apd = PeriodicEvaluationPerformance.objects.get(pk=args[1])
            apd.validate_modified()
            if apd.manifestation_apd.exists():
                raise Exception("Manifestação já realizada para esse período!")
            if (
                apd.state_evaluation != 4
                and apd.evaluation_apd.exists()
                and not apd.manifestation_apd.exists()
            ):
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)
            else:
                rst.update(
                    message=("Manifestação não disponível para esse período!"),
                    success=False,
                )

        except Exception as e:
            log.error(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_response_evaluation(self, args=[]):
        """RETORNA OS DADOS DE UMA AVALIAÇÃO/MANIFESTAÇÃO JÁ REALIZADA. RETORNA O QUESTIONÁRIO PREENCHIDO."""
        rst = {"count": 0, "collection": []}
        try:
            rst = None if len(args) == 0 else self.get_data_resposta(*args)
        except Exception as e:
            self.log.info(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def list_questionnaire_change(self, pk, servidor_pk=None):
        """RETORNA O QUESTIONARIO ESTRUTURADO PARA A ALTERAÇÃO DE UMA MANIFESTAÇÃO DA APD."""
        rst = {"collection": []}
        try:
            apd = PeriodicEvaluationPerformance.objects.get(pk=int(servidor_pk))
            apd.validate_modified()
            if int(self.request.POST.get("tipo")) == 1:
                # se for avaliacao pelo chefe
                if not apd.action_state_evaluation(1):
                    raise Exception(
                        str(PeriodicEvaluationPerformance.BlockEvaluation())
                    )

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
                # if not apd.action_state_evaluation(2):
                #     raise Exception(unicode(PeriodicEvaluationPerformance.BlockManifestation()))
                manifestation = Manifestation.objects.get(
                    subordinate=apd,
                    evaluation__subordinate__start_date=apd.start_date,
                    evaluation__subordinate__end_date=apd.end_date,
                )
                qr = QuestionarioResposta.objects.get(
                    pk=manifestation.questionnaire_response_id
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
        except Exception as e:
            self.log.info(e)
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True)
            return rst

    def get_questionnaire_change(self, args=[]):
        """RETORNA O QUESTIONARIO PARA ALTERACAO DE UMA APD."""
        try:
            rst = {"count": 0, "collection": []}
            apd = PeriodicEvaluationPerformance.objects.get(pk=args[1])
            apd.validate_modified()
            # @TIPO = 2 : ALTERAR MANIFESTACAO
            if int(apd.status) != 1 or not apd.action_state_evaluation(
                int(self.request.POST.get("tipo"))
            ):
                raise Exception("Não é possível alterar essa manifestação")

            if apd.manifestation_apd.exists():
                rst = None if len(args) == 0 else self.list_questionnaire_change(*args)
            else:
                rst.update(
                    message=("Nenhuma manifestação encontrada!"),
                    success=False,
                )
        except Exception as e:
            self.log.info(e)
            rst.update(message="{}".format(e.args[0]))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_manifestation(self, args=[]):
        """SALVA OS DADOS DO QUESTIONARIO DE UMA MANIFESTAÇÃO DE APD."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                evaluation = Evaluation.objects.get(
                    subordinate=apd,
                    start_period_evaluation=apd.start_date,
                    end_period_evaluation=apd.end_date,
                )
                questionnaire_response = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("questionnaire_response")
                )

                evaluation = Manifestation(
                    questionnaire_response=questionnaire_response,
                    subordinate=apd,
                    evaluation=evaluation,
                )
                evaluation.save()

                Notification.notify(
                    "apd-manifestation",
                    apd.get_immediate_boss(),
                    types=("SYS",),
                    **{
                        "from": str(apd.employee.servidor),
                        "period": str(apd.get_evaluation_period()),
                    }
                )
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("questionnaire_response")
            ).delete()
        else:
            rst.update(success=True, message="Manifestação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_change_manifestation(self, args=[]):
        """SALVA UMA ALTERAÇÃO DE UMA MANIFESTAÇÃO DE APD."""
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                # ACAO ALTERAR UMA AVALIACAO
                if apd.action_state_evaluation(1):
                    # boss = self.request.user.servidor
                    Manifestation.objects.get(
                        subordinate=apd,
                        evaluation__subordinate__start_date=apd.start_date,
                        evaluation__subordinate__end_date=apd.end_date,
                    ).save()
                #     Notification.notify(
                #         'gep-alteracao-chefe',
                #         gestor_estagio_avaliado.posse_servidor.servidor,
                #         types=('SYS',),
                #         **{
                #             'from': unicode(boss),
                #             'period': unicode(gestor_estagio_avaliado.current_stage)
                #         }
                #     )
                # else:
                #     raise Exception(unicode(PeriodicEvaluationPerformance.BlockEvaluation()))
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
        else:
            rst.update(success=True, message="Alteração salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_external_manifestation(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                apd = PeriodicEvaluationPerformance.objects.get(
                    pk=self.request.POST.get("pk_apd")
                )
                questionnaire_response = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionnaire_response")
                )
                evaluation = Evaluation.objects.get(
                    subordinate=apd,
                    start_period_evaluation=apd.start_date,
                    end_period_evaluation=apd.end_date,
                )

                if Manifestation.objects.filter(
                    subordinate=apd,
                    evaluation__subordinate__start_date=apd.start_date,
                    evaluation__subordinate__end_date=apd.end_date,
                ).exists():
                    rst.update(
                        collection=[],
                        message="Já existe uma manifestação realizada para esse período!",
                        success=False,
                    )
                else:
                    manifestation = Manifestation(
                        subordinate=apd,
                        evaluation=evaluation,
                        questionnaire_response=questionnaire_response,
                    )
                    manifestation.save()

        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar a manifestação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionario_resposta")
            ).delete()
        else:
            rst.update(success=True, message="Manifestação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)
