import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    page: number;
}

export class ApiRhPvfConfigEmployeesTeleworksStatusResponseItem {
    active_workplan: boolean;
    telework_pending: boolean;
    telework_id: number;
    send_workplan_reference: number;
}

export async function apiRhPvfConfigEmployeesTeleworksStatus(payload: Payload) {
    const { data } =
        await useGet<ApiRhPvfConfigEmployeesTeleworksStatusResponseItem>(
            '/rh/pvf/config/employees/teleworks/status/',
            payload
        );
    return data;
}
