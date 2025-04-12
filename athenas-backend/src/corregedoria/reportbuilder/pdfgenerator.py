# -*- coding:utf-8 -*-
import os
import json
import time
import uuid
import importlib
import csv
from datetime import datetime
from contrib.middleware import get_current_user
from engine.mq.models import Task
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Table,
    TableStyle,
    BaseDocTemplate,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.rl_config import defaultPageSize
from reportlab.pdfgen import canvas
from reportlab.rl_config import defaultPageSize
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame, PageTemplate
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT

from corregedoria.reportbuilder.tasks import generate_file

PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self._date = datetime.now()

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        self.annotations()
        canvas.Canvas.save(self)

    def annotations(canvas):
        canvas.setAuthor("MPTO")
        canvas.setTitle("Relatório")
        # canvas.setSubject("How to Generate PDF files using the ReportLab modules")

    def get_date_formated(self):
        return self._date.strftime("%d/%m/%Y - %H:%M")

    def get_request_user(self):
        return getattr(self, "current_user", None)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 9)
        self.line(20 * mm, 25 * mm, PAGE_WIDTH - 20 * mm, 25 * mm)
        self.drawRightString(
            PAGE_WIDTH - 30 * mm,
            20 * mm,
            "Página {} de {}".format(self._pageNumber, page_count),
        )
        self.drawString(
            30 * mm,
            20 * mm,
            f"Gerado em {self.get_date_formated()} por {self.get_request_user()}",
        )


class PDFGenerator(object):

    def __init__(self, output_file=None, params=[]):
        self.params = params
        self.output_file = output_file
        self.story = []
        self.styles = getSampleStyleSheet()

    def to_csv(self):
        dataset, header = self.load_csv()
        with open(self.output_file, "w") as file:
            writer = csv.DictWriter(file, delimiter=";", fieldnames=header)
            writer.writeheader()
            for data_item in dataset:
                writer.writerow(data_item)

    def to_pdf(self):
        self.doc = BaseDocTemplate(self.output_file, pagesize=A4)
        frame = Frame(
            self.doc.leftMargin,
            self.doc.bottomMargin,
            self.doc.width,
            self.doc.height - inch * 0.6,
            showBoundary=0,
        )

        template = PageTemplate(id="all_pages", frames=frame, onPage=self.header)

        self.doc.addPageTemplates([template])
        self.load()
        self.generate_file()

    def build(self):

        try:
            user = getattr(self, "current_user", None)
            if not user:
                raise Exception("Usuário que solicitou relatório é inválido/ausente")

            {"PDF": self.to_pdf, "CSV": self.to_csv}.get(
                self.params.get("format"), self.to_pdf
            )()

        except Exception as e:
            raise e

    def load(self):
        raise Exception("abstract method")

    def getStyle(self, style):
        return getSampleStyleSheet()[style]

    def getParams(self):
        return self.params

    def header(self, canvas, doc):
        title = "<h3><b>Ministério Público do Tocantins<br />Procuradoria Geral de Justiça</b></h3>"
        h3 = self.getStyle("Normal")
        # Draw logo
        self.drawLogoImage(canvas, doc, "/static/images/homedata.png", 0.8, 0.4, "LEFT")

        # Draw heading
        heading = Paragraph(title, h3)
        heading.wrap(doc.width, inch * 0.5)
        heading.drawOn(canvas, doc.leftMargin + 1.2 + inch, doc.height + inch)

        canvas.line(
            doc.leftMargin,
            doc.height + inch * 0.8,
            doc.width + doc.leftMargin,
            doc.height + inch * 0.8,
        )
        h2 = self.getStyle("Heading2")
        h2.alignment = 1
        h_title = Paragraph(self.header_report_title, h2)
        h_title.wrap(doc.width, inch * 0.5)
        h_title.drawOn(canvas, inch, doc.height + inch * 0.5)

    @property
    def header_report_title(self):
        return "Título do Relatório"

    def add_paragraph(self, text, align=TA_JUSTIFY, fontSize=12):
        sp = ParagraphStyle(
            "paragrafos", alignment=align, fontSize=fontSize, fontName="Helvetica"
        )

        self.story.append(Paragraph(text, sp))
        self.add_spacer()

    def add_bullet(self, text, align=TA_JUSTIFY, fontSize=10):
        sp = ParagraphStyle(
            "Bullet", alignment=align, fontSize=fontSize, fontName="Helvetica"
        )
        ptext = "<bullet>-</bullet>{}".format(text)
        self.story.append(Paragraph(ptext, sp))

    def choice_alignment(self, kind):
        return {
            "center": TA_CENTER,
            "justify": TA_JUSTIFY,
            "right": TA_RIGHT,
            "left": TA_LEFT,
        }.get(kind, TA_JUSTIFY)

    def add_spacer(self):
        self.story.append(Spacer(1, 0.1 * inch))

    def add_invisible_table(self, data, colWidths=None):
        table_style = TableStyle(
            [
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), "#e5e5e5"),
            ]
        )

        self.story.append(
            Table(data=data, repeatRows=1, style=table_style, colWidths=colWidths)
        )

    def add_table_default(
        self, data, summary=None, colWidths=None, summary_colWidths=None
    ):
        # INNERGRID - grid interna da tablea
        table_style = TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), "#e5e5e5"),
            ]
        )

        if summary:
            if not summary_colWidths:
                summary_colWidths = colWidths
            self.story.append(
                Table(
                    data=summary,
                    repeatRows=1,
                    style=table_style,
                    colWidths=summary_colWidths,
                )
            )
            self.story.append(Spacer(1, 0.1 * inch))
        self.story.append(
            Table(data=data, repeatRows=1, style=table_style, colWidths=colWidths)
        )
        self.story.append(Spacer(1, 0.5 * inch))

    def add_table_2(self, data, colWidths=None):
        # INNERGRID - grid interna da tablea
        table_style = TableStyle(
            [
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ]
        )

        table = Table(data=data, repeatRows=1, style=table_style, colWidths=colWidths)
        self.story.append(table)

    def add_table(self, data):
        # Styles for table
        table_style = TableStyle(
            [
                ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                ("ALIGN", (2, 0), (4, -1), "LEFT"),
            ]
        )
        # Create table and repeat row 1 at every split.
        table = Table(data, repeatRows=1, style=table_style)
        self.story.append(table)

    def drawLogoImage(self, canvas, doc, url, width, height, align="LEFT"):
        image = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + url
        im = Image(image, width * inch, height * inch)
        im.hAlign = align
        im.drawOn(canvas, doc.leftMargin, doc.height + inch * 1)

    def generate_file(self):
        canvas = FooterCanvas
        canvas.current_user = getattr(self, "current_user", "Naofoi")
        self.doc.build(self.story, canvasmaker=canvas)


class CreateDoc:

    def __init__(self, reportCls, params={}):
        self.reportCls = reportCls
        self.report_path = "{}.{}".format(reportCls.__module__, reportCls.__qualname__)
        self.params = params
        self.build()

    def build(self):

        # pode fazer uma verificacao se a classe que foi passada herda de pdfgenerator

        TaskView.start(
            generate_file,
            report=self.report_path,
            report_name=self.params.get("report_name"),
            params=self.params,
            output_format=self.params.get("format", "PDF"),
        )


class TaskView:
    @classmethod
    def start(klass, method, description="", **kwargs):
        task = Task()
        task.params = json.dumps(kwargs)
        task.description = description
        task.save()

        kwargs.update(
            task=task.uuid,
            hook="https://athenas.py27/athenas/MQTaskRestful/hook/%s/" % task.uuid,
        )

        method.apply_async(kwargs=kwargs)

        return task
