import json

from channels import Group
from channels.sessions import channel_session, http_session
from contrib.utils import getLogger
from channels.auth import channel_session_user, channel_session_user_from_http


log = getLogger("websocket")


@channel_session_user_from_http
def ws_connect(message):
    try:
        if message.user and message.user.pk:
            Group("user-id-%d" % message.user.pk).add(message.reply_channel)
    except Exception as e:
        log.exception(e)

    Group("main").add(message.reply_channel)
    message.reply_channel.send({"accept": True, "close": False})


@channel_session_user
def ws_message(message):
    pass


@channel_session_user
def ws_disconnect(message):
    try:
        if message.user:
            Group("user-id-%d" % message.user.pk).discard(message.reply_channel)
    except Exception as e:
        log.exception(e)

    Group("main").discard(message.reply_channel)
