# -*- coding: utf-8 -*-

import codecs
import os
import threading

from django.conf import settings

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.utils import get_json_engine, getLogger, make_zipfile
from engine.models import NullTaskSession, TaskSession
from ged.models import Arquivo as FileGED
from rh.gfp import reports
from rh.gfp.generators.plansaude import protocol

# import uuid
# import shutil

json = get_json_engine()

log = getLogger(__name__)


class GFPReturnPlansaude(reports.GFPReturnFile):
    """docstring for GFPReturnViabillize"""

    _generated_filename = "plansaude_mpto.zip"

    CODIGO = 103  # Código do orgão no Plan Saúde

    def get_generate_filename(self):
        return "plansaude_%s_%02d%04d.zip".lower() % (
            settings.ORGAN_IDENTIFIER,
            self.period.mes,
            self.period.ano,
        )

    def base_salary(self, task=NullTaskSession()):

        log.debug("BASE SALARY FOR %s" % self.period)

        lines = protocol.BasesFile(self.period, task)

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        file_path = os.path.join(self.tmp_dir, "BASE_SALARIAL_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def departures(self, task=NullTaskSession()):

        log.debug("DEPARTURES EMPLOYEE FOR %s" % self.period)

        lines = protocol.DeparturesFile(self.period, task)

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        file_path = os.path.join(self.tmp_dir, "AFASTADOS_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def consignables(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = protocol.ConsignablesFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "RETORNO_CONSIGNACOES_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s" % (user, self.period, self.tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivos Plansaude - %02d/%04d"
                % (self.period.mes, self.period.ano)
            )

            self.base_salary(task)
            self.consignables(task)
            self.departures(task)

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)

            zipfile = make_zipfile(
                os.path.join(self.tmp_dir, "..", self.get_generate_filename()),
                self.tmp_dir,
                False,
            )
            log.debug(">>>>>>>>>>>> ZIP GERADO: %s" % zipfile)
            gedfile = FileGED.from_filepath(zipfile, user, "application/zip", 1)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
