from contrib.utils import getLogger
from standard.models import EmailTemplate
from common.util.send_email import EmailNotification
from datetime import date, timedelta
from django.template.loader import render_to_string
from django.template.loader import render_to_string
from diarias.utils.utils import notificar_solititante_config_fluxo
from adm.utils.jwt_utils import gerar_token_jwt
from rh.apiv2.serializers.censoprevidenciario import data_limite


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

    dados_viagem = f"""
        <table class="custom-table">
            <tbody>
                <tr class="custom-row">
                    <th class="custom-header"><strong>Numero O.S.</strong></th>
                    <td class="custom-cell">{beneficiario.codigo_os}</td>
                </tr>
                <tr class="custom-row">
                    <td class="custom-cell"><strong>Eventos</strong></td>
                </tr>
                {eventos}
                <tr class="custom-row">
                    <td class="custom-cell"><strong>Trechos</strong></td>
                </tr>
                {techos}
            </tbody>
        </table>
    """

    return dados_viagem


def envio_email_prestacao_contas_colaboradores_externos(beneficiario):
    try:
        email_template_code = "PRESTACAO_CONTAS_DIARIAS_EXTERNA"

        email_template = get_email_template(email_template_code)

        email = (
            beneficiario.servidor.pessoa_fisica.email_institucional
            if beneficiario.servidor.pessoa_fisica.email_institucional
            else beneficiario.servidor.pessoa_fisica.email_pessoal
        )

        prestacao = beneficiario.prestacoes_contas.filter(status="aguardando").first()

        id_prestacao = prestacao.id

        token = gerar_token_jwt(
            beneficiario.servidor.user.username, prestacao.data_limite
        )

        link = f'<a href="https://mpmt.mp.br/diarias-prestacao-contas.php?id={id_prestacao}&token={token}" > Clique aqui </a>'  # link temporario

        data_limite = beneficiario.viagem.data_fim_viagem + timedelta(days=5)

        dados_viagem = get_dados_beneficiario(beneficiario)

        message = (
            email_template.contents.replace(
                "%BENEFICIARIO%", beneficiario.servidor.pessoa_fisica.social_name
            )
            .replace("%LINK%", link)
            .replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%DATA_LIMITE%", data_limite.strftime("%d/%m/%Y"))
        )

        destinatarios = [
            {
                "nome": f"{beneficiario.servidor.pessoa_fisica.social_name}",
                "email": f"{email}",
            },
        ]

        destinatarios = notificar_solititante_config_fluxo(beneficiario, destinatarios)

        log.info(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )
        print(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )

        html_content = render_to_string(
            "util/template_email.html", {"message": message}
        )
        response = EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

        print(f"response : {response}")
        log.info(f"response : {response}")

    except Exception as error:
        log.info(error)
        print(error)


def envio_email_prestacao_contas_deferida(prestacao_contas):
    try:
        email_template_code = "PRESTACAO_CONTAS_DIARIAS_DEFERIDA"
        email_template = get_email_template(email_template_code)

        beneficiario = prestacao_contas.beneficiario

        email = (
            beneficiario.servidor.pessoa_fisica.email_institucional
            if beneficiario.servidor.pessoa_fisica.email_institucional
            else beneficiario.servidor.pessoa_fisica.email_pessoal
        )

        dados_viagem = get_dados_beneficiario(beneficiario)

        message = (
            email_template.contents.replace(
                "%BENEFICIARIO%", beneficiario.servidor.pessoa_fisica.social_name
            )
            .replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%OBS_ANALISE%", prestacao_contas.obs_anlaise or "")
        )

        destinatarios = [
            {
                "nome": f"{beneficiario.servidor.pessoa_fisica.social_name}",
                "email": f"{email}",
            },
        ]

        destinatarios = notificar_solititante_config_fluxo(beneficiario, destinatarios)

        log.info(
            f"Envio de notificação de prestação de contas deferida do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )
        print(
            f"Envio de notificação de prestação de contas deferida do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )

        html_content = render_to_string(
            "util/template_email.html", {"message": message}
        )
        response = EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

        print(f"response : {response}")
        log.info(f"response : {response}")

    except Exception as error:
        log.info(error)
        print(error)


def envio_email_prestacao_contas_indeferida(prestacao_contas):
    try:
        email_template_code = "PRESTACAO_CONTAS_DIARIAS_INDEFERIDA"
        email_template = get_email_template(email_template_code)

        beneficiario = prestacao_contas.beneficiario

        email = (
            beneficiario.servidor.pessoa_fisica.email_institucional
            if beneficiario.servidor.pessoa_fisica.email_institucional
            else beneficiario.servidor.pessoa_fisica.email_pessoal
        )

        dados_viagem = get_dados_beneficiario(beneficiario)

        message = (
            email_template.contents.replace(
                "%BENEFICIARIO%", beneficiario.servidor.pessoa_fisica.social_name
            )
            .replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%OBS_ANALISE%", prestacao_contas.obs_anlaise or "")
        )

        destinatarios = [
            {
                "nome": f"{beneficiario.servidor.pessoa_fisica.social_name}",
                "email": f"{email}",
            },
        ]

        destinatarios = notificar_solititante_config_fluxo(beneficiario, destinatarios)

        log.info(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )
        print(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )

        html_content = render_to_string(
            "util/template_email.html", {"message": message}
        )
        response = EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

        print(f"response : {response}")
        log.info(f"response : {response}")

    except Exception as error:
        log.info(error)
        print(error)


def envio_email_prestacao_contas_aviso(prestacao_contas):
    try:
        email_template_code = "PRESTACAO_CONTAS_DIARIAS_AVISO"
        email_template = get_email_template(email_template_code)

        beneficiario = prestacao_contas.beneficiario

        email = (
            beneficiario.servidor.pessoa_fisica.email_institucional
            if beneficiario.servidor.pessoa_fisica.email_institucional
            else beneficiario.servidor.pessoa_fisica.email_pessoal
        )

        dados_viagem = get_dados_beneficiario(beneficiario)

        message = (
            email_template.contents.replace(
                "%BENEFICIARIO%", beneficiario.servidor.pessoa_fisica.social_name
            )
            .replace("%DADOS_VIAGEM%", dados_viagem)
            .replace("%DATA_LIMITE%", prestacao_contas.data_limite.strftime("%d/%m/%Y"))
        )

        destinatarios = [
            {
                "nome": f"{beneficiario.servidor.pessoa_fisica.social_name}",
                "email": f"{email}",
            },
        ]

        destinatarios = notificar_solititante_config_fluxo(beneficiario, destinatarios)

        log.info(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )
        print(
            f"Envio de notificação de prestação de contas do beneficiario {beneficiario.servidor.pessoa_fisica.social_name} - {beneficiario.codigo_os}"
        )

        html_content = render_to_string(
            "util/template_email.html", {"message": message}
        )
        response = EmailNotification().send_email_default(
            destinatarios, email_template.subject, html_content
        )

        print(f"response : {response}")
        log.info(f"response : {response}")

    except Exception as error:
        log.info(error)
        print(error)
