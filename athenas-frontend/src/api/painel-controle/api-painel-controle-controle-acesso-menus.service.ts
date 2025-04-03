import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: number;
}

export class ApiPainelControleControleAcessoMenusItem {
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
    servidores_favoritos: any[];
}

export class ApiPainelControleControleAcessoMenus extends ListPaginated<ApiPainelControleControleAcessoMenusItem> {}

export async function apiPainelControleControleAcessoMenus(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoMenus>(
        'painel-controle/controle-acesso/menus/',
        payload
    );

    return data;
}
