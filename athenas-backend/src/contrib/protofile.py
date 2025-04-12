# -*- coding: utf-8 -*-
from contrib.utils import getLogger

import functools


log = getLogger(__name__)


def my_cmp(first, second):
    rs = 1
    if type(first) == str or type(second) == str:
        rs = -1
    elif first < second:
        rs = -1
    return rs


class Record(object):
    """
    Classe para implementar os registros(linhas) dos arquivos bancários.
    """

    _separator = ""
    _separator_on_end_line = ""

    def __init__(self, type_, **kargs):
        self.layout = type_
        self.info = {}
        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            # log.debug('KEY: %s' % k)
            obj = self._protocol[self.layout][k]
            self.info[k] = kargs.get(obj["label"], obj.get("value", None))

    @property
    def _protocolo(self):
        return {}

    def validate_info(self):
        if not (self.info and isinstance(self.info, dict)):
            raise Exception("Validate Config File: Configuração inválida")
        return True

    def prepare(self, k):
        if not k == "cfg":
            if k not in self._protocol[self.layout]:
                return ""
            _dict = self._protocol[self.layout][k]
            fixed = _dict.get("fixed", True)
            required = _dict.get("required", True)
            fill = _dict.get("fill", None)
            if not fixed:
                fill = ""

            if not required and not self.info[k]:
                fill = ""

            if _dict["type"] in ["num", "N"]:
                fill = "0" if fill is None else fill
                if "decimal" in _dict:
                    return Protocol.prepare_float(
                        self.info[k], _dict["size"], _dict["decimal"], fill=fill
                    )
                else:
                    return Protocol.prepare_num(self.info[k], _dict["size"], fill=fill)
            elif _dict["type"] in ["alfa", "A"]:
                fill = " " if fill is None else fill
                return Protocol.prepare_alfa(self.info[k], _dict["size"], fill=fill)

        return ""

    def __str__(self):
        linha = ""

        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                pass
            else:
                # log.debug('KEY: %s' % k)
                if Record.is_empty(self.info[k]) and self.is_required(k):
                    line = self.__class__.get_required_value(
                        label=self._protocol[self.layout][k]["label"],
                        required=self._protocol[self.layout][k].get("required", 0),
                    )
                else:
                    line = self.prepare(k)
                try:
                    if linha:
                        linha += (
                            self._separator + line
                            if not isinstance(line, str)
                            else self._separator + str(line)
                        )
                    else:
                        linha += line if not isinstance(line, str) else str(line)
                except Exception as e:
                    log.exception(e)

        return linha + self._separator_on_end_line

    def __getitem__(self, idx):
        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if idx == k or idx == self._protocol[self.layout][k]["label"]:
                return self.info[k] or self._protocol[self.layout][k]["value"]
        return None

    def get(self, idx):
        return self.__getitem__(idx)

    def update_value(self, idx, value):
        for k in sorted(self._protocol[self.layout], key=functools.cmp_to_key(my_cmp)):
            if idx == k or idx == self._protocol[self.layout][k]["label"]:
                self.info[k] = value
                return value
        return None

    def is_required(self, key):
        """
        Este método verifica se o value informado, para o campo(key), é vazio ou None.
        Também verifica se o campo é obrigatório.
        Caso seja, a resposta será True de outra forma False.
        @param str - key, identificador da linha do campo.
        @return boolean - True caso seja obrigatório, False de outa forma.
        """
        try:
            return self._protocol[self.layout][key].get("required", False)
        except Exception as e:
            log.exception(e)

        return False

    @classmethod
    def get_required_value(cls, **kwargs):
        """
        Este método retorna um texto com o nome.
        @param str - key, identificador da linha do campo.
        @return str - label do campo.
        """
        return "O campo %s é obrigatório!" % kwargs["label"]

    @staticmethod
    def is_empty(value):
        """
        Este método verifica se o value informado é vazio ou None.
        @return boolean, True se for vazio, False de outra forma.
        """
        try:
            if value == "" or value is None:
                return True
            elif eval(value) is None:
                return True
        except Exception:
            pass
        return False


class GroupRecords(object):
    def __init__(self, cls, header_layout, trailer_layout, **kargs):
        self.class_record = cls
        self.header = (
            self.class_record(header_layout, **kargs) if header_layout else None
        )
        self.trailer = (
            self.class_record(trailer_layout, **kargs) if trailer_layout else None
        )
        self.records = []

    def get_records(self):
        regs = []
        if self.header:
            regs += [self.header]
        regs += self.records
        if self.trailer:
            regs += [self.trailer]
        return regs

    def count(self):
        return len(self.records)

    def update_header(self, **kargs):
        for k in kargs:
            self.header.update_value(k, kargs[k])

    def update_trailer(self, **kargs):
        for k in kargs:
            self.trailer.update_value(k, kargs[k])

    def add(self, layout, **kargs):
        rec = self.class_record(layout, **kargs)
        self.records.append(rec)
        return rec

    def get(self, key, value):
        for rec in self.records:
            if rec.get(key) == value:
                return rec
        return None


class Protocol(object):

    def __init__(self):
        self.regs = []
        self.nl = "\n"

    def __extract_regs__(self):
        return self.nl.join([str(r) for r in self.get_records()])

    def __str__(self):
        return self.__extract_regs__()

    @staticmethod
    def prepare_time(date):
        return date.strftime("%H%M%S")

    @staticmethod
    def prepare_date(date, type_=0):
        if type_ == 0:
            return date.strftime("%d%m%Y")
        else:
            return date.strftime("%Y%m%d")

    @staticmethod
    def prepare_float(f, size, decimal=2, align=1, fill="0"):
        # log.debug('%s - %s - %s %s %s' % (f, size, decimal, align, fill))
        if fill == "" and f is None:
            return ""
        f = float(f or 0)
        _f = "%0.f" % (f * (10**decimal))
        return Protocol.prepare_num(_f, size, fill)

    @staticmethod
    def prepare_str(s, size, align=0, fill=" "):

        try:
            buf = str(s)
        except Exception as e:
            log.exception(e)

        if size:
            if len(buf) > size:
                buf = buf[0:size]

            if fill:
                if align == 0:
                    while len(buf) < size:
                        buf += fill
                else:
                    while len(buf) < size:
                        buf = fill + buf

        return buf

    @staticmethod
    def prepare_num(f, size, fill="0"):
        """
        Formata número:
        ALINHAMENTO à direita com preenchimento de ZEROS '0' à esquerda
        """
        if fill == "" and f in [None, ""]:
            return ""
        return Protocol.prepare_str(str(f), size, 1, fill)

    @staticmethod
    def prepare_alfa(f, size, fill=" "):
        """
        Formata alfa-numéricos:
        ALINHAMENTO à esquerda com preenchimento de ESPAÇOS ' ' à direita
        """
        return Protocol.prepare_str(f, size, 0, fill)

    def get_records(self):
        return self.regs

    def execute(self):
        return self.regs
