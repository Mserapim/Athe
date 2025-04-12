# -*- coding: utf-8 -*-
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from contrib.utils import getLogger


log = getLogger(__name__)


class WSAuthBackend(ModelBackend):

    def authenticate(self, request, username, password):
        from auth.ws.models import Application, UserPermission

        user = None

        try:
            app = Application.objects.get(app_key=username)
        except Application.DoesNotExist:
            pass
        else:
            try:
                user_perm = app.users.get(user_token=password)
            except UserPermission.DoesNotExist:
                user = None
            else:
                user = user_perm.user

        return user

    def get_user(self, user_id):
        user = None

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            self.log.critical("Usuário não existe na base de dados.")
            user = None

        return user
