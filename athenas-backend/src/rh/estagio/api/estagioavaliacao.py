# -*- coding: utf-8 -*-

from django import forms
from django.db import models, transaction

from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_pk
from contrib.utils import DateUtils, getLogger
from engine.notification.models import Notification
from rh.estagio.models import (
    ControllerPermission,
    EstagioAvaliacao,
    EstagioProbatorioServidor,
    ManifestacaoEstagio,
)
from standard.questionario.models import (
    Elemento,
    Questao,
    QuestionarioResposta,
    ReferenciaTextual,
    Resposta,
)
from standard.questionario.views import QMontarQuestionario

log = getLogger(__name__)


class GepEstagioAvaliacao(Restful, QMontarQuestionario):

    _model = EstagioAvaliacao

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = EstagioProbatorioServidor

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.avaliado.Manage")')

    def get_list_questionario(self, args=[]):
        rst = {"count": 0, "collection": []}
        try:
            # self.log.info(self.request.POST)
            periodo = self.request.POST.get("periodo")
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
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
                and aval.status
            ):
                rst = None if len(args) == 0 else self.list_questionario(*args)
                rst.update(success=True)
            else:
                rst.update(
                    message=str(EstagioAvaliacao.EstagioFinalizado()),
                    success=False,
                )
            # verifica se já existe manifestacao para a etapa selecionada
            manifestacoes = ManifestacaoEstagio.objects.filter(servidor=args[1])
            for manifestacao in manifestacoes:
                if manifestacao.estagio_avaliacao.periodo_avaliado == int(periodo):
                    rst.update(
                        collection=[],
                        message=str(ManifestacaoEstagio.ManifestacaoRealizada()),
                        success=False,
                    )
        except EstagioAvaliacao.DoesNotExist:
            rst.update(
                message="Nenhuma avaliação foi encontrada!",
                success=False,
            )
        except Exception as e:
            self.log.info(e)
            rst.update(
                message="Não foi possível concluir a operação!",
                success=False,
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_manifestacao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                estagio_avaliacao = EstagioAvaliacao.objects.get(
                    pk=self.request.POST.get("pk_avaliacao_estagio")
                )
                gestor_estagio = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                questionario_resposta = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionario_resposta")
                )

                manifestacao_estagio = ManifestacaoEstagio(
                    servidor=gestor_estagio,
                    estagio_avaliacao=estagio_avaliacao,
                    questionario_resposta=questionario_resposta,
                )
                manifestacao_estagio.save()
                gestor_permission = ControllerPermission.objects.get(
                    name="estagio-gestor"
                )
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
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionario_resposta")
            ).delete()
        else:
            rst.update(success=True, message="Manifestação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_manifestacao_estagio_externa(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                gestor_estagio = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                estagio_avaliacao = EstagioAvaliacao.objects.get(
                    periodo_avaliado=gestor_estagio.current_stage,
                    avaliado=gestor_estagio,
                )
                questionario_resposta = QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionario_resposta")
                )

                manifestacao_estagio = ManifestacaoEstagio(
                    servidor=gestor_estagio,
                    estagio_avaliacao=estagio_avaliacao,
                    questionario_resposta=questionario_resposta,
                )
                manifestacao_estagio.save()

        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar avaliação!")
            QuestionarioResposta.objects.get(
                pk=self.request.POST.get("pk_questionario_resposta")
            ).delete()
        else:
            rst.update(success=True, message="Manifestação salva com sucesso")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def save_alteracao_manifestacao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                gestor_estagio = EstagioProbatorioServidor.objects.get(
                    pk=self.request.POST.get("pk_gestor_estagio")
                )
                estagio_avaliacao = EstagioAvaliacao.objects.get(
                    pk=self.request.POST.get("pk_avaliacao_estagio")
                )
                questionario_resposta = models.QuestionarioResposta.objects.get(
                    pk=self.request.POST.get("pk_questionario_resposta")
                )

                # 2 = ACAO ALTERAR UMA MANIFESTACAO
                if gestor_estagio._acao_estado_avalicao(2):
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
                else:
                    raise Exception(
                        str(EstagioProbatorioServidor.ManifestacaoBloqueada())
                    )
        except Exception as e:
            self.log.error(e)
            rst.update(message="Ocorreu um erro ao salvar alteração!")
        else:
            rst.update(success=True, message="Manifestação alterada com sucesso")

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
            self.log.error(e)
        else:
            rst.update(success=True)
            return rst

    def get_questionario_alteracao(self, args=[]):
        rst = None
        try:
            periodo = self.request.POST.get("periodo")
            estagio_servidor = EstagioProbatorioServidor.objects.get(pk=args[1])
            qtde_periodos = estagio_servidor.configuracao.qtde_avaliacoes
            avaliacoes = EstagioAvaliacao.objects.filter(avaliado=args[1])
            manif = ManifestacaoEstagio.objects.filter(servidor=args[1])
            aval = EstagioAvaliacao.objects.get(
                avaliado=args[1], periodo_avaliado=periodo
            )
            if (
                manif.count() <= qtde_periodos
                and avaliacoes.count() <= qtde_periodos
                and int(periodo) <= qtde_periodos
                and aval.status
            ):
                rst = (
                    None if len(args) == 0 else self.list_questionario_alteracao(*args)
                )
            else:
                rst = {
                    "success": False,
                    "message": "Já foi realizada uma manifestação para este período!",
                }

        except Exception as e:
            self.log.error(e)

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def ciencia_decisao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            eps = EstagioProbatorioServidor.objects.get(pk=self.request.POST.get("pk"))
            eps._ciencia_decisao()
        except Exception as e:
            self.log.error(e)
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Ciência realizada com sucesso!")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)
        if "status" in params:
            params.update(status=params.get("status", "off").lower() == "on")

        if "avaliado" in params:
            if params.get("avaliado") != "":
                field = getattr(self.Model, "avaliado")
                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()
                try:
                    params.update(avaliado=query.get(pk=params.get("avaliado")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(avaliado=None)
        if "lotacao_avaliado" in params:
            if params.get("lotacao_avaliado") != "":
                field = getattr(self.Model, "lotacao_avaliado")
                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()
                try:
                    params.update(
                        lotacao_avaliado=query.get(pk=params.get("lotacao_avaliado"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lotacao_avaliado=None)

        if "data_avaliacao_externa" in params:
            if params.get("data_avaliacao_externa") != "":
                params.update(
                    data_avaliacao_externa=DateUtils.str_to_date(
                        params.get("data_avaliacao_externa")
                    )
                )
            else:
                params.update(data_avaliacao_externa=None)

        if "questionario_resposta" in params:
            if params.get("questionario_resposta") != "":
                field = getattr(self.Model, "questionario_resposta")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        questionario_resposta=query.get(
                            pk=params.get("questionario_resposta")
                        )
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(questionario_resposta=None)

        if "data_fim_etapa" in params:
            if params.get("data_fim_etapa") != "":
                params.update(
                    data_fim_etapa=DateUtils.str_to_date(params.get("data_fim_etapa"))
                )
            else:
                params.update(data_fim_etapa=None)

        if "cargo_avaliador" in params:
            if params.get("cargo_avaliador") != "":
                field = getattr(self.Model, "cargo_avaliador")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        cargo_avaliador=query.get(pk=params.get("cargo_avaliador"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(cargo_avaliador=None)

        if "avaliador" in params:
            if params.get("avaliador") != "":
                field = getattr(self.Model, "avaliador")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(avaliador=query.get(pk=params.get("avaliador")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(avaliador=None)

        if "finalizado_em" in params:
            if params.get("finalizado_em") != "":
                params.update(
                    finalizado_em=DateUtils.str_to_datetime(params.get("finalizado_em"))
                )
            else:
                params.update(finalizado_em=None)

        if "lotacao_avaliador" in params:
            if params.get("lotacao_avaliador") != "":
                field = getattr(self.Model, "lotacao_avaliador")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        lotacao_avaliador=query.get(pk=params.get("lotacao_avaliador"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(lotacao_avaliador=None)

        if "data_inicio_etapa" in params:
            if params.get("data_inicio_etapa") != "":
                params.update(
                    data_inicio_etapa=DateUtils.str_to_date(
                        params.get("data_inicio_etapa")
                    )
                )
            else:
                params.update(data_inicio_etapa=None)

        if "criado_em" in params:
            if params.get("criado_em") != "":
                params.update(
                    criado_em=DateUtils.str_to_datetime(params.get("criado_em"))
                )
            else:
                params.update(criado_em=None)

        if "cargo_avaliado" in params:
            if params.get("cargo_avaliado") != "":
                field = getattr(self.Model, "cargo_avaliado")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        cargo_avaliado=query.get(pk=params.get("cargo_avaliado"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(cargo_avaliado=None)

        if "finalizado_por" in params:
            if params.get("finalizado_por") != "":
                field = getattr(self.Model, "finalizado_por")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        finalizado_por=query.get(pk=params.get("finalizado_por"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(finalizado_por=None)

        return params

    def get_query(self):
        query = super(self.__class__, self).get_query().order_by("periodo_avaliado")

        if self.request.user.has_perm("estagio.estagio_avaliado"):
            user = self.request.user.servidor
            posse = user.posses_ativas.filter(quadro__cargo__tipo_lei_cargo="EF")[0]
            eps = EstagioProbatorioServidor.objects.get(posse_servidor=posse)
            query = query.filter(avaliado=eps)
        else:
            query = query.exclude(id__gt=0)

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            status_display=instance.get_status(),
            status=instance.status,
            avaliado=nil_pk(instance.avaliado, None),
            avaliado_unicode=str(instance.avaliado) or None,
            lotacao_avaliado=nil_pk(instance.lotacao_avaliado, None),
            lotacao_avaliado_unicode=str(instance.lotacao_avaliado) or None,
            matricula_externo=instance.matricula_externo,
            data_avaliacao_externa=nil_date(instance.data_avaliacao_externa, None),
            media_comissao=float(instance.media_comissao or 0),
            questionario_resposta=nil_pk(instance.questionario_resposta, None),
            questionario_resposta_unicode=str(instance.questionario_resposta) or None,
            lotacao_externo=instance.lotacao_externo,
            avaliador_externo=instance.avaliador_externo,
            data_fim_etapa=nil_date(instance.data_fim_etapa, None),
            periodo_avaliado=int(instance.periodo_avaliado or 0),
            cargo_avaliador=nil_pk(instance.cargo_avaliador, None),
            cargo_avaliador_unicode=str(instance.cargo_avaliador) or None,
            dias_interrompidos=int(instance.dias_interrompidos or 0),
            observacao_comissao=instance.observacao_comissao,
            avaliador=nil_pk(instance.avaliador, None),
            avaliador_unicode=str(instance.avaliador) or None,
            finalizado_em=nil_datetime(instance.finalizado_em, None),
            lotacao_avaliador=nil_pk(instance.lotacao_avaliador, None),
            lotacao_avaliador_unicode=str(instance.lotacao_avaliador) or None,
            data_inicio_etapa=nil_date(instance.data_inicio_etapa, None),
            cargo_externo=instance.cargo_externo,
            criado_em=nil_datetime(instance.criado_em, None),
            cargo_avaliado=nil_pk(instance.cargo_avaliado, None),
            cargo_avaliado_unicode=str(instance.cargo_avaliado) or None,
            finalizado_por=nil_pk(instance.finalizado_por, None),
            finalizado_por_unicode=str(instance.finalizado_por) or None,
            servidor_id=instance.avaliado.posse_servidor.servidor.pk,
            questionario=str(instance.avaliado.configuracao.questionario) or None,
            questionario_id=nil_pk(instance.avaliado.configuracao.questionario, None),
            questionario_manifestacao_id=nil_pk(
                instance.avaliado.configuracao.questionario_manifestacao_servidor, None
            ),
            questionario_manifestacao=str(
                instance.avaliado.configuracao.questionario_manifestacao_servidor
            )
            or None,
            etapa_atual=instance.avaliado.current_stage,
            cargo_id=nil_pk(instance.avaliado.posse_servidor.quadro.cargo, None),
            posse_servidor=nil_pk(instance.avaliado.posse_servidor, None),
            posse_servidor_unicode=str(instance.avaliado.posse_servidor) or None,
        )

        return rst
