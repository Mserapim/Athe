import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsAbsencesMourningAbsencesIdResponse {
    death_certificate: number;
    family_bond: number;
    person: number;
    start_date: Date;
    end_date: Date;
    days: number;
}

export async function apiRhPvfRequestsAbsencesMourningAbsencesId(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsAbsencesMourningAbsencesIdResponse>(
            '/rh/pvf/requests/absences/mourning-absences/' + payload.requestId,
            payload
        );
    return data;
}
