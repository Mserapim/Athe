from standard.models import Choice
from rh.models import Lotacao
from diarias.models import FluxoViagem, HistoricoFluxoViagemBeneficiario


def mot_viagem_4_ou_5(viagem):
    """
    Método responsável por validar se o motivo da viagem tem o id com o valor 4 ou 5.
    O motivo da viagem utiliza a variável MOTIVO_VIAGEM dos parâmetros do sistema.

    4 - Cap Art 1 §7 Inci. I - Ato Adm. n° 1.122/2022-PGJ
    5 - Pos Grad. Art.1 §7 In.II Ato Adm. n°1.122/2022-PGJ

    O método deve receber um objeto do model Viagem e deve retornar um booleano, sendo True caso o
    motivo da viagem for um dos dois valores citados acima.
    """

    return True if viagem.motivo_viagem in [4, 5] else False


def benef_membro(benef):
    """
    Método responsável por validar se o beneficiário é do tipo 'Membro'.

    O método deve receber um objeto do model Beneficiario e retornar um booleano, sendo True caso o beneficiário
    seja do tipo Membro.
    """

    return True if benef.servidor.tipo == "M" else False


def benef_servidor_gsi(viagem):
    """
    Método responsável por validar se a viagem possui algum beneficiário que seja do tipo 'Servidor'
    e esteja na lotação GSI - GABINETE DE SEG. INSTITUCIONAL
    """

    lotacao_gsi = Lotacao.objects.get(nome="GABINETE DE SEG. INSTITUCIONAL")
    incluido = False

    for benef in viagem.beneficiarios.all():
        if benef.servidor.work_assignment.filter(lotacao=lotacao_gsi).exists():
            incluido = True

    return incluido


def transp_mpmt(benef):
    """
    Método responsável por validar se a viagem está sendo custeada pelo MPMT
    """

    if (
        benef.destinos.count() > 0
        and benef.destinos.filter(
            forma_deslocamento__in=["1", "2"]
        ).exists()  # se forma de deslocamento for '1 - Avião' ou '2 - Veículo institucional'
    ):
        return True
    else:
        return False


def alteracao_data_itinerario(benef):
    """
    Método responsável por validar se houve alteração nas datas do itinerário de destino de um Beneficiário
    """
    if benef.calculos_diarias_consolidados:
        return benef.calculos_diarias_consolidados.reanalise
    return False


def benef_servidor(benef):
    """
    Método responsável por validar se o beneficiário é 'Servidor'.

    O método deve receber um objeto do model Beneficiario e retornar um booleano, sendo True caso o beneficiário
    seja Servidor.
    """

    types = ["EFE", "ECM", "CMS", "REQ", "RCM", "EFC", "REX", "EXT"]
    return True if benef.servidor.type_by_possession in types else False


def viagem_comitiva(viagem):
    """
    Método responsável por validar se a viagem é em comitiva, ou seja, e há mais de um beneficiário na viagem
    e que tenha pelo menos um membro.

    # TODO - desenvolver a lógica
    """

    return True


def indicado_repr_mpmt(viagem):
    """
    Método responsável por validar se a viagem tem o beneficiário como representante do MPMT.

    É necessário comparar com o parâmetro de sistema FINALIDADE_VIAGEM com o valor do campo 'valor (int)'
    sendo '13' - Representar.
    """

    return True if viagem.finalidade_viagem == 13 else False


def viagem_nacional(viagem):
    """
    Método responsável por validar se a viagem é nacional.

    Valida se o campo 'tipo_viagem' do objeto Viagem tem o valor 'NACIONAL' ou 'INTERNACIONAL'.
    """

    return True if viagem.tipo_viagem in ["NACIONAL", "INTERNACIONAL"] else False


def viagem_estadual(viagem):
    """
    Método responsável por validar se a viagem é estadual.

    Valida se o campo 'tipo_viagem' do objeto Viagem tem o valor 'ESTADUAL'.
    """

    return True if viagem.tipo_viagem in ["ESTADUAL"] else False


def resp_lotacao(benef, lotacoes_ids):
    """
    Método responsável por validar se o beneficiário é responsável em alguma das lotações passadas no parâmetro.

    A lógica irá verificar se o Beneficiário é responsável em uma das lotações passadas pelo parâmetros 'lotacoes_ids'
    """

    return (
        True
        if benef.servidor.responsavel_por.filter(pk__in=lotacoes_ids.split(","))
        else False
    )


def nao_resp_lotacao(benef, lotacoes_ids):
    """
    Método responsável por validar que o beneficiário não pode ser responsável em alguma das lotações passadas no parâmetro.

    A lógica irá verificar se o Beneficiário é responsável em uma das lotações passadas pelo parâmetros 'lotacoes_ids'.
    Se for responsável irá retornar False
    """

    return (
        False
        if benef.servidor.responsavel_por.filter(pk__in=lotacoes_ids.split(","))
        else True
    )


def benef_externo_coe(benef):
    """
    Método responsável por validar se o beneficiário é externo ou COE.

    O método deve receber um objeto do model Beneficiario e retornar um booleano, sendo True caso o beneficiário
    seja 'Colaborador Eventual' ou 'Colaborador Externo'.
    """

    types = ["COE", "TCR"]
    return True if benef.servidor.type_by_possession in types else False


def viagem_excedente(benef):
    """
    Método responsável por validar se a viagem é de beneficiário com quantidade excedente.
    """

    return True if benef.viagem.excedente else False


def viagem_possui_membro(viagem):
    """
    Método responsável por validar se a viagem possui membro entre os beneficiários.

    O método deve receber um objeto do model Viagem e retornar um booleano, sendo True caso tenha algum
    Servidor do tipo Membro.
    """

    possui_membro = False
    for benef in viagem.beneficiarios.all():
        if benef.servidor.tipo == "M":
            possui_membro = True

    return possui_membro


def etapa_no_historico(benef, etapa_historico):
    """
    Método responsável por validar se no histórico do beneficiário possui a etapa passada no parâmetro.
    """

    # buscando etapa através do parâmetro 'etapa_historico'
    etapa = Choice.objects.get(
        name="ETAPA_SOLICITACAO_VIAGEM", description=etapa_historico
    ).value

    aguardando_analise = 14  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'
    aguardando_ciencia = 22  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'
    aguardando_reanalise = 23  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'

    fluxos = FluxoViagem.objects.filter(
        etapa=etapa,
        situacao__in=[aguardando_analise, aguardando_ciencia, aguardando_reanalise],
    )

    for fluxo in fluxos:
        if HistoricoFluxoViagemBeneficiario.objects.filter(
            beneficiario=benef,
            fluxo=fluxo,
        ).exists():
            return True


def etapa_anterior(benef, fluxo_anterior_ids):
    """
    Método responsável por validar se a etapa anterior é a etapa passada no parâmetro.

    A lógica irá utilizar para comparação o fluxo atual do Beneficiário como se fosse a etapa anterior,
    já que o Beneficiário ainda não entrou na etapa que está sendo validada.
    """

    return True if benef.fluxo.pk in map(int, fluxo_anterior_ids.split(",")) else False


def fluxo_no_historico(benef, fluxo_ids):
    """
    Método responsável por verificar se algum dos fluxos especificados está presente no histórico do beneficiário.
    """
    fluxos = [int(id.strip()) for id in fluxo_ids.split(",")]

    existe_fluxo = HistoricoFluxoViagemBeneficiario.objects.filter(
        beneficiario=benef, fluxo_id__in=fluxos
    ).exists()

    return existe_fluxo


def solic_transporte_aereo(benef):
    """
    Método responsável por validar se o beneficiário solicitou trasporte aéreo.
    """

    # se forma de deslocamento for '1 - Avião'
    if (
        benef.destinos.count() > 0
        and benef.destinos.filter(forma_deslocamento="1").exists()
    ):
        return True
    else:
        return False


def solic_veiculo_inst_ao_daa(benef):
    """
    Método responsável por validar se o beneficiário solicitou veículo institucional ao DAA.
    """

    # se forma de deslocamento for '2 - Veículo institucional'
    # E (com_motorista OU veiculo_daa)
    if (
        benef.destinos.count() > 0
        and benef.destinos.filter(forma_deslocamento="2").exists()
        and (
            benef.destinos.filter(com_motorista=True).exists()
            or benef.destinos.filter(veiculo_daa=True).exists()
        )
    ):
        return True
    else:
        return False


def membro_solicitou_veiculo_daa(benef):
    """
    Método responsável por validar se o beneficiário é Membro e solicitou veículo institucional ao DAA.
    """

    return (
        True
        if (benef_servidor(benef) is False and solic_veiculo_inst_ao_daa(benef))
        else False
    )


def benef_acomp_autoridade(benef):
    """
    Método responsável por validar se o beneficiário está acompanhando autoridade.

    A lógica verifica se a Finalidade da Viagem, id do campo 'finalidade_viagem', está com uma das opções abaixo:
    78 - Acompanhamento Corregedor Geral de Justica ou representantes  -- 71
    79 - Acompanhamento Corregedor Corregedor-Geral Adjunto ou representantes -- 72
    80 - Acompanhamento ao Procurador Geral de Justica ou representantes -- 73
    """

    return True if benef.viagem.finalidade_viagem in [71, 72, 73] else False


def viagem_nao_motorista(viagem):
    """
    Método responsável por validar se a viagem é de motorista.

    O método deve receber um objeto do model Viagem e deve retornar um booleano,
    sendo True caso o campo motorista seja False (ou seja, não é uma viagem de motorista).
    """

    return not viagem.motorista


def nao_etapa_no_historico(benef, etapa_historico):
    """
    Método responsável por validar se no histórico do beneficiário não possui a etapa passada no parâmetro.
    """

    etapa = Choice.objects.get(
        name="ETAPA_SOLICITACAO_VIAGEM", description=etapa_historico
    ).value

    aguardando_analise = 14  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'
    aguardando_ciencia = 22  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'
    aguardando_analise_daa = 4  # ID do Choice 'SITUACAO_SOLICITACAO_VIAGEM'

    fluxo = FluxoViagem.objects.filter(
        etapa=etapa,
        situacao__in=[aguardando_analise, aguardando_ciencia, aguardando_analise_daa],
    ).first()

    return not HistoricoFluxoViagemBeneficiario.objects.filter(
        beneficiario=benef,
        fluxo=fluxo,
    ).exists()
