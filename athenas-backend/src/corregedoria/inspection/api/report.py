# -*- coding: utf-8 -*-
import json
import re
from contrib.controller import DefaultController
from contrib.utils import getLogger
from corregedoria.reportbuilder.pdfgenerator import CreateDoc
from corregedoria.inspection.reports import HistoryInspectionReport


class INSPECTIONHistoryInspection(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))

            doc = CreateDoc(reportCls=HistoryInspectionReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))
