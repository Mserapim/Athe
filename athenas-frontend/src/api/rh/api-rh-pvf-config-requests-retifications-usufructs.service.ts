import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {}

export class ApiRhPvfConfigRequestsRetificationsUsufructsResponseItem {
    pk: number;
    start_date: Date;
    end_date: Date;
    days: number;
    type_activity: string;
    start_date_acquisition: string;
    type_usufruct: number;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsRetificationsUsufructsResponseItem> {}

export async function apiRhPvfConfigRequestsRetificationsUsufructs(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/retifications/usufructs',
        payload
    );
    return data;
}
