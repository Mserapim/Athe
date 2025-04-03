import { usePost } from 'api/@base/use-post';

export interface Payload {
    arquivo_id: number;
}

export async function apiESocialQualificacaoCadastralConfirmarQualificacao(payload: Payload) {
    const { data } = await usePost<any>(
        '/esocial/qualificacao-cadastral/confirmar-qualificacao/',
        payload
    );
    return data;
}
