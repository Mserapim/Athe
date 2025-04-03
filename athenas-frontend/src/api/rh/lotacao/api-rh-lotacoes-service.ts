import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { LotacaoModelReturn } from './lotacao-model';

interface Payload extends ListPayload {
    palavra_chave?: string;
    page?: number;
    per_page?: number;
    order_by?: string;
}

class Response extends ListPaginated<LotacaoModelReturn> {}

export async function apiRhLotacoesService(payload: Payload) {
    const { data } = await useGet<Response>('rh/lotacoes/', payload);
    return data;
}
