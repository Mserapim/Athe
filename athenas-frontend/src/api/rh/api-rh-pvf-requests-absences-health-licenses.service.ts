import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

export interface ApiPvfRequestsAbsencesHealthLicensesPayload {
    start_date: Date;
    end_date: Date;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    medical_certificate: number;
    hours: number;
    cid: number;
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function apiPvfRequestsAbsencesHealthLicensesService(
    payload: ApiPvfRequestsAbsencesHealthLicensesPayload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/absences/health-licenses/',
        payload
    );
    return data;
}
