# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import time
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import ServidorLotacao
from rh.pvf.models import PortalRequestSubstitute
from contrib.decorator import login_required


log = getLogger(__name__)


class PortalRequestSubstituteApi(RestfulDRY):

    _model = PortalRequestSubstitute

    def get_query(self):
        query = super(PortalRequestSubstituteApi, self).get_query()
        return query.filter(exercise__lotacao__electoral_zone=False)

    @login_required("JSON")
    def validate_substitute(self, params):
        """Validar se o substituto tem usufutos ou afastamento programdos"""

        rst = {"message": "nada foi feito ainda.", "success": False}
        try:
            can = self.check_permission(
                self.request.user,
                "add",
                self.Model._meta.app_label,
                self.Model._meta.object_name,
            )
            if can is False:
                rst.update(
                    message="Você não tem permissão para criar %s."
                    % self.Model._meta.object_name
                )
            else:
                instance = self._model()
                substitute = {
                    "start_date": self.request.GET.get("start_date", None),
                    "end_date": self.request.GET.get("end_date", None),
                    "substitute": self.request.GET.get("substitute_id", None),
                }
                exercise_id = self.request.GET.get("exercise_id", None)
                exercice = ServidorLotacao.objects.filter(pk=exercise_id).first()
                data_vigencia = None
                if (
                    exercice.data_vigencia_fim
                    and exercice.data_vigencia_fim
                    < datetime.strptime(
                        self.request.GET.get("end_date"), "%d/%m/%Y"
                    ).date()
                ):
                    data_vigencia = exercice.data_vigencia_fim.strftime("%d/%m/%Y")
                instance.validate_absence_schedule(substitute)
                rst.update(
                    success=True,
                    new_end_date=data_vigencia,
                    message="Validado com sucesso.",
                )
        except Exception as e:
            rst.update(message="{}".format(e))

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.pvf.portalrequestsubstitute.Manage")')
