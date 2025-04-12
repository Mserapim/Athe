# -*- coding: utf-8 -*-

from datetime import datetime
from logging import getLogger

from rh.models import Servidor
from standard.models import Configuration, RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("registration-base")
class BaseRegistration(object):
    """Esta classe é a interface basica para geracao automatica
    de numeros de matrícula

    Arguments:
        object {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    typeof = "REGISTRATION"
    title = "Gerador básico de matrícula"
    description = "Esta classe gera números de matricula sequenciais comecando de 1"

    MAP_TYPE_EMPLOYEE_WITH_SEQUENCES = {}

    def __init__(self, employee_type="b", registration_date=None, **kwargs):
        """[summary]

        Keyword Arguments:
            employee_type {[type]} -- [description] (default: {None})
            registration_date {[type]} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """
        log.debug(">>> %s <<<" % self.__class__)
        self.cfg = Configuration.get_or_create("rh")
        self.employee_type = employee_type
        self.registration_date = (
            datetime.now().date() if not registration_date else registration_date
        )

    class RegistrationNumberAlreadyExists(Exception):
        def __init__(self, rnumber=None):
            Exception.__init__(self, "Matrícula %s já existe!" % rnumber)

    @property
    def seq_key(self):
        return "seq_reg_b"

    def get_sequences(self):
        return {self.seq_key: self.cfg.get(self.seq_key, 0)}

    def increment_sequence(self, increment=0):
        sequence = int(self.cfg.get(self.seq_key, 1))
        self.cfg.set(self.seq_key, sequence + increment)
        return sequence + increment

    def _get_next_number(self, increment=0):
        """Este metodo deve retorna o proximo sequencial a ser utilzido na geracao da matricula

        Returns:
            int -- proximo sequencial para geracao da matricula
        """
        return self.increment_sequence(increment)

    def next_registration_number(self):
        next_registration = self._get_next_number()
        while Servidor.objects.filter(matricula=next_registration).exists():
            next_registration = self._get_next_number(1)

        return next_registration


@RunCodeManager.register("registration-typeyear")
class TypeYearRegistration(BaseRegistration):
    """[summary]

    Arguments:
        object {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    title = "Gerador de matrícula no formato TAAXXX"
    description = """Esta classe gera números de matricula utilizando a regra TAAXXX, onde:
    T: numero que identifica o tipo de servidor
    AA: 2 digitos que indentificam o ano
    XXX: sequencial de matricula no ano, deve ser zerado a cada ano
    """

    MAP_TYPE_EMPLOYEE_WITH_SEQUENCES = {
        "EST": 2,
        "VOL": 3,
        "TCR": 4,
        "JCA": 5,
        "MAP": 7,
        "SAP": 7,
        "BFP": 8,
        "COE": 9,
    }

    def get_sequences(self):
        seqs = {}
        for k in list(self.MAP_TYPE_EMPLOYEE_WITH_SEQUENCES.keys()) + ["b"]:
            skey = "seq_reg_%04d_%s" % (self.registration_date.year, k.lower())
            seqs[skey] = self.cfg.get(skey, 0)
        return seqs

    @property
    def seq_key(self):
        key = "b"
        if self.employee_type in list(self.MAP_TYPE_EMPLOYEE_WITH_SEQUENCES.keys()):
            key = self.employee_type
        return "seq_reg_%04d_%s" % (self.registration_date.year, key.lower())

    def _get_next_number(self, increment=0):
        prefix = self.MAP_TYPE_EMPLOYEE_WITH_SEQUENCES.get(self.employee_type, 1)
        year_multiple = int(self.registration_date.strftime("%y"))
        seq_number = self.increment_sequence(increment)

        return int("%d%02d%03d" % (prefix, year_multiple, seq_number))
