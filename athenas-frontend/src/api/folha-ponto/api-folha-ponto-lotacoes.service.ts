import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    lotacao_id?: number;
    exportar?: string;
    sincrono?: boolean;
}

export class ApiFolhaPontoLotacoesItem {
    id: number;
    lotacao_display: string;
}

export class ApiFolhaPontoLotacoes extends ListPaginated<ApiFolhaPontoLotacoesItem> {}

export async function apiFolhaPontoLotacoes(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoLotacoes>(
        'folha-ponto/lotacoes/',
        payload
    );

    return data;
}
