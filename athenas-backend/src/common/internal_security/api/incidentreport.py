# -*- coding: utf-8 -*-
from contrib.nil import nil_unicode
from contrib.newrest import RestfulDRY
from contrib.middleware import get_current_user
from contrib.utils import getLogger, employee_from_user, person_from_user
from common.internal_security.models import IncidentReport


log = getLogger(__name__)


class ISecIncidentReport(RestfulDRY):

    _model = IncidentReport

    force_upper = False

    def get_query(self):
        query = super(ISecIncidentReport, self).get_query()
        user = get_current_user()

        if user.has_perm("internal_security.can_admin_incident"):
            log.info("IncidentReport: %s is Admin", user)
        elif user.has_perm("internal_security.can_reginal_admin_incident"):
            log.info("IncidentReport: %s is Reginal Admin", user)
            employee = employee_from_user(user)
            if employee:
                locations = employee.work_locations.values("localidade")
                query = query.filter(places__place__localidade__in=locations)
                log.debug(query.count())
            else:
                log.info("IncidentReport: %s is bad Regional Admin", user)
                return query.none()
        else:
            log.info("IncidentReport: %s is client", user)
            query = query.filter(reported_by=user)

        return query

    def can_view_panic_button(self, args=[]):
        rst = {"success": False}
        user = get_current_user()

        if user.has_perm("internal_security.can_view_panic_button"):
            rst.update(success=True)

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = super(ISecIncidentReport, self).model_to_dict(instance)

        employee = employee_from_user(instance.reported_by)

        if employee:
            rst.update(
                employee=employee.pk, employee_unicode=str(employee.pessoa_fisica)
            )

        rst.update(
            received_by_person=nil_unicode(
                person_from_user(instance.received_by), None
            ),
            closed_by_person=nil_unicode(person_from_user(instance.closed_by), None),
            is_received=instance.is_received,
            reported_at_formated=instance.reported_at.strftime("%d/%m/%y %H:%M"),
            type_finish_unicode=nil_unicode(instance.get_type_finish_display(), ""),
        )

        return rst

    def report(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda"}
        try:
            user = get_current_user()
            report = self.Model.objects.filter(
                reported_by=user, received_by__isnull=True
            )
            if report.exists():
                incident = report.first()
                incident.increment_amount_click()
            else:
                self.Model.objects.create()
        except Exception as e:
            log.exception(e)
            rst.update(message="Falha ao enviar a solicitação.")
        else:
            rst.update(success=True, message="Solicitação em andamento.")

        self.renderer(rst)

    def render_incident_report(self, args=[]):
        rst = {"success": False, "message": "não foi implementado"}

        oid = args[0] if args else 0

        try:
            rst.update(
                success=True,
                message="Dados processados com sucesso",
                rendered=self.Model.objects.get(pk=oid).rendered,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def receive(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}
        self._read_special_verb()

        try:
            oid = self.request.PUT.get("pk", 0)
            incident = self.Model.objects.get(pk=oid)
            incident.receive()
        except Exception as e:
            log.exception(e)
            response.update(message=e.message)
        else:
            response.update(success=True, message="Incidente recebido com sucesso.")

        self.renderer(response)

    def finish(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}
        self._read_special_verb()

        try:
            oid = self.request.PUT.get("pk", 0)
            type_finish = self.request.PUT.get("type_finish", 0)
            incident = self.Model.objects.get(pk=oid)
            incident.save()
            incident.finish(type_finish)
        except Exception as e:
            log.exception(e)
            response.update(message=e.message)
        else:
            response.update(success=True, message="Incidente finalizado com sucesso.")

        self.renderer(response)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.internalSecurity.incidentReport.Manage")'
        )
