import { useGet } from 'api/@base/use-get';

interface Payload {
    pk?: number;
    id?: number;
}

export class ApiPainelControleControleAcessoMenu {
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

export async function apiPainelControleControleAcessoMenu(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoMenu>(
        'painel-controle/controle-acesso/menu/',
        payload
    );

    return data;
}
