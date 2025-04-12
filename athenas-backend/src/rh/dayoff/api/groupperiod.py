# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
from functools import partial

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseNotFound

from contrib.decorator import login_required
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from engine.mq.models import Task
from rh.dayoff.contrib import has_perm_block_unblock_ap
from rh.dayoff.models import AcquisitionPeriod, GroupPeriod

log = getLogger(__name__)


class DAYOFFGroupPeriod(RestfulDRY):

    _model = GroupPeriod

    full_text_index = (
        "title__icontains",
        "year_reference__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.groupperiod.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(DAYOFFGroupPeriod, self).model_to_dict(instance)
        _dict_.update({"icons": instance.icons})
        return _dict_

    @login_required(type="JSON")
    def release(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            group_period = self.request.POST.get("group_period", False)

            if group_period:
                inst = self.Model.objects.get(pk=group_period)
                AcquisitionPeriod.release_batch(group_id=inst.pk)

                rst.update(
                    {
                        "success": True,
                        "message": "Liberação iniciada com sucesso, acompanhe pelo gestor de processos.",
                    }
                )
            else:
                raise Exception("Grupo não informado.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required(type="JSON")
    def generate_all_acquisition_periods(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            group_period = self.request.POST.get("group_period", False)
            create_or_update = self.request.POST.get("create_or_update")

            if group_period:
                inst = self.Model.objects.get(pk=group_period)
                inst.generate_acquisition_periods(create_or_update)

                rst.update(
                    {
                        "success": True,
                        "message": "Geração de período aquisitivo iniciado com sucesso.",
                    }
                )
            else:
                raise Exception("Grupo não informado.")
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
            group_period = self.request.POST.get("group_period", False)
            homologation_date = self.request.POST.get("homologation_date")
            publication_date = self.request.POST.get("publication_date")
            attachment = self.request.POST.get("attachment", None)

            if group_period:
                AcquisitionPeriod.homologate_batch(
                    group=group_period,
                    homologation_date=homologation_date,
                    publication_date=publication_date,
                    attachment=attachment,
                    scale_homologation=True,
                    context="admin",
                )
                rst.update(
                    {
                        "success": True,
                        "message": "Homologação iniciada com sucesso, acompanhe pelo gestor de processos.",
                    }
                )
            else:
                raise Exception("Grupo não informado.")
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err)})
        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def download_file(self, args=[]):
        cache_path = os.path.join(settings.CACHE_PATH, self.request.GET.get("uuid"))

        try:
            task = Task.objects.get(
                uuid=self.request.GET.get("uuid"), owner=self.request.user
            )
            if task.state == "ready":
                data = json.loads(task.data)
                filename = data.get("filename")

                self.response["Content-Type"] = "application/pdf"
                self.response["Content-Disposition"] = (
                    'attachment; filename="%s"' % filename
                )
                with open(os.path.join(cache_path, filename), "rb") as fd:
                    for data in iter(partial(fd.read, 8192), b""):
                        self.response.write(data)

                task.save()
            else:
                self.response = HttpResponseNotFound(
                    "<h1>Arquivo do resumo dos recessos criados não está pronto ou não foi solicitado.</h1>"
                )
        except Exception as e:
            self.log.exception(e)
            self.response = HttpResponseBadRequest(
                "<h1>Não existe este pedido de arquivo do resumo dos recessos criados para o usuário logado.</h1>"
            )

    @login_required(type="JSON")
    def block_periods(self, args=[]):
        rst = {"success": False, "message": "Não foi processado nada ainda!"}
        try:
            group_period = self.request.POST.get("group_period", 0)
            lock = (
                True
                if self.request.POST.get("lock", False).lower() == "true"
                else False
            )

            if has_perm_block_unblock_ap():
                if group_period:
                    AcquisitionPeriod.objects.filter(
                        group_period__pk=group_period
                    ).update(
                        modified_at=datetime.now(),
                        modified_by=get_current_user(),
                        blocked=lock,
                    )
                    GroupPeriod.objects.filter(pk=group_period).update(
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
                    msg = "Grupo não informado."
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


class DAYOFFGroupPeriodExtended(DAYOFFGroupPeriod):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.groupperiod.ManageExtended")')
