from django.template.loader import render_to_string
from common.util.send_email import EmailNotification
from standard.models import EmailTemplate


def notifica_cadastro_plantao(template, plantao):
    email_template = EmailTemplate.objects.get(code=template)
    lista_destinatarios = []
    lista_destinatarios.append(
        {
            "email": plantao.employee.pessoa_fisica.email_institucional,
            "nome": plantao.employee.pessoa_fisica.nome,
            "idUsuario": plantao.employee.id_usuario_mastiff,
        },
    )
    conteudo = (
        email_template.contents.replace(
            "@nome_plantonista", str(plantao.employee.pessoa_fisica.nome)
        )
        .replace("@dia_inicio", str(plantao.start_date.strftime("%d/%m/%Y")))
        .replace("@dia_fim", str(plantao.end_date.strftime("%d/%m/%Y")))
        .replace("@nome_criador_plantão", str(plantao.owner))
        .replace("@lotacao_plantao", str(plantao.workplace))
    )
    assunto = email_template.subject
    html_content = render_to_string(
        "util/template_email_basic.html", {"message": conteudo}
    )
    EmailNotification().send_email_default(lista_destinatarios, assunto, html_content)
