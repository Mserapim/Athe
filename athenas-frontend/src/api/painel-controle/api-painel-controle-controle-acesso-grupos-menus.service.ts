import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoGruposMenusPayload extends ListPayload {
    id?: number | string;
    modulo_id?: number | string;
    modulo?: number | string;
    pk?: number | string;
}

export class ApiPainelControleControleAcessoGruposMenusItem {
    menus: any[];
    nome: string;
    ordem: number;
    pk: number;
    situacao: 'ATIVO';
}

export class ApiPainelControleControleAcessoGruposMenus extends ListPaginated<ApiPainelControleControleAcessoGruposMenusItem> {}

export async function apiPainelControleControleAcessoGruposMenus(
    payload: ApiPainelControleControleAcessoGruposMenusPayload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoGruposMenus>(
        'painel-controle/controle-acesso/grupos-menus/',
        payload
    );

    return data;
}
