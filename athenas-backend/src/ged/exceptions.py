class GEDError(Exception):
    """Classe base para as exceptions do GED."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FileHashExists(GEDError):
    pass
