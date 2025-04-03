import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

export class ApiRhPvfHorizontalProgressionsNextResponseItem {
    pk: number;
    name: string;
    description: string;
    target_level: string;
    contribution_time: number;
    qtd_documents: number;
    schooling_str: string;
}

class Response extends ListPaginated<ApiRhPvfHorizontalProgressionsNextResponseItem> {}

export async function apiRhPvfHorizontalProgressionsNext(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/horizontal-progressions/next',
        payload
    );
    return data;
}
