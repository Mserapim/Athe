import { useGet } from 'api/@base/use-get';

interface Payload {
    id?: number;
}

export class ApiPainelControleControleAcessoUsuario {
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

export async function apiPainelControleControleAcessoUsuario(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoUsuario>(
        'painel-controle/controle-acesso/usuario/',
        payload
    );

    return data;
}
