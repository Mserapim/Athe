# -*- coding: utf-8 -*-
import json

from contrib.utils import getLogger
from auth.ws.models import Application, UserPermission
from django.contrib.auth import login

log = getLogger(__name__)


class WSAuthenticatorBackend:

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        response = response or self.get_response(request)
        return response

    def process_request(self, request):
        try:
            app_key, user_token = request.META.get("HTTP_AUTHORIZATION", ":").split(":")

            if app_key and user_token:
                app = Application.objects.get(app_key=app_key)
                user_permission = app.users.get(user_token=user_token, active=True)

                if user_permission.user.is_active:
                    user_permission.user.backend = "WSAuthenticatorBackend"
                    login(request, user_permission.user)
                else:
                    log.info("Usuário não esta ativo")
        except Application.DoesNotExist as e:
            log.info(">>>>> APP_KEY NOT EXIST: %s" % app_key)
        except ValueError:
            pass
        except Exception as e:
            log.exception(e)
