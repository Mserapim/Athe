# -*- coding: utf-8 -*-

from django.test import TestCase
from rh.models import PessoaJuridica
from rh.gfp.models import FolhaTipo
from rh.gfp.planoconta.models import PlanoConta, Plano
import unittest


def create_planoconta():
    plano = create_plano()

    planoconta = PlanoConta(
        tipo=1,
        inscricao_ne="1",
        evento_nld="1",
        evento_nlc="1",
        classificacao_nld="1",
        classificacao_nlc="1",
        plano=plano,
    )
    planoconta.save()

    return planoconta


def create_plano():
    pessoajuridica = PessoaJuridica(
        nome="Pessoa Juridica Test", razao_social="Pessoa Juridica Test"
    )
    pessoajuridica.save()

    folhatipo = FolhaTipo(titulo="TIPO DE FOLHA TEST", ativo=True)
    folhatipo.save()

    plano = Plano(
        tipo=1,
        folha_tipo=folhatipo,
        pessoa_juridica=pessoajuridica,
        ano_calendario=2011,
    )
    plano.save()

    return plano


class PlanoTest(TestCase):

    def setUp(self):
        self.plano = create_plano()

    @unittest.skip("skipping test_related")
    def test_related(self):
        """ """
        self.assertTrue(hasattr(self.plano, "contas"))

    @unittest.skip("skipping test_fields")
    def test_fields(self):
        """ """
        self.assertTrue(hasattr(self.plano, "tipo"))
        self.assertTrue(hasattr(self.plano, "folha_tipo"))
        self.assertTrue(hasattr(self.plano, "pessoa_juridica"))
        self.assertTrue(hasattr(self.plano, "ano_calendario"))


class PlanoContaTest(TestCase):

    def setUp(self):
        """ """
        self.planoconta = create_planoconta()

    @unittest.skip("skipping test_fields")
    def test_fields(self):
        """ """
        self.assertTrue(hasattr(self.planoconta, "tipo"))
        self.assertTrue(hasattr(self.planoconta, "inscricao_ne"))
        self.assertTrue(hasattr(self.planoconta, "evento_nld"))
        self.assertTrue(hasattr(self.planoconta, "evento_nlc"))
        self.assertTrue(hasattr(self.planoconta, "classificacao_nld"))
        self.assertTrue(hasattr(self.planoconta, "classificacao_nlc"))
        self.assertTrue(hasattr(self.planoconta, "plano"))
