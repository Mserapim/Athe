# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from raf.models import NonProceduralActivities


class RAFNonProceduralActivities(RestfulDRY):
    _model = NonProceduralActivities
    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.nonproceduralactivities.Manage")')
