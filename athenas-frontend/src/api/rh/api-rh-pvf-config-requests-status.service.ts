import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    keyword?: number;
    page?: number;
    per_page?: number;
    palavra_chave?: string 
}

export class ApiRhPvfConfigRequestsStatusResponseItem {
    label: string;
    value: string;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsStatusResponseItem> {}

export async function apiRhPvfConfigRequestsStatus(payload: Payload) {
    if(payload.palavra_chave){
        payload.keyword = payload.palavra_chave as any
    }
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/status',
        payload
    );
    return data;
}
