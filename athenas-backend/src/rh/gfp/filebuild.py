# -*- coding: utf-8 -*-

import codecs
import threading

from django.conf import settings

from contrib.controller import CommandController
from rh.gfp.models import DadoBancarioServidorFolha
from rh.models import Servidor

if getattr(settings, "DEBUG", False) is True:

    def _unlink(*args):
        pass

    unlink = _unlink
else:
    from os import unlink


class GFPContaCreditoCSV(CommandController):

    def get_temporary_file(self):
        return "/tmp/conta-credito.csv"

    @staticmethod
    def prepare_cpf(value):
        chars = [
            c for c in value if c in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        ]

        while len(chars) < 11:
            chars.insert(0, "0")
        chars = chars[0:11]

        return "%s.%s.%s-%s" % (
            "".join(chars[0:3]),
            "".join(chars[3:6]),
            "".join(chars[6:9]),
            "".join(chars[9:]),
        )

    def process(self):
        self.set("pctText", "Iniciando o processamento...")
        self.set("pct", 0.0)
        self.set("done", False)

        query = Servidor.objects.filter()

        if self.get("situacao_servidor") == "2":
            query = query.filter(ativo=True)
        elif self.get("situacao_servidor") == "3":
            query = query.filter(ativo=False)

        count = 0
        total = query.count()

        try:
            with codecs.open(self.get_temporary_file(), "w", "utf-8") as fd:
                fd.write("MATRICULA;NOME;BANCO;AGENCIA;CONTA;CARGOS\n")
                for s in query:
                    count += 1
                    self.set("pct", float(count) / float(total if total > 0 else 1))
                    self.set(
                        "pctText", "Processando servidor %d de %d." % (count, total)
                    )

                    d = {
                        "matricula": s.matricula,
                        "cpf": GFPContaCreditoCSV.prepare_cpf(s.pessoa_fisica.cpf),
                        "nome": s.pessoa_fisica.nome,
                        "banco": "",
                        "agencia": "",
                        "conta": "",
                        "cargos": ", ".join([str(p.quadro) for p in s.posses_ativas]),
                    }

                    dbsf = DadoBancarioServidorFolha.objects.filter(
                        dado_bancario_pessoa__pessoa=s.pessoa_fisica,
                        tipo_folha=int(self.get("tipo_folha")),
                    ).order_by("-data_vigencia", "-id")

                    dbf = dbsf[0] if dbsf.count() > 0 else None
                    self.log.debug("%s: %d" % (s.pessoa_fisica.pk, dbsf.count()))

                    if dbf is not None:
                        d.update(banco=str(dbf.dado_bancario_pessoa.banco.numero))
                        d.update(agencia=str(dbf.dado_bancario_pessoa.agencia))
                        d.update(
                            conta=str(dbf.dado_bancario_pessoa.conta_corrente_completa)
                        )

                    try:
                        fd.write(
                            "%(matricula)s;%(nome)s;%(cpf)s;%(banco)s;%(agencia)s;%(conta)s;%(cargos)s\n"
                            % d
                        )
                    except Exception as e:
                        self.log.exception(e)
        except Exception as e:
            self.log.exception(e)
            self.set("pctText", "Ocorreram erros processando o arquivo!")
            self.set("pct", 1.0)
            self.set("done", True)
            self.set("error", e)
        else:
            self.set("pctText", "Pronto!")
            self.set("pct", 1.0)
            self.set("done", True)

    def getFile(self, args=[]):
        self.response["content-type"] = "text/csv"
        self.response["content-disposition"] = "attachment; filename=conta-credito.txt"

        with codecs.open(self.get_temporary_file(), "r", "utf-8") as fd:
            self.response.write(fd.read())

        unlink(self.get_temporary_file())

    def start(self, args=[]):
        t = threading.Thread(target=self.process)
        t.setDaemon(True)
        t.start()

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("new toolkit.gfp.CSVContaCredito()")
