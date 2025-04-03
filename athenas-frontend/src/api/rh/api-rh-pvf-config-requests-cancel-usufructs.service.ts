import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {}

export class ApiRhPvfConfigRequestsCancelUsufructsResponseItem {
    type_usufruct: TypeUsufructEnum;
    options: {
        enjoyment: number[];
        indemnity: [];
    }[];
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsCancelUsufructsResponseItem> {}

export async function apiRhPvfConfigRequestsCancelUsufructs(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/cancel/usufructs',
        payload
    );
    return data;
}
