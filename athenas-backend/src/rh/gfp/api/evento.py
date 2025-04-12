# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.gfp.models import Evento

# from contrib.utils import DateUtils


class GFPEventoRestful(RestfulDRY):

    _model = Evento

    full_text_index = ("titulo__icontains", "numero__icontains")

    force_persist_boolean_fields = [
        "automatico",
        "calculo_invertido",
        "aplica_consignado",
        "aplica_consignavel",
    ]

    # force_persist_clear_m2m = ['incide_sobre', ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.evento.EventoManage")')

    def convert_value_of_type_booleanfield(self, value):
        # log.info(u'VALUE: %s' % value)
        return (
            True
            if (value.lower() == "on" or (value and value.isdigit() and int(value)))
            else False
        )

    def model_to_dict(self, instance):
        params = super(GFPEventoRestful, self).model_to_dict(instance)

        params.update(
            incide_sobre=[[i.pk, i.titulo] for i in instance.incide_sobre.all()],
        )

        return params
