from app.settings import HERMES_TOKEN_RELATORIOS
from common.util.send_email import EmailNotification
from contrib.utils import employee_from_user
from engine.mq.const import SISTEMA_HERMES_RELATORIO, TEMPLATE_NOTIFICACAO_RELATORIO
from standard.models import EmailTemplate


def notificar_hermes_ged(user, link, relatorio):
    """Este método envia notificação para o hermes com o link para download do arquivo
    Args:
        user (obj):usuario logado
        link (str): link para donwload
        relatorio (str): nome do relatório
    """
    servidor = employee_from_user(user)
    pessoa_fisica = servidor.pessoa_fisica
    destinatarios = [
        {
            "email": pessoa_fisica.email,
            "nome": pessoa_fisica.nome,
            "idUsuario": servidor.id_usuario_mastiff,
        }
    ]
    template = EmailTemplate.objects.filter(code=TEMPLATE_NOTIFICACAO_RELATORIO).first()
    if template:
        conteudo = template.contents.replace("%link%", link).replace(
            "%nome_relatorio%", relatorio
        )
        assunto = template.subject
        token = HERMES_TOKEN_RELATORIOS
        sistema = SISTEMA_HERMES_RELATORIO
        EmailNotification().send_email_default(
            destinatarios, assunto, conteudo, hermes_token=token, sistema=sistema
        )
