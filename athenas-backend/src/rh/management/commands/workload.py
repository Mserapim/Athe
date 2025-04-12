import datetime

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.template.loader import render_to_string

from common.util.send_email import EmailNotification
from rh.models import Servidor, MovimentacaoTeletrabalho
from standard.models import EmailTemplate


log = getLogger("db")


class Command(BaseCommand):
    help = """Esse Comando irá disparar emails para os Servidores informando para eles enviarem a
    folha ponto, utilizando o modelo de emails.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--opentosend",
            action="store_true",
            dest="opentosend",
            help="Envia email com informativo que está aberto o período, primeiro dia do mês.",
        )
        parser.add_argument(
            "-l",
            "--lastdaytosend",
            action="store_true",
            dest="lastdaytosend",
            help="Envia email com informativo que é o último dia para envio, quinto dia útil do mês.",
        )

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
        if options["opentosend"]:
            self.set_user_to_job("job_send_info_workload")
            self.send_info_workload("ENTREGA_FOLHA_PONTO_DIA_1")
        if options["lastdaytosend"]:
            self.set_user_to_job("job_send_info_workload")
            self.send_info_workload("ENTREGA_FOLHA_PONTO_ULTIMO_DIA")

    def get_employees(self):
        employees = []

        q_employees = Servidor.objects.filter(
            type_by_possession__in=["EFE", "ECM", "CMS", "RCM", "EFC", "EFE", "EST"]
        )

        ## lógica abaixo comentada - lógica remove da lista os servidores em teletrabalho

        # dt_today = datetime.datetime.today().date()
        # for employee in q_employees:
        #     q_movteletrab = MovimentacaoTeletrabalho.objects.filter(
        #         servidor=employee,
        #         data_inicio__lte=dt_today,
        #         data_fim__gte=dt_today,
        #     )

        #     if employee.is_ativo and not q_movteletrab.exists():
        #         employees.append(employee)

        [employees.append(employee) for employee in q_employees if employee.is_ativo]
        return employees

    def get_email_template(self, template_code):
        try:
            return EmailTemplate.objects.get(code=template_code)
        except:
            return None

    def send_info_email(self, email_template, employees):
        log.info(f">>> Quantidade de servidores: {len(employees)}")
        for employee in employees:
            email_to = (
                employee.user.email
                if employee.user.email
                else employee.pessoa_fisica.email
            )
            receiver = {
                "email": email_to,
                "nome": employee.pessoa_fisica.social_name,
                "idUsuario": employee.id_usuario_mastiff,
            }

            message = email_template.contents
            message = message.replace(
                "%EMPLOYEE_NAME%", employee.pessoa_fisica.social_name
            )
            html_content = render_to_string(
                "util/template_email_basic.html", {"message": message}
            )

            log.info(f">>> Enviando email para: {email_to}")
            EmailNotification().send_email_default(
                [receiver], email_template.subject, html_content
            )

    def send_info_workload(self, email_template_code):
        log.info(
            "### Iniciando comando para enviar emails de informativo sobre Folha Ponto"
        )
        log.info(f">>> Template selecionado: {email_template_code}")
        employees = self.get_employees()
        email_template = self.get_email_template(email_template_code)

        if employees and email_template:
            self.send_info_email(email_template, employees)
        elif not employees:
            log.error(
                f"Não há servidores para enviar notificações sobre envio de Folha Ponto!"
            )
        elif email_template is None:
            log.error(
                f"Não foi possível encontrar o Modelo de Email: {email_template_code}!"
            )
