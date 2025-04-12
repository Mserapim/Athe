# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from rh.pvf.models import ShiftManager
from rh.pvf.const import STS_WAI_APPROVER, ONCALL_BONUS_SERVERS
from rh.dayoff.models import AcquisitionPeriod, AcquisitionPeriodAttachment
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.pvf.models import ApproveServerDuty
from standard.models import Choice, EmailTemplate, Item
from common.util.send_email import EmailNotification


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá realizar a criação da solicitação de plantão de servidores. """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.create_request_duty()

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def create_request_duty(self):
        self.conf()
        date = datetime.now().date() - timedelta(days=1)
        log.info(
            f">>> [{DateUtils.datetime_to_str(datetime.now())}] Iniciando a criação da solicitação de plantão de servidores >>>>>>>>>>>>>"
        )
        date_reference_str = Choice.objects.filter(
            app_label="pvf", name="DUTY_START_DATE"
        ).first()
        date_reference = DateUtils.str_to_date(date_reference_str.label)

        shift_requests = ShiftManager.objects.filter(
            end_date__lte=date, end_date__gt=date_reference
        ).exclude(server_duty__isnull=False)
        user = User.objects.get(username="athenas")

        texto_erros = ""
        lista_destinatarios = []
        email_approvers = Item.objects.get(
            configuration__application="vdf", key="notificacao_plantao_servidor"
        ).value
        emails = email_approvers.split(",")
        email_template = self.get_email_template("PLANTOESSERVIDORES_NAO_CRIADOS")

        for email in emails:
            lista_destinatarios.append(
                {
                    "email": email,
                    "nome": str(email),
                },
            )

        for request in shift_requests:
            try:
                request.validate()
                ApproveServerDuty.create(request, user)
            except Exception as err:
                log.error(err)
                texto_erros = (
                    texto_erros
                    + f"""
                    <br>Nome do Plantonista: {str(request.employee)}<br>
                    Lotação do Plantonista: {str(request.workplace)}<br>
                    Data início do Plantão: {str(request.start_date)}<br>
                    Data fim do Plantão: {str(request.end_date)}<br>
                    Responsável pelo cadastro: {str(request.owner)}<br>
                    Motivo: {str(err)}<br>
                """
                )

        if texto_erros != "":
            conteudo = email_template.contents.replace("@Conteudo@", str(texto_erros))
            html_content = render_to_string(
                "util/template_email_basic.html", {"message": conteudo}
            )
            assunto = email_template.subject
            EmailNotification().send_email_default(
                lista_destinatarios, assunto, html_content
            )

        log.info(
            ">>> [{}] Finalizando a criação da solicitação de plantão de servidores".format(
                DateUtils.datetime_to_str(date)
            )
        )

    def get_email_template(self, template_code):
        try:
            return EmailTemplate.objects.get(code=template_code)
        except:
            return None
