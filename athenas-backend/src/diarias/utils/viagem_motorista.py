from django.db import transaction
from contrib.utils import getLogger
from diarias.models import FluxoViagem


log = getLogger()


def criar_viagem_motorista(destinos, motorista_id, conta_bancaria_pgto, veiculo):
    """
    Função que cria uma nova viagem para o motorista, clonando os detalhes da viagem original (exceto o fluxo),
    cria um beneficiário associado ao motorista e clona os destinos únicos relacionados ao motorista.

    Args:
        destinos (QuerySet): Lista de destinos relacionados à viagem original.
        motorista_id (int): ID do motorista (Servidor) para o qual a viagem será criada.

    Raises:
        ValueError: Se o motorista com o ID fornecido não for encontrado.
        Exception: Caso ocorra um erro durante a criação da viagem e clonagem dos destinos.
    """

    from rh.models import Servidor, DadoBancarioPessoa
    from diarias.models import Beneficiario, Viagem
    from diarias.utils.utils import clonar_destino
    from diarias.utils.fluxo_movimentacao import benef_mover_etapa

    viagem_original = destinos[0].beneficiario.viagem

    try:
        motorista = Servidor.objects.get(id=motorista_id)
    except Servidor.DoesNotExist:
        raise ValueError(f"Motorista com ID {motorista_id} não encontrado")

    if conta_bancaria_pgto:
        try:
            conta_bancaria_pgto = DadoBancarioPessoa.objects.get(id=conta_bancaria_pgto)
        except DadoBancarioPessoa.DoesNotExist:
            raise ValueError(
                f"Conta bancária com ID {conta_bancaria_pgto} não encontrada"
            )

    fluxo_rascunho = FluxoViagem.objects.get(id=2)

    try:
        with transaction.atomic():
            nova_viagem = Viagem(
                viagem_origem=viagem_original,
                tipo_viagem=viagem_original.tipo_viagem,
                hospedagem_anfitriao=viagem_original.hospedagem_anfitriao,
                motivo_viagem=viagem_original.motivo_viagem,
                finalidade_viagem=viagem_original.finalidade_viagem,
                data_inicio_viagem=viagem_original.data_inicio_viagem,
                data_fim_viagem=viagem_original.data_fim_viagem,
                resumo=viagem_original.resumo,
                justificativa=viagem_original.justificativa,
                motorista=True,
                fluxo=fluxo_rascunho,
            )

            nova_viagem.save(ignorar_validacao=True)

            # Cria o beneficiário associado ao motorista
            beneficiario_motorista = Beneficiario.objects.create(
                servidor=motorista,
                viagem=nova_viagem,
                conta_bancaria_pgto=conta_bancaria_pgto,
            )

        destinos_clonados = []
        # Associa os destinos ao beneficiário
        for destino in destinos:
            destino_clonado = clonar_destino(destino, beneficiario_motorista)
            destinos_clonados.append(destino_clonado)

        criar_veiculos_passageiros_para_destinos(
            veiculo, destinos_clonados, beneficiario_motorista
        )

        benef_mover_etapa(beneficiario_motorista)

        return nova_viagem, beneficiario_motorista, destinos_clonados

    except Exception as e:
        log.error(e)
        raise Exception(f"Erro ao criar viagem para motorista - {e}")


def criar_veiculos_passageiros_para_destinos(veiculo, destinos, beneficiario):
    """
    Cria a relação de VeiculoPassageiro para os destinos clonados, associando o motorista.
    """
    from diarias.models import VeiculoPassageiro, HistoricoFluxoViagemBeneficiario

    fluxo_daa = FluxoViagem.objects.get(id=8)

    for destino in destinos:
        VeiculoPassageiro.objects.create(
            veiculo=veiculo, passageiro=destino, motorista=True
        )

    HistoricoFluxoViagemBeneficiario.objects.create(
        viagem=beneficiario.viagem,
        beneficiario=beneficiario,
        fluxo=fluxo_daa,
        tipo="beneficiario",
        decisao="deferido",
    )
