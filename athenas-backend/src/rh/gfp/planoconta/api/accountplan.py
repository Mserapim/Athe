# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.planoconta.models import Plano as Plan, PlanoConta as AccountPlan
from rh.gfp.models import FolhaTipo
from contrib.decorator import login_required
from contrib.utils import get_json_engine
from django.db import transaction

log = getLogger(__name__)
json = get_json_engine()


class PCPlan(RestfulDRY):

    _model = Plan

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.accountplan.PlanManage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update({"icons": self.get_icons(instance)})

        return rst

    def get_icons(self, instance):
        obj = []
        obj_tipo = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_tipo_display(),
        }

        if instance.tipo == 1:
            obj_tipo.update({"iconCls": "icon-core icon-core-calendar-plus"})
        elif instance.tipo == 2:
            obj_tipo.update({"iconCls": "icon-fopag icon-cash"})
        elif instance.tipo == 3:
            obj_tipo.update({"iconCls": "icon-fopag icon-blueprint-pencil"})
        elif instance.tipo == 4:
            obj_tipo.update({"iconCls": "icon-fopag icon-table-plus"})
        elif instance.tipo == 5:
            obj_tipo.update({"iconCls": "icon-fopag icon-truck"})
        elif instance.tipo == 6:
            obj_tipo.update({"iconCls": "icon-fopag icon-user-detective"})
        elif instance.tipo == 7:
            obj_tipo.update({"iconCls": "icon-fopag icon-cash"})
        elif instance.tipo == 8:
            obj_tipo.update({"iconCls": "icon-core icon-core-users"})

        obj.append(obj_tipo)

        return obj

    def list_payroll_type(self, args=[]):
        obj = {
            "root": [
                {"pk": f.pk, "description": str(f)}
                for f in FolhaTipo.objects.filter(ativo=True).order_by("titulo")
            ]
        }
        obj.get("root").insert(0, {"pk": 0, "description": "TODAS"})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def list_year_calendar(self, args=[]):
        obj = {}
        result = []

        for plan in (
            Plan.objects.order_by("-ano_calendario").values("ano_calendario").distinct()
        ):
            result.append(
                {
                    "year": plan.get("ano_calendario"),
                    "description": "Ano Calendário %d" % plan.get("ano_calendario"),
                }
            )

        obj.update(result=result)
        self.response.write(json.encode(obj))

    def copy_year_calendar(self, args=[]):
        obj = {"success": False, "message": "Não foi possível transportar nenhum plano"}
        q_plans = Plan.objects.all()
        plans_ids = [p for p in self.request.POST.getlist("plan") if p]
        log.debug("plans_ids: %s" % plans_ids)
        if plans_ids:
            q_plans = q_plans.filter(pk__in=plans_ids)
        year_calendar_src = self.request.POST.get("year_calendar_src")
        if year_calendar_src:
            q_plans = q_plans.filter(ano_calendario=year_calendar_src)
        type_payroll_src = self.request.POST.get("type_payroll_src")
        if type_payroll_src:
            q_plans = q_plans.filter(folha_tipo=type_payroll_src)

        year_calendar_trg = self.request.POST.get("year_calendar_trg")
        type_payroll_trg = (
            FolhaTipo.objects.get(pk=self.request.POST.get("type_payroll_trg"))
            if self.request.POST.get("type_payroll_trg")
            else None
        )

        plans_copied = Plan.copy_ano_calendario(
            plans=q_plans,
            year_from=year_calendar_src,
            year_to=year_calendar_trg,
            type_payroll_from=type_payroll_src,
            type_payroll_to=type_payroll_trg,
        )

        if not q_plans or not plans_copied:
            obj.update(message="Nenhum plano para transportar!")
        else:
            obj.update(success=True)
            obj.update(message="Planos transportados com sucesso!")
        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PCAccountPlan(RestfulDRY):

    _model = AccountPlan

    def get_icons(self, instance):
        obj = []
        obj_tipo = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_tipo_display(),
        }

        if instance.tipo == 1:
            obj_tipo.update({"iconCls": "icon-fopag icon-user-active"})
        elif instance.tipo == 2:
            obj_tipo.update({"iconCls": "icon-fopag icon-user-inactive"})
        elif instance.tipo == 3:
            obj_tipo.update({"iconCls": "icon-fopag icon-user-timer"})

        obj.append(obj_tipo)

        obj_finalidade = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_finalidade_display(),
        }

        if instance.finalidade == 1:
            obj_finalidade.update({"iconCls": "icon-fopag icon-notebook-plus"})
        elif instance.finalidade == 2:
            obj_finalidade.update({"iconCls": "icon-fopag icon-notebook-minus"})

        obj.append(obj_finalidade)

        return obj

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.accountplan.AccountPlanManage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update({"icons": self.get_icons(instance)})

        return rst
