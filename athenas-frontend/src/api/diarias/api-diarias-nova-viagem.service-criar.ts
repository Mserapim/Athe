import { usePost } from 'api/@base/use-post';

interface Payload {
    tipo_viagem: string;
    motivo_viagem: number;
    finalidade_viagem: number;
    hospedagem_anfitriao: boolean;
    data_inicio_viagem: string;
    data_fim_viagem: string;
    resumo: string;
    justificativa: string;
    anexos: number[];
}

export class ApiDiariasPvfMinhasDiariasViagemCriar {
    pk: number;
    tipo_viagem: string;
    motivo_viagem: number;
    finalidade_viagem: number;
    hospedagem_anfitriao: boolean;
    data_inicio_viagem: Date;
    data_fim_viagem: Date;
    resumo: string;
    justificativa: string;
    anexos: any[];

}

export async function apiDiariasViagemCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/minhas-diarias/viagem/criar/',
        payload
    );
    return data.data;
}
