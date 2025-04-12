# -.- coding: utf-8 -.-
import base64
import hashlib
import io
import json as JSON
import os
import os.path
import re
import pickle

# import tempfile
import shutil
import socket
import uuid
from functools import partial
from io import StringIO, BytesIO
from subprocess import call
from datetime import datetime

from django import forms

# from django.template.defaultfilters import slugify
from django.conf import settings
from django.db import IntegrityError

# from pdfrw import PageMerge, PdfReader, PdfWriter  # Lib que consegue lidar com pdfs que a PyPDF2 não consegue.
from PyPDF2 import PdfReader, PdfWriter  # , merger
from PyPDF2.errors import PdfReadError

# Precisa de refatorar para substituir a PyPDF2 por pdfrw
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import Color as RLABColor

from contrib import extjs

# from rh.models import ServidorLotacao, Servidor
from contrib.controller import DefaultController

# from unicodedata import normalize
from contrib.decorator import is_public
from contrib.utils import employee_from_user, get_json_engine, getLogger
from ged import models as ged_models
from ged.exceptions import FileHashExists

try:
    from PIL import Image, ImageColor, ImageFont, ImageDraw
except ImportError:
    import Image
    import ImageColor
    import ImageFont
    import ImageDraw


json = get_json_engine()
log = getLogger(__name__)


class FileUploadController(DefaultController):

    def _create_file_by_content_base64(
        self, data, filename, mimetype="application/octalstream", access=2
    ):
        plain = base64.b64decode(data)
        file = hashlib.new("md5", plain).hexdigest()

        fileobj = None
        query = ged_models.Arquivo.objects.filter(file=file)

        if not query.exists():
            fileobj = ged_models.Arquivo(
                **{
                    "file": file,
                    "filename": filename,
                    "acesso": access,
                    "user": self.request.user,
                    "mimetype": mimetype,
                }
            )

            ged_models.Arquivo.save_file(fileobj, file, plain)
            fileobj.save()
        else:
            fileobj = ged_models.Arquivo.objects.get(file=file)

        return fileobj

    def _async_upload_start(self):
        _uuid = str(uuid.uuid4())
        tempdir = os.path.join(
            getattr(settings, "CACHE_BASE"), "ged-async-upload", _uuid
        )

        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        return _uuid

    def _async_upload_store_part(self, _uuid, _part, content):
        tempfile = os.path.join(
            getattr(settings, "CACHE_BASE"),
            "ged-async-upload",
            _uuid,
            "%s.part" % _part,
        )

        with open(tempfile, "wt") as fd:
            fd.write(content)

    def _async_upload_finish(self, _uuid, filename, mimetype, access):
        tempdir = os.path.join(
            getattr(settings, "CACHE_BASE"), "ged-async-upload", _uuid
        )

        fddst = io.StringIO()
        for part_filename in sorted(
            [f for f in os.listdir(tempdir) if f.endswith(".part")]
        ):
            partfile = os.path.join(tempdir, part_filename)
            with open(partfile, "rt") as fdsrc:
                fddst.write(fdsrc.read())
            os.unlink(partfile)

        fddst.seek(0)
        fileobj = self._create_file_by_content_base64(
            data=fddst.read(), filename=filename, mimetype=mimetype, access=access
        )
        os.rmdir(tempdir)

        return fileobj

    def async_upload(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ate o momento"}

        if len(args) == 0:
            rst = {"success": True, "uuid": self._async_upload_start()}

            self.response.status_code = 201
        else:
            _uuid = args[0]
            _part = args[1]

            body = json.decode(self.request.read())

            if body.get("method", "undefined") == "store":
                self._async_upload_store_part(_uuid, _part, body.get("content", ""))

                rst = {"success": True, "message": "escrito com sucesso"}
            elif body.get("method", "undefined") == "finish":
                now = datetime.now()
                fileobj = self._async_upload_finish(
                    _uuid=_uuid,
                    filename=f'{now.strftime("%Y%m%d%H%M%S")}_{body.get("filename")}',
                    mimetype=body.get("mimetype"),
                    access=body.get("access", 2),
                )

                rst.update(
                    success=True,
                    file=fileobj.file,
                    file_id=fileobj.pk,
                    file_filename=fileobj.filename,
                    file_unicode=str(fileobj),
                    file_permalink=fileobj.permalink(),
                    message="file save with success",
                )

        self.response["Content-Type"] = "application/json"
        self.response.write(json.encode(rst))

    def upload(self, args=[]):
        rst = {"success": False, "message": "not implemented at now"}

        try:
            body = JSON.loads(self.request.body)
            data = base64.b64decode(body.get("content"))
            file = hashlib.new("md5", data).hexdigest()

            fileobj, created = ged_models.Arquivo.objects.get_or_create(
                file=file,
                defaults={
                    "filename": body.get("name"),
                    "acesso": 2,
                    "user": self.request.user,
                    "mimetype": body.get("mimetype"),
                },
            )

            ged_models.Arquivo.save_file(fileobj, file, data)

            rst.update(
                success=True,
                file=file,
                file_id=fileobj.pk,
                file_filename=fileobj.filename,
                file_unicode=str(fileobj),
                file_permalink=fileobj.permalink(),
                message="file save with success",
            )
        except Exception as e:
            log.exception(e)
            rst.update(message=str(e))

        self.response["Content-Type"] = "application/json"
        self.response.write(JSON.dumps(rst))

    def load_private_key(self):
        return pickle.load(open(settings.PRIVATE_KEY, "r"))

    def sign(self, args=[]):
        prkey = self.load_private_key()
        fileobj = ged_models.Arquivo.objects.get(pk=int(args[0]))
        filename = fileobj.absolute_path

        buf = open(filename, "r").read()
        hash = hashlib.new("md5", buf).digest()

        obj = str(prkey.sign(hash, "")[0])

        self.response["content-type"] = "text/plain"
        self.response["content-length"] = len(obj)
        self.response["content-disposition"] = (
            "attachment; filename={0}.sign" % fileobj.filename
        )
        self.response.write(obj)

    def list_files(self, args=[]):
        obj = {"result": []}

        if "level" in self.request.POST:
            level = int(self.request.POST["level"])
            servidor = employee_from_user(self.request.user)
            slt = servidor.work_assigment.first()

            if level == 1:
                query = ged_models.Arquivo.objects.filter(
                    acesso=level, user=self.request.user
                )
            elif level == 2:
                query = ged_models.Arquivo.objects.filter(
                    acesso=level, group=slt.lotacao
                )
            elif level == 3:
                query = ged_models.Arquivo.objects.filter(acesso=level)

            if "types" in self.request.POST:
                query = query.filter(mimetype__in=dict(self.request.POST)["types"])

            for file in query:
                try:
                    filename = file.absolute_path

                    obj["result"].append(
                        {
                            "pk": file.pk,
                            "filename": file.filename,
                            "size": os.path.getsize(filename),
                            "owner": file.user.username,
                        }
                    )
                except Exception as e:
                    self.log.exception(e)

        self.response.write(json.encode(obj))

    def list_dir(self, args=[]):
        obj = []

        if int(self.request.POST["node"]) == 0:
            obj = [
                {"text": "Privado", "id": "1", "leaf": True},
                {"text": "Privado da Lotação", "id": "2", "leaf": True},
                {"text": "Público", "id": "3", "leaf": True},
            ]

        self.response.write(json.encode(obj))

    def get_hash_file(self):
        buf = b"".join([chunk for chunk in self.request.FILES["file"].chunks()])
        # print(buf)
        filename = hashlib.md5(buf).hexdigest()
        return filename, buf

    def save_file(self):
        filename, buf = self.get_hash_file()
        dir_base = ged_models.Arquivo.directory_of_hash(filename)
        fp = os.path.join(dir_base, filename)

        if not os.path.exists(dir_base):
            os.makedirs(dir_base)

        if os.path.exists(fp):
            raise FileHashExists(
                "Arquivo com hash %s já existe no sistema de arquivos" % filename
            )
        else:
            tmp_file = self.request.FILES["file"].temporary_file_path()
            shutil.copy(tmp_file, fp)

            log.info(
                "GED SAVEFILE: %s: %s: %s"
                % (
                    socket.gethostname(),
                    filename,
                    fp if os.path.exists(fp) else ">>>> ERRO <<<<",
                )
            )

        return filename

    def get_value(self, args=[]):
        try:
            file = ged_models.Arquivo.objects.get(file=self.request.POST["pk"])
            obj = {
                "value": str(file),
            }
        except Exception as ex:

            obj = {"value": "Impossível localizar arquivo no servidor."}

        self.response.write(json.encode(obj))

    def get_file_info(self, args=[]):
        try:
            file = ged_models.Arquivo.objects.get(pk=self.request.POST["pk"])
            obj = {
                "success": True,
                "file_hash": file.file,
                "file_id": file.pk,
                "file_path": str(file),
                "file_url": file.complete_permalink(),
            }
        except Exception as ex:

            obj = {
                "success": False,
                "message": "Impossível localizar arquivo no servidor.",
            }

        self.response.write(json.encode(obj))

    def get_filewrapper(self, fileobj):
        mt_wrapper = {
            "application/pdf": pdf_file_wrapper_proxy,
            "default": DefaultFileWrapper,
        }

        wrapper = mt_wrapper.get(fileobj.mimetype, DefaultFileWrapper)

        return wrapper(fileobj)

    @is_public()
    def get_image_file(self, args=[]):
        data = BytesIO()

        mimetype = "image/jpeg"
        try:
            fileobj = ged_models.Arquivo.objects.filter(
                mimetype__startswith="image"
            ).get(file=args[0])
            filename = fileobj.absolute_path
            mimetype = fileobj.mimetype

            # if fileobj.acesso == 3 and not request.user.is_authenticated:
            #     img = Image.new('RGB', [int(x) for x in args[1].split('.')], ImageColor.getrgb('#ccc'))
            #     img.save(data, 'JPEG')
            # else:
            if not os.path.exists(filename):
                raise ged_models.Arquivo.DoesNotExist("Image not found")

            im = None
            if self.request.user.is_authenticated or fileobj.acesso == 3:
                im = Image.open(filename)
                ori = "P" if im.size[0] >= im.size[1] else "L"
                size = [int(num) for num in args[1].split(".")]

                if ori != "L":
                    ratio = float(size[1]) / float(im.size[1])
                else:
                    ratio = float(size[0]) / float(im.size[0])

                new_size = (
                    int(float(im.size[0]) * ratio),
                    int(float(im.size[1]) * ratio),
                )

                im.resize(new_size, Image.LANCZOS).save(data, im.format)
        except ged_models.Arquivo.DoesNotExist:
            im = Image.new(
                "RGB", [int(x) for x in args[1].split(".")], ImageColor.getrgb("#fff")
            )
            im.save(data, "JPEG")
        finally:
            self.response["content-type"] = mimetype  # 'image/%s' % im.format.lower()

            data.seek(0)
            for chunk in iter(partial(data.read, 8192), b""):
                self.response.write(chunk)

    @is_public()
    def get_public_file(self, args=[]):

        if args:
            fileobj = ged_models.Arquivo.objects.get(file=args[0])

            if fileobj.acesso == 3:
                fdw = self.get_filewrapper(fileobj)

                self.response["content-type"] = fileobj.mimetype
                self.response["content-disposition"] = (
                    'attachment; filename="%s"' % fileobj.filename
                )

                for buf in fdw:
                    self.response.write(buf)

                fdw.clear()
            else:
                self.response["content-type"] = "text/plain"
                self.response.status_code = 403
                self.response.write("Acesso negado a este arquivo.")
        else:
            self.response.status_code = 403
            self.response["content-type"] = "text/plain"
            self.response.write("Arquivo não encontrado.")

    @is_public()
    def get_file(self, args=[]):
        fileobj = None

        try:
            fileobj = ged_models.Arquivo.objects.get(file=args[0])
        except Exception as e:
            self.log.exception(e)

            self.response.status_code = 404
            self.response["content-type"] = "text/plain"
            self.response.write("Arquivo não encontrado.")
        else:
            token = False

            if fileobj.acesso == 3:
                token = True
            elif fileobj.acesso == 2:
                try:
                    token = self.request.user.is_authenticated
                except Exception as e:
                    self.log.exception(e)
            elif fileobj.acesso == 1:
                try:
                    token = self.request.user == fileobj.user
                except Exception as e:
                    self.log.exception(e)

            if token:
                fdw = self.get_filewrapper(fileobj)
                self.response["content-type"] = fileobj.mimetype
                self.response["content-disposition"] = (
                    'attachment; filename="%s"' % fileobj.filename
                )

                for buf in fdw:
                    self.response.write(buf)
                fdw.clear()
            else:
                self.response["content-type"] = "text/plain"
                self.response.status_code = 403
                self.response.write("Acesso negado a este arquivo.")

    def load(self, args=[]):
        try:
            file = ged_models.Arquivo(
                filename=self.request.FILES["file"].name,
                mimetype=self.request.FILES["file"].content_type,
                user=self.request.user,
                acesso=int(self.request.POST["acesso"]),
            )

            try:
                if "types" in self.request.POST:
                    types = json.decode(self.request.POST["types"])
                    if file.mimetype in types:
                        file.file = self.save_file()
                        file.save()
                        obj = {
                            "success": True,
                            "msg": "Arquivo salvo com sucesso.",
                            "file_id": file.pk,
                            "file_hash": file.file,
                            "file_store": str(file),
                            "file_url": file.complete_permalink(),
                        }
                    else:
                        obj = {
                            "success": False,
                            "msg": "O arquivo enviado não é do tipo esperado.",
                        }
                else:
                    file.file = self.save_file()
                    file.save()
                    obj = {
                        "success": True,
                        "msg": "Arquivo salvo com sucesso.",
                        "file_id": file.pk,
                        "file_hash": file.file,
                        "file_store": str(file),
                        "file_url": file.complete_permalink(),
                    }
            except IntegrityError as e:
                self.log.info(">>>>>>>>>>>>>>>>>>>>>> IntegrityError")
                hash, buf = self.get_hash_file()
                files = ged_models.Arquivo.objects.filter(file=hash)
                if files.count() == 0:
                    file.file = hash
                    file.save()
                else:
                    file = files[0]
                obj = {
                    "success": True,
                    "msg": "O arquivo já existia e por isso foi carregado.",
                    "file_id": file.pk,
                    "file_hash": file.file,
                    "permalink": file.permalink(),
                    "file_url": file.complete_permalink(),
                    "file_store": str(file),
                    "details": "IntegrityError",
                }
            except FileHashExists as e:
                self.log.info(">>>>>>>>>>>>>>>>>>>>>> FileHashExists")
                hash, buf = self.get_hash_file()
                files = ged_models.Arquivo.objects.filter(file=hash)
                if files.count() == 0:
                    file.file = hash
                    file.save()
                else:
                    file = files[0]
                obj = {
                    "success": True,
                    "msg": "O arquivo já existia e por isso foi carregado.",
                    "file_id": file.pk,
                    "file_hash": file.file,
                    "permalink": file.permalink(),
                    "file_url": file.complete_permalink(),
                    "file_store": str(file),
                    "details": "FileHashExists",
                }
            except Exception as e:
                self.log.info("TRY 1")
                self.log.exception(e)
                os.unlink(file.absolute_path)
                obj = {
                    "success": False,
                    "msg": "Erro gravando os dados do arquivo enviado.",
                }
        except Exception as e:
            self.log.info("TRY 2")
            self.log.exception(e)
            obj = {
                "success": False,
                "msg": "Não foi possível gravar arquivo no disco.",
            }

        self.response.write(json.encode(obj))


class GEDArquivo(extjs.ExtCrud):

    class Form(forms.ModelForm):
        class Meta:
            exclude = []
            model = ged_models.Arquivo

    titles = {
        "PANEL": "Arquivo",
        "LIST": "Gerenciador de Arquivo",
        "NEW": "Novo(a) Arquivo",
        "EDIT": "Editando um(a) Arquivo",
        "DELETE": "Removendo um(a) Arquivo",
        "FILTER": "NOT_DEFINED_IN_CONTROLLER",
    }


class DefaultFileWrapper:

    def sign(self, fileobj):
        filename = fileobj.absolute_path

        return open(filename, "rb")

    def __init__(self, fileobj):
        self.log = getLogger(self.__class__.__name__)

        self.fd = self.sign(fileobj)
        self.fd.seek(0, 2)
        self.filesize = self.fd.tell()
        self.fd.seek(0)

    def read(self, size=1024):
        return self.fd.read(size)

    def __iter__(self):
        return iter(partial(self.read, 8192), b"")

    def __next__(self):
        return self.fd.tell() < self.filesize

    def clear(self):
        if self.fd:
            self.fd.close()
        else:
            self.log.warn("Nenhum arquivo foi aberto para este wrapper.")


# class PDFFileWrapper(DefaultFileWrapper):

#     def make_sign(self, filehash, page_size):
#         sx = 10
#         sy = 20
#         center = float(page_size[0]) / 2.0
#         width = float(page_size[0]) - 20
#         height = 10
#         dashed_hash = ' - '.join([filehash[p: p + 8] for p in range(0, 32, 8)])
#         sing_text = 'Para verificar a autenticidade, acesse o site do MPE/TO e use a chave: %s' % dashed_hash

#         data = BytesIO()
#         board = Canvas(data, pagesize=page_size)
#         board.lines([
#             ((sx + width), (sy + height), sx, (sy + height)),
#         ])

#         xcenter = (float(page_size[0]) / 2.0)

#         board.setFillColor(RLABColor(255, 255, 255, 1.0), 1.0)
#         board.rect(
#             10, sy - 5,
#             width, height + 5,
#             False,
#             True
#         )

#         board.setFillColor(RLABColor(0, 0, 0, 1.0), 1.0)
#         board.setFontSize(6)
#         board.drawCentredString(
#             xcenter,
#             sy,
#             sing_text
#         )
#         board.save()
#         data.seek(0)

#         return PdfReader(fdata=data.read()).getPage(0)

#     def sign(self, fileobj):
#         origin_filename = fileobj.absolute_path
#         filename_cache = '%s.cache' % origin_filename
#         filename = None

#         try:
#             if not os.path.exists(filename_cache):
#                 origin = PdfReader(origin_filename, decrypt=True)

#                 for page in origin.pages:
#                     page_size = page.MediaBox[2:]
#                     page_sign = self.make_sign(fileobj.file, page_size)
#                     PageMerge(page).add(page_sign).render()

#                 PdfWriter(filename_cache, trailer=origin).write()

#         except Exception as e:
#             self.log.exception(e)
#             log.exception(e)
#             filename = origin_filename
#         else:
#             filename = filename_cache

#         return open(filename, 'rb')


class PDFFileWrapperPyPDF2(DefaultFileWrapper):

    def make_sign(self, hsum, page_size):
        data = BytesIO()
        board = Canvas(data, pagesize=page_size)

        sx = 10
        sy = 20

        width = page_size[0] - 20
        height = 10

        board.lines(
            [
                ((sx + width), (sy + height), sx, (sy + height)),
            ]
        )

        xcenter = float(page_size[0]) / 2.0

        board.setFillColor(RLABColor(255, 255, 255, 1.0), 1.0)
        board.rect(10, sy - 5, page_size[0] - 20, height + 5, False, True)

        board.setFillColor(RLABColor(0, 0, 0, 1.0), 1.0)
        board.setFontSize(6)
        board.drawCentredString(
            xcenter,
            sy,
            "Para verificar a autenticidade, acesse o site do MPE/TO e use a chave: %s"
            % " - ".join([hsum[p : p + 8] for p in range(0, 32, 8)]),
        )

        board.save()
        data.seek(0)

        return PdfReader(data, strict=False).pages[0]

    def sign(self, fileobj):
        filename = fileobj.absolute_path
        filename_cache = "%s.cache" % filename
        fd = None

        try:
            if not os.path.exists(filename_cache):
                log.info("creating filecache")
                file = open(filename, "rb")
                file_data = file.read()
                buffer = BytesIO(file_data)
                origin = PdfReader(buffer, strict=False)
                dest = PdfWriter()

                if origin.is_encrypted:
                    origin.decrypt("")

                for page in origin.pages:
                    page.merge_page(self.make_sign(fileobj.file, page.mediabox[2:]))
                    page.compress_content_streams()
                    dest.add_page(page)

                with open(filename_cache, "wb") as f:
                    dest.write(f)
                log.info("filecache created")
        except PdfReadError:
            log.info("Recovery File")
            pdf_recovery(fileobj)
            fd = open(filename, "rb")
        except Exception as e:
            self.log.exception(e)
            fd = open(filename, "rb")
            log.exception(e)
            log.info("getting main file")
        else:
            log.info("getting filecache")
            fd = open(filename_cache, "rb")

        return fd


def pdf_file_wrapper_proxy(gfd):
    filebase = gfd.absolute_path
    filebase = (
        "%s.recovered" % filebase
        if os.path.exists("%s.recovered" % filebase)
        else filebase
    )

    producer = None
    try:
        pdf = PdfReader(filebase)
        producer = pdf.documentInfo.get("/Producer", "")
    except PdfReadError:
        producer = ""
        pdf_recovery(gfd)
    except Exception as e:
        log.error(f"Error reading PDF: {e}")
        producer = ""

    problematic_producers = ("cairo", "adobe")
    except_producers = ("pdfium",)

    test = re.compile(f'^({"|".join(problematic_producers)})')

    log.info(["producer", producer])
    # if isinstance(producer, str) and test.match(producer.lower()):
    #     log.info('Select legacy PDF Wapper')
    #     return PDFFileWrapper(gfd)
    # el
    if isinstance(producer, str) and producer.lower() in except_producers:
        return DefaultFileWrapper(gfd)

    return PDFFileWrapperPyPDF2(gfd)


def pdf_recovery(attached):
    src = attached.absolute_path
    dst = "%s.recovered" % src

    cmd = ["/usr/bin/pdftocairo", "-pdf", src, dst]

    log.info(" · recuperando %s para %s ... " % (src, dst))
    if not os.path.exists(dst):
        call(cmd, shell=False)
        log.info("pronto")
    else:
        log.info("ignorado")
