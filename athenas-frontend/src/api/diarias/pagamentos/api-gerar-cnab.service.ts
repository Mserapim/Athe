import { usePost } from 'api/@base/use-post';

interface Payload {
    pgto_ids: number[];
    data_pgto: string;
    assinado_por: string;
}

export class ApiCnabCriar {
    message: string;
    cnab_id: string;
    file_id: string;
}

export async function apiGerarCnab(
    payload: Payload
): Promise<ApiCnabCriar> {
    const { data } = await usePost<ApiCnabCriar>(
        'diarias/gerar-cnab/',
        payload
    );

    return data;
}