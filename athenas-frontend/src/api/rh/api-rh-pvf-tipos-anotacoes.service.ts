import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
    keyword?: number;
    page?: number;
    per_page?: number;
}

export class ApiRhPvfTiposAnotacaoResponseItem {
    value: string;
    label: string;
}

class Response extends ListPaginated<ApiRhPvfTiposAnotacaoResponseItem> {}

export async function apiRhPvfTiposAnotacao(payload: Payload) {
    const { data } = await useGet<Response>(
        'anotacao-pessoal/tipos-anotacao/',
        payload
    );
    return data;
}
