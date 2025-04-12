# -*- coding: utf-8 -*-
import collections

from django.template.defaultfilters import slugify

from contrib.newrest import RestfulTree
from contrib.nil import nil_pk, nil_unicode
from contrib.utils import employee_from_user, getLogger
from default.views import Application
from engine import models as engine_models

log = getLogger(__name__)


class ENGApplicationRestful(RestfulTree):

    _model = engine_models.Application

    folder_index = "father"

    force_upper = False

    def get_params(self, *args, **kwargs):
        params = super(ENGApplicationRestful, self).get_params(*args, **kwargs)

        if "father" in params:
            if params.get("father") != "":
                field = getattr(self.Model, "father")

                # mater compatibilidade com django-1.4.x
                get_queryset = field.get_queryset
                query = get_queryset()

                try:
                    params.update(father=query.get(pk=params.get("father")))
                except Exception as e:
                    params.update(father=None)
            else:
                params.update(father=None)

        if "active" in params:
            params.update(active=params.get("active", "off").lower() == "on")

        return params

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("engine.ApplicationManage")')

    def model_to_dict(self, inst):
        rst = super(ENGApplicationRestful, self).model_to_dict(inst)

        rst.update(
            father=nil_pk(inst.father, None),
            father_unicode=nil_unicode(inst.father, None),
            icon=inst.icon,
            title=inst.title,
            active=inst.active,
        )

        return rst

    def model_to_node(self, node):
        return {
            "text": node.title,
            "iconCls": (
                "icon-%s" % slugify(node.icon.replace(".png", "")) if node.icon else ""
            ),
            "id": str(node.pk),
            "path": getattr(node, "path", None),
            "leaf": getattr(node, "leaf", False),
        }

    def __get_employee_restriction(self):
        employee = employee_from_user(self.request.user)
        return employee.get_afastamentos()[0].baselicencaafastamento

    def __is_employee_removed(self):
        employee = employee_from_user(self.request.user)

        if employee and (not employee.membro and employee.afastamento_ativo()):
            restriction = self.__get_employee_restriction().tipo
            return restriction not in [6, 26, 27, 40]
        return False

    def employee_portal_menu(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda"}

        try:

            key = "portal do servidor"
            if self.__is_employee_removed():
                key = f"{key} afastado"

            root = self._model.objects.get(title__iexact=key)
            menu_items = Application(self.request, self.response).get_leaf_menu(root)
        except Exception as e:
            log.exception(e)
        else:
            obj = dict(
                success=True,
                total=len(menu_items),
                collection=menu_items,
                message="Concluído com sucesso",
            )

        self.renderer(obj)
