# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger, get_json_engine
from auditlog.models import LogEntry
from django.contrib.contenttypes.models import ContentType


log = getLogger(__name__)
json = get_json_engine()


class AuditLogEntry(RestfulDRY):

    _model = LogEntry

    full_text_index = ("object_id__iexact", "actor__username__iexact")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("auditoria.auditlog.Manage")')

    def model_to_dict(self, instance):
        import json

        _dict_ = super(AuditLogEntry, self).model_to_dict(instance)

        _dict_.update(
            {
                "action": instance.get_action_display(),
                # 'changes':json.dumps(json.loads(instance.changes)),
                "changes": json.dumps(instance.changes),
                "object_id": instance.object_id,
                "timestamp": instance.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                "user": instance.actor.username if instance.actor else "",
                "model": instance.content_type.model,
            }
        )

        return _dict_


class AuditContentType(RestfulDRY):

    _model = ContentType

    full_text_index = ("model__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("auditoria.auditlog.ContentTypeManage")')
