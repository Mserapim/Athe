import { usePost } from 'api/@base/use-post';

export interface Payload {
}

export async function apiESocialQualificacaoCadastralAtualizarLista() {
    const { data } = await usePost<any>(
        '/esocial/qualificacao-cadastral/atualizar-lista/',
        null
    );
    return data;
}
