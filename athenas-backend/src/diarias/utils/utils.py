import re
from datetime import datetime, date

from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.core.exceptions import ValidationError
from contrib.utils import getLogger
from standard.models import Choice, Item
from adm.cnab_gerador.cnab_240.bb_cnab_240_gerar_pgto import BBCnab240GerarPgto

log = getLogger()


def buscar_tipo_solicitante_viagem(solicitante):
    """
    Método responsável por definir o TIpo de Solicitante de uma Viagem.
    As condicionais devem respeitar uma ordem de validação. Cada validação deverá ter a documentação das regras de negócio.
    As definições do Tipo de Solicitante estão vinculadas com o Choice 'TIPO_SOLICITANTE'.
    A comparação é feita com o campo 'cvlaue' e a definição com o campo 'value'. Não será validado os 'cvalue' dos tipos 3 e 9, que será
    utilizado apenas como histórico dos registros importados do antigo sistema SISDIAS.
    """

    q_choice = Choice.objects.filter(app_label="diarias", name="TIPO_SOLICITANTE")

    # 1° condicional - tipo 1:
    # Se o solicitante for Membro e estiver com provimento ativo no cargo 'código: 00084 - PROCURADOR - GERAL DE JUSTICA-MPMT'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '1' - Procurador Geral de Justiça
    if (
        solicitante.tipo == "M"
        and solicitante.work_assignment.filter(
            movimentacao_posse__quadro__cargo__codigo="00084"
        ).exists()
    ):
        return q_choice.filter(cvalue="1").first().value

    # 2° condicional - tipo 2:
    # Se o solicitante for Membro e estiver com provimento ativo como responsável da lotação 'SECRETÁRIO-GERAL DO MINISTÉRIO PÚBLICO, id: 52748'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '2' - Secretário-Geral de Gabinete
    if (
        solicitante.tipo == "M"
        and solicitante.work_assignment.filter(
            lotacao__pk=52748, responsible=True
        ).exists()
    ):
        return q_choice.filter(cvalue="2").first().value

    # 3° condicional - tipo 4:
    # Se o solicitante estiver com provimento ativo no cargo 'código: 00025 - DIRETOR - GERAL-MPMT'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '4' - Diretor Geral
    if solicitante.work_assignment.filter(
        movimentacao_posse__quadro__cargo__codigo="00025"
    ).exists():
        return q_choice.filter(cvalue="4").first().value

    # 4° condicional - tipo 6:
    # Se o solicitante for Servidor
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '6' - Servidor do Ministério Público
    if solicitante.tipo != "M":
        return q_choice.filter(cvalue="6").first().value

    # 5° condicional - tipo 7:
    # Se o solicitante for Membro e estiver com provimento ativo como responsável da lotação 'SUBPROCURADORIA-GERAL DE JUSTIÇA JURÍDICA E INSTITUCIONAL, id: 52344'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '7' - SubProcurador Geral de Justiça Júridico e Institucional
    if (
        solicitante.tipo == "M"
        and solicitante.work_assignment.filter(
            lotacao__pk=52344, responsible=True
        ).exists()
    ):
        return q_choice.filter(cvalue="7").first().value

    # 6° condicional - tipo 8:
    # Se o solicitante for Membro e estiver com provimento ativo como responsável da lotação 'SUBPROCURADORIA-GERAL DE JUSTIÇA ADMINISTRATIVA, id: 52645'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '8' - Subprocurador-Geral de Justiça Administrativo
    if (
        solicitante.tipo == "M"
        and solicitante.work_assignment.filter(
            lotacao__pk=52645, responsible=True
        ).exists()
    ):
        return q_choice.filter(cvalue="8").first().value

    # 7° condicional - tipo 10:
    # Se o solicitante for Membro e estiver com provimento ativo como responsável da lotação 'SUBPGJ PLAN - SUBPROCURADORIA-GERAL DE JUSTIÇA DE PLANEJAMENTO E GESTÃO, id: 53012'
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '10' - Subprocurador-Geral de Justiça Planejamento
    if (
        solicitante.tipo == "M"
        and solicitante.work_assignment.filter(
            lotacao__pk=53012, responsible=True
        ).exists()
    ):
        return q_choice.filter(cvalue="10").first().value

    # 8° condicional - tipo 5:
    # Se o solicitante for Membro
    # Retorna o campo 'value' do Choice de TIPO_SOLICITANTE com o parâmetro cvalue '5' - Membro do Ministério Público
    if solicitante.tipo == "M":
        return q_choice.filter(cvalue="5").first().value


def buscar_proximo_cod_os_beneficiario():
    """
    Método responsável por definir qual será o próximo código de OS (Ordem de Serviço) para uma Viagem.

    Definição: é o próximo número a partir do número máximo cadastrado dentro do ano vigente. Se não houver
    código no ano vigente, deve-se gerar o código 1 (um) para este ano.

    Ex.:
    1 - Se no ano vigente de 2024 a query encontrar o número máximo sendo 1096, o código a ser retornado deve ser o 1097.
    2 - Se no ano vigente de 2025 a query não encontrar nenhum número, o código deve ser 1.

    Obs.:
    O módulo de Diárias desenvolvido no Athenas tem dados importados do SISDIAS - MPMT, e já há uma sequência ativa de códigos
    de OS de Viagem. Para dar continuidade na sequência foi criado uma configuração inicial no Athenas.
    Caso a lógica não encotrar nenhum código sem referência de ano, o código a ser retornado deverá ser o que está na configuração inicial.
    """

    from diarias.models import Beneficiario

    q_benef = Beneficiario.objects.filter()
    q_item = Item.objects.filter(
        configuration__application="diarias", key="codigo_os_inicial"
    )

    codigo_max = q_benef.aggregate(Max("codigo"))["codigo__max"]
    if codigo_max is None:
        item = q_item.first()
        prox_codigo = int(item.value) + 1
    else:
        q_benef = q_benef.filter(created_at__year=datetime.today().year)
        codigo_max = q_benef.aggregate(Max("codigo"))["codigo__max"]
        if codigo_max is None:
            prox_codigo = 1
        else:
            prox_codigo = int(codigo_max) + 1

    return prox_codigo


def buscar_fluxo_viagem_beneficiario(instancia):
    """
    Método responsável por retornar informações de Fluxo, Viagem e Beneficuiário dependendo
    da instância recebida, sendo 'viagem' ou 'beneficiario'.
    """

    if instancia._meta.model_name == "viagem":
        return [instancia.fluxo_atual, instancia, None]

    if instancia._meta.model_name == "beneficiario":
        return [instancia.fluxo, instancia.viagem, instancia]


def criar_historico(instancia):
    """
    Método responsável por criar o histórico de fluxo, de uma Viagem ou de um Benefeciário.
    """

    from diarias.models import HistoricoFluxoViagemBeneficiario

    fluxo, viagem, beneficiario = buscar_fluxo_viagem_beneficiario(instancia)

    hist = HistoricoFluxoViagemBeneficiario(
        viagem=viagem,
        fluxo=fluxo,
        tipo=instancia._meta.model_name,
    )

    if instancia._meta.model_name == "beneficiario":
        hist.beneficiario = beneficiario

    hist.save()


def clonar_destino(destino_original, novo_beneficiario):
    """
    Função usada para clonar um destino
    """

    from diarias.models import Destino

    try:
        with transaction.atomic():  # Garantir transação atômica para consistência do banco de dados
            # Criar uma nova instância de Destino com os mesmos dados do original, mas com o novo beneficiário

            eventos = novo_beneficiario.eventos.filter(
                titulo=destino_original.evento.titulo,
                data_inicio=destino_original.evento.data_inicio,
                data_fim=destino_original.evento.data_fim,
            )

            if eventos.exists():
                evento = eventos.first()
            else:
                evento = clonar_evento(destino_original.evento, novo_beneficiario)

            novo_destino = Destino(
                beneficiario=novo_beneficiario,
                municipio_origem=destino_original.municipio_origem,
                municipio_destino=destino_original.municipio_destino,
                forma_deslocamento=destino_original.forma_deslocamento,
                pref_turno_ida=destino_original.pref_turno_ida,
                data=destino_original.data,
                distancia_m=destino_original.distancia_m,
                distancia_km=destino_original.distancia_km,
                com_motorista=destino_original.com_motorista,
                veiculo_daa=destino_original.veiculo_daa,
                data_daa=destino_original.data_daa,
            )
            novo_destino.save()
            evento.destinos.add(novo_destino)
    except Exception as e:
        log.info(e)
        raise f"Erro ao clonar Destino - {e}"

    return novo_destino


def clonar_evento(evento_original, novo_beneficiario):
    """
    Função usada para clonar um evento
    """

    from diarias.models import EventoBeneficiario

    try:
        with transaction.atomic():  # Garantir transação atômica para consistência do banco de dados
            # Criar uma nova instância de Evento com os mesmos dados do original, mas com o novo beneficiário
            novo_evento, created = EventoBeneficiario.objects.get_or_create(
                beneficiario=novo_beneficiario,
                titulo=evento_original.titulo,
                data_inicio=evento_original.data_inicio,
                data_fim=evento_original.data_fim,
            )
    except Exception as e:
        log.info(e)
        raise f"Erro ao clonar Evento - {e}"

    return novo_evento


def clonar_viagem(viagem):

    from diarias.models import Viagem, ViagemAnexo

    with transaction.atomic():
        nova_viagem = Viagem.objects.create(
            viagem_origem=viagem,
            excedente=True,
            tipo_viagem=viagem.tipo_viagem,
            hospedagem_anfitriao=viagem.hospedagem_anfitriao,
            motivo_viagem=viagem.motivo_viagem,
            finalidade_viagem=viagem.finalidade_viagem,
            data_inicio_viagem=viagem.data_inicio_viagem,
            data_fim_viagem=viagem.data_fim_viagem,
            resumo=viagem.resumo,
            justificativa=viagem.justificativa,
            tipo_solicitante=viagem.tipo_solicitante,
        )

        for anexo in viagem.anexos_viagem.all():
            ViagemAnexo.objects.create(viagem=nova_viagem, arquivo=anexo.arquivo)
    return nova_viagem


def clonar_beneficiario(beneficiario, nova_viagem):
    from diarias.models import Beneficiario

    novo_beneficiario = Beneficiario.objects.create(
        servidor=beneficiario.servidor,
        viagem=nova_viagem,
        conta_bancaria_pgto=beneficiario.conta_bancaria_pgto,
        cargo=beneficiario.cargo,
    )
    return novo_beneficiario


def consolidar_infos_beneficiario_cnab(beneficiario):

    if (
        beneficiario.conta_bancaria_pgto.agencia_numero
        and beneficiario.conta_bancaria_pgto.conta_numero
    ):

        agencia_num = beneficiario.conta_bancaria_pgto.agencia_numero
        agencia_dv = beneficiario.conta_bancaria_pgto.agencia_dv

        conta_num = beneficiario.conta_bancaria_pgto.conta_numero
        conta_dv = beneficiario.conta_bancaria_pgto.conta_dv

        if agencia_dv is None or agencia_dv == "" or agencia_dv == "None":
            agencia_dv = "0"

        if conta_dv is None or conta_dv == "" or conta_dv == "None":
            conta_dv = "0"

    else:

        agencia = re.sub(r"(\.|-)", "", beneficiario.conta_bancaria_pgto.agencia)
        agencia_num = agencia[0:-1]
        agencia_dv = agencia[-1].upper()

        conta_completa = re.sub(
            r"(\.|-)", "", beneficiario.conta_bancaria_pgto.conta_corrente_completa
        )
        conta_num = conta_completa[0:-1]
        conta_dv = (
            "0"
            if beneficiario.conta_bancaria_pgto.tipo_conta == "2"
            else conta_completa[-1].upper()
        )
        if agencia_dv.upper() == "E":
            agencia_dv = "0"

        if conta_dv.upper() == "E":
            conta_dv = "0"

    return {
        "doc": beneficiario.servidor.pessoa_fisica.cpf,
        "tipo_doc": "1",  # tipo de inscrição - CPF = '1
        "nome": beneficiario.servidor.pessoa_fisica.social_name,
        "cod_banco": beneficiario.conta_bancaria_pgto.banco.numero,
        "agencia_num": agencia_num,
        "agencia_dv": agencia_dv,
        "conta_num": conta_num,
        "conta_dv": conta_dv,
        "tipo_conta": beneficiario.conta_bancaria_pgto.tipo_conta,
        "valor_pgto": beneficiario.calculos_diarias_consolidados.valor_total_liquido_deferido,
    }


def gerar_cnab_pgto(pgto_ids, data_pgto):
    """
    Método responsável por:
    - consolidar as informações para geração de arquivo CNAB.
    - gerar o arquivo CNAB, gravar na tabela CnabPagamento e vincular aos registros de Pagamento.
    - alterar o status dos registros de pagamentos para o status 'cnab_criado'.
    """

    from diarias.models import Pagamento, CnabPagamento

    arquivo_cnab_pgto = None
    q_pgtos = Pagamento.objects.exclude(status="pago").filter(pk__in=pgto_ids)

    pgtos_bb = q_pgtos.filter(beneficiario__conta_bancaria_pgto__banco__numero="001")
    favorecidos_bb = [
        consolidar_infos_beneficiario_cnab(pgto.beneficiario) for pgto in pgtos_bb
    ]

    pgtos_outros = q_pgtos.exclude(
        beneficiario__conta_bancaria_pgto__banco__numero="001"
    )
    favorecidos_outros = [
        consolidar_infos_beneficiario_cnab(pgto.beneficiario) for pgto in pgtos_outros
    ]

    with transaction.atomic():
        arquivo_cnab = BBCnab240GerarPgto(
            tipo_servico="pgtos_diversos"
        ).criar_cnab_pgto_bb_outros_bancos(
            favorecidos_bb=favorecidos_bb,
            favorecidos_outros=favorecidos_outros,
            data_pgto=data_pgto,
        )

        arquivo_cnab_pgto = CnabPagamento.objects.create(cnab=arquivo_cnab)
        q_pgtos.update(
            cnab=arquivo_cnab_pgto,
            status="cnab_criado",
            data_pgto=data_pgto,
        )

    return arquivo_cnab_pgto


def assinar_pgto(pgto_ids, usuario):
    """
    Assina os pagamentos com os IDs fornecidos, atribuindo a pessoa e a data de assinatura.
    """

    from diarias.models import Pagamento

    pessoa = usuario.servidor.pessoa_fisica
    assinado_em = timezone.now()

    with transaction.atomic():
        Pagamento.objects.filter(pk__in=pgto_ids).update(
            assinado_por=pessoa, assinado_em=assinado_em
        )


def buscar_descricao_condicional(cond_id):
    """
    Método responsável por buscar a descrição de uma condicional.
    """

    choice = Choice.objects.get(
        app_label="diarias", name="CONDICIONAIS_FLUXO_DIARIAS", value=cond_id
    )

    return choice.label


def buscar_beneficiarios_servidor_mes(servidor, mes, ano):
    return servidor.diarias_viagens.filter(
        viagem__data_inicio_viagem__month=mes, viagem__data_inicio_viagem__year=ano
    )


def buscar_beneficiarios_servidor_ano(servidor, ano):
    return servidor.diarias_viagens.filter(viagem__data_inicio_viagem__year=ano)


def buscar_beneficiarios_servidor_mes_motivos(servidor, mes, ano, motivos):
    return buscar_beneficiarios_servidor_mes(servidor, mes, ano).filter(
        viagem__motivo_viagem__in=motivos
    )


def buscar_beneficiarios_servidor_ano_motivos(servidor, ano, motivos):
    return buscar_beneficiarios_servidor_ano(servidor, ano).filter(
        viagem__motivo_viagem__in=motivos
    )


def notificar_solititante_config_fluxo(beneficiario, destinatarios):
    """
    Função que recebe um beneficiario e um lista de destinararios,
    ela pega o fluxo atual do beneficiario e confere a se a flag notificar_solicitante
    está marcada como True, então busca o solicitante da viagem e adiona ele na lista de
    destinatarios e devolve a lista de destinatarios atualizada.
    """

    if beneficiario.fluxo.notificar_solicitante:
        solicitante = beneficiario.viagem.solicitante_servidor

        solicitante_nome = (
            solicitante.pessoa_fisica.social_name or solicitante.pessoa_fisica.nome
        )
        solicitante_email = (
            solicitante.pessoa_fisica.email_institucional
            if solicitante.pessoa_fisica.email_institucional
            else solicitante.pessoa_fisica.email_pessoal
        )

        destinatarios.append(
            {
                "nome": f"{solicitante_nome} (Solicitante)",
                "email": f"{solicitante_email}",
            }
        )

    return destinatarios


def notificar_aprovadores_fluxo(beneficiario, destinatarios):
    """
    Função que recebe um beneficiario e um lista de destinararios,
    ela pega o fluxo atual do beneficiario e busca os grupos de aprovadores,
    então busca os aprovadores da etapa atual da viagem e adiona eles na lista de
    destinatarios e devolve a lista de destinatarios atualizada.
    """

    from diarias.models import GrupoAprovador

    etapa = beneficiario.fluxo.etapa

    grupos_aprovadores = GrupoAprovador.objects.filter(grupos__overlap=[etapa])

    for grupo in grupos_aprovadores:

        for servidor in grupo.servidores.all():

            servidor_nome = (
                servidor.pessoa_fisica.social_name or servidor.pessoa_fisica.nome
            )
            servidor_email = (
                servidor.pessoa_fisica.email_institucional
                if servidor.pessoa_fisica.email_institucional
                else servidor.pessoa_fisica.email_pessoal
            )

            destinatarios.append(
                {
                    "nome": f"{servidor_nome}",
                    "email": f"{servidor_email}",
                }
            )

    return destinatarios


def validar_viagem_finalizar(viagem):
    # valida se a viagem está em rascunho
    if viagem.fluxo.id != 2:
        raise Exception("Esta solicitação de viagem já saiu do rascunho.")

    lista_beneficiarios = viagem.beneficiarios.all()

    # validar pelo menos um beneficiario
    if not lista_beneficiarios.exists():
        raise Exception(
            "Esta viagem não possui beneficiários. Cadastre pelo menos um para concluir a solicitação de diária."
        )

    # validar se todos os beneficiarios possuem Eventos e destinos cadastrados
    for beneficiario in lista_beneficiarios:
        if not beneficiario.eventos.exists():
            raise Exception(
                "Esta viagem tem beneficiários sem eventos cadastrados. Cadastre pelo menos um evento para concluir a solicitação de diária."
            )

        if not beneficiario.destinos.exists():
            raise Exception(
                "Esta viagem possui beneficiários sem trechos de destino cadastrados. Cadastre pelo menos um trecho de destino para concluir a solicitação de diária."
            )


def validar_viagem_cancelar(viagem, beneficiarios, solicitante, usuario):

    from diarias.models import FluxoViagem

    # Validar se existe pelo menos um beneficiário
    if not beneficiarios.exists():
        raise ValidationError(
            "Deve-se informar pelo menos um beneficiário para efetuar o cancelamento da solicitação de diária."
        )

    # Validar o cancelamento quando há apenas um beneficiário
    if beneficiarios.count() == 1:
        beneficiario = beneficiarios.first()
        if beneficiario.servidor.user != usuario and solicitante != usuario:
            raise ValidationError(
                "Somente o solicitante e o beneficiário podem cancelar uma solicitação de diária."
            )

    hoje = date.today()
    # Validar se a solicitação de cancelamento está ocorrendo com mais de um dia de antecedência
    if (viagem.data_inicio_viagem - hoje).days <= 1:
        raise ValidationError(
            "Somente poderá ser cancelada uma solicitação com prazo de mais de um dia antes do início da viagem."
        )

    fluxo_limite = FluxoViagem.objects.get(
        id=14
    )  # DEFIN - Gerência financeira - Aguardando ordem bancária

    fluxos_id_cancelados = [21, 32]

    # Validar se todos os beneficiários pertencem à mesma viagem e se têm eventos e destinos cadastrados
    for beneficiario in beneficiarios:
        if beneficiario.viagem != viagem:
            raise ValidationError(
                "Todos os beneficiários devem pertencer à mesma viagem."
            )

        if beneficiario.historico_fluxos.filter(fluxo=fluxo_limite).exists():
            raise ValidationError(
                f"O beneficiário {beneficiario.servidor.pessoa_fisica.social_name} "
                "já passou pelo fluxo 'DEFIN - Gerência financeira - Aguardando ordem bancária' "
                "e a sua solicitação não pode mais ser cancelada."
            )

        if beneficiario.historico_fluxos.filter(
            fluxo__id__in=fluxos_id_cancelados
        ).exists():
            raise ValidationError(
                f"A solicitação de diaria do {beneficiario.servidor.pessoa_fisica.social_name} "
                "já foi cancelada."
            )
