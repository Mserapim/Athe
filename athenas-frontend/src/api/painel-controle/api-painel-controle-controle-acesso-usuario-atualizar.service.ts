import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    username: string;
}

export class ApiPainelControleControleAcessoUsuarioAtualizar {
    id: number;
    matricula: number;
    nome: string;
    username: string;
    status: boolean;
    unicode: string;
    categoria_funcional: string;
    cargo: string;
    lotacao: string;
    qtd_grupos: number;
    qtd_menus: number;
}

export async function apiPainelControleControleAcessoUsuarioAtualizar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoUsuarioAtualizar>(
            'painel-controle/controle-acesso/usuario/editar/',
            payload
        );

    return data;
}
