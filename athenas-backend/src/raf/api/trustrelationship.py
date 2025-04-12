# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from raf.models import TrustRelationship

log = getLogger(__name__)


class RAFTrustRelationship(RestfulDRY):

    _model = TrustRelationship

    force_upper = False

    force_persist_boolean_fields = ["activated"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.trustrelationship.Launcher")')

    def model_to_dict(self, instance):
        _dict_ = super(RAFTrustRelationship, self).model_to_dict(instance)

        _dict_.update({"icons": instance.icons})

        return _dict_

    def trust_relationship_employee_box(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.employee_box_query()

            if len(args) == 0:

                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                rst.update(
                    success=True,
                    count=query.count(),
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.get(pk=args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def employee_box_query(self):
        employee = employee_from_user(self.request.user)

        return self.Model.objects.filter(trust_employee=employee)
