import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    month: number;
    year: number;
    employee_id: number;
}

export class ApiReportRhPvfPointSheetResponseItem {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiReportRhPvfPointSheetService(payload: Payload) {
    const { data } = await usePost<ApiReportRhPvfPointSheetResponseItem>(
        'report/rh/pvf/folha-ponto/',

        payload
    );
    return data;
}
