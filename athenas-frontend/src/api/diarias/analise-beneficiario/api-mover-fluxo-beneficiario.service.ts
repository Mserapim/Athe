import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiarios: number[];
    fluxoEspecifico: number;
    obs?: string;
}

export class ApiMoverFluxoBenecificarios {
    beneficiarios: number[];
    fluxoEspecifico: number;
    obs?: string;
}

export async function apiMoverFluxoBenecificarios(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiarios/mover-fluxo/',
        payload
    );
    return data.data;
}
