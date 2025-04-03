import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    // owner: number;
    workplace: number;
    type_shift: number;
    employee: number;
    days: number;
    start_date: Date;
    end_date: Date;
    anexo: number;
    observacao?: string;
}

class ResponseItem {
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
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfScalesServerShiftsPostService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/scales/server-shifts/',
        payload
    );
    return data;
}
