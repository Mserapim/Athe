import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    year: number;
    type: string;
}

class ResponseItem {
    uuid: string;
    error: any;
}

export async function apiReportRhPvfIncomeStatement(payload: Payload) {
    const { data } = await usePost<ResponseItem>(
        'report/rh/pvf/income-statement/',
        payload
    );
    return data;
}
