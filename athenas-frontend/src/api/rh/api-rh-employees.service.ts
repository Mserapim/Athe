import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    page?: number;
}

class ResponseItem {
    employee_matricula: string;
    employee_name: string;
    employee_type_by_possession: string;
    employee_job_position: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhEmployeesService(payload: Payload) {
    const { data } = await useGet<Response>('rh/employees/', payload);
    return data;
}
