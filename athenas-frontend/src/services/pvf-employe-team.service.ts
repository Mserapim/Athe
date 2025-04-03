import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    page: number;
}

class ResponseItem {
    id: string;
    name: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function pvfEmployeTeamService(payload: Payload) {
    const { data } = await useGet<Response>('/rh/pvf/employe-team', payload);
    return data;
}
