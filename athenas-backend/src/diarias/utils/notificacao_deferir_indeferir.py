from contrib.utils import getLogger
from standard.models import Item, EmailTemplate
from common.util.send_email import EmailNotification
from diarias.utils.utils import (
    notificar_solititante_config_fluxo,
    notificar_aprovadores_fluxo,
)
from django.template.loader import render_to_string


log = getLogger(__name__)


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
                <td class="custom-cell"  colspan="2">{ texto }</td>
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
                <td class="custom-cell"  colspan="2">{ texto }</td>
            </tr>
        """

    dados_beneficiario = f"""
        <table class="custom-table">
            <tbody>
                <tr>
                    <th class="custom-header"><strong>Beneficiário</strong></th>
                    <td class="custom-cell">{beneficiario.servidor.pessoa_fisica.social_name}</td>
                </tr>
                <tr class="custom-row">
                    <th class="custom-header"><strong>Numero O.S.</strong></th>
                    <td class="custom-cell">{beneficiario.codigo_os}</td>
                </tr>
                <tr class="custom-row">
                    <td class="custom-cell" colspan="2"><strong>Eventos</strong></td>
                </tr>
                {eventos}
                <tr class="custom-row">
                    <td class="custom-cell" colspan="2"><strong>Trechos</strong></td>
                </tr>
                {techos}
            </tbody>
        </table>
    """

    return dados_beneficiario


def enviar_email_acao(beneficiario, acao):
    try:
        if acao == "deferir":
            email_template_code = "DIARIAS_ACAO_DEFERIR"
        else:
            email_template_code = "DIARIAS_ACAO_INDEFERIR"

        email_template = get_email_template(email_template_code)

        email = (
            beneficiario.servidor.pessoa_fisica.email_institucional
            if beneficiario.servidor.pessoa_fisica.email_institucional
            else beneficiario.servidor.pessoa_fisica.email_pessoal
        )

        dados_viagem = get_dados_beneficiario(beneficiario)

        fluxos = beneficiario.historico_fluxos.all().order_by("-id")[:2]

        message = (
            email_template.contents.replace(
                "%BENEFICIARIO%", beneficiario.servidor.pessoa_fisica.social_name
            )
            .replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%NUMERO_OS%", beneficiario.codigo_os)
            .replace("%ETAPA%", f"{fluxos[1].fluxo.get_situacao_display()}")
            .replace("%AVALIADOR%", f"{fluxos[1].acao_por}")
        )

        destinatarios = [
            {
                "nome": f"{beneficiario.servidor.pessoa_fisica.social_name}",
                "email": f"{email}",
            },
        ]

        config = Item.objects.get(key="notificar_acao_diarias")

        for email in config.value.split(";"):
            destinatarios.append(
                {
                    "nome": f"",
                    "email": f"{email}",
                }
            )

        destinatarios = notificar_solititante_config_fluxo(beneficiario, destinatarios)
        destinatarios = notificar_aprovadores_fluxo(beneficiario, destinatarios)

        log.info(
            f"Envio de notificação de deferir/indeferir em  etapa da solicitação de diaria do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )
        print(
            f"Envio de notificação de deferir/indeferir em  etapa da solicitação de diaria do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )

        html_content = render_to_string(
            "util/template_email_anexo.html", {"message": message}
        )

        response = EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

        print(f"response : {response}")
        log.info(f"response : {response}")

        return response

    except Exception as error:
        log.info(error)
        print(error)
