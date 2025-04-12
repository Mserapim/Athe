# -*- coding: utf-8 -*-
"""
    Declaração de Exception.
"""


from contrib.utils import getLogger

log = getLogger("Ferias:exceptions")


class FeriasError(Exception):
    """
    Classe base para as exceptions das férias
    """

    def __init__(self, value):
        self.value = value
        self.header = "Rh.Férias"

    def __str__(self):
        return repr("Erro: %s" % (self.value))


class DataReferenciaNotFoundError(FeriasError):
    """
    Dispara exceção quando um servidor não possui uma 'data de referência de férias'
    """

    def __str__(self):
        return repr(
            "%s - Servidor %s sem data de referência para férias"
            % (self.header, self.value)
        )


class InvalidStateFeriasError(FeriasError):

    def __str__(self):
        return repr("Operação não permitida: %s" % (self.value))


class ValidateFeriasError(FeriasError):
    def __str__(self):
        return repr("Erro de validação: %s" % (self.value))


class ConflictFeriasError(FeriasError):
    def __init__(self, value):
        super(ConflictFeriasError, self).__init__(
            """Sua parcela não pode ser marcada para esta data, pois está em conflito com todos os seus
                substitutos. Infringindo, contudo, o Art. 3° do Ato 220/2005. <br>%s"""
            % value
        )
