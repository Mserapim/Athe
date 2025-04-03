import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: string | number;
    justificativa_id?: string | number;
}

export class ApiFolhaPontoJustificativaCancelar {
    tipo_justificativa: 0;
    horas: string;
    data_inicio: string;
    data_fim: string;
    observacao: string;
    anexo_id: 0;
    cancelado: boolean;
    origem: number;
    servidor_id: number;
}

export async function apiFolhaPontoJustificativaCancelar(payload: Payload) {
    const { data } = await usePost<ApiFolhaPontoJustificativaCancelar>(
        'folha-ponto/justificativa/cancelar/',
        payload
    );

    return data;
}
