# -*- coding: utf-8 -*-
import json
from datetime import date

from contrib.utils import getLogger
from contrib.newrest import RestfulDRY

from django.db.models import Q

from rh.models import MembersTelecommuting
from standard.models import Choice


log = getLogger(__name__)


class RHTelecommutingManager(RestfulDRY):

    _model = MembersTelecommuting

    force_upper = False
    full_text_index = (
        "employee__pessoa_fisica__nome__icontains",
        "employee__matricula__icontains",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.telecommuting.Manage")')

    def model_to_dict(self, instance):
        _dict = super().model_to_dict(instance)
        _dict.update(
            reason_description=instance.telecommuting_reason_description,
        )
        return _dict

    def export(self, args=[]):
        rst = []
        query = self.get_query()
        if "filter" in self.request.GET:
            query = self.do_filter(query)
        if "keyword" in self.request.GET:
            query = self.do_full_text_filter(query)
        if "sort" in self.request.GET:
            query = self.do_sort(query)
        query = self.do_page(query)
        for record in query:

            rst.append(
                {
                    "Servidor": record.employee,
                    "Motivo": record.telecommuting_reason_description,
                    "Data início": (
                        record.data_inicio.strftime("%d/%m/%Y")
                        if record.data_inicio
                        else None
                    ),
                    "Data fim": (
                        record.data_fim.strftime("%d/%m/%Y")
                        if record.data_fim
                        else None
                    ),
                    "Status": record.get_status_display(),
                }
            )

        renderer = self.get_renderer(self.request.GET.get("format", "text/javascript"))
        self.response["content-disposition"] = "attachment; filename=export.csv"
        renderer(rst)

    def get_reasons(self, args=[]):

        obj = {
            "result": [
                {"pk": choice.value, "description": str(choice.description)}
                for choice in Choice.objects.filter(
                    app_label="rh", name="TELECOMMUTING_REASONS"
                )
            ]
        }

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
