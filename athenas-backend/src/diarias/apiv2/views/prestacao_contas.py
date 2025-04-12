from apiv2.baseviews import ApiCore, ApiDetailView, ListBaseView

from diarias.models import (
    HistoricoFluxoViagemBeneficiario,
    PrestacaoContas,
    PrestacaoContasAnexo,
)

from contrib.utils import getLogger
from contrib.middleware import set_current_user
from django.http import Http404
from rest_framework.response import Response
from django.db import transaction
from datetime import datetime
from standard.models import Choice
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from diarias.apiv2.serializers.prestacao_contas import (
    ContaMpmtSerializer,
    PrestacaoContasSerializer,
)
from diarias.utils.fluxo_movimentacao import benef_mover_etapa
from rh.models import Servidor
from ged.models import Arquivo
import traceback
from datetime import date, timedelta
from auth.backend import MultiAuthentication

from diarias.utils.notificacao_prestacao_contas import (
    envio_email_prestacao_contas_colaboradores_externos,
    envio_email_prestacao_contas_aviso,
)
from diarias.apiv2.serializers.beneficiarios import BeneficiarioConsolidadSerializer
from adm.utils.jwt_utils import verificar_token_jwt
from rh.apiv2.serializers.censoprevidenciario import data_limite
from rh.gfp.models import BankingConvenant
from diarias.const import FLUXO_AGUARDADO_PRESTACAO_CONTAS
from django.shortcuts import get_object_or_404

log = getLogger(__name__)


class PrestacaoContasApiDetailView(ApiDetailView):

    serializer_class = PrestacaoContasSerializer
    model = PrestacaoContas


class PrestacaoContasApiCore(ApiCore):

    serializer_class = PrestacaoContasSerializer
    model = PrestacaoContas

    path_function_map = {
        "editar": "update",
        "assinar": "assinar",
        "aprovar": "aprovar",
        "indeferir": "indeferir",
        "cancelar": "cancelar",
        "notificar": "notificar",
        "receber": "receber",
    }

    def assinar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()

        try:
            usuario = request.user
            pessoa = usuario.servidor.pessoa_fisica
            with transaction.atomic():
                instance.assinar(pessoa)
                instance.status = "entregue"
                instance.save()

                benef_mover_etapa(
                    instance.beneficiario
                )  # FUNÇÃO que move o beneficiario para proxima etapa

            resposta["data"] = PrestacaoContasSerializer(instance).data
            resposta["message"] = "Assinado com sucesso"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            resposta["message"] = f"Erro ao tentar Assinar - {erro_completo}"

        return Response(resposta, status=resposta["code"])

    def aprovar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()
        try:
            usuario = request.user
            pessoa = usuario.servidor.pessoa_fisica
            with transaction.atomic():
                instance.assinar(pessoa)
                instance.status = "aprovado"
                instance.avaliador = usuario.servidor
                instance.save()

                benef_mover_etapa(instance.beneficiario)

            resposta["data"] = PrestacaoContasSerializer(instance).data
            resposta["message"] = "Aprovado com sucesso"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            resposta["message"] = (
                f"Erro ao tentar aprovar a prestação de contas - {erro_completo}"
            )

        return Response(resposta, status=resposta["code"])

    def indeferir(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()
        try:
            usuario = request.user
            with transaction.atomic():
                instance.status = "com_pendencias"
                instance.avaliador = usuario.servidor
                instance.save()

                beneficiario = instance.beneficiario

                benef_mover_etapa(beneficiario)

                nova_prestacao = PrestacaoContas.objects.create(
                    beneficiario=instance.beneficiario,
                    obs_servicos_executados=instance.obs_servicos_executados,
                    obs_resultado=instance.obs_resultado,
                    obs=instance.obs,
                    obs_anlaise=instance.obs_anlaise,
                )

                for anexo in instance.anexos.all():
                    PrestacaoContasAnexo.objects.create(
                        prestacao=nova_prestacao, arquivo=anexo.arquivo
                    )

            resposta["data"] = PrestacaoContasSerializer(instance).data
            resposta["message"] = "Indeferido com sucesso"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            resposta["message"] = (
                f"Erro ao tentar Indeferido a prestação de contas - {erro_completo}"
            )

        return Response(resposta, status=resposta["code"])

    def cancelar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()
        try:
            instance.delete()

            resposta["data"] = PrestacaoContasSerializer(instance).data
            resposta["message"] = "Cancelado com sucesso"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            resposta["message"] = (
                f"Erro ao tentar Cancelar a prestação de contas - {erro_completo}"
            )

        return Response(resposta, status=resposta["code"])

    def notificar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()

        try:
            usuario = request.user
            if usuario.servidor.type_by_possession in ["COE", "TCR"]:
                envio_email_prestacao_contas_colaboradores_externos(
                    instance.beneficiario
                )
            else:
                envio_email_prestacao_contas_aviso(instance)

            resposta["message"] = "Notificação envida"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            resposta["message"] = (
                f"Erro ao tentar reenviar notificação sobre a prestação de contas - {erro_completo}"
            )

        return Response(resposta, status=resposta["code"])

    def receber(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "code": 400,
        }
        set_current_user(request.user)
        instance = self.get_object()
        try:
            instance.avaliador = request.user.servidor
            instance.status = "em_analise"

            instance.save()

            hist_beneficiario = HistoricoFluxoViagemBeneficiario.objects.create(
                viagem=instance.beneficiario.viagem,
                beneficiario=instance.beneficiario,
                fluxo=instance.beneficiario.fluxo,
                obs=f"Prestação de contas recebida por {request.user.servidor.pessoa_fisica.social_name}",
                decisao=" ",
                tipo="beneficiario",
            )

            resposta["data"] = PrestacaoContasSerializer(instance).data
            resposta["message"] = "Prestação de contas recebida com sucesso"
            resposta["code"] = 200

        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            resposta["message"] = (
                f"Erro ao tentar receber a prestação de contas - {erro_completo}"
            )

        return Response(resposta, status=resposta["code"])


class PrestacaoContasApiList(ListBaseView):

    serializer_class = PrestacaoContasSerializer
    model = PrestacaoContas
    full_text_index = (
        "beneficiario__servidor__pessoa_fisica__nome__unaccent__icontains",
        "beneficiario__servidor__pessoa_fisica__social_name__unaccent__icontains",
        "beneficiario__servidor__matricula__icontains",
        "beneficiario__servidor__user__username__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(
                name="exportar",
                description="Formato do arquivo a ser exportado",
                type=str,
            ),
            OpenApiParameter(
                name="sincrono",
                description="informar a execução do download",
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
        return PrestacaoContas.objects.filter()

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        status = self.request.GET.getlist("status[]")
        servidores = self.request.GET.getlist("servidores[]")

        if status and len(status) > 0:
            queryset = queryset.filter(status__in=status)

        beneficiario_id = self.request.GET.get("beneficiario_id")

        if beneficiario_id and beneficiario_id is not None:
            queryset = queryset.filter(beneficiario=beneficiario_id)

        if servidores and len(servidores) > 0:
            queryset = queryset.filter(beneficiario__servidor__in=servidores)

        return queryset.distinct()


def string_para_boolean(value):
    """Converte um valor de string ou booleano em um booleano."""
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


class PrestacaoContasExternaView(ApiCore):

    authentication_classes = [MultiAuthentication]
    serializer_class = PrestacaoContasSerializer
    model = PrestacaoContas

    path_function_map = {
        "autenticar": "autenticar",
        "cadastrar": "cadastrar",
    }

    def cadastrar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "data": {},
            "code": 400,
        }
        set_current_user(request.user)

        try:
            with transaction.atomic():

                instance = self.get_object()

                if instance.beneficiario.fluxo.id != FLUXO_AGUARDADO_PRESTACAO_CONTAS:
                    raise Exception(
                        "Reenvio não permitido: a Prestação de Contas já foi enviada anteriormente."
                    )

                for key, arquivo in request.FILES.items():

                    anexo = Arquivo.create_ged(upfile=arquivo)
                    PrestacaoContasAnexo.objects.create(
                        prestacao=instance, arquivo=anexo
                    )

                viagem_realizada = request.POST.get("viagem_realizada")
                viagem_total = request.POST.get("viagem_total")

                instance.obs_servicos_executados = request.POST.get(
                    "obs_servicos_executados"
                )
                instance.obs_resultado = request.POST.get("obs_resultado")
                instance.obs = request.POST.get("obs")

                instance.viagem_realizada = string_para_boolean(viagem_realizada)
                instance.viagem_total = string_para_boolean(viagem_total)

                instance.assinado_por = instance.beneficiario.servidor.pessoa_fisica
                instance.assinado_em = datetime.now()

                instance.status = "entregue"

                instance.save()

                benef_mover_etapa(instance.beneficiario)

                resposta["data"] = PrestacaoContasSerializer(instance).data

                resposta["message"] = f"Prestação de Contas Cadastrada"
                resposta["success"] = True
                resposta["code"] = 200
        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            log.error(e)
            resposta["message"] = f"{e}"

        return Response(resposta, status=resposta["code"])

    def autenticar(self, request, *args, **kwargs):
        resposta = {
            "success": False,
            "message": "Nada Feito",
            "data": {},
            "code": 400,
        }
        set_current_user(request.user)

        try:
            token = request.data.get("token")
            instance = self.get_object()

            if instance.beneficiario.fluxo.id != FLUXO_AGUARDADO_PRESTACAO_CONTAS:
                raise Exception(
                    "Reenvio não permitido: a Prestação de Contas já foi enviada anteriormente."
                )

            user_token = verificar_token_jwt(token)

            if user_token.get("status") == "válido":
                user_token = user_token.get("usuario")
            else:
                raise Exception(user_token.get("mensagem"))

            if instance.beneficiario.servidor.user.username != user_token:
                raise Exception(
                    "O ID e o token fornecidos não pertencem ao mesmo usuário."
                )

            dados_bancarios_mpmt = BankingConvenant.objects.get(id=1)  # convenio do BB

            resposta["data"]["data_limite"] = instance.data_limite
            resposta["data"]["beneficiario"] = BeneficiarioConsolidadSerializer(
                instance.beneficiario
            ).data
            resposta["data"]["dados_bancarios_mpmt"] = ContaMpmtSerializer(
                dados_bancarios_mpmt
            ).data

            resposta["message"] = f"Autenticado com Sucesso"
            resposta["success"] = True
            resposta["code"] = 200
        except Exception as e:
            erro_completo = traceback.format_exc()
            log.error(erro_completo)
            log.error(e)
            resposta["message"] = f"{e}"

        return Response(resposta, status=resposta["code"])


class ContaMpmtDevolucaoDetailView(ApiDetailView):

    serializer_class = ContaMpmtSerializer
    model = BankingConvenant

    def retrieve(self, request, *args, **kwargs):
        id = 1
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, id=id)
        serializer = self.serializer_class(item)
        return Response(serializer.data)
