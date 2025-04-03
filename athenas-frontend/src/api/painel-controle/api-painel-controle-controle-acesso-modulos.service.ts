import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    palavra_chave?: number;
    situacao?: string;
}

export class ApiPainelControleControleAcessoModulosItem {
    pk: number;
    nome: string;
    ordem: number;
    situacao: 'ATIVO' | string;
}

export class ApiPainelControleControleAcessoModulos extends ListPaginated<ApiPainelControleControleAcessoModulosItem> {}

export async function apiPainelControleControleAcessoModulos(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoModulos>(
        'painel-controle/controle-acesso/modulos/',
        payload
    );

    return data;
}
