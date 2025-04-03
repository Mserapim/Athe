import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    usufructs_in: {
        start_date: Date;
        end_date: Date;
        days: number;
        sale_usufruct: number;
    }[];
    type_usufruct: number;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    parcel_number: number;
    observation: string;
}

class Response {
    pk: number;
    type_of_request: string;
    date: Date;
    employee_name: string;
    approver_name: string;
    status_name: string;
    get_parcel_number: string;
    acquisitive_period: string;
}

export async function pvfRequestsUsufructsServerShiftsService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/usufructs/server-shifts/',
        payload
    );
    return data;
}
