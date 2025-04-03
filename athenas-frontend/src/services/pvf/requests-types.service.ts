import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload extends ListPayload {}

class ResponseItem {
    value: number;
    label: string;
}

class Response extends ListPaginated<ResponseItem> {}

export function pvfRequestsTypesService(payload: Payload) {
    return useGet<Response>('/rh/pvf/requests/types', payload);
}
