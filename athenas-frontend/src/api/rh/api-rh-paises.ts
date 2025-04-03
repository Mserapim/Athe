import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
    order_by?: string;
    id?: number;
}

class ResponseItem {
    id: number;
    nome: string;
    ddi: string;
    nome_completo: string;
    nacionalidade: string;
    esocial_code: number;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPaises(payload: Payload) {
    const { data } = await useGet<Response>('rh/paises/', payload);
    return data;
}
