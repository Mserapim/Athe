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
    name: string;
    pk: number;
}

class Response extends ListPaginated<ResponseItem> {}

export async function pvfConfigRequestsPersonsService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/persons',
        payload
    );
    return data;
}
