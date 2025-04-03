import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
}

class Response {
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
    anexo: number;
    observacao: string;
    anexo_display: string;
}

export async function apiRhPvfScalesServerShiftsIdService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/scales/server-shifts/' + payload.id,
        payload
    );
    return data;
}
