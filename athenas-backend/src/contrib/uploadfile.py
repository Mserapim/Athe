from contrib.utils import get_json_engine, getLogger
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from ged import models as ged_models
from ged.models import Arquivo
import base64
import hashlib
import mimetypes


log = getLogger(__name__)
json = get_json_engine()


class UploadFile:

    max_size = 5 * 1024 * 1024  # 5MB max size

    @classmethod
    def upload(cls, data, filename, user, access=2):
        if not filename:
            mimetype = "application/octalstream"
            filename = "arquivo"
        mimetype = mimetypes.guess_type(filename)[0]
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
                    "user": user,
                    "mimetype": mimetype,
                }
            )

            ged_models.Arquivo.save_file(fileobj, file, plain)
            fileobj.save()
        else:
            fileobj = ged_models.Arquivo.objects.get(file=file)

        return fileobj

    @classmethod
    def upload_steam(cls, data, filename, user, access=2):
        if not filename:
            mimetype = "application/octalstream"
            filename = "arquivo"
        mimetype = mimetypes.guess_type(filename)[0]
        plain = data
        file = hashlib.new("md5", plain).hexdigest()

        fileobj = None
        query = ged_models.Arquivo.objects.filter(file=file)

        if not query.exists():
            fileobj = ged_models.Arquivo(
                **{
                    "file": file,
                    "filename": filename,
                    "acesso": access,
                    "user": user,
                    "mimetype": mimetype,
                }
            )

            ged_models.Arquivo.save_file(fileobj, file, plain)
            fileobj.save()
        else:
            fileobj = ged_models.Arquivo.objects.get(file=file)

        return fileobj

    @classmethod
    def create_file(cls, file_obj, filename, user):
        file = None
        try:
            file_base64 = base64.b64encode(file_obj.read()).decode("utf-8")
            if file_base64:
                validators = [MaxSizeFileValidator(cls.max_size)]
                for validator in validators:
                    validator(file_base64)
                file = cls.upload(file_base64, filename, user)
        except Exception as err:
            log.error(err)
        return file

    @classmethod
    def get_file(cls, file_id):
        file = None
        try:
            file = Arquivo.objects.get(pk=file_id)
        except Exception as err:
            log.error(err)
        return file


class MaxSizeFileValidator(BaseValidator):
    message = (
        "O arquivo é maior do que o tamanho máximo permitido de %(max_size)s bytes."
    )
    code = "max_size"

    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        content = base64.b64decode(value)
        if len(content) > self.max_size:
            raise ValidationError(
                self.message, params={"max_size": self.max_size}, code=self.code
            )
