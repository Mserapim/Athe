# -*- coding: utf-8 -*-

import threading

from django.contrib.auth.models import User

from contrib.decorator import login_required
from contrib.middleware import set_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import get_json_engine, getLogger
from engine.models import TaskSession
from engine.mq.models import Task
from rh.gfp.dirf.models import (
    Declaracao,
    Demonstrativo,
    Dialect,
    DirfSummary,
    NaturezaRendimento,
    Token,
)
from rh.gfp.dirf.tasks import summarize_dirf_by_dialect

# from django.conf import settings

json = get_json_engine()
log = getLogger(__name__)


class DIRFDirfSummary(RestfulDRY):

    _model = DirfSummary

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "code__codigo__iexact",
        "calendar_year__iexact",
        "person__nome__icontains",
        "info__icontains",
        "person__pessoajuridica__cnpj__iexact",
        "person__pessoafisica__cpf__iexact",
    )


class DIRFDirfSummaryFinancial(DIRFDirfSummary):

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.dirf.DirfSummaryManage")')

    # def get_query(self):
    #     return super(DIRFDirfSummaryFinancial, self).get_query().filter(dirf_created=False)


class DIRFNaturezaRendimento(RestfulDRY):

    _model = NaturezaRendimento

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = ("codigo__iexact", "titulo__icontains")


class DIRFIncomeTaxReturn(RestfulDRY):

    _model = Declaracao


class DIRFFileIncomeTax(RestfulDRY):

    _model = Demonstrativo

    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "servidor__matricula__iexact",
    )

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.dirf.DemonstrativoManage")')


class DIRFDialect(RestfulDRY):

    _model = Dialect

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = (

    # )

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    force_upper = False

    @login_required("JSON")
    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("rh.gfp.dirf.DialectManage")')

    @login_required("JSON")
    def engine(self, args=[]):
        rst = {
            "count": 0,
            "success": False,
            "message": "Nada foi executado ainda!",
            "collection": [],
        }

        rst.update(
            count=len(rst["collection"]), success=True, message="Processao com sucesso!"
        )

        rendererer = self.get_renderer(
            self.request.META.get("HTTP_ACCEPT", "text/json")
        )
        rendererer(rst)

    @login_required("JSON")
    def summarize(self, args=[]):
        """Cria um thread para sumarizar a DIRF para um determinado dialect.

        Args:
            args (list, optional): Description

        Returns:
            JSON: Object rendererizado para o response
        """
        obj = {
            "success": True,
            "message": "A DIRF %s está sendo gerada pelo sistema! Acompanhe no gestor de tarefas.",
        }

        dialect = Dialect.objects.get(pk=self.request.POST.get("dialect"))
        receipt_number = self.request.POST.get("receipt_number") or ""

        can = self.check_permission(
            self.request.user,
            "change",
            self.Model._meta.app_label,
            self.Model._meta.object_name,
        )
        if can is False:
            obj.update(
                success=False,
                message="Você não tem permissão para processar %s."
                % self.Model._meta.object_name,
            )
        else:
            Task.start(
                summarize_dirf_by_dialect,
                description="Sumarizando folha de pagamento para DIRF %s" % dialect,
                dialect_id=dialect.pk,
                user=self.request.user.id,
                receipt_number=receipt_number,
                clear=True,
            )

        # Task.start(
        #     process_evaluation_differences_payroll,
        #     description=u'Avaliando diferenças da folha %s' % payroll,
        #     payroll_id=payroll.pk,
        #     user=self.request.user.id,
        # )
        # self.response.write(json.encode(obj))

        # método 'process' foi comentado na atualização vinda de TO em 2023-Jan

        # def process(request, dialect, log, receipt_number, user_id):
        #     user = User.objects.get(pk=user_id)
        #     set_current_user(user)
        #     # log.debug(('******************')
        #     task = TaskSession.start_execution('Processando DIRF %s/%s' %
        #                                        (dialect.calendar_year, dialect.reference_year))
        #     try:
        #         dialect.summarize_entries(clear=True, task=task)
        #         dialect.generate_file(receipt_number=receipt_number, task=task)
        #     except Exception as e:
        #         log.exception(e)
        #         task.finish_execution('Erro ao gerar DIRF! (%s)' % e)
        #     else:
        #         task.finish_execution()
        # # log.debug(('INICIANDO SUMMARIZE')
        # t = threading.Thread(target=process, args=(self.request, dialect, log, receipt_number, self.request.user.id))
        # t.start()
        # log.debug('INICIADO SUMMARIZE')

        # self.response['content-type'] = 'text/javascript'
        self.response.write(json.encode(obj))

    @login_required("JSON")
    def generate(self, args=[]):
        """Cria um thread para gerar o arquivo da DIRF para um determinado dialect.

        Args:
            args (list, optional): Description

        Returns:
            JSON: Object rendererizado para o response
        """
        obj = {
            "success": True,
            "message": "O arquivo da DIRF %s está sendo gerado pelo sistema! Acompanhe no gestor de tarefas.",
        }

        dialect = Dialect.objects.get(pk=self.request.POST.get("dialect"))
        receipt_number = self.request.POST.get("receipt_number") or ""

        # Task.start(
        #     summarize_dirf_by_dialect,
        #     description=u'Sumarizando folha de pagamento para DIRF %s' % dialect,
        #     dialect_id=dialect.pk,
        #     user=self.request.user.id,
        #     clear=True
        # )

        # Task.start(
        #     process_evaluation_differences_payroll,
        #     description=u'Avaliando diferenças da folha %s' % payroll,
        #     payroll_id=payroll.pk,
        #     user=self.request.user.id,
        # )
        # self.response.write(json.encode(obj))

        # dialect = Dialect.objects.get(pk=self.request.POST.get('dialect'))
        # receipt_number = self.request.POST.get('receipt_number') or ''

        def process(request, dialect, log, receipt_number, user_id):
            user = User.objects.get(pk=user_id)
            set_current_user(user)
            log.debug("******************")
            task = TaskSession.start_execution(
                "Gerando arquivo da DIRF %s/%s"
                % (dialect.calendar_year, dialect.reference_year)
            )
            try:
                # dialect.summarize_entries(clear=True, task=task)
                dialect.generate_file(receipt_number=receipt_number, task=task)
            except Exception as e:
                log.exception(e)
                task.finish_execution("Erro ao gerar DIRF! (%s)" % e)
            else:
                task.finish_execution()

        log.debug("INICIANDO SUMMARIZE")
        t = threading.Thread(
            target=process,
            args=(self.request, dialect, log, receipt_number, self.request.user.id),
        )
        t.start()
        log.debug("INICIADO SUMMARIZE")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))


class DIRFToken(RestfulDRY):

    _model = Token

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "nome__icontains",
        "id_receita__icontains",
    )
