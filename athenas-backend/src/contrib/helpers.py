# -*- coding:utf-8 -*-
import calendar
import datetime
import decimal
import hashlib
import json
import os
import pickle
import re
import shutil
import threading
import time
from decimal import Decimal
from io import StringIO
from unicodedata import normalize

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import addslashes
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

from contrib.controller import DefaultController
from contrib.utils import DateUtils, getLogger

try:
    from PIL import Image
except ImportError:
    import Image


log = getLogger(__file__)


def clean_text(text, include_chars=[]):
    base_chars = [r"\w"]

    if include_chars:
        base_chars += include_chars

    pattern = r"[^%s]+" % "\\".join(base_chars)
    replaced = re.sub(pattern, "", text)

    return replaced


class DynaObject(object):
    pass


class BaseConverter(object):
    ALPHABET = "dgLa5tuA9rFHl46RMOj3ChYUBQfbKW7Xzi8VcpxPqoNewJSGv1DEZs2mkTny0I"

    @classmethod
    def baseN_encode(cls, num, alphabet=ALPHABET):
        """Encode a number in Base X

        `num`: The number to encode
        `alphabet`: The alphabet to use for encoding
        """
        if num == 0:
            return alphabet[0]
        arr = []
        base = len(alphabet)
        while num:
            rem = num % base
            num = num // base
            arr.append(alphabet[rem])
        arr.reverse()
        return "".join(arr)

    @classmethod
    def baseN_decode(cls, string, alphabet=ALPHABET):
        """Decode a Base X encoded string into the number

        Arguments:
        - `string`: The encoded string
        - `alphabet`: The alphabet to use for encoding
        """
        base = len(alphabet)
        strlen = len(string)
        num = 0

        idx = 0
        for char in string:
            power = strlen - (idx + 1)
            num += alphabet.index(char) * (base**power)
            idx += 1

        return num


def PublicReportWrapperFacotry(ReportBuilderClass):

    from contrib.decorator import is_public

    ReportBuilder = ReportBuilderClass

    class PublicReportWrapper(DefaultController):

        PARAMS = {}

        def __init__(self, *args, **kwargs):
            super(PublicReportWrapper, self).__init__(*args, **kwargs)
            self.PARAMS.update(getattr(self.request, self.request.method, {}).copy())
            self.report_builder = ReportBuilder(self.request, self.response)
            self.report_builder.PARAMS = self.PARAMS

        @is_public()
        def create_session(self, args=[]):
            self.report_builder.create_session(args)

        @is_public()
        def run_report(self, args=[]):
            self.report_builder.run_report(args)

        @is_public()
        def get_status_session(self, args=[]):
            self.report_builder.get_status_session(args)

        @is_public()
        def download(self, args=[]):
            self.report_builder.download(args)

    return PublicReportWrapper


def get_public_attrs(obj):
    if hasattr(obj, "__dict__"):
        return dict([(k, v) for k, v in vars(obj) if not k.startswith("_")])
    return {}


def create_fixture(qs, fixtures_path, format="json", fields=[]):
    folder = os.path.dirname(fixtures_path)
    if not os.path.exists(folder):
        raise Exception(
            "Local %s para criação do arquivo de fixtures não existe." % folder
        )

    from django.core.serializers import serialize

    params = {"format": format, "queryset": qs}
    if fields:
        params["fields"] = fields
    data = serialize(format, qs)

    with open(fixtures_path, "w") as f:
        f.write(data)

    check = False
    with open(fixtures_path) as f:
        check = (
            hashlib.md5(data.encode()).hexdigest()
            == hashlib.md5(f.read().encode()).hexdigest()
        )
    return check


class WrapperSharedMemory:

    __slots = {}
    __memory_size = 1024 * 4
    __memory_allocated = 0

    class SlotNotFound(Exception):

        def __init__(self, slot):
            Exception.__init__(
                self, "Não consegui encontrar informações para o slot (%s)." % slot
            )

    class MemoryOutOfBound(Exception):

        def __init__(self):
            Exception.__init__(self, "Não há memoria suficiente para ser alocada.")

    @classmethod
    def register_slot(cls, slot, size):
        if slot not in cls.__slots:
            if size <= cls.__memory_size - cls.__memory_allocated:
                cls.__slots.update(
                    {slot: {"start": cls.__memory_allocated, "size": size}}
                )
                cls.__memory_allocated += size
            else:
                raise cls.MemoryOutOfBound()
        else:
            log.info("Slot já esta registrado!")

    @classmethod
    def has_slot(cls, slot):
        return cls.__slots.get(slot) or False

    @classmethod
    def get_slot_value(cls, slot):
        slotinfo = cls.has_slot(slot)
        if not slotinfo:
            raise cls.SlotNotFound(slot)

        return cls.read(slotinfo.get("start"), slotinfo.get("size"))

    @classmethod
    def set_slot_value(cls, slot, value):
        slotinfo = cls.has_slot(slot)
        if not slotinfo:
            raise cls.SlotNotFound(slot)

        return cls.write(value, slotinfo.get("start"), slotinfo.get("size"))


try:
    import uwsgi
except ImportError:

    class PseudoSharedMemory(WrapperSharedMemory):

        @classmethod
        def write(cls, memory, start_position=0, size=None):
            log.warn("Não posso utilizar memória compartilhada sem o uWsgi")

        @classmethod
        def read(cls, start_position, size):
            log.warn("Não posso utilizar memória compartilhada sem o uWsgi")

    SharedMemory = PseudoSharedMemory

else:

    class UWSGISharedMemory(WrapperSharedMemory):

        @classmethod
        def write(cls, memory, start_position=0, size=None):
            pos = start_position
            size = size if size is not None else len(memory)
            for x in range(0, size):
                byte = memory[x] if len(memory) > x else b"\0"
                uwsgi.sharedarea_writebyte(pos, ord(byte))
                pos += 1

        @classmethod
        def read(cls, start_position, size):
            chr_plus = lambda byte: chr(byte) if byte > 0 else ""

            byte_array = list(
                map(
                    ord,
                    [
                        uwsgi.sharedarea_read(pos)
                        for pos in range(start_position, start_position + size)
                    ],
                )
            )
            byte_array = list(map(chr_plus, byte_array))

            my_str = "".join(byte_array)
            return my_str if len(my_str) > 0 else None

    SharedMemory = UWSGISharedMemory


class Cache(object):

    def __init__(self, prefix="", path=None, timeout=172800):
        self.__prefix = prefix
        self.__path = path or settings.CACHE_PATH
        self.__timeout = timeout

    def __create_save_point(self, key):
        """cria o diretório onde serão armazenados os caches(caso não exista) e monta o nome do arquivo de cache"""
        if not os.path.exists(self.__path):
            try:
                os.mkdir(self.__path, 0o777)
            except Exception:
                raise Exception(
                    "Não foi possível criar o diretório %s. Sem permissão de escrita."
                    % self.__path
                )
        return os.path.normpath(
            "%s/%s%s"
            % (
                self.__path,
                self.__prefix + "_" if self.__prefix else "",
                hashlib.md5(str(key).encode()).hexdigest(),
            )
        )

    def touch(self, key):
        touch(self.__create_save_point(key))

    def do(self, key, data, timeout=None):
        if timeout:
            self.__timeout = timeout

        cache = self.__create_save_point(key)
        lock_cache = "%s.lock" % cache
        touch(cache)
        if not os.path.exists(lock_cache):
            pickle.dump(data, open(lock_cache, "w"))
            shutil.move(lock_cache, cache)

    def get(self, key):
        lock_cache = "%s.lock" % self.__create_save_point(key)
        if self.valid(key) and not os.path.exists(lock_cache):
            try:
                return pickle.load(open(self.__create_save_point(key)))
            except Exception:
                pass
        return False

    def valid(self, key):
        save_point = self.__create_save_point(key)
        if (
            not os.path.exists(save_point)
            or (time.time() - os.path.getmtime(save_point)) > self.__timeout
        ):
            return False
        return True

    def clear(self):
        """apaga todos os arquivos de cache com tempo de vida expirado"""
        for cache in os.listdir(self.__path):
            if (
                os.path.exists(cache)
                and (time.time() - os.path.getmtime(cache)) > self.__timeout
            ):
                os.remove(cache)

    def clear_all(self):
        """apaga todos os arquivos de cache"""
        for cache in os.listdir(self.__path):
            if os.path.exists(cache):
                os.remove(cache)

    def delete(self, key=None):
        """apaga o arquivo de cache que corresponde a key. Se omitido apaga todos caches
        com o prefixo correpondente ao passado como parâmentro no construtor"""
        if key:
            save_point = self.__create_save_point(key)
            if os.path.exists(save_point):
                os.remove(save_point)
        else:
            for cache in os.listdir(self.__path):
                cache = os.path.join(self.__path, cache)
                if self.__prefix in cache and os.path.exists(cache):
                    os.remove(cache)

    def timeout(self, timeout):
        """altera o tempo de vida do cache"""
        self.__timeout = timeout


class Resize(object):

    def __init__(self, fp, force=False):
        self.__img = Image.open(fp)
        self.__new_img = self.__img
        self.__format = self.__img.format or "jpeg"
        self.__size = self.__img.size
        self.__min_coord = (
            self.__size[0] if self.__size[0] < self.__size[1] else self.__size[1]
        )
        self.__permalink = ""
        self.__force = force

    def __save(self, filename):
        self.__new_img.save(filename, self.__format, quality=90)
        self.__filename = filename
        return filename

    def __make_filename(self, key="", make_permalink=True):
        hashname = hashlib.md5(self.__img.filename.encode()).hexdigest()
        filename = "%s/%s-%s.%s" % (
            settings.RESIZED_IMAGES_DIR,
            hashname,
            key,
            self.__format.lower(),
        )
        if make_permalink:
            self.__make_permalink(filename)
        return filename

    def __make_permalink(self, filename):
        self.__permalink = "%s/%s" % (
            settings.DOWNLOAD_IMAGES_URL,
            filename.split("/")[-1],
        )

    def permalink(self):
        return self.__permalink

    def get(self):
        return self.__new_img

    def do(self, coord):
        if "square" in coord:
            return self.by_square(coord["square"])

        elif "width" in coord:
            return self.by_width(coord["width"])

        elif "height" in coord:
            return self.by_height(coord["height"])

    def by_width(self, size, save=True):

        filename = self.__make_filename("width-%s" % size, save)

        if not os.path.exists(filename) or self.__force:

            size = int(size)
            if size < self.__size[0]:
                resize_calc = int((size * self.__size[1]) / self.__size[0])
                self.__new_img = self.__new_img.resize(
                    (size, resize_calc), Image.LANCZOS
                )
            return self.__save(filename) if save else None
        return filename

    def by_height(self, size, save=True):

        filename = self.__make_filename("height-%s" % size, save)

        if not os.path.exists(filename) or self.__force:

            size = int(size)
            if size < self.__size[1]:
                resize_calc = int((size * self.__size[0]) / self.__size[1])
                self.__new_img = self.__new_img.resize(
                    (resize_calc, size), Image.LANCZOS
                )

            return self.__save(filename) if save else None
        return filename

    def by_square(self, size):

        filename = self.__make_filename("square-%s" % size)

        if not os.path.exists(filename) or self.__force:
            log.info("cuting by square")
            size = int(size)
            if size < self.__min_coord:

                if self.__size[0] < self.__size[1]:
                    self.by_width(size, save=False)
                else:
                    self.by_height(size, save=False)

                center = (self.__new_img.size[0] / 2, self.__new_img.size[1] / 2)

                self.__resize = [0, 0, 0, 0]
                self.__resize[0] = center[0] - (size / 2)
                self.__resize[1] = center[1] - (size / 2)
                self.__resize[2] = center[0] + (size / 2)
                self.__resize[3] = center[1] + (size / 2)

                self.__new_img = self.__new_img.crop(self.__resize)

            return self.__save(filename)
        return filename


def err(message="Errors occurred in:", form=None):
    return dict(success=False, msg=message, message=message, errors=err2dict(form))


def err2html(message="Errors occurred in:", form=None):
    out = '<div class="error"><p>%s</p>' % message
    if form and len(form.errors) > 1:
        out += "<ul>"
        for k, v in list(form.errors.items()):
            out += "<li> <span> %s </span>" % (form.fields[k].label or k)
            if isinstance(v, list) and len(v) > 1:
                out += "<ul> %s </ul>" % "".join(["<li>%s</li>" % err for err in v])
            else:
                out += "".join([err for err in v])
            out += "</li>"
        out += "</ul>"
    return out + "</div>"


def err2text(message="Errors occurred in:", form=None):
    out = message + "\n"
    if form and len(form.errors) > 1:
        for k, v in list(form.errors.items()):
            out += "-%s\n" % (form.fields[k].label or k)
            for err in v:
                out += "\t-" + err + "\n"
    return out


def err2title(form):
    for k, v in list(form.errors.items()):
        attrs = form.fields[k].widget.attrs
        attrs["title"] = "%s %s" % (attrs.get("title", ""), v)
    return form


def err2dict(form):
    return [
        {"name": k, "label": form.fields[k].label, "msgs": [addslashes(i) for i in v]}
        for k, v in list(form.errors.items())
    ]


def get_controller_for_model(model):
    ct = ContentType.objects.get(
        app_label=model._meta.app_label, model=model._meta.object_name.lower()
    )
    ccts = ct.controllercontenttype_set.order_by("-priority")
    return [cct.controller for cct in ccts]


def get_default_controller_for_model(model, generic=True):
    ctls = get_controller_for_model(model)
    if len(ctls) > 0:
        return ctls[0]
    elif len(ctls) == 0 and generic is True:

        class T:
            controller = ""
            title = ""
            icon = None

        obj = T()
        obj.controller = "ExtCrudGeneric"
        obj.title = "Generico"

        return obj
    else:
        return None


def touch(filename):
    if os.path.exists(filename):
        os.utime(filename, (time.time(), time.time()))
    else:
        open(filename, "w").close()


def capitalize_words(value, aditional_preposition=[]):
    # value = value.decode('u8')
    acronyms = ["PAE", "URV", "IRRF", "RRA", "PF", "EC", "MP", "DOE"]
    prepositions = [
        "DA",
        "DE",
        "DO",
        "DOS",
        "DAS",
        "E",
        "NA",
        "NO",
        "EM",
        "PARA",
        "O(A)",
        "PELO",
        "É",
        "Á",
        "À",
    ]
    capitalized = []

    for part in value.split(" "):
        if part.upper() in prepositions:
            capitalized.append(part.lower())
        elif part in acronyms:
            capitalized.append(part)
        else:
            capitalized.append(part.capitalize())

    return " ".join(capitalized)


def clear_to_ascii(text):
    if isinstance(text, str) is False:
        text = str(text)
    return (
        normalize("NFKD", text)
        .encode("ascii", "ignore")
        .replace(b"`", b"")
        .replace(b"'", b"")
        .decode()
    )


class StackThread:
    """
    Como usar:

    def foo(result, ...):
        ...
        result.append(...)

    def generator():
        ...
        yield foo, [...]

    stack = StackThread(size, generator)
    stack.start()

    print stack.results
    """

    def __init__(self, size, factory, wait=0.05, **kargs):
        self.size = size
        self.factory = factory
        self.stack = []
        self.dei = True
        self.wait = wait
        self.results = []
        self.kargs = kargs

    def is_empty(self):
        self._gb()
        return len(self.stack) == 0

    def _gb(self):
        for t in self.stack:
            if t.is_alive() is False:
                self.stack.remove(t)

    def is_full(self):
        if len(self.stack) < self.size:
            return False
        else:
            self._gb()
            return len(self.stack) >= self.size

    def is_dei(self):
        return self.dei

    def do_wait(self, wait=None):
        time.sleep(wait if wait else self.wait)

    def start(self):
        counter = 0
        self.dei = False

        for target, args in self.factory(**self.kargs):
            args.insert(0, self.results)
            counter += 1
            t = threading.Thread(target=target, args=args, name="task_%d" % counter)
            t.start()
            self.stack.append(t)

            while self.is_full():
                time.sleep(self.wait)

        while self.is_empty() is False:
            self._gb()
            time.sleep(self.wait)

        self.dei = True


class DateCalendar:

    @classmethod
    def get_month_limit(cls, year, month):
        week_day, end_day = calendar.monthrange(year, month)
        start_day = 1
        return datetime.date(year, month, start_day), datetime.date(
            year, month, end_day
        )


def copy_file(src, dst, buffer_size=4096):
    fd_src = open(src, "r")
    fd_dst = open(dst, "w")

    log.info("copiando arquivo...")
    while True:
        copy_buffer = fd_src.read(buffer_size)
        log.info(". %d bytes" % len(copy_buffer))
        if copy_buffer:
            fd_dst.write(copy_buffer)
        else:
            print("done")
            break

    fd_src.close()
    fd_dst.close()


def json_serializer(obj):
    v = ""
    if isinstance(obj, datetime.datetime):
        v = DateUtils.datetime_to_str(obj)
    elif isinstance(obj, datetime.date):
        v = DateUtils.date_to_str(obj)
    elif isinstance(obj, datetime.time):
        v = obj.strftime("H:M:S")
    elif isinstance(obj, decimal.Decimal):
        v = float(obj)
    return v


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        return json_serializer(obj)


def get_cross_domain_response(self, result):
    """Método para configurar respostas cross domain conforme definido pelo cliente.

    :param result: Estrutura de dados a ser serializada.
    :type result: Object

    :returns:  Object -- Objeto ou nome de função de Callback.
    """
    out = json.dumps(result, ensure_ascii=False, default=json_serializer)
    # Verifica a necessidade de configuracao
    if "callback" in getattr(self.request, self.request.method, {}):
        out = "%s(%s)" % (
            getattr(self.request, self.request.method, {}).get("callback"),
            out,
        )
    return out


def make_pagination(max_registers, page_number, values, result):
    """Método para paginar resultados de QuerySets.

    :param max_registers: Número máximo de registros por página.
    :type max_registers: Integer

    :param page_number: Número da página atual.
    :type page_number: Integer

    :param values: QuerySet a ser paginado.
    :type values: QuerySet

    :param result: Estrutura de dados que irá conter detalhes sobre a paginação.
    :type result: Object

    :returns:  QuerySet -- QuerySet paginado.
    """

    # Executa paginacao de resultados de consultas
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

    paginator = Paginator(values, max_registers)
    try:
        response = paginator.page(page_number)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    # Informa detalhes sobre a paginacao
    page_details = {
        "total": response.paginator.count,
        "num_pages": response.paginator.num_pages,
        "number": response.number,
        "start_index": response.start_index(),
        "end_index": response.end_index(),
        "has_previous": response.has_previous(),
        "has_next": response.has_next(),
    }
    result.update(page=page_details)

    return response


def index_of(d, value):
    """
    d = dict or choice tuple
    value = value to search
    """
    try:
        dict_ = dict(d)
    except TypeError:
        print("Type %s incopatible" % d.__class__.__name__)
    except Exception as e:
        print(e)
    else:
        for k, v in dict_.items():
            if v == value:
                return k

    return None


def clear_bug_fix_ext_editor(self):
    """Método para retirar tag <br> e o comentário de correção de bug da ExtJS adicionado pelo editor de texto.
    @self = texto a ser aplicado o filtro
    """
    text = re.sub(r"\<\!\-|-.+\-\-\>", "", self)
    text = text.replace("<br>", "")
    return text


def get_controller_class_for_model(Model):
    controller = get_default_controller_for_model(Model)
    print(controller.controller)

    py_tpl = """
try:
    from %s import %s as Controller
except:
    Controller = None
    """

    for repo in getattr(settings, "ROUTER", {}).get("controllers", []):
        exec(py_tpl % (repo, controller.controller))
        if Controller is not None:
            return Controller
        else:
            continue

    return None


def roundf(v, p=2):
    return float(Decimal(str(v)).quantize(Decimal(str(pow(10, -p)))))


def roundfb(v, decimals=2):
    multi = pow(10, decimals)
    return int(v * multi) / float(multi)


def roundrfb(v, multi=100):
    return int(v * multi) / float(multi)


def pdf_extract_text(fname, pages=None):
    """converts pdf, returns its text content as a string"""
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(fname, "rb")
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text
