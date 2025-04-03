import { usePost } from 'api/@base/use-post';

interface Payload {
    valor_estado: number;
    valor_fora_estado: number;
    valor_exterior: number;
    dt_inicio_vigencia: string;
    dt_fim_vigencia: string;
}

export class ApiDiariasConfigValorCriar {
    id: number;
    valor_estado: number;
    valor_fora_estado: number;
    valor_exterior: number;
    dt_inicio_vigencia: string;
    dt_fim_vigencia: string;
}

export async function apiDiariasConfigValorCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasConfigValorCriar>(
        'diarias/config/valor/criar/',
        payload
    );

    return data;
}
