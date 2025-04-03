import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

export class ApiRhPvfConfigEmployeesServiceResponseItem {
    pk: number;
    name: string;
    matricula: number;
}

class Response extends ListPaginated<ApiRhPvfConfigEmployeesServiceResponseItem> {}

export async function apiRhPvfConfigEmployeesService(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/employees/',
        payload
    );
    return data;
}
