import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoModuloGruposMenusPayload extends ListPayload {
    id?: number | string;
    modulo_id?: number | string;
    modulo?: number | string;
    pk?: number | string;
}

export class ApiPainelControleControleAcessoModuloGruposMenusItem {
    menus: any[];
    nome: string;
    icone: string;
    ordem: number;
    pk: number;
    situacao: 'ATIVO';
}

export class ApiPainelControleControleAcessoModuloGruposMenus extends ListPaginated<ApiPainelControleControleAcessoModuloGruposMenus> {}

export async function apiPainelControleControleAcessoModuloGruposMenus(
    payload: ApiPainelControleControleAcessoModuloGruposMenusPayload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoModuloGruposMenus>(
        'painel-controle/controle-acesso/modulo/grupos-menus/',
        payload
    );

    return data;
}
