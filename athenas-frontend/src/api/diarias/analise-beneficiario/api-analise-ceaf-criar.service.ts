import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem: number;
    beneficiario: number;
    obs: string;
    anexos: any[];
}

export class ApiBeneficiarioAnaliseCeafCriar {
    viagem: number;
    beneficiario: number;
    obs: string;
    anexos: any[];
}

export async function apiBeneficiarioAnaliseCeafCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-ceaf/criar/',
        payload
    );
    return data.data;
}
