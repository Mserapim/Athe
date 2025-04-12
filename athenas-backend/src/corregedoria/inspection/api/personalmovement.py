# -*- coding: utf-8 -*-
from django.db.models import Q

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import (
    MovimentacaoPessoal as PersonalMovement,
    MovimentacaoPosse as PossessionMovement,
)

from corregedoria.utils import format_category_employee

log = getLogger(__name__)


class INSPECTIONPersonalMovement(RestfulDRY):

    force_upper = False

    full_text_index = ("servidor__pessoa_fisica__nome__icontains",)

    _model = PersonalMovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.personalmovement.Launcher")'
        )


class INSPECTIONEffetivePossessionMovement(INSPECTIONPersonalMovement):

    force_upper = False

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "quadro__cargo__nome__icontains",
    )

    _model = PossessionMovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.personalmovement.Launcher")'
        )

    def get_query(self):
        query = (
            super(INSPECTIONEffetivePossessionMovement, self)
            .get_query()
            .filter(ativo=True, quadro__cargo__tipo_lei_cargo__in=["EF", "FC"])
            .order_by("servidor__pessoa_fisica__nome")
        )

        return query

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONEffetivePossessionMovement, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "employee_unicode": instance.servidor.pessoa_fisica.nome,
                "occupation_unicode": instance.quadro.cargo.nome,
            }
        )
        return _dict_


class INSPECTIONCommissionedPossessionMovement(INSPECTIONPersonalMovement):

    force_upper = False

    full_text_index = (
        "servidor__pessoa_fisica__nome__icontains",
        "quadro__cargo__nome__icontains",
    )

    _model = PossessionMovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.personalmovement.Launcher")'
        )

    def get_query(self):
        query = (
            super(INSPECTIONCommissionedPossessionMovement, self)
            .get_query()
            .filter(ativo=True, quadro__cargo__tipo_lei_cargo__in=["CM"])
            .order_by("servidor__pessoa_fisica__nome")
        )

        return query

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONCommissionedPossessionMovement, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "employee_unicode": instance.servidor.pessoa_fisica.nome,
                "occupation_unicode": instance.quadro.cargo.nome,
            }
        )
        return _dict_


class INSPECTIONExternalPossessionMovement(INSPECTIONPersonalMovement):

    force_upper = False

    full_text_index = ("servidor__pessoa_fisica__nome__icontains",)

    _model = PersonalMovement

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("corregedoria.inspection.inspection.filling.structure.personalmovement.Launcher")'
        )

    def get_query(self):
        query = (
            super(INSPECTIONExternalPossessionMovement, self)
            .get_query()
            .filter(
                Q(
                    movimentacaoposse__requestmove__isnull=False,
                    movimentacaoposse__ativo=True,
                )
            )
            .order_by("servidor__pessoa_fisica__nome")
        )
        return query

    def model_to_dict(self, instance):
        _dict_ = super(INSPECTIONExternalPossessionMovement, self).model_to_dict(
            instance
        )
        _dict_.update(
            {
                "employee_unicode": instance.servidor.pessoa_fisica.nome,
                "occupation_unicode": (
                    instance.movimentacaoposse.quadro.cargo.nome
                    if PossessionMovement.objects.filter(pk=instance.pk).exists()
                    else None
                ),
                "category": format_category_employee(instance.servidor.categoria_cache),
                # 'category': instance.servidor.categoria_cache,
            }
        )
        return _dict_
