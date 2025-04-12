# -*- coding: utf-8 -*-

import os
import json

from celery import Celery
from contrib.middleware import set_current_user
from engine.mq.models import Task
from datetime import datetime
from rh.gfp.models import Folha, Periodo
from rh.gfp.previdencia import sisprev as sisprev_arquivo
from rh.gfp.previdencia.igeprev import IgeprevGenerator
from rh.gfp.previdencia.sisprevweb import SisprevWebGenerator
from contrib.utils import getLogger
from dateutil.relativedelta import relativedelta


log = getLogger("tasker")

app = Celery("igeprev")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))


@app.task
def generator(task, hook, sheet, user, success):
    state = "failed"
    message = "<p>Gerando arquivos IGEPREV...</p>"
    task = Task.objects.get(uuid=task)
    has_exception = None

    def feedback(progress_message, progress, **kwargs):
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.save()
        sheet_instance = Folha.objects.get(pk=sheet)
        sheet_month = sheet_instance.periodo.mes
        sheet_year = sheet_instance.periodo.ano

        try:
            tfiles = {
                "orgaos_sisprev": sisprev_arquivo.OrgaosSisprev,
                "unidades_sisprev": sisprev_arquivo.UnidadeSisprev,
                "lotacoes_sisprev": sisprev_arquivo.LotacoesSisprev,
                "cargos_sisprev": sisprev_arquivo.CargosSisprev,
                "fontepagadora_sisprev": sisprev_arquivo.FontePagadoraSisprev,
                "tipo_situacaofuncional_sisprev": sisprev_arquivo.TipoSituacaoFuncionalSisprev,
                "estadocivil_sisprev": sisprev_arquivo.EstadoCivilSisprev,
                "escolaridade_sisprev": sisprev_arquivo.EscolaridadeSisprev,
                "tipodependencia_sisprev": sisprev_arquivo.TipoDependenciaSisprev,
                "quadromilitares_sisprev": sisprev_arquivo.QuadroMilitaresSisprev,
                "pessoas_sisprev": sisprev_arquivo.PessoasSisprev,
                "segurados_sisprev": sisprev_arquivo.SeguradosSisprev,
                "seguradoscedidos_sisprev": sisprev_arquivo.SeguradosCedidosSisprev,
                "pessoasdependentes_sisprev": sisprev_arquivo.PessoasDependentesSisprev,
                "dependentes_sisprev": sisprev_arquivo.DependentesSisprev,
                "eventosrubricas_sisprev": sisprev_arquivo.EventosRubricasSisprev,
                "bancos_sisprev": sisprev_arquivo.BancosSisprev,
                "cargosocupados_sisprev": sisprev_arquivo.CargosOcupadosSisprev,
                "financeiro_sisprev": sisprev_arquivo.FinanceiroSisprev,
                "pensoesalimenticias_sisprev": sisprev_arquivo.PensoesAlimenticiasSisprev,
                "contribuicoesmensal_sisprev": sisprev_arquivo.ContribuicoesMensalSisprev,
                # 'contribuicoeshistorico_sisprev': sisprev_arquivo.ContribuicoesHistoricoSisprev,
                # 'contribuicoeshomologacao_sisprev': sisprev_arquivo.ContribuicoesHomologacaoSisprev,
            }

            igeprev_generator = IgeprevGenerator(
                sheet=sheet,
                ano_referencia=sheet_year,
                mes_referencia=sheet_month,
                feedback=feedback,
            )
            igeprev_generator.gerador(tfiles=tfiles, importacao_completa=False)

            state = "ready"
            msg_params = locals()
            msg_params.update(
                deadline=(datetime.now().date() + relativedelta(days=2)).strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
            msg_params.update(uuid=task.uuid)
            msg_params.update(igeprev="%s-%s" % (sheet_month, sheet_year))
            message = success % msg_params
            task.data = json.dumps({"filename": igeprev_generator.get_zip_name()})
        except Exception as err:
            print(err)
        print("IGEPREV gerado para competência %s-%s." % (sheet_month, sheet_year))
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>RH - Falha na geração dos arquivos do IGEPREV."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task
def sisprev_web(task, hook, period, user, success):
    state = "failed"
    message = "<p>Gerando arquivos Sisprev Web - IGEPREV...</p>"
    task = Task.objects.get(uuid=task)
    has_exception = None

    def feedback(progress_message, progress, info=False, **kwargs):
        if info:
            task.info(msg=progress_message % kwargs, type_of=1)
        task.progress_message = progress_message % kwargs
        task.progress = progress
        task.save()

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.save()
        period_instance = Periodo.objects.get(pk=period)
        sheet_month = period_instance.mes
        sheet_year = period_instance.ano

        try:
            generator = SisprevWebGenerator(
                year=sheet_year,
                month=sheet_month,
                feedback=feedback,
            )
            generator.gerador()

            state = "ready"
            msg_params = locals()
            msg_params.update(
                deadline=(datetime.now().date() + relativedelta(days=2)).strftime(
                    "%d/%m/%Y %H:%M"
                )
            )
            msg_params.update(uuid=task.uuid)
            msg_params.update(igeprev="%s-%s" % (sheet_month, sheet_year))
            message = success % msg_params
            task.data = json.dumps({"filename": generator.get_zip_name()})
        except Exception as err:
            log.exception(err)
        log.exception(
            "IGEPREV gerado para competência %s-%s." % (sheet_month, sheet_year)
        )
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "<p>RH - Falha na geração dos arquivos do IGEPREV."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
