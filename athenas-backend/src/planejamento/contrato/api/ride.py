# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from django.db.models import Q
from contrib.nil import nil_display
from planejamento.contrato.models import Ride, RideItem
from rh.models import PessoaJuridica as Person
import json


log = getLogger(__name__)


class PHMRide(RestfulDRY):

    _model = Ride

    full_text_index = ("number__icontains",)

    force_upper = False

    def get_query(self):
        query = super(PHMRide, self).get_query().distinct()
        user = get_current_user()

        group_views = {
            1: "hiring-agreement-supervisor",
            2: "hiring-agreement-view-all",
            3: "hiring-agreement-manager",
            5: "hiring-agreement-financial",
        }

        # Se for gestor geral ou financeiro, visualiza todos
        if user.groups.filter(
            Q(name=group_views.get(2))
            | Q(name=group_views.get(3))
            | Q(name=group_views.get(5))
        ).exists():
            query = query.filter()

        # Se for fiscal, visualiza os que ele é gestor ou responsável
        elif user.groups.filter(name=group_views.get(1)).exists():
            subordinates = user.servidor.subordinados.filter()
            query = query.filter(
                Q(agreementsupervisors__employee__user=user)
                | Q(agreementsupervisors__employee__in=subordinates),
                Q(agreementsupervisors__end=None),
            )

        # Se for de tipo algum, não recebe nada
        else:
            query = query.none()

        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.ride.Manage")')


class PHMRideItem(RestfulDRY):

    _model = RideItem

    force_upper = False

    def model_to_dict(self, instance):
        _dict_ = super(PHMRideItem, self).model_to_dict(instance)

        unitary_value = float(instance.item.unitary_value)

        total_value = float(instance.amount) * unitary_value

        _dict_.update(
            {
                "group": instance.item.group,
                "line": instance.item.line,
                "unitary_value": unitary_value,
                "total_value": total_value,
            }
        )

        return _dict_

    def change_status_ride_item(self, *args):
        """
        Este método altera status do item de uma Carona.
        Obs.: até o momento alterando status apenas para Cancelado
        """

        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            item = int(self.request.POST.get("item"))  # item da carona
            justificative = self.request.POST.get("justificative")  # justificativa
            action = int(self.request.POST.get("action"))  # ação

        except Exception:
            obj.update(message="Selecione um item para cancelar")
        else:
            ride_item = RideItem.objects.get(id=item)
            ride_item.status = action
            ride_item.justification = justificative

            try:
                ride_item.save()
            except Exception as e:
                obj.update(success=False, message=str(e))
            else:
                obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))
