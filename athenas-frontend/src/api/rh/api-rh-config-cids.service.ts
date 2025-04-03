import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiRhPvfConfigCidsServiceResponseItem {
    pk: number;
    chapter: string;
    code: string;
    description: string;
}

class Response extends ListPaginated<ApiRhPvfConfigCidsServiceResponseItem> {}

export async function apiRhPvfConfigCidsService(payload: Payload) {
    const { data } = await useGet<Response>('rh/pvf/config/cids/', payload);
    return data;
}
