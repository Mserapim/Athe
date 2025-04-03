import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: number;
    menu_grupo_id?: number;
}

export class ApiPainelControleControleAcessoModuloGrupoMenusMenusItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    ordem: number;
    icone: string;
    created_by: number;
    modified_by: number;
    grupo: number;
}

export class ApiPainelControleControleAcessoModuloGrupoMenusMenus extends ListPaginated<ApiPainelControleControleAcessoModuloGrupoMenusMenusItem> {}

export async function apiPainelControleControleAcessoModuloGrupoMenusMenus(
    payload: Payload
) {
    const { data } =
        await useGet<ApiPainelControleControleAcessoModuloGrupoMenusMenus>(
            'painel-controle/controle-acesso/modulo/grupo-menus/menus/',
            payload
        );

    return data;
}
