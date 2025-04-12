# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from edocs.protocolo.models import Movimentacao as Movement


log = getLogger(__name__)


class EDOCMovement(RestfulDRY):

    _model = Movement

    full_text_index = (
        "protocolo__codigo__icontains",
        "lotacao_origem__nome__icontains",
        "lotacao_destino__nome__icontains",
        "lotacao_origem__descricao__icontains",
        "lotacao_destino__descricao__icontains",
        "lotacao_origem__abreviacao__icontains",
        "lotacao_destino__abreviacao__icontains",
        "lotacao_origem__sigla__icontains",
        "lotacao_destino__sigla__icontains",
        "servidor_origem__pessoa_fisica__nome__icontains",
        "servidor_destino__pessoa_fisica__nome__icontains",
        "parecer__icontains",
    )

    force_upper = False

    force_persist_boolean_fields = [
        "deferido",
        "encaminhado",
        "urgente",
        "physical",
        "with_workflow",
    ]

    def model_to_dict(self, instance):
        _dict_ = super(EDOCMovement, self).model_to_dict(instance)

        _dict_.update(
            {
                "pessoa_fisica_origem_unicode": instance.servidor_origem.pessoa_fisica.nome,
                "pessoa_fisica_destino_unicode": (
                    instance.servidor_destino.pessoa_fisica.nome
                    if instance.servidor_destino
                    else ""
                ),
            }
        )

        return _dict_
