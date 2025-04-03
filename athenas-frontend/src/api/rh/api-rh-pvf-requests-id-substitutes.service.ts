import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsIdSubstitutesResponseItem {
    pk: number;
    substitute_name: string;
    designation: string;
    start_date: Date;
    end_date: Date;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdSubstitutesResponseItem> {}

export async function apiRhPvfRequestsIdSubstitutes(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/' + payload.requestId + '/substitutes',
        payload
    );
    return data;
}
