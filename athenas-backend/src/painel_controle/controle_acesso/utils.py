from contrib.utils import getLogger

log = getLogger(__name__)


def atualizar_favoritos():
    from menu_permissoes.models import Menu

    for menu in Menu.objects.filter(situacao="ATIVO"):
        q_favoritos = menu.servidores_favoritos.all()
        if q_favoritos.exists():
            for servidor in q_favoritos:
                q_permissao = menu.configs.filter(usuario_grupo__servidores=servidor)
                # Se o Servidor não tem permissão ao Menu, o Menu é retirado da lista de favoritos
                if not q_permissao.exists():
                    menu.servidores_favoritos.remove(servidor)
