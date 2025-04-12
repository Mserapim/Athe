# -*- coding: utf-8 -*-
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from contrib.utils import employee_from_user, getLogger

log = getLogger("websocket")


class DefaultConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope["user"]
        if self.user.pk:
            self.user_group_name = "user_id_%d" % self.user.pk
            async_to_sync(self.channel_layer.group_add)(
                self.user_group_name,
                self.channel_name,
            )

            employee = employee_from_user(self.user)
            for work_location in employee.work_assignment_effective_exercise:
                if work_location.lotacao:
                    group_name = "work_location_id_%d" % work_location.lotacao.pk
                    async_to_sync(self.channel_layer.group_add)(
                        group_name,
                        self.channel_name,
                    )

        else:
            self.user_group_name = None

        async_to_sync(self.channel_layer.group_add)(
            "main",
            self.channel_name,
        )

        self.accept()

    def disconnect(self, close_code):
        if self.user_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.user_group_name,
                self.channel_name,
            )

        async_to_sync(self.channel_layer.group_discard)(
            "main",
            self.channel_name,
        )

    def bus_control(self, event):
        self.send(text_data=event.get("content", "{}"))
