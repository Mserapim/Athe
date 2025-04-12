# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, DateUtils
from contrib.controller import DefaultController
from contrib.decorator import login_required
from engine.mq.models import Task
from functools import partial

from rh.models import HoursWorkContract
from rh.models import HoursWorkContractWorkload
from rh.models import EmployeeHoursWorkContractWorkload

from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.conf import settings

import os
import datetime


log = getLogger(__name__)


class RHHoursWorkContract(RestfulDRY):

    _model = HoursWorkContract

    full_text_index = (
        "title__icontains",
        "code__icontains",
        "publication__cache_unicode__icontains",
        "duration_hour__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.hoursworkcontract.Manage")')

    def model_to_dict(self, instance):
        params = super(RHHoursWorkContract, self).model_to_dict(instance)
        params.update(
            {
                "time_start_formated": instance.time_start_formated,
                "time_end_formated": instance.time_end_formated,
                "duration_interval": instance.duration_interval_count,
                "duracao_intervalo_formatado": instance.duracao_intervalo_formatado,
                "jornada_semanal": instance.jornada_semanal,
            }
        )
        return params


class RHHoursWorkContractManager(RHHoursWorkContract):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.hoursworkcontract.manager.Manage")')


class RHHoursWorkContractWorkload(RestfulDRY):

    _model = HoursWorkContractWorkload

    full_text_index = (
        "title__icontains",
        "duration_hour__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.hoursworkcontract.workload.Manage")')


class RHHoursWorkContractWorkloadManager(RHHoursWorkContractWorkload):

    _model = HoursWorkContractWorkload

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.hoursworkcontract.workload.manager.Manage")'
        )


class RHHoursWorkContractWorkloadManagerTab(RHHoursWorkContractWorkload):

    _model = HoursWorkContractWorkload

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.hoursworkcontract.workload.manager.ManageTab")'
        )


class RHEmployeeHoursWorkContractWorkload(RestfulDRY):

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    _model = EmployeeHoursWorkContractWorkload

    exclude_fields = [
        "audittimestampmodel_ptr",
        "auditablemixins_ptr",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.hoursworkcontract.employeeworkload.Manage")'
        )

    @login_required("JSON")
    def apply_employee_workload(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}

        self._read_special_verb()
        try:
            date_start = (
                DateUtils.str_to_date(self.request.PUT.get("date_start"))
                if self.request.PUT.get("date_start")
                else None
            )
            date_end = (
                DateUtils.str_to_date(self.request.PUT.get("date_end"))
                if self.request.PUT.get("date_end")
                else None
            )
            hwc_workload_origin = self.request.PUT.get(
                "hoursworkcontractworkload_origin", None
            )
            if hwc_workload_origin:
                hwc_workload_origin = int(hwc_workload_origin)
            hwc_workload_destiny = int(
                self.request.PUT.get("hoursworkcontractworkload_destiny")
            )
            self._model.apply_employee_workload(
                workplace=self.request.PUT.get("workplace", None),
                date_start=date_start,
                date_end=date_end,
                reapply=self.request.PUT.get("reapply", False),
                hwc_workload_origin=hwc_workload_origin,
                hwc_workload_destiny=hwc_workload_destiny,
                all_employee=self.request.PUT.get("allEmployee", False),
                locality=self.request.PUT.get("locality", None),
            )
        except Exception as err:
            log.exception(err)
            response.update(message="%s" % err.args[0])
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.renderer(response)

    @login_required("JSON")
    def remove_by_date_start(self, args=[]):
        response = {"success": False, "message": "Nada foi feito ainda."}

        self._read_special_verb()
        try:
            date_start = (
                DateUtils.str_to_date(self.request.POST.get("date_start"))
                if self.request.POST.get("date_start")
                else None
            )
            # date_end = DateUtils.str_to_date(self.request.POST.get('date_end')) if self.request.POST.get('date_end') else None
            hours_work_contract_workload = self.request.POST.get(
                "hours_work_contract_workload", None
            )
            self._model.remove_by_date_start(
                date_start=date_start,
                # date_end=date_end,
                hours_work_contract_workload=hours_work_contract_workload,
            )
        except Exception as err:
            log.exception(err)
            response.update(message="%s" % err.args[0])
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.renderer(response)

    @login_required(type="JSON")
    def file(self, args=[]):
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                filename = "%s/escalas-%s.csv" % (settings.CACHE_PATH, task.uuid)
                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="escala_%s"'
                    % DateUtils.datetime_to_str(datetime.datetime.now())
                )
                with open(os.path.join(filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)
                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo para o usuário logado.</h1>"
            )


class RHEmployeeHoursWorkContractWorkloadWindow(DefaultController):

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.hoursworkcontract.employeeworkload.specialize.WindowApplyWorkload")'
        )
