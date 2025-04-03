import { usePost } from 'api/@base/use-post';

export interface Payload {
    codigo: number,
    tabela_esocial: number,
    info: string,
    titulo: string,
    descricao: string,
    inicio_vigencia: string,
    fim_vigencia: string,
    opcoes: number[];
}

export async function apiESocialCriarItemTabela(
    payload: Payload
) {
    const { data } = await usePost<any>(
        '/esocial/item-tabela/criar/',
        payload
    );
    return data;
}
