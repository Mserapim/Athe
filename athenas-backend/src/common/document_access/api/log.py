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


class DALog(RestfulDRY):

    _model = Log

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem informações", "appends": []},
        }

        try:
            control = self._model.objects.get(pk=args[0])

            rst.update(
                success=True, document={"content": control.rendered, "appends": []}
            )
        except self.Model.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def model_to_dict(self, instance):
        dict_ = super(DALog, self).model_to_dict(instance)

        dict_.update(
            signed_by_unicode=nil_unicode(
                person_from_user(instance.signed_by), instance.signed_by.__str__()
            ).title()
        )

        return dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.document_access.log.Manage")')
