import json

from contrib.utils import getLogger

log = getLogger("websocket")

try:
    from channels import Group
except ImportError:
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer

    class Group(object):

        def __init__(self, name):
            self._name = name

        def send(self, data):
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                self._name, {"type": "bus_control", "content": data.get("text")}
            )


class RemoteEmmiter(object):

    @classmethod
    def _send_to_target(klass, target, data):
        try:
            Group(target).send({"text": json.dumps(data)})
        except Exception as e:
            log.exception(e)

    @classmethod
    def _send(klass, targets, data):
        for target in klass._iter_targets(targets):
            log.info(
                'Send event "%s" to "%s"',
                data.get("event", "__undefined_event__"),
                target,
            )
            log.debug(json.dumps(data.get("options"), indent=2))

            klass._send_to_target(target, data)

    @classmethod
    def _iter_targets(klass, targets):
        if not isinstance(targets, list):
            targets = [targets]

        for target in targets:
            yield target

    @classmethod
    def emmit(klass, targets, name, options):
        event = {"event": name, "options": options}

        klass._send(targets, event)

    @classmethod
    def emmit_for_user(klass, user, name, **options):
        klass.emmit("user_id_%d" % (user.pk), name, options)

    @classmethod
    def emmit_for_worklocation(klass, lotacao, name, **options):
        klass.emmit("work_location_id_%d" % (lotacao.pk), name, options)

    @classmethod
    def raw_emmit(klass, targets, data):
        klass._send(targets, data)
