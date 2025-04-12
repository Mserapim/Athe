# -*- coding: utf-8 -*-
import json
import re
from contrib.controller import DefaultController
from contrib.utils import getLogger
from corregedoria.cirdir.models import Address, Debits, Irpf, Property
from corregedoria.reportbuilder.pdfgenerator import CreateDoc
from corregedoria.cirdir.reports import (
    EmployeeMemberPendenceReport,
    ListAddressReport,
    PendenciesReport,
    SubmittedAfterDeadlineReport,
    MemberTeachingReport,
)


log = getLogger(__name__)


class CIRDIREmployeeMemberPendenceReport(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))
            CreateDoc(reportCls=EmployeeMemberPendenceReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))


class CIRDIRSubmittedAfterDeadlineReport(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))
            doc = CreateDoc(reportCls=SubmittedAfterDeadlineReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))


class CIRDIRMemberTeachingListReport(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))
            check = re.search("^[0-9]{4}$", params.get("year_base", ""))
            if check is None:
                raise Exception("Informe um ano válido")

            for p in [
                "address",
                "property",
                "debits",
                "teaching1",
                "teaching2",
                "irpf",
            ]:
                if p in params:
                    params[p] = params.get(p, "off").lower() == "on"

            doc = CreateDoc(reportCls=MemberTeachingReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))


class CIRDIRPendenciesListReport(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))
            params.update({"parts": []})

            check = re.search("^[0-9]{4}$", params.get("year_base", ""))
            if check is None:
                raise Exception("Informe um ano válido")

            parts = {
                "address": Address.codename,
                "teaching1": "teaching_1st_semestry",
                "teaching2": "teaching_2nd_semestry",
            }

            # FIX-ME: ano de corte adocao da declaracao do irpf
            if int(params.get("year_base", 0)) <= 2021:
                parts.update(
                    {
                        "debits": Debits.codename,
                        "property": Property.codename,
                    }
                )
            else:
                parts.update({"irpf": Irpf.codename})

            for p in parts:
                if p in params:
                    add = params.get(p, "off").lower() == "on"
                    if add:
                        params["parts"] = params.get("parts") + [parts.get(p)]

            CreateDoc(reportCls=PendenciesReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))


class CIRDIRAddressListReport(DefaultController):

    def start(self, args=[]):
        rst = {"success": False, "message": "Nada feito ainda!"}

        try:
            params = json.loads(self.request.POST.get("params"))

            check = re.search("^[0-9]{4}$", params.get("year_base", ""))
            if check is None:
                raise Exception("Informe um ano válido")

            CreateDoc(reportCls=ListAddressReport, params=params)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(
                success=True,
                message="Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.",
            )

        self.response["Content-Type"] = "text/json"
        self.response.write(json.dumps(rst))
