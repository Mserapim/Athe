# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.nil import nil_pk, nil_unicode
from contrib.middleware import get_current_user
from contrib.utils import getLogger
from corregedoria.cirdir.models import HealthAssessment, Health

log = getLogger(__name__)


class CIRDIRHealthAssessmentRestful(RestfulDRY):

    force_upper = False

    full_text_index = (
        "health__controlinformation__employee__pessoa_fisica__nome__icontains",
    )

    _model = HealthAssessment

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.cirdir.health.assessment.Manage")'
        )

    def model_to_dict(self, instance):
        _dict_ = super(CIRDIRHealthAssessmentRestful, self).model_to_dict(instance)
        _dict_.update(
            {
                "icons": instance.icons,
                "integrant_unicode": nil_unicode(
                    instance.health.controlinformation.employee, None
                ),
                "integrant": nil_pk(instance.health.controlinformation.employee, None),
            }
        )
        return _dict_

    def get_query(self):
        query = super(CIRDIRHealthAssessmentRestful, self).get_query()
        return query.filter(evaluator__employee__user=get_current_user())

    def management(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.management_query()

            if len(args) == 0:
                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                count = query.count()
                query = self.do_page(query)

                rst.update(
                    success=True,
                    count=count,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.filter(pk=args[0]).first()

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def management_query(self):
        if get_current_user().has_perm("cirdir.can_management_health_area"):
            return self.Model.objects.filter()
        else:
            return self.Model.objects.none()

    def rendered(self, args=[]):

        rst = {"success": False}

        try:
            instance = self.Model.objects.get(pk=self.request.GET.get("pk"))

        except self.Model.DoesNotExist as e:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique as condições de acesso.",
            )
        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="documento pronto para ser exibido",
                content=instance.rendered,
            )

        self.renderer(rst)

    def sign(self, args=[]):

        rst = {"success": False, "message": "nada foi feito ainda"}

        try:

            instance = self.Model.objects.get(pk=self.request.POST.get("pk"))
            instance.sign()
            rst.update(success=True, message="Avaliação concluída.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def confirm_recommendation(self, args=[]):

        rst = {"success": False, "message": "nada foi feito ainda"}

        try:

            health = Health.objects.get(pk=self.request.POST.get("health"))

            for h in HealthAssessment.query_all_recommendation_pending(
                health=health, employee=health.controlinformation.employee
            ):
                h.confirm()

            rst.update(success=True, message="Operação realizada com sucesso!")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
