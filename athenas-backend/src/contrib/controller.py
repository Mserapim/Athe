# -.- coding: utf-8 -.-
import pickle
import os
import threading
import random
import hashlib
import time
import codecs

from django.template import engines
from django.conf import settings

from contrib.utils import getLogger, get_json_engine


"""
FIXME isto deve ser corrigido parta usar o novo sistema de temapltes do django
"""
TEMPLATE_DIRS = getattr(settings, "TEMPLATES", [{}])[0].get("DIRS", [])

CONTEXT = getattr(settings, "CONTEXT", "")
DEBUG = getattr(settings, "DEBUG", False)


json = get_json_engine()


class ContentType(object):

    def __init__(self, content_type):
        self.content_type = content_type
        self.log = getLogger(self.__class__.__name__)

    def __call__(self, method):
        def wrapper(*args, **kargs):
            the_self = args[0]
            the_self.response["content-type"] = self.content_type
            method(*args, **kargs)

        return wrapper


class DefaultController(object):
    """
    Controlador default utilizado pelo router.
    """

    request = None

    response = None

    log = None

    def __init__(self, request, response, response_format=False):
        """
        Construtor do Controller Default.
        @param request: HttpRequest da chamada.
        @param response: HttpResponse da chamada.
        @return: Devolve uma instancia do Controlador Default.
        """
        self.request = request
        self.response = response
        self.response_format = response_format
        self.log = getLogger(self.__class__.__name__)

    def index(self, args):
        """
        Página inicial default.
        :param args Array com argumentos passado pela URL.
        :return Este metodo não tem retorno.
        """
        self.response["Content-Type"] = "text/plain"
        self.response.write("Página default")

    def load_static_template(self, filename):
        """
        Metodo que ler um arquivo especificado em filename e joga dentro de uma instancia do Django Template.
        :param filename Nome do arquivo para carregar o Template.
        :return Retorna uma instância de django.template.Template com o conteúdo do arquivo.
        """
        return engines["django"].from_string(self.load_static_file(filename))

    def load_static_file(self, filename):
        """
        Metodo que ler um arquivo especificado em filename e devolve como str.
        :param filename Nome do arquivo para carregado.
        :return Retorna uma str com o conteúdo do arquivo.
        """
        try:
            f = open(filename, "r")
            b = ""
            for line in f.readlines():
                b += line
            f.close()
            return b
        except Exception:
            raise Exception("CAN'T_LOAD_STATIC_FILE {0}".format(filename))

    def render(self, data={}, template=None):
        import contrib.ezjson as json

        if self.response_format == "serial":
            return self.response.write(pickle.dumps(data))
        elif self.response_format == "json":
            return self.response.write(json.dump(data, max_depth=5))

        return (
            self.render_template(template, data)
            if template
            else self.response.write(data)
        )

    def render_template(self, filename, pars={}):
        """
        Atalho para a renderizar o template carregado a partir da função load_static_template.
        @param filename: path do arquivo de template à ser renderizado
        @param pars: dicionário com os parâmetros para renderização do template
        @return: template renderizado
        """
        from datetime import datetime as time
        import locale

        try:
            locale.setlocale(locale.LC_ALL, "pt_BR.utf8")
        except Exception:
            pass
        feira = "-feira" if time.now().strftime("%w") not in ("0", "6") else ""

        pars["date"] = time.now().strftime("Tocantins, %A" + feira + ", %d de %B de %Y")
        pars["context"] = CONTEXT
        return self.response.write(
            self.load_static_template(self.__get_template_path(filename)).render(pars)
        )

    def render_error(
        self,
        error="Erro.",
        message="",
        link="",
        detail="",
        extends="templates/template.html",
    ):
        pars = {
            "error": error,
            "message": message,
            "link": link,
            "detail": detail,
            "extends_template": self.__get_template_path(extends),
        }
        return self.render_template("base/templates/error.html", pars)

    def redirect(self, url):
        """
        Função para redirecionar para outra página.
        @param url: url da página para onde deve ser redirecionada
        @return: Escreve o html responsável pelo redirecionamento.
        """
        return self.response.write(
            '<html><head><meta http-equiv="refresh" content="0;URL=/%s/%s"></head><body></body></html>'
            % (CONTEXT, url)
        )

    def set_restful(self, kind="json"):
        self.response_format = kind

    def __get_template_path(self, filename):
        for path in TEMPLATE_DIRS:
            tmp = "%s/%s" % (path, filename)
            if os.path.exists(tmp):
                filename = tmp
                break
        return filename


class JsonResponseController(DefaultController):

    def render(self, data, **kwargs):

        from django.http import JsonResponse

        if not kwargs.get("encoder"):
            from contrib.helpers import JsonEncoder

            kwargs["encoder"] = JsonEncoder
        self.response = JsonResponse(data, safe=False, **kwargs)


class CommandController(DefaultController):

    # prefix = '/tmp/cc_'
    prefix = os.path.join(getattr(settings, "CACHE_PATH", ""), "cc_")

    def __contains__(self, key):
        obj = {}

        try:
            with open(self.getSessionFilename(self.request.POST.get("sid")), "r") as fd:
                obj = json.decode(fd.read())
        except Exception as e:
            self.log.exception(e)

        return key in obj

    def createSessionId(self, args=[]):
        obj = {}

        random.seed(os.urandom(10))
        magic = random.randint(0, 999999999)
        h = hashlib.new("md5")
        h.update(str(magic).encode())

        obj.update(sid=h.hexdigest())

        for k in self.request.POST:
            if isinstance(self.request.POST.getlist(k), (list, tuple)):
                obj[k] = self.request.POST.get(k)
            else:
                obj[k] = self.request.POST.getlist(k)

        with codecs.open(self.getSessionFilename(obj.get("sid")), "w") as fd:
            self.log.debug("CREATESESSION: %s" % fd)
            fd.write(json.encode(obj))
        # fd.close()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def getSessionInformation(self, args=[]):
        obj = {}

        try:
            with codecs.open(
                self.getSessionFilename(self.request.POST.get("sid")), "r"
            ) as fd:
                obj = json.decode(fd.read())
        except Exception as e:
            self.log.exception(e)
        # else:
        # fd.close()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))

    def getSessionFilename(self, sid):
        return "%(prefix)s%(sid)s" % {"prefix": self.prefix, "sid": sid}

    def get(self, key, sid=None):
        obj = {}

        try:
            sid = sid if sid is not None else self.request.POST.get("sid")
            fd = open(self.getSessionFilename(sid), "r")
            obj = json.decode(fd.read())
        except Exception as e:
            self.log.exception(e)
        else:
            fd.close()

        return obj.get(key, None)

    def set(self, key, value, sid=None):
        try:
            sid = sid if sid is not None else self.request.POST.get("sid")
            fd = open(self.getSessionFilename(sid), "r")
            obj = json.decode(fd.read())
            fd.close()

            obj.update(**{key: value})

            fd = open(self.getSessionFilename(sid), "w")
            fd.write(json.encode(obj))
            fd.close()
        except Exception as e:
            self.log.exception(e)

    def start(self, args=[]):
        """
        Este metodo deve ser implementado
        """

    def update(self, **kargs):
        for k in list(kargs.keys()):
            self.set(k, kargs[k])

    def destroySession(self, args=[]):
        obj = {"success": True}

        def task(sid):
            time.sleep(300)
            os.unlink(self.getSessionFilename(sid))

        t = threading.Thread(
            target=task,
            args=[
                self.request.POST.get("sid"),
            ],
        )
        t.setDaemon(True)
        t.start()

        self.response["content-type"] = "text/javascript"
        self.response.write(json.encode(obj))
