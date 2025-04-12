import json
from datetime import datetime

from django.contrib.auth.models import Permission
from django.db import transaction
from django.db.models import Q

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
from edocs.protocolo.models import Protocolo

log = getLogger(__name__)


class DAControlType(RestfulDRY):
    _model = ControlType

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    # Força a persistência de boolean fields vindos do form
    force_persist_boolean_fields = ["is_secret", "not_allow_admin_access"]

    def allowed_control_types(self, args=[]):
        """Devolve somente os tipos de controles permitidos para o usuário corrente."""
        result = {"success": False, "message": "Nothing done yet."}

        try:
            current_user_permissions = Permission.objects.filter(
                content_type__app_label="document_access",
                group__user=get_current_user(),
            )
            control_types = self.Model.objects.filter(
                required_permission__in=current_user_permissions
            )
        except Exception as e:
            log.exception(e)
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Ação realizada com sucesso.",
                count=control_types.count(),
                collection=[
                    {"pk": control_type.pk, "title": control_type.title}
                    for control_type in control_types
                ],
            )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(result))

    def model_to_dict(self, instance):
        _dict_ = super(DAControlType, self).model_to_dict(instance)

        _dict_.update(
            {
                "required_permission_unicode": (
                    instance.required_permission.name
                    if instance.required_permission
                    else None
                )
            }
        )

        return _dict_

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.document_access.controltype.Manage")')


class DAControlTypeByUser(DAControlType):
    def get_query(self, *args, **kwargs):
        current_user_permissions = Permission.objects.filter(
            content_type__app_label="document_access", group__user=get_current_user()
        )

        criteria_1 = Q(enabled=True)
        criteria_2 = Q(required_permission__in=current_user_permissions)

        # Tipo de controle já aplicado.
        control_type_id = self.request.GET.get("control_type", None)
        if control_type_id:
            criteria_1.add(Q(pk=control_type_id), conn_type="OR")
            criteria_2.add(Q(pk=control_type_id), conn_type="OR")

        return super().get_query(*args, **kwargs).filter(criteria_1).filter(criteria_2)
