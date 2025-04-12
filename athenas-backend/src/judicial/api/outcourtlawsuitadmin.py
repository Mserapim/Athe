# -*- coding: utf-8 -*-
import json

from contrib.newrest import Restful
from contrib.utils import getLogger
from judicial.models import OutCourtLawsuit
from judicial.api.outcourtlawsuit import EJudOutCourtLawsuit
from contrib.nil import nil_display
from contrib.nil import nil_pk, nil_unicode
from django.template import loader
from django.conf import settings
from contrib.utils import DateUtils
from django.utils.safestring import mark_safe
from default.views import Application


log = getLogger(__name__)


class EJudOutCourtLawsuitAdmin(EJudOutCourtLawsuit):

    def json(self, args=[]):
        self.response.write('Ext._create("judicial.outcourtlawsuit.Manage")')

    def get_query(self):
        query = super(EJudOutCourtLawsuit, self).get_query()

        if not self.request.user.has_perm("judicial.outcourtlawsuitadmin"):
            query = query.none()

        return query

    def all_authorized_lawsuits(self):
        return self.get_query()

    def check_permission_admin(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}

        try:
            rst.update(
                success=True,
                is_admin=self.request.user.has_perm("judicial.outcourtlawsuitadmin"),
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)


class EJudOutCourtLawsuitReportActivity(EJudOutCourtLawsuit):

    def json(self, args=[]):
        self.response.write('Ext._create("judicial.reports.LawsuitLogReportPanel")')
