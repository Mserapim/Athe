import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

export class ApiRhPvfConfigRequestsTimesheetsJustificationItensItem {
    value_key: number;
    name: string;
}

export class ApiRhPvfConfigRequestsTimesheetsJustificationItensResponse extends ListPaginated<ApiRhPvfConfigRequestsTimesheetsJustificationItensItem> {}

export async function apiRhPvfConfigRequestsTimesheetsJustificationItens(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfConfigRequestsTimesheetsJustificationItensResponse>(
            '/rh/pvf/config/requests/timesheets/justification-itens/',
            payload
        );
    return data;
}
