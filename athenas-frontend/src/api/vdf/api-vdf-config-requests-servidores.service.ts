import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiVdfConfigRequestsServidoresResponseItem {
    pk: string;
    nome: string;
    matricula: string;
    tipo_posse: string;
    ativo: string;
    data_posse: string;
    unicode: string;
}

class Response extends ListPaginated<ApiVdfConfigRequestsServidoresResponseItem> {}

export async function apiVdfConfigRequestsServidores(payload: Payload) {
    const { data } = await useGet<Response>('vdf/config/requests/servidores/', payload);
    return data;
}
