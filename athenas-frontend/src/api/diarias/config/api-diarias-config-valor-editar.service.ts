import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    valor_estado: number;
    valor_fora_estado: number;
    valor_exterior: number;
    dt_inicio_vigencia: string;
    dt_fim_vigencia: string;
}

export class ApiDiariasConfigValorEditar {
    id: number;
    valor_estado: number;
    valor_fora_estado: number;
    valor_exterior: number;
    dt_inicio_vigencia: string;
    dt_fim_vigencia: string;
}

export async function apiDiariasConfigValorEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiDiariasConfigValorEditar>(
        'diarias/config/valor/editar/',
        payload
    );

    return data;
}
