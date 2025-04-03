import { usePost } from 'api/@base/use-post';

interface Payload {
    codigo_email: string;
}

export class RhCurrentUserValidaEmailPessoalResponse {
    message: string;
}

export async function apiRhCurrentUserValidaEmailPessoalService(
    payload: Payload
) {
    const { data } = await usePost<RhCurrentUserValidaEmailPessoalResponse>(
        'rh/current-user/valida-email-pessoal/',
        payload
    );

    return data;
}
