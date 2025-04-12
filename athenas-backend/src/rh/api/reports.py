# -*- coding: utf-8 -*-
import json as js

from django.conf import settings

from contrib.controller import DefaultController
from contrib.decorator import login_required
from contrib.utils import get_json_engine, getLogger

from reports.api.mpmt.lotacionogram.lotacionogram import LotacionogramPdf
from standard.models import Choice

json = get_json_engine()
log = getLogger(__name__)


class RHEmployeeDesignationReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeDesignation")')


class RHCommissionPositionsReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.CommissionPositions")')


class RHEmployeeLotationReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeLotation")')


class RHLottationgramReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.Lottationgram")')

    def employee_type_by_possessions(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            types_by_possession = Choice.objects.filter(
                app_label="rh", name="CLASSIF_EMPLOYEE_BY_POSSESSION", active=True
            ).exclude(
                cvalue__in=[
                    "MCM",
                    "MEC",
                    "TCR",
                    "CTR",
                    "SAP",
                    "MAP",
                    "RFC",
                    "JCA",
                    "XXX",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "MAP2",
                    "APO",
                    "BFP",
                    "REX",
                    "COE",
                ]
            )
        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=types_by_possession.count(),
                collection=[
                    {"value": tp.cvalue, "description": str(tp.label)}
                    for tp in types_by_possession
                ],
            )

        self.response["content-type"] = "text/json"
        self.response.write(js.dumps(result))

    def generate_report_pdf(self, *args):
        LotacionogramPdf(self.request, self.response).generate_lotacionogram_pdf()

    def generate_report_csv(self, *args):
        LotacionogramPdf(self.request, self.response).generate_lotacionogram_csv()


class RHEmployeeRelationReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeRelation")')


class RHListaBeneficiariosReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.ListaBeneficiarios")')


class RHLotationControlReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.LotationControl")')


class RHFuncionalFormReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        storage_dir = settings.EXTERNAL_UPLOAD_STORE_DIR

        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.reports.FuncionalForm",{"storageDir":"%s"})' % storage_dir
        )

    def get_annotations(self, args=[]):
        result = {
            "success": False,
            "message": "Nothing made yet.",
            "count": 0,
            "collection": [],
        }

        try:
            annotations = (
                ["anot_geral", "Anotação Geral"],
                ["anot_afastamento", "Anotação Afastamento"],
                ["anot_ausencia", "Anotação Ausência"],
                ["anot_carreira", "Anotação Carreira"],
                ["anot_enquadramento", "Anotação Enquadramento"],
                ["anot_elogio", "Anotação Elogio"],
                ["anot_evento", "Anotação Evento"],
                ["anot_falta", "Anotação Falta"],
                ["anot_ferias", "Anotação Ferias"],
                ["anot_folga_eleitoral", "Anotação Folga Eleitoral"],
                ["anot_gratificacao", "Anotação Gratificacao"],
                ["anot_licenca", "Anotação Licenca"],
                ["anot_pena_disciplinar", "Anotação Pena Disciplinar"],
                ["anot_plantao", "Anotação Plantao"],
                ["anot_recesso", "Anotação Recesso"],
                ["anot_remocao", "Anotação Remocao"],
                ["anot_tempo_dobro", "Anotação Tempo em Dobro"],
                ["anot_tempo_servico", "Anotação Tempo Servico"],
                ["anot_transposicao", "Anotação Transposicao"],
                ["anot_viagem", "Anotação Viagem"],
            )

        except Exception as e:
            result.update(message=str(e))
        else:
            result.update(
                success=True,
                message="Dados encontrados com sucesso.",
                count=len(annotations),
                collection=[
                    {"value": tp[0], "description": str(tp[1])} for tp in annotations
                ],
            )

        self.response["content-type"] = "text/json"
        self.response.write(js.dumps(result))


class RHFuncionalWalletReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        storage_dir = settings.EXTERNAL_UPLOAD_STORE_DIR

        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("rh.reports.FuncionalWallet",{storageDir:"%s"})' % storage_dir
        )


class RHTransparencyPayCheck(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.transparency.PayCheck")')


class RHHealthTimeReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.HealthTime")')


class RHEmployeeByCityReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeByCityReport")')


class RHSalaryTableReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.SalaryTableReport")')


class RHNatureESocialReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.NatureESocialReport")')


class RHAdmittedPreviousYearReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.AdmittedPreviousYearReport")')


class RHAnnualListEmployeeReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.AnnualListEmployeeReport")')


class RHHealthLicenseProtocolReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.HealthLicenseProtocolReport")')


class RHTimeSheetReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.TimeSheetReport")')


class RHCorrespondenceCSV(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.CorrespondenceCSV")')


class RHEmployeeTermination(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeTermination")')


class RHVacationRequest(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.VacationRequest")')


class RHAbsenteeismReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.AbsenteeismReport")')


class RHEmployeeBirthdayReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeBirthday")')


class RHEmployeeProvisionalLotationReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.EmployeeProvisionalLotation")')


class RHExerciseRelationshipReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.ExerciseRelationshipReport")')


class RHMemberActivitiesMonthReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.ReportMemberActivitiesMonth")')


class RHPensionerPaymentReport(DefaultController):

    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.transparency.PensionerPayment")')


class RHJobPositionReport(DefaultController):
    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.JobPosition")')


class RHWorkplaceByLocality(DefaultController):
    @login_required("JSON")
    def json(self, args=[]):
        """DOCSTRING."""
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.reports.WorkplaceByLocality")')
