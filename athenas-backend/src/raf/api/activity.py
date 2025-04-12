# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.br import br_month
from raf.models import Activity, Quiz, Item, SubItem
import raf.api.util as util

log = getLogger(__name__)


class RAFActivity(RestfulDRY):

    _model = Activity

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.activity.Launcher")')

    def get_taxonomy(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        try:
            params = util.request_params(self)
            # activity = self.get_query().get(id=params.get('activity')) if params.get('activity') != '0' else None
            data = []
            data.append(
                {
                    "quiz_id": params.get("quiz_id"),
                    "quiz_display": Quiz.objects.filter(
                        pk=params.get("quiz_id")
                    ).values_list("typequiz__title")[0],
                    "item_id": params.get("item_id"),
                    "item_display": Item.objects.filter(
                        pk=params.get("item_id")
                    ).values_list("title")[0],
                    "subitem_id": params.get("subitem_id"),
                    "subitem_display": SubItem.objects.filter(
                        pk=params.get("subitem_id")
                    ).values_list("title")[0],
                }
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=self.get_query().filter(id=params.get("activity")).count(),
                collection=data,
            )
        return self.renderer(rst)

    def all_activities(self, args=[]):
        rst = {
            "success": False,
            "message": "Nada foi feito ainda",
            "count": 0,
            "collection": [],
        }
        params = util.request_params(self)
        act = Activity.objects.filter(pk=params.get("activity", 0)).first()
        acts = []
        if act:
            acts = Activity.objects.filter(
                item=act.item,
                subitem=act.subitem,
                workerlocation__raf__month=act.workerlocation.raf.month,
                workerlocation__raf__year=act.workerlocation.raf.year,
                workerlocation__location=act.workerlocation.location,
            )
        total = 0
        for a in acts:
            total = total + a.amount_submitted
        data = [
            {
                "activity": a.pk,
                "month_year": "%s/%s"
                % (a.workerlocation.raf.month, a.workerlocation.raf.year),
                "employee_matricula": a.workerlocation.raf.employee.matricula,
                "employee_unicode": a.workerlocation.raf.employee.pessoa_fisica.nome,
                "amount": a.amount_submitted,
            }
            for a in acts
        ]
        rst.update(
            success=True,
            message="Dados encontrados com sucesso.",
            count=acts.count() if acts else 0,
            collection=data,
            total=total,
        )
        return self.renderer(rst)
