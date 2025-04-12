# -*- coding: utf-8 -*-
from contrib.decorator import login_required
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.configuration.models import ConfigReport
from standard.models import Choice
from django.contrib.auth.models import Group
from contrib.middleware import get_current_user


log = getLogger(__name__)

SQL = 3


class ConfigReportRestful(RestfulDRY):

    _model = ConfigReport

    full_text_index = (
        "pk__icontains",
        "text__icontains",
    )

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        _dict_.update(
            {
                "formula": (
                    "Consultar sql via banco."
                    if instance.type_formula == SQL
                    else instance.formula
                )
            }
        )

        return _dict_

    def is_permission_sql(self):
        return False

    @login_required("JSON")
    def include_register(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            pk = self.request.POST.get("pk")
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                config = ConfigReport.objects.get(pk=pk)
                ConfigReport.include_register(config)
                rst = {
                    "success": True,
                    "message": "Procedimento realizado com sucesso.",
                }
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def exclude_register(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            pk = self.request.POST.get("pk")
            can = self.check_permission(
                self.request.user,
                "change",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para alterar %s."
                    % self.Model._meta.object_name
                )
            else:
                config = ConfigReport.objects.get(pk=pk)
                ConfigReport.exclude_register(config)
                rst = {
                    "success": True,
                    "message": "Procedimento realizado com sucesso.",
                }
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.configuration.ConfigReportManage", {is_permission_sql:"%s"})'
            % (self.is_permission_sql())
        )
