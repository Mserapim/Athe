# -*- coding: utf-8 -*-
from contrib.middleware import StartupLoader
from contrib.tests.utils import ViewsTestCase
from contrib.utils import getLogger
from judicial.rpc.execution_organ import ExecutionOrganRPC
from judicial.models import ExecutionOrgan, County

log = getLogger(__name__)

import json


class ExecutionOrganRPCTestCase(ViewsTestCase):

    view_class = ExecutionOrganRPC

    def test_json(self):
        url = "%s/%s/" % (self.url_athenas, self.view_class.__name__)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_allorgans(self):
        url = "%s/%s/allorgans" % (self.url_athenas, self.view_class.__name__)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


def allorgans(self, args=[]):
    obj = dict(total="0", list=[])
    total = 0
    organs_list = []
    counties = County.objects.filter().order_by("title")
    for county in counties:
        humanify = lambda x: str(x.first()) if x.first() else ""
        strip = lambda x: x.split(":")[-1].strip() if x else ""
        explode = lambda x: [strip(y) for y in x.split("|")] if x else ""

        qs = ExecutionOrgan.objects.filter(
            localidade__in=county.locations.all()
        ).order_by("instancia__nome", "nome")
        total += qs.count()
        for eo in qs:
            replacements = []
            for replaced in eo.replaceds.all().order_by("order"):
                replacements.append(
                    {
                        "organ": str(replaced.substitute),
                        "order": replaced.order,
                        "owner": strip(replaced.substitute.owner_unicode()),
                        "job_position": humanify(replaced.substitute.cargo_responsavel),
                        "exercise": explode(
                            replaced.substitute.employee_exercise_unicode()
                        ),
                        # 'full_exercise': explode(replaced.substitute.employee_workplaces_full_exercise_unicode()),
                    }
                )

            areas = []
            d_table_qs = eo.in_distribution_tables.all()
            if d_table_qs.exists():
                for dist in eo.in_distribution_tables.all():
                    areas.append(
                        {
                            "attribution": str(dist.matter),
                            "document": {
                                "title": str(dist.document),
                                "url": "http://%s%s"
                                % (settings.DOMAIN, dist.document.arquivo.permalink()),
                            },
                        }
                    )
            else:
                areas.append({"attribution": "Geral", "document": None})
            # http://10.113.254.37/athenas/ExecutionOrganRPC/allorgans/json/
            organs_list.append(
                {
                    "pk": eo.pk,
                    "organ": str(eo),
                    "owner": strip(eo.owner_unicode()),
                    "exercise": explode(eo.employee_exercise_unicode()),
                    # 'full_exercise': explode(eo.employee_workplaces_full_exercise_unicode()),
                    "phone": humanify(eo.telefone),
                    "address": humanify(eo.endereco),
                    "job_position": humanify(eo.cargo_responsavel),
                    "instance": eo.instancia.nome if eo.instancia else "",
                    "areas": areas,
                    "range": [str(city) for city in county.locations.all()],
                    "replacements": replacements,
                }
            )

        obj.update(total=total, list=organs_list)

    self.render(obj)


ExecutionOrganRPC.allorgans = allorgans
StartupLoader().doLoad()
