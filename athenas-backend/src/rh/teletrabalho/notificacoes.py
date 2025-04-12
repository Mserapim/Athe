from common.util.send_email import EmailNotification
from contrib.utils import DateUtils
from django.template.loader import render_to_string
from standard.models import EmailTemplate
from logging import getLogger
from standard.models import EmailTemplate, Item

log = getLogger(__name__)


def enviar_notificacao_email_gestor(mov_teletrabalhos):
    """Rotina que envia email para o gestor sobre os bloqueios do tele
    Args:
        mov_teletrabalho (obj): plano do tele.
    """
    try:
        codigo_email = "BLOQUEIO_TELETRABALHO"
        email_template = EmailTemplate.objects.get(code=codigo_email)

        dados_planos = []
        for tele in mov_teletrabalhos:
            vigencia = f"""{DateUtils.date_to_str(tele.data_inicio)} até 
                {DateUtils.date_to_str(tele.data_fim) if tele.data_fim else ''}
            """
            dados_planos.append(
                {
                    "nome_servidor": str(tele.servidor),
                    "plano_id": tele.pk,
                    "vigencia_plano": vigencia,
                    "qtde_bloqueios": f"{str(tele.qtd_bloqueios) if tele.qtd_bloqueios else 0}",
                    "aprovador_nome": str(tele.aprovador),
                }
            )

        conteudo_html = render_to_string(
            "util/template_tabela_teletrabalho.html", {"dados": dados_planos}
        )

        conteudo = email_template.contents.replace("@conteudo", conteudo_html)

        config_email_item = Item.objects.get(key="notificacao_bloqueio_teletrabalho")

        lista_email = config_email_item.value.split(",")

        lista_destinatarios = []

        for email in lista_email:
            lista_destinatarios.append(
                {
                    "email": email,
                    "nome": email.upper(),
                }
            )

        html_content = render_to_string(
            "util/template_email.html", {"message": conteudo}
        )
        EmailNotification().send_email_default(
            lista_destinatarios, email_template.subject, html_content
        )

    except Exception as error:
        log.error(error)


def enviar_notificacao_email_servidor(mov_teletrabalho, servidor, qtd_bloqueios):
    """Rotina que envia email para o servidor avisando sobre o bloqueio do plano de teletrabalho
    Args:
        mov_teletrabalho (obj): planon do tele.
        servidor (obj):  Servidor que será notificado.
        qtd_bloqueios (int): quantidade de bloqueios do tele
    """
    try:
        codigo_email = "BLOQUEIO_TELETRABALHO_SERVIDOR"
        email_template = EmailTemplate.objects.get(code=codigo_email)

        conteudo = (
            email_template.contents.replace(
                "@nome_servidor", servidor.pessoa_fisica.social_name
            )
            .replace("@codigo_plano", str(mov_teletrabalho.pk))
            .replace(
                "@data_inicio", DateUtils.date_to_str(mov_teletrabalho.data_inicio)
            )
            .replace(
                "@data_fim",
                (
                    DateUtils.date_to_str(mov_teletrabalho.data_fim)
                    if mov_teletrabalho.data_fim
                    else ""
                ),
            )
            .replace("@qtde_bloqueios", str(qtd_bloqueios) if qtd_bloqueios else 0)
        )

        assunto = email_template.subject.replace(
            "@nome_servidor", mov_teletrabalho.servidor.pessoa_fisica.nome.upper()
        )

        lista_destinatarios = [
            {
                "email": servidor.pessoa_fisica.email,
                "nome": servidor.pessoa_fisica.nome.upper(),
                "idUsuario": servidor.id_usuario_mastiff,
            }
        ]

        html_content = render_to_string(
            "util/template_email.html", {"message": conteudo}
        )
        EmailNotification().send_email_default(
            lista_destinatarios, assunto, html_content
        )

    except Exception as error:
        log.error(error)


def enviar_notificacao_cadastro_plano(mov_teletrabalho):
    """Rotina que envia email para um novo cadastro do plano do teletrabalho
    Args:
        mov_teletrabalho (obj): plano do teletrabalho.
    """
    try:
        servidor = mov_teletrabalho.servidor
        aprovador = mov_teletrabalho.aprovador
        codigo_email = "CADASTRO_TELETRABALHO"
        email_template = EmailTemplate.objects.get(code=codigo_email)

        conteudo_html = f"""
            <ul>
                <li><strong>Plano:</strong> {str(mov_teletrabalho)}</li>
                <li><strong>Tipo Pedido:</strong> {mov_teletrabalho.get_tipo_pedido_display()}</li>
                <li><strong>Gedoc:</strong> {mov_teletrabalho.gedoc}</li>
                <li><strong>Aprovador:</strong> {str(aprovador)}</li>
            </ul>
        """

        conteudo = email_template.contents.replace("@dados_teletrabalho", conteudo_html)

        lista_destinatarios = [
            {
                "email": servidor.pessoa_fisica.email,
                "nome": servidor.pessoa_fisica.nome.upper(),
                "idUsuario": servidor.id_usuario_mastiff,
            },
            {
                "email": aprovador.pessoa_fisica.email,
                "nome": aprovador.pessoa_fisica.nome.upper(),
                "idUsuario": aprovador.id_usuario_mastiff,
            },
        ]

        config_email_item = Item.objects.get(key="notificacao_cadastro_teletrabalho")
        lista_email = config_email_item.value.split(",")

        for email in lista_email:
            lista_destinatarios.append(
                {
                    "email": email,
                    "nome": email.upper(),
                }
            )

        html_content = render_to_string(
            "util/template_email.html", {"message": conteudo}
        )
        EmailNotification().send_email_default(
            lista_destinatarios, email_template.subject, html_content
        )

    except Exception as error:
        log.error(error)


def enviar_notificacao_alteracao_meta(mov_teletrabalho, meta_tele):
    """Rotina que envia email para quando há uma alteração de meta do plano,
        seja alterar a quantidade, novas metas ou inativações de metas.
    Args:
        mov_teletrabalho (obj): plano do teletrabalho.
        meta do plano (obj): meta do teletrabalho.
    """
    try:
        servidor = mov_teletrabalho.servidor
        codigo_email = "ALTERACOES_TELETRABALHO"
        email_template = EmailTemplate.objects.get(code=codigo_email)

        conteudo_html = f"""
            <ul>
                <li><strong>Plano:</strong> {str(mov_teletrabalho)}</li>
                <li><strong>Vigência da meta:</strong>
                  {DateUtils.date_to_str(meta_tele.data_inicio)} até {DateUtils.date_to_str(meta_tele.data_fim)}
                </li>
                <li><strong>Ativo:</strong> { 'SIM' if meta_tele.active else 'NÃO'}</li>
                <li><strong>Quantidade da meta:</strong> {meta_tele.meta}</li>
                <li><strong>Descrição:</strong> {meta_tele.descricao}</li>
            </ul>
        """

        conteudo = email_template.contents.replace("@dados_teletrabalho", conteudo_html)

        lista_destinatarios = [
            {
                "email": servidor.pessoa_fisica.email,
                "nome": servidor.pessoa_fisica.nome.upper(),
                "idUsuario": servidor.id_usuario_mastiff,
            }
        ]

        config_email_item = Item.objects.get(key="notificacao_cadastro_teletrabalho")
        lista_email = config_email_item.value.split(",")

        for email in lista_email:
            lista_destinatarios.append(
                {
                    "email": email,
                    "nome": email.upper(),
                }
            )

        html_content = render_to_string(
            "util/template_email.html", {"message": conteudo}
        )
        EmailNotification().send_email_default(
            lista_destinatarios, email_template.subject, html_content
        )

    except Exception as error:
        log.error(error)


def enviar_notificacao_saldo_devedor(metas):
    """Rotina que envia email para quando a meta informada for menor que a do mês
    Args:
        metas (obj): metas do plano de teletrabalho.
    """
    try:
        mov_teletrabalho = metas[0].request.work_plan
        solicitacao = metas[0].request
        servidor = mov_teletrabalho.servidor
        codigo_email = "SALDO_DEVEDOR_META"
        email_template = EmailTemplate.objects.get(code=codigo_email)

        dados_meta = []

        for meta in metas:
            dados_meta.append(
                {
                    "descricao": meta.mark_plan.descricao,
                    "plano": str(mov_teletrabalho),
                    "meta_cadastrada": meta.mark_plan.meta,
                    "meta_mes": meta.meta_mes,
                    "meta_informada": meta.total_completed,
                    "saldo_devedor": meta.saldo_devedor,
                }
            )

        conteudo_html = render_to_string(
            "util/template_tabela_metas.html", {"dados": dados_meta}
        )

        conteudo = (
            email_template.contents.replace(
                "@nome_servidor", servidor.pessoa_fisica.nome
            )
            .replace("@dados_meta", conteudo_html)
            .replace("@mes", str(solicitacao.reference_month))
            .replace("@ano", str(solicitacao.reference_year))
        )

        lista_destinatarios = [
            {
                "email": servidor.pessoa_fisica.email,
                "nome": servidor.pessoa_fisica.nome.upper(),
                "idUsuario": servidor.id_usuario_mastiff,
            }
        ]

        html_content = render_to_string(
            "util/template_email.html", {"message": conteudo}
        )
        EmailNotification().send_email_default(
            lista_destinatarios, email_template.subject, html_content
        )

    except Exception as error:
        log.error(error)
