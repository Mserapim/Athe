# -*- coding: utf-8 -*-
from django.db.models import Count

from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from esocial.models import ItemTable
from standard.models import Choice

log = getLogger(__name__)
json = get_json_engine()


CHOICE_NAME_MAP = {
    "99": "DEGREE_EDUCATION",
    "20": "TYPE_STREET",
    "19": "TYPE_FIRED",
    "18": "TIPO_BASE_LICENCA_AFASTAMENTO",
    "7": "DEPENDENT_TYPE",
    "1": "CLASSIF_EMPLOYEE_BY_POSSESSION",
    "9": "CLASSIF_EMPLOYEE_BY_POSSESSION",
}


class ESOCIALItemTable(RestfulDRY):

    _model = ItemTable

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "code__iexact",
        "title__icontains",
    )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    def model_to_dict(self, instance):
        _dict = super().model_to_dict(instance)
        try:
            choice_filter = Choice.get_dict_choices_for("esocial", "CHOICE_ITEM_MAP")[
                instance.esocial_table_int
            ]
        except KeyError:
            choice_filter = ""
        _dict.update({"choice_filter": choice_filter})
        return _dict

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def table_list(self, args=[]):
        tablesqs = ItemTable.objects.values("esocial_table").annotate(
            Count("esocial_table")
        )
        obj = {
            "root": [
                {"pk": x["esocial_table"], "desc": "Tabela " + x["esocial_table"]}
                for x in tablesqs
            ]
        }
        obj.get("root").insert(0, {"pk": 0, "description": "TODAS"})

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("esocial.itemtable.Manage")')
