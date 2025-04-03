import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario: number;
    obs?: string;
    quantidadeDeferida?: number;
    fluxoEspecifico?: number;
    acompanhandoAutoridade?: boolean;
    feedback?: string;
}

export class ApiBenecificarioAnaliseQuantidadeDiarias {
    beneficiario: number;
}

export async function apiBenecificarioAnaliseQuantidadeDiarias(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-quantidade-diarias/',
        payload
    );
    return data.data;
}
