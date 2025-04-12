# -*- coding:utf-8 -*-
# from reportlab.lib.units import inch
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.db.models import Q, Min

from corregedoria.reportbuilder.pdfgenerator import PDFGenerator
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib.units import inch, mm
from corregedoria.inspection.models import Inspection


class HistoryInspectionReport(PDFGenerator):

    @property
    def header_report_title(self):
        return "Inspeção/Correição"

    #
    # def load_csv(self):
    #     # header = ['Nome', 'Bens e Direitos', 'Dívidas e Ônus']
    #     header = ['employee__matricula', 'employee__pessoa_fisica__nome', 'bens_e_direitos', 'dividas_e_onus']
    #     year = self.params.get('year_base', 0)
    #
    #     query = Q(
    #         ~Q(employee__tipo='M') &
    #         Q(
    #             Q(property_submitted_at=None) |
    #             Q(debits_submitted_at=None)
    #         ) &
    #         Q(
    #             Q(hidden=False) &
    #             Q(year=year)
    #         )
    #     )
    #
    #     result = ControlInformation.objects.filter(query).annotate(
    #         bens_e_direitos=Case(
    #             When(property_submitted_at=None, then=Value('Não submetido')),
    #             default=Value('Submetido'),
    #             output_field=TextField()
    #         )
    #     ).annotate(
    #         dividas_e_onus=Case(
    #             When(debits_submitted_at=None, then=Value('Não submetido')),
    #             default=Value('Submetido'),
    #             output_field=TextField()
    #         )
    #     ).values('employee__matricula','employee__pessoa_fisica__nome', 'bens_e_direitos', 'dividas_e_onus')
    #
    #
    #     return list(result), header

    def load(self):

        initial = self.params.get("initial", 0)
        final = self.params.get("final", 0)

        fn_strip = lambda d: (int(d.split("/")[0]), int(d.split("/")[1]))

        initial_month, initial_year = fn_strip(initial)
        final_month, final_year = fn_strip(final)

        self.add_paragraph(
            "<center><h2><b>Histórico - {} - {}</b></h2></center>".format(
                initial, final
            ),
            self.choice_alignment("center"),
        )
        self.add_spacer()

        final_date = datetime(final_year, final_month, 1).date() + relativedelta(day=31)
        initial_date = datetime(initial_year, initial_month, 1).date()

        result = Inspection.objects.filter(
            inspection_date_initial__range=(initial_date, final_date)
        )

        def get_employee_responsible(obj):
            if obj.employee:
                return obj.employee.pessoa_fisica.nome
            else:
                employee = (
                    obj.in_member_organ.values_list("employee__pessoa_fisica__nome")
                    .annotate(Min("member_role"))
                    .first()
                )

                if employee:
                    return employee[0]
                else:
                    return ""

        if result.exists():
            data = [["Inicio", "Fim", "Órgao Inspecionado", "Procurador/Promotor"]]
            data.extend(
                [
                    [
                        i.inspection_date_initial.strftime("%d/%m/%Y"),
                        i.inspection_date_final.strftime("%d/%m/%Y"),
                        (
                            Paragraph(i.execution_organ.nome, self.getStyle("Normal"))
                            if i.execution_organ
                            else Paragraph("", self.getStyle("Normal"))
                        ),
                        Paragraph(get_employee_responsible(i), self.getStyle("Normal")),
                    ]
                    for i in result
                ]
            )
            self.add_table_2(data, colWidths=(None, None, 80 * mm, 60 * mm))
        else:
            self.add_paragraph(self.empty, self.choice_alignment("center"))

    @property
    def empty(self):
        return """<h2>O Relatório não retornou resultado.</h2>"""
