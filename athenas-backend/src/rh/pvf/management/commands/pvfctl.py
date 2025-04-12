# -*- coding: utf-8 -*-

from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
from rh.pvf.models import PortalRequest
from common.util.send_email import EmailNotification
from rh.pvf.const import STS_WAI_SUBS_SCIENCE
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá realizar envio de email do portal vida funcional para os substitutos diariamente, enquanto não derem
    ciência da substituição que foram designados. """

    # def add_arguments(self, parser):
    #     parser.add_argument('-m', '--send_mail', action='store_true', dest="send_mail", help="Envia emails!")
    #     parser.add_argument('-a', '--all', action='store_true', dest="all", help="Realiza todas as ações!")

    # def __init__(self, *args, **kargs):
    #     BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        # if options['send_mail'] or options['all']:
        #     self.send_mail()
        self.send_mail()

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def send_mail(self):
        date = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(date)}] Iniciando envio de emails >>>>>>>>>>>>>"
        )
        solicitations = PortalRequest.objects.filter(status=STS_WAI_SUBS_SCIENCE)
        for solicitation in solicitations:
            if solicitation.days_awaiting_approval > 0:
                try:
                    subject = "Portal Vida Funcional - Protocolo ID: {}".format(
                        solicitation.id
                    )
                    message = "O pedido abaixo necessita da sua manifestação/ciência."
                    type_of_request = solicitation.type_of_request
                    code = solicitation.id
                    date_request = solicitation.date.strftime("%d/%m/%Y")
                    requester = solicitation.employee.pessoa_fisica.social_name
                    approver_email = [
                        {
                            "email": (
                                solicitation.approver.pessoa_fisica.email_institucional
                                if solicitation.approver.pessoa_fisica.email_institucional
                                else solicitation.approver.pessoa_fisica.email
                            ),
                            "nome": solicitation.approver.pessoa_fisica.social_name,
                            "idUsuario": solicitation.approver.id_usuario_mastiff,
                        },
                    ]
                    EmailNotification().send_email_pvf(
                        subject=subject,
                        message=message,
                        solicitation=type_of_request,
                        code=str(code),
                        date=str(date_request),
                        requester=requester,
                        receivers=approver_email,
                        receivers_rh_person_ids=None,
                    )
                except Exception as err:
                    log.error(err)

        log.info(
            ">>> [%s] Finalizando o envio de emails >>>>>>>>>>>>>"
            % DateUtils.datetime_to_str(date)
        )
