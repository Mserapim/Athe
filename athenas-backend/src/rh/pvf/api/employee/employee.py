# -*- coding: utf-8 -*-
from contrib.utils import getLogger, employee_from_user
from contrib.newrest import RestfulDRY
from rh.api.employee import RHEmployeeRestful
from django.db.models import Q
from contrib.middleware import get_current_user
from rh.pvf.const import (
    REQUEST_STEP_GROUP,
    GROUPS_PVF,
    REQUEST_ACT_DEFER,
    REQUEST_ACT_INDEFER,
    REQUEST_ACT_SCIENCE,
    REQUEST_ACT_ANNOTATION,
    REQUEST_ACT_EFFECTIVENESS,
    REQUEST_ACT_CANCEL,
    REQUEST_STEP,
)

log = getLogger(__name__)


class PVFEmployeeRestful(RHEmployeeRestful):

    def get_employee_approver(self):
        """Retorna o(s) grupo(s) em que o servidor está vinculado"""
        employee = employee_from_user(get_current_user())
        groups = {}
        for group in employee.user.groups.all():
            groups[group.name] = group.name

        return groups

    def group_list(self):
        """Retorna uma lista dos steps relacionados aos grupos de aprovação VDF"""
        groups = self.get_employee_approver()
        groups_list = []
        for group in groups:
            groups_list.append(REQUEST_STEP_GROUP.get(group, 0))

        return groups_list

    def group_list_all(self):
        """Retorna uma lista de todos eteps VDF"""
        groups_list = []
        for group in REQUEST_STEP:
            groups_list.append(REQUEST_STEP.get(group, 0))

        return groups_list

    def belongs_group_dgp(self):
        """Verifica se o servidor pertence ao grupo Gerência de Membros ou Servidores ou Auditoria"""
        groups = self.get_employee_approver()
        for group in groups:
            if group in [GROUPS_PVF["GS"], GROUPS_PVF["GM"], GROUPS_PVF["AUDIT"]]:
                return group

        return ""

    def get_query(self):
        query = super(PVFEmployeeRestful, self).get_query()
        if not self.belongs_group_dgp():
            return query.filter(
                Q(ativo=True),
                Q(
                    portal_request_employee__approver__pk=employee_from_user(
                        get_current_user()
                    ).pk
                )
                | Q(portal_request_employee__step_current__in=self.group_list())
                | Q(
                    portal_request_employee__portalrequesthistory__group__in=list(
                        self.get_employee_approver()
                    )
                )
                | Q(
                    portal_request_employee__portalrequesthistory__user=get_current_user()
                )
                & Q(
                    portal_request_employee__portalrequesthistory__action__in=[
                        REQUEST_ACT_DEFER,
                        REQUEST_ACT_INDEFER,
                        REQUEST_ACT_SCIENCE,
                        REQUEST_ACT_ANNOTATION,
                        REQUEST_ACT_EFFECTIVENESS,
                    ]
                ),
            ).distinct()
        else:
            groups = self.group_list_all()
            return query.filter(
                ativo=True, portal_request_employee__step_current__in=groups
            ).distinct()

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.employee.Manage")')
