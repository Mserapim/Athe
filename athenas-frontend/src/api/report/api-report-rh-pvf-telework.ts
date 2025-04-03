import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    plan_work_id: number;
    send_telework_id: number;
    employee_id: number;
}

export class ApiReportRhPvfTeleworkResponseItem {
    message: string;
    success: boolean;
    uuid: string;
}

class Response extends ListPaginated<ApiReportRhPvfTeleworkResponseItem> {}

export async function apiReportRhPvfTeleworkService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/report/rh/pvf/telework/',
        payload
    );
    return data;
}
