# -*- coding:utf-8 -*-

from django.forms import Form, IntegerField


class ReportForm(Form):
    region = IntegerField(label="Comarca")

    month = IntegerField(label="Mês")
    year = IntegerField(label="Ano")

    month2 = IntegerField(label="Mês 2")
    year2 = IntegerField()

    region2 = IntegerField(required=False)
