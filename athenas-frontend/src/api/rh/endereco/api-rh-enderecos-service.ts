import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { EnderecoModelReturn } from './endereco-model';

interface Payload extends ListPayload {
    palavra_chave?: string;
    page?: number;
    per_page?: number;
    order_by?: string;
    pessoa_id?: number;
    orgao_id?: number;
}

class Response extends ListPaginated<EnderecoModelReturn> {}

export async function apiRhEnderecos(payload: Payload) {
    const { data } = await useGet<Response>('rh/enderecos/', payload);
    return data;
}
