# -*- coding: utf-8 -*-

from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo
from edocs.protocolo.utils import EDOCBoxQuery

log = getLogger(__name__)


class EDOCMasterBoxProtocolRestful(RestfulDRY):

    _model = Protocolo

    def renderer_document(self, args=[]):

        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {"content": "Sem conteúdo", "appends": []},
        }

        try:
            protocol = self.get_query().get(pk=args[0])
            if protocol:
                rst.update(
                    success=True,
                    document={
                        "content": protocol.rendered,
                        "appends": protocol.appends_of_document,
                    },
                )
        except Protocolo.DoesNotExist:
            rst.update(message="Erro ao buscar o Protocolo.")
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def do_full_text_filter(self, query):
        """Performs full text filter using SearchVector"""
        keyword = self.request.GET.get("keyword")
        striped_keyword = keyword.strip()
        if striped_keyword != "":
            raw_search_query = EDOCBoxQuery.raw_search_query(striped_keyword)
            query = query.filter(search_vector=raw_search_query)
        return query

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("edocs.protocolo.masterbox.Manage")')
