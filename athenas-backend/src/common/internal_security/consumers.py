from channels import Group
from channels.sessions import channel_session, http_session
from contrib.utils import getLogger


log = getLogger(__name__)


@http_session
@channel_session
def ws_connect(message):
    Group("main").add(message.reply_channel)
    message.reply_channel.send({"accept": True})


@http_session
@channel_session
def ws_message(message):
    log.info(message.content.get("text"))


@channel_session
def ws_disconnect(message):
    Group("main").discard(message.reply_channel)
