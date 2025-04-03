import { usePost } from 'api/@base/use-post';

export interface Payload {
    certificado_id: number,
    certificado_ca_id: number,
    certificado_senha: string,
}

export async function apiESocialAtualizarCertificado(
    payload: Payload
) {
    const { data } = await usePost<any>(
        '/esocial/configuracao/atualizar-certificado/',
        payload
    );
    return data;
}
