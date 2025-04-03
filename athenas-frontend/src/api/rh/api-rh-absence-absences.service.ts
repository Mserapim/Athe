import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    page: number;
}

class ResponseItem {
    employee_matricula: string;
    employee_name: string;
    absence_type: string;
    absence_start_date: string;
    absence_end_date: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhAbsenceAbsences(payload: Payload) {
    const { data } = await useGet<Response>('rh/absence/absences/', payload);
    return data;
}
