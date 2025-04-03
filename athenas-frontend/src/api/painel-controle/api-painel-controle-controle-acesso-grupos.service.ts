import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoGruposPayload extends ListPayload {
    id?: number;
    menus_qtd?: number | string;
    usuarios_qtd?: number | string;
    nome?: string;
    descricao?: string;
    situacao?: string;
    menu_id?: number;
    modulo_id?:number
}

export class ApiPainelControleControleAcessoGruposItem {
    id?: number;
    menus_qtd?: number | string;
    usuarios_qtd?: number | string;
    nome?: string;
    descricao?: string;
    situacao?: 'ATIVO' | 'INATIVO';
}

export class ApiPainelControleControleAcessoGrupos extends ListPaginated<ApiPainelControleControleAcessoGruposItem> {}

export async function apiPainelControleControleAcessoGrupos(
    payload: ApiPainelControleControleAcessoGruposPayload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoGrupos>(
        'painel-controle/controle-acesso/grupos/',
        payload
    );

    return data;
}
