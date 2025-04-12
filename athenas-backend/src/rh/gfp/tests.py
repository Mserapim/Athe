# -*- coding: utf-8 -*-

import unittest
from default.testting import AthenasTestCase
from rh.gfp.calculo_auditoria import Auditoria
from rh.gfp.models import Folha

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from django.contrib.auth.models import User

log = getLogger(__name__)

# set_current_user(User.objects.get(username='athenas'))
set_current_user(User.objects.get(username="gustavodettenborn"))


class CalculoTestCase(AthenasTestCase):

    avoid = False
    classe = None
    anotacao = None

    @classmethod
    def tearDownClass(cls):
        pass

    @unittest.skip("skipping test_calculo_normal")
    def test_calculo_normal(self):
        eventos = ["0001"]
        folha = (
            Folha.objects.filter(lancamentos__evento__numero="0001")
            .latest("dt_pagamento")
            .pk
        )
        Auditoria(folha=folha, eventos=eventos).audita()

    @unittest.skip("skipping test_calculo_auxilio_alimentacao")
    def test_calculo_auxilio_alimentacao(self):
        eventos = ["0259"]
        folha = (
            Folha.objects.filter(lancamentos__evento__numero="0259")
            .latest("dt_pagamento")
            .pk
        )
        Auditoria(folha=folha, eventos=eventos).audita()

    @unittest.skip("skipping test_calculo_gratificacao_natalina")
    def test_calculo_gratificacao_natalina(self):
        eventos = ["1305"]
        folha = (
            Folha.objects.filter(lancamentos__evento__numero="1305")
            .latest("dt_pagamento")
            .pk
        )
        Auditoria(folha=folha, eventos=eventos).audita()
