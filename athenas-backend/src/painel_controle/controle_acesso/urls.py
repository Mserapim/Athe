from django.urls import path

from painel_controle.controle_acesso.apiv2.views import (
    MenuConfigApicoreView,
    MenuPorUsuarioView,
    ModulosPorUsuarioView,
    ModulosView,
    ModuloView,
    MenusView,
    ModuloDetailView,
    MenuAjudaView,
    GruposMenusView,
    GruposMenus,
    GrupoMenuCoreView,
    MenuCoreView,
    MenuDetailView,
    MenusListView,
    MenuConfigsView,
    MenuConfigCoreView,
    AcoesMenuConfigView,
    UsuarioGruposView,
    UsuarioGruposApicoreView,
    UsuarioGrupoUsersAPIList,
    UsuarioGruposDetailView,
    MenusGrupoUsersAPIList,
    UsuarioGrupoVinculadoAPIList,
    UsuarioEstruturaListView,
    UsuariosAPIList,
    UsuarioApiDetailView,
    UsuarioApiCore,
    AtualizarInfoMastiffView,
    IconsListView,
    UsuariosPorMenuView,
    UsuarioMininoGrupoUserAPIList,
)


urlpatterns = [
    path("modulos/", ModulosView.as_view(), name="modulos"),
    path("modulo/", ModuloDetailView.as_view(), name="modulo"),
    path("modulo/criar/", ModuloView.as_view(), name="modulo-criar"),
    path("modulo/editar/", ModuloView.as_view(), name="modulo-editar"),
    path(
        "modulo/grupos-menus/", GruposMenusView.as_view(), name="modulos_grupos_menus"
    ),
    path("modulo/grupo-menus/menus/", MenusView.as_view(), name="modulos_menus"),
    path(
        "modulo/grupo-menu/criar/", GrupoMenuCoreView.as_view(), name="criar_grupo_menu"
    ),
    path(
        "modulo/grupo-menu/editar/",
        GrupoMenuCoreView.as_view(),
        name="editar_grupo_menu",
    ),
    path("grupos-menus/", GruposMenus.as_view(), name="consolidado_grupos_menus"),
    path("menus/", MenusListView.as_view(), name="menus"),
    path("menu/", MenuDetailView.as_view(), name="menu"),
    path("menu/criar/", MenuCoreView.as_view(), name="criar_menu"),
    path("menu/editar/", MenuCoreView.as_view(), name="editar_menu"),
    path(
        "menu/menu-config/criar/",
        MenuConfigCoreView.as_view(),
        name="criar_menu_config",
    ),
    path(
        "menu/menus-configs/usuarios",
        UsuariosPorMenuView.as_view(),
        name="usuarios-por-menu",
    ),
    path("menu/ajuda/", MenuAjudaView.as_view(), name="menu-ajuda"),
    path("acoes/", AcoesMenuConfigView.as_view(), name="lista_acoes"),
    path("icons/", IconsListView.as_view(), name="lista_icons"),
    path("menu-configs/", MenuConfigsView.as_view(), name="menu_configs"),
    path("grupos/", UsuarioGruposView.as_view(), name="usuario_grupos"),
    path("grupo/", UsuarioGruposDetailView.as_view(), name="detalhes_usuario_grupos"),
    path(
        "grupo/criar/", UsuarioGruposApicoreView.as_view(), name="criar_usuario_grupos"
    ),
    path(
        "grupo/editar/",
        UsuarioGruposApicoreView.as_view(),
        name="editar_usuario_grupos",
    ),
    path(
        "grupo/apagar/",
        UsuarioGruposApicoreView.as_view(),
        name="apagar_usuario_grupos",
    ),
    path(
        "grupo/atualizar-usuarios/",
        UsuarioGruposApicoreView.as_view(),
        name="atualizar_usuarios_usuario_grupos",
    ),
    path(
        "grupo/usuarios/",
        UsuarioGrupoUsersAPIList.as_view(),
        name="usuarios_usuario_grupos",
    ),
    path(
        "grupo/usuarios/minimo/",
        UsuarioMininoGrupoUserAPIList.as_view(),
        name="usuarios_usuario_grupos",
    ),
    path(
        "grupo/menus-config/",
        MenusGrupoUsersAPIList.as_view(),
        name="menus_usuario_grupos",
    ),
    path("modulos/usuario/", ModulosPorUsuarioView.as_view(), name="modulos_usuario"),
    path("menu/usuario/", MenuPorUsuarioView.as_view(), name="menu_usuario"),
    path(
        "menu-config/criar/", MenuConfigApicoreView.as_view(), name="criar_menu_config"
    ),
    path(
        "menu-config/apagar/",
        MenuConfigApicoreView.as_view(),
        name="apagar_menu_config",
    ),
    path(
        "menu-config/editar/",
        MenuConfigApicoreView.as_view(),
        name="editar_menu_config",
    ),
    path("usuarios/", UsuariosAPIList.as_view(), name="usuarios"),
    path("usuario/", UsuarioApiDetailView.as_view(), name="detalhes_usuario"),
    path("usuario/editar/", UsuarioApiCore.as_view(), name="editar_usuario"),
    path(
        "usuario/grupos/",
        UsuarioGrupoVinculadoAPIList.as_view(),
        name="usuario_grupos_por_usuario",
    ),
    path(
        "usuario/atualizar-grupos/",
        UsuarioApiCore.as_view(),
        name="usuario_grupos_por_usuario",
    ),
    path(
        "usuario/estrutura-menus/",
        UsuarioEstruturaListView.as_view(),
        name="usuario_estrutura_menus",
    ),
    path(
        "usuario/atualizar-infos-mastiff/",
        AtualizarInfoMastiffView.as_view(),
        name="atualizar_infos_mastiff",
    ),
    path(
        "usuario/menu/atualizar-favoritos/",
        MenuCoreView.as_view(),
        name="atualizar_favoritos",
    ),
]
