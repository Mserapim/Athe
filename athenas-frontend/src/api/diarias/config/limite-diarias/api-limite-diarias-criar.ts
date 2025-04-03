import { usePost } from 'api/@base/use-post';

interface Payload {
    tipo: string;
    referencia: string;
    motivos_viagem: number[];
    limite: number;
    dt_inicio_vigencia: string;
}

export class ApiLimitesDiariasCriar {
    id: number;
    tipo: string;
    referencia: string;
    motivos_viagem: number[];
    limite: number;
    dt_inicio_vigencia: string;
}

export async function apiLimitesDiariasCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiLimitesDiariasCriar>(
        'diarias/config/limite-diarias/criar/',
        payload
    );

    return data;
}