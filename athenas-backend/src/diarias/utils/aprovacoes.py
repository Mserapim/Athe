from datetime import datetime
from contrib.utils import getLogger
from diarias.utils.calculo_diarias import CalcularConsolidarDiarias
from rest_framework.exceptions import ValidationError
from diarias.models import (
    Beneficiario,
    CalculoConsolidado,
    Destino,
    HistoricoAnexo,
    PassagemAereaAnexo,
    PassagemAeriaViagem,
)
from diarias.utils.fluxo_movimentacao import benef_mover_etapa
from diarias.utils.historico import clonar_ultimo_historico
from ged.models import Arquivo
from diarias.utils.notificacao_deferir_indeferir import enviar_email_acao

log = getLogger()


def dar_ciencia_chefe_imediato(beneficiario_id, ciencia_chefe, chefe_imediato):
    """
    Método responsável por salvar a ciência do chefe_imediato, o chefe_imediato e criar HistoricoAnexo segundo a ação.
    """
    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    beneficiario.chefe_imediato = chefe_imediato
    beneficiario.save()

    historico = clonar_ultimo_historico(beneficiario)

    if ciencia_chefe == True:
        historico.decisao = "deferido"
        historico.save()
        benef_mover_etapa(beneficiario)
    else:
        historico.decisao = "indeferido"
        historico.save()
        benef_mover_etapa(
            beneficiario, fluxo_especifico=21
        )  # Fluxo: 'Cancelado - Indeferido'


def aprovar_beneficiario(beneficiario_id, acao_deferimento, obs, feedback):
    """
    Método responsável por salvar "obs" e criar HistoricoFluxoViagemBeneficiario segundo a ação de deferimento (deferir/indeferir).
    """
    beneficiario = Beneficiario.objects.get(id=beneficiario_id)

    historico = clonar_ultimo_historico(beneficiario)

    if obs:
        historico.obs = obs

    if feedback:
        historico.feedback = feedback

    if acao_deferimento == True:
        historico.decisao = "deferido"
        historico.save()
        benef_mover_etapa(beneficiario)
    else:
        historico.decisao = "indeferido"
        historico.save()
        benef_mover_etapa(
            beneficiario, fluxo_especifico=21
        )  # Fluxo: 'Cancelado - Indeferido'

    if beneficiario.servidor.membro:
        enviar_email_acao(beneficiario, "deferir" if acao_deferimento else "indeferir")


def analisar_diarias_beneficiario(
    beneficiario_id,
    quantidade_deferida,
    fluxo_especifico,
    obs,
    acomp_autoridade,
    feedback,
):
    """
    Método responsável por atualizar o histórico do beneficiário e a quantidade de diárias deferidas, além de realizar o cálculo consolidado
    se necessário. Este método executa as seguintes ações:

    1. Cria um novo registro de histórico para o beneficiário (HistoricoFluxoViagemBeneficiario) com a observação fornecida, se disponível.
    2. Atualiza o campo 'qtd_total_diarias_deferido' no modelo CalculoConsolidado com a nova quantidade deferida.
    3. Caso a quantidade deferida seja diferente da quantidade total de diárias, chama o método 'recalcular_diarias_deferidas' para recalcular os valores.
    4. Atualiza o campo 'acomp_autoridade_deferimento' no modelo Beneficiario.
    5. Move o beneficiário para a próxima etapa do fluxo de viagem.
    """
    from diarias.utils.calculo_diarias import CalcularConsolidarDiarias

    beneficiario = Beneficiario.objects.get(id=beneficiario_id)

    historico = clonar_ultimo_historico(beneficiario)
    if obs:
        historico.obs = obs

    if fluxo_especifico:
        historico.decisao = "encaminhado"
    else:
        historico.decisao = "deferido"

    if feedback:
        historico.feedback = feedback
    historico.save()

    if quantidade_deferida:
        calculo_consolidado = beneficiario.calculos_diarias_consolidados
        calculo_consolidado.qtd_total_diarias_deferido = quantidade_deferida
        calculo_consolidado.save()

        calcular_diarias = CalcularConsolidarDiarias(beneficiario=beneficiario)
        calcular_diarias.recalcular_diarias_deferidas(quantidade_deferida)

    if acomp_autoridade:
        beneficiario.acomp_autoridade_deferimento = True
        beneficiario.save()

    benef_mover_etapa(beneficiario, fluxo_especifico)


def adicionar_passagem_aerea(
    destino_id, empresa, aeroporto, numero_bilhete, data_hora_voo, anexos
):
    """
    Função responsável por criar um registro de PassagemAeriaViagem vinculado ao destino informado, armazena as informações da passagem,
    e associa os arquivos anexados a PassagemAereaAnexo.
    """
    import pytz

    destino = Destino.objects.get(id=destino_id)

    if isinstance(data_hora_voo, str):
        data_hora_voo = datetime.fromisoformat(data_hora_voo.replace("Z", "+00:00"))
        data_hora_voo = data_hora_voo.astimezone(pytz.UTC)

    passagem = PassagemAeriaViagem.objects.create(
        destino=destino,
        nome_companhia=empresa,
        numero_bilhete=numero_bilhete,
        aeroporto=aeroporto,
        data_hora_bilhete=data_hora_voo,
    )

    destino.data_daa = data_hora_voo
    destino.save()

    if destino.data.date() != data_hora_voo.date():
        CalcularConsolidarDiarias(
            beneficiario=destino.beneficiario
        ).calcular_consolidar_diarias()

        calculo_consolidado = destino.beneficiario.calculos_diarias_consolidados
        calculo_consolidado.reanalise = True
        calculo_consolidado.save()

    if anexos:
        for anexo_id in anexos:
            arquivo = Arquivo.objects.get(pk=anexo_id)
            PassagemAereaAnexo.objects.create(passagem=passagem, arquivo=arquivo)


def salvar_veiculos_passageiros(destinos, veiculo_data, motorista_data):
    """
    Função para salvar a relação de motoristas e/ou veículos com os destinos.
    """
    import pytz
    from diarias.models import VeiculoViagem, VeiculoPassageiro
    from diarias.utils.viagem_motorista import criar_viagem_motorista

    veiculo = None
    if veiculo_data:
        veiculo = VeiculoViagem.objects.create(
            placa=veiculo_data.get("placa"),
            marca=veiculo_data.get("marca"),
            modelo=veiculo_data.get("modelo"),
            capacidade_passageiros=veiculo_data.get("capacidade_passageiros"),
        )

    destinos_unicos = []

    for destino_info in destinos:
        ids = destino_info.get("ids", [])
        data_hora = destino_info.get("dataHora")

        for destino_id in ids:
            try:
                if isinstance(data_hora, str):
                    data_hora = datetime.fromisoformat(data_hora.replace("Z", "+00:00"))
                    data_hora = data_hora.astimezone(pytz.UTC)

                destino = Destino.objects.get(id=destino_id)
                destino.data_daa = data_hora
                destino.save()

                if destino.data.date() != destino.data_daa.date():
                    CalcularConsolidarDiarias(
                        beneficiario=destino.beneficiario
                    ).calcular_consolidar_diarias()

                    calculo_consolidado = (
                        destino.beneficiario.calculos_diarias_consolidados
                    )
                    calculo_consolidado.reanalise = True
                    calculo_consolidado.save()

                VeiculoPassageiro.objects.create(
                    veiculo=veiculo, passageiro=destino, motorista=False
                )

                verificar_destinos_e_mover_fluxo(destino_id)

            except Destino.DoesNotExist:
                raise ValidationError(
                    {"error": f"Destino com ID {destino_id} não encontrado."}
                )

        if ids:
            destinos_unicos.append(Destino.objects.get(id=ids[0]))

    motorista_id = motorista_data.get("motorista")
    conta_bancaria_pgto = motorista_data.get("conta_bancaria_pgto")

    if motorista_id:
        criar_viagem_motorista(
            destinos_unicos, motorista_id, conta_bancaria_pgto, veiculo
        )


def verificar_destinos_e_mover_fluxo(destino_id):
    """
    Verifica se todos os destinos de um beneficiário têm 'analise_daa = True'.
    Se todos tiverem, move o beneficiário para o próximo fluxo.
    """

    destino = Destino.objects.get(id=destino_id)
    beneficiario = destino.beneficiario

    destinos_filtrados = beneficiario.destinos.filter(
        forma_deslocamento__in=["1", "2"]
    )  # Avião ou Veículo institucional
    destinos_analise_daa = all(destino.analise_daa for destino in destinos_filtrados)

    if destinos_analise_daa:
        historico = clonar_ultimo_historico(beneficiario)
        historico.decisao = "deferido"
        historico.save()

        benef_mover_etapa(beneficiario)


def aprovar_defin_excedente(
    beneficiario_id, gedoc, quantidade_deferida, acao_deferimento, anexos
):
    """
    Método responsável por atualizar o histórico do beneficiário e a quantidade de diárias deferidas, além de realizar o cálculo consolidado
    se necessário. Este método executa as seguintes ações:

    1. Cria um novo registro de histórico para o beneficiário (HistoricoFluxoViagemBeneficiario) com a ação de deferimento fornecida.
    2. Salva os anexos em HistoricoAnexo.
    3. Atualiza o campo 'qtd_total_diarias_deferido' no modelo CalculoConsolidado com a nova quantidade deferida.
    4. Caso a quantidade deferida seja diferente da quantidade total de diárias, chama o método 'recalcular_diarias_deferidas' para recalcular os valores.
    5. Atualiza o campo 'gedoc_numero' no modelo Beneficiario.
    6. Move o beneficiário para a próxima etapa do fluxo de viagem.
    """
    from diarias.utils.calculo_diarias import CalcularConsolidarDiarias

    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    historico = clonar_ultimo_historico(beneficiario)

    if anexos:
        for anexo_id in anexos:
            arquivo = Arquivo.objects.get(pk=anexo_id)
            anexo, _ = HistoricoAnexo.objects.get_or_create(
                historico=historico, arquivo=arquivo
            )

    if quantidade_deferida:
        calculo_consolidado = beneficiario.calculos_diarias_consolidados
        calculo_consolidado.qtd_total_diarias_deferido = quantidade_deferida
        calculo_consolidado.save()

        calcular_diarias = CalcularConsolidarDiarias(beneficiario=beneficiario)
        calcular_diarias.recalcular_diarias_deferidas(quantidade_deferida)

    beneficiario.gedoc_numero = gedoc
    beneficiario.save()

    if acao_deferimento == True:
        historico.decisao = "deferido"
        historico.save()
        benef_mover_etapa(beneficiario)
    else:
        historico.decisao = "indeferido"
        historico.save()
        benef_mover_etapa(
            beneficiario, fluxo_especifico=21
        )  # Fluxo: 'Cancelado - Indeferido'


def atualizar_valor_deferido_diarias(beneficiario_id, valor_deferido):
    """
    Método responsável por salvar valor_total_liquido_deferido em CalculoConsolidado e criar ação em histórico.
    """
    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    historico = clonar_ultimo_historico(beneficiario)

    calculo_consolidado = beneficiario.calculos_diarias_consolidados
    calculo_consolidado.valor_total_liquido_deferido = valor_deferido
    calculo_consolidado.save()

    historico.decisao = "valor_alterado"
    historico.save()


def dar_ciencia_cancelamento(beneficiario_id):
    """
    Método responsável por salvar a ciência de cancelamento do DAA e DEPLAN.
    """
    beneficiario = Beneficiario.objects.get(id=beneficiario_id)

    historico = clonar_ultimo_historico(beneficiario)
    historico.decisao = "ciente"

    historico.save()

    benef_mover_etapa(beneficiario)


def mover_fluxo_especifico(beneficiarios, fluxo_especifico, obs):
    """
    Método responsável mover Beneficiários para um fluxo.
    """

    for beneficiario_id in beneficiarios:
        beneficiario = Beneficiario.objects.get(id=beneficiario_id)
        historico = clonar_ultimo_historico(beneficiario)

        if obs:
            historico.obs = obs

        historico.decisao = "encaminhado"
        historico.save()
        benef_mover_etapa(beneficiario, fluxo_especifico=fluxo_especifico)


def receber_beneficarios(viagem_id):
    """
    Método responsável por receber os benefiários de uma viagem para nota de liquidação ou ordem bancária.
    """
    from diarias.models import Viagem

    viagem = Viagem.objects.get(id=viagem_id)

    beneficiarios = viagem.beneficiarios.all()

    for beneficiario in beneficiarios:
        historico = clonar_ultimo_historico(beneficiario)
        historico.decisao = "recebido"
        historico.save()

        benef_mover_etapa(beneficiario)


def adicionar_nota_liquidacao(beneficiario_id, numero_nota_liquidacao, anexos):
    """
    Método responsável por salvar nota de liquidação segundo análise do Defin.
    """

    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    beneficiario.numero_nota_liquidacao = numero_nota_liquidacao
    beneficiario.save()

    historico = clonar_ultimo_historico(beneficiario)
    historico.decisao = "deferido"
    historico.save()

    if anexos:
        for anexo_id in anexos:
            arquivo = Arquivo.objects.get(pk=anexo_id)
            HistoricoAnexo.objects.create(historico=historico, arquivo=arquivo)

    benef_mover_etapa(beneficiario)


def analise_ordem_bancaria(
    beneficiario_id, numero_ordem_bancaria, anexos, data_pagamento
):
    """
    Método responsável por salvar numero_ordem_bancaria de Beneficiario e criar HistoricoAnexo segundo análise do Defin.
    """

    from diarias.models import Pagamento

    fluxo_aguardando_pagamento = 15

    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    beneficiario.numero_ordem_bancaria = numero_ordem_bancaria
    beneficiario.save()

    historico = clonar_ultimo_historico(beneficiario)
    historico.decisao = "deferido"
    historico.save()
    if anexos:
        for anexo_id in anexos:
            arquivo = Arquivo.objects.get(pk=anexo_id)
            HistoricoAnexo.objects.create(historico=historico, arquivo=arquivo)

    if data_pagamento:
        benef_mover_etapa(beneficiario, fluxo_especifico=fluxo_aguardando_pagamento)

        pagamento = (
            Pagamento.objects.filter(beneficiario=beneficiario).order_by("-id").first()
        )
        pagamento.status = "cnab_criado"
        pagamento.data_pgto = data_pagamento
        pagamento.save()

    else:
        benef_mover_etapa(beneficiario)


def analise_empenho(beneficiario_id, numero_empenho, anexos, empenho_liberado):
    """
    Métoddo responsável por salvar numero_empenhode Beneficiario e criar HistoricoAnexo segundo análise do Deplan
    e por liberar empenho segundo análise do DG.
    """

    beneficiario = Beneficiario.objects.get(id=beneficiario_id)
    historico = clonar_ultimo_historico(beneficiario)

    if anexos:
        for anexo_id in anexos:
            arquivo = Arquivo.objects.get(pk=anexo_id)
            HistoricoAnexo.objects.create(historico=historico, arquivo=arquivo)

    if empenho_liberado:
        historico.decisao = "liberado"
        historico.save()

        benef_mover_etapa(beneficiario)

    elif numero_empenho:
        beneficiario.numero_empenho = numero_empenho
        beneficiario.save()

        historico.decisao = "deferido"
        historico.save()

        benef_mover_etapa(beneficiario)
