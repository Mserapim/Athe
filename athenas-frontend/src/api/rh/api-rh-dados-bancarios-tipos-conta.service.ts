import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
}

export class ResponseItem {
    id: number;
    descricao: string;
    
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhDadosBancariosTiposConta(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/dados-bancarios/tipos-conta/',
        payload
    );
    return data;
}
