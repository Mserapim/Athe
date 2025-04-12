# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, employee_from_user
from contrib.middleware import get_current_user
from raf.models import TrustRelationship, ActivityAdjustment, FunctionalActivityReport
from rh.models import Servidor
from django.db.models import Q, Min
from contrib.nil import nil_datetime


log = getLogger(__name__)


class RAFEmployee(RestfulDRY):

    _model = Servidor

    full_text_index = (
        "matricula__icontains",
        "pessoa_fisica__nome__icontains",
    )

    def employee_trust_relation(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.employee_trust_relation_box()

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
                inst = query.get(pk=args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def employee_trust_relation_box(self):
        query = super(RAFEmployee, self).get_query()

        employee = employee_from_user(get_current_user())

        query_set = Q(
            Q(
                pk__in=TrustRelationship.objects.exclude(activated=False)
                .filter(trust_employee=employee)
                .values_list("employee")
            )
            | Q(pk=employee.pk)
        )

        if get_current_user().has_perm("raf.can_management_raf"):
            query_set = Q(Q(tipo="M") | Q(pk=employee.pk))

        return query.filter(query_set)

    def model_to_dict(self, instance):
        rst = super(RAFEmployee, self).model_to_dict(instance)

        rst.update(
            {
                # 'first_adjustment_date': nil_datetime(ActivityAdjustment.objects.filter(situation__in=[0, 1], activity__workerlocation__raf__employee=instance.pk).aggregate(Min('created_at'))['created_at__min'], None),
                "first_adjustment_date": (
                    ActivityAdjustment.objects.filter(
                        situation__in=[0, 1],
                        activity__workerlocation__raf__employee=instance.pk,
                    )
                    .aggregate(Min("created_at"))["created_at__min"]
                    .strftime("%d/%m/%Y %H:%M:%S")
                    if ActivityAdjustment.objects.filter(
                        situation__in=[0, 1],
                        activity__workerlocation__raf__employee=instance.pk,
                    ).exists()
                    else ""
                ),
                "locations_follow": self.getWorkerplaceEmployee(instance),
            }
        )

        return rst

    def employee_adjustment(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.employee_adjustment_box()

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
                inst = query.get(pk=args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def employee_adjustment_box(self):
        query = super(RAFEmployee, self).get_query()

        # pklist = ActivityAdjustment.objects.filter(situation__in=[0, 1]).values_list('activity__workerlocation__raf__employee').distinct()
        rst = (
            query.filter(
                functionalactivityreports__workerlocations__activities__adjustment__situation__in=[
                    0,
                    1,
                ]
            )
            .annotate(
                first_adjustment_date=Min(
                    "functionalactivityreports__workerlocations__activities__adjustment__created_at"
                )
            )
            .order_by("first_adjustment_date")
        )

        return rst

    def getWorkerplaceEmployee(self, employee):

        locations = []
        if employee:
            for l in employee.get_workplace().values_list("lotacao__pk", flat=True):
                locations.append(l)
        return locations

    def employee_initial(self, args=[]):

        rst = {
            "success": False,
            "message": "Nada foi feito ainda.",
        }

        try:
            employee = self.employee_trust_relation_box().get(
                pk=employee_from_user(get_current_user()).pk
            )

            locationsFollow = self.getWorkerplaceEmployee(employee)

        except self.Model.DoesNotExist:
            rst.update(message="Pessoa não encontrada.")

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="dados carregados com sucesso",
                data={
                    "pk": employee.pk,
                    "pessoa_fisica_unicode": employee.pessoa_fisica.nome,
                    "locations_follow": locationsFollow,
                },
            )

        self.renderer(rst)
