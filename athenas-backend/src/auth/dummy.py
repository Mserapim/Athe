# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from django.contrib.auth import backends
from django.contrib.auth.models import User
from django.conf import settings

log = getLogger(__name__)


class Backend(backends.ModelBackend):

    def password_check(self, password):
        dummy_password = getattr(settings, "AUTH_DUMMY_PASSWORD", None)
        log.debug(
            "%s == %s -> %s", dummy_password, password, dummy_password == password
        )

        return True if dummy_password is None else (dummy_password == password)

    def authenticate(self, request, username=None, password=None):
        log.info("Auth with username %s" % username)
        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            user = User()
            log.warn("The user %s not found or not active." % username)
        except Exception as e:
            user = None
            log.exception(e)
        finally:
            return user if self.password_check(password) is True else None

    def get_user(self, user_id):
        """
        Metodo responsável por retorna um usuário de acordo com seu user_id.
        :param user_id Identificador do usuário.
        :return Caso consegui encontrar o usuário retorna, caso contrario retorna None.
        """
        user = None

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None
        finally:
            if not user:
                log.warn("User not found with id %s" % user_id)
            return user
