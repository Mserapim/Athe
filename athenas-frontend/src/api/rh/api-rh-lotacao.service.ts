import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword: string;
}

class ResponseItem {
    id: number;
    nome: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhLotacao(payload: Payload) {
    const { data } = await useGet<Response>('rh/workplaces/', payload);
    return data;
}
