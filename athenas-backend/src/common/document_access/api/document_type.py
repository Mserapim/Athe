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


class DADocumentType(RestfulDRY):
    _model = DocumentType

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("title__icontains", "slug__icontains", "description__icontains")

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.document_access.documenttype.Manage")')
