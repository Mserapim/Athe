from contrib.controller import JsonResponseController
from contrib.decorator import is_public
from contrib.utils import getLogger, person_from_user
from ged.models import Arquivo

log = getLogger(__name__)


def is_file_public(_file):
    for attach in _file.anexo_set.all():
        for m in attach.movimentacao.all():
            if m.protocolo.sigiloso:
                return False
    return True


class DocsVerifyRPC(JsonResponseController):

    @is_public()
    def verify(self, args=[]):
        response_data = {"success": False, "message": "Nenhum documento encontrado."}

        if self.request.POST:
            filehash = self.request.POST.get("filehash") or 0
            _file = Arquivo.objects.filter(file=filehash.lower(), acesso=3)
            if _file:
                file_data = {
                    "creator": person_from_user(_file[0].user).nome,
                    "created": _file[0].created,
                    "url": _file[0].permalink(),
                    "filename": _file[0].filename,
                    "is_public": is_file_public(_file[0]),
                }

                response_data = {
                    "success": True,
                    "message": "Documento encontrado.",
                    "file_data": file_data,
                }

        self.render(response_data)
