# -*- coding: utf-8 -*-
import re

from contrib.utils import getLogger
from auth.jwt.models import Voucher


log = getLogger(__name__)


lex_authorization = re.compile("^(?P<auth>[A-Z]+)\s+(?P<token>.*)$")


class Backend:

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        response = response or self.get_response(request)
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response

    def process_request(self, request):
        try:
            result = lex_authorization.match(request.META.get("HTTP_AUTHORIZATION", ""))
            if result:
                auth_type = result.groupdict().get("auth")
                auth_key = result.groupdict().get("token")

                if auth_type == "JWT":
                    Voucher.use(request)
        except Exception as e:
            log.exception(e)

    def process_response(self, request, response):
        return response
