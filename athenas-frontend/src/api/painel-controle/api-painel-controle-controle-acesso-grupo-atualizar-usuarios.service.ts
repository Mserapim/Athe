import { usePost } from 'api/@base/use-post';

interface PayloadAtualizarUsuarios {
    id: number;
    servidores:any[];
}

export class ApiPainelControleControleAcessoGrupoAtualizarUsuarios {
    id: number;
    servidores:any[];
}

export async function apiPainelControleControleAcessGrupoAtualizarUsuarios(
    payload: PayloadAtualizarUsuarios
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoGrupoAtualizarUsuarios>(
            'painel-controle/controle-acesso/grupo/atualizar-usuarios/',
            payload
        );

    return data;
}
