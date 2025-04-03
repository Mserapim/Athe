import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
    ano?: number;
    inicio?: string;
    fim?: string;
    mes?: string;
    servidor_id?: number;
}

export class ApiFolhaPontoJustificativasItem {
    id: number;
    tipo_justificativa: number;
    tipo_justificativa_display: string;
    horas: string;
    data_inicio: Date;
    data_fim: Date;
    observacao: string;
    anexo_id: number;
    cancelado: boolean;
    origem: number;
    origem_display: string;
    servidor_id: number;
}

export class ApiFolhaPontoJustificativas extends ListPaginated<ApiFolhaPontoJustificativasItem> {}

export async function apiFolhaPontoJustificativas(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoJustificativas>(
        'folha-ponto/justificativas/',
        payload
    );

    return data;
}
