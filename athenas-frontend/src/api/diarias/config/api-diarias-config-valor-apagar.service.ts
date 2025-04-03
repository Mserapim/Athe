import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
    valor_estado?: number;
    valor_fora_estado?: number;
    valor_exterior?: number;
    dt_inicio_vigencia?: Date;
    dt_fim_vigencia?: Date;
}

export class ApiDiariasConfigValorApagar {
    id: number;
    valor_estado: number;
    valor_fora_estado: number;
    valor_exterior: number;
    dt_inicio_vigencia: Date;
    dt_fim_vigencia: Date;
}

export async function apiDiariasConfigValorApagar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiDiariasConfigValorApagar>(
            'diarias/config/valor/apagar/',
            payload
        );

    return data;
}
