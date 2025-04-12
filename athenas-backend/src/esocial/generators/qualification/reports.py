# -*- coding: utf-8 -*-


from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.utils import get_json_engine, getLogger
from engine.models import TaskSession
from ged.models import Arquivo as FileGED
from esocial.generators.qualification import protocol
from contrib.extjs import ExtFileBuild
from django.conf import settings

import threading
import os
from datetime import datetime

json = get_json_engine()

log = getLogger(__name__)


class ESCQualificationFile(ExtFileBuild):
    """docstring for GFPReturnViabillize"""

    generate_file = "qualification.txt"
    _tmp_dir = "esocial"

    def get_generate_filename(self):
        today = datetime.now().strftime("%d%m%Y")
        return "%s_%s.txt" % (settings.ORGAN_IDENTIFIER, today)

    @login_required("JSON")
    def generate_file(self, args=[]):
        obj = {"success": True}

        def process(user, log):
            # SETTING USER FOR LOCAL

            log.info(
                "GENERATE FILE PROCESS: %s: %s: %s"
                % (user, "QUALIFICATION ESOCIAL", self.tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution("Gerando arquivos de qualificação")

            lines = protocol.QualificationFile(task)

            file_path = os.path.join(self.tmp_dir, self.get_generate_filename())
            log.info(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % self._tmp_dir)
            qualif_file = self.create_file(file_path, lines.__extract_regs__())

            gedfile = FileGED.from_filepath(qualif_file, user, "text/plain", 1)

            task.add_file(gedfile)

            task.finish_execution()

            self.clear_tmpdir()

        t = threading.Thread(target=process, args=(self.request.user, log))
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
