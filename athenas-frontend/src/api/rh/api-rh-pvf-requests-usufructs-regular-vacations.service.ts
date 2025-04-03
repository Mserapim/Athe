import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    usufructs_in: {
        start_date?: Date;
        end_date?: Date;
        days?: number;
        sale_usufruct?: number;
        parcel_number?: number;
    }[];
    parcel_number: number;
    type_usufruct?: number;
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    observation: string;
}

class Response {}

export async function apiRhPvfRequestsUsufructsRegularVacations(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/usufructs/regular-vacations/',
        payload
    );
    return data;
}
