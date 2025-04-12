import unittest
from raf.models import *
from rh.models import *


class TestLoadDataEExt(unittest.TestCase):
    """Load data E-Ext Tests"""

    def test_load(self):
        """Load data eext"""
        employee = Servidor.objects.get(matricula=102310)

        initial_date = "2021-05-01"
        final_date = "2021-05-30"

        rst = DataEExt.extract_extrajudicial_movements(
            employee, initial_date, final_date
        )

        # self.assertTrue(len(rst) > 0)
        locais = []
        count = 0
        for i in rst:
            print(
                "{}, Membro: {}, Assinado Por: {}, local: {}".format(
                    i.get("legalmovement"),
                    i.get("employee"),
                    i.get("signed_by_user"),
                    i.get("location"),
                )
            )

            if i.get("legalmovement", None) is not None:
                count += 1
            l = i.get("location")
            if l not in locais:
                locais.append(l)

        print(
            "###########################--############--##############################"
        )
        print(locais)
        print(count)
        # self.assertTrue(count == 182)
