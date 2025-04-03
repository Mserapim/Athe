import { usePost } from 'api/@base/use-post';

interface Payload {
    nome: string;
    descricao: string;
    ordem: number;
    sigla: string;
    icone: string;
    situacao: 'ATIVO' | 'INATIVO' | string;
}

export class ApiPainelControleControleAcessoModuloCriar {
    pk: number;
    nome: string;
    descricao: string;
    ordem: number;
    icone: string;
    situacao: 'ATIVO' | string;
}

export async function apiPainelControleControleAcessoModuloCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleControleAcessoModuloCriar>(
        'painel-controle/controle-acesso/modulo/criar/',
        payload
    );

    return data;
}
