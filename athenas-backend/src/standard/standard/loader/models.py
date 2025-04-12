# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from contrib.decorator import cache_return

# from standard import models as std_models
import os
import codecs


log = getLogger("standard.loaders")

TYPEOFLINE = {
    "HF": "HEADER FILE",
    "HG": "HEADER GROUP",
    "RC": "RECORD",
    "TG": "TRAILER GROUP",
    "TF": "TRAILER FILE",
}


class FileLoader(object):

    SEPARATOR = ";"
    TRUNK_CR_NL = True
    HEADER_LINES = 0
    TRANSACTION_FULL = False
    CODE_TYPE = "utf-8"
    CONFIG = {}
    CONFIG_FROM_HEADER_LINE = 0

    class FileDoesNotExist(Exception):
        def __init__(self, file):
            Exception.__init__(self, "O arquivo (%s) não foi encontrado!" % file)

    class ValidateError(Exception):
        def __init__(self, msg=""):
            Exception.__init__(self, "Erro de validação: %s" % msg)

    def __init__(self, file_, **kargs):
        self.file = file_
        for key in kargs:
            setattr(self, key, kargs[key])
        self.header = []
        self.objects = []
        if not os.path.exists(self.file):
            raise self.FileDoesNotExist(self.file)

    @property
    def config(self):
        return self.CONFIG

    def load_config(self, cfg=[]):
        idx = 0
        for k in cfg:
            self.CONFIG[k.lower()] = idx
            idx += 1

    def validate_header(self):
        pass

    def pre_validate(self):
        pass

    def pos_validate(self):
        pass

    def convert_line(self, line, **kargs):
        """
        Este método retorna um objeto array referente a linha (@line) passada como parametro
        """
        linec = line.split(self.SEPARATOR)
        if self.TRUNK_CR_NL:
            linec[-1] = linec[-1].strip("\r\n")
        log.debug(linec)
        return linec

    def validate_line(self, linec):
        return True

    def line_to_dict(self, linec):
        """
        Retorna um dicionário com os campos do CONFIG rastreados no array da linha carregada.
        O valor de cada elemento pode ser manipulado criando um método com nome
        _convert_FIELD(self, value) onde value é o valor a ser convertido
        """
        dict_ = {}
        dict_["_line_"] = self.SEPARATOR.join(linec)

        if not self.validate_line(linec):
            return {}

        for key in self.config:
            dict_[key] = (
                linec[self.config[key]]
                if not hasattr(self, "_convert_%s" % key)
                else getattr(self, "_convert_%s" % key)(linec[self.config[key]])
            )
        return dict_

    def header_to_dict(self, linec):
        """Converte o header.

        Retorna um dicionário com os campos do CONFIG rastreados no array da linha carregada.
        O valor de cada elemento pode ser manipulado criando um método com nome
        _convert_FIELD(self, value) onde value é o valor a ser convertido
        """
        return linec

    def get_line(self, dict_):
        """
        Retorna um dicionário com os campos do CONFIG rastreados no array da linha carregada.
        O valor de cada elemento pode ser manipulado criando um método com nome
        _convert_FIELD(self, value) onde value é o valor a ser convertido
        """
        if "_line_" in dict_:
            return dict_["_line_"]

        return self.SEPARATOR.join(dict_)

    def load(self):
        self.pre_validate()

        with open(self.file, "r") as f:
            hl = 1
            for line in f:
                log.debug("LINE (%d): %s" % (hl, line))
                linec = self.convert_line(line.decode(self.CODE_TYPE))
                if not (len(linec) == 1 and not linec[0]):  # DESCARTA LINHAS VAZIAS
                    if hl <= self.HEADER_LINES:
                        if hl == self.CONFIG_FROM_HEADER_LINE:
                            self.load_config(linec)
                        _dict_ = self.header_to_dict(linec)
                        if _dict_:
                            self.header.append(_dict_)
                    else:
                        _dict_ = self.line_to_dict(linec)
                        if _dict_:
                            self.objects.append(_dict_)
                hl += 1

        if self.HEADER_LINES:
            self.validate_header()

        self.pos_validate()

        return self.objects

    def create_return_file(self):
        split_file = os.path.splitext(self.file)
        ret_file = "%s.ret%s" % split_file

        with codecs.open(ret_file, "w", self.CODE_TYPE) as f:

            for hd in self.header:
                line = self.SEPARATOR.join(hd)  # unicode(x) for x in
                if self.TRUNK_CR_NL:
                    line = "%s%s" % (line, "\r\n")
                f.write(line)

            for obj in self.objects:
                line = self.get_line(obj)
                if self.TRUNK_CR_NL:
                    line = "%s%s" % (line, "\r\n")
                f.write(line)


class FileLoaderCSV(FileLoader):
    SEPARATOR = ";"
    # TRUNK_CR_NL = True
    HEADER_LINES = 0
    # TRANSACTION_FULL = False
    # CODE_TYPE = 'utf-8'
    CONFIG = {}


class FileLoaderXML(FileLoader):
    pass
