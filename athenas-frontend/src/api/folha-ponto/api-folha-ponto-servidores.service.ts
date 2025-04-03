import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: number;
    lotacao_id?: number;
}

export class ApiFolhaPontoServidoresItem {
    id: number;
    servidor: string;
}

export class ApiFolhaPontoServidores extends ListPaginated<ApiFolhaPontoServidoresItem> {}

export async function apiFolhaPontoServidores(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoServidores>(
        'folha-ponto/servidores/',
        payload
    );

    return data;
}
