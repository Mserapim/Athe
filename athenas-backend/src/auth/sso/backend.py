from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

from .utils import oauth_session, sync_user, create_user

from contrib.utils import getLogger

log = getLogger(__name__)


class SSOAuthBackend(ModelBackend):

    def _extract_userdata(self, response):
        return response.json()

    def _sync_user(self, user, userdata):
        sync_user(user, userdata)

    def _create_user(self, userdata):
        return create_user(userdata)

    def authenticate(self, request=None, code=None, redirect_uri=None):
        if redirect_uri is None:
            oauth = oauth_session()
        else:
            oauth = oauth_session(redirect_uri=redirect_uri)

        try:
            token = oauth.fetch_token(
                settings.OAUTH_SERVER + settings.OAUTH_TOKEN_URL,
                code=code,
                client_secret=settings.OAUTH_CLIENT_SECRET,
                verify=settings.OAUTH_VERIFY_SSL,
            )

            _request = oauth.get(settings.OAUTH_SERVER + settings.OAUTH_RESOURCE_URL)

        except InvalidGrantError as invalid_grant_error:
            log.error("Erro na requisição para verificação do token")
            log.error(invalid_grant_error)
            return None

        if _request.status_code != 200:
            log.warning("Erro na consulta dos dados do usuário")
            return None

        userdata = self._extract_userdata(_request)

        if not userdata or "email" not in userdata or "username" not in userdata:
            log.warning(
                "Nome de usuário e email não retornados pelo servidor de autenticação"
            )
            return None

        user, created = self._create_user(userdata)
        self._sync_user(user, userdata)

        user.oauth_token = token

        return user
