import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
    acoes?: string[];
    usuario_grupo?: number;
    menu?: number;
}

export class ApiPainelControleControleAcessoMenuConfigApagar {
    id: number;
    usuario_grupo_nome: string;
    acoes: [string];
    usuario_grupo: number;
    menu: number;
}

export async function apiPainelControleControleAcessoMenuConfigApagar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoMenuConfigApagar>(
            'painel-controle/controle-acesso/menu-config/apagar/',
            payload
        );

    return data;
}
