import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    tipo: string;
    referencia: string;
    motivos_viagem: number[];
    limite: number;
    dt_inicio_vigencia: string;
}

export class ApiLimiteDiariasEditar {
    id: number;
    tipo: string;
    referencia: string;
    motivos_viagem: number[];
    limite: number;
    dt_inicio_vigencia: string;
}

export async function apiLimiteDiariasEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiLimiteDiariasEditar>(
        'diarias/config/limite-diarias/editar/',
        payload
    );

    return data;
}