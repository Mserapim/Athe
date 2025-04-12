# -*- coding: utf-8 -*-

from contrib.utils import getLogger, DateUtils, employee_from_user
from edocs.protocolo.requestform.models import Resignation
from edocs.protocolo.api.manage import EDOCManage
from rh.models import MovimentacaoPosse as PossessionMovement


log = getLogger(__name__)


class RequestFormResignation(EDOCManage):

    _model = Resignation

    def prepare_params(self, querydict):
        params = super(RequestFormResignation, self).prepare_params(querydict)

        try:
            params.update(
                possession=PossessionMovement.objects.get(pk=params.get("possession"))
            )
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo Cargo.")

        try:
            params.update(start_date=DateUtils.str_to_date(params.get("start_date")))
        except Exception:
            raise Exception("Por favor, preencha corretamente o campo Data de início.")

        return params

    def model_to_dict(self, instance):
        data = super(RequestFormResignation, self).model_to_dict(instance)

        form = instance.protocolo.resignation

        data.update(
            {
                "start_date": (
                    DateUtils.date_to_str(form.start_date)
                    if form.start_date is not None
                    else ""
                ),
                "possession": form.possession.pk if form.possession is not None else "",
            }
        )

        return data

    def active_possessions(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing done yet.",
            "count": 0,
            "collection": [],
        }

        try:
            employee = employee_from_user(self.request.user)

            result.update(
                success=True,
                message="Data found successfully.",
                count=employee.posses_ativas.count(),
                collection=[
                    {
                        "pk": possession.pk,
                        "description": str(possession.my_origin.description_possession),
                    }
                    for possession in employee.posses_ativas
                ],
            )
        except Exception as e:
            result.update(message=str(e))

        self.renderer(result)
