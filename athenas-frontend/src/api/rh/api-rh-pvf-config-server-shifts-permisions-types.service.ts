import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    keyword?: string;
    page?: string;
    per_page?: string;
    todos_tipos?: boolean;
}

class ResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigServerShiftsPermissionsTypes(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/server-shifts/permissions/types',
        payload
    );
    return data;
}
