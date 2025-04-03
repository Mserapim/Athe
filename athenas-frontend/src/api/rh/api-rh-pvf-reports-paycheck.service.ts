import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    month: number;
    year: number;
    type: number;
}

class Response {
    uuid: string;
}

export async function apiRhPvfReportsPaycheckService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/reports/paycheck/',
        payload
    );
    return data;
}
