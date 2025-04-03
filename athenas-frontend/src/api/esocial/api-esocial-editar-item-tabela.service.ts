import { usePost } from 'api/@base/use-post';

export interface Payload {
    id: number,
    codigo: number,
    tabela_esocial: number,
    info: string,
    titulo: string,
    descricao: string,
    inicio_vigencia: string,
    fim_vigencia: string,
    opcoes: number[];
}

export async function apiESocialEditarItemTabela(
    payload: Payload
) {
    const { data } = await usePost<any>(
        '/esocial/item-tabela/editar/',
        payload
    );
    return data;
}
