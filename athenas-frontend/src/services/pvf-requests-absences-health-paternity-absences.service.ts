import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    start_date: Date;
    end_date: Date;
    dependent: number;
    dependent_type: number;
    is_childcare_assistence: boolean;
    capacity: boolean;
    is_incoming_tax: boolean;
    birth_certificate: number;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function pvfRequestsAbsencesPaternityAbsencesService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/absences/paternity-absences/',
        payload
    );
    return data;
}
