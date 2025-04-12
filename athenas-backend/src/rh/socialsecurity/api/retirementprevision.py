# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.nil import nil_date
from contrib.utils import getLogger
from rh.socialsecurity.models import RetirementPrevision

log = getLogger(__name__)


class SSRetirementPrevision(RestfulDRY):

    _model = RetirementPrevision

    full_text_index = (
        "natural_person__nome__icontains",
        "last_occupation__cargo__nome__icontains",
        "last_occupation__especialidade__nome__icontains",
    )

    force_persist_boolean_fields = ["active", "negative_previous_bond"]

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.socialsecurity.RetirementPrevisionManage")'
        )

    def get_query(self):
        query = super(SSRetirementPrevision, self).get_query()
        return query.filter(
            natural_person__servidor__type_by_possession__in=[
                "EFE",
                "ECM",
                "EFC",
                "MBR",
                "MEL",
                "MCM",
                "MEC",
            ],
            natural_person__servidor__ativo=True,
        )

    def model_to_dict(self, instance):
        _dict_ = super(SSRetirementPrevision, self).model_to_dict(instance)

        if instance.last_occupation and instance.last_occupation.cargo:
            cargo = instance.last_occupation.cargo.nome
        else:
            cargo = ""

        if instance.last_occupation and instance.last_occupation.especialidade:
            especialidade = instance.last_occupation.especialidade.nome
        else:
            especialidade = ""

        _dict_.update(
            {
                "icons": instance.get_icons,
                "person_sex": instance.natural_person.sexo,
                "before_ec_20_98": instance.before_ec_20_98,
                "last_occupation_unicode": f"{cargo} - {especialidade}",
                "birth_date": nil_date(instance.natural_person.data_nascimento, None),
                "age": instance.natural_person.idade,
                "exercise_date": nil_date(instance.exercise_date, None),
                "contribution_prevision_date": nil_date(
                    instance.contribution_prevision_date, None
                ),
                "age_prevision_date": nil_date(instance.age_prevision_date, None),
                "integral_prevision_date": nil_date(
                    instance.integral_prevision_date, None
                ),
                "rgps_liquid_days": instance.rgps_liquid_days,
                "rpps_liquid_days": instance.rpps_liquid_days,
            }
        )

        return _dict_
