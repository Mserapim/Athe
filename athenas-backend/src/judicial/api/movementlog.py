# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from judicial.models import MovementLog
from contrib.utils import employee_from_user


class EJudMovementLog(RestfulDRY):

    _model = MovementLog

    full_text_index = (
        "from_location__nome__icontains",
        "from_location__descricao__icontains",
        "from_location__abreviacao__icontains",
        "from_location__sigla__icontains",
        "sended_by__pessoa_fisica__nome__icontains",
        "to_location__nome__icontains",
        "to_location__descricao__icontains",
        "to_location__abreviacao__icontains",
        "to_location__sigla__icontains",
        "received_by__pessoa_fisica__nome__icontains",
    )

    def user_to_str(self, user):
        _user_to_str = None

        if user:
            _user_to_str = employee_from_user(user, only_active=False)
            if _user_to_str:
                _user_to_str = _user_to_str.pessoa_fisica.nome
            elif user.get_full_name():
                _user_to_str = user.get_full_name()
            else:
                _user_to_str = str(user)

        return _user_to_str

    def model_to_dict(self, instance):
        _dict_ = super(EJudMovementLog, self).model_to_dict(instance)

        _dict_.update(
            {
                "sended_by_unicode": self.user_to_str(instance.sended_by),
                "received_by_unicode": self.user_to_str(instance.received_by),
            }
        )

        return _dict_
