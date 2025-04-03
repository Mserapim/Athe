import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword: string;
    page: number;
    per_page: number;
    id?: number;
}

class ResponseItem {
    id: number;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiPainelControleClasscodes(payload: Payload) {
    const { data } = await useGet<Response>('adm/classcodes/', payload);
    return data;
}
