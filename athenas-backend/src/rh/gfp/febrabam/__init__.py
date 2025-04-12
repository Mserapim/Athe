# -*- coding: utf-8 -*-
from contrib.utils import getLogger
from rh.gfp.febrabam.layouts import FEBRABAN
from contrib.protofile import my_cmp

import functools


log = getLogger()


class Protocol(object):

    def __init__(self):
        self.header = None
        self.bodys = []
        self.regs = []
        self.trailer = None
        self.nl = "\n"

    class Header:
        def __str__(self):
            return "not implemented"

    class Trailer:
        def __str__(self):
            return "not implemented"

    def __extract_bodys__(self):
        buf = ""
        for body in self.bodys:
            buf += "{0}{nl}".format(str(body), nl=self.nl)
        return buf

    def __extract_regs__(self):
        buf = ""
        for reg in self.regs:
            try:
                buf += "{0}{nl}".format(str(reg), nl=self.nl)
            except Exception as e:
                log.exception(e)
        return buf

    def __str__(self):
        return "{0}{nl}{1}{2}".format(
            self.header, self.__extract_bodys__(), self.trailer, nl=self.nl
        )

    @staticmethod
    def prepare_time(date, apply_blank=True):
        return date.strftime("%H%M%S")

    @staticmethod
    def prepare_date(date, tipo=0, apply_blank=True):
        if tipo == 0:
            return date.strftime("%d%m%Y")
        else:
            return date.strftime("%Y%m%d")

    @staticmethod
    def prepare_float(f, size, decimal=2, align=1, branco="0", apply_blank=True):
        _f = "%0.f" % (f * (10**decimal))
        return Protocol.prepare_num(_f, size, branco, apply_blank)

    @staticmethod
    def prepare_str(s, size, align=0, branco=" ", apply_blank=True):
        if branco is None:
            branco = " "
        try:
            buf = str(s)
        except Exception as e:
            log.exception(e)

        if len(buf) > size:
            buf = buf[0:size]

        if apply_blank:
            if align == 0:
                while len(buf) < size:
                    buf += branco
            else:
                while len(buf) < size:
                    buf = branco + buf

        return buf

    @staticmethod
    def prepare_num(f, size, branco="0", apply_blank=True):
        """
        Formata número de acordo com a versão 08.4 da FEBRABAN
        ALINHAMENTO à direita com preenchimento de ZEROS '0' à esquerda
        """
        return Protocol.prepare_str("%s" % f, size, 1, branco or "0", apply_blank)

    @staticmethod
    def prepare_alfa(f, size, branco=" ", apply_blank=True):
        """
        Formata alfa-numéricos de acordo com a versão 08.4 da FEBRABAN
        ALINHAMENTO à esquerda com preenchimento de ESPAÇOS ' ' à direita
        """
        return Protocol.prepare_str(f, size, 0, branco, apply_blank)


class Registro:
    """
    Classe para implementar os registros(linhas) dos arquivos bancários.
    """

    _protocolo = FEBRABAN
    _separador = ""

    def __init__(self, type, **kargs):
        self.layout = type
        self.info = {}
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            try:
                if self._protocolo[self.layout][k]["label"] in kargs:
                    self.info[k] = kargs[self._protocolo[self.layout][k]["label"]]
                    if self._protocolo[self.layout][k]["tipo"] == "alfa":
                        self.info[k] = "%s" % self.info[k]
                    else:
                        if "decimais" in self._protocolo[self.layout][k]:
                            self.info[k] = (
                                float(self.info[k])
                                if k in self.info
                                else self._protocolo[self.layout][k]["valor"]
                            )
                        else:
                            #                            log.debug(u'%s' % (self._protocolo[self.layout][k]['label']))
                            self.info[k] = (
                                int(self.info[k])
                                if k in self.info
                                else self._protocolo[self.layout][k]["valor"]
                            )
                else:
                    self.info[k] = self._protocolo[self.layout][k]["valor"]
            except Exception as e:
                log.debug("%s" % (self._protocolo[self.layout][k]["label"]))
                log.exception(e)

    def get_layout(self):
        """
        Esse método é abstrato e deve ser implementado em toda classe que herda Registro
        Deve retornar a configuração do layout a ser instanciado
        """
        return {}

    def validate_info(self):
        if not (self.info and isinstance(self.info, dict)):
            raise Exception("Validate Config File: Configuração inválida")
        return True

    def prepare(self, k):
        if not k == "cfg":
            if k not in self._protocolo[self.layout]:
                return ""
            branco = (
                self._protocolo[self.layout][k]["branco"]
                if "branco" in self._protocolo[self.layout][k]
                else None
            )
            if self._protocolo[self.layout][k]["tipo"] == "alfa":
                return Protocol.prepare_alfa(
                    (
                        self.info[k]
                        if k in self.info
                        else self._protocolo[self.layout][k]["valor"]
                    ),
                    self._protocolo[self.layout][k]["size"],
                    branco=branco,
                )
            else:
                if "decimais" in self._protocolo[self.layout][k]:
                    return Protocol.prepare_float(
                        (
                            self.info[k]
                            if k in self.info
                            else self._protocolo[self.layout][k]["valor"]
                        ),
                        self._protocolo[self.layout][k]["size"],
                        self._protocolo[self.layout][k]["decimais"],
                        branco=branco,
                    )
                else:
                    #                    log.debug('%s %s' % (self._protocolo[self.layout][k]['label'], self.info[k]))
                    return Protocol.prepare_num(
                        (
                            self.info[k]
                            if k in self.info
                            else self._protocolo[self.layout][k]["valor"]
                        ),
                        self._protocolo[self.layout][k]["size"],
                        branco=branco,
                    )
        return ""

    def __str__(self):
        linha = ""
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                break
            if Registro.is_vazio(self.info[k]) and self.is_obrigatorio(k):
                l = self.__class__.get_valor_obrigatorio(
                    label=self._protocolo[self.layout][k]["label"],
                    obrigatorio=self._protocolo[self.layout][k]["obrigatorio"],
                )
            else:
                l = self.prepare(k)
            try:
                if not linha == "" or linha is not None:
                    linha += (
                        self._separador + l
                        if not isinstance(l, str)
                        else self._separador + str(l)
                    )
                else:
                    linha += l if not isinstance(l, str) else str(l)
            except Exception as e:
                log.exception(e)
        return linha

    def __getitem__(self, idx):
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            if idx == k or idx == self._protocolo[self.layout][k]["label"]:
                return self.info[k] or self._protocolo[self.layout][k]["valor"]
        return None

    def get(self, idx):
        return self.__getitem__(idx)

    def update_value(self, idx, value):
        for k in sorted(FEBRABAN[self.layout], key=functools.cmp_to_key(my_cmp)):
            if idx == k or idx == FEBRABAN[self.layout][k]["label"]:
                self.info[k] = value
                return value
        return None

    def is_obrigatorio(self, key):
        """
        Este método verifica se o valor informado, para o campo(key), é vazio ou None.
        Também verifica se o campo é obrigatório.
        Caso seja, a resposta será True de outra forma False.
        @param str - key, identificador da linha do campo.
        @return boolean - True caso seja obrigatório, False de outa forma.
        """
        try:
            if (
                "obrigatorio" in self._protocolo[self.layout][key]
                and self._protocolo[self.layout][key]["obrigatorio"] == 1
            ):
                return True
        except:
            pass
        return False

    @classmethod
    def get_valor_obrigatorio(cls, **kwargs):
        """
        Este método retorna um texto com o nome.
        @param str - key, identificador da linha do campo.
        @return str - label do campo.
        """
        return "O campo %s é obrigatório!" % kwargs["label"]

    @staticmethod
    def is_vazio(valor):
        """
        Este método verifica se o valor informado é vazio ou None.
        @return boolean, True se for vazio, False de outra forma.
        """
        try:
            if valor == "" or valor is None:
                return True
            elif eval(valor) is None:
                return True
        except:
            pass
        return False


class LoteFebraban:
    def __init__(self, header_layout, trailer_layout, **kargs):
        self.header = Registro(header_layout, **kargs) if header_layout else None
        self.trailer = Registro(trailer_layout, **kargs) if trailer_layout else None
        self.detalhes = []

    def getRegistros(self):
        regs = []
        if self.header:
            regs += [self.header]
        regs += self.detalhes
        if self.trailer:
            regs += [self.trailer]
        return regs

    def getCountDetalhes(self):
        return len(self.detalhes)

    def updateHeader(self, **kargs):
        for k in kargs:
            self.header.update_value(k, kargs[k])

    def updateTrailer(self, **kargs):
        for k in kargs:
            self.trailer.update_value(k, kargs[k])

    def addRegistro(self, layout, **kargs):
        self.detalhes.append(Registro(layout, **kargs))

    def addRegistro3A(self, layout, **kargs):
        self.addRegistro(layout, **kargs)  # Adicionando um registro 3A
        if "registro3B" in FEBRABAN[layout]["cfg"]:
            # Adicionando um registro 3B, caso seja solicitado no layout escolhido pelo 3A.
            # Nesse caso as configurações do registro 3B vem juntas com as do 3A
            self.addRegistro(layout, **kargs)
