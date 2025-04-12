from contrib.utils import getLogger

from menu_permissoes.models import Modulo, MenuGrupo, Menu, MenuConfig
from rh.models import Servidor
from standard.models import Choice

from menu_permissoes.permissoes import Permissoes

log = getLogger(__name__)


class Menus(object):
    """
    Classe com métodos e lógicas para funcionalidades sobre módulos, grupo de menus e menus
    """

    def __init__(self, *args, **kwargs):
        self.modulo = kwargs.get("modulo", None)

    def normalizar_item_res(self, item_menu):
        """
        Método para normalizar a resposta da estrutura de Menu
        """

        res = {
            "pk": item_menu.pk,
            "nome": item_menu.nome,
            "ordem": item_menu.ordem,
            "icone": item_menu.icone,
            "situacao": item_menu.situacao,
            "cor": item_menu.cor,
        }

        if isinstance(item_menu, Modulo):
            res["sigla"] = item_menu.sigla or ""

        if isinstance(item_menu, Menu):
            res["url"] = item_menu.url or ""
            res["descricao"] = item_menu.descricao or ""

        return res

    def normalizar_item_menu_config(self, item):
        """
        Método para normalizar a resposta da estrutura de MenuConfig
        """

        return {
            "pk": item.pk,
            "nome": item.usuario_grupo.nome,
            "descricao": item.usuario_grupo.descricao,
            "acoes": item.acoes,
        }

    def normalizar_item_usuario_grupo(self, item):
        """
        Método para normalizar a resposta da estrutura de UsuarioGrupo
        """

        return {
            "matricula": item.matricula,
            "nome": item.pessoa_fisica.nome,
        }

    def buscar_menus(self, grupo, ativo):
        """
        Método para buscar os menus vinculados a um grupo de menus
        """

        q_menus = Menu.objects.filter(grupo=grupo)

        if ativo is not None:
            q_menus = q_menus.filter(situacao=ativo)

        return q_menus

    def buscar_grupos(self, modulo, ativo):
        """
        Método para buscar os grupos de menus vinculados a um módulo
        """

        q_grupos_menu = MenuGrupo.objects.filter(modulo=modulo)

        if ativo is not None:
            q_grupos_menu = q_grupos_menu.filter(situacao=ativo)

        return q_grupos_menu

    def buscar_modulos(self, ativo, modulo_id):
        """
        Método para buscar os Módulos
        """

        q_modulos = Modulo.objects.filter()

        if ativo is not None:
            q_modulos = q_modulos.filter(situacao=ativo)

        if modulo_id is not None:
            q_modulos = q_modulos.filter(pk=modulo_id)

        return q_modulos

    def buscar_menu_config(self, menu, ativo):
        """
        Método para buscar os MenuConfig
        """

        q_menu_config = MenuConfig.objects.filter(menu=menu)

        # if ativo is not None:
        #     q_menu_config = q_menu_config.filter(situacao=ativo)

        return q_menu_config

    def buscar_acoes(self, menu_config_id):
        """
        Método para buscar Ações de um MenuConfig
        """

        q_menu_config = MenuConfig.objects.get(pk=menu_config_id)

        return q_menu_config.acoes

    def quantidade_servidores(self, menus_config):
        """
        Método que retorna a quantidade de servidores no(s) MenuConfig(s) informado(s)
        """
        return (
            Servidor.objects.filter(grupos_permissao__configs__in=menus_config)
            .distinct()
            .count()
        )

    def buscar_acoes_menu_servidor(self, menu_item, menus_comparacao):
        menu_econtrado = [
            menu for menu in menus_comparacao if menu["menu"] == menu_item
        ]
        if len(menu_econtrado) == 0:
            return []
        else:
            return menu_econtrado[0]["acoes"]

    def buscar_todas_acoes(self):
        """
        Método que retorna uma lista de todas as Ações disponíveis no sistema
        """
        return Choice.objects.filter(
            app_label="menu_permissoes", name="ACOES_PERMISSOES"
        ).values_list("label", flat=True)

    def buscar_todas_acoes_selecionadas(self):
        """
        Método que retorna uma lista de todas as Ações que estão registradas/selecionadas no sistema
        """
        query_acoes = MenuConfig.objects.distinct("acoes").values_list(
            "acoes", flat=True
        )
        acoes_encontradas = []

        for acoes in query_acoes:
            for acao in acoes:
                if acao not in acoes_encontradas:
                    acoes_encontradas.append(acao)
        return acoes_encontradas

    def buscar_menus_favoritos(self, servidor_id):
        servidor = Servidor.objects.get(id=servidor_id)
        menus = servidor.menus_favoritos.all().values_list("id", "nome", "url")
        return [{"id": x[0], "nome": x[1], "url": x[2] if x[2] else ""} for x in menus]

    def buscar_estrutura_completa(self, *args, **kwargs):
        """
        Método para buscar toda a estrutura hierárquica de módulos, grupo de menus e menus
        """

        situacao = kwargs.get("situacao", None)
        modulo_id = kwargs.get("modulo_id", None)
        consolidado = kwargs.get("consolidado", False)
        servidor_id = kwargs.get("servidor_id", None)
        retornar_favoritos = kwargs.get("retornar_favoritos", False)

        try:
            itens = []
            for modulo in self.buscar_modulos(situacao, modulo_id):
                item_modulo = self.normalizar_item_res(modulo)
                item_modulo["grupos"] = []

                for grupo in self.buscar_grupos(modulo, situacao):
                    item_grupo = self.normalizar_item_res(grupo)
                    item_grupo["menus"] = []

                    for menu in self.buscar_menus(grupo, situacao):
                        item_menu = self.normalizar_item_res(menu)

                        # Se cosolidado = True, retorna as informações referente aos MenuConfig e UsuarioGrupo
                        if consolidado:
                            menus_config = self.buscar_menu_config(menu, situacao)

                            item_menu["qtd_grupo_permissao"] = menus_config.count()
                            item_menu["qtd_usuario_grupo"] = self.quantidade_servidores(
                                menus_config
                            )

                        if servidor_id is None:
                            item_grupo["menus"].append(item_menu)
                        else:
                            # Lógica para adicionar à lista somente menus que o servidor tem permissão
                            servidor = Servidor.objects.get(pk=servidor_id)
                            menus_servidor = (
                                Permissoes().buscar_menus_permissoes_servidor(servidor)
                            )
                            acoes_menu_servidor = self.buscar_acoes_menu_servidor(
                                menu, menus_servidor
                            )
                            if len(acoes_menu_servidor) > 0:
                                item_menu["acoes"] = acoes_menu_servidor
                                item_grupo["menus"].append(item_menu)

                    if servidor_id is None or len(item_grupo["menus"]) > 0:
                        item_modulo["grupos"].append(item_grupo)

                if servidor_id is None or len(item_modulo["grupos"]) > 0:
                    itens.append(item_modulo)

            if retornar_favoritos and servidor_id:
                menus = {"menus_favoritos": self.buscar_menus_favoritos(servidor_id)}
                itens.append(menus)

            return itens
        except:
            return []
