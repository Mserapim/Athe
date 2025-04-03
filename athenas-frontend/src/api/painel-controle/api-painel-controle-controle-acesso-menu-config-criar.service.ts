import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    acoes?: string[];
    usuario_grupo?: number;
    menu?: number;
}

export class ApiPainelControleControleAcessoMenuConfigCriar {
    id: number;
    usuario_grupo_nome: string;
    acoes: [string];
    usuario_grupo: number;
    menu: number;
}

export async function apiPainelControleControleAcessoMenuConfigCriar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoMenuConfigCriar>(
            'painel-controle/controle-acesso/menu-config/criar/',
            payload
        );

    return data;
}
