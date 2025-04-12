# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from contrib.middleware import set_current_user
from contrib.utils import DateUtils, getLogger
from rh.pvf.models import ApproveServerDuty
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from standard.models import Choice
from rh.afastamento.models import CID, CIDCode
import json


log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """Esse Comando irá cria os cids a partir de um arquivo json. """

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def handle(self, *args, **options):
        self.criar_cid()

    def conf(self):
        set_current_user(User.objects.get(username="athenas"))

    def criar_cid(self):
        self.conf()
        date = datetime.now().date() - timedelta(days=1)
        log.info(
            f">>> [{DateUtils.datetime_to_str(datetime.now())}] Iniciando a criação dos cids >>>>>>>>>>>>>"
        )
        dados = None
        with open("rh/afastamento/fixtures/codigos_cid.json", "r") as arquivo:
            dados = json.load(arquivo)
        cids = []
        cid_codigos = []

        for dado in dados:
            # Criar ou obter o CID
            cid, criado = CID.objects.get_or_create(
                chapter="-", code="-", description=dado["description"][:244]
            )
            cids.append({"codigo": dado["code"], "cid": cid})
            if criado:
                # Criar o CIDCode
                c_codigo = CIDCode(code=dado["code"])
                cid_codigos.append(c_codigo)
                log.info(
                    f">>>>>>>>>>>>>>>>>>>>>> Cid criado {cid} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
                )

        CIDCode.objects.bulk_create(cid_codigos)

        for cid in cids:
            c_codigos = CIDCode.objects.filter(code=cid["codigo"])
            cid["cid"].cid_code.add(*c_codigos)
            log.info(
                f">>>>>>>>>>>>>>>>>>>>>> Cid relacionado {cid} <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
            )

        log.info(
            ">>> [{}] Finalizando a criação dos cids".format(
                DateUtils.datetime_to_str(date)
            )
        )
