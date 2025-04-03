import { usePost } from 'api/@base/use-post';

interface PayloadAtualizarGrupos {
    servidor_id?: number;
    usuario_grupos_ids:any[];
}

export class ApiPainelControleControleAcessoUsuarioAtualizarGrupos {
    servidor_id?: number;
    usuario_grupos_ids:any[];
}

export async function apiPainelControleControleAcessUsuarioAtualizarGrupos(
    payload: PayloadAtualizarGrupos
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoUsuarioAtualizarGrupos>(
            'painel-controle/controle-acesso/usuario/atualizar-grupos/',
            payload
        );

    return data;
}
