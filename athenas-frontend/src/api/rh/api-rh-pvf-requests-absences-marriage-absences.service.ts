import { usePost } from 'api/@base/use-post';

interface Payload {
    start_date: Date;
    end_date: Date;
    person: number;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    marriage_certificate: number;
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function apiPvfRequestsAbsencesMarriageAbsencesService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/absences/marriage-absences/',
        payload
    );
    return data;
}
