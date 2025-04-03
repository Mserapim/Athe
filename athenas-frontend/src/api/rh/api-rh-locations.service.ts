import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    estado?: number;
    order_by?: string;
}

export class ApiRhLocationsItem {
    id: number;
    name: string;
    sigla: string;
}

class Response extends ListPaginated<ApiRhLocationsItem> {}

export async function apiRhLocations(payload: Payload) {
    const { data } = await useGet<Response>('rh/locations/', payload);
    return data;
}
