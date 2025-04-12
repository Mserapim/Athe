from django.db.models import Q

from rh.api.workplace import RHWorkplaceRestful
from rh.models import Servidor, OrgaoGeral
from judicial.models import RequestCollaboration, Secretary
from contrib.middleware import get_current_user
from contrib.utils import getLogger, employee_from_user


log = getLogger(__name__)


class EJudWorkplaceRestful(RHWorkplaceRestful):

    def get_query(self):
        query = super(EJudWorkplaceRestful, self).get_query()
        user = get_current_user()

        if not user.has_perm("judicial.outcourtlawsuitadmin"):
            if user.servidor.tipo == "M":
                query = query.filter(
                    pk__in=user.servidor._raw_locations().values_list(
                        "lotacao", flat=True
                    )
                )
            else:
                query = query.filter(pk__in=user.servidor.work_locations.all())

        return query

    def locations_of_work(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda"}

        try:
            employee = employee_from_user(get_current_user())
            work_locations = [
                {
                    "pk": wl.pk,
                    "node": wl.pk,
                    "description": str(wl),
                    "is_collaboration": False,
                    "icon": "icon-judicial icon-ejud-departament",
                }
                for wl in employee.work_locations
            ]

            query = (
                RequestCollaboration.objects.filter(canceled_by=None)
                .filter(
                    Q(requestcollaborationperson__person=employee.pessoa_fisica)
                    | Q(
                        requestcollaborationgeneralorgan__general_organ__in=employee.work_locations
                    )
                )
                .values("lawsuit__location_id")
            )

            locations_collaboration = [
                {
                    "pk": ("wl_%d" % wl.pk),
                    "description": str(wl),
                    "node": wl.pk,
                    "is_collaboration": True,
                    "icon": "icon-judicial icon-ejud-manifestation-indirect",
                }
                for wl in OrgaoGeral.objects.filter(pk__in=query)
            ]

            rst.update(
                success=True,
                message="Dados processados com sucesso",
                collection=work_locations + locations_collaboration,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def secretaries_of_work(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda"}

        try:
            user = get_current_user()
            employee = employee_from_user(user)

            employee_locations = employee.work_assignment_effective_exercise.values(
                "lotacao"
            )
            secretaries = Secretary.objects.filter(location__in=employee_locations)

            work_locations = [
                {
                    "pk": wl.location.pk,
                    "node": wl.location.pk,
                    "description": str(wl),
                    "is_collaboration": False,
                    "icon": "icon-judicial icon-ejud-departament",
                }
                for wl in secretaries
            ]

            rst.update(
                success=True,
                message="Dados processados com sucesso",
                collection=work_locations,
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)
