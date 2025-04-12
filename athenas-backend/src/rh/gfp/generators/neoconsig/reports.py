# -*- coding: utf-8 -*-

import os
import threading

from django.conf import settings

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.utils import get_json_engine, getLogger, make_zipfile
from engine.models import NullTaskSession, TaskSession
from ged.models import Arquivo as FileGED
from rh.gfp import reports

from .protocol import (
    ClassificationsFile,
    ConsigneeFile,
    EmployeesFile,
    EventsFile,
    FinancialFile,
    HistoryFile,
    OrgansFile,
    SituationsFile,
    WorkLocationsFile,
    PaidOffFile,
)

# import uuid
# import shutil

json = get_json_engine()

log = getLogger(__name__)


class GFPNeoConsigInitial(reports.GFPReturnFile):
    """docstring for GFPNeoConsigInitial"""

    _generated_filename = "neoconsig_initial.zip"

    NL_END_OF_FILE = True

    def get_generate_filename(self):
        return "neoconsig_initial_%s_%02d%04d.zip".lower() % (
            settings.ORGAN_IDENTIFIER,
            self.period.mes,
            self.period.ano,
        )

    def employees(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = EmployeesFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "SERVIDORES_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def organs(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = OrgansFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "SECRETARIAS_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def work_locations(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = WorkLocationsFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "LOTACOES_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def events(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = EventsFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "VANTAGEMDESCONTO_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def classifications(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = ClassificationsFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "CADCATEGORIA_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def situations(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = SituationsFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "CADSITFUNCIONAL_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def financial(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = FinancialFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "FINANCEIRO_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def history(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = HistoryFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "CARGAEMPRESTIMO_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def consignee(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = ConsigneeFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "CADCONSIGNATARIA_%s.txt" % ref)

        return self.create_file(file_path, str(lines))

    def paid_off(self, task=NullTaskSession()):

        ref = "%02d%04d" % (self.period.mes, self.period.ano)

        lines = PaidOffFile(self.period, task)

        file_path = os.path.join(self.tmp_dir, "RETORNOQUITADAS_%s.txt" % ref)

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
                "Gerando arquivos NeoConsig - %02d/%04d"
                % (self.period.mes, self.period.ano)
            )

            self.employees(task)
            self.organs(task)
            self.work_locations(task)
            # self.events(task)
            self.classifications(task)
            self.situations(task)
            self.financial(task)
            # self.history(task)
            # self.consignee(task)
            self.paid_off(task)

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
