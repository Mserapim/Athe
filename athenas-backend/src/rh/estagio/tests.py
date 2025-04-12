"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from rh.estagio.models import EstagioComissaoServidor, EstagioProbatorioServidor

# from django.utils import unittest


class EstagioProbatorioServidorTestCase(TestCase):

    def test_basic_addition(self):
        eps = EstagioProbatorioServidor.objects.get(pk=550)
        print((eps.pk, eps))
        for dco in EstagioComissaoServidor.objects.get(
            estagio_prob_servidor=eps
        ).decisao_chefe_orgao.filter():
            print(dco)
        # EstagioProbatorioServidor.homologate([eps.pk])
