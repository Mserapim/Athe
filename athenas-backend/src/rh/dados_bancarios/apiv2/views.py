from apiv2.baseviews import ApiCore, ListBaseView

from django.db.models import Q
from rh.models import Banco, DadoBancarioPessoa
from standard.models import Choice

from contrib.utils import getLogger

from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework import status

from rh.dados_bancarios.apiv2.serializers import (
    BancoSerializer,
    DadoBancarioPessoaSerializer,
    TipoContaSerializer,
)

log = getLogger(__name__)


class BancosApiList(ListBaseView):

    serializer_class = BancoSerializer
    model = Banco
    queryset = Banco.objects.all()
    full_text_index = ("nome__unaccent__icontains", "sigla", "numero")


class TipoContaApiList(ListBaseView):

    serializer_class = TipoContaSerializer
    model = Choice
    queryset = Choice.objects.filter(app_label="rh", name="TIPO_CONTA")


class DadoBancarioPessoaApiList(ListBaseView):

    serializer_class = DadoBancarioPessoaSerializer
    model = DadoBancarioPessoa

    def get_queryset(self):

        servidor_id = self.request.GET.get("servidor_id")
        contas = DadoBancarioPessoa.objects.filter(
            pessoa__pessoafisica__servidor__id=servidor_id
        )

        contas = contas.exclude(
            tipo_conta=3
        )  # exclui todas acontas do tipo conta salario

        contas_exclude = contas.exclude(
            banco=1
        )  # cria uma lista com as contas exceto as contas do banco do brasil

        contas_exclude = contas_exclude.filter(
            Q(agencia_numero__isnull=True)
            or Q(conta_numero__isnull=True)
            or Q(conta_dv__isnull=True)
        )

        contas = contas.exclude(id__in=contas_exclude.values_list("id", flat=True))

        return contas

    def filter_extra_queryset(self, queryset):
        tipos_conta_include = self.request.GET.getlist("tipos_conta", [])
        if len(tipos_conta_include) > 0:
            queryset = queryset.filter(tipo_conta__in=tipos_conta_include)

        tipos_conta_exclude = self.request.GET.getlist("tipos_conta_exclude", [])
        if len(tipos_conta_exclude) > 0:
            queryset = queryset.exclude(tipo_conta__in=tipos_conta_exclude)

        tipo_conta_sal = (
            Choice.objects.filter(app_label="rh", name="TIPO_CONTA", label="SALÁRIO")
            .first()
            .cvalue
        )

        if len(tipos_conta_exclude) == 0 and tipo_conta_sal not in tipos_conta_include:
            queryset = queryset.exclude(tipo_conta=tipo_conta_sal)

        return queryset


class DadoBancarioPessoaApiCore(ApiCore):

    serializer_class = DadoBancarioPessoaSerializer
    model = DadoBancarioPessoa

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "servidor": {"type": "integer"},
                    "banco": {"type": "integer"},
                    "tipo_conta": {"type": "integer"},
                    "agencia": {"type": "string"},
                    "conta_completa": {"type": "string"},
                    "principal": {"type": "boolean"},
                    "agencia_numero": {"type": "string"},
                    "agencia_dv": {"type": "string"},
                    "conta_numero": {"type": "string"},
                    "conta_dv": {"type": "string"},
                },
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Descrição da operação GET

        execulta uma função diacordo com o path da requisição

        Parâmetros:
        - id: Chave primaria do objeto.
        """

        path = request.path

        for keyword, func_name in self.path_function_map.items():
            if keyword in path:
                if func_name == "update":
                    kwargs["partial"] = True
                func = getattr(self, func_name)
                return func(request, *args, **kwargs)

        return Response(
            {"message": "Método não suportado"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
