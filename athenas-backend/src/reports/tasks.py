from celery import Celery
from engine.mq.const import TIPO_TASK_PROCESSAMENTO_RELATORIO
import pdfkit
import os

from django.template import loader

from contrib.middleware import set_current_user
from engine.mq.models import Task
from contrib.utils import getLogger
from django.template import loader
from reports.utils import (
    create_csv,
    create_file_xls,
    create_file_xlsx,
    criar_doc_docx,
    get_data_model_dinamico,
    get_filename,
    create_gedfile,
    remote_emmiter,
    pdf_header_footer_options,
    run_context_data_function,
    write_odt,
    gerar_arquivo_docx,
    montar_servidor_lotacao_xlsx,
)


log = getLogger("reports")
app = Celery("reports")
app.config_from_object(os.environ.get("CELERY_MODULE_CONFIG", "app.celeryconf"))
app.conf.update(
    worker_pool_restarts=True,
)


@app.task()
def pdf_task(task, **kwargs):
    """
    Está Task é responsável por renderizar um template html e criar um arquivo pdf
    """
    options = pdf_header_footer_options()
    success = kwargs.get("success")
    user = kwargs.get("user")
    html_path = kwargs.get("html_path")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    identifier = kwargs.get("identifier")
    extension = kwargs.get("extension")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    context_data = kwargs.get("context_data")
    origem_apiv2 = kwargs.get("origem_apiv2")
    notificar = kwargs.get("notificar", False)

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        context_data = run_context_data_function(path, class_name, params)
        task.state = "progress"
        task.notificar_hermes = notificar
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_RELATORIO

        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        html = loader.render_to_string(html_path, context_data)
        output = pdfkit.from_string(html, output_path=file_path, options=options)
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)

        if file is None:
            absolute_path = ""
        else:
            absolute_path = file.absolute_path

        task.data = {
            "file": absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        if not origem_apiv2:
            remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


# @app.task()
# def write_pdf_task(task,**kwargs):
#     """
#         Está Task é responsável por escrever um pdf atualizando seus dados"

#     """
#     success = kwargs.get('success')
#     user = kwargs.get('user')
#     html_path = kwargs.get('html_path')
#     mimetype = kwargs.get('mimetype')
#     filename = kwargs.get('filename')
#     extension = kwargs.get('extension')
#     identifier = kwargs.get('identifier')
#     download = kwargs.get('download')
#     params = kwargs.get('params')
#     path = kwargs.get('path')
#     class_name = kwargs.get('class_name')
#     context_data = kwargs.get('context_data')

#     state = 'failed'
#     task = Task.objects.get(uuid=task)
#     has_exception = None
#     message = "'<p>Gerando Relatório...</p>'"
#     try:
#         set_current_user(user)
#         task.message = message
#         context_data = run_context_data_function(path,class_name,params)
#         task.state = 'progress'
#         output = write_pdf(html_path,context_data,identifier)
#         task.data = {'file':output, 'filename':filename, 'mimetype':mimetype, 'extension':extension}
#         remote_emmiter(download, task, class_name, filename)

#         msg_params = locals()
#         msg_params.update(uuid = task.uuid)
#         message = success % msg_params
#         state = 'ready'
#     except Exception as err:
#         log.exception(err)
#         has_exception = err
#         message = err

#     task.message = message
#     task.state = state
#     task.save()

#     if has_exception:
#         raise has_exception


@app.task()
def report_xls(task, **kwargs):
    """
    Está Task é responsável por renderizar um template html criar arquivo xls para o
    relatório de consultas
    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    identifier = kwargs.get("identifier")
    extension = kwargs.get("extension")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    keys = kwargs.get("keys", None)
    origem_apiv2 = kwargs.get("origem_apiv2")
    notificar = kwargs.get("notificar", False)

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.notificar_hermes = notificar
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_RELATORIO

        values = run_context_data_function(path, class_name, params)

        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        output = create_file_xls([values], file_path, values.get("keys", keys))
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        if not origem_apiv2:
            remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def report_xlsx(task, **kwargs):
    """
    Está Task é responsável por renderizar um template html criar arquivo xlsx para o
    relatório de consultas
    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    identifier = kwargs.get("identifier")
    extension = kwargs.get("extension")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    keys = kwargs.get("keys", None)
    origem_apiv2 = kwargs.get("origem_apiv2")
    notificar = kwargs.get("notificar", False)

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.notificar_hermes = notificar
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_RELATORIO

        values = run_context_data_function(path, class_name, params)

        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        output = create_file_xlsx(
            values.get("data"), values.get("keys", keys), file_path
        )
        if not file:
            file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        if not origem_apiv2:
            remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def report_csv(task, **kwargs):
    """
    Está Task é responsável por renderizar um pacote de dados criar arquivo csv.
    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    identifier = kwargs.get("identifier")
    extension = kwargs.get("extension")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    data_model = kwargs.get("data_model")
    origem_apiv2 = kwargs.get("origem_apiv2")
    notificar = kwargs.get("notificar", False)
    campos = kwargs.get("campos", [])

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.notificar_hermes = notificar
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_RELATORIO

        data = None
        if data_model:
            if "dados_lista" in data_model:
                dados_filtrados = [
                    {k: d.get(k, "") for k in campos} for d in data_model["dados_lista"]
                ]
                values = {
                    "data": dados_filtrados,
                    "keys": campos,
                }
            else:
                data = get_data_model_dinamico(data_model, campos)
                values = (
                    data
                    if data
                    else run_context_data_function(path, class_name, params)
                )
        else:
            values = run_context_data_function(path, class_name, params)

        file = get_filename(filename, identifier)
        file_path = file.absolute_path if file else False
        output = create_csv([values], file_path, values.get("keys", None), filename)
        if not file:
            file = create_gedfile(filename, output.encode(), mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }

        if not origem_apiv2:
            remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def write_odt_task(task, **kwargs):
    """
    Está Task é responsável por escrever um pdf atualizando seus dados"

    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    html_path = kwargs.get("html_path")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    extension = kwargs.get("extension")
    identifier = kwargs.get("identifier")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    context_data = kwargs.get("context_data")

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        context_data = run_context_data_function(path, class_name, params)
        task.state = "progress"
        output = write_odt(html_path, context_data, identifier)
        task.data = {
            "file": output,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def create_docx_task(task, **kwargs):
    """
    Está Task é responsável cria um arquivo DOCX"

    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    html_path = kwargs.get("html_path")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    extension = kwargs.get("extension")
    identifier = kwargs.get("identifier")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    context_data = kwargs.get("context_data")

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        context_data = run_context_data_function(path, class_name, params)
        task.state = "progress"
        output = criar_doc_docx(context_data, html_path)
        file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def criar_task_docx(task, **kwargs):
    """
    Está Task é responsável cria um arquivo DOCX"

    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    html_path = kwargs.get("html_path")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    extension = kwargs.get("extension")
    identifier = kwargs.get("identifier")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    context_data = kwargs.get("context_data")

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"
    try:
        set_current_user(user)
        task.message = message
        context_data = run_context_data_function(path, class_name, params)
        task.state = "progress"
        log.info(f"par {params}")
        output = gerar_arquivo_docx(html_path, context_data)
        file = create_gedfile(filename, output, mimetype, identifier)
        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }
        remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = err

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception


@app.task()
def criar_task_servidores_lotacao(task, **kwargs):
    """
    Está Task é responsável por renderizar um template html criar arquivo xls para o
    relatório de consultas
    """
    success = kwargs.get("success")
    user = kwargs.get("user")
    mimetype = kwargs.get("mimetype")
    filename = kwargs.get("filename")
    identifier = "servidores-lotacao-excel"
    extension = kwargs.get("extension")
    download = kwargs.get("download")
    params = kwargs.get("params")
    path = kwargs.get("path")
    class_name = kwargs.get("class_name")
    keys = kwargs.get("keys", None)
    origem_apiv2 = kwargs.get("origem_apiv2")
    notificar = kwargs.get("notificar", False)

    state = "failed"
    task = Task.objects.get(uuid=task)
    has_exception = None
    message = "'<p>Gerando Relatório...</p>'"

    try:
        set_current_user(user)
        task.message = message
        task.state = "progress"
        task.notificar_hermes = notificar
        task.tipo_processamento = TIPO_TASK_PROCESSAMENTO_RELATORIO

        values = run_context_data_function(path, class_name, params)

        output = montar_servidor_lotacao_xlsx(values.get("lotacoes", []), None)
        file = create_gedfile(filename, output, mimetype, identifier)

        task.data = {
            "file": file.absolute_path,
            "filename": filename,
            "mimetype": mimetype,
            "extension": extension,
        }

        remote_emmiter(download, task, class_name, filename)

        msg_params = locals()
        msg_params.update(uuid=task.uuid)
        message = success % msg_params
        state = "ready"
    except Exception as err:
        log.exception(err)
        has_exception = err
        message = "Falha ao tentar criar o relatório."

    task.message = message
    task.state = state
    task.save()

    if has_exception:
        raise has_exception
