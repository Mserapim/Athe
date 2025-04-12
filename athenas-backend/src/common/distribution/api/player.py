# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.distribution.models import Player


log = getLogger(__name__)


class CDPlayer(RestfulDRY):

    _model = Player

    force_upper = False

    full_text_index = "title__icontains"

    def get_params(self, *args, **kwargs):
        params = super(CDPlayer, self).get_params(*args, **kwargs)

        # O end-user não pode modificar os scores.
        if "score" in params:
            params.pop("score")

        return params

    def model_to_dict(self, instance):
        _dict_ = super(CDPlayer, self).model_to_dict(instance)

        # O end-user não pode ver os scores.
        _dict_.pop("score")

        return _dict_
