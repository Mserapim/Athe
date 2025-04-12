# -*- coding:utf-8 -*-

"""
No escopo de módulo NÃO DEVE HAVER import do settings ou qualquer outro módulo ou aplicativo que tenha
importação do settings do Django.

Solução: Criar modulos separados e fazer import via importlib
a partir do escopo do método ready do AppConfig
"""

import importlib
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "common.payments"
    verbose_name = "Payments"
    default_auto_field = "django.db.models.BigAutoField"

    controllers = [
        "common.payments.api",
    ]

    def ready(self):
        register_statics()
        connect_signals()
        # carregar qualquer outra coisa necessária ao app


def connect_signals():
    """Seus sinais devem ser carregados aqui.

    importlib.import_module('nome.canonico.do.modulo.de.sinais')
    """
    pass


def register_statics():

    Application = importlib.import_module("default.views").Application

    js_paths = (
        "/%(context)s/static/common/payments/BankPartnershipRestful.js",
        "/%(context)s/static/common/payments/BankPartnershipWindow.js",
        "/%(context)s/static/common/payments/BankPartnershipGrid.js",
        "/%(context)s/static/common/payments/BankPartnershipManage.js",
        "/%(context)s/static/common/payments/TicketPayRestful.js",
        "/%(context)s/static/common/payments/TicketPayWindow.js",
        "/%(context)s/static/common/payments/TicketPayGrid.js",
        "/%(context)s/static/common/payments/TicketPayManage.js",
        "/%(context)s/static/common/payments/IssueTicketManage.js",
        "/%(context)s/static/common/payments/SecondTicketWayForm.js",
    )
    # '/%(context)s/static/common/payments/FielsRepository.js'

    for path in js_paths:
        Application.register_javascript(path, scope="common")
