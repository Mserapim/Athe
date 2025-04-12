# -*- coding: utf-8 -*-

import functools
import re

from contrib.utils import getLogger
from contrib.protofile import my_cmp
from contrib.helpers import clear_to_ascii
from rh.gfp import febrabam as fb
from rh.gfp.previdencia.layouts import IGEPREV

log = getLogger()


TAG_RE = re.compile(r"<[^>]+>")


def remove_tags(text):
    return TAG_RE.sub("", text)


class Registro:
    """
    Classe para implementar os registros(linhas) dos arquivos bancários.
    """

    _protocolo = IGEPREV
    _separador = "|"
    index = None

    def __init__(self, index, classe_origem, **kargs):
        self.index = index
        self.layout = classe_origem
        self.apply_blank = kargs.get("apply_blank", True)
        self._separador = kargs.get("separator", self._separador)
        self.info = {}
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            try:
                if self._protocolo[self.layout][k]["label"] in kargs:
                    self.info[k] = kargs[self._protocolo[self.layout][k]["label"]]
                    if (
                        self.info[k] == "<br><!-- Correção de bug da ExtJS -->"
                        or self.info[k] == "<!-- Correção de bug da ExtJS -->"
                        or self.info[k] == "<!-- Correcao de bug da ExtJS -->"
                        or self.info[k] == "<BR><!-- CORRECAO DE BUG DA EXTJS -->"
                    ):
                        self.info[k] = ""
                    if self._protocolo[self.layout][k]["tipo"] == "alfa":
                        self.info[k] = "%s" % self.info[k].replace(
                            "<!-- Correção de bug da ExtJS -->", ""
                        )
                        self.info[k] = "%s" % self.info[k].replace(
                            "<!-- Correcao de bug da ExtJS -->", ""
                        )
                        self.info[k] = "%s" % self.info[k].replace(
                            "<!-- CORRECAO DE BUG DA EXTJS -->", ""
                        )
                        self.info[k] = "%s" % self.info[k].replace(
                            "<BR><!-- CORRECAO DE BUG DA EXTJS -->", ""
                        )
                        self.info[k] = "%s" % remove_tags(self.info[k])
                    else:
                        if "decimais" in self._protocolo[self.layout][k]:
                            self.info[k] = (
                                float(self.info[k])
                                if k in self.info
                                else self._protocolo[self.layout][k]["valor"]
                            )
                        else:
                            self.info[k] = (
                                int(self.info[k])
                                if k in self.info
                                else self._protocolo[self.layout][k]["valor"]
                            )
                else:
                    self.info[k] = self._protocolo[self.layout][k]["valor"]
                if (
                    self.is_vazio(self.info[k])
                    and self.get_obrigatoriedade_campo_layout(k) == "1*"
                ):
                    self.info[k] = self.get_obrigatoriedade_campo_layout(k)
            except:
                if self.info[k] in ["1*", "2*", "3*", "4*", "5*", "6*", "7*"]:
                    self.info[k] = self.info[k]
                elif self.get_obrigatoriedade_campo_layout(k) == "1*":
                    self.info[k] = "1*"
                else:
                    self.info[k] = self._protocolo[self.layout][k]["valor"]

    def __str__(self):
        coluna_erro = []
        linha = ""
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            if k == "cfg":
                break
            if self.is_obrigatorio_info(k):
                l = self.__class__.get_valor_obrigatorio(
                    label=self._protocolo[self.layout][k]["label"],
                    obrigatorio=self._protocolo[self.layout][k]["obrigatorio"],
                )
                coluna_erro.append(
                    {
                        "campo": {
                            self._protocolo[self.layout][k][
                                "label"
                            ]: self.format_valor_coluna(l)
                        },
                        "linha": k,
                    }
                )
            else:
                l = self.prepare(k)

            try:
                if linha == "":
                    linha += self.format_valor_coluna(l)
                else:
                    linha += self._separador + self.format_valor_coluna(l)
            except Exception as e:
                log.exception(e)
        self.erros(coluna_erro)
        return linha

    def escreve_erro(
        self, arquivo_origem_erro, linha, campo, mensagem, valor_esperado=""
    ):
        try:
            texto = "%s|%s|%s|%s|%s\n" % (
                arquivo_origem_erro,
                linha,
                campo,
                str(mensagem).encode("utf-8"),
                valor_esperado,
            )
            arquivo = open(
                "/tmp/" + self._protocolo["Erro-header"]["cfg"]["nome_arquivo"], "a"
            )
            arquivo.write(texto)
            arquivo.close()
        except Exception as e:
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
            if self._protocolo[self.layout][k]["tipo"] == "alfa":
                return fb.Protocol.prepare_alfa(
                    (
                        self.info[k]
                        if k in self.info
                        else self._protocolo[self.layout][k]["valor"]
                    ),
                    self._protocolo[self.layout][k]["size"],
                    apply_blank=self.apply_blank,
                )
            else:
                if "decimais" in self._protocolo[self.layout][k]:
                    return fb.Protocol.prepare_float(
                        (
                            self.info[k]
                            if k in self.info
                            else self._protocolo[self.layout][k]["valor"]
                        ),
                        self._protocolo[self.layout][k]["size"],
                        self._protocolo[self.layout][k]["decimais"],
                        apply_blank=self.apply_blank,
                    )
                else:
                    return fb.Protocol.prepare_num(
                        (
                            self.info[k]
                            if k in self.info
                            else self._protocolo[self.layout][k]["valor"]
                        ),
                        self._protocolo[self.layout][k]["size"],
                        apply_blank=self.apply_blank,
                    )
        return ""

    def erros(self, coluna_erro):
        for coluna in coluna_erro:
            self.escreve_erro(
                self.layout,
                "linha: %s " % (self.index - 1),
                list(coluna.get("campo").keys())[0],
                list(coluna.get("campo").values())[0],
                "",
            )

    def format_valor_coluna(self, valor):
        return clear_to_ascii(valor) if not isinstance(valor, str) else str(valor)

    def __getitem__(self, idx):
        for k in sorted(self._protocolo[self.layout], key=functools.cmp_to_key(my_cmp)):
            if idx == k or idx == self._protocolo[self.layout][k]["label"]:
                return self.info[k] or self._protocolo[self.layout][k]["valor"]
        return None

    def is_obrigatorio_layout(self, key):
        """
        Este método verifica se o valor informado, para o campo(key), é vazio ou None.
        Também verifica se o campo é obrigatório.
        Caso seja, a resposta será True de outra forma False.
        @param str - key, identificador da linha do campo.
        @return boolean - True caso seja obrigatório, False de outa forma.
        """
        try:
            if self.get_obrigatoriedade_campo_layout(key) in (
                "1*",
                "2*",
                "3*",
                "4*",
                "5*",
                "6*",
                "7*",
            ):
                return True
        except:
            pass
        return False

    def get_obrigatoriedade_campo_layout(self, key):
        """
        Este método retorna a configuração de obrigatoriedade do campo conforme o layout.
        """
        try:
            return self._protocolo[self.layout][key]["obrigatorio"]
        except:
            pass
        return ""

    def is_obrigatorio_info(self, key):
        """
        Este método verifica se o valor informado, para o campo(key), é vazio ou None.
        Também verifica se o campo é obrigatório.
        Caso seja, a resposta será True de outra forma False.
        @param str - key, identificador da linha do campo.
        @return boolean - True caso seja obrigatório, False de outa forma.
        """
        try:
            if self.get_obrigatoriedade_campo_info(key) in (
                "1*",
                "2*",
                "3*",
                "4*",
                "5*",
                "6*",
                "7*",
            ):
                return True
        except:
            pass
        return False

    def get_obrigatoriedade_campo_info(self, key):
        """
        Este método retorna a configuração de obrigatoriedade do campo conforme o layout.
        """
        try:
            return self.info[key]
        except:
            pass
        return ""

    @classmethod
    def get_valor_obrigatorio(cls, **kwargs):
        """
        Este método retorna um texto com o nome.
        @param str - key, identificador da linha do campo.
        @return str - label do campo.
        """
        label = kwargs["label"]
        obrigatorio = kwargs["obrigatorio"]
        if obrigatorio == "1*":
            return "O campo %s é obrigatório para todos!" % label
        elif obrigatorio == "2*":
            return "O campo %s é obrigatório para ativos!" % label
        elif obrigatorio == "3*":
            return "O campo %s é obrigatório para inativos!" % label
        elif obrigatorio == "4*":
            return "O campo %s é obrigatório para pensionistas!" % label
        elif obrigatorio == "5*":
            return "O campo %s é obrigatório para todos afastamentos!" % label
        elif obrigatorio == "6*":
            return (
                "O campo %s é obrigatório para todos afastamentos à disposição!" % label
            )
        elif obrigatorio == "7*":
            return (
                "O campo %s é obrigatório para todos afastamentos por licença!" % label
            )

    @staticmethod
    def is_vazio(valor):
        """
        Este método verifica se o valor informado é vazio ou None.
        @return boolean, True se for vazio, False de outra forma.
        """
        vazio = False
        try:
            if valor == "" or valor is None:
                vazio = True
            elif eval(valor) is None:
                vazio = True
        except:
            pass
        return vazio
