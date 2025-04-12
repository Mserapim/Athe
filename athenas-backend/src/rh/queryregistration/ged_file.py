import os
from django.conf import settings
from contrib.middleware import get_current_user


class GedFile(object):
    """
    Classe responsável por salvar os arquivos no storage
    """

    def __init__(self, file, identifier):
        self.file = file
        self.identifier = identifier

    @staticmethod
    def directory_of_hash(identifier):
        return os.path.join(
            getattr(settings, "UPLOAD_STORE_DIR", ""),
            identifier,
            get_current_user().username,
        )

    @property
    def absolute_directory(self):
        return GedFile.directory_of_hash(self.identifier)

    @property
    def absolute_path(self):
        if not os.path.exists(self.absolute_directory):
            os.makedirs(self.absolute_directory)
        return os.path.join(self.absolute_directory, self.file)

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
