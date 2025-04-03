import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword: string;
    page: number;
    per_page: number;
}

class ResponseItem {
    id: number;
    nome: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhComarcas(payload: Payload) {
    const { data } = await useGet<Response>('rh/comarcas/', payload);
    return data;
}
