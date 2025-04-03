import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    
}

class ResponseItem {
    id: number;
    descricao: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasChoicesSituacoes(payload: Payload) {
    const { data } = await useGet<Response>('diarias/situacoes/', payload);
    return data;
}