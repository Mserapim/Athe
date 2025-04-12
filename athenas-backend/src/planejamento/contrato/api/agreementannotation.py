# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from contrib.middleware import get_current_user
from planejamento.contrato.models import AgreementAnnotation, MinuteAnnotation
from contrib.nil import nil_display
from django.db.models import Q

log = getLogger(__name__)


class PHAAgreementAnnotation(RestfulDRY):

    _model = AgreementAnnotation

    force_upper = False

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("planning.hiring.agreementannotation.Manage")')


class PHAMinuteAnnotation(RestfulDRY):

    _model = MinuteAnnotation

    force_upper = False
