# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.clinical.models import Prescription
from django.db import transaction
from django.template import loader

log = getLogger(__name__)


class ClinicalPrescription(RestfulDRY):

    _model = Prescription

    force_upper = False

    def printer(self, args=[]):
        tpl = loader.get_template("clinical/printer.html")

        prescription = self.get_query().get(pk=int(args[0] or 0))
        context = {"pages": [prescription.rendered]}

        self.response["Content-Type"] = "text/html; charset=utf-8"
        self.response.write(tpl.render(context))

    def render_content(self, args=[]):
        rst = {"success": False, "message": "not implemented at moment"}

        try:
            instance = self.get_query().get(pk=int(args[0] or 0))
            rst.update(
                success=True,
                message="Renderizado com sucesso.",
                content=instance.rendered,
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.renderer(rst)

    def sign(self, args=[]):
        rst = {"success": False, "message": "not implemented at moment"}

        try:
            item = self.get_query().get(pk=int(args[0]))
            with transaction.atomic():
                item.sign()
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Receituário assinado com sucesso.")

        self.renderer(rst)
