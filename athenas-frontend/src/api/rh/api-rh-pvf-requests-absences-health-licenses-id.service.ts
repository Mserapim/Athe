import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsAbsencesHealthLicensesIdResponse {
    medical_certificate: number;
    start_date: Date;
    end_date: Date;
    days: number;
}

export async function apiRhPvfRequestsAbsencesHealthLicensesId(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsAbsencesHealthLicensesIdResponse>(
            '/rh/pvf/requests/absences/health-licenses/' + payload.requestId,
            payload
        );
    return data;
}
