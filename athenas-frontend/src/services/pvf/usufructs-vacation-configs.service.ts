import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    total_days: number;
    type_usufruct: TypeUsufructEnum;
}

class ResponseItem {
    type_usufruct: TypeUsufructEnum;
    options: {
        enjoyment: number[];
        indemnity: [];
    }[];
}

class Response extends ListPaginated<ResponseItem> {}

export async function pvfUsufructsVacationConfigs(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/usufructs/vacation-configs',
        payload
    );
    return data;
}
