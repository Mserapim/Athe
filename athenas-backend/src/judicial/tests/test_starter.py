# -*- coding: utf-8 -*-

from judicial.models import ExecutionOrgan

import unittest


class StarterTestCase(unittest.TestCase):

    def test_starter(self):
        self.assertTrue(True)


class ExecutionOrganTestCase(unittest.TestCase):

    def test(self):

        eos = ExecutionOrgan.objects.filter()
        for eo in eos:
            print(eo)
            print(eo.employee_exercise_unicode())
            print("----------------------------------------------------------")
