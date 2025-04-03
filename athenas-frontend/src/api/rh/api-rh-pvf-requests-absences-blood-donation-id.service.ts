import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsAbsencesBloodDonationIdResponse {
    blood_donation_certificate: number;
    start_date: Date;
    end_date: Date;
    days: number;
}

export async function apiRhPvfRequestsAbsencesBloodDonationId(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsAbsencesBloodDonationIdResponse>(
            '/rh/pvf/requests/absences/blood-donation/' + payload.requestId,
            payload
        );
    return data;
}
