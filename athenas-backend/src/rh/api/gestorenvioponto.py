from calendar import monthrange
from datetime import datetime, time
import json
from django.db.models import Q, Min, Max
from common.util.send_email import EmailNotification
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import DateUtils, getLogger, get_json_engine
from engine.mq.models import Task
from reports.data.mpmt.pvf.approversvdf import get_approver_vdf
from rh.afastamento.models import BaseLicencaAfastamento
from rh.const import CANCELED, WORKPLACE
from rh.models import MovimentacaoPosse, Servidor, MovimentacaoTeletrabalho
from rh.pvf.models import PortalRequest, PortalRequestHistory, SendingTimeSheet
from rh.pvf.tasks import start_send_mail_gestor_folha_ponto
from rh.registerpoint.models import FolhaPontoHistoricoNotificacoes
from standard.models import Choice, EmailTemplate, Item
from django.db import transaction
from django.template.loader import render_to_string


log = getLogger(__name__)
json_engine = get_json_engine()


class RHGestorEnvioPontos(RestfulDRY):

    _model = Servidor

    full_text_index = (
        "matricula__icontains",
        "pessoa_fisica__nome__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new rh.gestorenvioponto.Manage")

    def get_store_notificacoes(self, args=[]):
        obj = {"totalRows": 0, "result": []}
        ano = self.request.POST.get("ano")
        mes = self.request.POST.get("mes")
        servidor_id = self.request.POST.get("servidor")
        if ano and mes and servidor_id:
            servidor = Servidor.objects.get(pk=servidor_id)
            notificacoes = FolhaPontoHistoricoNotificacoes.objects.filter(
                servidor=servidor,
                referencia_mes=mes,
                referencia_ano=ano,
            )
            obj["totalRows"] = notificacoes.count()
            for notificacao in notificacoes:
                obj["result"].append(
                    {
                        "data": DateUtils.datetime_to_str(notificacao.created_at),
                        "email": notificacao.servidor.pessoa_fisica.email_institucional,
                        "usuario": notificacao.created_by.username,
                    }
                )
        self.response["content-type"] = "text/javascript"
        self.response.write(json_engine.encode(obj))

    def get_query(self):
        ano = int(self.request.GET.get("periodo_ano", datetime.today().year))
        mes = int(self.request.GET.get("periodo_mes", datetime.today().month))

        queryset = super(RHGestorEnvioPontos, self).get_query()

        primeiro_dia_mes = datetime(ano, mes, 1)
        ultimo_dia_mes = datetime(ano, mes, monthrange(ano, mes)[1])

        queryset = queryset.filter(
            Q(
                movimentacaopessoal__movimentacaoposse__data_desligamento__gt=primeiro_dia_mes
            )
            | Q(movimentacaopessoal__movimentacaoposse__data_desligamento__isnull=True),
            movimentacaopessoal__movimentacaoposse__isnull=False,
            movimentacaopessoal__movimentacaoposse__data_posse__lte=ultimo_dia_mes,
            type_by_possession__in=[
                "EFE",
                "ECM",
                "EFC",
                "CMS",
                "REQ",
                "REX",
                "RCM",
                "RFC",
                "RES",
                "EST",
                "VOL",
                "EXT",
            ],
        ).distinct()

        return queryset

    def model_to_dict(self, instance):
        rst = super(RHGestorEnvioPontos, self).model_to_dict(instance)

        ano = int(self.request.GET.get("periodo_ano", datetime.today().year))
        mes = int(self.request.GET.get("periodo_mes", datetime.today().month))

        ultimo_dia_mes = monthrange(ano, mes)[1]
        data_inicio_mes = datetime(ano, mes, 1)
        data_fim_mes = datetime(ano, mes, ultimo_dia_mes)

        lotacao = instance._raw_locations(active=True, option=WORKPLACE).first()
        if lotacao:
            nome_lotacao = str(lotacao.lotacao)
        else:
            nome_lotacao = "Sem lotação"

        status_excluidos_label = [
            "Cancelado Solicitante",
            "Aguardando Envio",
            "Cancelado DGP",
            "Indeferido",
        ]
        status_excluidos = Choice.objects.filter(
            app_label="pvf", name="REQUEST_STATUS", label__in=status_excluidos_label
        ).values_list("value", flat=True)

        ultimo_envio = (
            SendingTimeSheet.objects.filter(employee=instance)
            .exclude(status__in=status_excluidos)
            .last()
        )
        mes_ultimo_envio = ultimo_envio.reference_month if ultimo_envio else None
        ano_ultimo_envio = ultimo_envio.reference_year if ultimo_envio else None

        folha_ponto_mes = (
            SendingTimeSheet.objects.filter(
                employee=instance, reference_month=mes, reference_year=ano
            )
            .exclude(status__in=status_excluidos)
            .last()
        )
        status = (
            "Não criado"
            if not folha_ponto_mes
            else folha_ponto_mes.get_status_display()
        )
        cod_vdf = folha_ponto_mes.pk if folha_ponto_mes else None

        if folha_ponto_mes:
            aprovador = get_approver_vdf(folha_ponto_mes, instance)
        elif ultimo_envio:
            aprovador = get_approver_vdf(ultimo_envio, instance)
        else:
            request = PortalRequest()
            aprovador = get_approver_vdf(request, instance)

        historico_vdf = PortalRequestHistory.objects.filter(portal_request=cod_vdf)
        enviado_em = None
        aprovado_em = None
        efetivado_em = None
        if historico_vdf:
            action_enviado_em = Choice.objects.get(
                app_label="pvf", name="ACTION_TAKEN", label="Solicitação"
            ).value
            action_aprovado_em = Choice.objects.get(
                app_label="pvf", name="ACTION_TAKEN", label="Deferido"
            ).value
            action_efetivado_em = Choice.objects.get(
                app_label="pvf", name="ACTION_TAKEN", label="Efetivado"
            ).value

            enviado_em = (
                historico_vdf.filter(action=action_enviado_em)
                .order_by("-date")
                .first()
                .date
                if historico_vdf.filter(action=action_enviado_em).exists()
                else None
            )
            aprovado_em = (
                historico_vdf.filter(action=action_aprovado_em)
                .order_by("-date")
                .first()
                .date
                if historico_vdf.filter(action=action_aprovado_em).exists()
                else None
            )
            efetivado_em = (
                historico_vdf.filter(action=action_efetivado_em)
                .order_by("-date")
                .first()
                .date
                if historico_vdf.filter(action=action_efetivado_em).exists()
                else None
            )

        teletrabalho_ativo = MovimentacaoTeletrabalho.objects.filter(
            servidor=instance, data_inicio__lte=data_fim_mes, data_fim__gte=data_fim_mes
        ).exists()

        afastamentos = BaseLicencaAfastamento.objects.filter(
            Q(data_inicio__lte=data_fim_mes)
            & Q(servidor=instance)
            & Q(data_fim__gte=data_inicio_mes)
        ).exclude(estado__in=[CANCELED])

        tipo_afastamento = None
        data_inicio_afastamento = None
        data_fim_afastamento = None
        afastamentos_str = []
        for afastamento in afastamentos:
            tipo_afastamento = afastamento.situation_unicode
            data_inicio_afastamento = afastamento.data_inicio
            data_fim_afastamento = afastamento.data_fim
            if (
                datetime.combine(data_inicio_afastamento, time.min) <= data_inicio_mes
                and datetime.combine(data_fim_afastamento, time.max) >= data_fim_mes
            ):
                status = "Isento de envio"
            if data_fim_afastamento:
                afastamento_str = f"{tipo_afastamento} de {data_inicio_afastamento.strftime('%d/%m/%Y')} a {data_fim_afastamento.strftime('%d/%m/%Y')}"
            else:
                afastamento_str = f"{tipo_afastamento} de {data_inicio_afastamento.strftime('%d/%m/%Y')}"
            afastamentos_str.append(afastamento_str)
        tipo_afastamento = ", ".join(afastamentos_str)

        movposse = MovimentacaoPosse.objects.filter(servidor=instance, ativo=True)
        tipos_membro = ["MBR", "MEL", "MCM", "MEC", "MBR2", "MEL2", "MCM2", "MEC2"]
        dt_admissao = None
        if movposse.last():
            if instance.type_by_possession in tipos_membro:
                dt_admissao = (
                    MovimentacaoPosse.objects.filter(servidor=instance)
                    .first()
                    .data_posse
                )
            else:
                dt_admissao = movposse.last().data_posse

        qtd_notificacoes = FolhaPontoHistoricoNotificacoes.objects.filter(
            servidor=instance,
            referencia_mes=mes,
            referencia_ano=ano,
        ).count()

        rst.update(
            servidor_pk=instance.pk,
            ativo=instance.ativo,
            matricula=instance.matricula,
            nome=instance.pessoa_fisica.social_name,
            lotacao=nome_lotacao,
            categoria_funcional=instance.get_type_by_possession_display(),
            type_by_possession=instance.type_by_possession,
            in_teletrabalho="SIM" if teletrabalho_ativo else "NÃO",
            ultimo_envio=(
                f"{mes_ultimo_envio:02d}/{ano_ultimo_envio}" if ultimo_envio else None
            ),
            aprovador=aprovador,
            cod_vdf=cod_vdf,
            enviado_em=enviado_em.strftime("%d/%m/%Y") if enviado_em else None,
            aprovado_em=aprovado_em.strftime("%d/%m/%Y") if aprovado_em else None,
            efetivado_em=efetivado_em.strftime("%d/%m/%Y") if efetivado_em else None,
            tipo_afastamento=tipo_afastamento,
            status=status,
            dt_admissao=dt_admissao.strftime("%d/%m/%Y") if dt_admissao else "",
            qtd_notificacoes=qtd_notificacoes,
            ano=ano,
            mes=mes,
        )

        return rst

    def do_get(self, pk=None):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        if pk is not None:
            try:
                inst = self.get_query().get(pk=pk)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                rst.update(message=str(e))
                log.exception(e)
            else:
                rst.update(
                    {
                        "success": True,
                        "message": "Processo com sucesso!",
                        "instance": self.model_to_dict(inst),
                    }
                )
        else:
            try:
                query = self.get_query()
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                query = self.filtrar_registros(query)

                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                query = self.remove_projection(query)

                rst.update(count=query.count())
                query = self.do_page(query)
            except NotImplementedError:
                rst.update(
                    message="Erro de implementação, não foi informado o modelo de dados para o Restful"
                )
            except Exception as e:
                log.exception(str(e))
                rst.update(message=str(e))
            else:
                rst.update(
                    {
                        "collection": [self.model_to_dict(record) for record in query],
                        "success": True,
                        "message": "Processado com sucesso!",
                    }
                )

        return rst

    def filtrar_registros(self, query):
        filtro_teletrabalho = self.request.GET.get("teletrabalho", "teletrabalho_nao")
        filtro_status = self.request.GET.get("status", None)
        filtro_notificado = self.request.GET.get("notificado", None)

        periodo_ano = int(self.request.GET.get("periodo_ano", datetime.today().year))
        periodo_mes = int(self.request.GET.get("periodo_mes", datetime.today().month))

        primeiro_dia_mes = datetime(periodo_ano, periodo_mes, 1)
        ultimo_dia_mes = datetime(
            periodo_ano, periodo_mes, monthrange(periodo_ano, periodo_mes)[1]
        )

        if filtro_notificado:
            if filtro_notificado == "sim":
                query = query.filter(
                    folha_ponto_historico_notificacoes__referencia_ano=periodo_ano,
                    folha_ponto_historico_notificacoes__referencia_mes=periodo_mes,
                )
            elif filtro_notificado == "nao":
                query = query.exclude(
                    folha_ponto_historico_notificacoes__referencia_ano=periodo_ano,
                    folha_ponto_historico_notificacoes__referencia_mes=periodo_mes,
                )

        if filtro_teletrabalho:
            if filtro_teletrabalho == "teletrabalho_sim":
                query = query.filter(
                    Q(
                        movimentacaopessoal__movimentacaoteletrabalho__data_inicio__lte=ultimo_dia_mes
                    ),
                    Q(
                        movimentacaopessoal__movimentacaoteletrabalho__data_fim__gte=ultimo_dia_mes
                    ),
                )
            elif filtro_teletrabalho == "teletrabalho_nao":
                query = query.exclude(
                    Q(
                        movimentacaopessoal__movimentacaoteletrabalho__data_inicio__lte=ultimo_dia_mes
                    ),
                    Q(
                        movimentacaopessoal__movimentacaoteletrabalho__data_fim__gte=ultimo_dia_mes
                    ),
                )

        query_isento = query.filter(
            Q(
                Q(
                    movimentacaopessoal__baselicencaafastamento__data_fim__gte=ultimo_dia_mes
                )
                & Q(
                    movimentacaopessoal__baselicencaafastamento__data_inicio__lte=primeiro_dia_mes
                )
            ),
            Q(movimentacaopessoal__baselicencaafastamento__estado__in=[1, 2, 3]),
        )

        if filtro_status:
            if filtro_status == "nao_criado":
                status_possiveis = [2, 3, 4]

                query_status = query.filter(
                    Q(
                        portal_request_employee__sendingtimesheet__reference_year=periodo_ano,
                        portal_request_employee__sendingtimesheet__reference_month=periodo_mes,
                        portal_request_employee__status__in=status_possiveis,
                    )
                ).values_list("pk", flat=True)

                query = query.exclude(
                    pk__in=query_isento.values_list("pk", flat=True)
                ).exclude(pk__in=query_status)

            elif filtro_status == "aguardando_aprovador":
                query = query.filter(
                    Q(portal_request_employee__status=2),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                    ),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                    ),
                )
            elif filtro_status == "aguardando_efetivacao":
                query = query.filter(
                    Q(portal_request_employee__status=3),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                    ),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                    ),
                )
            elif filtro_status == "efetivado":
                query = query.filter(
                    Q(portal_request_employee__status=4),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_year=periodo_ano
                    ),
                    Q(
                        portal_request_employee__sendingtimesheet__reference_month=periodo_mes
                    ),
                )
            elif filtro_status == "isento":
                query = query_isento

        return query

    @login_required("JSON")
    def anos_folha_ponto(self, args=[]):
        obj = {"root": []}

        ano_minimo = SendingTimeSheet.objects.aggregate(
            ano_minimo=Min("reference_year")
        )["ano_minimo"]
        ano_maximo = SendingTimeSheet.objects.aggregate(
            ano_maximo=Max("reference_year")
        )["ano_maximo"]

        if ano_minimo is not None and ano_maximo is not None:
            for ano in range(ano_maximo, ano_minimo - 1, -1):
                obj["root"].append({"pk": ano, "descricao": str(ano)})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def enviar_notificacao_email(self, *args):
        obj = {
            "success": True,
            "message": "Nada Feito",
        }

        try:
            servidor_pk = int(self.request.POST.get("matricula"))
            mes_competencia = self.request.POST.get("mes")
            ano_competencia = self.request.POST.get("ano")
            ultimo_envio = self.request.POST.get("ultimo_envio")
            aprovador = self.request.POST.get("aprovador")

            competencia = f"{mes_competencia}/{ano_competencia}"
            servidor = Servidor.objects.get(matricula=servidor_pk)
            aprovador = Servidor.objects.get(
                pessoa_fisica__social_name=aprovador, ativo=True
            )

            if servidor.type_by_possession == "EST":
                codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO_ESTAGIARIO"
            elif servidor.type_by_possession == "RES":
                codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO_RESIDENTE"
            else:
                codigo_email = "ENTREGA_FOLHA_PONTO_NOTIFICACAO"

            email_template = EmailTemplate.objects.get(code=codigo_email)

            conteudo = (
                email_template.contents.replace(
                    "@nome_servidor%", servidor.pessoa_fisica.social_name
                )
                .replace("@comp%", competencia)
                .replace("@comp_ultimo_envio%", ultimo_envio)
            )

            lista_destinatarios = [
                {
                    "email": servidor.pessoa_fisica.email_institucional,
                    "nome": servidor.pessoa_fisica.social_name,
                    "idUsuario": servidor.id_usuario_mastiff,
                }
            ]

            email_aprovador = (
                aprovador.pessoa_fisica.email_institucional if aprovador else None
            )
            if email_aprovador:
                lista_destinatarios.append(
                    {
                        "email": email_aprovador,
                        "nome": aprovador.pessoa_fisica.social_name,
                        "idUsuario": aprovador.id_usuario_mastiff,
                    }
                )

            config_email_item = Item.objects.get(key="notificacao_envio_folha_ponto")

            lista_email = config_email_item.value.split(",")

            for email in lista_email:
                lista_destinatarios.append({"email": email, "nome": email.upper()})

            html_content = render_to_string(
                "util/template_email.html", {"message": conteudo}
            )

            with transaction.atomic():
                EmailNotification().send_email_default(
                    lista_destinatarios, email_template.subject, html_content
                )
                FolhaPontoHistoricoNotificacoes.objects.create(
                    servidor=servidor,
                    referencia_ano=ano_competencia,
                    referencia_mes=mes_competencia,
                )
            obj["message"] = (
                f" Notificação enviada para {servidor.pessoa_fisica.social_name}!"
            )

        except Exception as error:
            log.error(error)
            obj["success"] = False
            obj["message"] = "Erro ao tentar Enviar a Notificação por Email."

        self.response.write(json_engine.encode(obj))

    @login_required(type="JSON")
    def enviar_notificacao_em_massa(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            mes_competencia = self.request.POST.get("mes")
            ano_competencia = self.request.POST.get("ano")
            status = self.request.POST.get("status")
            posses = self.request.POST.get("posses")
            notificado = self.request.POST.get("notificado")

            Task.start(
                start_send_mail_gestor_folha_ponto,
                mes_competencia=mes_competencia,
                ano_competencia=ano_competencia,
                status=status,
                posses=posses,
                notificado=notificado,
                user=get_current_user().pk,
            )
        except Exception as e:
            rst.update(message="{}".format(e))
        else:
            rst.update(success=True, message="Notificações de email enviada.")
        self.renderer(rst)

    def export(self, args=[]):
        rst = []

        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        if "teletrabalho" in self.request.GET or "status" in self.request.GET:
            query = self.filtrar_registros(query)
        query = self.do_page(query)

        ano = int(self.request.GET.get("periodo_ano", datetime.today().year))
        mes = int(self.request.GET.get("periodo_mes", datetime.today().month))

        ultimo_dia_mes = monthrange(ano, mes)[1]
        data_inicio_mes = datetime(ano, mes, 1)
        data_fim_mes = datetime(ano, mes, ultimo_dia_mes)

        for record in query:
            if record:
                lotacao = record._raw_locations(active=True, option=WORKPLACE).first()

                teletrabalho_ativo = MovimentacaoTeletrabalho.objects.filter(
                    servidor=record,
                    data_inicio__lte=data_fim_mes,
                    data_fim__gte=data_fim_mes,
                ).exists()

                afastamentos = BaseLicencaAfastamento.objects.filter(
                    Q(data_inicio__lte=data_fim_mes)
                    & Q(servidor=record)
                    & Q(data_fim__gte=data_inicio_mes)
                ).exclude(estado__in=[CANCELED])
                tipo_afastamento = None
                data_inicio_afastamento = None
                data_fim_afastamento = None
                afastamentos_str = []
                for afastamento in afastamentos:
                    tipo_afastamento = afastamento.situation_unicode
                    data_inicio_afastamento = afastamento.data_inicio
                    data_fim_afastamento = afastamento.data_fim
                    if (
                        datetime.combine(data_inicio_afastamento, time.min)
                        <= data_inicio_mes
                        and datetime.combine(data_fim_afastamento, time.max)
                        >= data_fim_mes
                    ):
                        status = "Isento de envio"
                    if data_fim_afastamento:
                        afastamento_str = f"{tipo_afastamento} de {data_inicio_afastamento.strftime('%d/%m/%Y')} a {data_fim_afastamento.strftime('%d/%m/%Y')}"
                    else:
                        afastamento_str = f"{tipo_afastamento} de {data_inicio_afastamento.strftime('%d/%m/%Y')}"
                    afastamentos_str.append(afastamento_str)
                tipo_afastamento = ", ".join(afastamentos_str)

                status_excluidos_label = [
                    "Cancelado Solicitante",
                    "Aguardando Envio",
                    "Cancelado DGP",
                    "Indeferido",
                ]
                status_excluidos = Choice.objects.filter(
                    app_label="pvf",
                    name="REQUEST_STATUS",
                    label__in=status_excluidos_label,
                ).values_list("value", flat=True)

                ultimo_envio = (
                    SendingTimeSheet.objects.filter(employee=record)
                    .exclude(status__in=status_excluidos)
                    .last()
                )
                mes_ultimo_envio = (
                    ultimo_envio.reference_month if ultimo_envio else None
                )
                ano_ultimo_envio = ultimo_envio.reference_year if ultimo_envio else None

                folha_ponto_mes = (
                    SendingTimeSheet.objects.filter(
                        employee=record, reference_month=mes, reference_year=ano
                    )
                    .exclude(status__in=status_excluidos)
                    .last()
                )
                status = (
                    "Não criado"
                    if not folha_ponto_mes
                    else folha_ponto_mes.get_status_display()
                )
                cod_vdf = folha_ponto_mes.pk if folha_ponto_mes else None

                if folha_ponto_mes:
                    aprovador = get_approver_vdf(folha_ponto_mes, record)
                elif ultimo_envio:
                    aprovador = get_approver_vdf(ultimo_envio, record)
                else:
                    request = PortalRequest()
                    aprovador = get_approver_vdf(request, record)

                historico_vdf = PortalRequestHistory.objects.filter(
                    portal_request=cod_vdf
                )
                enviado_em = None
                aprovado_em = None
                efetivado_em = None
                if historico_vdf:
                    action_enviado_em = Choice.objects.get(
                        app_label="pvf", name="ACTION_TAKEN", label="Solicitação"
                    ).value
                    action_aprovado_em = Choice.objects.get(
                        app_label="pvf", name="ACTION_TAKEN", label="Deferido"
                    ).value
                    action_efetivado_em = Choice.objects.get(
                        app_label="pvf", name="ACTION_TAKEN", label="Efetivado"
                    ).value

                    enviado_em = (
                        historico_vdf.filter(action=action_enviado_em)
                        .order_by("-date")
                        .first()
                        .date
                        if historico_vdf.filter(action=action_enviado_em).exists()
                        else None
                    )
                    aprovado_em = (
                        historico_vdf.filter(action=action_aprovado_em)
                        .order_by("-date")
                        .first()
                        .date
                        if historico_vdf.filter(action=action_aprovado_em).exists()
                        else None
                    )
                    efetivado_em = (
                        historico_vdf.filter(action=action_efetivado_em)
                        .order_by("-date")
                        .first()
                        .date
                        if historico_vdf.filter(action=action_efetivado_em).exists()
                        else None
                    )

                movposse = MovimentacaoPosse.objects.filter(servidor=record, ativo=True)
                tipos_membro = [
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                ]
                dt_admissao = None
                if movposse.last():
                    if record.type_by_possession in tipos_membro:
                        dt_admissao = (
                            MovimentacaoPosse.objects.filter(servidor=record)
                            .first()
                            .data_posse
                        )
                    else:
                        dt_admissao = movposse.last().data_posse

                rst.append(
                    {
                        "Matrícula": record.matricula,
                        "Nome": record.pessoa_fisica.social_name,
                        "Lotação": str(lotacao.lotacao) if lotacao else "Sem lotação",
                        "Categoria Funcional": record.get_type_by_possession_display(),
                        "Aprovador": aprovador,
                        "Data Admissão": (
                            dt_admissao.strftime("%d/%m/%Y") if dt_admissao else ""
                        ),
                        "Status": status,
                        "Cód. VDF": cod_vdf if cod_vdf else "",
                        "Teletrabalho": "SIM" if teletrabalho_ativo else "NÃO",
                        "Afastamento": tipo_afastamento,
                        "Último Envio": (
                            f"{mes_ultimo_envio:02d}/{ano_ultimo_envio}"
                            if ultimo_envio
                            else ""
                        ),
                        "Chave": record.pk,
                        "Enviado em": (
                            enviado_em.strftime("%d/%m/%Y") if enviado_em else ""
                        ),
                        "Aprovado em": (
                            aprovado_em.strftime("%d/%m/%Y") if aprovado_em else ""
                        ),
                        "Efetivado em": (
                            efetivado_em.strftime("%d/%m/%Y") if efetivado_em else ""
                        ),
                    }
                )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)


class RHFolhaPontoHistoricoNotificacoes(RestfulDRY):

    _model = FolhaPontoHistoricoNotificacoes

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gestorbatida.FolhaPontoHistoricoManage")')

    def get_query(self):
        queryset = super(RHFolhaPontoHistoricoNotificacoes, self).get_query()
        return queryset
