import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    page?: number;
    per_page?: number;
    keyword?: number;
}

class ResponseItem {
    servidor_id: string;
    name: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfEmployeTeamsService(payload: Payload) {
    const { data } = await useGet<Response>('/rh/pvf/employee-teams', payload);
    return data;
}
