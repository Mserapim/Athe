# -*- coding:utf-8 -*-

import unittest, itertools
from pprint import pprint
from concurrent import futures

from django.contrib.auth.models import User
from contrib import mongo
from workflow.models import Vertex
from web.models import *


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.vertex = Vertex.objects.all().latest("id")


class ModelJuicerTestCase(BaseTestCase):

    def test_getting_all(self):
        juice = mongo.ModelJuicer(self.vertex)

        values = list(juice.values())
        # relations = juice.relations()

        self.assertIsInstance(
            values, dict, "O método values deve retornar um dicionário"
        )
        # self.assertIsInstance(relations, dict, 'O método relations deve retornar um dicionário')

        self.assertTrue(
            values, "O método get_public_vars não deve retornar um dicionário vazio"
        )
        # self.assertTrue(relations, 'O método relations não deve retornar um dicionário vazio')

    def test_exclude_fields(self):

        fields = [
            # 'common_ptr',
            # 'jokervertex',
            # 'lotacaovertex',
            # 'pessoavertex',
            # 'servidorvertex',
            "solicitacoes",
            # 'source_edge',
            # 'target_edge',
        ]

        juice = mongo.ModelJuicer(self.vertex, exclude=fields)

        values = list(juice.values())
        relations = juice.relations()

        for field in fields:
            self.assertNotIn(
                field, values, "O campo não %s não deveria estar em values" % field
            )
            self.assertNotIn(
                field,
                relations,
                "O campo não %s não deveria estar em relations" % field,
            )

        pprint(values, indent=2, width=150, depth=5)
        pprint(relations, indent=2, width=150, depth=5)
        pprint(self.vertex.solicitacoes.all().count())


class ODMTestCase(BaseTestCase):

    def test_connection(self):
        pass

    def test_document(self):
        fields = [
            # 'common_ptr',
            "jokervertex",
            "lotacaovertex",
            # 'pessoavertex',
            "servidorvertex",
            # 'solicitacoes',
            # 'source_edge',
            # 'target_edge',
        ]
        odm = mongo.ODM(exclude=fields)
        odm.rel("common_ptr", only_id=True)
        odm.rel("target_edge", only_id=True)
        odm.rel("solicitacoes", only_id=True, limit=20)
        pprint(odm.save(self.vertex, fake=True), indent=4)


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class VassalsTestCase(unittest.TestCase):

    def setUp(self):
        self.tasks = Post.objects.all()[0:1000]

    def multiple_tasks(self, tasks):
        for task in tasks:
            # print task
            self.work_tool(task)

    def work_tool(self, task):
        excludes = ["post", "text", "content_ptr"]
        odm = mongo.ODM(exclude=excludes)
        odm.rel("images")
        odm.rel("files")
        odm.rel("audios")
        odm.rel("videos")
        odm.save(task, fake=True)

        # pprint(odm.save(fake=True), indent=4)

    def test_work(self):

        pool = futures.ThreadPoolExecutor(4)
        futures_list = [
            pool.submit(self.multiple_tasks, group) for group in grouper(self.tasks, 10)
        ]
        futures.wait(futures_list)

        # vassals = mongo.Vassals(self.tasks, 1, self.work_tool)
        # vassals.work()

        # excludes = [
        #     'post',
        #     'text',
        #     'content_ptr'
        # ]
        # for task in self.tasks:
        #     odm = mongo.ODM(task, exclude=excludes)
        #     odm.rel('images')
        #     odm.rel('files')
        #     odm.rel('audios')
        #     odm.rel('videos')
        #     odm.save(fake=True)
