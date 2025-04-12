# -*- coding: utf-8 -*-

from contrib.controller import DefaultController
from contrib.utils import getLogger
from django.conf import settings
import json
from common.itop.api.rest import Api

log = getLogger(__name__)


class CIQuickContent(DefaultController):

    def get_notifications(self, args=[]):
        obj = {}

        rest = Api()

        rest.connect(
            getattr(settings, "ITOP_URL"),
            getattr(settings, "ITOP_VERSION"),
            getattr(settings, "ITOP_USER"),
            getattr(settings, "ITOP_PWD"),
        )

        quick_contents = rest.get(
            "SIATUMessages",
            "SELECT SIATUMessages WHERE status = 'active'",
            "title, description_notify",
        )
        try:
            if quick_contents["code"] == 0:
                if quick_contents["objects"]:
                    obj.update(
                        data=[
                            {
                                "title": "{v[fields][title]}".format(v=value),
                                "description_notify": "{v[fields][description_notify]}".format(
                                    v=value
                                ),
                            }
                            for i, value in list(quick_contents["objects"].items())
                        ]
                    )
                else:
                    obj.update(
                        data=[
                            {
                                "title": "",
                                "description_notify": "",
                            }
                        ]
                    )
        except Exception:
            pass

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
