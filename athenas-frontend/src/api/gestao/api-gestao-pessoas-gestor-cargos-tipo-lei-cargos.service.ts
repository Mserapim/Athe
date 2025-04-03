import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface ApiGestorCargosTipoLeiCargosPayload extends ListPayload {
    keyword?: string;
}

interface ResponseItem {
    valor: number;
    display: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiGestorCargosTipoLeiCargos(payload: ApiGestorCargosTipoLeiCargosPayload) {
    const { data } = await useGet<Response>('rh/tipo-lei-cargos/', payload);
    return data;
}
