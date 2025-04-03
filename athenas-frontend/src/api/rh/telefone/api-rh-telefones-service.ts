import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { TelefoneModelReturn } from './telefone-model';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
    order_by?: string;
    id?: number;
}



class Response extends ListPaginated<TelefoneModelReturn> {}

export async function apiRhTelefones(payload: Payload) {
    const { data } = await useGet<Response>('rh/telefones/', payload);
    return data;
}
