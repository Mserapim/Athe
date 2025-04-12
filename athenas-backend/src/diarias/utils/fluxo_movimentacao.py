from datetime import datetime, timedelta

from django.db import transaction

from diarias.models import FluxoViagem
from standard.models import Choice

from contrib.utils import getLogger

from diarias.utils.fluxo_condicionais import (
    benef_servidor,
    fluxo_no_historico,
    mot_viagem_4_ou_5,
    benef_membro,
    benef_servidor_gsi,
    nao_etapa_no_historico,
    transp_mpmt,
    alteracao_data_itinerario,
    viagem_nao_motorista,
    viagem_possui_membro,
    indicado_repr_mpmt,
    viagem_nacional,
    viagem_estadual,
    etapa_no_historico,
    benef_externo_coe,
    etapa_anterior,
    viagem_excedente,
    resp_lotacao,
    nao_resp_lotacao,
    solic_transporte_aereo,
    solic_veiculo_inst_ao_daa,
)

from diarias.utils.calculo_diarias import CalcularConsolidarDiarias
from diarias.utils.utils import criar_historico
from diarias.utils.notificacao_mov_fluxo import (
    enviar_email_movimentacao_fluxo_beneficiario,
)

log = getLogger(__name__)


def buscar_prox_fluxo(fluxo):
    """
    Método responsável por buscar o próximo fluxo
    """

    q_fluxo = FluxoViagem.objects.filter(ordem=fluxo.ordem + 1)

    return q_fluxo.first() if q_fluxo.exists() else False


def buscar_condicional(condicional_id):
    """
    Método responsável por buscar as condicionais configuradas nos parâmetros do sistema assossiadas ao fluxo
    """

    return Choice.objects.get(
        name="CONDICIONAIS_FLUXO_DIARIAS",
        value=condicional_id,
    )


def validar_condicional(benef, condicional):
    """
    Método responsável por executar a validação assossiada à condicional configurada
    """

    conds_list = condicional.split("-")
    cond = conds_list[0]
    params = conds_list[1] if len(conds_list) > 1 else ""

    if cond == "mot_viagem_4_5":
        return mot_viagem_4_ou_5(benef.viagem)

    if cond == "benef_membro":
        return benef_membro(benef)

    if cond == "benef_serv_gsi":
        return benef_servidor_gsi(benef.viagem)

    if cond == "nao_benef_serv_gsi":
        return not benef_servidor_gsi(benef.viagem)

    if cond == "transporte_mpmt":
        return transp_mpmt(benef)

    if cond == "alt_dt_itinerario":
        return alteracao_data_itinerario(benef)

    if cond == "benef_servidor":
        return benef_servidor(benef)

    if cond == "viagem_possui_membro":
        return viagem_possui_membro(benef.viagem)

    if cond == "indicado_repr_mpmt":
        return indicado_repr_mpmt(benef.viagem)

    if cond == "viagem_nacional":
        return viagem_nacional(benef.viagem)

    if cond == "viagem_estadual":
        return viagem_estadual(benef.viagem)

    if cond == "etapa_no_historico":
        log.info(params)
        return etapa_no_historico(benef, params)

    if cond == "benef_externo_coe":
        return benef_externo_coe(benef)

    if cond == "etapa_anterior":
        return etapa_anterior(benef, params)

    if cond == "viagem_excedente":
        return viagem_excedente(benef)

    if cond == "resp_lotacao":
        return resp_lotacao(benef, params)

    if cond == "nao_resp_lotacao":
        return nao_resp_lotacao(benef, params)

    if cond == "solic_transporte_aereo":
        return solic_transporte_aereo(benef)

    if cond == "solic_veiculo_inst_ao_daa":
        return solic_veiculo_inst_ao_daa(benef)

    if cond == "viagem_nao_motorista":
        return viagem_nao_motorista(benef.viagem)

    if cond == "nao_etapa_no_historico":
        return nao_etapa_no_historico(benef, params)

    if cond == "fluxo_no_historico":
        return fluxo_no_historico(benef, params)


def validar_lista_condicionais(benef, fluxo_condicionais):
    """
    Método responsável por agrupar as condicionais do fluxo e executar a validação
    """

    conds_validas = False
    for i, conds_item in enumerate(fluxo_condicionais):
        conds_item_validas = False

        conds = conds_item.condicionais
        if ";" not in conds and "," not in conds:
            """
            Valida condicionais simples, que não tem operadores 'OU' nem 'E'
            """
            cond_choice = buscar_condicional(conds)
            if validar_condicional(benef, cond_choice.description) is True:
                conds_item_validas = True
        elif ";" in conds:
            """
            Valida condicionais com operador 'E'
            """
            cond_operador_e_valida = True
            for cond in conds.split(";"):
                if cond_operador_e_valida:
                    cond_choice = buscar_condicional(cond)
                    if validar_condicional(benef, cond_choice.description) is False:
                        cond_operador_e_valida = False
            conds_item_validas = cond_operador_e_valida
        elif "," in conds:
            """
            Valida condicionais com operador 'OU'
            """
            cond_operador_ou_valida = False
            for cond in conds.split(","):
                if cond_operador_ou_valida is False:
                    cond_choice = buscar_condicional(cond)
                    if validar_condicional(benef, cond_choice.description):
                        cond_operador_ou_valida = True
            conds_item_validas = cond_operador_ou_valida

        if i == 0:
            conds_validas = conds_item_validas
        elif conds_item.tipo_operador is not None and conds_item.tipo_operador == "E":
            conds_validas = True if conds_validas and conds_item_validas else False
        elif conds_item.tipo_operador is not None and conds_item.tipo_operador == "OU":
            conds_validas = True if conds_validas or conds_item_validas else False

    return conds_validas


def buscar_prox_fluxo_condicionado(benef):
    """
    Método responsável por buscar o próximo fluxo do beneficiário validando pelas condicionais
    """

    fluxo = buscar_prox_fluxo(benef.fluxo)
    fluxo_definido = False

    while fluxo_definido is False:
        if fluxo.condicionais.exists() is False:
            fluxo_definido = True
        else:
            if validar_lista_condicionais(benef, fluxo.condicionais.all()) is True:
                fluxo_definido = True
            else:
                fluxo_definido = False
                fluxo = buscar_prox_fluxo(fluxo)

    return fluxo


def benef_mover_etapa(benef, fluxo_especifico=None):
    """
    Método responsável por definir e salvar a Situação e a Etapa do beneficiário em relação ao fluxo de viagem.
    Caso tenha 'fluxo_especifico', o beneficiário é movido para o fluxo específico. Caso contrário, segue a lógica
    de buscar_prox_fluxo_condicionado.
    """

    if benef.fluxo.calcular:
        CalcularConsolidarDiarias(beneficiario=benef).calcular_consolidar_diarias()

    if fluxo_especifico:
        fluxo = FluxoViagem.objects.get(id=fluxo_especifico)
    else:
        fluxo = buscar_prox_fluxo_condicionado(benef)

    benef.fluxo = fluxo
    benef.save()

    criar_historico(benef)
    viagem_mover_etapa(benef.viagem)
    criar_registros_fluxos_dependentes(benef)
    enviar_email_movimentacao_fluxo_beneficiario(benef)


def viagem_mover_etapa(viagem):
    """
    Método responsável por atualizar o fluxo da Viagem.
    """

    if (
        viagem.beneficiarios.filter(fluxo_id__in=[21, 32]).count()
        == viagem.beneficiarios.count()
    ):
        """
        Se todos os beneficiários estiverem em fluxos de cancelamentos a viagem terá o fluxo definido como 'Indeferido - Cancelado'.
        Fluxos de cancelamentos:

        id: 21 - Indeferido - Cancelado
        id: 32 - Beneficiário - Cancelado
        """

        viagem.fluxo_id = 21
        viagem.save()
    elif viagem.fluxo_atual != viagem.fluxo:
        """
        Como o property 'fluxo_atual' retorna o fluxo do beneficiário que está mais atrás em relação a ordem de fluxo,
        sempre que a viagem tiver o valor do property 'fluxo_atual' diferente do valor do campo 'fluxo' a lógica irá
        atualizar o campo 'fluxo' com o valor do property 'fluxo_atual'.
        """

        viagem.fluxo = viagem.fluxo_atual
        viagem.save()


def criar_registros_fluxos_dependentes(benef):
    """
    Método responsável por criar registros automaticamente em models para fluxos específicos.
    Abaixo segue relação dos fluxos e registros que devem ser criados:

    Quando fluxo_id = 15 (DEFIN Gerência Financeira - Aguardando pagamento), criar registro para model Pagamento com status 'aguardando'.
    Quando fluxo_id = 17 (DEFIN Gerência de Tomada de Contas - Aguardando prestação de contas), criar registro para model PrestacaoContas com status 'aguardando'.
    """

    from diarias.models import Pagamento, PrestacaoContas
    from diarias.utils.notificacao_prestacao_contas import (
        envio_email_prestacao_contas_aviso,
        envio_email_prestacao_contas_colaboradores_externos,
    )

    with transaction.atomic():
        if benef.fluxo.pk == 15:
            Pagamento.objects.create(beneficiario=benef)
        elif benef.fluxo.pk == 17:

            prestacao, criado = PrestacaoContas.objects.get_or_create(
                beneficiario=benef,
                data_limite=benef.viagem.data_fim_viagem + timedelta(days=5),
            )

            if benef.servidor.type_by_possession in ["TCR", "COE"]:
                envio_email_prestacao_contas_colaboradores_externos(benef)
            else:
                envio_email_prestacao_contas_aviso(prestacao)
