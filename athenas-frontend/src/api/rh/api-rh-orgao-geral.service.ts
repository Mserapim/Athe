import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

class ApiRhOrgaoGeralResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    nome: string;
    descricao: string;
    abreviacao: string;
    esfera_governamental: number;
    poder: number;
    sigla: string;
    ativo: boolean;
    codigo_igeprev: number;
    data_alteracao: Date;
    publica_doc: boolean;
    habilita_protocolo: boolean;
    order_nome: string;
    cache_identifier: string;
    order_weight: number;
    created_by: number;
    modified_by: number;
    old: number;
    publication: number;
}

class Response extends ListPaginated<ApiRhOrgaoGeralResponseItem> {}

export async function apiRhOrgaoGeral(payload: Payload) {
    const { data } = await useGet<Response>('rh/orgao-geral/', payload);
    return data;
}
