# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.gfp.planoconta.models import (
    ProvisionPlan,
    ProvisionEmployee,
    Provision,
    ProvisionManager,
)
from rh.gfp.calcs.mpto.provisions import VacationGenerator, ChristmasGenerator
from contrib.decorator import login_required
from contrib.middleware import set_current_user
from engine.models import TaskSession
from contrib.utils import get_json_engine, Locker
import threading

log = getLogger(__name__)
json = get_json_engine()


class PCProvisionPlan(RestfulDRY):

    _model = ProvisionPlan

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.provisionplan.ProvisionPlanManage")')


class PCProvisionManager(RestfulDRY):

    _model = ProvisionManager

    def get_icons(self, instance):
        obj = []
        obj_status = {
            "iconCls": "icon-core icon-core-blank",
            "title": instance.get_status_display(),
        }
        if instance.status == 1:
            obj_status.update({"iconCls": "icon-core icon-core-run"})
        elif instance.status == 2:
            obj_status.update({"iconCls": "icon-core icon-core-waiting"})
        elif instance.status == 3:
            obj_status.update({"iconCls": "icon-fopag icon-closed-padlock"})
        elif instance.status == 4:
            obj_status.update({"iconCls": "icon-fopag icon-stamp-arrow"})

        obj.append(obj_status)

        return obj

    def model_to_dict(self, instance):
        _dict = super(PCProvisionManager, self).model_to_dict(instance)
        _dict["icons"] = self.get_icons(instance)
        log.debug(_dict)
        return _dict

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.gfp.provisionplan.ProvisionManagerManage")'
        )

    def generateProvisionTask(self, generator, task=None):

        lock_file = Locker.create_lock("apply_model")
        task = TaskSession.start_execution(generator.title) if not task else task
        log.debug("TASK: GENERATE PROVISION")
        try:
            generator.create_periods(task=task)
        except Exception as e:
            task.info(e, 3)

        task.finish_execution()
        Locker.remove_lock(lock_file)

    @login_required("JSON")
    def generateProvision(self, args=[]):
        obj = {"success": True, "message": "Gerando provisionamento."}

        provision_type = self.request.POST.get("provisionplan")
        month = self.request.POST.get("month")
        year = self.request.POST.get("year")
        # employee = Servidor.objects.get(pk=self.request.POST.get('employee')) if

        generator = None
        if int(provision_type) == 1:
            generator = VacationGenerator(int(year), int(month), int(provision_type))
        if int(provision_type) == 2:
            generator = ChristmasGenerator(int(year), int(month), int(provision_type))

        def process(request, generator, log):
            # SETTING USER FOR LOCAL

            set_current_user(request.user)
            log.debug("INIT PROCESS PROVISIONS...")
            if generator:
                self.generateProvisionTask(generator)

        t = threading.Thread(target=process, args=(self.request, generator, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def recalculateProvision(self, args=[]):
        obj = {"success": True, "message": "Recalculando provisionamento."}

        provision_pk = self.request.POST.get("provision_pk")

        try:
            pm = ProvisionManager.objects.get(pk=provision_pk)
        except Exception as e:
            obj.update({"success": False, "message": e})

        generator = None
        if pm and int(pm.provision_plan.type_provision) == 1:
            generator = VacationGenerator(
                pm.reference_year,
                pm.reference_month,
                pm.provision_plan.type_provision,
                [pm.pension_system],
            )
        if pm and int(pm.provision_plan.type_provision) == 2:
            generator = ChristmasGenerator(
                pm.reference_year,
                pm.reference_month,
                pm.provision_plan.type_provision,
                [pm.pension_system],
            )

        def process(request, generator, log):
            # SETTING USER FOR LOCAL

            set_current_user(request.user)
            log.debug("INIT PROCESS PROVISIONS...")
            if generator:
                self.generateProvisionTask(generator)

        t = threading.Thread(target=process, args=(self.request, generator, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def update_status_provision(self, args=[]):

        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            pm = ProvisionManager.objects.get(pk=int(self.request.POST.get("pk")))
            pm.change_status(int(self.request.POST.get("status")))
        except ProvisionManager.DoesNotExist:
            obj.update(message="Não foi possível localizar a provisão desejada.")
        except Exception as e:
            obj.update(message=str(e))
        else:
            obj.update(success=True)
            obj.update(
                provision={"pk": pm.pk, "description": str(pm), "status": pm.status}
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class PCProvisionEmployee(RestfulDRY):

    _model = ProvisionEmployee

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "info__icontains",
        "employee__matricula__iexact",
        "employee__pessoa_fisica__nome__icontains",
    )


class PCProvision(RestfulDRY):

    _model = Provision

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "provision_employee__info__icontains",
        "provision_employee__employee__matricula__iexact",
        "provision_employee__employee__pessoa_fisica__nome__icontains",
    )
