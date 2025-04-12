import base64
import jwt
import logging
import time
from django.conf import settings
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin

from .utils import oauth_session, sync_user

from django.contrib.auth.models import User

from contrib.utils import getLogger

log = getLogger(__name__)


class OAuthMiddleware(MiddlewareMixin):

    def _sync_user(self, user, userdata):
        sync_user(user, userdata)

    def process_request(self, request):

        if settings.USE_SSO and "MPTO.SSO.Token" not in request.COOKIES:
            request_service = request.headers.get("X-SERVICE-TOKEN-ALLOWED", "")
            if request_service != getattr(settings, "SERVICE_TOKEN_ALLOWED"):
                logout(request)

        sync_frequency = getattr(settings, "OAUTH_USER_SYNC_FREQUENCY", 3600)

        if not sync_frequency:
            return

        if "oauth_token" not in request.session:
            return

        token = request.session["oauth_token"]

        if not token or time.time() > token["expires_at"]:
            return

        oauth = oauth_session(token=token)

        _request = oauth.get(
            settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL,
            verify=settings.OAUTH_VERIFY_SSL,
        )

        if _request.status_code == 403:
            return logout(request)

        if _request.status_code != 200:
            return

        if token != oauth.token:
            request.session["oauth_token"] = oauth.token

        userdata = _request.json()

        if not userdata or "username" not in userdata:
            return

        if userdata["username"] != request.user.username:
            return logout(request)

        # no nosso contexto não é necessário atualizar as informações de usuário com tanta frequencia.
        # self._sync_user(request.user, userdata)
        request.session["oauth_user_data"] = dict(synced_at=time.time())

        return


class SSOMiddleware:

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
        if request.user.is_authenticated:
            return

        authorization = request.headers.get("Authorization")
        if not authorization:
            return

        token = authorization.split(" ")[-1]

        try:
            public_key = settings.SSO_PUBLIC_KEY
            payload = jwt.decode(token, key=public_key, algorithms=["RS256"])
            user = User.objects.get(username=payload["username"])

            if user and user.is_active:
                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )

        except User.DoesNotExist:
            pass
        except Exception as e:
            log.exception(e)
