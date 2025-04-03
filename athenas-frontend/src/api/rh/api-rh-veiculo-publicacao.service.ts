import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

class ResponseItem {
    label: string;
    value: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhVeiculoPublicacao(payload: Payload) {
    const { data } = await useGet<Response>('rh/veiculo-publicacao/', payload);
    return data;
}
