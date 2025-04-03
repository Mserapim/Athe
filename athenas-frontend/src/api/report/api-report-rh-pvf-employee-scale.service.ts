import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    employee_id: number;
    workplace_id: number;
    competence: string;
    tipo_plantao: number;
    inicio: Date;
    fim: Date;
    comarcas: number[];
}

class Response {
    uuid: string;
}

export async function apiReportRhPvfEmployeeScaleService(payload: Payload) {
    const { data } = await usePost<Response>(
        'report/rh/pvf/employee-scale/',
        payload
    );
    return data;
}
