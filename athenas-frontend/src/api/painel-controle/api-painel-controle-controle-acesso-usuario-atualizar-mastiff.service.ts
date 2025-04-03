import { usePost } from 'api/@base/use-post';

interface Payload {
    servidor_id?: number;
}

export class ApiPainelControleControleAcessoUsuarioAtualizarMastiff {
    servidor_id?: number;
}

export async function apiPainelControleControleAcessUsuarioAtualizarMastiff(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoUsuarioAtualizarMastiff>(
            'painel-controle/controle-acesso/usuario/atualizar-infos-mastiff/',
            payload
        );

    return data;
}
