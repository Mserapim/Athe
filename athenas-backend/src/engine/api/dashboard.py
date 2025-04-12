# -*- coding: utf-8 -*-
import json

from contrib.controller import DefaultController
from contrib.utils import employee_from_user, getLogger
from rh.utils import format_situacao_funcional as format_position
from common.poll.models import Poll
from standard.models import Choice


log = getLogger(__name__)


class Dashboard(DefaultController):

    def json(self, args=None):
        args = args or []

        employee = employee_from_user(self.request.user, only_active=False)

        self._do_log(employee)

        cfg = {
            "user": {
                "employee": self._get_employee_info(employee),
                "hasToVote": self._has_to_vote(),
            }
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(f"new core.dashboard.Manager({json.dumps(cfg)})")

    def _do_log(self, employee):
        if not employee:
            log.error(
                f"Dashboard: Nenhum servidor associado ao usuário {self.request.user}"
            )
            return

        log.info(f"Dashboard: Servidor: {employee}")
        log.info(f"Dashboard: Servidor é membro: {employee.membro}")
        log.info(f"Dashboard: Servidor está afastado: {employee.afastamento_ativo()}")

    def _is_employee_retired(self, employee):
        return employee and employee.aposentado or False

    def _is_employee_absent(self, employee):
        if Choice.objects.filter(name="VDF_ACCESS_RESTRICTION", active=True, value=1):
            return False

        if employee and (not employee.membro and employee.afastamento_ativo()):
            restriction = self._get_employee_restriction(employee).tipo
            return restriction not in [6, 26, 27, 40]

        return False

    def _get_employee_restriction(self, employee):
        return employee.get_afastamentos()[0].baselicencaafastamento

    def _get_employee_status(self, employee):
        return format_position(
            self._get_employee_restriction(employee).situacao_funcional
        )

    def _get_employee_info(self, employee):
        is_absent = self._is_employee_absent(employee)

        info = {
            "name": employee and employee.pessoa_fisica.nome or "",
            "isRetired": self._is_employee_retired(employee),
            "isAbsent": is_absent,
            "absentReason": is_absent and self._get_employee_status(employee) or "",
        }

        return info

    def _has_to_vote(self):
        polls = Poll.polls_by_user(self.request.user)
        return len(polls) > 0
