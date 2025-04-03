import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
    pais?: number;
    order_by?: string;
}

class ResponseItem {
    id: number;
    nome: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhUnidadesAdministrativas(payload: Payload) {
    const { data } = await useGet<Response>('rh/unidades-admisitrativas/', payload);
    return data;
}
