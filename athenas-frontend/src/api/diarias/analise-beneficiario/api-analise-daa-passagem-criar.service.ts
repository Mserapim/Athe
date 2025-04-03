import { usePost } from 'api/@base/use-post';

interface Payload {
    destino: number;
    empresa: string;
    aeroporto: string;
    numeroBilhete: number;
    dataHoraVoo: Date;
    anexos: any[];
}

export class ApiBeneficiarioDaaPassagemCriar {
    destino: number;
    empresa: string;
    aeroporto: string;
    numeroBilhete: number;
    dataHoraVoo: Date;
    anexos: any[];
}

export async function apiBeneficiarioDaaPassagemCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-daa-passagem/criar/',
        payload
    );
    return data.data;
}
