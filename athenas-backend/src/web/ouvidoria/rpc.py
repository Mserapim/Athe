# -*- coding:utf-8 -*-

from contrib.controller import JsonResponseController
from contrib.decorator import is_public
from .models import load_personal_data


class OmbudsmanRPC(JsonResponseController):

    @is_public()
    def person_data(self, args=[]):
        params = {
            "cpf": self.request.GET.get("cpf"),
            "cnpj": self.request.GET.get("cnpj"),
        }

        data = load_personal_data(**params)

        return self.render(data)
