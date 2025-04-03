import { useGet } from 'api/@base/use-get';

interface Payload {
    id: number;
}

export class ApiDiariasPvfMinhasDiariasViagemCriar {
    pk: number;
    tipo_viagem: string;
    motivo_viagem: number;
    finalidade_viagem: number;
    hospedagem_anfitriao: boolean;
    data_inicio_viagem: string;
    data_fim_viagem: string;
    resumo: string;
    justificativa: string;
    excedente: boolean;
    importada: boolean;

    anexos: any[];
    
    solicitante: string;
    solicitante_unicode: string;
    solicitante_servidor: number;

    created_at: Date;
}

export async function apiDiariasViagem(
    payload: Payload
) {
    const { data } = await useGet<ApiDiariasPvfMinhasDiariasViagemCriar>(
        'diarias/viagem/',
        payload
    );
    return data;
}
