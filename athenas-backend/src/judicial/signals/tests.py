# -.- coding: utf-8 -.-
import unittest
from django.contrib.auth.models import User
from django.db.models import Q
from mixer.backend.django import mixer
from judicial.models import OfficerDiligence
from rh.models import Servidor, MovimentacaoPosse, CANCELED
from contrib.utils import getLogger
from contrib.middleware import set_current_user, StartupLoader
from dateutil.relativedelta import relativedelta
from datetime import datetime


log = getLogger(__name__)

StartupLoader().doLoad()
set_current_user(User.objects.get(username="athenas"))


class SignalsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not OfficerDiligence.objects.exists():
            for possession in MovimentacaoPosse.objects.filter(
                quadro__cargo__nome__icontains="oficial de dilige", ativo=True
            ):
                mixer.blend(
                    "judicial.OfficerDiligence", officer_diligence=possession.servidor
                )

    @classmethod
    def employee_officer_diligence(cls):
        officer_diligence = None
        for employee in Servidor.objects.filter(
            Q(ativo=True) & ~Q(officerdiligence=None)
        ):
            if employee.departures().exists():
                officer_diligence = employee
                break
        if not officer_diligence:
            for employee in Servidor.objects.filter(
                Q(ativo=True) & ~Q(officerdiligence=None)
            ):
                try:
                    mixer.blend(
                        "afastamento.FolgaCompensacao",
                        servidor=employee,
                        data_inicio=datetime.now().date(),
                        data_prevista=datetime.now().date() + relativedelta(days=3),
                        data_fim=datetime.now().date() + relativedelta(days=3),
                    )
                except:
                    pass
                else:
                    officer_diligence = employee
                    break
        return officer_diligence

    def test_update_officer_diligence(self):
        employee = SignalsTestCase.employee_officer_diligence()
        departure = employee.departures().last()._instancia_modelo()
        departure.save()
        assert Servidor.objects.get(pk=employee.pk).officerdiligence.status == 2
        departure.alteracao = CANCELED
        departure.save()
        assert Servidor.objects.get(pk=employee.pk).officerdiligence.status == 1
