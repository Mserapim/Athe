import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

class ResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ResponseItem> {}

/* @deprecated */
export async function pvfConfigParamsDegreeKinshiptService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/config/params/degree-kinshipt',
        payload
    );
    return data;
}
