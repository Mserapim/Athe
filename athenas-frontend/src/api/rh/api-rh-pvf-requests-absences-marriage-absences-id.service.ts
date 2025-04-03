import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsAbsencesMarriageAbsencesIdResponse {
    marriage_certificate: number;
    person: number;
    person_name: string;
    start_date: Date;
    end_date: Date;
    days: number;
}

export async function apiRhPvfRequestsAbsencesMarriageAbsencesId(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsAbsencesMarriageAbsencesIdResponse>(
            '/rh/pvf/requests/absences/marriage-absences/' + payload.requestId,
            payload
        );
    return data;
}
