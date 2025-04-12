from contrib.utils import getLogger


log = getLogger(__name__)


class Permissoes(object):
    """
    Classe com métodos e lógicas para funcionalidades sobre permissões em menus e submenus
    """

    def consolidar_permissoes(self, acoes_menu, acoes_config):
        return list(set(acoes_menu) | set(acoes_config))

    def buscar_grupos_permissoes(self, servidor):
        return servidor.grupos_permissao.all()

    def buscar_configs_permissoes(self, item):
        return item.configs.all()

    def buscar_servidores_grupo(self, grupo):
        return grupo.servidores.all()

    def verificar_atualizar_menu_permissoes(self, menus_permissoes, config):
        criar_config = True
        for mp in menus_permissoes:
            if mp["menu"] == config.menu:
                criar_config = False
                mp["acoes"] = self.consolidar_permissoes(mp["acoes"], config.acoes)

        if criar_config:
            menus_permissoes.append(
                {
                    "menu": config.menu,
                    "acoes": config.acoes,
                }
            )

        return menus_permissoes

    def buscar_menus_permissoes_servidor(self, servidor):
        menus_permissoes = []
        for grupo in self.buscar_grupos_permissoes(servidor):
            for config in self.buscar_configs_permissoes(grupo):
                menus_permissoes = self.verificar_atualizar_menu_permissoes(
                    menus_permissoes, config
                )

        return menus_permissoes

    def buscar_servidores_permissoes_menu(self, menu):
        grupos_permissoes = []
        for config in self.buscar_configs_permissoes(menu):
            grupos_permissoes.append(
                {
                    "grupo": config.usuario_grupo,
                    "servidores": [
                        servidor
                        for servidor in self.buscar_servidores_grupo(
                            config.usuario_grupo
                        )
                    ],
                    "acoes": config.acoes,
                }
            )

        return grupos_permissoes
