# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime, timedelta
from functools import partial

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger
from engine.mq.models import Task
from rh.dayoff.contrib import has_perm_block_unblock_ap
from rh.dayoff.models import AcquisitionPeriod, Configuration
from rh.models import Servidor

log = getLogger(__name__)


class DAYOFFAcquisitionPeriod(RestfulDRY):

    _model = AcquisitionPeriod

    context = None

    full_text_index = (
        "group_period__title__icontains",
        "group_period__year_reference__icontains",
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.acquisitionperiod.Manage")')

    def model_to_dict(self, instance):
        configurations = Configuration.objects.filter(prescription_days__gt=0)
        if (
            instance.group_period.configuration in configurations
            and instance.attachment_acquisitionperiod
        ):
            prescription_days = instance.group_period.configuration.prescription_days
            for attachment in instance.attachment_acquisitionperiod.all():
                prescription_sum = attachment.date_start + timedelta(
                    days=prescription_days
                )
                # Subtrai do "Saldo Disponível" quando o anexo estiver "Prescrito"
                if attachment.status == 2 and prescription_sum <= datetime.now().date():
                    instance.days_not_booked_cache -= attachment.days_law

        _dict_ = super(DAYOFFAcquisitionPeriod, self).model_to_dict(instance)
        _dict_.update({"icons": instance.icons})
        _dict_.update(
            {
                "unicode_full_group_period": "{} - {}-{}/{}".format(
                    instance.group_period.title,
                    instance.start_date_acquisition.year,
                    instance.end_date_acquisition.year,
                    instance.group_period.period,
                )
            }
        )
        return _dict_

    def extract_params(self, params, signature=[]):
        params_new = {}
        for key in signature:
            if key in params:
                try:
                    params_new.update(
                        {key: json.loads(params[key]) if params[key] != "" else None}
                    )
                except:
                    params_new.update({key: params[key]})
        return params_new

    @login_required("JSON")
    def book(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)

            _data = [
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if extract_params.get("immediate_authorization", False):
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if extract_params.get("mediate_authorization", False):
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            extract_params.update({"context": self.context})

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                activity = inst.book(**extract_params)
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def change(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = self.request.POST.get("acquisition_period", False)

            _data = [
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if extract_params.get("immediate_authorization", False):
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if extract_params.get("mediate_authorization", False):
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            extract_params.update({"context": self.context})

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                activity = inst.change(**extract_params)
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def interrupt(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)

            _data = [
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if extract_params.get("immediate_authorization", False):
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if extract_params.get("mediate_authorization", False):
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                activity = inst.interrupt(**extract_params)
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def suspend(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)

            _data = [
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if extract_params.get("immediate_authorization", False):
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if extract_params.get("mediate_authorization", False):
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                activity = inst.suspend(**extract_params)
                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def cancel(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)

            _data = [
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "activity",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if extract_params.get("immediate_authorization", False):
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if extract_params.get("mediate_authorization", False):
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                activity = inst.cancel(**extract_params)
                message = "não foi cancelada."
                if activity.canceled:
                    message = "cancelada com sucesso."
                message = "%s %s" % (activity.get_type_of_activity_display(), message)
                rst.update(
                    {
                        "success": True,
                        "message": message,
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def file(self, args=[]):
        try:
            task = Task.objects.get(
                uuid=self.request.REQUEST.get("uuid"), owner=self.request.user
            )

            if task.state == "ready":
                filename = "%s/homologacao-%s.csv" % (settings.CACHE_PATH, task.uuid)
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="homologacao-relatorio-%s.csv"' % now
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

    @login_required(type="JSON")
    def release(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            acquisition_period = self.request.POST.get("acquisition_period", False)

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                inst.release()
                rst.update(
                    {
                        "success": True,
                        "message": "Liberação realizada com sucesso.",
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def homologate(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            # TODO: IMPLEMENTAR, homologação em batch e homologação de groupperiod
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)
            attachment = params.get("attachment", None)
            note = params.get("note", True)
            activity = params.get("activity", None)
            scale_homologation = params.get("scale_homologation", False)

            if acquisition_period:
                inst = self.Model.objects.get(pk=acquisition_period)
                inst.homologate(
                    attachment, note, activity, scale_homologation, self.context
                )
                rst.update(
                    {
                        "success": True,
                        "message": "Homologação realizada com sucesso.",
                    }
                )
            else:
                msg = "Período Aquisitivo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def sell(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}

        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", False)
            _data = [
                "days",
                "usufructs_in",
                "modifieds",
                "authorize",
                "attachment",
                "justification",
                "note",
                "activity",
                "scale_homologation",
                "immediate_authorization",
                "mediate_authorization",
            ]
            extract_params = self.extract_params(params, _data)
            if "immediate_authorization" in extract_params:
                extract_params["immediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["immediate_authorization"]
                )
            if "mediate_authorization" in extract_params:
                extract_params["mediate_authorization"] = Servidor.objects.get(
                    pk=extract_params["mediate_authorization"]
                )

            extract_params.update({"context": self.context})

            if acquisition_period and extract_params.get("days", None) is not None:
                inst = self._model.objects.get(pk=acquisition_period)
                activity = inst.sell(**extract_params)

                rst.update(
                    {
                        "success": True,
                        "message": "%s realizada com sucesso."
                        % activity.get_type_of_activity_display(),
                    }
                )
            else:
                msg = "Informe o Período Aquisitivo e a quantidade de dias."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def homologate_batch(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            params = self.request.POST
            acquisition_period = params.get("acquisition_period", None)
            attachment = params.get("attachment", None)
            homologation_date = params.get("homologation_date")
            publication_date = params.get("publication_date")

            if acquisition_period:
                AcquisitionPeriod.homologate_batch(
                    acquisition_period=acquisition_period,
                    homologation_date=homologation_date,
                    publication_date=publication_date,
                    attachment=attachment,
                    context=self.context,
                )
                rst.update(
                    {
                        "success": True,
                        "message": "Homologação iniciada com sucesso, acompanhe pelo gestor de processos.",
                    }
                )
            else:
                msg = "Grupo não informado."
                rst.update({"message": msg})
                raise Exception(msg)
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def block_periods(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            pks = self.request.POST.getlist("pks", [])
            lock = (
                True
                if self.request.POST.get("lock", False).lower() == "true"
                else False
            )

            if has_perm_block_unblock_ap():
                if pks and pks != [""]:
                    AcquisitionPeriod.objects.filter(pk__in=pks).update(
                        modified_at=datetime.now(),
                        modified_by=get_current_user(),
                        blocked=lock,
                    )
                    rst.update(
                        {
                            "success": True,
                            "message": "Bloqueio realizado com sucesso.",
                        }
                    )
                else:
                    msg = "Período aquisitivo não informado."
                    rst.update({"message": msg})
                    raise Exception(msg)
            else:
                msg = "Você não possui permissão para executar esta ação."
                rst.update({"message": msg})
                raise Exception(msg)

        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def run_upgrade_aquisition_period(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            acquisition_period = self.request.POST.getlist("acquisition_period", [])
            AcquisitionPeriod.run_upgrade_aquisition_period(
                acquisition_periods=acquisition_period
            )
            rst.update(
                {
                    "success": True,
                    "message": "Atualização iniciada com sucesso, acompanhe pelo gestor de processos.",
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)


class DAYOFFAcquisitionPeriodEmployee(DAYOFFAcquisitionPeriod):

    context = "employee"

    def get_query(self):
        query = super(DAYOFFAcquisitionPeriodEmployee, self).get_query()
        return query.filter(
            employee=employee_from_user(get_current_user()), blocked=False
        )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.acquisitionperiod.ManageEmployee", {resourceRestful: "DAYOFFAcquisitionPeriodEmployee"})'
        )


class DAYOFFAcquisitionPeriodAdmin(DAYOFFAcquisitionPeriod):

    context = "admin"

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.acquisitionperiod.ManageAdmin", {resourceRestful: "DAYOFFAcquisitionPeriodAdmin"})'
        )

    def get_query(self):
        return super(DAYOFFAcquisitionPeriodAdmin, self).get_query()
