# -*- coding: utf-8 -*-

from logging import getLogger
from datetime import datetime

from rh.classcodes.registration.base import BaseRegistration
from rh.models import Servidor
from standard.models import RunCodeManager, Configuration

log = getLogger(__name__)


@RunCodeManager.register("mpmt-registration")
class MPMTRegistration(BaseRegistration):
    """[summary]

    Arguments:
        object {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    title = "Gerador de matrícula do MPMT"
    description = (
        "Esta classe gera números de matricula utilizando a regra XXXXXXXAA, "
        "onde XXXXXXX é um número sequencial e AA o ano de criação da matrícula"
    )

    MAP_TYPE_EMPLOYEE_WITH_SEQUENCES = {"E": "sequence_trainee", "T": "sequence_out"}

    def __init__(self, by_possession="b", registration_date=None, **kwargs):
        """[summary]

        Keyword Arguments:
            by_possession {[type]} -- [description] (default: {None})
            registration_date {[type]} -- [description] (default: {None})

        Returns:
            [type] -- [description]
        """
        log.debug(">>> %s <<<" % self.__class__)
        self.cfg = Configuration.get_or_create("rh")
        self.by_possession = by_possession
        self.registration_date = (
            datetime.now().date() if not registration_date else registration_date
        )

    def increment_sequence(self, key="sequence_base", increment=1):
        sequence = int(self.cfg.get(key, 1))
        self.cfg.set(key, sequence + increment)
        return sequence + increment

    def _get_next_number(self, increment=0):
        # cfg = Configuration.get_or_create(application='rh')
        if self.by_possession in [
            "EFE",
            "ECM",
            "EFC",
            "CMS",
            "REQ",
            "RCM",
            "RFC",
            "CTR",
            "EXT",
        ]:
            key = "sequence_employee"
        elif self.by_possession in [
            "MBR",
            "MEL",
            "MCM",
            "MEC",
            "MBR2",
            "MEL2",
            "MCM2",
            "MEC2",
        ]:
            key = "sequence_member"
        elif self.by_possession in ["EST", "JCA", "RES"]:
            key = "sequence_trainee_young"
        elif self.by_possession in ["TCR", "VOL"]:
            key = "sequence_voluntary_outsourced"
        elif self.by_possession in ["SAP", "APO", "BFP", "MAP"]:
            key = "sequence_retiree"
        elif self.by_possession in ["COE"]:
            key = "sequence_occasional_collaborator"

        sequence = self.increment_sequence(key=key)
        # sequence = int(self.cfg.get(key, 1).value)
        # if increment:
        #     sequence += increment
        #     self.cfg.set(key, sequence)

        return sequence

    def next_registration_number(self):
        next_registration = self._get_next_number()
        while Servidor.objects.filter(matricula=next_registration).exists():
            next_registration = self._get_next_number(increment=1)

        return next_registration
