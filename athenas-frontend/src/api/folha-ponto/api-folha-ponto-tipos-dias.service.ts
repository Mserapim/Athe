import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    lotacao_id?: number;
    exportar?: string;
    sincrono?: boolean;
}

export class ApiFolhaPontoTiposDiasItem {
    cod: number;
    descricao: string;
}

export class ApiFolhaPontoTiposDias extends ListPaginated<ApiFolhaPontoTiposDiasItem> {}

export async function apiFolhaPontoTiposDias(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoTiposDias>(
        'folha-ponto/tipos-dias/',
        payload
    );

    return data;
}
