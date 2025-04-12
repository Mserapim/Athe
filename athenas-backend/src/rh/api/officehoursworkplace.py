# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from rh.models import OfficeHoursWorkplace, Workplace


class RHOfficeHoursWorkplace(RestfulDRY):

    _model = OfficeHoursWorkplace

    force_upper = False

    full_text_index = ("description__icontains",)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.officehoursworkplace.Manage")')

    def apply_all(self, args=[]):
        rst = {"message": "Nada foi feito ainda.", "success": False}
        office_hours = self.request.POST.get("office_hours_pk")
        if office_hours:
            try:
                self._model.objects.get(id=office_hours)
            except Exception as e:
                rst.update(message={e})
            else:
                Workplace.objects.filter(ativo=True).update(office_hours=office_hours)
                rst.update(
                    message="Horários de Expediente atualizados com sucesso",
                    success=True,
                )

        self.renderer(rst)
