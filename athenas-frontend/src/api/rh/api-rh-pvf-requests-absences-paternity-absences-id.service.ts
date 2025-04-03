import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    requestId: number;
}

export class ApiRhPvfRequestsAbsencesPaternityAbsencesIdResponse {
    birth_certificate: number;
    dependent: number;
    dependent_name: string;
    is_childcare_assistence: boolean;
    is_incoming_tax: boolean;
    capacity: number;
    capacity_label: string;
    incapacity: boolean;
    dependent_type: number;
    dependent_type_label: string;
    start_date: Date;
    end_date: Date;
    days: number;
}

export async function apiRhPvfRequestsAbsencesPaternityAbsencesId(
    payload: Payload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsAbsencesPaternityAbsencesIdResponse>(
            '/rh/pvf/requests/absences/paternity-absences/' + payload.requestId,
            payload
        );
    return data;
}
