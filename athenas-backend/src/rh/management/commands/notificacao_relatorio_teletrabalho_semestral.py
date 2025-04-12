import calendar
import datetime

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models import Q

from common.util.send_email import EmailNotification
from standard.models import EmailTemplate, Item
from rh.models import Servidor, MovimentacaoTeletrabalho
from rh.teletrabalho.models import ConfigPeriodoEnvioRelatoriosSemestrais
from rh.pvf.signals import get_emails_approvers


log = getLogger("db")


class Command(BaseCommand):
    help = """Esse Comando irá disparar emails para os aprovadores de teletrabalho informando sobre
    o período de envio do relatório de teletrabalho semestral utilizando o modelo de emails.
    """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        self.set_user_to_job("job_enviar_notificacao_relatorio")
        self.enviar_notificacao_relatorio()

    def get_aprovadores(self):
        data_atual = datetime.datetime.today().date()
        data_envio_notificacao = data_atual + datetime.timedelta(days=5)
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.order_by(
            "data_inicio_periodo_envio"
        ).last()
        if periodo:
            data_inicio_envio = periodo.data_inicio_periodo_envio
            if (
                data_inicio_envio == data_envio_notificacao
                or data_inicio_envio == data_atual
            ):
                mes_inicio_analisado, ano_inicio_analisado = map(
                    int, periodo.data_inicio_periodo_analisado.split("/")
                )
                mes_fim_analisado, ano_fim_analisado = map(
                    int, periodo.data_fim_periodo_analisado.split("/")
                )
                data_inicio_analisado = datetime.date(
                    ano_inicio_analisado, mes_inicio_analisado, 1
                )
                ultimo_dia_mes_fim_analisado = calendar.monthrange(
                    ano_fim_analisado, mes_fim_analisado
                )[1]
                data_fim_analisado = datetime.date(
                    ano_fim_analisado, mes_fim_analisado, ultimo_dia_mes_fim_analisado
                )

                aprovadores = (
                    MovimentacaoTeletrabalho.objects.filter(
                        Q(data_inicio__lte=data_fim_analisado)
                        & Q(data_fim__gte=data_inicio_analisado)
                    )
                    .values_list("aprovador", flat=True)
                    .distinct()
                )
                return Servidor.objects.filter(pk__in=aprovadores)

            else:
                log.error(
                    f"Não foi possível encontrar aprovadores no período de relatórios semestrais configurado."
                )
                return []
        else:
            return []

    def lista_aprovadores_compilada(self, aprovadores):
        nomes_aprovadores = [
            aprovador.pessoa_fisica.social_name for aprovador in aprovadores
        ]
        return ", ".join(nomes_aprovadores)

    def get_email_template(self, template_code):
        try:
            log.info(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
            return EmailTemplate.objects.get(code=template_code)
        except EmailTemplate.DoesNotExist:
            log.error(f"Não foi possível encontrar o Modelo de Email: {template_code}!")
            return None

    def enviar_email_notificacao(self, email_template, aprovadores):
        log.info(f">>> Quantidade de aprovadores: {len(aprovadores)}")
        periodo = ConfigPeriodoEnvioRelatoriosSemestrais.objects.order_by(
            "data_inicio_periodo_envio"
        ).last()
        if not periodo:
            log.error(
                "Não foi possível encontrar o período atual para o relatório semestral de teletrabalho."
            )
            return

        data_inicio = periodo.data_inicio_periodo_envio.strftime("%d/%m/%Y")
        data_fim = periodo.data_fim_periodo_envio.strftime("%d/%m/%Y")

        email_destinatario = Item.objects.get(
            configuration__application="vdf", key="notificacao_semestral_teletrabalho"
        ).value
        destinatarios = get_emails_approvers(email_destinatario)

        for aprovador in aprovadores:
            email_to = (
                aprovador.user.email
                if aprovador.user.email
                else aprovador.pessoa_fisica.email
            )
            destinatario = {
                "email": email_to,
                "nome": aprovador.pessoa_fisica.social_name,
                "idUsuario": aprovador.id_usuario_mastiff,
            }
            destinatarios.append(destinatario)

        for destinatario in destinatarios:
            message = (
                email_template.contents.replace("@nome_gestor", destinatario["nome"])
                .replace("@mes_ano_inicio", periodo.data_inicio_periodo_analisado)
                .replace("@mes_ano_final", periodo.data_fim_periodo_analisado)
                .replace("@dia_inicio", data_inicio)
                .replace("@dia_fim", data_fim)
            )
            html_content = render_to_string(
                "util/template_email.html", {"message": message}
            )

            log.info(
                f">>> Enviando email para: {destinatario['nome']}, email: {destinatario['email']}"
            )
            EmailNotification().send_email_default(
                [destinatario], email_template.subject, html_content
            )

    def enviar_notificacao_relatorio(self):
        log.info(
            "### Iniciando comando para enviar notificações sobre o Relatório Semestral de Teletrabalho"
        )
        email_template_code = "RELATORIO_SEMESTRAL_TELETRABALHO"
        log.info(f">>> Template selecionado: {email_template_code}")
        aprovadores = self.get_aprovadores()
        email_template = self.get_email_template(email_template_code)

        if aprovadores and email_template:
            aprovadores_list = self.lista_aprovadores_compilada(aprovadores)
            log.info(f">>>>> Lista de aprovadores: {aprovadores_list}")
            self.enviar_email_notificacao(email_template, aprovadores)

        elif not aprovadores:
            log.error(
                f"Não há aprovadores de teletrabalho para enviar notificações sobre envio de Relatório Semestral de Teletrabalho!"
            )
        elif email_template is None:
            log.error(
                f"Não foi possível encontrar o Modelo de Email: {email_template_code}!"
            )
