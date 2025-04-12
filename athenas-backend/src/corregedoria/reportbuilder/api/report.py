# -*- coding: utf-8 -*-
import os
import json

# from django.http import HttpResponseBadRequest, HttpResponseNotFound
# from contrib.controller import DefaultController
from engine.mq.api.report import MQReportBuilder
from engine.mq.models import Task

# from corregedoria.reportbuilder.tasks import start_report
# from contrib.jasper import Client
from django.conf import settings
from contrib.utils import getLogger

# from functools import partial
log = getLogger(__name__)


class RLReportBuilder(MQReportBuilder):

    def start(self, args=[]):
        pass
        # rst = {
        #     'success': False,
        #     'message': 'Nada feito ainda!'
        # }
        #
        # try:
        #     params = json.loads(self.request.POST.get('params'))
        #     if not 'organ_identifier' in params:
        #         params['organ_identifier'] = settings.ORGAN_IDENTIFIER
        #     report = self.request.POST.get('report')
        #
        #     if getattr(settings, 'REPORT_DEFAULT_PATH', None):
        #         report = ''.join([
        #             '/',
        #             settings.REPORT_DEFAULT_PATH,
        #             report
        #         ])
        #
        #     t = Task.start(
        #         start_report,
        #         report=report,
        #         report_name=self._report_name(**params),
        #         params=params,
        #         output_format=self.request.POST.get('output_format', 'PDF'),
        #         success='''<p>O Relatorio <span style="font-weight:bold">%(report_name)s</span> foi gerado com sucesso. Para fazer o download clique no
        #         <a href="/athenas/MQReportBuilder/file/?uuid=%(task)s&output_format=%(output_format)s">link</a>.
        #         </p>
        #         <p>Esta relatório estara disponivel para download até dia <span style="font-weight:bold">%(deadline)s</span></p>'''
        #     )
        # except Exception as e:
        #     rst.update(message=str(e))
        # else:
        #     rst.update(
        #         success=True,
        #         message='Relatório requisitado com sucesso, você será avisado quando o mesmo for concluido.'
        #     )
        #
        # self.renderer(rst)
