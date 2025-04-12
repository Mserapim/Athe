# -*- coding: utf-8 -*-

import os
import threading

from django.conf import settings

from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger
from engine.mq.models import Task
from rh.gfp import reports
from rh.gfp.tasks import process_get_consigfacil

json = get_json_engine()

log = getLogger(__name__)


class GFPConsigFacilInitial(reports.GFPReturnFile):
    _generated_filename = "consigfacil__initial.zip"

    NL_END_OF_FILE = True

    def get_generate_filename(self):
        return "consigfacil_initial_%s_%02d%04d.zip".lower() % (
            settings.ORGAN_IDENTIFIER,
            self.period.mes,
            self.period.ano,
        )

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        Task.start(
            process_get_consigfacil,
            tmp_dir=self.tmp_dir,
            period=self.period.pk,
            filename=self.get_generate_filename(),
            user=self.request.user.pk,
        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
