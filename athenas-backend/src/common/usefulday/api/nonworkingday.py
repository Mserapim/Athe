# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.usefulday.models import NonWorkingDay

import json

log = getLogger(__name__)


class CUNNonWorkingDay(RestfulDRY):

    _model = NonWorkingDay

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "description__icontains",
        "places__sigla__icontains",
        "places__nome__icontains",
        "places__descricao__icontains",
    )

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    force_orm_single = True

    exclude_fields = ["modified_by", "modified_at", "created_by", "created_at"]

    force_persist_boolean_fields = ["is_partial"]

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def model_to_dict(self, instance):
        _dict_ = super(CUNNonWorkingDay, self).model_to_dict(instance)

        _dict_.update(
            {"date_period": instance.date_period, "has_places": instance.has_places}
        )

        return _dict_

    def get_year_list(self, args=[]):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            year_list = NonWorkingDay.get_year_list()
        except Exception as e:
            self.log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=len(year_list),
                collection=[{"value": y, "display": str(y)} for y in year_list],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def copy(self, *args):
        obj = {"success": False, "message": "Nada foi feito ainda."}

        try:
            NonWorkingDay.copy(self.request.POST)
        except Exception as e:
            log.exception(e)
            obj.update(message=str(e))
        else:
            obj.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(obj))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.usefulday.nonworkingday.NonWorkingDayManage")'
        )
