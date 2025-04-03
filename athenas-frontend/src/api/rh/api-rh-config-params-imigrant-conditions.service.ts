import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    keyword?: string;
}

export class ApiRhConfigImigrantConditionsItem {
    label: string;
    value: string;
}

class Response extends ListPaginated<ApiRhConfigImigrantConditionsItem> {}

export async function apiRhConfigParamsImigrantConditionsService(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/config/params/imigrant-conditions/',
        payload
    );
    return data;
}
