# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from judicial.models import County, ExecutionOrgan
from django.db.models import Q


log = getLogger(__name__)


class EJudCounty(RestfulDRY):

    _model = County

    full_text_index = [
        "title__icontains",
    ]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('judicial.county.Manage')")

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        rst.update(title=instance.title, phones=instance.phones)

        return rst


class EJudCountyAPI(EJudCounty):

    full_text_index = [
        "locations__nome__unaccent__icontains",
        "title__unaccent__icontains",
    ]

    def get_query(self):
        return super().get_query().exclude(locations=None).distinct()

    def model_to_dict(self, instance):
        rst = super().model_to_dict(instance)

        county_address = None
        if instance.address:
            exclude_values = ["<br><!-- Correção de bug da ExtJS -->"]

            county_address = {
                "public_place": instance.address.logradouro or None,
                "number": instance.address.numero or None,
                "neighborhood": instance.address.bairro or None,
                "complement": (
                    instance.address.complemento
                    if instance.address.complemento not in exclude_values
                    else None
                ),
                "zip_code": instance.address.cep,
            }

        abrangency = [str(location.nome) for location in instance.locations.all()]

        eo = ExecutionOrgan.objects.filter(
            localidade__in=instance.locations.all()
        ).last()
        office_hour = eo.office_hours.description if eo.office_hours else None

        rst.update(
            coordinate=instance.coordinate,
            county_address=county_address,
            office_hour=office_hour,
            abrangency=abrangency,
        )

        return rst
