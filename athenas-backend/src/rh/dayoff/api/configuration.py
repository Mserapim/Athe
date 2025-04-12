# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.dayoff.models import (
    ConfiguracaoPlantaoEleitoral,
    Configuration,
    ConfigurationSale,
)


log = getLogger(__name__)


class DAYOFFConfiguration(RestfulDRY):

    _model = Configuration

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

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

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.configuration.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            # type_employees_cache=instance.type_employees_cache
        )

        return rst


class DAYOFFConfigurationSale(RestfulDRY):

    _model = ConfigurationSale

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.dayoff.configuration.sale.Manage")')

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)
        return rst


class DAYOFFConfiguracaoPlantaoEleitoral(RestfulDRY):

    _model = ConfiguracaoPlantaoEleitoral

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.dayoff.configuration.plantao_eleitoral.Manage")'
        )

    def model_to_dict(self, instance):
        rst = RestfulDRY.model_to_dict(self, instance)

        rst.update(
            icons_ativo=self.get_icons_ativo(instance),
        )

        return rst

    def get_icons_ativo(self, instance):
        icon_ativo = "icon-status" if instance.ativo else "icon-status-busy"
        icon = f"icon-fopag {icon_ativo}"
        status = "Ativo" if instance.ativo else "Inativo"
        icons_ativo = [
            {
                "iconCls": icon,
                "title": status,
                "alt": status,
            }
        ]

        return icons_ativo
