# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import person_from_user
from contrib.middleware import get_current_user


class FilterEvalValueMixin(object):

    def _filter_eval_value(self, value):
        rsp = Restful._filter_eval_value(self, value)

        if isinstance(rsp, str) and rsp == "__USER_PERSON__":
            rsp = person_from_user(get_current_user())
        elif isinstance(rsp, str) and rsp == "__USER__":
            rsp = get_current_user()

        return rsp
