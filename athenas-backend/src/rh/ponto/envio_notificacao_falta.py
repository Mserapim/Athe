from contrib.utils import getLogger
from django.template.loader import render_to_string
from common.util.send_email import EmailNotification
from standard.models import EmailTemplate, Item, JustificationItem


log = getLogger(__name__)


def enviar_notificacao_falta(falta, tipo_notificacao="FALTA"):
    """
    Envia notificações por e-mail com base na instância do modelo Falta. Esta função é usada para:
    - Notificar sobre uma falta que teve prejuízo financeiro (com ou sem justificativa).
    - Notificar sobre a remoção de uma falta.

    :para falta: instância do modelo Falta
    :para tipo_notificacao: Tipo de notificação - 'FALTA' (default) ou 'REMOCAO'
    """

    codigo = None

    servidor = falta.servidor

    email_superior = (
        servidor.chefe_imediato.pessoa_fisica.email_institucional
        if servidor.chefe_imediato
        else None
    )

    lista_destinatarios = [
        {
            "email": servidor.pessoa_fisica.email_institucional,
            "nome": servidor.pessoa_fisica.nome,
            "idUsuario": servidor.id_usuario_mastiff,
        }
    ]

    if email_superior:
        lista_destinatarios.append(
            {
                "email": servidor.chefe_imediato.pessoa_fisica.email_institucional,
                "nome": servidor.chefe_imediato.pessoa_fisica.nome,
                "idUsuario": servidor.chefe_imediato.id_usuario_mastiff,
            }
        )

    config_email_item = Item.objects.get(key="notificacao_falta")

    lista_email = config_email_item.value.split(",")

    for email in lista_email:
        lista_destinatarios.append({"email": email, "nome": email.upper()})

    if tipo_notificacao == "FALTA":
        if (falta.justificado and falta.payroll) or falta.justificado is False:
            if falta.justificado is False:
                codigo = "NOTIFICACAO_FALTA"
            else:
                codigo = "NOTIFICACAO_FALTA_FINANCEIRO"
                justificativa = falta.point_justification.last()
                item_justificativa = JustificationItem.objects.get(
                    value=justificativa.reason_type
                )
                descricao_justificativa = item_justificativa.name

    elif tipo_notificacao == "REMOCAO":
        if falta.data_processado is not None:
            codigo = "REMOCAO_FALTA"

    if codigo is None:
        return

    email_template = EmailTemplate.objects.get(code=codigo)
    conteudo = email_template.contents.replace(
        "%nome_servidor%", servidor.pessoa_fisica.nome
    ).replace("dd/mm/aaa", falta.data.strftime("%d/%m/%Y"))

    if tipo_notificacao == "FALTA":
        conteudo = conteudo.replace(
            "%competencia_desconto%", falta.competencia_desconto
        )
        if falta.justificado and falta.payroll:
            conteudo = conteudo.replace("%justificativa%", descricao_justificativa)

    assunto = email_template.subject

    html_content = render_to_string("util/template_email.html", {"message": conteudo})

    EmailNotification().send_email_default(
        lista_destinatarios, email_template.subject, html_content
    )
