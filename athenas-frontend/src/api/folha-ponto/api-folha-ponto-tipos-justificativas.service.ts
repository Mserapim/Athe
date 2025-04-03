import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    lotacao_id?: number;
    exportar?: string;
    sincrono?: boolean;
}

export class ApiFolhaPontoTiposJustificativasItem {
    id: number;
    value: number;
    justificativa_display: string;
    anexo_obrigatorio: string;
}

export class ApiFolhaPontoTiposJustificativas extends ListPaginated<ApiFolhaPontoTiposJustificativasItem> {}

export async function apiFolhaPontoTiposJustificativas(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoTiposJustificativas>(
        'folha-ponto/tipos-justificativas/',
        payload
    );

    return data;
}
