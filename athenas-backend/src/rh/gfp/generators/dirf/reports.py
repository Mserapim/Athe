# -*- coding: utf-8 -*-

import codecs
import os
import threading

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.utils import get_json_engine, getLogger
from engine.models import TaskSession
from ged.models import Arquivo as FileGED
from rh.gfp import reports
from rh.gfp.generators.dirf import protocol

# import uuid
# import shutil

json = get_json_engine()

log = getLogger(__name__)


class GFPDIRFFile(reports.GFPReturnFile):
    """docstring for GFPReturnViabillize"""

    _generated_filename = "fpsf900.txt"

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.debug(
                "GENERATE FILE PROCESS: %s: %s: %s"
                % (user, self.payroll.periodo, self.tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution(
                "Gerando arquivos PASEP FPS900 - %02d/%04d"
                % (self.payroll.periodo.mes, self.payroll.periodo.ano)
            )

            file_pasep = protocol.File(self.payroll, task)

            log.debug(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self.tmp_dir)
            file_path = os.path.join(self.tmp_dir, self.get_generate_filename())

            if not os.path.exists(self.tmp_dir):
                os.makedirs(self.tmp_dir)

            with codecs.open(file_path, "w", "utf-8") as fd:
                fd.write(str(file_pasep))

            gedfile = FileGED.from_filepath(file_path, user, "application/txt", 1)
            # zipfile = make_zipfile(os.path.join(self.tmp_dir, '..',
            #                                     self.get_generate_filename()),
            #                                     self.tmp_dir, False)
            # log.debug(u'>>>>>>>>>>>> ZIP GERADO: %s' % zipfile)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
