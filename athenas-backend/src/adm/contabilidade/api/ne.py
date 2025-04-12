# -*- coding: utf-8 -*-
from adm.contabilidade.models import NE
from contrib.newrest import Restful
from contrib.nil import nil_date, nil_datetime, nil_display
from contrib.utils import DateUtils, getLogger

log = getLogger(__name__)


class ContabNE(Restful):

    _model = NE

    full_text_index = ("numero__icontains",)

    def get_params(self, *args, **kargs):
        params = Restful.get_params(self, *args, **kargs)

        if "data_nota" in params:
            if params.get("data_nota") != "":
                params.update(data_nota=DateUtils.str_to_date(params.get("data_nota")))
            else:
                params.update(data_nota=None)

        if "data" in params:
            if params.get("data") != "":
                params.update(data=DateUtils.str_to_datetime(params.get("data")))
            else:
                params.update(data=None)

        return params

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)

        rst.update(
            data_nota=nil_date(instance.data_nota, None),
            data=nil_datetime(instance.data, None),
            modalidade=instance.modalidade,
            modalidade_display=nil_display(instance, "modalidade", None),
            numero=instance.numero,
            valor=float(instance.valor or 0),
        )

        return rst
