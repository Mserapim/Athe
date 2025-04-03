import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    usufructs_ids: number[];
    usufructs_in: {
        start_date?: Date;
        end_date?: Date;
        days?: number;
        sale_usufruct?: number;
        parcel_number?: number;
    }[];
    substitutes?: {
        start_date: Date;
        end_date: Date;
        substitute: number;
        exercise: number;
    }[];
    observation: string;
}

class Response {}

export async function apiRhPvfRequestsSchedulesRetifications(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/schedules/retifications/',
        payload
    );
    return data;
}
