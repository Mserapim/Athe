import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {}

class ResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ResponseItem> {}

export function pvfRequestsStatus(payload: Payload) {
    return useGet<Response>('/rh/pvf/requests/status', payload);
}
