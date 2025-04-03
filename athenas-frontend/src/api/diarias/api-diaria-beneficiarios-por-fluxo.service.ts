import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload {
    viagem_id: number;
    fluxo_id: number;
}

export class ResponseItem {
    id:number;
    servidor_unicode: string;
    fluxo: number;
    fluxo_unicode: string;
    qtd_destinos: number;
    numero_empenho: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiBeneficiariosPorFluxo(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/minhas-diarias/beneficiarios-fluxo-historico/',
        payload
    );
    return data;
}