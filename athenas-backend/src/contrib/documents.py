# /usr/bin/env python
# -*- coding:UTF-8 -*-
# fonte: http://www.python.org.br/wiki/VerificadorDeCPF

import re

from validate_docbr import CPF as CPFValidateDocBr


class DigitValidator(object):

    # Tamanho total da string a ser validada
    MAX_LENGHT = 11

    # Tamanho da string base, sem o dígito
    LENGHT_OF_BASE = 9

    # Divisor do algorito de geração do dígito verificador
    DIVISOR_DIGIT = 11

    # Tipo de documento
    LABEL = "Doc"

    WEIGHTS = []

    EXCEPTIONS = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999",
    ]

    def __init__(self, number):
        """O argumento number pode ser uma string nas formas:

        12345678910
        123.456.789-10

        ou uma lista ou tuple
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0]
        (1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 0)

        ou um inteiro de %d digitos ou menor, no caso de ser menor
        será completado com zeros à esquerda
        58563625412
          254500025
        """ % (
            self.MAX_LENGHT
        )

        if isinstance(number, str):
            if not number.isdigit():
                number = self._translate(number)
        elif isinstance(number, int):
            number = "%s" % number
            if len(number) < self.MAX_LENGHT:
                number = number.rjust(self.MAX_LENGHT, "0")

        self.number = [int(x) for x in number]

        if not self.isValid():
            raise Exception("Número de %s %s inválido!!" % (self.LABEL, number))

    @staticmethod
    def _translate(number):
        return "".join(re.findall(r"\d", number))

    @classmethod
    def _gen_digit(cls, number):
        """Gera o próximo dígito do número de number"""
        digit = []

        new_number = number[: cls.LENGHT_OF_BASE]

        while len(new_number) < cls.MAX_LENGHT:
            weights = cls.WEIGHTS[cls.MAX_LENGHT - len(new_number) - 1 :]
            res = (
                sum([x * y for (x, y) in zip(new_number, weights)]) % cls.DIVISOR_DIGIT
            )
            d = (cls.DIVISOR_DIGIT - res) if res > 1 else 0
            # print '%s > %d' % (weights, d)
            new_number.append(d)
            digit.append(d)
            # weights.insert(0, 6)

        return digit

    @classmethod
    def _exceptions(cls, number):
        """Se o número de number estiver dentro das exceções é inválido"""
        if len(number) != cls.MAX_LENGHT:
            return True
        else:
            s = "".join(str(x) for x in number)
            if s in cls.EXCEPTIONS:
                return True
        return False

    def __getitem__(self, index):
        """Retorna o dígito em index como string"""

        return self.number[index]

    def __repr__(self):
        """Retorna uma representação 'real', ou seja:

        eval(repr(number)) == number

        """

        return "%s('%s')" % (self.LABEL, "".join(str(x) for x in self.number))

    def __eq__(self, other):
        """Provê teste de igualdade para números de number"""

        return isinstance(other, self.number) and self.number == other.number

    def __str__(self):
        """Retorna uma representação do number na forma:

        123.456.789-10

        """

        d = iter("..-")
        s = list(map(str, self.number))
        for i in range(3, 12, 4):
            s.insert(i, next(d))
        r = "".join(s)
        return r

    def isValid(self):
        """Valida o número de number"""

        if self._exceptions(self.number):
            return False

        s = self.number[: self.LENGHT_OF_BASE]
        s += self._gen_digit(s)
        # s.append(self._gen_digit(s))
        return s == self.number[:]

    @property
    def clear(self):
        return "".join(str(x) for x in self.number)


class CPF(DigitValidator):

    # Tamanho total da string a ser validada
    MAX_LENGHT = 11

    # Tamanho da string base, sem o dígito
    LENGHT_OF_BASE = 9

    # Divisor do algorito de geração do dígito verificador
    DIVISOR_DIGIT = 11

    # Tipo de documento
    LABEL = "CPF"

    WEIGHTS = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

    EXCEPTIONS = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999",
    ]


class CNPJ(DigitValidator):

    # Tamanho total da string a ser validada
    MAX_LENGHT = 14

    # Tamanho da string base, sem o dígito
    LENGHT_OF_BASE = 12

    # Divisor do algorito de geração do dígito verificador
    DIVISOR_DIGIT = 11

    # Tipo de documento
    LABEL = "CNPJ"

    WEIGHTS = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    EXCEPTIONS = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999",
    ]


class NIS(CPF):

    # Tamanho total da string a ser validada
    MAX_LENGHT = 11

    # Tamanho da string base, sem o dígito
    LENGHT_OF_BASE = 10

    # Divisor do algorito de geração do dígito verificador
    DIVISOR_DIGIT = 11

    # Tipo de documento
    LABEL = "NIS"

    WEIGHTS = [3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    EXCEPTIONS = [
        "00000000000",
        "11111111111",
        "22222222222",
        "33333333333",
        "44444444444",
        "55555555555",
        "66666666666",
        "77777777777",
        "88888888888",
        "99999999999",
    ]

    #     return ''.join(str(x) for x in self.nis)


def mascarar_cpf(cpf):
    """
    Método para colocar máscara em um número de CPF.
    """

    cpf_klass = CPFValidateDocBr()

    try:
        return cpf_klass.mask(cpf)
    except:
        return None
