# -*- coding: utf-8 -*-
import json
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.nil import nil_display, nil_unicode
from django.db import transaction
from judicial.models import (
    RequestCollaboration,
    RequestCollaborationPerson,
    RequestCollaborationGeneralOrgan,
)
from judicial.api.mixins import FilterEvalValueMixin

log = getLogger(__name__)


class EJudRequestCollaboration(FilterEvalValueMixin, RestfulDRY):

    _model = RequestCollaboration

    def model_to_dict(self, instance):
        _dict_ = super(EJudRequestCollaboration, self).model_to_dict(instance)

        _dict_.update(
            {
                "target": instance.my_origin.target.nome,
                "lawsuit_cache_number": instance.lawsuit.cache_number,
                "type_lawsuit_display": nil_display(
                    instance.lawsuit, "type_lawsuit", None
                ),
                "protocol": instance.protocol.codigo if instance.protocol else "-",
            }
        )

        return _dict_

    def inactivate(self, *args):
        response = {"success": False, "message": "Nada foi feito ainda."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                log.debug(self.request.PUT.getlist("pkset"))
                for rc in RequestCollaboration.objects.filter(
                    pk__in=self.request.PUT.getlist("pkset"), canceled_by__isnull=True
                ):
                    rc.inactivate()
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Requisições inativadas com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))


class EJudRequestCollaborationPerson(EJudRequestCollaboration):

    _model = RequestCollaborationPerson


class EJudRequestCollaborationGeneralOrgan(EJudRequestCollaboration):

    _model = RequestCollaborationGeneralOrgan
