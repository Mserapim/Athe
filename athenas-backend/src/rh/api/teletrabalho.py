# -*- coding: utf-8 -*-
import datetime
import base64
import html
import re

from contrib.utils import getLogger, get_json_engine
from contrib.decorator import login_required

from contrib.newrest import RestfulDRY

from rh.const import (
    STATUS_TELETRABALHO_BLOQUEADO,
    STATUS_TELETRABALHO_IGNORADO,
    STATUS_TELETRABALHO_REVOGADO,
)
from rh.models import MovimentacaoTeletrabalho
from rh.afastamento.models import BaseLicencaAfastamento
from rh.pvf.models import (
    MarkTelework,
    PVFSolicitacaoDesbloqueioTeletrabalho,
    SendingTelework,
)
from django.db.models import Q, Max, F

from rh.pvf.const import STS_CANCELED_APPLICANT, STS_CANCELED_DGP
from reports.api.mpmt.rh.teletrabalho import RelatorioGestorTeletrabalho
from rh.teletrabalho.utils import (
    bloquear_mov_teletrabalho,
    ignorar_mov_teletrabalho,
    zerar_saldo_devedor,
)

log = getLogger(__name__)
json_engine = get_json_engine()


class RHGestorTeletrabalho(RestfulDRY):

    _model = MovimentacaoTeletrabalho

    force_upper = False
    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "servidor__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.teletrabalho.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(RHGestorTeletrabalho, self).model_to_dict(instance)
        _dict_.update(
            {
                "qtd_bloqueios": (
                    instance.qtd_bloqueios if instance.qtd_bloqueios else 0
                ),
                "qtd_dias_bloqueados": instance.qtd_dias_bloqueados,
                "icons": instance.icons,
            }
        )
        return _dict_

    def do_post(self):
        if self.validate_aprovador():
            return self.validate_aprovador()
        return super().do_post()

    def do_put(self, pk=None):
        if self.validate_aprovador():
            return self.validate_aprovador()
        return super().do_put(pk)

    def validate_aprovador(self):
        try:
            if self.request.POST:
                aprovador = self.request.POST.get("aprovador", None)
            elif self.request.PUT:
                aprovador = self.request.PUT.get("aprovador", None)
            if not aprovador:
                value = {
                    "success": False,
                    "message": "O campo Aprovador deve ser preenchido",
                }
                return value
        except Exception as error:
            log.error(error)

    @login_required("JSON")
    def bloquear_teletrabalho(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            plano_id = self.request.POST.get("plano_id", None)
            observacao = self.request.POST.get("observacao", None)
            anexo_id = self.request.POST.get("anexo_id", None)

            if not plano_id:
                raise Exception("Plano não informado.")

            mov_teletrabalho = self.Model.objects.get(pk=plano_id)
            if mov_teletrabalho.situacao in [
                STATUS_TELETRABALHO_BLOQUEADO,
                STATUS_TELETRABALHO_REVOGADO,
                STATUS_TELETRABALHO_IGNORADO,
            ]:
                raise Exception(
                    "Plano selecionado já está cancelado/ignorado ou revogado."
                )

            bloquear_mov_teletrabalho(
                mov_teletrabalho,
                observacao=observacao,
                anexo_id=anexo_id,
                status=STS_CANCELED_DGP,
            )
            rst.update(
                {
                    "success": True,
                    "message": "Procedimento realizado com sucesso.",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def ignorar_teletrabalho(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            plano_id = self.request.POST.get("plano_id", None)
            observacao = self.request.POST.get("observacao", None)

            if not plano_id:
                raise Exception("Plano não informado.")

            mov_teletrabalho = self.Model.objects.get(pk=plano_id)

            ignorar_mov_teletrabalho(mov_teletrabalho, observacao=observacao)
            rst.update(
                {
                    "success": True,
                    "message": "Procedimento realizado com sucesso.",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def solicitar_desbloqueio(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            plano_id = self.request.POST.get("plano_id", None)
            observacao = self.request.POST.get("observacao", None)
            anexo_id = self.request.POST.get("anexo_id", None)

            if not plano_id:
                raise Exception("Teletrabalho não informado.")

            mov_teletrabalho = self.Model.objects.get(pk=plano_id)
            if mov_teletrabalho.situacao == STATUS_TELETRABALHO_REVOGADO:
                raise Exception("Plano selecionado já está revogado.")

            PVFSolicitacaoDesbloqueioTeletrabalho.criar_solicitacao_sub(
                mov_teletrabalho, observacao, anexo_id
            )
            rst.update(
                {
                    "success": True,
                    "message": "Procedimento realizado com sucesso.",
                }
            )

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def zerar_saldo_devedor(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            plano_id = self.request.POST.get("plano_id", None)
            observacao = self.request.POST.get("observacao", None)
            anexo_id = self.request.POST.get("anexo_id", None)

            if not plano_id:
                raise Exception("Plano não informado.")

            mov_teletrabalho = self.Model.objects.get(pk=plano_id)

            resultado = zerar_saldo_devedor(mov_teletrabalho, observacao, anexo_id)

            if resultado["success"]:
                rst.update(
                    {
                        "success": True,
                        "message": resultado["message"],
                    }
                )
            else:
                rst.update({"message": resultado["message"]})

        except MovimentacaoTeletrabalho.DoesNotExist:
            rst.update({"message": "MovimentacaoTeletrabalho não encontrada."})
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def export(self, args=[]):
        obj = {
            "success": True,
            "message": "Download em andamento",
        }

        pk = self.request.GET.get("mov_teletrabalho_pk")

        if not pk:
            obj["message"] = "Erro ao tentar realizar o download"
            obj["success"] = False

        else:
            metas = (
                MarkTelework.objects.filter(mark_plan__mov_teletrabalho__pk=pk)
                .exclude(request__status=STS_CANCELED_APPLICANT)
                .exclude(request__cancelado_solicitacao=True)
                .order_by("-request__pk")
            )

            rst = []

            for meta in metas:
                competencia = datetime.date(
                    meta.request.reference_year, meta.request.reference_month, 1
                )

                if meta.total_completed and meta.mark:
                    porcentagem = f"{round((meta.total_completed/meta.mark)*100, 2)}%"
                else:
                    porcentagem = ""

                q_observacao_aprovador = meta.request.portalrequesthistory_set.filter(
                    action=12
                ).exclude(observation="")
                observacao_aprovador = (
                    q_observacao_aprovador.last().observation
                    if q_observacao_aprovador
                    else ""
                )

                q_observacao_solicitacao = meta.request.portalrequesthistory_set.filter(
                    action=1
                ).exclude(observation="")
                if q_observacao_solicitacao.last() is None:
                    observacao_solicitacao = ""
                else:
                    observacao_solicitacao = (
                        q_observacao_solicitacao.last().observation
                        if q_observacao_solicitacao.last().observation
                        else ""
                    )

                rst.append(
                    {
                        "Servidor": str(meta.request.employee),
                        "Lotacao": str(meta.mark_plan.mov_teletrabalho.lotacao),
                        "Data inicio": str(meta.mark_plan.data_inicio),
                        "Data fim": str(meta.mark_plan.data_fim),
                        "Gedoc": meta.mark_plan.mov_teletrabalho.gedoc,
                        "Competencia": competencia.strftime("%m/%Y"),
                        "Codigo VDF": str(meta.request.pk),
                        "Situacao": meta.request.get_status_display(),
                        "Observacao do solicitante": observacao_solicitacao,
                        "Observacao do aprovador": observacao_aprovador,
                        "Descricao da meta": meta.mark_plan.descricao,
                        "Observacao da meta": (
                            meta.observation if meta.observation else ""
                        ),
                        "Periodicidade": meta.mark_plan.get_periodicity_display(),
                        "Situacao da meta": (
                            meta.get_mark_situation_display()
                            if meta.get_mark_situation_display()
                            else ""
                        ),
                        "Meta": meta.mark,
                        "Total da meta": (
                            meta.total_completed if meta.total_completed else ""
                        ),
                        "Porcentagem": porcentagem,
                    }
                )

            renderer = self.get_renderer(self.request.GET.get("format", "text/csv"))
            self.response["content-disposition"] = "attachment; filename=export.csv"
            renderer(rst)

    def generate_report_pdf(self, *args):
        RelatorioGestorTeletrabalho(
            self.request, self.response
        ).generate_teletrabalho_pdf()

    def generate_report_csv(self, *args):
        RelatorioGestorTeletrabalho(
            self.request, self.response
        ).generate_teletrabalho_csv()

    def generate_report_xls(self, *args):
        RelatorioGestorTeletrabalho(
            self.request, self.response
        ).generate_teletrabalho_xls()


class RHGestorMarkTelework(RestfulDRY):

    _model = MarkTelework

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.teletrabalho.mark_telework.Manage")')

    def get_query(self):
        query = super(RHGestorMarkTelework, self).get_query()
        return (
            query.exclude(request__status=STS_CANCELED_APPLICANT)
            .exclude(request__cancelado_solicitacao=True)
            .distinct("request")
        )

    def limpar_texto(self, text):
        """Remove tags HTML e decodifica entidades HTML."""
        if not text:
            return ""
        clean_text = re.sub(r"<[^>]*>", "", text)
        return html.unescape(clean_text)

    def model_to_dict(self, instance):
        params = super(RHGestorMarkTelework, self).model_to_dict(instance)

        competence = datetime.date(
            instance.request.reference_year, instance.request.reference_month, 1
        )
        status = instance.request.get_status_display()
        q_aproove_observation = instance.request.portalrequesthistory_set.filter(
            action=12
        ).exclude(observation="", observation__isnull=True)
        aproove_observation = (
            q_aproove_observation.last().observation if q_aproove_observation else ""
        )
        q_observacao_solicitante = instance.request.portalrequesthistory_set.filter(
            action=1
        ).exclude(observation="", observation__isnull=True)
        observacao_solicitante = (
            q_observacao_solicitante.last().observation
            if q_observacao_solicitante
            else ""
        )
        if instance.total_completed and instance.mark:
            percentage = f"{round((instance.total_completed/instance.mark)*100, 2)}%"
        else:
            percentage = ""
        q_anexo = SendingTelework.objects.get(pk=instance.request).anexo
        possui_anexo = True if q_anexo else False
        possui_anexo_display = "Sim" if q_anexo else "Não"

        servidor = str(instance.request.employee)
        data_inicio_plano = instance.mark_plan.mov_teletrabalho.data_inicio.strftime(
            "%d/%m/%Y"
        )
        data_fim_plano = instance.mark_plan.mov_teletrabalho.data_fim.strftime(
            "%d/%m/%Y"
        )
        gedoc_plano = str(instance.mark_plan.mov_teletrabalho.gedoc)
        status_plano = (
            "Ativo" if instance.mark_plan.mov_teletrabalho.ativo else "Inativo"
        )

        possui_afastamento = BaseLicencaAfastamento.objects.filter(
            Q(servidor=instance.request.employee)
            & Q(data_inicio__month__lte=instance.request.reference_month)
            & Q(data_inicio__year__lte=instance.request.reference_year)
            & Q(data_fim__month__gte=instance.request.reference_month)
            & Q(data_fim__year__gte=instance.request.reference_year)
        ).exclude(estado__in=[4])

        possui_saldo_devedor_display = "Sim" if instance.saldo_devedor else "Não"

        params.update(
            description_mark=instance.description_mark,
            mark=instance.mark,
            is_update=instance.is_update,
            mark_plan_periodicity=instance.mark_plan.periodicity,
            mark_plan_periodicity_display=instance.mark_plan.get_periodicity_display(),
            competence=competence.strftime("%m/%Y"),
            status=status,
            aproove_observation=aproove_observation,
            percentage=percentage,
            observacao_solicitante=self.limpar_texto(observacao_solicitante),
            possui_anexo=possui_anexo,
            possui_anexo_display=possui_anexo_display,
            servidor=servidor,
            data_inicio_plano=data_inicio_plano,
            data_fim_plano=data_fim_plano,
            gedoc_plano=gedoc_plano,
            status_plano=status_plano,
            possui_afastamento=True if possui_afastamento else False,
            possui_saldo_devedor=True if instance.saldo_devedor else False,
            possui_saldo_devedor_display=possui_saldo_devedor_display,
        )
        return params

    def download_anexo(self, *args):
        obj = {
            "success": True,
            "message": "Download do Anexo em Andamento",
        }

        request_pk = self.request.POST.get("request_pk")

        if not request_pk:
            obj["message"] = "Erro ao tentar realizar o Download do anexo"
            obj["success"] = False
        else:
            anexo = SendingTelework.objects.get(pk=request_pk).anexo
            if not anexo:
                obj["message"] = "Não há anexo para realizar o Download"
                obj["success"] = False

                self.response["content-type"] = "text/javascript"
            else:
                with open(anexo.absolute_path, "rb") as f:
                    file_content = f.read()
                    file_base64 = base64.b64encode(file_content).decode("utf-8")

                obj["arquivo"] = file_base64

        self.response.write(json_engine.encode(obj))


class RHDetalheMetaTeletrabalho(RestfulDRY):

    _model = MarkTelework

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.teletrabalho.detalhe_meta.Manage")')

    def get_query(self):
        return super(RHDetalheMetaTeletrabalho, self).get_query()

    def model_to_dict(self, instance):
        params = super(RHDetalheMetaTeletrabalho, self).model_to_dict(instance)

        competence = datetime.date(
            instance.request.reference_year, instance.request.reference_month, 1
        )
        status = instance.request.get_status_display()
        q_aproove_observation = instance.request.portalrequesthistory_set.filter(
            action=12
        ).exclude(observation="", observation__isnull=True)
        aproove_observation = (
            q_aproove_observation.last().observation if q_aproove_observation else ""
        )
        q_observacao_solicitante = instance.request.portalrequesthistory_set.filter(
            action=1
        ).exclude(observation="", observation__isnull=True)
        observacao_solicitante = (
            q_observacao_solicitante.last().observation
            if q_observacao_solicitante
            else ""
        )

        if instance.saldo_devedor_anterior:
            meta_mes = instance.mark + instance.saldo_devedor_anterior
        else:
            meta_mes = instance.mark

        if instance.total_completed and instance.mark:
            percentage = f"{round((instance.total_completed/meta_mes)*100, 2)}%"
        else:
            percentage = ""
        q_anexo = SendingTelework.objects.get(pk=instance.request).anexo
        possui_anexo = True if q_anexo else False

        params.update(
            description_mark=instance.description_mark,
            mark=instance.mark,
            is_update=instance.is_update,
            mark_plan_periodicity=instance.mark_plan.periodicity,
            mark_plan_periodicity_display=instance.mark_plan.get_periodicity_display(),
            competence=competence.strftime("%m/%Y"),
            status=status,
            aproove_observation=aproove_observation,
            percentage=percentage,
            observacao_solicitante=observacao_solicitante,
            possui_anexo=possui_anexo,
            meta_mes=meta_mes,
            saldo_devedor_anterior=instance.saldo_devedor_anterior,
        )
        return params
