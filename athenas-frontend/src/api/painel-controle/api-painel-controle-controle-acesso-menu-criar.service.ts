import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload {
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    ordem: number;
    icone?: string;
    grupo: number;
    url: string;
    link_de_ajuda: string;
}

export class ApiPainelControleControleAcessoMenuCriar {
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

export async function apiPainelControleControleAcessoMenuCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleControleAcessoMenuCriar>(
        'painel-controle/controle-acesso/menu/criar/',
        payload
    );

    return data;
}
