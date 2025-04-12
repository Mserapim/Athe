from contrib.utils import getLogger
from diarias.models import (
    Beneficiario,
    CalculoConsolidado,
    LimiteDiarias,
    PrestacaoContasAnexo,
    Viagem,
    ViagemAnexo,
)
from django.db import transaction
from django.template.loader import render_to_string
import traceback
from diarias.const import FLUXOS_CANCELADOS
from diarias.utils.utils import (
    buscar_beneficiarios_servidor_ano_motivos,
    buscar_beneficiarios_servidor_mes_motivos,
    clonar_beneficiario,
    clonar_evento,
    clonar_viagem,
    clonar_destino,
)
from django.db.models import Sum
from standard.models import Item, EmailTemplate
from common.util.send_email import EmailNotification
from diarias.utils.os_consolidada import GerarOsConsolidada


log = getLogger(__name__)


def verificar_excedentes(beneficiario, qtd_diarias=0):
    """
    Função que recebe um beneficiario e retorna o numero de diarias excedentes que ele vai possuir com a nova diaria que ele foi cadastrado

    é feito o teste de o servidor é um membro ou servidor, e com isso é feito a busca dos LimiteDiarias pertencentes a esse tipo, e em seguida
    e feito mais filtro na query de limites para buscar o LimiteDiarias que abrange o motivo da viagem do beneficiario, em seguida pega o limite
    encontrado e testa se ele possui limite definido, caso esteja nulo, ele passa direto.

    busca-se todos os beneficiarios/viagens que o servidor possui, se acordo com a referencia do limite encontrado, anual ou mensal, logo em seguida,
    exclui a viagem atual do servidor e as viagens que possuem uma viagem de origem. Caso exista algum resultado com este filtro, é feito a  busca de
    todos os CalculosConsolidados vinculados a lista de beneficiarios, e feito a soma do campo qtd_total_diarias_calculada, para encontrar o numero de
    diarias usadas no periodo de referencia do limite .

    falta criar a logica para pegar a quantidade de diarias, da viagem atual, antes do calculoconsolidado.

    """

    qtd_excedentes = 0
    qtd_total_excedentes = 0
    qtd_limite = None
    qtd_saldo = 0
    qtd_uso = 0

    servidor = beneficiario.servidor
    ano_viagem = beneficiario.viagem.data_inicio_viagem.year
    mes_viagem = beneficiario.viagem.data_inicio_viagem.month

    tipo = "membro" if servidor.membro else "servidor"

    q_limites = LimiteDiarias.objects.filter(tipo=tipo)
    q_limites = q_limites.filter(
        motivos_viagem__contains=[beneficiario.viagem.motivo_viagem]
    )

    limite = q_limites.first()

    q_beneficiarios = []
    if limite.limite:
        qtd_limite = limite.limite

        if limite.referencia == "anual":
            q_beneficiarios = buscar_beneficiarios_servidor_ano_motivos(
                servidor, ano=ano_viagem, motivos=limite.motivos_viagem
            )
        else:
            q_beneficiarios = buscar_beneficiarios_servidor_mes_motivos(
                servidor, ano=ano_viagem, mes=mes_viagem, motivos=limite.motivos_viagem
            )

        q_beneficiarios = (
            q_beneficiarios.exclude(viagem=beneficiario.viagem)
            .exclude(viagem__viagem_origem__isnull=False)
            .exclude(fluxo__in=FLUXOS_CANCELADOS)
        )

        if q_beneficiarios.exists():
            soma_diarias = CalculoConsolidado.objects.filter(
                beneficiario__in=q_beneficiarios
            ).aggregate(soma=Sum("qtd_total_diarias_calculadas"))["soma"]

            if soma_diarias is None:
                soma_diarias = 0

            qtd_uso = soma_diarias + qtd_diarias
            qtd_saldo = (
                0
                if soma_diarias and soma_diarias > qtd_limite
                else qtd_limite - soma_diarias
            )

            if soma_diarias and qtd_uso > qtd_limite:
                qtd_total_excedentes = qtd_uso - qtd_limite
                qtd_excedentes = qtd_diarias - qtd_saldo
                qtd_saldo = 0
            else:
                qtd_saldo = qtd_limite - qtd_uso

        else:
            qtd_uso = qtd_diarias

            if qtd_diarias > qtd_limite:
                qtd_total_excedentes = qtd_diarias - qtd_limite
                qtd_excedentes = qtd_total_excedentes
                qtd_saldo = 0
            else:
                qtd_saldo = qtd_limite - qtd_diarias

    return qtd_limite, qtd_saldo, qtd_uso, qtd_total_excedentes, qtd_excedentes


def criar_excedente(beneficiario, qtd_excedentes):
    from diarias.utils.fluxo_movimentacao import benef_mover_etapa

    try:
        viagem = beneficiario.viagem
        with transaction.atomic():
            nova_viagem = clonar_viagem(viagem)

            novo_beneficiario = clonar_beneficiario(beneficiario, nova_viagem)

            for evento in beneficiario.eventos.all():
                clonar_evento(evento, novo_beneficiario)

            for destino in beneficiario.destinos.all():
                clonar_destino(destino, novo_beneficiario)

            enviar_email_diaria_excedente_gedoc(
                beneficiario, novo_beneficiario, qtd_excedentes
            )
            benef_mover_etapa(novo_beneficiario, fluxo_especifico=27)

    except Exception as e:
        erro_completo = traceback.format_exc()
        print(e)
        log.error(e)
        log.error(erro_completo)


def get_email_template(template_code):
    try:
        log.info(f"Buscando o Modelo de Email: {template_code}!")

        return EmailTemplate.objects.get(code=template_code)
    except EmailTemplate.DoesNotExist:
        log.error(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
        return None


def get_dados_beneficiario(beneficiario):

    eventos = ""
    for evento in beneficiario.eventos.all():

        dt_inicio = evento.data_inicio.strftime("%d/%m/%Y")
        dt_fim = (
            f" até {evento.data_fim.strftime('%d/%m/%Y')}" if evento.data_fim else ""
        )
        texto = (
            f"{evento.titulo}: de {dt_inicio}{dt_fim}"
            if dt_fim
            else f"{evento.titulo}:{evento.titulo}: data: {dt_inicio}"
        )

        eventos += f"""
            <tr class="custom-row">
                <td class="custom-cell"  colspan="6">{ texto }</td>
            </tr>
        """
    techos = ""
    for trecho in beneficiario.destinos.all():
        origem = (
            f"{trecho.municipio_origem.estado.sigla}/{trecho.municipio_origem.nome}"
        )
        destino = (
            f"{trecho.municipio_destino.estado.sigla}/{trecho.municipio_destino.nome}"
        )
        data = trecho.data.strftime("%d/%m/%Y")

        texto = f"origem:{origem} - destino: {destino} - data: { data }"

        techos += f"""
            <tr class="custom-row">
                <td class="custom-cell"  colspan="6">{ texto }</td>
            </tr>
        """

    dados_beneficiario = f"""
        <table class="custom-table">
            <tbody>
                <tr class="custom-row">
                    <th class="custom-header"><strong>Beneficiário</strong></th>
                    <td class="custom-cell">{beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.servidor.matricula}</td>
                    <th class="custom-header"><strong>Categoria Funcional</strong></th>
                    <td class="custom-cell">{beneficiario.servidor.get_type_by_possession_display()}</td>
                    <th class="custom-header"><strong>Numero O.S.</strong></th>
                    <td class="custom-cell">{beneficiario.codigo_os}</td>
                </tr>
                <tr class="custom-row">
                    <td class="custom-cell" colspan="6"><strong>Dados da Viagem</strong></td>
                </tr>
                <tr class="custom-row">
                    <th class="custom-header"><strong>Tipo da Viagem</strong></th>
                    <td class="custom-cell">{beneficiario.viagem.get_tipo_viagem_display()}</td>

                    <th class="custom-header"><strong>Motivo da Viagem</strong></th>
                    <td class="custom-cell">{beneficiario.viagem.get_motivo_viagem_display()}</td>

                    <th class="custom-header"><strong>Finalidade da Viagem</strong></th>
                    <td class="custom-cell">{beneficiario.viagem.get_finalidade_viagem_display()}</td>
                </tr>
                 <tr class="custom-row">
                    <th class="custom-header"><strong>Data Inicio</strong></th>
                    <td class="custom-cell">{beneficiario.viagem.data_inicio_viagem}</td>

                    <th class="custom-header"><strong>Data Fim</strong></th>
                    <td class="custom-cell">{beneficiario.viagem.data_inicio_viagem}</td>
                   
                </tr>
                <tr class="custom-header">
                    <td class="custom-cell" colspan="6"><strong>Eventos</strong></td>
                </tr>
                {eventos}
                <tr class="custom-header">
                    <td class="custom-cell" colspan="6"><strong>Trechos</strong></td>
                </tr>
                {techos}
            </tbody>
        </table>
    """

    return dados_beneficiario


def enviar_email_diaria_excedente_gedoc(
    beneficiario_original, beneficiario_excedente, qtd_excedentes
):
    try:
        email_template_code = "SOLICITACAO_DIARIAS_EXCEDENTES_GEDOC"

        email_template = get_email_template(email_template_code)

        dados_viagem = get_dados_beneficiario(beneficiario_excedente)

        os_original = beneficiario_original.codigo_os
        os_excedente = beneficiario_excedente.codigo_os
        qtd_diarias = f"{qtd_excedentes}"

        anexos = []
        for anexo in beneficiario_excedente.viagem.anexos_viagem.all():
            anexos.append(anexo.arquivo)

        message = (
            email_template.contents.replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%OSORIGINAL%", os_original)
            .replace("%OSEXCEDENTE%", os_excedente)
            .replace("%QTD_DIAS%", qtd_diarias)
        )

        config = Item.objects.get(key="email_gedoc_excedentes")

        destinatarios = []

        for email in config.value.split(";"):

            destinatarios.append(
                {
                    "nome": f"",
                    "email": f"{email}",
                }
            )

        files = []

        os_consolidada = GerarOsConsolidada().criar_os(beneficiario_original)

        if os_consolidada:
            files.append(os_consolidada)

        log.info(f"Envio de solicitacao de abertura de GEDOC para diaria excedente ")
        print(f"Envio de solicitacao de abertura de GEDOC para diaria excedente ")

        html_content = render_to_string(
            "util/template_email_anexo.html", {"message": message}
        )
        response = EmailNotification().send_email_anexo(
            destinatarios,
            email_template.subject,
            html_content,
            anexos=anexos,
            files=files,
        )

    except Exception as error:
        erro_completo = traceback.format_exc()
        log.info(erro_completo)
        print(erro_completo)

        log.info(error)
        print(error)
