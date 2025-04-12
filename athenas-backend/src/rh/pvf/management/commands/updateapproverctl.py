# -*- coding: utf-8 -*-
import inspect

from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.pvf.models import PortalRequest, SendingTelework
from rh.pvf.const import STS_WAI_APPROVER


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá realizar envio de email do portal vida funcional para os substitutos diariamente, enquanto não derem
    ciência da substituição que foram designados. """

    def handle(self, *args, **options):
        self.set_user_to_job("job_updateapproverctl_pvf_update_approver")
        self.pvf_update_approver()

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário  "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def pvf_update_approver(self):
        dt_hr_inicio = datetime.now()
        log.info(
            f">>> [{DateUtils.datetime_to_str(dt_hr_inicio)}] Iniciando atualização de aprovadores no Portal Vida Funcional >>>>>>>>>>>>>"
        )

        requests_with_approvers = PortalRequest.objects.filter(status=STS_WAI_APPROVER)
        for request in requests_with_approvers:
            try:
                if hasattr(request, "sendingtelework"):
                    telework_approver = (
                        SendingTelework.objects.filter(pk=request.pk)
                        .first()
                        .work_plan.aprovador
                    )
                    if request.approver != telework_approver:
                        request.approver = telework_approver
                elif request.approver:
                    if request.approver != request.get_immediate_boss(request.employee):
                        request.approver = request.get_immediate_boss(request.employee)
                else:
                    raise ObjectDoesNotExist(
                        f"A requisição {request} não possui aprovador cadastrado."
                    )
                request.save()
            except ObjectDoesNotExist as err:
                log.error(err)
            except Exception as err:
                log.error(
                    f"A atualização do aprovador da requisição {request} - ID nº {request.id}, apresentou o seguinte erro:"
                )
                log.error(err)

        dt_hr_fim = datetime.now()
        log.info(
            ">>> [{}] Finalizando a atualização de aprovadores".format(
                DateUtils.datetime_to_str(dt_hr_fim)
            )
        )
