import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiVdfConfigRequestsAcoesServiceResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ApiVdfConfigRequestsAcoesServiceResponseItem> {}

export async function apiVdfConfigRequestsAcoesService(payload: Payload) {
    const { data } = await useGet<Response>('vdf/config/requests/acoes/', payload);
    return data;
}
