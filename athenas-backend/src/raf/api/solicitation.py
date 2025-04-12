# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from raf.models import Solicitation, FunctionalActivityReport

log = getLogger(__name__)


class RAFSolicitation(Restful):

    force_upper = False

    _model = Solicitation

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.solicitation.Manage")')

    def register_reopening(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}
        try:

            pk = int(self.request.POST.get("raf", 0))
            raf = FunctionalActivityReport.objects.get(pk=pk)
            self._model.register(raf=raf, kind=self._model.KIND_REOPENING)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Solicitação realizada com sucesso.")

        return self.renderer(rst)

    def accept_reopen(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito."}

        try:
            pk = int(self.request.POST.get("solicitation", 0))

            instance = self._model.objects.get(pk=pk)
            instance.accept()

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Ação realizada com sucesso.")

        return self.renderer(rst)
