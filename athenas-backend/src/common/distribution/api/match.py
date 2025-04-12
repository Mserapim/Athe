# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.distribution.models import Match


log = getLogger(__name__)


class CDMatch(RestfulDRY):

    _model = Match

    force_upper = False

    def model_to_dict(self, instance):
        _dict_ = super(CDMatch, self).model_to_dict(instance)

        _dict_.update({"player_title": instance.player.title})

        return _dict_
