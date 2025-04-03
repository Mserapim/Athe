import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    keyword?: string;
    per_page?: number;
    page?: number;
}

export class ApiRhPublicationsResponseItem {
    pk: number;
    description: string;
}

class Response extends ListPaginated<ApiRhPublicationsResponseItem> {}

export async function apiRhPublications(payload: Payload) {
    const { data } = await useGet<Response>('rh/publications/', payload);
    return data;
}
