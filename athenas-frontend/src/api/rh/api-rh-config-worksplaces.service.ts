import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword: string;
}

export class ApiRhConfigWorkplacesResponseItem {
    pk: number;
    name: string;
    responsible: string;
}

class Response extends ListPaginated<ApiRhConfigWorkplacesResponseItem> {}

export async function apiRhConfigWorkplaces(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/workplaces/',
        payload
    );
    return data;
}
