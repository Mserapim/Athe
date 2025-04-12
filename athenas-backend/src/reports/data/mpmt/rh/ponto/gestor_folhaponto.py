from contrib.utils import DateUtils, getLogger
import base64
from datetime import datetime
from django.db.models.query_utils import Q
from rh.const import WORKPLACE
from rh.pvf.const import (
    STS_CANCELED_APPLICANT,
    STS_CANCELED_DGP,
    STS_REJECTED,
    STS_STAND_BY,
)
from rh.pvf.utils.folha_ponto import filtro_gestor_folha_ponto
from rh.pvf.models import SendingTimeSheet
from rh.registerpoint.models import FolhaPontoHistoricoNotificacoes
from rh.pvf.const import (
    REQUEST_ACT_SOLICITATION,
    REQUEST_ACT_DEFER,
    REQUEST_ACT_EFFECTIVENESS,
)
from rh.registerpoint.utils.ponto import inicio_fim_competencia
import json

log = getLogger(__name__)


def get_data_report(params):
    """
    Função que retorna um dicionário de dados necessários à geração do relatório
    """

    data = []

    keyword = params["data"].get("keyword")

    status_display = {
        "todos": "Todos",
        "nao_criado": "Não criado",
        "aguardando_aprovador": "Aguardando aprovador",
        "aguardando_efetivacao": "Aguardando efetivação",
        "efetivado": "Efetivado",
        "isento": "Isento de envio",
    }

    notificacao_display = {"todos_notificados": "Todos", "sim": "Sim", "nao": "Não"}

    params_filtro = {
        "mes_competencia": params["data"].get("mes_competencia"),
        "ano_competencia": params["data"].get("ano_competencia"),
        "status": params["data"].get("status"),
        "posses": params["data"].get("posses"),
        "teletrabalho": params["data"].get("teletrabalho"),
        "palavra_chave": keyword if keyword else "",
        "notificado": params["data"].get("notificado"),
    }

    filtro_tipo_posse = (
        json.loads(params_filtro["posses"]) if params_filtro["posses"] else []
    )

    filtros_display = {
        "mes_competencia": params_filtro["mes_competencia"],
        "ano_competencia": params_filtro["ano_competencia"],
        "status": status_display[params_filtro["status"]],
        "posses": (
            ",".join(filtro_tipo_posse) if len(filtro_tipo_posse) > 0 else "Todos"
        ),
        "teletrabalho": (
            "Não" if params_filtro["teletrabalho"] == "teletrabalho_nao" else "Sim"
        ),
        "palavra_chave": params_filtro["palavra_chave"],
        "notificado": notificacao_display.get(params_filtro["notificado"]),
    }

    query_servidores = filtro_gestor_folha_ponto(params_filtro)

    if keyword:
        query_servidores = text_filter(keyword, query_servidores)

    mes = params_filtro.get("mes_competencia")
    ano = params_filtro.get("ano_competencia")

    for servidor in query_servidores:
        ultimo_envio = (
            SendingTimeSheet.objects.filter(employee=servidor)
            .exclude(
                status__in=[
                    STS_CANCELED_APPLICANT,
                    STS_STAND_BY,
                    STS_CANCELED_DGP,
                    STS_REJECTED,
                ]
            )
            .last()
        )
        mes_ultimo_envio = ultimo_envio.reference_month if ultimo_envio else None
        ano_ultimo_envio = ultimo_envio.reference_year if ultimo_envio else None
        lotacao = servidor._raw_locations(active=True, option=WORKPLACE).first()

        notificacoes, total_notificacoes = get_historico_notificacoes(
            servidor, mes, ano
        )
        if params["output_format"] == "PDF":
            dados_dict = {
                "matricula": servidor.matricula,
                "nome": servidor.pessoa_fisica.social_name,
                "lotacao": str(lotacao.lotacao) if lotacao else "Sem lotação",
                "categoria_funcional": servidor.get_type_by_possession_display(),
                "situacao": "ATIVO" if servidor.ativo else "INATIVO",
                "ultimo_envio": (
                    f"{mes_ultimo_envio:02d}/{ano_ultimo_envio}" if ultimo_envio else ""
                ),
                "notificacoes": notificacoes,
            }

        if params["output_format"] in ["XLS", "CSV"]:
            dt_admissao = (
                servidor.posses_ativas.last().data_posse
                if servidor.posses_ativas.last()
                else None
            )
            chefe_imediato = ultimo_envio.get_approver_vdf_str if ultimo_envio else None

            enviado_em = ""
            aprovado_em = ""
            efetivado_em = ""

            if ultimo_envio:
                historico_vdf = ultimo_envio.portalrequesthistory_set.all()
                enviado_em = (
                    historico_vdf.filter(action=REQUEST_ACT_SOLICITATION)
                    .order_by("-date")
                    .first()
                )
                aprovado_em = (
                    historico_vdf.filter(action=REQUEST_ACT_DEFER)
                    .order_by("-date")
                    .first()
                )
                efetivado_em = (
                    historico_vdf.filter(action=REQUEST_ACT_EFFECTIVENESS)
                    .order_by("-date")
                    .first()
                )

            dt_inicio_mes, dt_fim_mes = inicio_fim_competencia(mes, ano)

            dados_dict = {
                "Matrícula": servidor.matricula,
                "nome": servidor.pessoa_fisica.social_name,
                "Lotação": str(lotacao.lotacao) if lotacao else "Sem lotação",
                "Categoria funcional": servidor.get_type_by_possession_display(),
                "Situação": "ATIVO" if servidor.ativo else "INATIVO",
                "Último envio": (
                    f"{mes_ultimo_envio:02d}/{ano_ultimo_envio}" if ultimo_envio else ""
                ),
                "aprovador": chefe_imediato if chefe_imediato else "",
                "Qtde notificações": total_notificacoes,
                "Data admissão": (
                    dt_admissao.strftime("%d/%m/%Y") if dt_admissao else ""
                ),
                "Cod do VDF": ultimo_envio.pk if ultimo_envio else "",
                "teletrabalho": "SIM" if servidor.teletrabalho_ativo() else "NÃO",
                "afastamento": servidor.afastamento_mes_str(dt_inicio_mes, dt_fim_mes),
                "Enviado em": (
                    enviado_em.date.strftime("%d/%m/%Y") if enviado_em else ""
                ),
                "Aprovado em": (
                    aprovado_em.date.strftime("%d/%m/%Y") if aprovado_em else ""
                ),
                "Efetivado em": (
                    efetivado_em.date.strftime("%d/%m/%Y") if efetivado_em else ""
                ),
            }

        data.append(dados_dict)

    with open("static/images/logo-report-mpmt.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

    values = {
        "title": params["report_name"],
        "data": data,
        "hour": datetime.now().strftime("%H:%M"),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "logo_mpmt": encoded_string.decode("utf-8"),
        "keys": [
            "Matrícula",
            "nome",
            "Lotação",
            "Categoria funcional",
            "Situação",
            "Último envio",
            "aprovador",
            "Qtde notificações",
            "Data admissão",
            "Cod do VDF",
            "teletrabalho",
            "afastamento",
            "Enviado em",
            "Aprovado em",
            "Efetivado em",
        ],
        "filtros": filtros_display,
    }
    return values


def get_historico_notificacoes(sevidor, mes, ano):
    notificacoes = []
    query_notificacoes = FolhaPontoHistoricoNotificacoes.objects.filter(
        servidor=sevidor,
        referencia_mes=mes,
        referencia_ano=ano,
    )

    for notificacao in query_notificacoes:
        notificacoes.append(
            {
                "data": DateUtils.datetime_to_str(notificacao.created_at),
                "email": notificacao.servidor.pessoa_fisica.email_institucional,
                "usuario": notificacao.created_by.username,
            }
        )
    return notificacoes, query_notificacoes.count()


def text_filter(keyword, query):
    """Realiza pesquisa com valor de keyword do Request nos campos adicionados em full_text_index.
    :param query: QuerySet a ser aplicada o filtro com keyword.
    :returns: QuerySet com filtro aplicado.
    """

    text_index = (
        "matricula__icontains",
        "pessoa_fisica__nome__icontains",
    )

    qf = None

    for index in text_index:
        q = Q(**{index: keyword})
        qf = q if qf is None else Q(qf | q)

    query = query.filter(qf)

    return query
