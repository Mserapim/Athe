# -*- coding: utf-8 -*-

import codecs
import hashlib
import os
import threading

from django.conf import settings

from contrib.controller import CommandController
from contrib.decorator import cache_return
from rh.gfp.rais import File


class RAISGerador(CommandController):

    def getFile(self, *args):
        SID = self.request.GET.get("sid")
        tempfile = self.get("tempfile", SID)

        self.log.debug(tempfile)

        with codecs.open(tempfile, "r") as fd:
            for buf in fd.readlines():
                self.response.write(buf)

        self.response["content-disposition"] = (
            "attachment; filename=rais-%s.txt" % self.get("ano_base", SID)
        )

        if not settings.DEBUG:
            os.unlink(tempfile)

    @cache_return
    def create_temporary_filename(self):
        # cache = getattr(settings, 'CACHE', {})
        path = settings.CACHE_PATH or "/tmp"

        hmd5 = hashlib.new("md5")
        hmd5.update(os.urandom(64))

        return os.path.join(path, hmd5.hexdigest())

    def proccess(self):
        filename = self.create_temporary_filename()
        self.set("tempfile", filename)

        self.log.debug("FILE GENERATE INIT =========================")
        f = File(
            {
                "ano_base": int(self.get("ano_base")),
                "retificadora": self.get("retificadora"),
                "observer": self,
            }
        )
        self.log.debug("FILE GENERATE END =========================")
        try:
            with codecs.open(filename, "w", "utf8") as fd:
                fd.write(str(f))
        except Exception as e:
            self.log.exception(e)
            self.set("done", False)
        else:
            self.set("done", True)

    def start(self, args=[]):
        t = threading.Thread(target=self.proccess)
        t.setDaemon(True)
        self.log.debug("INIT START PROCESS =====================")
        t.start()
