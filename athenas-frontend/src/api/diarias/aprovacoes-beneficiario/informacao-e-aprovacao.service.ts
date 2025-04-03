import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario: number;
    acaoDeferimento: boolean;
    obs?: string;
    feedback?: string;
}

export class ApiBenecificarioInformacaoEAprovacao {
    beneficiario: number;
    acaoDeferimento: boolean;
    obs?: string;
}

export async function apiBenecificarioInformacaoEAprovacao(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/informacao-e-aprovacao/',
        payload
    );
    return data.data;
}
