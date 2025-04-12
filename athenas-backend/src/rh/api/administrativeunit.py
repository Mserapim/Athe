# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import (
    AdministrativeUnitConfig,
    EstablishmentConfig,
    TaxAllocationConfig,
    UnidadeAdministrativa,
)


class RHAdministrativeUnitRestful(RestfulDRY):

    _model = UnidadeAdministrativa

    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
        "abreviacao__icontains",
        "sigla__icontains",
    )

    # exclude_fields = ['orgaogeral_ptr']

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.administrativeunit.Manage")')

    def model_to_dict(self, instance):
        _dict_ = super(RHAdministrativeUnitRestful, self).model_to_dict(instance)

        _dict_.update({"orgaogeral_ptr": "%s" % instance.orgaogeral_ptr})

        return _dict_


class RHAdministrativeUnitConfigRestful(RestfulDRY):

    _model = AdministrativeUnitConfig

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.administrativeunit.config.Manage")')


class RHEstablishmentConfigRestful(RestfulDRY):

    _model = EstablishmentConfig

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.administrativeunit.config.establishment.Manage")'
        )


class RHTaxAllocationConfigRestful(RestfulDRY):

    _model = TaxAllocationConfig

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.administrativeunit.config.taxallocation.Manage")'
        )
