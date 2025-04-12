import json

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import status, serializers
from rest_framework.views import APIView

from apiv2.const import MSG_SUCCESS_METHOD


from django.db.models import Q

from contrib.middleware import set_current_user

from apiv2.baseviews import ListBaseView, ApiCore, ApiDetailView
from contrib.utils import getLogger

from menu_permissoes.models import Modulo, MenuGrupo, Menu, MenuConfig, UsuarioGrupo
from menu_permissoes.menus import Menus
from rh.models import Servidor, ServidorLotacao

from django.contrib.auth.models import User

from rh.servidor.atualizar_infos import AtualizarInfosServidor
from painel_controle.controle_acesso.apiv2.serializers import (
    ModuloSerializer,
    GruposMenuSerializer,
    MenuSerializer,
    MenuConfigSerializer,
    UsuarioGrupoSerializer,
    UsuarioSerializer,
    UsuarioGrupoPorUsuarioSerializer,
    UsuarioMinimoSerializer,
)
from painel_controle.const import ICONS
from painel_controle.controle_acesso.utils import atualizar_favoritos


log = getLogger(__name__)


class ModulosView(ListBaseView):
    """
    View da lista de módulos
    """

    permission_classes = [IsAuthenticated]
    queryset = Modulo.objects.filter()
    serializer_class = ModuloSerializer
    full_text_index = (
        "nome__unaccent__icontains",
        "descricao__unaccent__icontains",
    )

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """

        situacao_list = self.request.query_params.getlist("situacao")
        if len(situacao_list) > 0:
            queryset = queryset.filter(situacao__in=[x.upper() for x in situacao_list])

        return queryset


class ModuloDetailView(ApiDetailView):
    """
    View do detalhe de um módulo
    """

    model = Modulo
    serializer_class = ModuloSerializer


class ModuloView(ApiCore):
    """
    View do detalhe de um módulo
    """

    model = Modulo
    serializer_class = ModuloSerializer


class GruposMenusView(ListBaseView):
    """
    View da lista de grupos de menus de um módulo
    """

    permission_classes = [IsAuthenticated]
    queryset = MenuGrupo.objects.filter()
    serializer_class = GruposMenuSerializer

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        modulo_id = self.request.query_params.get("modulo_id")
        if modulo_id:
            queryset = queryset.filter(modulo__id=modulo_id)

        menu_grupo_id = self.request.query_params.get("id")
        if menu_grupo_id:
            queryset = queryset.filter(id=menu_grupo_id)

        return queryset


class MenusView(ListBaseView):
    """
    View da lista de menus de um grupo de menus
    """

    permission_classes = [IsAuthenticated]
    queryset = Menu.objects.filter()
    serializer_class = MenuSerializer

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        grupo_id = self.request.query_params.get("menu_grupo_id")
        queryset = queryset.filter(grupo__id=grupo_id)

        return queryset


class GruposMenus(ListBaseView):
    """
    View da lista de grupo de menus
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        modulo_id = request.query_params.get("modulo_id")

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": Menus().buscar_estrutura_completa(
                modulo_id=modulo_id, consolidado=True
            )[0]["grupos"],
        }

        return Response(res)


class GrupoMenuDetailView(ApiDetailView):
    """
    Detalhes de Grupo Menu
    """

    model = MenuGrupo
    serializer_class = GruposMenuSerializer


class GrupoMenuCoreView(ApiCore):
    """
    CRUD de Grupo Menu
    """

    model = MenuGrupo
    serializer_class = GruposMenuSerializer


class MenusListView(ListBaseView):
    """
    View da lista de Menus
    """

    permission_classes = [IsAuthenticated]
    serializer_class = MenuSerializer
    pagination_class = None

    def get_queryset(self):
        pk_grupo = self.request.query_params.get("grupo_id", None)
        return Menu.objects.filter(grupo__pk=pk_grupo)


class MenuDetailView(ApiDetailView):
    """
    Detalhes de Menu
    """

    model = Menu
    serializer_class = MenuSerializer


class MenuCoreView(ApiCore):
    """
    CRUD de Menu
    """

    model = Menu
    serializer_class = MenuSerializer

    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "atualizar-favoritos": "update_favoritos",
    }

    def update_favoritos(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        servidor_id = request.data.get("servidor_id")
        menu_id = request.data.get("menu_id")

        try:
            menu = Menu.objects.get(id=menu_id)
        except:
            resposta["resposta"] = "Menu não encontrado!"
            return Response(resposta, status=resposta["code"])

        try:
            servidor = Servidor.objects.get(id=servidor_id)
        except:
            resposta["resposta"] = "Servidor não encontrado!"
            return Response(resposta, status=resposta["code"])

        try:
            if menu.servidores_favoritos.filter(id=servidor.id).exists():
                menu.servidores_favoritos.remove(servidor)
            else:
                menu.servidores_favoritos.add(servidor)

            resposta["resposta"] = MenuSerializer(menu).data

        except:
            resposta["resposta"] = "Erro ao tentar atualizar a lista de Favoritos!"

        return Response(resposta, status=resposta["code"])


class MenuConfigsView(ListBaseView):
    """
    View da lista de MenuConfigs de um Menu
    """

    permission_classes = [IsAuthenticated]
    queryset = MenuConfig.objects.filter()
    serializer_class = MenuConfigSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="menu_id", description="ID do Menu", type=int),
            OpenApiParameter(
                name="usuario_grupo_id", description="ID do UsuarioGrupo", type=int
            ),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        usuario_grupo_id = self.request.query_params.get("usuario_grupo_id")
        if usuario_grupo_id:
            queryset = queryset.filter(usuario_grupo_id=usuario_grupo_id)

        menu_id = self.request.query_params.get("menu_id")
        if menu_id:
            queryset = queryset.filter(menu_id=menu_id)

        return queryset


class MenuConfigDetailView(ApiDetailView):
    """
    Detalhes de MenuConfig
    """

    model = MenuConfig
    serializer_class = MenuConfigSerializer


class MenuConfigCoreView(ApiCore):
    """
    CRUD de MenuConfig
    """

    model = MenuConfig
    serializer_class = MenuConfigSerializer


class UsuarioGruposView(ListBaseView):
    """
    View da lista de UsuarioGrupos
    """

    permission_classes = [IsAuthenticated]
    queryset = UsuarioGrupo.objects.filter()
    serializer_class = UsuarioGrupoSerializer
    full_text_index = (
        "nome__icontains",
        "descricao__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="modulo_id", description="ID do Módulo", type=int),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """

        modulo_id = self.request.query_params.get("modulo_id")
        if modulo_id:
            queryset = queryset.filter(
                configs__menu__grupo__modulo__id=modulo_id
            ).distinct()

        return queryset


class UsuarioGruposDetailView(ApiDetailView):
    """
    View de detalhes de UsuarioGrupos
    """

    model = UsuarioGrupo
    serializer_class = UsuarioGrupoSerializer


class UsuarioGruposApicoreView(ApiCore):
    """
    View da Criar, editar e apagar de UsuarioGrupos
    """

    model = UsuarioGrupo
    serializer_class = UsuarioGrupoSerializer
    path_function_map = {
        "criar": "create",
        "editar": "update",
        "apagar": "exclude",
        "atualizar-usuarios": "update_servidores",
    }

    def update_servidores(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        try:
            grupo_id = request.data.get("id")
            servidores_ids = request.data.get("servidores")

            grupo = UsuarioGrupo.objects.get(id=grupo_id)

            grupo.servidores.clear()

            servidores = Servidor.objects.filter(id__in=servidores_ids)

            grupo.servidores.add(*servidores)

            atualizar_favoritos()

            resposta["resposta"] = UsuarioGrupoSerializer(grupo).data

        except:
            resposta["resposta"] = (
                "Erro ao tentar atualizar a lista de servidores/usuarios"
            )

        return Response(resposta, status=resposta["code"])


class UsuarioGrupoUsersAPIList(ListBaseView):
    """
    View para listar os usuarios de um UsuarioGrupo
    """

    model = Servidor
    serializer_class = UsuarioSerializer
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__social_name__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="usuario_grupo_id", description="ID do Grupo usuario", type=int
            ),
        ]
    )
    def get_queryset(self):
        usuario_grupo_id = self.request.GET.get("usuario_grupo_id")

        try:
            usuario_grupo = UsuarioGrupo.objects.get(pk=usuario_grupo_id)
            return usuario_grupo.servidores.all()
        except:
            return []


class UsuarioMininoGrupoUserAPIList(ListBaseView):
    """
    View para listar os usuarios de um UsuarioGrupo
    """

    model = Servidor
    serializer_class = UsuarioMinimoSerializer
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__social_name__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="usuario_grupo_id", description="ID do Grupo usuario", type=int
            ),
        ]
    )
    def get_queryset(self):
        usuario_grupo_id = self.request.GET.get("usuario_grupo_id")

        try:
            usuario_grupo = UsuarioGrupo.objects.get(pk=usuario_grupo_id)
            return usuario_grupo.servidores.all()
        except:
            return []


class MenusGrupoUsersAPIList(ListBaseView):
    """
    View para listar os usuarios de um UsuarioGrupo
    """

    model = MenuConfig
    serializer_class = MenuConfigSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="usuario_grupo_id", description="ID do Grupo usuario", type=int
            ),
        ]
    )
    def get_queryset(self):
        usuario_grupo_id = self.request.GET.get("usuario_grupo_id")

        try:
            return MenuConfig.objects.filter(usuario_grupo__pk=usuario_grupo_id)
        except:
            return []


class AcoesMenuConfigView(ListBaseView):
    """
    View da lista de Ações de um MenuConfig
    """

    permission_classes = [IsAuthenticated]

    def list(self, request):
        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": Menus().buscar_todas_acoes(),
        }

        return Response(res)


class IconsListView(ListBaseView):
    """
    View da lista de Icones do sitema
    """

    def list(self, request):

        familia = request.GET.get("familia", "mat_outline")

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": ICONS.get(familia) if familia else ICONS,
        }

        return Response(res)


class ModulosPorUsuarioView(ListBaseView):
    """
    View para listar módulos com base nas permissões do usuário logado.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="servidor_id", description="ID do Servidor", type=int
            ),
        ],
        responses={
            200: inline_serializer(
                name="MenuResponse",
                fields={
                    "pk": serializers.IntegerField(),
                    "nome": serializers.CharField(),
                    "ordem": serializers.IntegerField(),
                    "situacao": serializers.CharField(),
                },
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        """
        Lista os módulos do usuário logado.
        """
        servidor_id = request.user.servidor.id
        estrutura_modulos = Menus().buscar_estrutura_completa(servidor_id=servidor_id)
        resultados = []
        for modulo in estrutura_modulos:
            resultados.append(
                {
                    "pk": modulo["pk"],
                    "nome": modulo["nome"],
                    "ordem": modulo["ordem"],
                    "icone": modulo["icone"],
                    "situacao": modulo["situacao"],
                }
            )

        res = {
            "total": "",
            "page": 1,
            "per_page": "",
            "navigation": {"next": None, "previous": None},
            "results": resultados,
        }

        return Response(res)


class MenuPorUsuarioView(ListBaseView):
    """
    View para listar menu com base nas permissões do usuário logado e módulo.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="servidor_id", description="ID do Servidor", type=int
            ),
            OpenApiParameter(name="modulo_id", description="ID do Servidor", type=int),
            OpenApiParameter(
                name="retornar_favoritos",
                description="Retornar menus favoritos?",
                type=bool,
            ),
        ],
        responses=MenuSerializer,
    )
    def list(self, request, *args, **kwargs):
        """
        Lista os módulos do usuário logado.
        """
        q_params = request.query_params

        servidor_id = request.user.servidor.id
        modulo_id = q_params.get("modulo_id")
        situacao = q_params.get("situacao")
        retornar_favoritos = (
            q_params.get("retornar_favoritos")
            if "retornar_favoritos" in q_params
            else False
        )

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": Menus().buscar_estrutura_completa(
                modulo_id=modulo_id,
                servidor_id=servidor_id,
                retornar_favoritos=retornar_favoritos,
                situacao=situacao,
            ),
        }

        return Response(res)


class MenuConfigApicoreView(ApiCore):
    """
    View para criar, editar e apagar configurações de MenuConfig
    """

    model = MenuConfig
    serializer_class = MenuConfigSerializer


class UsuarioGrupoVinculadoAPIList(ListBaseView):
    """
    View para listar os UsuarioGrupo de um Usuario
    """

    model = UsuarioGrupo
    serializer_class = UsuarioGrupoPorUsuarioSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name="usuario_id", description="ID do Usuario", type=int),
            OpenApiParameter(name="modulo_id", description="ID do Módulo", type=int),
            OpenApiParameter(name="nome", description="nome", type=str),
        ]
    )
    def get_queryset(self):
        usuario_id = self.request.query_params.get("usuario_id")

        try:
            servidor = Servidor.objects.get(pk=usuario_id)
        except:
            return Response({"error": "Servidor não entcontrado!"})
        return servidor.grupos_permissao.all()

    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        modulo_id = self.request.GET.get("modulo_id")
        nome = self.request.GET.get("nome")

        if modulo_id:
            queryset = queryset.filter(configs__menu__grupo__modulo__pk=modulo_id)
        if nome:
            queryset = queryset.filter(nome__icontains=nome)

        return queryset


class UsuariosAPIList(ListBaseView):
    """
    View para listar os usuarios
    """

    model = Servidor
    serializer_class = UsuarioSerializer
    queryset = Servidor.objects.all()
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__social_name__icontains",
        "matricula__icontains",
        "user__username__icontains",
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(name="keyword", description="Campo de Pesquisa", type=str),
            OpenApiParameter(name="per_page", description="Por Página", type=int),
            OpenApiParameter(name="situacao", description="Situação", type=str),
            OpenApiParameter(name="lotacao", description="Lotação", type=int),
            OpenApiParameter(
                name="cat_func", description="Caategoria Funcional", type=str
            ),
        ]
    )
    def filter_extra_queryset(self, queryset):
        """
        Realiza os filtros com os valores do filter backend extras
        """
        situacao = self.request.GET.get("situacao")

        if situacao is not None and situacao != "Todos":
            if situacao == "Ativo":
                queryset = queryset.filter(ativo=True)
            else:
                queryset = queryset.filter(ativo=False)

        cat_func = self.request.GET.get("cat_func")

        if cat_func is not None and cat_func != "":
            queryset = queryset.filter(type_by_possession=cat_func)

        lotacao = self.request.GET.get("lotacao")

        if lotacao is not None and lotacao != "":
            lotacoes = ServidorLotacao.objects.filter(
                lotacao_id=lotacao, designacao=False, ativo=True
            )
            queryset = queryset.filter(servidor_lotacao__in=lotacoes)

        return queryset


class UsuarioApiDetailView(ApiDetailView):
    """
    View para editar usuario
    """

    model = Servidor
    serializer_class = UsuarioSerializer


class UsuarioApiCore(ApiCore):
    """
    View para editar usuario
    """

    model = Servidor
    serializer_class = UsuarioSerializer

    path_function_map = {"editar": "update", "atualizar-grupos": "update_grupos"}

    def update(self, request, *args, **kwargs):
        set_current_user(request.user)
        rst = {
            "success": False,
            "message": "Não foi processado nada ainda!",
            "code": status.HTTP_201_CREATED,
        }
        try:
            instance = self.get_object()
            username = request.data.get("username", None)
            instance.user.username = username
            instance.user.save()
            rst.update(
                {
                    "success": True,
                    "message": MSG_SUCCESS_METHOD["put"],
                    "data": UsuarioSerializer(instance).data,
                }
            )
        except Exception as err:
            log.exception(err)
            rst.update({"message": str(err), "code": status.HTTP_400_BAD_REQUEST})
        rst

        return Response(rst, status=rst["code"])

    def update_grupos(self, request, *args, **kwargs):
        set_current_user(request.user)
        resposta = {"code": 200, "resposta": "Nada feito"}

        servidor_id = request.data.get("servidor_id")
        usuario_grupos_ids = request.data.get("usuario_grupos_ids")

        grupos = UsuarioGrupo.objects.filter(id__in=usuario_grupos_ids)

        try:
            servidor = Servidor.objects.get(id=servidor_id)
        except:
            resposta["resposta"] = "Servidor não encontrado!"
            return Response(resposta, status=resposta["code"])

        if not grupos:
            servidor.grupos_permissao.clear()
            resposta["resposta"] = UsuarioSerializer(servidor).data

        try:
            servidor.grupos_permissao.clear()
            servidor.grupos_permissao.add(*grupos)
            atualizar_favoritos()

            resposta["resposta"] = UsuarioSerializer(servidor).data

        except:
            resposta["resposta"] = (
                "Erro ao tentar atualizar a lista de Grupos de Permissão!"
            )

        return Response(resposta, status=resposta["code"])


class UsuarioEstruturaListView(ListBaseView):
    """
    View da estrutura de menus do usuário
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retorno da estrutura de menus do usuário
        """
        return self.list(request, *args, **kwargs)

    def list(self, request):
        servidor_id = request.query_params.get("servidor_id")

        res = {
            "total": "",
            "page": 1,
            "navigation": {"next": None, "previous": None},
            "results": Menus().buscar_estrutura_completa(servidor_id=servidor_id),
        }

        return Response(res)


class AtualizarInfoMastiffView(APIView):
    """
    View para chamar a task que atualiza as informações do Servidor através do Mastiff
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            "application/json": {"type": "object", "properties": {}},
        },
        responses={
            "application/json": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "message": {"type": "string"},
                },
            },
        },
    )
    def post(self, request):
        set_current_user(request.user)
        obj = {
            "success": False,
            "message": "Nada foi feito ainda!",
        }

        servidor_id = self.request.data.get("servidor_id")
        try:
            servidor = Servidor.objects.get(id=servidor_id)
        except:
            obj.update(
                success=False,
                message="Servidor não encontrado",
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)

        try:
            AtualizarInfosServidor().atualizar_username(servidor)

            obj.update(
                success=True,
                message="Conferência de informações do usuário com Mastiff solicitada com sucesso.",
            )
            return Response(obj, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(f"ERRO {e}")
            obj.update(
                success=False,
                message=str(e),
            )
            return Response(obj, status=status.HTTP_400_BAD_REQUEST)


class UsuariosPorMenuView(ListBaseView):
    """
    View da lista de Usuários que possuem acesso a um Menu
    """

    permission_classes = [IsAuthenticated]
    queryset = MenuConfig.objects.filter()
    serializer_class = UsuarioSerializer
    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__social_name__icontains",
    )

    def get_queryset(self):
        menu_id = self.request.GET.get("menu_id")

        try:
            menu_configs = MenuConfig.objects.filter(menu_id=menu_id).select_related(
                "usuario_grupo"
            )
            usuario_grupos_ids = menu_configs.values_list(
                "usuario_grupo_id", flat=True
            ).distinct()
            servidores = Servidor.objects.filter(
                grupos_permissao__in=usuario_grupos_ids
            ).distinct()
            return servidores
        except:
            return []


class MenuAjudaView(APIView):
    """
    View retorna link de ajuda
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        sigla = request.query_params.get("sigla")
        response = {
            "link_de_ajuda": "https://mp-mt.atlassian.net/wiki/spaces/MAN/pages/6102901/Vida+Funcional"
        }
        try:
            menu = Menu.objects.get(url__iexact=sigla)
        except Menu.DoesNotExist:
            return Response(response)
        if not menu.link_de_ajuda:
            return Response(response)
        response.update({"link_de_ajuda": menu.link_de_ajuda})
        return Response(response)
