import os
import shutil
import threading
from apiv2.utils import response_api_view
from app import settings
from contrib.hermes import notificar_hermes_ged
from contrib.middleware import get_current_user, set_current_user
from engine.models import TaskSession
from engine.mq.models import Task
from esocial.apiv2.serializers.qualificacaocadastral import (
    ConfigFiltrosEsocialSerializer,
    QualificacaoCadastralSerializer,
)
from esocial.generators.qualification import protocol
from esocial.models import RegistrationQualification
from apiv2.baseviews import ApiCore, ListBaseView
from drf_spectacular.utils import OpenApiParameter, extend_schema
from esocial.apiv2.utils import (
    criar_arquivo_qualificacao,
    get_categoria_tipo_pessoa,
    get_filtro_orientacao_cpf,
    get_filtro_orientacao_nis_pis_pasep,
    get_gerar_nome_arquivo,
    get_status_qualificacao,
)
from esocial.tasks.qualification import discouver_persons, qualificate_batch
from ged.models import Arquivo
from esocial.apiv2.utils import tmp_dir
from rest_framework.response import Response
from contrib.utils import getLogger


log = getLogger(__name__)


class QualificacaoCadastralView(ListBaseView):
    """
    View da tela de qualificação cadastral do esocial
    """

    model = RegistrationQualification
    serializer_class = QualificacaoCadastralSerializer
    full_text_index = (
        "nome__icontains",
        "cpf__icontains",
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
            OpenApiParameter(
                name="categoria[]", description="Categoria pessoa", type=int
            ),
            OpenApiParameter(
                name="status[]", description="Situação da qualificação", type=int
            ),
            OpenApiParameter(
                name="orientacao_cpf[]", description="Orientação CPF", type=int
            ),
            OpenApiParameter(
                name="orientacao_nis[]",
                description="Orientação NIS/PIS/PASEP",
                type=int,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        View de qualificação cadastral do esocial
        """
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        query = self.model.objects.all()
        status_list = self.request.query_params.getlist("status[]")
        categoria_list = self.request.query_params.getlist("categoria[]")
        orientacao_cpf_list = self.request.query_params.getlist("orientacao_cpf[]")
        orientacao_nis_list = self.request.query_params.getlist("orientacao_nis[]")

        if status_list:
            query = query.filter(status__in=status_list)
        if categoria_list:
            query = query.filter(type_of_person__in=categoria_list)
        if orientacao_cpf_list:
            query = query.filter(cod_orientacao_cpf__in=orientacao_cpf_list)
        if orientacao_nis_list:
            query = query.filter(cod_orientacao_nis__in=orientacao_nis_list)

        return query


class QualificacaoCadastralCoreView(ApiCore):
    """
    View para editar usuario
    """

    model = RegistrationQualification
    serializer_class = QualificacaoCadastralSerializer

    path_function_map = {
        "atualizar-lista": "atualizar_lista",
        "confirmar-qualificacao": "confirmar_qualificacao",
        "gerar-arquivo": "gerar_arquivo",
    }

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"arquivo_id": {"type": "integer"}},
            },
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Descrição da operação POST

        executa uma função conforme o path da requisição
        """
        return super(QualificacaoCadastralCoreView, self).post(request, args, kwargs)

    def atualizar_lista(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}
        try:
            Task.start(discouver_persons, user=get_current_user().pk)
        except Exception as e:
            resposta.update(code=400, resposta="Erro ao atualizar a lista.")
            log.error(e)
            return Response(resposta, status=resposta["code"])
        else:
            resposta.update(
                resposta="Avaliação em andamento, você será avisado quando o mesmo for concluído."
            )

        return Response(resposta, status=resposta["code"])

    def confirmar_qualificacao(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        try:
            arquivo_id = request.data.get("arquivo_id")
            Task.start(
                qualificate_batch, ged_file_id=arquivo_id, user=get_current_user().pk
            )
        except Exception as e:
            resposta.update(code=400, resposta="Erro ao gerar a qualificação.")
            log.error(e)
            return Response(resposta, status=resposta["code"])
        else:
            resposta.update(
                resposta="Qualificação em andamento, você será avisado quando o mesmo for concluído."
            )

        return Response(resposta, status=resposta["code"])

    def gerar_arquivo(self, request, *args, **kwargs):
        resposta = {"code": 200, "resposta": "Nada feito"}

        def processar(user, log):
            _tmp_dir = tmp_dir("esocial")
            log.info(
                "GENERATE FILE PROCESS: %s: %s: %s"
                % (user, "QUALIFICATION ESOCIAL", _tmp_dir)
            )
            set_current_user(user)
            task = TaskSession.start_execution("Gerando arquivos de qualificação")

            linhas = protocol.QualificationFile(task)
            caminho_arquivo = os.path.join(_tmp_dir, get_gerar_nome_arquivo())
            log.info(">>>>>>>>>>>> ARQUIVOS GERADOS EM %s" % _tmp_dir)
            arquivo_qualificado = criar_arquivo_qualificacao(
                caminho_arquivo, linhas.__extract_regs__()
            )

            gedfile = Arquivo.from_filepath(arquivo_qualificado, user, "text/plain", 1)

            task.add_file(gedfile)
            task.finish_execution()
            shutil.rmtree(_tmp_dir)

            link_url = f"<a href=/athenas/api/v2/ged/download/?file_id={gedfile.pk}>Download</a>"
            nome_relatorio = "Qualificação Cadastral"
            notificar_hermes_ged(user, link_url, nome_relatorio)

        try:
            t = threading.Thread(target=processar, args=(request.user, log))
            t.start()
        except Exception as e:
            resposta.update(code=400, resposta="Erro ao gerar o arquivo.")
            log.error(e)
            return Response(resposta, status=resposta["code"])
        else:
            resposta.update(
                resposta="Arquivo requisitado com sucesso, você será avisado quando o mesmo for concluido."
            )

        return Response(resposta, status=resposta["code"])


class FiltroCategoriaTipoPessoaView(ListBaseView):
    """
    View do filtro categoria tipo pessoa
    """

    serializer_class = ConfigFiltrosEsocialSerializer

    def get(self, request, *args, **kwargs):
        """
        View do filtro categoria tipo pessoa
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_categoria_tipo_pessoa()
        dados_paginados = self.paginate_queryset(data)
        if dados_paginados is not None:
            data_serializer = self.serializer_class(dados_paginados, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = ConfigFiltrosEsocialSerializer(
            dados_paginados, many=True
        ).data
        return response_api_view(data_serializer)


class FiltroStatusQualificacaoView(ListBaseView):
    """
    View do filtro status de qualificação
    """

    serializer_class = ConfigFiltrosEsocialSerializer

    def get(self, request, *args, **kwargs):
        """
        View do filtro status de qualificação
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_status_qualificacao()
        dados_paginados = self.paginate_queryset(data)
        if dados_paginados is not None:
            data_serializer = self.serializer_class(dados_paginados, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(dados_paginados, many=True).data
        return response_api_view(data_serializer)


class FiltroOrientacaoCPFView(ListBaseView):
    """
    View do filtro por orientação CPF
    """

    serializer_class = ConfigFiltrosEsocialSerializer

    def get(self, request, *args, **kwargs):
        """
        View do filtro por orientação CPF
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_filtro_orientacao_cpf()
        dados_paginados = self.paginate_queryset(data)
        if dados_paginados is not None:
            data_serializer = self.serializer_class(dados_paginados, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(dados_paginados, many=True).data
        return response_api_view(data_serializer)


class FiltroOrientacaoNISPISPASEPView(ListBaseView):
    """
    View do filtro por orientação nis/pis/pasep
    """

    serializer_class = ConfigFiltrosEsocialSerializer

    def get(self, request, *args, **kwargs):
        """
        View do filtro por orientação nis/pis/pasep
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        data = get_filtro_orientacao_nis_pis_pasep()
        dados_paginados = self.paginate_queryset(data)
        if dados_paginados is not None:
            data_serializer = self.serializer_class(dados_paginados, many=True).data
            return self.get_paginated_response(data_serializer)
        data_serializer = self.serializer_class(dados_paginados, many=True).data
        return response_api_view(data_serializer)
