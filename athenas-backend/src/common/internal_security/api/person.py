# -*- coding: utf-8 -*-
from rh.api.person import RHPersonRestful
from contrib.utils import getLogger
from common.internal_security.models import EmotionalState


log = getLogger(__name__)


class ISecPerson(RHPersonRestful):

    def emotionalstate(self, person):
        query = EmotionalState.objects.filter(person=person).order_by("-reported_at")
        if query.exists():
            return query.first().emotional_state
        else:
            return 0

    def model_to_dict(self, instance):
        data = super(ISecPerson, self).model_to_dict(instance)
        data.update(emotionalstate=self.emotionalstate(instance))
        return data
