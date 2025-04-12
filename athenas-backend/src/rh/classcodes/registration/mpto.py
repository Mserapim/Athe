# -*- coding: utf-8 -*-

from logging import getLogger

from rh.classcodes.registration.base import BaseRegistration
from rh.models import Servidor
from standard.models import RunCodeManager

log = getLogger(__name__)


@RunCodeManager.register("mpto-registration")
class MPTORegistration(BaseRegistration):
    """[summary]

    Arguments:
        object {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    title = "Gerador de matrícula do MPTO"
    description = (
        "Esta classe gera números de matricula utilizando a regra XXXXXXXAA, "
        "onde XXXXXXX é um número sequencial e AA o ano de criação da matrícula"
    )

    MAP_TYPE_EMPLOYEE_WITH_SEQUENCES = {"E": "sequence_trainee", "T": "sequence_out"}

    def increment_sequence(self, key="sequence_base", increment=1):
        sequence = int(self.cfg.get(key, 1))
        self.cfg.set(key, sequence + increment)
        return sequence + increment

    def _get_next_number(self, increment=0):
        # cfg = Configuration.get_or_create(application='rh')
        if self.employee_type in ["S", "M", "V"]:
            key, multiple, sufixe = (
                "sequence_base",
                100,
                int(self.registration_date.strftime("%y")),
            )
        elif self.employee_type in ["E"]:
            key, multiple, sufixe = (
                "sequence_trainee",
                100,
                int(self.registration_date.strftime("%y")),
            )
        elif self.employee_type in ["T"]:
            key, multiple, sufixe = (
                "sequence_out",
                10000,
                int(self.registration_date.strftime("%Y")),
            )

        sequence = self.increment_sequence(key=key)
        # sequence = int(self.cfg.get(key, 1).value)
        # if increment:
        #     sequence += increment
        #     self.cfg.set(key, sequence)

        return sequence * multiple + sufixe

    def next_registration_number(self):
        next_registration = self._get_next_number()
        while Servidor.objects.filter(matricula=next_registration).exists():
            next_registration = self._get_next_number(increment=1)

        return next_registration
