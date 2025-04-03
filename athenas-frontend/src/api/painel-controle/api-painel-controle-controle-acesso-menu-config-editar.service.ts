import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
    acoes?: string[];
    usuario_grupo?: number;
    menu?: number;
}

export class ApiPainelControleControleAcessoMenuConfigEditar {
    id: number;
    usuario_grupo_nome: string;
    acoes: [string];
    usuario_grupo: number;
    menu: number;
}

export async function apiPainelControleControleAcessoMenuConfigEditar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoMenuConfigEditar>(
            'painel-controle/controle-acesso/menu-config/editar/',
            payload
        );

    return data;
}
