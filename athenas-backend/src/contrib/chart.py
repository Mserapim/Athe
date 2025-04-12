# -*- coding: utf-8 -*-
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import Color
from contrib.controller import DefaultController

import random


class DjangoChart(DefaultController):
    type = ""

    def draw(self, args=[]):
        """Metódo responsável por desenhar o gráfico."""


class DjangoLineChart(DjangoChart):

    def get_colors(self):
        num = len(self.get_data())
        rnd = random.Random()
        result = []
        for i in range(0, num):
            red, green, blue = (
                rnd.random() * 127,
                rnd.random() * 127,
                rnd.random() * 127,
            )
            color = Color(red, green, blue)
            result.append(color)
        return tuple(result)

    def get_marks(self):
        return makeMarker("Circle", size=5)

    def get_x_limits(self):
        min = 0
        max = 0

        for cords in self.get_data():
            for cord in cords:
                num = cord[0]
                if min > num:
                    min = num
                elif max < num:
                    max = num

        min = min - int(min * 0.25)
        max = max + int(max * 0.25)

        return min, max

    def get_y_limits(self):
        min = 0
        max = 0

        for cords in self.get_data():
            for cord in cords:
                num = cord[1]
                if min > num:
                    min = num
                elif max < num:
                    max = num

        min = min - int(min * 0.25)
        max = max + int(max * 0.25)

        return min, max

    def get_data(self):
        return []

    def draw(self, args=[]):
        shape = Drawing(width=450, height=375)

        chart = LinePlot()
        chart.width = 405
        chart.height = 305
        chart.x = 25
        chart.y = 25
        chart.data = self.get_data()
        chart.joinedLines = 1
        chart.xValueAxis.valueMin, chart.xValueAxis.valueMax = self.get_x_limits()
        chart.yValueAxis.valueMin, chart.yValueAxis.valueMax = self.get_y_limits()
        chart.lineLabelFormat = "%0.2f"

        marks = self.get_marks()
        if isinstance(marks, list) or isinstance(marks, tuple):
            i = 0
            for mark in marks:
                try:
                    chart.lines[i].symbol = mark
                    i += 1
                except Exception:
                    pass
        else:
            chart.lines.symbol = marks

        colors = self.get_colors()
        if isinstance(colors, list) or isinstance(colors, tuple):
            i = 0
            for color in colors:
                try:
                    chart.lines[i].strokeColor = color
                    i += 1
                except Exception:
                    pass

        shape.add(chart, name="chart")

        self.response["content-type"] = "image/png"
        self.response["Pragama"] = "no-cache"
        self.response["Cache-Control"] = "no-cache"

        bc = shape.asString("png")
        self.response.write(bc)
