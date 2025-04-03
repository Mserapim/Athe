import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
}

export class ApiRhPvfRequestsIdServerShiftsServiceItem {
    pk: number;
    owner: number;
    workplace: number;
    workplace_name: string;
    type_shift: number;
    type_shift_label: string;
    employee: number;
    employee_name: string;
    days: number;
    start_date: Date;
    end_date: Date;
    status: number;
    status_name: string;
    anexo: number;
    observacao: string;
    anexo_display: string;
}

class Response extends ListPaginated<ApiRhPvfRequestsIdServerShiftsServiceItem> {}

export async function apiRhPvfRequestsIdServerShiftsService(payload: Payload) {
    const { data } = await useGet<Response>(
        `/rh/pvf/requests/${payload.id}/server-shifts/`,
        payload
    );
    return data;
}
