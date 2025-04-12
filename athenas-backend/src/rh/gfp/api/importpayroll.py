# -*- coding: utf-8 -*-

import json

from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.gfp.models import Periodo as Period
from rh.gfp.models import Folha
from rh.gfp.tasks import import_payroll
from rh.gfp.tools.import_payroll import import_payments

log = getLogger(__name__)


class GFPImportPayroll(DefaultController):

    def renderer(self, data):
        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(data))

    def check_permission(self, user, action, app_label, object_name):
        perm = "%(app_label)s.%(action)s_%(object_name)s" % vars()
        perm = perm.lower()

        log.info("check %s permission for %s" % (perm, user))
        if user.has_perm(perm) is True:
            log.info("user %s has permission %s" % (user, perm))
            return True
        else:
            log.warn("permission %s dained for %s" % (perm, user))
            return False

    @login_required(type="JSON")
    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}
        try:
            can = self.check_permission(
                self.request.user,
                "change",
                Folha._meta.app_label,
                Folha._meta.object_name,
            )
            if can is False:
                rst.update(
                    success=False,
                    message="Você não tem permissão para alterar %s."
                    % Folha._meta.object_name,
                )
            else:
                Task.start(
                    import_payroll,
                    payroll_type=int(self.request.POST.get("payroll_type")),
                    period=int(self.request.POST.get("period")),
                    user=get_current_user().pk,
                )
                rst.update(
                    success=True,
                    message="Importação iniciada com sucesso, você será avisado quando o mesmo for concluído.",
                )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
