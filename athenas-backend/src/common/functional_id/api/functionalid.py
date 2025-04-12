# -*- coding: utf-8 -*-
import json
import re

from common.functional_id.models import FunctionalId
from contrib.controller import DefaultController
from contrib.decorator import is_public
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from django.conf import settings
from rh.models import Servidor as Employee
from standard.models import Configuration

log = getLogger(__name__)


class FIdFunctionalId(RestfulDRY):

    _model = FunctionalId

    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "name__icontains",
        "employee_registration__icontains",
        "national_id_number__icontains",
        "job_position__icontains",
    )

    def url_to_validate_functional_id(self, args=[]):
        self.renderer(
            {
                "success": True,
                "data": {
                    "url_validator": getattr(settings, "FUNCTIONALID_VALIDATOR_URL", "")
                },
            }
        )

    def preview_by_id(self, args=[]):
        rst = {"success": False, "message": "Not implemented"}

        try:
            fid = self.get_query().get(pk=int(args[0]))
            rst.update(
                success=True, message="Processado com sucesso.", content=fid.content
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    @is_public()
    def preview_by_version(self, args=[]):
        rst = {"success": False, "message": "not implmented"}

        try:
            fid = self.get_query().get(version=args[0])
            rst.update(
                success=True, message="Processado com sucesso.", content=fid.content
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def sign(self, args=[]):
        rst = {"success": False, "message": "Not implemented"}

        try:
            func_id = self.get_query().get(pk=args[0])
            func_id.sign()
            rst.update(success=True, message="Carteira funcional assinada com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def deliver(self, args=[]):
        rst = {"success": False, "message": "Not implemented"}

        try:
            func_id = self.get_query().get(pk=args[0])
            func_id.deliver()
            rst.update(success=True, message="Carteira funcional entregue com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def revoke(self, args=[]):
        rst = {"success": False, "message": "Not implemented"}

        try:
            func_id = self.get_query().get(pk=args[0])
            func_id.revoke()
            rst.update(success=True, message="Carteira funcional revogada com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def initiate(self, args=[]):
        rst = {"success": False, "message": "Not implemented"}

        try:
            employee = Employee.objects.get(pk=args[0])
            self.Model.objects.create(employee=employee)

            rst.update(success=True, message="Carteira funcional criada com sucesso.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def json(self, args=[]):
        storage_dir = settings.EXTERNAL_UPLOAD_STORE_DIR
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.functionalId.Manage",{storageDir: "%s"})' % storage_dir
        )

    def model_to_dict(self, instance):
        data = super(FIdFunctionalId, self).model_to_dict(instance)

        def abs_path(gedfile):
            return gedfile.absolute_path if gedfile else None

        data.update(
            icons=instance.icons,
            employee_sign_image_abs_path=abs_path(instance.employee_sign_image),
            validator_sign_image_abs_path=abs_path(instance.validator_sign_image),
            photo_abs_path=abs_path(instance.photo),
            storedir=getattr(settings, "EXTERNAL_UPLOAD_STORE_DIR", "/tmp"),
            local_id_unicode=" ".join(
                [
                    instance.local_id_number if instance.local_id_number else "",
                    instance.local_id_issuance if instance.local_id_issuance else "",
                ]
            ),
        )

        return data


class FIdFunctionalIdPendentSign(DefaultController):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.functionalId.PendentSignManage")')


class FIdFunctionalIdConfiguration(DefaultController):

    def eval_value(self, value):
        if re.match(r"^\[.*\]$", value):
            return eval(value)
        else:
            return value

    def dataReload(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("fid")
            rst.update(
                config={
                    item.key: self.eval_value(item.value) for item in cfg.items.filter()
                }
            )
        except Exception as e:
            rst.update(message=e.message if isinstance(e.message, str) else str(e))
        else:
            rst.update(message="Configuração restaurada", success=True)

        self.response.write(json.dumps(rst))

    def write(self, args=[]):
        rst = {"success": False, "message": "nada feito ainda"}

        cfg = Configuration.get_or_create("fid")

        cfg.set(self.request.POST.get("property"), self.request.POST.get("value"))
        rst.update(
            success=True, message="Identidades funcionais persistidas com sucesso"
        )

        self.response.write(json.dumps(rst))

    def save(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda"}

        try:
            cfg = Configuration.get_or_create("fid")
            for attr in self.request.POST:
                cfg.set(attr, self.request.POST.get(attr))
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Configurações persistidas com sucesso")

        self.response.write(json.dumps(rst))

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("common.functionalId.Configuration")')
