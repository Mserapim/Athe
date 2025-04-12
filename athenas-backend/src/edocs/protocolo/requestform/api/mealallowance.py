# -*- coding: utf-8 -*-

from contrib.utils import getLogger
from edocs.protocolo.requestform.models import MealAllowance
from edocs.protocolo.api.manage import EDOCManage


log = getLogger(__name__)


class RequestFormMealAllowance(EDOCManage):

    _model = MealAllowance

    def prepare_params(self, querydict):
        params = super(RequestFormMealAllowance, self).prepare_params(querydict)

        if not params.get("email", ""):
            raise Exception("Por favor, preencha corretamente o campo Email.")

        if not params.get("working_time", ""):
            raise Exception("Por favor, preencha corretamente o campo Carga horária.")

        try:
            params.update(option_term=int(params.get("option_term", "")))
        except ValueError:
            raise Exception("Por favor, preencha corretamente o campo Termo de opção.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormMealAllowance, self).model_to_dict(instance)

        form = instance.protocolo.mealallowance

        data.update(
            {
                "working_time": form.working_time or "",
                "email": form.email or "",
                "previous_public_institution": form.previous_public_institution or "",
                "contact_number": form.contact_number or "",
                "option_term": form.option_term if form.option_term is not None else "",
            }
        )

        return data
