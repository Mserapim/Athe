# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.controller import DefaultController
from contrib.utils import getLogger
from judicial.models import OfficerDiligence, County, Diligence
from contrib.utils import employee_from_user
from contrib.nil import nil_pk, nil_unicode, nil_display
from contrib.middleware import get_current_user
from django.db import transaction

log = getLogger(__name__)


class EJudOfficerDiligenceDashboard(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            "Ext._create('judicial.diligences.officer.DiligenceDashboard')"
        )


class EJudOfficerDiligence(Restful):

    _model = OfficerDiligence

    full_text_index = ("officer_diligence__pessoa_fisica__nome__icontains",)

    force_upper = False

    def get_params(self, *args, **kargs):
        params = super(EJudOfficerDiligence, self).get_params(*args, **kargs)

        if "officer_diligence" in params:
            if params.get("officer_diligence") != "":
                field = getattr(self.Model, "officer_diligence")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(
                        officer_diligence=query.get(pk=params.get("officer_diligence"))
                    )
                except Exception:
                    params.pop("officer_diligence")
            else:
                params.update(officer_diligence=None)

        if "is_removed" in params:
            params.update(is_removed=params.get("is_removed", "off").lower() == "on")

        return params

    def accept_diligence(self, args=[]):
        rst = {"message": "nada foi feito ainda", "success": False}

        try:
            employee = employee_from_user(self.request.user)
            officer = self.Model.objects.get(officer_diligence=employee)

            with transaction.atomic():
                for diligence in Diligence.objects.filter(
                    pk__in=self.request.POST.getlist("pkset")
                ):
                    officer.accept_diligence(diligence)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Diligencia aceita com sucesso.")

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.diligences.OfficerDiligence')")

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        rst.update(
            icons_status=instance.icons_status,
            score=instance.score,
            status=instance.status,
            status_display=nil_display(instance, "status", None),
            officer_diligence=nil_pk(instance.officer_diligence, None),
            officer_diligence_unicode=nil_unicode(instance.officer_diligence, None),
            work_county=nil_pk(instance.work_county, None),
            work_county_unicode=nil_unicode(instance.work_county, "Indefinido"),
            is_removed=instance.is_removed,
            is_removed_display="SIM" if instance.is_removed else "NÃO",
        )

        return rst

    def get_query(self, *args, **kwargs):
        query = self.Model.objects.none()

        if self.request.user.is_superuser or self.request.user.has_perm(
            "judicial.outcourtlawsuitadmin"
        ):
            query = self.Model.objects.filter()
        else:
            employee = employee_from_user(get_current_user())

            if len(employee.work_locations) > 0:
                counties = County.objects.filter(
                    locations__in=[wl.localidade for wl in employee.work_locations]
                )
                query = self.Model.officies_working_in_counties(counties).order_by(
                    "officer_diligence__pessoa_fisica__nome"
                )

        return query
