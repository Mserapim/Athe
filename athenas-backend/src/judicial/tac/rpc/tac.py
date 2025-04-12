# -*- coding:utf-8 -*-
# from django.conf import settings
import datetime
from django.db.models import Q, Min

from contrib.utils import getLogger
from contrib.controller import DefaultController
from contrib.decorator import is_public

from judicial.tac.models import ManagementTAC


log = getLogger(__file__)


def attachment_tpl(attach, file_attr="file_descriptor"):
    attach_file = {}
    if hasattr(attach, file_attr):
        attach_file.update(
            {
                "title": attach.title,
                "url": getattr(attach, file_attr).no_logged_permalink(),
            }
        )
    return attach_file


class TacRPC(DefaultController):

    UNITS = {1: ["dia", "dias"], 2: ["mês", "meses"], 3: ["ano", "anos"]}

    def __init__(self, *args, **kwargs):
        super(TacRPC, self).__init__(*args, **kwargs)

        self.SIGNED = Q(signed_by__isnull=False, signed_at__isnull=False)

        if self.response_format == "json":
            self.response["content-type"] = "text/javascript; charset=utf-8"

    @is_public()
    def years_choices(self, args=[]):
        min_date = ManagementTAC.objects.aggregate(min_date=Min("signed_at")).get(
            "min_date"
        )
        today = datetime.date.today()

        if not min_date:
            min_date = today

        years = list(range(min_date.year, today.year + 1))
        choices = [("", "Todos")] + list(zip(years, years))
        self.render(choices)

    @is_public()
    def list_by_lawsuit(self, args=[]):
        response_data = {"success": False}

        lawsuit_id = self.request.POST.get("lawsuit") or 0

        part_tacs = []
        qs = ManagementTAC.objects.filter(self.SIGNED, lawsuit=lawsuit_id).order_by(
            "-created_at"
        )

        for tac in qs:

            part_tacs.append(
                {
                    "id": tac.id,
                    "description": tac.description,
                    "lawsuit_number": tac.lawsuit.cache_number,
                    "lawsuit_kind": tac.lawsuit.get_type_lawsuit_display(),
                }
            )

        response_data.update(success=True, list=part_tacs)

        self.render(response_data)

    @is_public()
    def list(self, args=[]):
        qs = ManagementTAC.objects.filter(self.SIGNED)

        page = int(self.request.REQUEST.get("page") or 1)
        length = int(self.request.REQUEST.get("length") or 15)
        keyword = self.request.REQUEST.get("keyword")
        year = self.request.POST.get("year")

        if year:
            qs = qs.filter(signed_at__year=year)

        if keyword:
            qs = qs.filter(description__icontains=keyword)

        total = qs.count() or "0"
        end = page * length
        start = end - length

        tac_list = [
            {
                "id": tac.id,
                "description": tac.description,
                "lawsuit_number": tac.lawsuit.cache_number,
                "lawsuit_kind": tac.lawsuit.get_type_lawsuit_display(),
            }
            for tac in qs[start:end]
        ]

        self.render({"total": total, "list": list(tac_list)})

    @is_public()
    def get(self, args=[]):
        data = None
        if args:
            tac_id = args[0]
            tac = ManagementTAC.objects.filter(self.SIGNED, id=tac_id).first()
            if tac:

                lawsuit_data = {}
                if tac.lawsuit:
                    lawsuit = tac.lawsuit
                    lawsuit_data.update(
                        id=lawsuit.id,
                        title=str(lawsuit),
                        number_lawsuit=str(lawsuit.number_lawsuit).rjust(7, "0"),
                        involved_parts=[str(part) for part in lawsuit.blokes.all()],
                    )

                activities_list = []
                for act in tac.activities_tac.all():

                    unit = TacRPC.UNITS.get(act.time_type, "")
                    if unit:
                        unit = unit[1] if act.time > 1 else unit[0]

                    activity_attachment_qs = act.document_activity.all()
                    activities_list.append(
                        {
                            "id": act.id,
                            "description": act.description,
                            "status": act.get_realized_display(),
                            "time_unit": unit,
                            "time": act.time,
                            "deadline": "%s %s" % (act.time, unit.lower()),
                            "fine_value": act.fine_value,
                            "repair_value": act.repair_value,
                            "attachments": [
                                attachment_tpl(attach, "file_document")
                                for attach in activity_attachment_qs
                            ],
                        }
                    )

                attachs_qs = tac.attaches.all()

                data = {
                    "id": tac.id,
                    "description": tac.description,
                    "considerations": tac.considerations,
                    "signed_date": tac.signed_at.date() if tac.signed_at else "",
                    "lawsuit": lawsuit_data,
                    "attachments": [attachment_tpl(attach) for attach in attachs_qs],
                    "activities": activities_list,
                }

        self.render(data)
