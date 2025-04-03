import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    keyword?: string;
    page?: string;
    per_page?: string;
}

export class ApiRhPvfConfigServerShiftsTypesItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ApiRhPvfConfigServerShiftsTypesItem> {}

export async function apiRhPvfConfigServerShiftsTypes(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/server-shifts/types',
        payload
    );
    return data;
}
