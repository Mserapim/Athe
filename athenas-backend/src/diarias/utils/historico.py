from contrib.utils import getLogger
from diarias.models import HistoricoFluxoViagemBeneficiario

log = getLogger(__name__)


def preparar_res(tipo, item):
    """
    Método responsável por tratar a resposta de cada registro de histórico de fluxo, seja de viagem ou beneficiário.
    """

    viagem = item if tipo == "viagem" else item.viagem

    res = {
        "historico_id": item.id,
        "viagem_data_inicio": viagem.data_inicio_viagem.strftime("%d/%m/%Y"),
        "viagem_data_fim": viagem.data_fim_viagem.strftime("%d/%m/%Y"),
        "etapa": item.fluxo.get_etapa_display(),
        "situacao": item.fluxo.get_situacao_display(),
        "ação_por": "" if tipo == "viagem" else item.acao_por,
        "data_acao": (
            "" if tipo == "viagem" else item.created_at.strftime("%d/%m/%Y %H:%M")
        ),
        "tipo_historico": tipo if tipo == "viagem" else item.get_tipo_display(),
        "decisao": "",
        "numero_empenho": "",
        "numero_nota_liquidacao": "",
        "numero_ordem_bancaria": "",
        "obs": "",
        "tem_anexo": False,
        "tem_informacao": False,
        "acomp_autoridade": False,
        "qtd_total_diarias_deferido": "",
    }

    if tipo == "historico" and item.tipo == "beneficiario":
        res["beneficiario"] = item.beneficiario.servidor.pessoa_fisica.social_name
        res["decisao"] = item.decisao
        res["numero_empenho"] = (
            item.beneficiario.numero_empenho
            if item.beneficiario.numero_empenho
            else "-"
        )
        res["numero_nota_liquidacao"] = (
            item.beneficiario.numero_nota_liquidacao
            if item.beneficiario.numero_nota_liquidacao
            else "-"
        )
        res["numero_ordem_bancaria"] = (
            item.beneficiario.numero_ordem_bancaria
            if item.beneficiario.numero_ordem_bancaria
            else "-"
        )
        res["obs"] = item.obs if item.obs else "-"
        res["tem_anexo"] = item.tem_anexo
        res["tem_informacao"] = item.tem_informacao
        res["acomp_autoridade"] = item.beneficiario.acomp_autoridade_deferimento

        if (
            hasattr(item.beneficiario, "calculos_diarias_consolidados")
            and item.beneficiario.calculos_diarias_consolidados.qtd_total_diarias_deferido
        ):
            res["qtd_total_diarias_deferido"] = (
                item.beneficiario.calculos_diarias_consolidados.qtd_total_diarias_deferido
            )

    return res


def buscar_historico_viagem(viagem):
    """
    Método responsável por buscar o histórico do fluxo de uma Viagem.
    A resposta deve ser ordenada iniciando pelo registro mais recente, e terminando com o registro mais antigo.
    E o primeiro registro deve ser a situação atual da Viagem.
    """

    q_hist = HistoricoFluxoViagemBeneficiario.objects.filter(viagem=viagem).order_by(
        "-created_at"
    )

    historico = [preparar_res("historico", hist) for hist in q_hist]
    historico.insert(0, preparar_res("viagem", viagem))

    return historico


def buscar_historico_beneficiario(beneficiario):
    """
    Método responsável por buscar o histórico do fluxo de um Beneficiário.
    A resposta deve ser ordenada iniciando pelo registro mais recente, e terminando com o registro mais antigo.
    """

    q_hist = HistoricoFluxoViagemBeneficiario.objects.filter(
        beneficiario=beneficiario
    ).order_by("-created_at")

    historico = [preparar_res("historico", hist) for hist in q_hist]

    return historico


def clonar_ultimo_historico(beneficiario):
    """
    Função para clonar o último histórico de um beneficiário.
    """
    ultimo_historico = beneficiario.historico_fluxos.latest("created_at")

    historico_clonado = HistoricoFluxoViagemBeneficiario.objects.create(
        viagem=ultimo_historico.viagem,
        beneficiario=ultimo_historico.beneficiario,
        fluxo=ultimo_historico.fluxo,
        tipo=ultimo_historico.tipo,
    )

    return historico_clonado
