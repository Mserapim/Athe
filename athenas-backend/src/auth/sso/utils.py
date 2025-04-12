from django.conf import settings
from django.contrib.auth import get_user_model
from requests_oauthlib.oauth2_session import OAuth2Session


def oauth_session(
    token=None,
    client_id=settings.OAUTH_CLIENT_ID,
    redirect_uri=settings.OAUTH_CALLBACK_URL,
    auto_refresh_url=settings.OAUTH_SERVER + settings.OAUTH_REFRESH_TOKEN_URL,
    scope=getattr(settings, "OAUTH_SCOPE", None),
    **kwargs
):

    return OAuth2Session(
        client_id=client_id,
        redirect_uri=redirect_uri,
        auto_refresh_url=auto_refresh_url,
        token=token,
        scope=scope,
        **kwargs
    )


def get_login_url():
    oauth = oauth_session()
    auth_url = settings.OAUTH_SERVER + settings.OAUTH_AUTHORIZATION_URL
    authorization_url, state = oauth.authorization_url(auth_url, approval_prompt="auto")
    return dict(authorization_url=authorization_url, state=state)


def sync_user(user, userdata):
    is_modified = False
    for key in ["email", "first_name", "last_name"]:
        if getattr(user, key) != userdata[key]:
            is_modified = True
            setattr(user, key, userdata[key])

    if is_modified:
        user.save()


def create_user(userdata):
    user_model = get_user_model()

    user, is_new = user_model.objects.get_or_create(
        username=userdata["username"],
        defaults={
            "email": userdata["email"],
            "first_name": userdata["first_name"],
            "last_name": userdata["last_name"],
            "is_staff": True,
        },
    )

    return user, is_new
