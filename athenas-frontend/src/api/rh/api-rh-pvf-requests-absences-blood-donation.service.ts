import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    start_date: Date;
    end_date: Date;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    blood_donation_certificate: number;
    observation: string;
}

class Response {
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver: number;
    status_name: string;
}

export async function apiPvfRequestsAbsencesBloodDonationService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/absences/blood-donation/',
        payload
    );
    return data;
}
