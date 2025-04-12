import json
from datetime import datetime

from django.contrib.auth.models import Permission
from django.db import transaction
from django.http import HttpResponseNotAllowed

from common.document_access.models import (
    AllowedListItem,
    Control,
    ControlType,
    DocumentType,
    LegalPrerogative,
    Log,
    ProtocolControl,
)
from contrib.middleware import get_current_user
from contrib.newrest import RestfulDRY
from contrib.nil import nil_unicode
from contrib.utils import DateUtils, getLogger, person_from_user


log = getLogger(__name__)


class DAControl(RestfulDRY):

    _model = Control

    # Tupla com atributos de Model e seus respectivos argumentos de pesquisa utilizados para indexar as buscas.
    full_text_index = (
        "document_number__icontains",
        "document_type__title__icontains",
        "control_type__title__icontains",
        "source__nome__icontains",
        "source__sigla__icontains",
    )

    def get_query(self):
        return self.Model.objects.filter(is_committed=True)

    def model_to_dict(self, instance):
        dict_ = super(DAControl, self).model_to_dict(instance)

        dict_.update(
            is_secret=instance.is_secret,
            control_type_title=instance.control_type_title,
            last_movement_date=DateUtils.datetime_to_str(instance.last_movement_date),
        )

        return dict_

    def document_renderer(self, *args):
        result = {
            "success": False,
            "message": "Nothing done yet.",
            "detail": "Sem informações.",
            "content": "Sem informações.",
            "extra_pages": [],
        }

        try:
            control = self._model.objects.get(pk=self.request.REQUEST.get("pk"))
            result.update(
                success=True,
                message="Documento renderizado com sucesso.",
                detail=control.rendered,
                content=control.my_origin.rendered_content,
                extra_pages=control.my_origin.appends_of_document,
            )
        except self._model.DoesNotExist:
            result.update(message="Documento não encontrado.")
        except Exception as e:
            result.update(message=str(e))

        self.renderer(result)

    def classify(self, *args):
        pass

    def declassify(self, *args):
        response = {"success": False, "message": "Ainda não foi realizado nada."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                params = self.request.PUT.dict()

                if not params.get("justification"):
                    raise Exception(
                        "Não posso desclassificar uma informação sem uma Justificativa."
                    )

                excluded = ["pk_set", "action"]
                for i in excluded:
                    params.pop(i)

                for control in self._model.objects.filter(
                    pk__in=self.request.PUT.getlist("pk_set")
                ):
                    control.declassify(**params)
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def validate_control_params(self, params):
        if not params.get("control_type"):
            raise Exception(
                "Não posso classificar uma informação sem um Nível de Acesso."
            )

        if not params.get("legal_prerogative"):
            raise Exception(
                "Não posso classificar uma informação sem uma Hipótese Legal."
            )

        if not params.get("justification"):
            raise Exception(
                "Não posso classificar uma informação sem uma Justificativa."
            )

    def reclassify(self, *args):
        response = {"success": False, "message": "Ainda não foi realizado nada."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                params = self.request.PUT.dict()
                self.validate_control_params(params)
                params.update(
                    {
                        "control_type": ControlType.objects.get(
                            pk=params.get("control_type")
                        )
                    }
                )
                params.update(
                    {
                        "legal_prerogative": LegalPrerogative.objects.get(
                            pk=params.get("legal_prerogative")
                        )
                    }
                )

                excluded = ["pk_set", "action"]
                for i in excluded:
                    params.pop(i)

                for control in self._model.objects.filter(
                    pk__in=self.request.PUT.getlist("pk_set")
                ):
                    control.reclassify(**params)
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def deadline_change(self, *args):
        response = {"success": False, "message": "Ainda não foi realizado nada."}

        try:
            self._read_special_verb()
            with transaction.atomic():
                params = self.request.PUT.dict()
                params.update(
                    final_term=DateUtils.str_to_datetime(params.get("final_term"))
                )
                excluded = ["pk_set", "action"]
                for i in excluded:
                    params.pop(i)

                for control in self._model.objects.filter(
                    pk__in=self.request.PUT.getlist("pk_set")
                ):
                    control.deadline_change(**params)
        except Exception as e:
            log.exception(e)
            response.update(message=str(e))
        else:
            response.update(success=True, message="Ação realizada com sucesso.")

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("common.document_access.control.Manage")')


class DAProtocolControl(DAControl):

    _model = ProtocolControl


class DAControlView(DAControl):
    """Classe que retorna os documentos para o site

    Esta classe tem por objetivo implementar métodos de retorno dos documentos classificados e desclassificados ao site.
    """

    def get_classify_document(self, args=[]):
        """Método de retorno de documentos

        Este método retorna os documentos classificados ou desclassificados.
        """
        response = {"count": 0}

        if self.request.method != "GET":
            self.response = HttpResponseNotAllowed(
                ["GET"], reason="Method not allowed. Only allowed method is GET."
            )
            self.response.write("Operação não permitida")
        else:
            try:
                classify_flag = (
                    True if self.request.GET.get("classify_flag") == "True" else None
                )

                query = (
                    self._model.objects.select_related(
                        "control_type", "document_type", "source"
                    )
                    .filter(is_committed=True, control_type=classify_flag)
                    .order_by("year", "month", "production_date__day")
                )

                if "filter" in self.request.GET:
                    query = self.do_filter(query)

                response.update(count=query.count())
                query = self.do_page(query)

            except Exception as e:
                log.debug(e)
            else:
                response.update(
                    classify_documents=[
                        {
                            "document_number": document.document_number,
                            "document_type": document.document_type.title,
                            "source": document.source.nome,
                            "subject": document.subject,
                            "document_date": str(
                                document.production_date.strftime("%d/%m/%Y %H:%M")
                            ),
                            "last_move_date": str(
                                document.last_movement_date.strftime("%d/%m/%Y %H:%M")
                            ),
                            "is_confidential": "Sim" if classify_flag else "Não",
                            "control_type_title": document.control_type_title,
                        }
                        for document in query
                    ]
                )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(response))

    def get_document_years(self, args=[]):
        """Método de retorno dos anos dos documentos

        Este método retorna os anos dos documentos classificados e desclassificados em ordem decrescente
        """

        classify_flag = (
            True if self.request.GET.get("classify_flag") == "True" else None
        )

        years = sorted(
            list(
                self._model.objects.filter(
                    is_committed=True, control_type=classify_flag
                )
                .values_list("year", flat=True)
                .distinct()
            ),
            reverse=True,
        )

        self.response["content-type"] = "text/javascript"
        self.response.write(json.dumps(years))
