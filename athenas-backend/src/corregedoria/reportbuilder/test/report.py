# -*- coding:utf-8 -*-
from reportlab.lib.units import inch
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


class MyReport(PDFGenerator):

    def load(self):
        # for i in range(1, 25):
        #     self.add_paragraph(self.p1)

        # Data for table
        data = [["String", "String", "Number", "Number", "Number"]]
        data.extend([["one", "two", i, i, i] for i in range(90)])

        self.add_table(data)

    def header(self, canvas, doc):
        title = "Ministério Público do Tocantins"
        sub_title = "Procuradoria Geral de Justiça"
        title_style = self.getStyle("Heading3")
        sub_style = self.getStyle("Heading3")
        # year_style = self.getStyle('Heading5')
        sub_style.alignment = 1
        title_style.alignment = 1
        # year_style.alignment = 1
        # Draw logo
        self.drawImage(canvas, doc, "/static/images/homedata.png", 1.2, 0.5, "LEFT")

        # Draw heading
        heading = Paragraph(title, title_style)
        heading.wrap(doc.width, inch * 0.5)
        heading.drawOn(canvas, doc.leftMargin, doc.height + inch)

        subheading = Paragraph(sub_title, sub_style)
        subheading.wrap(doc.width, inch * 0.25)
        subheading.drawOn(canvas, doc.leftMargin, doc.height + inch * 0.75)

        # yearbase = Paragraph('Ano Base - {}'.format(self.params.get('year_base')), year_style)
        # yearbase.wrap(doc.width, inch * 0.25)
        # yearbase.drawOn(canvas, doc.leftMargin, doc.height + inch * 0.5)

        canvas.line(
            doc.leftMargin,
            doc.height + inch * 0.4,
            doc.width + doc.leftMargin,
            doc.height + inch * 0.4,
        )

    @property
    def p1(self):
        return """Lorem ipsum dolor sit amet, consectetur adipisicing
            elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
            Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in
            voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint
            occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim
            id est laborum."""
