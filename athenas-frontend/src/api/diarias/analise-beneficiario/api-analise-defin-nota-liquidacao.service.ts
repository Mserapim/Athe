import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem: number;
    beneficiario: number;
    numero_nota_liquidacao: number;
    anexos: any[];
}

export class ApiBeneficiarioAnaliseDefinCriar {
    viagem: number;
    beneficiario: number;
    numero_nota_liquidacao: number;
    anexos: any[];
}

export async function apiBeneficiarioAnaliseDefinCriar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-defin/criar/',
        payload
    );
    return data.data;
}