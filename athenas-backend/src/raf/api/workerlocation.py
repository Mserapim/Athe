# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_unicode
from raf.models import WorkerLocation

log = getLogger(__name__)


class RAFWorkerLocation(RestfulDRY):

    force_upper = False

    _model = WorkerLocation

    full_text_index = (
        "location__nome__icontains",
        "location__sigla__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.workerlocation.Launcher")')

    def model_to_dict(self, instance):
        _dict_ = super(RAFWorkerLocation, self).model_to_dict(instance)

        _dict_.update(
            {
                "location_unicode": nil_unicode(instance.location, None),
                "raf_unicode": nil_unicode(instance.raf, None),
            }
        )

        return _dict_
