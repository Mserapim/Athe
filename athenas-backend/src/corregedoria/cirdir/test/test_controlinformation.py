import unittest
from corregedoria.cirdir.models import *


class TestControlInformation(unittest.TestCase):

    def test_permission_criteria(self):

        c_member = ControlInformation.objects.filter(employee__tipo="M").last()
        c_employee = ControlInformation.objects.filter(employee__tipo="S").last()

        print(
            "###########################--############--##############################"
        )
        for criteria in [
            "address",
            "teaching",
            "property",
            "debits",
            "irpf",
            "health",
            None,
            "nao existe",
        ]:
            permission = c_member.check_access_criteria(criteria)
            print(criteria, permission)

        print(
            "###########################--############--##############################"
        )
        for criteria in [
            "address",
            "teaching",
            "property",
            "debits",
            "irpf",
            "health",
            None,
            "nao existe",
        ]:
            permission = c_employee.check_access_criteria(criteria)
            print(criteria, permission)
