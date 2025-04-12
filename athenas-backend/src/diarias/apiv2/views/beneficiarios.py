from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView
from django.db.models import Q
from diarias.apiv2.serializers.beneficiarios import BeneficiarioSerializer
from diarias.models import (
    Beneficiario,
    CargoDiarias,
    HistoricoFluxoViagemBeneficiario,
    Viagem,
)
from rh.models import Banco, DadoBancarioPessoa
from rh.models import (
    PessoaFisica,
    Localidade,
    Servidor,
    SocialSecurityEmployee,
    SocialSecurityConfig,
)
from contrib.utils import getLogger
from rest_framework.generics import CreateAPIView
from contrib.middleware import set_current_user
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime
from rh.pvf.utils.chefe_imediato import get_aprovador
from standard.models import Choice
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.views import APIView

from diarias.utils.calculo_diarias import CalcularConsolidarDiarias


log = getLogger(__name__)


class BeneficiariosApiList(ListBaseView):

    serializer_class = BeneficiarioSerializer
    model = Beneficiario

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="viagem_id", description="Id da Viagem", type=int),
            OpenApiParameter(
                name="exclude",
                description="Id de um Beneficiario para não ser exibido",
                type=int,
            ),
            OpenApiParameter(
                name="telaChefeImediato",
                description="Indica se a tela é de chefe imediato",
                type=bool,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):

        viagem_id = self.request.GET.get("viagem_id")

        return Beneficiario.objects.filter(viagem__id=viagem_id)

    def filter_extra_queryset(self, queryset):
        exclude_ids = self.request.GET.getlist("exclude[]")
        if exclude_ids:
            queryset = queryset.exclude(pk__in=exclude_ids)

        tela_chefe_imediato = (
            self.request.GET.get("telaChefeImediato", "false").lower() == "true"
        )
        if tela_chefe_imediato:
            current_user = self.request.user
            filtered_queryset = []

            for beneficiario in queryset:
                if beneficiario.chefe_imediato:
                    if beneficiario.chefe_imediato.user == current_user:
                        filtered_queryset.append(beneficiario)
                else:
                    aprovador = get_aprovador(beneficiario.servidor)
                    if aprovador and aprovador.user == current_user:
                        filtered_queryset.append(beneficiario)

            queryset = Beneficiario.objects.filter(
                pk__in=[b.pk for b in filtered_queryset]
            )

        return queryset.distinct()


class BeneficiariosApiCore(ApiCore):

    serializer_class = BeneficiarioSerializer
    model = Beneficiario

    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "recalcular": "recalcular",
    }

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        situacao_rascunho = Choice.objects.get(
            app_label="diarias", name="SITUACAO_SOLICITACAO_VIAGEM", label="Rascunho"
        )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def recalcular(self, request, *args, **kwargs):
        response = {
            "message": "Erro ao recalcular a viagem.",
            "code": 404,
            "data": {},
        }

        set_current_user(request.user)
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        try:
            calculo = CalcularConsolidarDiarias(beneficiario=instance)

            calculo.recalcular_diarias()

            response["message"] = "Viagem recalculada com sucesso."
            response["code"] = 200
        except Exception as e:
            log.error(e)
            response["message"] = e.args[0] if e.args else str(e)

        response["data"] = serializer.data

        return Response(response, response.get("code", 404))


class BeneficiariosDetailView(ApiDetailView):

    serializer_class = BeneficiarioSerializer
    model = Beneficiario


class ColaboradorventualApiCreate(CreateAPIView):

    serializer_class = BeneficiarioSerializer
    model = Beneficiario

    def create(self, request, *args, **kwargs):
        response = {
            "success": True,
            "message": "Erro ao criar colaborador Eventual.",
            "code": 404,
            "data": {},
        }
        set_current_user(request.user)

        try:

            nome = request.data.get("nome")
            email = request.data.get("email")
            cpf = request.data.get("cpf")
            data_nasc = request.data.get("data_nasc")
            cargo_pk = request.data.get("cargo")
            banco_pk = request.data.get("banco")
            tipo_conta = request.data.get("tipo_conta")
            agencia_numero = request.data.get("agencia_numero")
            agencia_dv = request.data.get("agencia_dv")
            conta_numero = request.data.get("conta_numero")
            conta_dv = request.data.get("conta_dv")
            viagem_pk = request.data.get("viagem")

            agencia = f"{agencia_numero}{agencia_dv}"
            conta_completa = f"{conta_numero}{conta_dv}"

            with transaction.atomic():

                pessoa = PessoaFisica.objects.create(
                    social_name=nome,
                    cpf=cpf,
                    data_nascimento=data_nasc,
                    email_pessoal=email,
                    nome=nome,
                    sexo="N",
                    municipio_naturalidade=Localidade.objects.get(pk=12360),
                )

                PessoaFisica.validate_coe_employee(pessoa)

                servidor = Servidor.objects.create(
                    pessoa_fisica=pessoa, type_by_possession="COE", ativo=True
                )

                previdencia = SocialSecurityEmployee()
                previdencia.employee = servidor
                previdencia.mass_segregation_plan = 2
                # "RGPS, Plano previdenciário ou único - INSTITUTO NACIONAL DE SEGURIDADE SOCIAL
                rgps = SocialSecurityConfig.objects.get(pk=1)
                previdencia.social_security_config = rgps
                previdencia.start_validity = datetime.today()
                previdencia.save()

                banco = Banco.objects.get(pk=banco_pk)
                conta_pg = DadoBancarioPessoa.objects.create(
                    pessoa=pessoa,
                    banco=banco,
                    tipo_conta=tipo_conta,
                    agencia=agencia,
                    conta_corrente_completa=conta_completa,
                    agencia_numero=agencia_numero,
                    agencia_dv=agencia_dv,
                    conta_numero=conta_numero,
                    conta_dv=conta_dv,
                )
                viagem = Viagem.objects.get(pk=viagem_pk)

                cargo = CargoDiarias.objects.get(pk=cargo_pk)

                beneficiario = Beneficiario.objects.create(
                    viagem=viagem,
                    servidor=servidor,
                    conta_bancaria_pgto=conta_pg,
                    cargo=cargo,
                )

                response["data"] = BeneficiarioSerializer(beneficiario).data
                response["code"] = 201
                response["message"] = "Registro criado com sucesso."

        except Exception as e:
            log.error(e)
            response["message"] = e.args[0] if e.args else str(e)

        return Response(response, status=response["code"])


class BeneficiariosFluxoHistoricoApiList(ListBaseView):

    serializer_class = BeneficiarioSerializer
    model = Beneficiario

    @extend_schema(
        parameters=[
            OpenApiParameter(name="viagem_id", description="Id da Viagem", type=int),
            OpenApiParameter(name="fluxo_id", description="Id do Fluxo", type=int),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Retorno do Método HTTP GET
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):

        viagem_id = self.request.GET.get("viagem_id")
        fluxo_id = self.request.GET.get("fluxo_id")

        beneficiarios = Beneficiario.objects.filter(
            viagem__id=viagem_id, historico_fluxos__fluxo__id=fluxo_id
        ).distinct()

        return beneficiarios
