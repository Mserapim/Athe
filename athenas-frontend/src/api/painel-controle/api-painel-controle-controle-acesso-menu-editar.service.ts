import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    ordem: number;
    icone?: string;
    grupo: number;
    url: string;
    link_de_ajuda: string;
}

export class ApiPainelControleControleAcessoMenuEditar {
    id: number;
    created_at: Date;
    modified_at: Date;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    ordem: number;
    icone: string;
    created_by: number;
    modified_by: number;
    grupo: number;
    url: string;
    link_de_ajuda: string;
}

export async function apiPainelControleControleAcessoMenuEditar(payload: Payload) {
    const { data } = await usePost<ApiPainelControleControleAcessoMenuEditar>(
        'painel-controle/controle-acesso/menu/editar/',
        payload
    );
    return data;
}
