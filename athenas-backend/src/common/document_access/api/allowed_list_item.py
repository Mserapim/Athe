import json
from datetime import datetime

from django.contrib.auth.models import Permission
from django.db import transaction

from common.document_access.models import (
    Control,
    ControlType,
    DocumentType,
    Log,
    ProtocolControl,
    AllowedListItem,
)
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_unicode
from contrib.utils import DateUtils, getLogger, person_from_user

log = getLogger(__name__)


class DAAllowedListItem(RestfulDRY):

    _model = AllowedListItem

    def model_to_dict(self, instance):
        _dict_ = super(DAAllowedListItem, self).model_to_dict(instance)

        revoked_by_unicode = ""
        if instance.revoked_by:
            revoked_by_unicode = nil_unicode(
                person_from_user(instance.revoked_by), instance.revoked_by.__str__()
            ).title()

        _dict_.update(
            {
                "granted_by_unicode": nil_unicode(
                    person_from_user(instance.granted_by), instance.granted_by.__str__()
                ).title(),
                "revoked_by_unicode": revoked_by_unicode,
            }
        )

        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.document_access.allowedlistitem.Manage")'
        )

    def revoke(self, *args):
        response = {"success": False, "message": "Ainda não foi realizado nada."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                for obj in self._model.objects.filter(
                    pk__in=self.request.PUT.getlist("pk_set")
                ):
                    obj.revoke()
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))
