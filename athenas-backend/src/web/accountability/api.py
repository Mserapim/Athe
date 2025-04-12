# -*- coding:utf-8 -*-

from django.http import HttpResponseNotAllowed
from contrib.decorator import is_public
from contrib.newrest import RestfulDRY
from edocs.protocolo.models import TipoDocumento
from .models import DocumentCache


class AccountabilityRestful(RestfulDRY):
    _model = DocumentCache
    force_upper = False

    @is_public()
    def v1(self, args=[]):
        if self.request.method != "GET":
            self.response = HttpResponseNotAllowed(
                ["GET"], reason="Method not allowed. Only allowed method is GET."
            )
            self.response.write("Operação não permitida")
        else:
            super(AccountabilityRestful, self).v1(args)
