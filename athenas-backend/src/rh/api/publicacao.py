# -*- coding: utf-8 -*-

import collections
import re

from django.template.defaultfilters import striptags
from contrib.helpers import capitalize_words
from contrib.newrest import RestfulDRY
from django.db.models import Count, Q

# from standard.views import AutoCompleteField
# from django import forms
from contrib.utils import DateUtils, get_json_engine, getLogger
from rh.models import Publicacao
from standard.models import Choice

json = get_json_engine()
log = getLogger(__name__)


class RHPublicacaoRestful(RestfulDRY):

    _model = Publicacao

    force_persist_boolean_fields = ["interno", "lei_autorizativa"]

    force_upper = False

    full_text_index = ("cache_unicode__icontains", "interessado_nome__icontains")

    def confirm_publication(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            publication = self.get_query().get(pk=args[0])
            publication.confirm_publication(
                publication_number=self.request.POST.get("numero_publicacao"),
                publication_date=DateUtils.str_to_date(
                    self.request.POST.get("data_publicacao")
                ),
                page=int(self.request.POST.get("vehicle_page") or 0),
            )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True)

        self.renderer(rst)

    def sent_to_publication(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            publication = self.get_query().get(pk=args[0])
            publication.sent_to_publication(
                int(self.request.POST.get("veiculo_publicacao") or 0)
            )
        except Exception as e:
            rst.update(message="{}".format(e.args[0]))
        else:
            rst.update(success=True)

        self.renderer(rst)

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.publicacao.Manage')")

    def model_to_dict(self, inst, *args, **kwargs):
        rst = super(RHPublicacaoRestful, self).model_to_dict(inst, *args, **kwargs)

        rst.update(icons=inst.icons, formated_content=inst.formated_content)

        return rst


class RHPublicationGeneral(RHPublicacaoRestful):

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write("Ext._create('rh.publicacao.PublicationGeneralManage')")


class RHOfficialDocsAPI(RHPublicacaoRestful):

    def fetch_years(self, args=[]):
        rst = {"success": False, "message": "Nada foi feito ainda."}

        try:
            years = (
                self._model.objects.filter(
                    interno=True, arquivo__isnull=False, tipo__in=(1, 3, 5)
                )
                .order_by("-ano")
                .values_list("ano", flat=True)
                .annotate(total=Count("ano"))
            )
        except Exception as e:
            rst.update(message="Não foi possícel encontrar os anos dos documentos")
        else:
            rst.update(
                message="Processado com sucesso!",
                count=years.count(),
                collection=list(years),
            )

            self.renderer(rst)

    def get_query(self):
        query = super().get_query()

        ATOS = 1
        PORTARIAS = 3
        DESPACHOS = 5

        query = query.filter(
            Q(interno=True)
            & Q(arquivo__isnull=False)
            & Q(tipo__in=[ATOS, PORTARIAS, DESPACHOS])
        ).order_by("-ano", "-numero")

        return query

    def model_to_dict(self, instance):
        _dict_ = super().model_to_dict(instance)

        DOCS = Choice.get_dict_choices_for("rh", "TIPO_DOCUMENTO")

        if instance.data_publicacao:
            if instance.get_veiculo_publicacao_display() and instance.numero_publicacao:
                info = (
                    f"PUBLICAÇÂO EM: {instance.data_publicacao:%d/%m/%Y} "
                    f"({instance.get_veiculo_publicacao_display()} Nº {instance.numero_publicacao})"
                )
            else:
                info = f"PUBLICAÇÂO EM: {instance.data_publicacao:%d/%m/%Y}"
        else:
            info = f"PUBLICAÇÂO EM: Indisponível"

        _dict_.update(
            title=f"{capitalize_words(DOCS[instance.tipo])} {instance.numero}/{instance.ano}",
            url=instance.arquivo.no_logged_permalink(),
            abstract=str(
                striptags(re.sub("[\\t\\n\\r\\f\\v]", "", instance.observacao or ""))
            ).replace("&nbsp;", " "),
            info=info,
        )

        return _dict_
