# -*- coding: utf-8 -*-
from judicial.api.legalclassification import EJudLegalClassification
from contrib.utils import getLogger
from judicial.models import LegalMoviment as LegalMovement

log = getLogger(__name__)


class EJudLegalMoviment(EJudLegalClassification):

    _model = LegalMovement
