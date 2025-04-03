import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | 'INATIVO' | string;
    grupo_padrao: boolean;
}

export class ApiPainelControleControleAcessoGrupoEditar {
    id: number;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    grupo_padrao: boolean;
}
export async function apiPainelControleControleAcessoGrupoEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleControleAcessoGrupoEditar>(
        'painel-controle/controle-acesso/grupo/editar/',
        payload
    );

    return data;
}
