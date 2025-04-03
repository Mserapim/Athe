import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

class ResponseItem {
    pk: number;
    name: string;
    responsible: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigServerShiftsWorkplacesService(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/server-shifts/workplaces/',
        payload
    );
    return data;
}
