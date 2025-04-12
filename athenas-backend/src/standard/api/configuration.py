# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from standard.models import Configuration, Item, JustificationItem


log = getLogger(__name__)


class STDConfiguration(RestfulDRY):

    _model = Configuration

    force_upper = False

    full_text_index = (
        "application__icontains",
        "",
    )

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.configuration.Manage")')


class STDItem(RestfulDRY):

    _model = Item

    force_upper = False

    full_text_index = (
        "configuration__application__icontains",
        "key__icontains",
        "justificationitem__name__icontains",
    )

    def model_to_dict(self, instance):
        rst = super(STDItem, self).model_to_dict(instance)
        rst.update(
            type=instance.configuration.application,
            name=instance.get_name,
            max_value=instance.get_max_value,
            min_value=instance.get_min_value,
            paid=instance.get_paid,
            gera_falta=instance.get_gera_falta,
            payroll=instance.get_payroll,
            vertical_progression=instance.get_vertical_progression,
            premium_license=instance.get_premium_license,
            type_by_possession=instance.get_type_by_possession,
            all_tbp=instance.get_all_tbp,
            mandatory_document=instance.get_mandatory_document,
            exibir_folha_ponto=instance.get_exibir_folha_ponto,
        )
        return rst

    def json(self, args=[]):
        self.response["Content-Type"] = "text/javascript"
        self.response.write('Ext._create("standard.configuration.item.Manage")')


class STDJustificationItem(STDItem):

    _model = JustificationItem

    full_text_index = ("name__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("standard.configuration.item.justification.Manage")'
        )
