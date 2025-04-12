# -*- coding: utf-8 -*-
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from common.official_journal.models import DoeLegalSign, OfficialDiary
from django.template import loader
from django.db import transaction

log = getLogger(__name__)


class JournalOfficialDiary(RestfulDRY):

    _model = OfficialDiary

    full_text_index = (
        "title__icontains",
        "published_for__icontains",
    )

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    # full_text_index = ()

    # Força o tratamento de todos os dados vindos do browser em uppercase.
    # force_upper = True

    # Em caso de delete ou update multi row força utilizar o ORM para realizar as ações.
    # force_orm_single = False

    # primary_key = 'pk'

    # Fields que não serão rastreados pelo model_to_dict e pelo get_params
    # exclude_fields = ['modified_by', 'created_by', 'created_at', 'modified_at']

    # Persistirá como False os booleans listados aqui que não estão presentes no @querydict de get_param(self, querydict, check_case).
    # Normalmente acontece com checkboxes e radiobutton não checkados no formulário
    # force_persist_boolean_fields = []

    # Persistirá como vazios os m2m listados que não vierem no request. Este é o caso de "selects" vazios comitados
    # force_persist_clear_m2m = []

    def printer(self, *args):

        try:
            pkDiary = self.request.GET.get("pk", None)
            official_diary = OfficialDiary.objects.get(pk=pkDiary)
            documents = official_diary.documents.all().order_by(
                "department_origin__general_organ__order", "department_origin__nome"
            )
            departamentos = (
                official_diary.documents.all()
                .select_related("department_origin")
                .order_by(
                    "department_origin__general_organ__order", "department_origin__nome"
                )
                .distinct(
                    "department_origin__general_organ__order", "department_origin__nome"
                )
            )
            sign = DoeLegalSign.objects.get(doe=pkDiary)
            context = {}
            lista_docs_geral = []
            lista_docs = []

            for dep in departamentos:
                context = {"nome": dep.department_origin.nome}
                lista_docs = []
                for doc in documents.filter(
                    department_origin=dep.department_origin, ativo=True
                ):
                    lista_docs.append(
                        {"titulo": doc.protocol.codigo, "conteudo": doc.content}
                    )

                context["documentos"] = lista_docs

                lista_docs_geral.append(context)

            official_diary.documentos = documents

            # log.debug('@'*80)
            # log.debug(documents)

            """
                {
                    "sumario" : [
                        { "nome": "DIRETORIA GERAL" },
                        { "nome": "COLEGIO DE PROCURADORES" },
                    ],
                    "departamentos": [
                        {
                            "nome": "DIRETORIA GERAL",
                            "documentos: [
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                            ]
                        },
                        {
                            "nome": "COLEGIO DE PROCURADORES",
                            "documentos: [
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                                { "titulo": "Titulo", "conteudo": "<html>conteudo do documento" },
                            ]
                        }
                    ]
                }
            """

            if official_diary:

                tpl = loader.get_template("official_diary/official_diary.html")
                self.response["Content-Type"] = "text/html; charset=utf-8"

                self.response.write(
                    tpl.render(
                        {
                            "diary": official_diary,
                            "documentos_geral": lista_docs_geral,
                            "doe_sign": sign.plain_content,
                        }
                    )
                )
            else:
                self.response.write("<h1>Documento não encontrado!</h1>")

        except Exception as e:
            log.exception(e)
            self.response.write("<h1>Documento não encontrado!</h1>")

    # assinar o diario sem renderizar, sera exibido ao realizar o download
    def sign_doe(self, *args):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
        }

        try:
            pkDiary = self.request.POST.get("pkset")
            official_diary = OfficialDiary.objects.get(pk=pkDiary)

            if official_diary.signed_at == None:
                official_diary.sign_doe()
            else:
                raise Exception('O diário "%s" já esta assinado.' % official_diary)

            # log.debug('@'*80)
            # log.debug(official_diary)

        except Exception as e:
            rst.update(message=str(e))
        else:
            rst.update(success=True, message="Diário assinado.")

        self.renderer(rst)

    def download_doe(self, *args):
        try:
            pkDiary = self.request.GET.get("pk", None)
            official_diary = OfficialDiary.objects.get(pk=pkDiary)
            documents = official_diary.documents.all().order_by(
                "department_origin__general_organ__order", "department_origin__nome"
            )
            departamentos = (
                official_diary.documents.all()
                .select_related("department_origin")
                .order_by(
                    "department_origin__general_organ__order", "department_origin__nome"
                )
                .distinct(
                    "department_origin__general_organ__order", "department_origin__nome"
                )
            )
            sign = DoeLegalSign.objects.get(doe=pkDiary)
            # log.debug('@'*80)
            # log.debug(sign)
            context = {}
            lista_docs_geral = []
            lista_docs = []

            for dep in departamentos:
                context = {"nome": dep.department_origin.nome}
                lista_docs = []
                for doc in documents.filter(
                    department_origin=dep.department_origin, ativo=True
                ):
                    lista_docs.append(
                        {"titulo": doc.protocol.codigo, "conteudo": doc.content}
                    )

                context["documentos"] = lista_docs

                lista_docs_geral.append(context)

            official_diary.documentos = documents

            if official_diary:

                tpl = loader.get_template("official_diary/official_diary.html")
                self.response["Content-Type"] = "text/html; charset=utf-8"

                self.response.write(
                    tpl.render(
                        {
                            "diary": official_diary,
                            "documentos_geral": lista_docs_geral,
                            "doe_sign": sign.plain_content,
                        }
                    )
                )
            else:
                self.response.write("<h1>Documento não encontrado!</h1>")

        except Exception as e:
            log.exception(e)
            self.response.write("<h1>Documento não encontrado!</h1>")

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("common.official_journal.official_diary.Manage")'
        )
