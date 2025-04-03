import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    approver?: string;
    approver_matricula?: number;
    page?: number;
    per_page?: number;
    request_type?: number[];
    status?: number[];
}

class ResponseItem {
    approver: number;
    approver_name: string;
    date: string;
    employee: number;
    employee_name: string;
    pk: number;
    portal_request_type: number;
    status: number;
    status_name: string;
    step_current: number;
    step_current_name: string;
    type_of_request: string;
}

class Response extends ListPaginated<ResponseItem> {}

export function pvfRequestsService(payload: Payload) {
    return useGet<Response>('/rh/pvf/requests', payload, {});
}
