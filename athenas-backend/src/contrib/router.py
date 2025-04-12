# -.- coding: utf-8 -.-
import traceback

from time import time
from importlib import import_module
from django.contrib.auth.models import AnonymousUser
from django import http
from django import template
from datetime import datetime
from django.conf import settings
from contrib.utils import getLogger
from contrib.controller import DefaultController


log = getLogger(__name__)


class _Router(object):
    controllers = None

    @classmethod
    def _call_action(klass, req, res, action, args):
        if getattr(action, "__update_timeout_session__", True):
            log.debug("%s update timeout session." % action)
            req.session.set_expiry(getattr(settings, "TIMEOUT_SESSION", 1200))
        else:
            log.debug("%s not update timeout session." % action)
            pass

        if getattr(action, "_is_public", False) or req.user.is_active:
            t_start = time()
            action(args)
            t_end = time()
            res["Response-Time"] = "%0.3fms" % ((t_end - t_start) * 1000.0)
        else:
            res.status_code = 403

    @classmethod
    def execute(klass, context, req, res):
        t_start = time()
        klass.prepare()
        t_end = time()
        print("Load time for read controllers: %0.3fms" % ((t_end - t_start) * 1000.0))

        Controller = klass.controllers.get(context.get("controller"), None)

        if Controller:
            controller = Controller(req, res, context.get("response_format"))
            action = getattr(controller, context.get("action", None), None)

            if action:
                klass._call_action(req, res, action, context.get("args", []))
                res = controller.response
            else:
                res.status_code = 404
        else:
            res.status_code = 404

        return res

    @classmethod
    def is_valid_controller(klass, Controller, name):
        blacklist = ["Restful", "RestfulDRY", "DefaultController", "ExtWidget"]

        if name not in blacklist:
            return isinstance(Controller, type) and issubclass(
                Controller, DefaultController
            )

        return False

    @classmethod
    def _register_controller(klass, Controller, name):
        try:
            if klass.is_valid_controller(Controller, name):
                klass.controllers.update({name: Controller})
        except Exception as e:
            print(e)
            log.exception(e)

    @classmethod
    def prepare(klass):
        if not klass.controllers:
            ROUTER = getattr(settings, "ROUTER", {})
            klass.controllers = {}
            for controler_lib in ROUTER.get("controllers", []):
                pkg = import_module(controler_lib)
                for attr in dir(pkg):
                    item = getattr(pkg, attr, None)
                    klass._register_controller(item, attr)


def check_autorized(request, conf):
    """
    Verifica se a requisição é de um usuário que esta autênticado.
    :param request Requisição para ser analisada.
    :return Retorna True se o usuário estiver autenticado e não for AnonymousUser.
    """
    result = False
    if conf:
        if not isinstance(request.user, AnonymousUser):
            result = True
        else:
            result = False
    return result


def router_function(request, url=""):
    """
    Faz o roteamento das requisições dos usuários para chamada de actions em controladores.
    @param request: Requisição do Usuário.
    @param url: URL requisitada pelo usuário.
    @return: Retorna um HttpReponse com o processamento do Usuário.
    """
    response = http.HttpResponse()
    dt = datetime.now()

    response["Expires"] = "Mon, 26 Jul 1997 05:00:00 GMT"
    response["Last-Modified"] = dt.strftime("%a, %d %b %Y %H:%M:%S")
    response["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, post-check=0, pre-check=0"
    )
    response["Pragma"] = "no-cache"

    return _Router.execute(__router_extract_dictionary__(url), request, response)


def __router_build_runtime_source__(ctx):
    """
    Elabora código para ser executado pelo procedimento <b>__router_excute_runtime_source__</b>.
    @param ctx: Dicionario de dados contendo as informações da URL.
    @return: String com código gerado.
    """
    src = ""

    try:
        # fd = open(template.__path__[0] + "/router_call_controller.txt", "r")
        fd = open("/app/root/contrib/template/router_call_controller.txt", "r")
        buf = fd.read()
        fd.close()

        tmp = template.engines["django"].from_string(buf)
        # tmp = template.engine.Engine().from_string(buf)

        src = tmp.render(ctx)
    except Exception as e:
        log.exception(e)
        traceback.print_exc()

    return src


def __router_extract_dictionary__(url):
    """
    Extrai as informações da url para um dicionario de dados, contendo o nome do Controller,
    Action e os parametros se for possível.
    @param url: URL requisitada pelo usuário.
    @return: Retorna um dicionario de dados contendo as informações da URL.
    """
    ctx = {}
    default = settings.ROUTER["default"]
    part = url.split("/")

    # Caso da url /application/
    if len(part) == 0:
        ctx["controller"] = default["controller"]
        ctx["action"] = default["action"]
        ctx["args"] = ()
    # Caso da url /application/controller/
    elif len(part) == 1:
        ctx["controller"] = part[0]
        ctx["action"] = default["action"]
        ctx["args"] = ()
    # Caso da url /application/controller/action/
    elif len(part) == 2:
        ctx["controller"] = part[0]
        ctx["action"] = part[1]
        ctx["args"] = ()
    # Caso da url /application/controller/arg1/../argN
    elif len(part) > 2:
        ctx["controller"] = part[0]
        ctx["action"] = part[1]
        ctx["args"] = part[2:]
    # Caso da url vir com alguma anormalidade
    else:
        ctx["controller"] = default["controller"]
        ctx["action"] = default["action"]
        ctx["args"] = ()

    if ctx["controller"] == "":
        ctx["controller"] = default["controller"]
    if ctx["action"] == "":
        ctx["action"] = default["action"]

    """
    A linha abaixo serve para que o router encontre o controller mesmo se o nome controller na url
    estiver com 1ª letra minuscula. Visto que o padrão de Python é que as classes sejam
    com letra maiuscula caso contrário geraria uma exceção de classe não encontrada
    """
    ctx["controller"] = ctx["controller"][0].capitalize() + ctx["controller"][1:]

    """
    Verifica se a resposta será restful e qual o formato que será utilizado.
    """
    if part[-1] == "/":
        part = part[:-1]

    if "json" in part[-1]:
        ctx["response_format"] = "json"
    elif "xml" in part[-1]:
        ctx["response_format"] = "xml"
    elif "serial" in part[-1]:
        ctx["response_format"] = "serial"
    else:
        ctx["restful"] = url

    return ctx


def __router_execute_runtime_source__(request, response, src):
    """
    Executa código em python gerado pelo procedimento <b>__router_build_runtime_source__</b>.
    @param src: Código fonte a ser executado.
    @return: Retorna <b>True</b> se a execução ocorrer sem nenhum erro.
    """
    try:
        exec(src, globals(), locals())

        if ERROR:
            ltb = ERROR_TRACEBACK
            response["content-type"] = "text/html"
            response.write("<html><body>")
            response.write("<p>Source Code</p>")
            response.write("<pre>")

            lines = src.split("\n")
            c = 1
            for line in lines:
                response.write("#{0}\t{1}\n".format(c, line))
                c += 1

            response.write("</pre><hr/>")
            response.write("<p>Traceback</p>")
            response.write("<pre>")
            if ltb:
                for line in ltb:
                    response.write(line)
                    response.write("\n")

            response.write(ERROR_EXCEPTION)
            response.write("</pre>")
            response.write("</body></html>")
            return
    except Exception as exception:
        ltb = traceback.extract_stack()
        response.write("<p>Source Code</p>")
        response.write("<pre>")
        response.write(src)
        response.write("</pre><hr/>")
        response.write("<p>Traceback</p>")
        response.write("<pre>")
        if ltb:
            for line in ltb:
                response.write(line)
                response.write("\n")

        response.write(exception)
        response.write("</pre>")
