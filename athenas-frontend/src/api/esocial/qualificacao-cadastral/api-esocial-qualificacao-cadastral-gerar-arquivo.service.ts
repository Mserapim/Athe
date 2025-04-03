import { usePost } from 'api/@base/use-post';

export interface Payload {
}

export async function apiESocialQualificacaoCadastralGerarArquivo() {
    const { data } = await usePost<any>(
        '/esocial/qualificacao-cadastral/gerar-arquivo/',
        null
    );
    return data;
}
