import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem?: number;
    beneficiario: number;
    numero_empenho?: number;
    empenho_liberado?: boolean;
    anexos?: any[];
}

export class ApiBeneficiarioAnaliseDeplanCriar {
    viagem: number;
    beneficiario: number;
    numero_empenho: number;
    empenho_liberado: boolean;
    anexos: any[];
}

export async function apiBeneficiarioAnaliseDeplanCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-deplan/criar/',
        payload
    );
    return data.data;
}
