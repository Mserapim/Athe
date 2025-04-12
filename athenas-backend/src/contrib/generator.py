# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from django.conf import settings

import os
import codecs
import shutil
import uuid


log = getLogger(__name__)


class FileGenerator(object):
    """
    Controller Widget básico baseado na ExtJS.
    """

    mimetype = "text/plain"
    generate_file = "default.txt"
    encoding_out = "utf-8"
    _tmp_dir = "tmp"

    def __init__(self, *args, **kargs):
        log.debug("INIT ExtFileBuild")
        super(FileGenerator, self).__init__(*args, **kargs)
        self.uuid = uuid.uuid1().hex

    def get_generate_filename(self):
        return self.generate_file

    @property
    def generated_filename(self):
        return self.generate_file

    @property
    def tmp_dir(self):
        return os.path.join(settings.UPLOAD_STORE_DIR, self._tmp_dir, self.uuid)

    def create_file(self, file_path, objs=[], xml=False):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        if xml:
            objs.write(file_path, encoding=self.encoding_out, xml_declaration=True)
        else:
            with codecs.open(file_path, "w", self.encoding_out) as fd:
                fd.writelines(objs)

        return file_path

    def generate_file(self, args=[]):
        log.exception("method generate_file not implemented!")

    def clear_tmpdir(self):
        shutil.rmtree(self.tmp_dir)
