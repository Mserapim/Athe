import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    dates:
        | {
              start_date: Date;
              end_date: Date;
          }[]
        | any;
}

export class apiRhPvfConfigRequestsDesignationsItem {
    pk: number;
    employee: string;
    exercise: string;
    range_dates?: [Date, Date][];
}

class Response extends ListPaginated<apiRhPvfConfigRequestsDesignationsItem> {}

export async function apiRhPvfConfigRequestsDesignations(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/requests/designations/',
        payload
    );
    return data;
}
