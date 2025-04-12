# -*- coding: utf-8 -*-
from contrib.controller import DefaultController
from contrib.utils import getLogger
from django.conf import settings
from datetime import datetime

import json
import uuid
import os

log = getLogger(__name__)


class Stats(DefaultController):

    def persist(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "seed": str(uuid.uuid1()),
        }

        store_dir = getattr(settings, "CACHE_PATH")
        stats_filename = os.path.join(store_dir, "stats.cache")

        rst.update(stats_filename=stats_filename)

        stats_data = {}
        if os.path.isfile(stats_filename) is True:
            stats_data = json.load(open(stats_filename, "r"))

        data = None
        try:
            data = json.loads(self.request.POST.get("stats", None))
        except Exception as e:
            log.exception(e)
        finally:
            data.update(
                addr=self.request.META.get("REMOTE_ADDR"),
                user=self.request.user.username,
                date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S-0300"),
            )

            stats_data.update({rst.get("seed"): data})

        json.dump(stats_data, open(stats_filename, "w"), indent=4)

        self.response["Content-Type"] = "text/javascript"
        self.response.write(json.dumps(rst))
