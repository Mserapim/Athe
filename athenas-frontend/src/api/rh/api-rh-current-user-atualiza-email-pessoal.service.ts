import { usePost } from 'api/@base/use-post';

interface Payload {
    email_pessoal: string;
}

export class RhCurrentUserAtualizaEmailPessoalResponse {}

export async function apiRhCurrentUserAtualizaEmailPessoalService(
    payload: Payload
) {
    const { data } = await usePost<RhCurrentUserAtualizaEmailPessoalResponse>(
        'rh/current-user/atualiza-email-pessoal/',
        payload
    );

    return data;
}
