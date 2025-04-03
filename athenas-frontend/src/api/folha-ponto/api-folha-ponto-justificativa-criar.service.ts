import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    tipo_justificativa?: string | number;
    horas?: string | number;
    data_inicio?: string | Date;
    data_fim?: string | Date;
    observacao?: string;
    anexo_id?: number;
    cancelado?: boolean;
    origin?: number;
    origem?: number;
    servidor_id: number;
}

export class ApiFolhaPontoJustificativaCriar {
    id: number;
    tipo_justificativa: number;
    tipo_justificativa_display: string;
    horas?: string;
    data_inicio: Date;
    data_fim: Date;
    observacao: string;
    anexo_id: number;
    cancelado: boolean;
    origem: number;
    origem_display: string;
    servidor_id: number;
}

export async function apiFolhaPontoJustificativaCriar(payload: Payload) {
    const { data } = await usePost<ApiFolhaPontoJustificativaCriar>(
        'folha-ponto/justificativa/criar/',
        payload
    );

    return data;
}
