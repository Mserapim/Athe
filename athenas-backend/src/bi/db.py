# -*- coding:utf-8 -*-
import pymssql
from contextlib import contextmanager
from django.db import connections

DB_ALIAS = dict(
    almoxarifado=lambda: pymssql.connect(
        host="10.113.10.7", user="maksuel", password="alone", database="Bco_Almox"
    ),
    patrimonio=lambda: pymssql.connect(
        host="10.113.10.7", user="maksuel", password="alone", database="sispat"
    ),
    default=lambda: connections["default"],
)


@contextmanager
def SimpleDB(name="default"):
    layer = Layer(DB_ALIAS[name])
    yield layer
    layer.connection.close()


class Layer(object):

    def __init__(self, db):
        self.connection = db() if callable(db) else db
        self.__set_cursor()

    def __set_cursor(self):
        self.cursor = self.connection.cursor()
        if hasattr(self.cursor, "cursor"):
            self.cursor = self.cursor.cursor.cursor

    def query(self, sql, pars=None):
        self.cursor.execute(sql)
        tuples = self.cursor.fetchall()

        result_set = []
        for t in tuples:
            _tuple = {}
            for i in range(len(t)):
                _tuple[self.cursor.description[i][0].lower()] = t[i]
            result_set.append(_tuple)
        return result_set
