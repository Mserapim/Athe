# -*- coding: utf-8 -*-
from judicial.api.legalclassification import EJudLegalClassification
from contrib.utils import getLogger
from judicial.models import LegalMatter


log = getLogger(__name__)


class EJudLegalMatter(EJudLegalClassification):

    _model = LegalMatter
