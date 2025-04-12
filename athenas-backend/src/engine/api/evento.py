# -*- coding: utf-8 -*-
from contrib.controller import DefaultController
from contrib.newrest import Restful
from engine.models import Evento
from contrib.utils import DateUtils
from datetime import datetime
from django.db.models import Q


class EngEvento(Restful):

    _model = Evento

    force_upper = False

    def active(self, args=[]):

        query = self.Model.objects.filter(
            Q(start_date__lte=datetime.now())
            & Q(Q(end_date__gte=datetime.now()) | Q(end_date__isnull=True))
        )

        rst = {
            "count": query.count(),
            "collection": [
                self.model_to_dict(evt) for evt in query.order_by("start_date")
            ],
        }

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def model_to_dict(self, instance):
        rst = super(EngEvento, self).model_to_dict(instance)

        dtt_str = lambda x: DateUtils.datetime_to_str(x) if x is not None else None

        rst.update(
            title=instance.title,
            start_date=dtt_str(instance.start_date),
            end_date=dtt_str(instance.end_date),
            resource=instance.resource,
            interface=instance.interface,
        )

        return rst

    def get_params(self, querydict=None, **kargs):
        params = super(EngEvento, self).get_params(querydict, **kargs)

        if params.get("start_date", None) not in ("", None):
            params.update(
                start_date=DateUtils.str_to_datetime(params.get("start_date"))
            )
        elif params.get("start_date", None) == "":
            params.update(start_date=None)

        if params.get("end_date", None) not in ("", None):
            params.update(end_date=DateUtils.str_to_datetime(params.get("end_date")))
        elif params.get("end_date", None) == "":
            params.update(end_date=None)

        return params


class EngEventoManager(DefaultController):

    def json(self, args=[]):
        self.response["ContentType"] = "text/javascript"
        self.response.write('Ext._create("engine.evento.Manager")')
