from time import time, sleep

from django.conf import settings
from django.contrib.auth import login as auth_login, authenticate, logout
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from contrib.utils import getLogger
from .utils import get_login_url

log = getLogger(__name__)


def login_redirect(request):
    request.session["next"] = request.GET.get("next", settings.LOGIN_REDIRECT_URL)
    urldata = get_login_url()
    request.session["oauth_login_state"] = urldata["state"]
    return redirect(urldata["authorization_url"])


def login_callback(request):

    if "code" not in request.GET:
        log.info("No code in request")
        raise PermissionDenied

    if "state" not in request.GET:
        log.info("No state in request")
        raise PermissionDenied

    user = authenticate(request=request, code=request.GET["code"])

    if user is not None and user.is_active:
        auth_login(request, user)
        request.session["oauth_token"] = getattr(user, "oauth_token", None)
        request.session["oauth_user_data"] = dict(synced_at=time())

        sleep(0.5)
        return redirect(settings.ATHENAS)

    return login_redirect(request)
