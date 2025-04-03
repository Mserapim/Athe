import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiarioID: number;
    valorDeferido: number;
}

export class ApiBenecificarioAnaliseValorDeferido {
    beneficiarioID: number;
}

export async function apiBenecificarioAnaliseValorDeferido(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-valor-deferido/',
        payload
    );
    return data.data;
}
