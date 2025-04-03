import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
}

export class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    unicode: string;
    nome: string;
    numero: string;
    
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhDadosBancariosBancos(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/dados-bancarios/bancos/',
        payload
    );
    return data;
}
