# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from raf.models import TypeQuiz

log = getLogger(__name__)


class RAFTypeQuiz(RestfulDRY):

    force_upper = False

    full_text_index = ("title__icontains",)

    _model = TypeQuiz

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("raf.typequiz.Launcher")')
