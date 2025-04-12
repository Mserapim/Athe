# -.- coding: utf-8 -.-

import os
import hashlib
import shutil
from io import FileIO
from django.db import models
from django.contrib.auth.models import User
from contrib.decorator import to_search
from django.conf import settings
from django.core.files import File
from contrib.utils import getLogger
from contrib.middleware import get_current_user

CONTEXT = getattr(settings, "CONTEXT", None)

log = getLogger(__name__)


class FileManager(models.Manager):

    def get_by_natural_key(self, hashfile):
        return self.get(file=hashfile)


@to_search(
    [
        {"name": "filename", "type": "text"},
        {"name": "user__servidor__pessoa_fisica__nome", "type": "text"},
        {"name": "user__servidor__lotacoes__nome", "type": "text"},
    ]
)
class Arquivo(models.Model):

    objects = FileManager()

    OWNER, GROUP, PUBLIC = range(1, 4)

    filename = models.CharField(max_length=260, null=True, blank=True)
    mimetype = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    file = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    group = models.ForeignKey(
        "rh.Lotacao", null=True, blank=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    acesso = models.PositiveIntegerField(
        choices=((OWNER, "PRIVADO"), (GROUP, "PRIVADO AO GRUPO"), (PUBLIC, "PÚBLICO")),
        default=PUBLIC,
    )
    copia_de = models.ForeignKey(
        "Arquivo", blank=True, null=True, on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    # rel_dir = models.CharField(max_length=260, )

    # class Meta:
    #     unique_together = ("file")

    @property
    def is_queued(self):
        return os.path.exists("%s.queue" % self.absolute_path)

    @property
    def is_cached(self):
        return os.path.exists("%s.cache" % self.absolute_path)

    @property
    def need_cache(self):
        return self.mimetype == "application/pdf" and (
            not self.is_queued or not self.is_cached
        )

    def create_cache(self):
        from ged.task import sign_pdf_validation

        open("%s.queue" % self.absolute_path, "wt")
        sign_pdf_validation.delay(self.pk)

    def save(self, ignore_cache=False, *args, **kwags):
        super(Arquivo, self).save(*args, **kwags)
        if self.need_cache and not ignore_cache:
            self.create_cache()

    def __str__(self):
        return "{0}/{1}".format(self.user.username, self.filename)

    def natural_key(self):
        return (self.file,)

    def resizelink(self, wh):
        return "/{0}/{1}/{2}/{3}/{4}.{5}/".format(
            getattr(settings, "CONTEXT", "undefined.context"),  # 0
            "FileUploadController",  # 1
            "get_image_file",  # 2
            self.file,  # 3
            wh[0],  # 4
            wh[1],  # 5
        )

    def verify_code(self):
        return " - ".join([self.file[i : i + 8] for i in range(0, 32, 8)])

    def complete_permalink(self):
        return "%(schema)s://%(domain)s%(uri)s" % {
            "schema": getattr(settings, "HTTP_PROTOCOL", "http"),
            "domain": getattr(settings, "DOMAIN", "unknow.domain"),
            "uri": self.permalink(),
        }

    def permalink(self):
        context = getattr(settings, "CONTEXT", "undefined.context")

        context = context if not context.startswith("/") else context[1:]

        return "/".join(
            ["", context, "FileUploadController", "get_file", self.file, ""]
        )

    def no_logged_permalink(self):
        """
        Permalink para documentos publicos sem necesidade de login.
        """
        return self.complete_permalink().replace("get_file", "get_public_file")

    @staticmethod
    def directory_of_hash(hashdata):
        return os.path.join(
            getattr(settings, "UPLOAD_STORE_DIR", ""),
            hashdata[0:2],
            hashdata[2:4],
            hashdata[4:6],
        )

    @property
    def absolute_directory(self):
        return Arquivo.directory_of_hash(self.file)

    @property
    def absolute_path(self):
        return os.path.join(self.absolute_directory, self.file)

    @property
    def older_absolute_path(self):
        return os.path.join(getattr(settings, "UPLOAD_STORE_DIR", ""), self.file)

    @classmethod
    def from_filepath(cls, path, user, mimetype, acesso=3, ignore_cache=False):
        log.debug("PATH: %s USER: %s MIME: %s" % (path, user, mimetype))
        if os.path.isfile(path):
            ahash = cls.hash_file(path, hashlib.md5())
            if cls.objects.filter(file=ahash).exists():
                file_ged = cls.objects.get(file=ahash)
                if file_ged.user != user:
                    file_ged.user = user
                    file_ged.save(ignore_cache)
            else:
                dst_dir = cls.directory_of_hash(ahash)
                dst_file = os.path.join(dst_dir, ahash)

                if not os.path.exists(dst_dir):
                    log.debug('Criando diretório "%s"', dst_dir)
                    os.makedirs(dst_dir)

                log.debug('Movendo o arquivo "%s" para "%s"', path, dst_file)
                shutil.move(path, dst_file)
                file_ged = cls(
                    filename=os.path.basename(path),
                    file=ahash,
                    user=user,
                    mimetype=mimetype,
                    acesso=acesso,
                )
                file_ged.save(ignore_cache)
                log.debug("Criado no GED o arquivo %s", file_ged)

            return file_ged

    @classmethod
    def hash_buffer(klass, buf):
        return hashlib.md5(buf).hexdigest()

    @classmethod
    def hash_file(cls, path, hasher, blocksize=65536):
        if os.path.isfile(path):
            for chunk in File(FileIO(path)).chunks():
                hasher.update(chunk)
            return hasher.hexdigest()
        return None

    @classmethod
    def create_from_file(cls, filepath, user=False):
        obj = None

        with open(filepath, "rb") as fd:
            obj = cls.create_from_stream(fd, user)

        return obj

    @classmethod
    def create_from_stream(cls, stream, user=False):
        return cls.create_ged(stream, user)

    @classmethod
    def create_ged(cls, upfile, user=False):
        buffer = b""
        for chunk in iter(lambda: upfile.read(8192), b""):
            buffer += chunk

        hashfilename = hashlib.md5(buffer).hexdigest()
        instance = None

        if not cls.objects.filter(file=hashfilename).exists():
            instance = cls(
                **{
                    "file": hashfilename,
                    "filename": upfile.name,
                    "mimetype": upfile.content_type,
                    "file": hashfilename,
                    "user": (user or get_current_user()),
                }
            )

            cls.save_file(instance, hashfilename, buffer)
            instance.save()
        else:
            instance = cls.objects.get(file=hashfilename)

        return instance

    @classmethod
    def save_file(cls, instance, hashfilename, buf):
        filepath = instance.absolute_path
        directory_path = instance.absolute_directory

        cls._save_file(filepath, directory_path, hashfilename, buf)

    @classmethod
    def _save_file(cls, filepath, directory_path, hashfilename, buf):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        if not os.path.exists(filepath):
            with open(filepath, "wb") as f:
                f.write(buf)
