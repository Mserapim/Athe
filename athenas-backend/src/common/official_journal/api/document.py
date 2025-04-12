# -*- coding: utf-8 -*-
from dataclasses import fields
from email import contentmanager
import json
from logging import debug
from pydoc import doc

from django.db.models.query_utils import Q
from common.official_journal.models import Devolution, Document, OfficialDiary
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.utils import employee_from_user, getLogger, person_from_user
from edocs.protocolo.models import (
    LegalSign,
    Movimentacao,
    ProtocolLegalSign,
    Protocolo,
    TipoDocumento,
)
from judicial.models import PartLawsuit
from web.media_indoor.models import Content
from django.db.models import Max
from django.core import serializers


log = getLogger(__name__)


class JournalDocument(RestfulDRY):

    _model = Document

    full_text_index = (
        "content__icontains",
        "department_origin__abreviacao__icontains",
        "protocol__cache_rendered__icontains",
        "protocol__codigo__icontains",
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

    def renderer_document(self, *args):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            document = Document.objects.get(
                pk=self.request.POST.get("idDocument", None)
            )
            if document:
                rst.update(
                    success=True,
                    message="Documento carregado com sucesso",
                    content=document.content,
                )
        except Document.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

        # log.debug('@'*80)
        # log.debug(self.request.POST)

    def save_info_edoc(self, args=[]):  # e-doc para o diário oficial
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:

            pkProtocol = self.request.POST.get("pk", None)
            document = Document.objects.filter(protocol=pkProtocol).first()
            if not document is None:
                raise Exception(
                    "Não foi possivel realizar a movimentação pois o documento já foi enviado ao diário."
                )

            protocolo = Protocolo.objects.get(pk=pkProtocol)

            if not protocolo.resumo:
                rst.update(success=False, message="Este documento não possui conteúdo.")
            else:
                documento = Document()

                documento.department_origin = protocolo.orgao_geral_origem
                documento.protocol = protocolo
                # documento.content = protocolo.resumo
                documento.content = protocolo.rendered

                documento.save()

                rst.update(
                    success=True,
                    message="Documento enviado ao diário com sucesso!",
                )

        except Document.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def save_info_eext(self, args=[]):  # eext para diário oficial
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:

            pkPartLawsuit = self.request.POST.get("pk", None)
            partLawsuit = PartLawsuit.objects.get(pk=pkPartLawsuit)

            document = Document.objects.filter(
                protocol=partLawsuit.lawsuit.origin, content=partLawsuit.cache_rendered
            ).first()
            if not document is None:
                raise Exception(
                    "Não foi possivel realizar a movimentação pois o documento já foi enviado ao diário."
                )

            if not partLawsuit.cache_rendered:
                rst.update(success=False, message="Este documento não possui conteúdo.")
            else:
                documento = Document()

                documento.department_origin = partLawsuit.create_location
                documento.protocol = partLawsuit.lawsuit.origin
                documento.content = partLawsuit.cache_rendered
                # salvar a assinatura

                documento.save()

                rst.update(
                    success=True,
                    message="Documento enviado ao diário com sucesso!",
                )

        except Document.DoesNotExist:
            rst.update(
                message="Não consegui encontrar o documento desejado. Verifique condições de acesso."
            )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

    def save_info_diary(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}
        try:
            pkDocuments = self.request.POST.get("pk", None).split(",")
            pkDiary = self.request.POST.get("official_diary", None)

            diary = OfficialDiary.objects.get(pk=pkDiary)

            for pkdoc in pkDocuments:
                document = Document.objects.get(pk=pkdoc)
                document.official_diary = diary

                document.save()

            rst.update(
                success=True,
                message="Documento enviado ao diário com sucesso!",
            )
        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

        # log.debug('@'*80)
        # log.debug(rst)

    def save_devolution(self, *args):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            pkDocument = self.request.POST.get("document", None)
            devolution = self.request.POST.get("devolution", None)

            # document = Document.objects.get(pk=pkDocument)
            document = Document.objects.select_related("department_origin").get(
                pk=pkDocument
            )

            document.ativo = False if document.ativo else True

            protocol = Protocolo.docketing(
                subject=document.protocol.assunto,
                document_type=TipoDocumento.objects.get(pk=51),
                interested=person_from_user(get_current_user()),
                home_court=document.department_origin,
                content="".join(devolution),
            )
            current = Movimentacao.inbox_queryset().get(protocolo=protocol)

            current.do_send(
                location_destination=document.department_origin.pk,
                employee_origin=employee_from_user(get_current_user()),
                advice=document.content,
                physical=False,
                opinion=True,
            )

            document.save()

            rst.update(
                success=True,
                message="Movimentação alterada com sucesso!",
            )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

        # log.debug('@'*80)
        # log.debug(document)

    def get_query(self):
        """Esta propriedade retorna os documentos com a cláusula principal:
        - Os documentos que constam com ativo = true
        - Ou seja, status de ativo e aguardando serão retornados."""
        return Document.objects.filter(ativo=True)

    def connect_diary(self, *args):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        # buscar diario mais recente que tenha data nula
        # buscar no diario oficial (published_date nula e tiver > (max)data de criação ou > pk)
        # Objeto da consulta
        # pegar o obj da consulta e atualizar no obj documento
        # salvar

        try:
            pkDocument = self.request.POST.get("pk", None)
            document = Document.objects.get(pk=pkDocument)

            # selecionado o que tem a maior 'create_date', o aggregate (adiciona uma clausula na consulta), [pegando o valor da propriedade expecifica do objeto ]
            max_create_date = OfficialDiary.objects.aggregate(Max("create_date"))[
                "create_date__max"
            ]
            # consulta: adiciona o 'max_create_date' como uma clausula do filtro do primeiro registro.
            official_diary = OfficialDiary.objects.filter(
                published_date=None, create_date=max_create_date
            ).first()

            if official_diary is None:
                rst.update(
                    success=False,
                    message="Não foi possível associar porque o diário atual já foi publicado",
                )
            else:
                document.official_diary = official_diary

                document.save()

                # data = serializers.serialize('json', [document], fields=('official_diary', 'department_origin',
                #                                                        'protocol', 'content', 'send_date', 'ativo'))

                rst.update(
                    success=True,
                    message="Diário associado com sucesso!",
                    data={
                        "official_diary": {"title": official_diary.title},
                        "ativo": document.ativo,
                    },
                )

        except Exception as e:
            rst.update(message=str(e))

        self.renderer(rst)

        # log.debug('@'*80)
        # log.debug(official_diary)

    def get_info_devolution(self, *args):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        # Fluxo

        # Ao clicar em devolver e realizar o load deve ser chamada esta função
        # Pegar a pk do documento
        # Buscar o documento registrado
        # Pegar o pk de cada campo que consta nos relacionamentos do documento
        # Buscar os pks os relacionando
        # Devolver para variavel de retorno rst
        # No ajax retirar o load
        # Na tela de exibição da devolução
        # Pegar a variavel que retorna o destinatário do documento
        try:
            pkDocument = self.request.POST.get("pk", None)
            # relacionamento de chaves estrangeiras, selecionando dados adicionais de objetos relacionados ao executar a consulta.
            document = Document.objects.select_related(
                "protocol__servidor_origem__pessoa_fisica"
            ).get(pk=pkDocument)

            rst.update(
                success=True,
                message="Teste",
                data={
                    "destinatario": str(document.protocol.servidor_origem.pessoa_fisica)
                },
            )

        except Exception as e:
            rst.update(message=str(e))
        self.renderer(rst)

    def model_to_dict(self, instance):
        recurso = super().model_to_dict(instance)
        recurso.update(status_unicode=instance.status_icons())

        return recurso

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.official_journal.document.Manage")')
