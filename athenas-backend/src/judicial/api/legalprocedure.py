# -*- coding: utf-8 -*-
from judicial.api.legalclassification import EJudLegalClassification
from contrib.utils import getLogger
from judicial.models import LegalProcedure


log = getLogger(__name__)


class EJudLegalProcedure(EJudLegalClassification):

    _model = LegalProcedure
