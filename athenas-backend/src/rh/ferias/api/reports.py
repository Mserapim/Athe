# -*- coding: utf-8 -*-

from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.utils import employee_from_user
from rh.models import Lotacao


class FRSCollaboratorReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        employee = employee_from_user(get_current_user())
        workplace_responsible = [
            workplace.get("pk")
            for workplace in Lotacao.objects.filter(responsavel=employee).values("pk")
        ]
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.ferias.reports.Collaborator", {workplace_responsible: %s})'
            % workplace_responsible
        )


class RHHomologationMembrosReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HomologationMembros")')


class RHHomologationEmployeeReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HomologationEmployee")')


class RHSMHolidayScale(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.ferias.holidayScale.HolidayScaleReportManager")'
        )


class FRSHolidayHistoryReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HolidayHistory")')


class FRSPendingHolidayReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.PendingHolidays")')


class FRSHolidaysEnjoyReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HolidaysEnjoyMonth")')


class FRSHolidaysActivityReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HolidaysActivity")')


class FRSHolidayEnjoyedReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HolidayEnjoyed")')


class FRSUnmarkedScalesReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.UnmarkedScales")')


class FRSHolidayStockReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.ferias.reports.HolidayStock")')
