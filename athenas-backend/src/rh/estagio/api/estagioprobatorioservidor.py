# -*- coding: utf-8 -*-

from datetime import datetime

from django import forms as django_forms
from django.db import transaction
from django.db.models import Q

from contrib import extjs
from contrib.newrest import Restful
from contrib.nil import nil_date, nil_display, nil_pk
from contrib.utils import DateUtils, getLogger
from rh.estagio.models import (
    ComissaoAvaliadora,
    EstagioAvaliacao,
    EstagioComissaoServidor,
    EstagioProbatorioServidor,
    IntegrantesComissao,
)
from rh.models import Publicacao, Servidor

# from standard.questionario.models import estagio_servidor
from standard.questionario.views import QMontarQuestionario

log = getLogger(__name__)


class GepEstagioProbatorioServidor(Restful, QMontarQuestionario):

    _model = EstagioProbatorioServidor

    class Form(django_forms.ModelForm):
        class Meta:
            exclude = []
            model = EstagioProbatorioServidor

    full_text_index = (
        "posse_servidor__servidor__matricula__icontains",
        "posse_servidor__servidor__pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.gestor.Manage")')

    def homologacao_estagio(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            pks = self.request.POST.get("pk", "").split(",")
            EstagioProbatorioServidor.homologate(
                pks, self.request.POST.get("publicacao")
            )
        except Publicacao.DoesNotExist as err:
            log.exception(err)
            # log.info(estagio_servidor)
            # log.debug(estagio_servidor)
            rst.update(message="Publicação não encontrada!")
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
                message="Dados persistidos com sucesso!",
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def finalizar_etapa(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                estagio_servidor = self.Model.objects.get(
                    pk=int(self.request.POST.get("pk"))
                )

                # VERIFICA SE EXISTE UMA MANIFESTAÇÃO E SE O STATUS PARA FINALIZACAO DA ETAPA ESTA SETADO CORRETAMENTE
                if not estagio_servidor.manifestacao_servidor.exists() and int(
                    estagio_servidor.estado_avaliacao
                ) in [1]:
                    raise Exception("Essa etapa está pendente de manifestação!")

                # CASO OCORRA DE O SERVIDOR MANIFESTAR DISCORDANCIA E O CHEFE ALTERAR A AVALIAÇÃO DO ESTAGIO, O SERVIDOR
                # DEVE NOVAMENTE ALTERAR A MANFIESTAÇÃO PARA ALTEARR O STATUS E PERMITIR A FINALIZAÇÃO DA ETAPA
                if int(estagio_servidor.estado_avaliacao) in [1, 2]:
                    raise Exception(
                        "Essa etapa está pendente ou de reavaliação ou remanifestação em virtude de possível"
                        "pedido de discordância de avaliação.!"
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
                    rst.update(
                        message="%sª Etapa de %s atualizada com sucesso."
                        % (
                            estagio_servidor.avaliacoes_realizadas,
                            estagio_servidor._servidor_estagio_nome,
                        )
                    )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def bloquear_etapa(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                estagio_servidor = self.Model.objects.get(
                    pk=int(self.request.POST.get("pk"))
                )
                estagio_servidor.bloqueia_etapa()
                rst.update(
                    message="%sª Etapa de %s bloqueada com sucesso."
                    % (
                        estagio_servidor.current_stage,
                        estagio_servidor._servidor_estagio_nome,
                    )
                )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def desbloquear_etapa(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                estagio_servidor = self.Model.objects.get(
                    pk=int(self.request.POST.get("pk"))
                )
                estagio_servidor.bloqueia_etapa()

                if not estagio_servidor.bloqueada:
                    rst.update(message="Esta etapa não está bloqueada.")
                else:
                    estagio_servidor.desbloqueia_etapa()
                    rst.update(
                        message="%sª Etapa de %s desbloqueada com sucesso."
                        % (
                            estagio_servidor.current_stage,
                            estagio_servidor._servidor_estagio_nome,
                        )
                    )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def finalizar_processo(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                eps = self.Model.objects.filter(pk__in=self.request.POST.getlist("pks"))
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
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Processo realizado com sucesso.")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def montar_comissao(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                data = datetime.now()
                eps = self.Model.objects.filter(pk__in=self.request.POST.getlist("pks"))
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
                            comissao_id=comissao_avaliadora.id,
                            tipo_participante__in=[4],
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
                                    suplentes.filter().exclude(
                                        pk__in=integ.values("id")
                                    )[0],
                                    bulk=False,
                                )
                            elif (
                                estagio_servidor.posse_servidor.servidor
                                == integrante.servidor_id
                            ):
                                ecs.integrante_comissao_avaliadora.add(
                                    suplentes.filter().exclude(
                                        pk__in=integ.values("id")
                                    )[0],
                                    bulk=False,
                                )
                            elif integrante.impedimento:
                                ecs.integrante_comissao_avaliadora.add(
                                    suplentes.filter().exclude(
                                        pk__in=integ.values("id")
                                    )[0],
                                    bulk=False,
                                )
                            else:
                                ecs.integrante_comissao_avaliadora.add(integrante)
                        ecs.save()
                    else:
                        self.log.info(
                            "Estágio do(a) Servidor(a): %s não está liberado para formar comissao"
                            % estagio_servidor._servidor_estagio
                        )

        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Processo realizado com sucesso.")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def notifica_divergencia(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                eps = self.Model.objects.get(pk=int(self.request.POST.get("pk")))
                estag_aval = EstagioAvaliacao.objects.get(
                    periodo_avaliado=eps.current_stage, avaliado=eps
                )
                estag_aval.notifica_chefe_nao_concordancia(
                    eps, self.request.POST.get("mensagem")
                )
        except Exception as e:
            log.exception(e)
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True, message="Processo realizado com sucesso.")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def nota_comissao(self, args=[]):
        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            with transaction.atomic():
                eps = self.Model.objects.get(pk=int(self.request.POST.get("pk")))
                estag_aval = EstagioAvaliacao.objects.get(
                    periodo_avaliado=eps.current_stage, avaliado=eps
                )
                estag_aval.media_comissao = self.request.POST.get("nota")
                estag_aval.observacao_comissao = self.request.POST.get("observacao")
                estag_aval.save()
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(
                success=True,
            )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

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

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "ultima_avaliacao" in params:
            if params.get("ultima_avaliacao") != "":
                params.update(
                    ultima_avaliacao=DateUtils.str_to_date(
                        params.get("ultima_avaliacao")
                    )
                )
            else:
                params.update(ultima_avaliacao=None)

        if "fim_estagio" in params:
            if params.get("fim_estagio") != "":
                params.update(
                    fim_estagio=DateUtils.str_to_date(params.get("fim_estagio"))
                )
            else:
                params.update(fim_estagio=None)

        if "configuracao" in params:
            if params.get("configuracao") != "":
                field = getattr(self.Model, "configuracao")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(configuracao=query.get(pk=params.get("configuracao")))
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(configuracao=None)

        if "proxima_avaliacao" in params:
            if params.get("proxima_avaliacao") != "":
                params.update(
                    proxima_avaliacao=DateUtils.str_to_date(
                        params.get("proxima_avaliacao")
                    )
                )
            else:
                params.update(proxima_avaliacao=None)
        if "bloqueada" in params:
            params.update(bloqueada=params.get("bloqueada", "off").lower() == "on")

        if "posse_servidor" in params:
            if params.get("posse_servidor") != "":
                field = getattr(self.Model, "posse_servidor")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        posse_servidor=query.get(pk=params.get("posse_servidor"))
                    )
                except Exception as e:
                    log.exception(e)
                    raise e
            else:
                params.update(posse_servidor=None)

        if "ciencia_decisao_estagio" in params:
            if params.get("ciencia_decisao_estagio") != "":
                params.update(
                    ciencia_decisao_estagio=DateUtils.str_to_date(
                        params.get("ciencia_decisao_estagio")
                    )
                )
            else:
                params.update(ciencia_decisao_estagio=None)

        return params

    def get_query(self):
        query = super(GepEstagioProbatorioServidor, self).get_query()

        if not (
            self.request.user.has_perm("estagio.estagio_admin")
            or self.request.user.has_perm("estagio.estagio_avaliador")
        ):
            query = query.exclude(id__gt=0)

        return query

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        log.info(";;;;;;;; %s" % instance)

        rst.update(
            deadline=instance.get_deadline(),
            status=instance.status,
            status_display=instance.get_state_icons(),
            media=float(instance.media or 0),
            ultima_avaliacao=nil_date(instance.ultima_avaliacao, None),
            avaliacoes_realizadas=int(instance.avaliacoes_realizadas or 0),
            dias_falta=float(instance.dias_falta or 0),
            fim_estagio=nil_date(instance.fim_estagio, None),
            configuracao=nil_pk(instance.configuracao, None),
            configuracao_unicode=str(instance.configuracao) or None,
            proxima_avaliacao=nil_date(instance.proxima_avaliacao, None),
            estado_avaliacao=instance.estado_avaliacao,
            estado_avaliacao_display=nil_display(instance, "estado_avaliacao", None),
            bloqueada=instance.bloqueada,
            posse_servidor=nil_pk(instance.posse_servidor, None),
            posse_servidor_unicode=str(instance.posse_servidor) or None,
            data_exercicio=nil_date(instance._inicio_estagio, None),
            prazos="%s dia(s)" % instance.dias,
            etapa_atual=instance.current_stage,
            cargo_id=instance.posse_servidor.quadro.cargo_id,
            servidor_id=instance.posse_servidor.servidor.pk,
            questionario=str(instance.configuracao.questionario),
            questionario_id=instance.configuracao.questionario_id,
            questionario_manifestacao_id=str(
                instance.configuracao.questionario_manifestacao_servidor_id
            ),
            questionario_manifestacao=str(
                instance.configuracao.questionario_manifestacao_servidor
            )
            or None,
            chefe=str(instance.posse_servidor.servidor.chefe_imediato) or None,
            periodo_estagio=str(instance.get_periodo_estagio()) or None,
        )

        return rst


class GepPrintAvaliacao(extjs.ExtReportBuild):
    class Form(django_forms.Form):
        servidor = django_forms.CharField()
        cargo = django_forms.CharField()

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


class GepPrintDecisaoEstagio(extjs.ExtReportBuild):

    class Form(django_forms.Form):
        servidor = django_forms.CharField()
        cargo = django_forms.CharField()

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


class GepPrintAvaliacaoChefe(extjs.ExtReportBuild):

    class Form(django_forms.Form):
        servidor = django_forms.CharField()
        cargo = django_forms.CharField()
        etapa = django_forms.CharField()
        questionario_avaliacao = django_forms.CharField()
        questionario_manifestacao = django_forms.CharField()

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
