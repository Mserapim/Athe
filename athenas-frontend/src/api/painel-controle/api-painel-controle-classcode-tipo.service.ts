import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

class ResponseItem {
    sigla: string;
    texto: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiPainelControleTiposClasscode(payload: Payload) {
    const { data } = await useGet<Response>('adm/classcode/tipos/', payload);
    return data;
}
