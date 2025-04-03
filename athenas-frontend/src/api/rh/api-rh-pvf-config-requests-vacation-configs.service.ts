import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    total_days?: number;
    type_usufruct: TypeUsufructEnum;
}

export class ApiRhPvfConfigRequestsVacationConfigsResponseItem {
    type_usufruct: TypeUsufructEnum;
    options: {
        enjoyment: number[];
        indemnity: [];
    }[];
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsVacationConfigsResponseItem> {}

export async function apiRhPvfConfigRequestsVacationConfigs(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/vacation-configs',
        payload
    );
    return data;
}
