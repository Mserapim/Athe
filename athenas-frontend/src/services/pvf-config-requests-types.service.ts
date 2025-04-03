import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    page: number;
}

export class PvfConfigRequestsTypesItem {
    value: number;
    label: string;
}

class Response extends ListPaginated<PvfConfigRequestsTypesItem> {}

export async function pvfConfigRequestsTypesService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/types',
        payload
    );
    return data;
}
